#!/usr/bin/env python3
"""
OMEGA v6 Vertex payload: global in-memory XGBoost training on base_matrix.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import pickle
import shutil
import subprocess
import sys
import time
from pathlib import Path

from importlib.metadata import version as pkg_version


def _install_dependencies() -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "polars",
            "gcsfs",
            "fsspec",
            "numpy",
            "xgboost",
            "google-cloud-storage",
            "scikit-learn",
            "python-json-logger",
            "psutil",
        ]
    )


def _resolved_version(name: str) -> str:
    try:
        return pkg_version(name)
    except Exception:
        return "unknown"


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _download_file(gcs_uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    if not gcs_uri.startswith("gs://"):
        if Path(gcs_uri).resolve() != local_path.resolve():
            shutil.copyfile(gcs_uri, local_path)
        return
    try:
        subprocess.check_call(["gsutil", "cp", gcs_uri, str(local_path)])
        return
    except Exception:
        pass
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))


def _upload_file(local_path: Path, gcs_uri: str) -> None:
    if not gcs_uri.startswith("gs://"):
        dest_path = Path(gcs_uri)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if dest_path.resolve() != local_path.resolve():
            shutil.copyfile(local_path, dest_path)
        return
        
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(local_path))


def _bootstrap_codebase(code_bundle_uri: str) -> None:
    if not code_bundle_uri:
        return
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())


def run_global_training(args: argparse.Namespace) -> None:
    repo_root = str(Path(__file__).resolve().parent.parent)
    if repo_root not in sys.path:
        sys.path.append(repo_root)
        
    import numpy as np
    import polars as pl
    import xgboost as xgb
    from config import FEATURE_COLS

    base_uri = str(args.base_matrix_uri).strip()
    if not base_uri:
        raise RuntimeError("--base-matrix-uri is required and must not be empty.")
    local_matrix = Path("base_matrix_train.parquet")
    print(f"[*] Downloading base matrix: {base_uri}", flush=True)
    _download_file(base_uri, local_matrix)

    print("[*] Loading global manifold into RAM...", flush=True)
    started = time.time()

    # V62 Handover Defense: 1. Data Gravity Tax
    cloud_region = os.environ.get("CLOUD_ML_REGION", "us-central1")
    if cloud_region != "us-central1":
        raise RuntimeError(f"Data Gravity Violation: Running in {cloud_region}. Must match data in us-central1 strictly to avoid egress tax.")

    # V62 Handover Defense: 2. Heavy Trace Memory Defenses (Lazy Load to Prevent OOM)
    heavy_traces = ["ofi_list", "vol_list", "time_trace", "ofi_trace", "vol_trace"]
    lf = pl.scan_parquet(local_matrix)
    drop_cols = [c for c in heavy_traces if c in lf.collect_schema().names()]
    if drop_cols:
        lf = lf.drop(drop_cols)
    df = lf.collect()

    if "srl_resid" not in df.columns and "srl_resid_050" in df.columns:
        df = df.with_columns(pl.col("srl_resid_050").alias("srl_resid"))

    required_cols = {
        "date",
        "epiplexity",
        "is_energy_active",
        "sigma_eff",
        "singularity_vector",
        "spoof_ratio",
        "srl_resid",
        "t1_fwd_return",
        "topo_area",
        "topo_energy",
        *list(FEATURE_COLS),
    }

    missing = sorted([c for c in required_cols if c not in df.columns])
    if missing:
        raise RuntimeError(f"base_matrix missing columns: {missing}")

    # [HOTFIX V64.1] Dynamically reconstruct the true `is_signal` based on V64.1 math closure.
    # The L2 parquets on disk have the old V64.0 `is_signal` which compared topo_energy with sigma_eff.
    # We fix it here in-memory before training.
    signal_epi_threshold = float(args.signal_epi_threshold)
    topo_energy_min = float(args.topo_energy_min)
    spoofing_ratio_max = 2.5
    srl_resid_sigma_mult = float(args.srl_resid_sigma_mult)
    topo_area_min_abs = 1e-9
    
    df = df.with_columns([
        (
            (pl.col("is_energy_active") == True)
            & (pl.col("epiplexity") > signal_epi_threshold) 
            & (pl.col("srl_resid").abs() > srl_resid_sigma_mult * pl.col("sigma_eff"))
            & (pl.col("topo_area").abs() > topo_area_min_abs)
            & (pl.col("topo_energy") > topo_energy_min) # 纯几何无量纲门控比较 (HOTFIX)
            & (pl.col("spoof_ratio") < spoofing_ratio_max)
        ).alias("is_signal")
    ])

    # V62 Handover Defense: 3. Dynamic Schema Preflight for Time Key
    time_key = "time"
    valid_time_keys = ["time", "time_end", "bucket_id", "time_start", "__time_dt"]
    for cand in valid_time_keys:
        if cand in df.columns:
            time_key = cand
            break
            
    if time_key not in df.columns:
        # Fallback to creating a dummy row-index if absolutely no time-column found
        df = df.with_row_index(name="time_idx")
        time_key = "time_idx"

    # v61 Fix: Calculate Excess Return Target (Alpha) without Look-Ahead Bias
    print(f"[*] Orthogonalizing target (Excess Return) using temporal key: {time_key}...", flush=True)
    df = df.with_columns([
        (pl.col("t1_fwd_return") - pl.col("t1_fwd_return").mean().over(["date", time_key])).alias("t1_excess_return")
    ])

    singularity = df.get_column("singularity_vector").fill_nan(0.0).fill_null(0.0).to_numpy()
    X_all = df.select(list(FEATURE_COLS)).to_numpy()
    
    # Use Excess Return for label
    y_all = (df.get_column("t1_excess_return").to_numpy() > 0).astype(int)

    print(
        "[*] Applying V64 physics gates "
        f"(singularity_threshold={args.singularity_threshold})...",
        flush=True,
    )
    physics_mask = (
        (np.abs(singularity) > float(args.singularity_threshold))
    )

    mask_rows = int(np.sum(physics_mask))
    X_clean = X_all[physics_mask]
    y_clean = y_all[physics_mask]
    
    # V64: The weight of the sample IS the amplitude of the singularity
    weights_clean = np.abs(singularity)[physics_mask]

    finite = np.isfinite(weights_clean) & (weights_clean > 1e-8)
    X_clean = X_clean[finite]
    y_clean = y_clean[finite]
    weights_clean = weights_clean[finite]

    base_rows = int(df.height)
    train_rows = int(len(y_clean))
    print(f"[*] Sliced rows for training: {train_rows} / {base_rows} (mask_rows={mask_rows})", flush=True)
    if train_rows <= 0:
        raise RuntimeError("Physics gates removed all rows; cannot train.")

    del df, singularity, X_all, y_all, physics_mask, finite
    gc.collect()

    dtrain = xgb.DMatrix(
        X_clean,
        label=y_clean,
        weight=weights_clean,
        feature_names=list(FEATURE_COLS),
    )

    params = {
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "max_depth": int(args.xgb_max_depth),
        "eta": float(args.xgb_learning_rate),
        "subsample": float(args.xgb_subsample),
        "colsample_bytree": float(args.xgb_colsample_bytree),
        "tree_method": "hist",
        "n_jobs": int(args.n_jobs),
        "seed": int(args.seed),
    }
    rounds = int(max(1, args.num_boost_round))
    print("[*] Running one-shot global xgb.train()...", flush=True)
    model = xgb.train(params=params, dtrain=dtrain, num_boost_round=rounds)

    payload = {
        "model": model,
        "scaler": None,
        "feature_cols": list(FEATURE_COLS),
    }
    model_name = "omega_xgb_final.pkl"
    with open(model_name, "wb") as f:
        pickle.dump(payload, f)

    seconds = round(time.time() - started, 2)
    output_prefix = str(args.output_uri).rstrip("/")
    model_uri = f"{output_prefix}/{model_name}"
    _upload_file(Path(model_name), model_uri)

    metrics = {
        "status": "completed",
        "base_matrix_uri": base_uri,
        "base_rows": base_rows,
        "mask_rows": mask_rows,
        "total_training_rows": train_rows,
        "seconds": seconds,
        "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
        "model_uri": model_uri,
        "runtime_versions": {
            "python": sys.version.split()[0],
            "numpy": _resolved_version("numpy"),
            "polars": _resolved_version("polars"),
            "xgboost": _resolved_version("xgboost"),
            "scikit-learn": _resolved_version("scikit-learn"),
        },
        "overrides": {
            "signal_epi_threshold": float(args.signal_epi_threshold),
            "singularity_threshold": float(args.singularity_threshold),
            "srl_resid_sigma_mult": float(args.srl_resid_sigma_mult),
            "topo_energy_min": float(args.topo_energy_min),
            "xgb_max_depth": int(args.xgb_max_depth),
            "xgb_learning_rate": float(args.xgb_learning_rate),
            "xgb_subsample": float(args.xgb_subsample),
            "xgb_colsample_bytree": float(args.xgb_colsample_bytree),
            "num_boost_round": rounds,
            "seed": int(args.seed),
            "stage3_param_contract": "canonical_v64_1",
        },
    }
    metrics_path = Path("train_metrics.json")
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    _upload_file(metrics_path, f"{output_prefix}/train_metrics.json")
    print(json.dumps(metrics, ensure_ascii=False), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="OMEGA v6 global XGBoost trainer payload")
    ap.add_argument("--base-matrix-uri", required=True, help="GCS URI for base_matrix.parquet")
    ap.add_argument("--output-uri", required=True, help="GCS prefix for model output")

    ap.add_argument(
        "--singularity-threshold",
        "--peace-threshold",
        dest="singularity_threshold",
        type=float,
        default=0.10,
        help="Canonical singularity_vector amplitude gate. Legacy alias: --peace-threshold",
    )
    ap.add_argument(
        "--signal-epi-threshold",
        dest="signal_epi_threshold",
        type=float,
        default=0.5,
        help="Canonical V64.1 MDL signal gate used when reconstructing is_signal in-memory.",
    )
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=2.0)
    ap.add_argument(
        "--topo-energy-min",
        "--topo-energy-sigma-mult",
        dest="topo_energy_min",
        type=float,
        default=2.0,
        help="Canonical dimensionless topology gate. Legacy alias: --topo-energy-sigma-mult",
    )
    ap.add_argument("--xgb-max-depth", type=int, default=5)
    ap.add_argument("--xgb-learning-rate", type=float, default=0.03)
    ap.add_argument("--xgb-subsample", type=float, default=0.9)
    ap.add_argument("--xgb-colsample-bytree", type=float, default=0.8)
    ap.add_argument("--num-boost-round", type=int, default=150)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-jobs", type=int, default=-1)

    # Legacy args kept for compatibility with old submitters.
    ap.add_argument("--code-bundle-uri", required=True, help="Run-pinned code bundle URI.")
    ap.add_argument("--data-pattern", default="")
    ap.add_argument("--train-years", default="")
    ap.add_argument("--max-files", type=int, default=0)
    ap.add_argument("--max-rows-per-file", type=int, default=0)

    args, _ = ap.parse_known_args()
    if str(args.data_pattern).strip():
        raise RuntimeError("`--data-pattern` is forbidden for this training payload. Use `--base-matrix-uri` only.")
    if str(args.train_years).strip():
        raise RuntimeError("`--train-years` is forbidden for this training payload. Use prebuilt base_matrix scope.")
    _install_dependencies()
    _bootstrap_codebase(args.code_bundle_uri)
    run_global_training(args)


if __name__ == "__main__":
    main()
