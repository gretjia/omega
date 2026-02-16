#!/usr/bin/env python3
"""
OMEGA v6 Cloud Backtest Payload
-------------------------------
Runs backtest metrics on GCS parquet frames and (optionally) a trained model.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import pickle
import shutil
import subprocess
import sys
import time
import warnings
from pathlib import Path


warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("omega_backtest")


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _download_file(gcs_uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.check_call(["gsutil", "cp", gcs_uri, str(local_path)])
        return
    except Exception:
        pass

    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))


def _upload_json(payload: dict, gcs_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    tmp = Path("backtest_metrics.json")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(tmp))


def install_dependencies() -> None:
    logger.info("Installing dependencies...")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "polars",
            "gcsfs",
            "fsspec",
            "scikit-learn",
            "numpy",
            "pandas",
            "google-cloud-storage",
            "psutil",
            "xgboost",
        ]
    )


def bootstrap_codebase(code_bundle_uri: str) -> None:
    logger.info("Bootstrapping code from %s ...", code_bundle_uri)
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    sys.path.append(os.getcwd())
    logger.info("Codebase bootstrapped.")


def _iter_selected_files(fs, data_pattern: str, years: list[str]) -> list[str]:
    files = sorted(fs.glob(data_pattern))
    if years:
        files = [p for p in files if any(y in p for y in years)]
    return ["gs://" + p for p in files]


def _load_model_payload(model_uri: str) -> tuple[object | None, object | None, list[str] | None]:
    if not model_uri:
        return None, None, None
    local_path = Path("omega_model.pkl")
    _download_file(model_uri, local_path)
    with open(local_path, "rb") as f:
        payload = pickle.load(f)
    model = payload.get("model")
    scaler = payload.get("scaler")
    features = payload.get("feature_cols", payload.get("features"))
    return model, scaler, list(features) if features else None


def run_backtest(args: argparse.Namespace) -> dict:
    import polars as pl
    import gcsfs
    from config import L2PipelineConfig
    from omega_core.trainer import OmegaTrainerV3, evaluate_frames

    fs = gcsfs.GCSFileSystem()
    files = _iter_selected_files(fs, args.data_pattern, args.test_years)
    if not files:
        raise RuntimeError(f"No test files matched data pattern={args.data_pattern} years={args.test_years}")

    selected = files[: int(max(1, args.max_files))]
    logger.info("Matched %d test files, using %d", len(files), len(selected))

    cfg = L2PipelineConfig()
    trainer = OmegaTrainerV3(cfg)
    model, scaler, feature_cols = _load_model_payload(args.model_uri)

    metric_keys = ["Topo_SNR", "Orthogonality", "Phys_Alignment", "Model_Alignment", "Vector_Alignment"]
    weighted_sum = {k: 0.0 for k in metric_keys}
    total_weight = 0
    per_file: list[dict] = []
    started = time.time()

    for uri in selected:
        try:
            df_raw = pl.scan_parquet(uri).head(int(max(1, args.max_rows_per_file))).collect()
            if df_raw.height == 0:
                continue
            df_proc = trainer._prepare_frames(df_raw, cfg)
            if df_proc.height == 0:
                continue

            metrics = evaluate_frames(
                df_proc,
                cfg,
                model=model,
                scaler=scaler,
                feature_cols=feature_cols,
            )
            weight = int(df_proc.height)
            total_weight += weight
            for key in metric_keys:
                v = metrics.get(key)
                if v is None or (isinstance(v, float) and not math.isfinite(v)):
                    continue
                weighted_sum[key] += float(v) * weight

            per_file.append(
                {
                    "source_uri": uri,
                    "raw_rows": int(df_raw.height),
                    "proc_rows": int(df_proc.height),
                    **{k: float(metrics.get(k, float("nan"))) for k in metric_keys},
                }
            )
        except Exception as exc:
            logger.warning("Skip %s: %s", uri, exc)

    if not per_file:
        raise RuntimeError("Backtest produced no valid processed frames.")

    summary_metrics = {}
    for key in metric_keys:
        if total_weight > 0:
            summary_metrics[key] = weighted_sum[key] / float(total_weight)
        else:
            summary_metrics[key] = float("nan")

    result = {
        "status": "completed",
        "files_matched": int(len(files)),
        "files_used": int(len(per_file)),
        "total_proc_rows": int(total_weight),
        "seconds": round(time.time() - started, 2),
        "model_uri": args.model_uri or None,
        "data_pattern": args.data_pattern,
        "test_years": args.test_years,
        "summary": summary_metrics,
        "per_file": per_file[:200],
    }
    return result


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="OMEGA v6 cloud backtest payload")
    ap.add_argument("--code-bundle-uri", default="gs://omega_v52/staging/code/omega_core.zip")
    ap.add_argument("--data-pattern", default="gs://omega_v52/omega/v52/frames/host=*/*.parquet")
    ap.add_argument("--test-years", default="2025,2026")
    ap.add_argument("--model-uri", default="", help="Optional trained model pkl in GCS")
    ap.add_argument("--max-files", type=int, default=32)
    ap.add_argument("--max-rows-per-file", type=int, default=200000)
    ap.add_argument("--output-uri", required=True, help="GCS json path, e.g. gs://bucket/path/backtest_metrics.json")
    args = ap.parse_args()
    args.test_years = [x.strip() for x in str(args.test_years).split(",") if x.strip()]
    return args


def main() -> None:
    args = parse_args()
    install_dependencies()
    bootstrap_codebase(args.code_bundle_uri)
    result = run_backtest(args)
    _upload_json(result, args.output_uri)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
