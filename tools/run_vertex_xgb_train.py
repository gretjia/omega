#!/usr/bin/env python3
"""
OMEGA v6 Vertex payload: train XGBoost on framed signal parquet from GCS.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path


def _install_dependencies() -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "polars",
            "gcsfs",
            "fsspec",
            "numpy",
            "pandas",
            "xgboost",
            "scikit-learn",
            "google-cloud-storage",
            "psutil",
        ]
    )


def _bootstrap_codebase(code_bundle_uri: str) -> None:
    try:
        subprocess.check_call(["gsutil", "cp", code_bundle_uri, "omega_core.zip"])
    except Exception:
        from google.cloud import storage

        uri = code_bundle_uri.replace("gs://", "", 1)
        bucket_name, blob_name = uri.split("/", 1)
        storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename("omega_core.zip")

    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    sys.path.append(os.getcwd())


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _upload_file(local_path: Path, gcs_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(local_path))


def _iter_selected_files(fs, data_pattern: str, years: list[str]) -> list[str]:
    files = fs.glob(data_pattern)
    if not years:
        return ["gs://" + p for p in files]
    return ["gs://" + p for p in files if any(y in p for y in years)]


def run_training(args: argparse.Namespace) -> None:
    import gcsfs
    import polars as pl
    import xgboost as xgb

    from config import L2PipelineConfig
    from omega_core.trainer import OmegaTrainerV3

    cfg = L2PipelineConfig()
    cfg = replace(cfg, model=replace(cfg.model, model_type="xgboost"))

    trainer = OmegaTrainerV3(cfg)
    xgb_params = {
        "objective": str(cfg.model.xgb_objective),
        "eval_metric": str(cfg.model.xgb_eval_metric),
        "max_depth": int(cfg.model.xgb_max_depth),
        "eta": float(cfg.model.xgb_eta),
        "subsample": float(cfg.model.xgb_subsample),
        "colsample_bytree": float(cfg.model.xgb_colsample_bytree),
        "verbosity": 1,
    }
    rounds = int(max(1, cfg.model.xgb_num_boost_round))

    fs = gcsfs.GCSFileSystem()
    train_files = _iter_selected_files(fs, args.data_pattern, args.train_years)
    if not train_files:
        raise RuntimeError("No training files matched data pattern/year filters.")

    total_rows = 0
    files_used = 0
    start = time.time()
    for uri in train_files:
        try:
            df_raw = pl.scan_parquet(uri).collect()
            if df_raw.height == 0:
                continue
            df_proc = trainer._prepare_frames(df_raw, cfg)
            if df_proc.height == 0:
                continue
            dtrain = trainer.build_epistemic_dmatrix(df_proc)
            if dtrain is None:
                continue
            trainer.model = xgb.train(xgb_params, dtrain, num_boost_round=rounds, xgb_model=trainer.model)
            total_rows += int(dtrain.num_row())
            files_used += 1
        except Exception as exc:
            print(f"[Warn] Skip {uri}: {exc}", flush=True)

    if trainer.model is None or total_rows == 0:
        raise RuntimeError("Training produced no valid rows/model.")

    out_dir = Path(".")
    model_name = "omega_v6_xgb_final.pkl"
    trainer.save(out_dir=str(out_dir), name=model_name, extra_state={"total_rows": total_rows, "files_used": files_used})

    output_prefix = args.output_uri.rstrip("/")
    model_uri = f"{output_prefix}/{model_name}"
    metrics_uri = f"{output_prefix}/train_metrics.json"

    _upload_file(out_dir / model_name, model_uri)
    metrics = {
        "total_rows": total_rows,
        "files_used": files_used,
        "seconds": round(time.time() - start, 2),
        "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
    }
    metrics_path = out_dir / "train_metrics.json"
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    _upload_file(metrics_path, metrics_uri)
    print(json.dumps({"model_uri": model_uri, "metrics_uri": metrics_uri, **metrics}, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser(description="OMEGA v6 XGBoost Trainer Payload")
    ap.add_argument("--code-bundle-uri", default="gs://omega_v52/staging/code/omega_core.zip")
    ap.add_argument("--data-pattern", default="gs://omega_v52/omega/v52/frames/host=*/*.parquet")
    ap.add_argument("--train-years", default="2023,2024")
    ap.add_argument("--output-uri", required=True, help="GCS prefix, e.g. gs://bucket/staging/models/v6")
    args = ap.parse_args()
    args.train_years = [x.strip() for x in str(args.train_years).split(",") if x.strip()]

    _install_dependencies()
    _bootstrap_codebase(args.code_bundle_uri)
    run_training(args)


if __name__ == "__main__":
    main()
