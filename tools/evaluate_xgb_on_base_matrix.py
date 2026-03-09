#!/usr/bin/env python3
"""
Evaluate a trained OMEGA XGBoost payload on one isolated Stage3 base-matrix artifact.
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import polars as pl
import xgboost as xgb
from sklearn.metrics import roc_auc_score

from config import FEATURE_COLS
from tools.run_optuna_sweep import (
    _audit_training_base_matrix_contract,
    _bootstrap_codebase,
    _canonical_fingerprint,
    _download_file,
    _resolved_version,
    _spearman_rank_ic,
    _top_quantile_alpha,
    _upload_file,
)


def _load_model_payload(model_uri: str) -> dict:
    local_model = Path("omega_xgb_eval_model.pkl")
    _download_file(str(model_uri).strip(), local_model)
    with local_model.open("rb") as f:
        payload = pickle.load(f)
    if not isinstance(payload, dict):
        raise RuntimeError("model_payload_invalid_type")
    if "model" not in payload:
        raise RuntimeError("model_payload_missing_model")
    return payload


def _load_optional_json_artifact(uri: str) -> dict | None:
    clean = str(uri or "").strip()
    if not clean:
        return None
    local_path = Path("optional_metrics.json")
    _download_file(clean, local_path)
    return json.loads(local_path.read_text(encoding="utf-8"))


def _audit_holdout_scope(df: pl.DataFrame, *, expected_date_prefix: str = "") -> dict:
    date_expr = pl.col("date").cast(pl.Utf8, strict=False)
    diag = (
        df.select(
            [
                pl.len().alias("rows"),
                date_expr.min().alias("date_min"),
                date_expr.max().alias("date_max"),
                date_expr.str.slice(0, 4).min().alias("year_min"),
                date_expr.str.slice(0, 4).max().alias("year_max"),
                date_expr.str.slice(0, 4).n_unique().alias("year_count"),
                date_expr.n_unique().alias("date_count"),
            ]
        )
        .row(0, named=True)
    )
    diag = {
        "rows": int(diag["rows"] or 0),
        "date_min": str(diag["date_min"] or ""),
        "date_max": str(diag["date_max"] or ""),
        "year_min": str(diag["year_min"] or ""),
        "year_max": str(diag["year_max"] or ""),
        "year_count": int(diag["year_count"] or 0),
        "date_count": int(diag["date_count"] or 0),
    }
    if diag["rows"] <= 0:
        raise RuntimeError("holdout_scope_empty")
    prefix = str(expected_date_prefix or "").strip()
    if prefix:
        mismatch_rows = int(
            df.select(
                (~date_expr.str.starts_with(prefix)).sum().alias("prefix_mismatch_rows")
            ).item()
            or 0
        )
        if mismatch_rows > 0:
            raise RuntimeError(
                "holdout_scope_prefix_mismatch:"
                + json.dumps(
                    {
                        "expected_date_prefix": prefix,
                        "mismatch_rows": mismatch_rows,
                        **diag,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
        diag["expected_date_prefix"] = prefix
        diag["date_prefix_assertion_passed"] = True
    else:
        diag["expected_date_prefix"] = ""
        diag["date_prefix_assertion_passed"] = False
    print(
        "[GATE] Holdout scope passed "
        + json.dumps(diag, ensure_ascii=False, sort_keys=True),
        flush=True,
    )
    return diag


def _prepare_holdout_dataset(args: argparse.Namespace, *, feature_cols: list[str]) -> dict:
    base_uri = str(args.base_matrix_uri).strip()
    if not base_uri:
        raise RuntimeError("--base-matrix-uri is required and must not be empty.")

    local_matrix = Path("base_matrix_holdout.parquet")
    print(f"[*] Downloading holdout base matrix: {base_uri}", flush=True)
    _download_file(base_uri, local_matrix)

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
        *feature_cols,
    }
    missing = sorted(c for c in required_cols if c not in df.columns)
    if missing:
        raise RuntimeError(f"base_matrix missing columns: {missing}")

    scope_diag = _audit_holdout_scope(df, expected_date_prefix=args.expected_date_prefix)
    contract_diag = _audit_training_base_matrix_contract(
        df,
        singularity_threshold=float(args.singularity_threshold),
    )

    signal_epi_threshold = float(args.signal_epi_threshold)
    topo_energy_min = float(args.topo_energy_min)
    spoofing_ratio_max = 2.5
    srl_resid_sigma_mult = float(args.srl_resid_sigma_mult)
    topo_area_min_abs = 1e-9

    df = df.with_columns(
        [
            (
                (pl.col("is_energy_active") == True)
                & (pl.col("epiplexity") > signal_epi_threshold)
                & (pl.col("srl_resid").abs() > srl_resid_sigma_mult * pl.col("sigma_eff"))
                & (pl.col("topo_area").abs() > topo_area_min_abs)
                & (pl.col("topo_energy") > topo_energy_min)
                & (pl.col("spoof_ratio") < spoofing_ratio_max)
            ).alias("is_signal")
        ]
    )

    time_key = "time"
    for cand in ("time", "time_end", "bucket_id", "time_start", "__time_dt"):
        if cand in df.columns:
            time_key = cand
            break
    if time_key not in df.columns:
        df = df.with_row_index(name="time_idx")
        time_key = "time_idx"

    print(f"[*] Orthogonalizing holdout target using temporal key: {time_key}", flush=True)
    df = df.with_columns(
        [
            (
                pl.col("t1_fwd_return") - pl.col("t1_fwd_return").mean().over(["date", time_key])
            ).alias("t1_excess_return")
        ]
    )

    singularity = df.get_column("singularity_vector").fill_nan(0.0).fill_null(0.0).to_numpy()
    X_all = df.select(feature_cols).to_numpy()
    y_all = (df.get_column("t1_excess_return").to_numpy() > 0).astype(int)
    excess_all = df.get_column("t1_excess_return").to_numpy()

    physics_mask = np.abs(singularity) > float(args.singularity_threshold)
    full_mask = physics_mask

    X_eval = X_all[full_mask]
    y_eval = y_all[full_mask]
    excess_eval = excess_all[full_mask]

    eval_rows = int(y_eval.size)
    positive_rows = int(np.sum(y_eval))
    negative_rows = int(eval_rows - positive_rows)
    if eval_rows <= 0:
        raise RuntimeError("holdout_eval_empty_after_physics_mask")

    dholdout = xgb.DMatrix(
        X_eval,
        label=y_eval,
        feature_names=feature_cols,
    )
    summary = {
        "base_matrix_uri": base_uri,
        "dataset_role": str(args.dataset_role),
        "expected_date_prefix": str(args.expected_date_prefix or ""),
        "base_rows": int(df.height),
        "mask_rows": int(np.sum(physics_mask)),
        "eval_rows": eval_rows,
        "positive_rows": positive_rows,
        "negative_rows": negative_rows,
        "contract_diag": contract_diag,
        "scope_diag": scope_diag,
        "feature_cols": list(feature_cols),
        "feature_col_count": int(len(feature_cols)),
        "time_key": str(time_key),
    }
    print(
        "[GATE] Holdout evaluation dataset prepared "
        + json.dumps(summary, ensure_ascii=False, sort_keys=True),
        flush=True,
    )
    return {
        "dholdout": dholdout,
        "y_eval": y_eval,
        "excess_eval": excess_eval,
        "summary": summary,
        "canonical_fingerprint": _canonical_fingerprint(args),
    }


def _predict_payload(payload: dict, dholdout: xgb.DMatrix) -> np.ndarray:
    model = payload.get("model")
    if model is None:
        raise RuntimeError("model_payload_missing_model")
    if isinstance(model, xgb.Booster):
        return model.predict(dholdout)
    raise RuntimeError(f"unsupported_model_type_for_holdout_eval:{type(model).__name__}")


def _validate_training_overrides(args: argparse.Namespace, train_metrics: dict | None) -> dict | None:
    if not train_metrics:
        return None
    overrides = dict(train_metrics.get("overrides") or {})
    if not overrides:
        raise RuntimeError("train_metrics_missing_overrides")
    expected = {
        "signal_epi_threshold": float(args.signal_epi_threshold),
        "singularity_threshold": float(args.singularity_threshold),
        "srl_resid_sigma_mult": float(args.srl_resid_sigma_mult),
        "topo_energy_min": float(args.topo_energy_min),
        "stage3_param_contract": "canonical_v64_1",
    }
    mismatches = {}
    for key, expected_value in expected.items():
        actual_value = overrides.get(key)
        if actual_value != expected_value:
            mismatches[key] = {"expected": expected_value, "actual": actual_value}
    if mismatches:
        raise RuntimeError(
            "train_metrics_override_mismatch:"
            + json.dumps(mismatches, ensure_ascii=False, sort_keys=True)
        )
    return overrides


def evaluate_holdout(args: argparse.Namespace) -> dict:
    payload = _load_model_payload(args.model_uri)
    train_metrics = _load_optional_json_artifact(args.train_metrics_uri)
    validated_overrides = _validate_training_overrides(args, train_metrics)
    feature_cols = list(payload.get("feature_cols") or payload.get("features") or FEATURE_COLS)
    datasets = _prepare_holdout_dataset(args, feature_cols=feature_cols)
    preds = _predict_payload(payload, datasets["dholdout"])
    positive_rows = int(datasets["summary"]["positive_rows"])
    negative_rows = int(datasets["summary"]["negative_rows"])
    auc = None
    auc_defined = positive_rows > 0 and negative_rows > 0
    if auc_defined:
        auc = float(roc_auc_score(datasets["y_eval"], preds))
    spearman_ic = _spearman_rank_ic(preds, datasets["excess_eval"])
    alpha_top_decile = _top_quantile_alpha(preds, datasets["excess_eval"], 0.90)
    alpha_top_quintile = _top_quantile_alpha(preds, datasets["excess_eval"], 0.80)

    summary = {
        "status": "completed",
        "dataset_role": str(args.dataset_role),
        "base_matrix_uri": str(args.base_matrix_uri),
        "model_uri": str(args.model_uri),
        "auc": auc,
        "auc_defined": bool(auc_defined),
        "spearman_ic": float(spearman_ic),
        "alpha_top_decile": float(alpha_top_decile),
        "alpha_top_quintile": float(alpha_top_quintile),
        "pred_mean": float(np.mean(preds)),
        "pred_std": float(np.std(preds)),
        "learner_mode": str(payload.get("learner_mode", "unknown")),
        "canonical_fingerprint": datasets["canonical_fingerprint"],
        "validated_training_overrides": validated_overrides,
        "dataset_summary": datasets["summary"],
        "runtime_versions": {
            "python": sys.version.split()[0],
            "numpy": _resolved_version("numpy"),
            "polars": _resolved_version("polars"),
            "xgboost": _resolved_version("xgboost"),
            "scikit-learn": _resolved_version("scikit-learn"),
        },
    }
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate a trained OMEGA XGBoost model on one base-matrix artifact")
    ap.add_argument("--base-matrix-uri", required=True)
    ap.add_argument("--model-uri", required=True)
    ap.add_argument("--output-uri", required=True, help="GCS or local prefix for metrics output")
    ap.add_argument("--dataset-role", default="holdout")
    ap.add_argument("--expected-date-prefix", default="")
    ap.add_argument("--train-metrics-uri", default="")
    ap.add_argument(
        "--singularity-threshold",
        "--peace-threshold",
        dest="singularity_threshold",
        type=float,
        default=0.10,
    )
    ap.add_argument("--signal-epi-threshold", dest="signal_epi_threshold", type=float, default=0.5)
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=2.0)
    ap.add_argument(
        "--topo-energy-min",
        "--topo-energy-sigma-mult",
        dest="topo_energy_min",
        type=float,
        default=2.0,
    )
    ap.add_argument("--code-bundle-uri", default="")
    args, _ = ap.parse_known_args()

    if str(args.code_bundle_uri).strip():
        _bootstrap_codebase(args.code_bundle_uri)

    started = time.time()
    summary = evaluate_holdout(args)
    summary["seconds"] = round(time.time() - started, 2)

    local_out = Path("holdout_metrics.json")
    local_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    output_prefix = str(args.output_uri).rstrip("/")
    _upload_file(local_out, f"{output_prefix}/holdout_metrics.json")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
