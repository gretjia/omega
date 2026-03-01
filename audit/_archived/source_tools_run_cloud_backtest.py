#!/usr/bin/env python3
"""
OMEGA v6 Cloud Backtest Payload
Architectural Fix: Global In-Memory Causal Reconstruction.
Replaces the broken isolated-thread map-reduce with a unified, chronological Polars DataFrame.
Preserves absolute time causality for T+1 labels while saturating cloud CPUs.
"""

from __future__ import annotations

import argparse
import gc
import json
import logging
import math
import os
import pickle
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

import numpy as np

warnings = logging.getLogger("py.warnings")
warnings.setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("omega_backtest")


def _resolve_time_key(columns: list[str]) -> str:
    for candidate in ("time", "time_end", "time_start", "bucket_id"):
        if candidate in columns:
            return candidate
    raise RuntimeError(
        "No valid time column found. Expected one of: "
        "['time', 'time_end', 'time_start', 'bucket_id']; "
        f"available columns={columns}"
    )


def _assert_required_schema(columns: list[str], cfg) -> None:
    required = ["symbol", "close"]
    missing = [c for c in required if c not in columns]
    if missing:
        raise RuntimeError(
            f"Missing required columns for backtest: {missing}; available columns={columns}"
        )

    t1_days = int(max(0, getattr(cfg.micro, "t_plus_1_horizon_days", 0)))
    if t1_days > 0 and "date" not in columns:
        raise RuntimeError(
            "t_plus_1_horizon_days is enabled but 'date' column is missing; "
            f"available columns={columns}"
        )


def _build_dedup_sort_keys(columns: list[str], time_key: str) -> tuple[list[str], list[str]]:
    dedup_keys: list[str] = []
    sort_keys: list[str] = []

    if "symbol" in columns:
        dedup_keys.append("symbol")
        sort_keys.append("symbol")

    if "date" in columns:
        # For bucket_id time keys, date is required to avoid cross-day collisions.
        if time_key == "bucket_id":
            dedup_keys.append("date")
        sort_keys.append("date")
    elif time_key == "bucket_id":
        raise RuntimeError(
            "Found 'bucket_id' time key but missing 'date' column; cannot preserve cross-day causality."
        )

    dedup_keys.append(time_key)
    sort_keys.append(time_key)
    return dedup_keys, sort_keys


def _preflight_schema(selected_uris: list[str], cfg, pl_mod) -> tuple[str, list[str], list[str]]:
    probe_uri = selected_uris[0]
    logger.info("Running schema preflight on: %s", probe_uri)
    probe_cols = list(pl_mod.scan_parquet(probe_uri).collect_schema().names())
    _assert_required_schema(probe_cols, cfg)
    time_key = _resolve_time_key(probe_cols)
    dedup_keys, sort_keys = _build_dedup_sort_keys(probe_cols, time_key)
    logger.info(
        "Schema preflight passed: time_key=%s dedup_keys=%s sort_keys=%s",
        time_key,
        dedup_keys,
        sort_keys,
    )
    return time_key, dedup_keys, sort_keys


def _can_reuse_precomputed_physics(columns: list[str]) -> bool:
    required = {
        "sigma_eff",
        "depth_eff",
        "epiplexity",
        "topo_area",
        "topo_energy",
        "srl_resid",
        "adaptive_y",
        "is_signal",
        "direction",
        "price_change",
    }
    return required.issubset(set(columns))


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob

def _download_file(gcs_uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    if not gcs_uri.startswith("gs://"):
        return
    try:
        subprocess.check_call(["gsutil", "-q", "cp", gcs_uri, str(local_path)])
        return
    except Exception:
        from google.cloud import storage
        bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
        storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))

def _fast_parallel_download(uris: list[str], dest_dir: Path, max_workers: int) -> list[str]:
    """Rapid parallel download that prevents collision between linux1 and windows1 hosts."""
    from google.cloud import storage
    dest_dir.mkdir(parents=True, exist_ok=True)
    max_workers = max(1, int(max_workers))
    logger.info("Rapid downloading %d files to local NVMe (workers=%d)...", len(uris), max_workers)
    
    client = storage.Client()
    def _dl(uri: str):
        clean = uri.replace("gs://", "", 1)
        bucket_name, blob_name = clean.split("/", 1)
        # Unique local name to prevent host=linux1 vs host=windows1 collisions
        safe_name = blob_name.replace("/", "_")
        local_path = dest_dir / safe_name
        if not local_path.exists():
            client.bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))
        return str(local_path)
            
    local_paths: list[str] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_dl, uri) for uri in uris]
        total = len(futures)
        for idx, fut in enumerate(as_completed(futures), start=1):
            local_paths.append(fut.result())
            if idx == total or idx % 20 == 0:
                logger.info("Download progress: %d/%d", idx, total)
    logger.info("Parallel download complete.")
    return local_paths

def _upload_json(payload: dict, gcs_uri: str) -> None:
    from google.cloud import storage
    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    tmp = Path("backtest_metrics.json")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(tmp))

def _install_dependencies() -> None:
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--quiet",
        "polars", "gcsfs", "fsspec", "scikit-learn", "numpy", "pandas", "google-cloud-storage", "psutil", "xgboost"
    ])

def _bootstrap_codebase(code_bundle_uri: str) -> None:
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())

def _extract_day_key(path_or_uri: str) -> str:
    name = str(path_or_uri).rsplit("/", 1)[-1]
    m = re.match(r"^(\d{8})_", name)
    return m.group(1) if m else ""

def _day_summary(uris: list[str]) -> dict:
    days = sorted({d for d in (_extract_day_key(x) for x in uris) if d})
    if not days:
        return {"count": 0, "first": None, "last": None}
    return {"count": len(set(days)), "first": days[0], "last": days[-1]}

def _select_backtest_files(fs, data_pattern: str, test_years: list[str], test_ym: list[str], max_files: int) -> tuple[list[str], list[str]]:
    files = [f"gs://{x}" if not x.startswith("gs://") else x for x in sorted(fs.glob(data_pattern))]
    filtered = []
    year_set = {str(y).strip() for y in test_years if str(y).strip()}
    ym_prefixes = [str(x).strip() for x in test_ym if str(x).strip()]

    for uri in files:
        day = _extract_day_key(uri)
        if not day: continue
        if year_set and day[:4] not in year_set: continue
        if ym_prefixes and not any(day.startswith(p) for p in ym_prefixes): continue
        filtered.append(uri)

    if max_files <= 0 or len(filtered) <= max_files:
        return filtered, list(filtered)

    idx = np.linspace(0, len(filtered) - 1, num=max_files, dtype=int).tolist()
    return filtered, [filtered[int(i)] for i in idx]

def _load_model_payload(model_uri: str) -> tuple[object | None, object | None, list[str] | None]:
    if not model_uri: return None, None, None
    local_model = Path("omega_model.pkl")
    _download_file(model_uri, local_model)
    with local_model.open("rb") as f:
        payload = pickle.load(f)
    return payload.get("model"), payload.get("scaler"), payload.get("feature_cols", payload.get("features"))

def run_global_backtest(args: argparse.Namespace) -> dict:
    import gcsfs
    import polars as pl
    import psutil
    from config import L2PipelineConfig
    from omega_core.trainer import OmegaTrainerV3, evaluate_frames

    started = time.time()
    fs = gcsfs.GCSFileSystem()
    matched, selected_uris = _select_backtest_files(
        fs, args.data_pattern, list(args.test_years), list(args.test_ym), int(args.max_files)
    )
    if not selected_uris:
        raise RuntimeError("No backtest files matched criteria.")
        
    logger.info(f"Target locked: {len(selected_uris)} frames of data.")

    if args.model_uri:
        _download_file(args.model_uri, Path("omega_model.pkl"))

    # 1. Config Overrides
    cfg = L2PipelineConfig()
    sig = cfg.signal
    if args.peace_threshold is not None: sig = replace(sig, peace_threshold=float(args.peace_threshold))
    if args.srl_resid_sigma_mult is not None: sig = replace(sig, srl_resid_sigma_mult=float(args.srl_resid_sigma_mult))
    if args.topo_energy_sigma_mult is not None: sig = replace(sig, topo_energy_sigma_mult=float(args.topo_energy_sigma_mult))
    cfg = replace(cfg, signal=sig)
    max_eval_traces = int(getattr(args, "max_eval_traces", 0))
    if max_eval_traces > 0:
        vcfg = cfg.validation
        current = getattr(vcfg, "max_traces", None)
        if current is None or int(current) > max_eval_traces:
            cfg = replace(cfg, validation=replace(vcfg, max_traces=max_eval_traces))
            logger.info("Capping evaluation traces to max_traces=%d", max_eval_traces)

    # 2. Schema preflight (fail-fast before full download)
    expected_time_key, expected_dedup_keys, expected_sort_keys = _preflight_schema(selected_uris, cfg, pl)

    # 3. Localize Data (The Data Gravity Move)
    local_data_dir = Path("/tmp/omega_backtest_raw")
    if local_data_dir.exists():
        shutil.rmtree(local_data_dir)
    download_workers = int(getattr(args, "download_workers", 16) or 16)
    local_paths = _fast_parallel_download(selected_uris, local_data_dir, max_workers=download_workers)

    model, scaler, feature_cols = _load_model_payload(args.model_uri)
    trainer = OmegaTrainerV3(cfg)

    # 4. Global Memory Materialization & Causal Restoration
    logger.info("Loading all raw data into a single massive RAM matrix...")
    df_raw = pl.scan_parquet(local_paths).collect()
    
    if df_raw.height == 0:
        raise RuntimeError("Backtest raw data is completely empty.")

    _assert_required_schema(df_raw.columns, cfg)
    reuse_precomputed_physics = _can_reuse_precomputed_physics(df_raw.columns)
    if reuse_precomputed_physics:
        os.environ["OMEGA_REUSE_PRECOMPUTED_PHYSICS"] = "1"
        drop_cols = [c for c in ("ofi_list", "ofi_trace", "vol_list", "vol_trace", "time_trace") if c in df_raw.columns]
        if drop_cols:
            df_raw = df_raw.drop(drop_cols)
            logger.info(
                "Enabled precomputed physics reuse; dropped heavy columns before sort/prepare: %s",
                drop_cols,
            )
    else:
        os.environ.pop("OMEGA_REUSE_PRECOMPUTED_PHYSICS", None)
        logger.info("Precomputed physics reuse unavailable; recursive kernel recompute remains enabled.")

    time_key = _resolve_time_key(df_raw.columns)
    dedup_keys, sort_keys = _build_dedup_sort_keys(df_raw.columns, time_key)
    if time_key != expected_time_key or dedup_keys != expected_dedup_keys or sort_keys != expected_sort_keys:
        logger.warning(
            "Schema keys changed after localization. preflight=(%s,%s,%s) localized=(%s,%s,%s)",
            expected_time_key,
            expected_dedup_keys,
            expected_sort_keys,
            time_key,
            dedup_keys,
            sort_keys,
        )
    logger.info(
        "Resolved causal keys: time_key=%s dedup_keys=%s sort_keys=%s",
        time_key,
        dedup_keys,
        sort_keys,
    )

    logger.info("Deduplicating tick collisions across hosts (linux1 vs windows1)...")
    df_raw = df_raw.unique(subset=dedup_keys, keep="last")
    
    # [ARCHITECTURAL KERNEL]: sorting by symbol/date/time preserves causality for T+1 shift
    logger.info(f"Sorting multidimensional spacetime ({df_raw.height} rows)...")
    df_raw = df_raw.sort(sort_keys)

    # 5. Global Physics Forging & Labeling
    logger.info("Applying physical engine. Polars Rust backend will saturate all CPU cores.")
    df_proc = trainer._prepare_frames(df_raw, cfg)
    proc_rows = df_proc.height
    logger.info(f"Valid processed rows after T+1 causality shift: {proc_rows}")
    
    if proc_rows == 0:
        raise RuntimeError("Backtest produced no valid processed frames. T+1 shift dropped all rows.")

    del df_raw
    gc.collect()

    # 6. Global Evaluation
    logger.info("Evaluating Non-Linear Oracle (Model Alignment)...")
    metrics = evaluate_frames(df_proc, cfg, model=model, scaler=scaler, feature_cols=feature_cols)
    metric_keys = ["Topo_SNR", "Orthogonality", "Phys_Alignment", "Model_Alignment", "Vector_Alignment"]
    summary = {k: float(metrics.get(k, float("nan"))) for k in metric_keys}

    cpu_cores = psutil.cpu_count(logical=True)
    mem_gb = psutil.virtual_memory().total / (1024 ** 3)

    # 7. Schema Compliance (Mocking per_file for downstream pipelines)
    result = {
        "status": "completed",
        "files_matched": len(matched),
        "files_selected": len(selected_uris),
        "files_used": len(selected_uris),
        "day_span_selected": _day_summary(selected_uris),
        "day_span_used": _day_summary(selected_uris),
        "total_proc_rows": proc_rows,
        "seconds": round(time.time() - started, 2),
        "model_uri": args.model_uri or None,
        "data_pattern": args.data_pattern,
        "test_years": list(args.test_years),
        "test_ym": list(args.test_ym),
        "split_guard": {"enforced": True, "test_years": list(args.test_years), "test_ym": list(args.test_ym)},
        "overrides": {
            "peace_threshold": args.peace_threshold,
            "srl_resid_sigma_mult": args.srl_resid_sigma_mult,
            "topo_energy_sigma_mult": args.topo_energy_sigma_mult,
        },
        "worker_plan": {
            "requested": 1, "min_workers": 1, "max_workers": cpu_cores, "start_workers": cpu_cores, 
            "adaptive": False, "cpu_total": cpu_cores, "mem_total_gb": round(mem_gb, 2), 
            "architecture": "global_causal_materialization",
            "reuse_precomputed_physics": bool(reuse_precomputed_physics),
        },
        "summary": summary,
        "per_file_count": 1,
        "per_file": [{
            "source_uri": "global_continuum_manifold",
            "raw_rows": -1,
            "proc_rows": proc_rows,
            **summary
        }]
    }
    return result

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--code-bundle-uri", required=True)
    ap.add_argument("--data-pattern", default="gs://omega_v52/omega/v52/frames/host=*/*.parquet")
    ap.add_argument("--test-years", default="")
    ap.add_argument("--test-ym", default="")
    ap.add_argument("--model-uri", default="")
    ap.add_argument("--max-files", type=int, default=0)
    ap.add_argument("--max-rows-per-file", type=int, default=0)
    ap.add_argument("--output-uri", required=True)
    ap.add_argument("--peace-threshold", type=float, default=None)
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=None)
    ap.add_argument("--topo-energy-sigma-mult", type=float, default=None)
    ap.add_argument("--max-eval-traces", type=int, default=50000)
    ap.add_argument("--download-workers", type=int, default=16)
    
    # Catch legacy autopilot worker args and ignore them to prevent crash
    for arg in ["--workers", "--workers-min", "--workers-max", "--workers-start", "--workers-cpu-frac", 
                "--workers-cpu-util-low", "--workers-cpu-util-high", "--workers-mem-headroom-gb", 
                "--workers-est-mem-gb", "--workers-adjust-step", "--workers-poll-sec"]:
        ap.add_argument(arg, default=None)

    args = ap.parse_args()
    args.test_years = [x.strip() for x in str(args.test_years).split(",") if x.strip()]
    args.test_ym = [x.strip() for x in str(args.test_ym).split(",") if x.strip()]
    if not args.test_years:
        raise SystemExit("--test-years cannot be empty.")
    return args

def main():
    args = parse_args()
    _install_dependencies()
    _bootstrap_codebase(args.code_bundle_uri)
    res = run_global_backtest(args)
    _upload_json(res, args.output_uri)
    print(json.dumps(res, ensure_ascii=False))

if __name__ == "__main__":
    main()
