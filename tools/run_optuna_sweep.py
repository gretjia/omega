#!/usr/bin/env python3
"""
OMEGA v643 Vertex payload: temporal Optuna/XGBoost sweep on one immutable train-only base matrix.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from importlib.metadata import version as pkg_version
from importlib.util import find_spec


OBJECTIVE_METRICS = {
    "val_auc",
    "alpha_top_decile",
    "alpha_top_quintile",
    "structural_tail_monotonicity_gate",
}
WEIGHT_MODES = {
    "none",
    "physics_abs_singularity",
    "abs_excess_return",
    "pow_0p875_abs_excess_return",
    "pow_0p75_abs_excess_return",
    "pow_0p625_abs_excess_return",
    "sqrt_abs_excess_return",
}
LEARNER_MODES = {"binary_logistic_sign", "reg_squarederror_excess_return"}
HARD_LOSING_OBJECTIVE_VALUE = -1.0e9
STRUCTURAL_TAIL_OBJECTIVE = "structural_tail_monotonicity_gate"
STRUCTURAL_TAIL_REQUIRED_BINARY_WEIGHT_MODE = "sqrt_abs_excess_return"
STRUCTURAL_TAIL_REQUIRED_BINARY_LEARNER_MODE = "binary_logistic_sign"
STRUCTURAL_TAIL_REQUIRED_REGRESSION_WEIGHT_MODE = "none"
STRUCTURAL_TAIL_REQUIRED_REGRESSION_LEARNER_MODE = "reg_squarederror_excess_return"
STRUCTURAL_TAIL_MIN_AUC_FLOOR = 0.505
STRUCTURAL_TAIL_MIN_SPEARMAN_FLOOR = 0.0


def _install_dependencies() -> None:
    required_modules = [
        "optuna",
        "polars",
        "gcsfs",
        "fsspec",
        "numpy",
        "xgboost",
        "google.cloud.storage",
        "sklearn",
        "pythonjsonlogger",
        "psutil",
    ]
    if all(find_spec(name) is not None for name in required_modules):
        return
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "optuna",
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
        src = Path(gcs_uri)
        if src.resolve() != local_path.resolve():
            shutil.copyfile(src, local_path)
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
    if not gcs_uri:
        return
    if not gcs_uri.startswith("gs://"):
        dest = Path(gcs_uri)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.resolve() != local_path.resolve():
            shutil.copyfile(local_path, dest)
        return
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(local_path))


def _bootstrap_codebase(code_bundle_uri: str) -> None:
    if not code_bundle_uri:
        return
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.append(cwd)


def _audit_training_base_matrix_contract(df, *, singularity_threshold: float) -> dict:
    import polars as pl

    diag = (
        df.select(
            [
                pl.len().alias("rows"),
                (pl.col("epiplexity").fill_null(0.0).fill_nan(0.0) > 0.0).sum().alias("epi_pos_rows"),
                (pl.col("topo_energy").fill_null(0.0).fill_nan(0.0) > 0.0).sum().alias("topo_energy_pos_rows"),
                (
                    pl.col("singularity_vector").fill_null(0.0).fill_nan(0.0).abs() > float(singularity_threshold)
                ).sum().alias("signal_gate_rows"),
            ]
        )
        .row(0, named=True)
    )
    diag = {k: int(v or 0) for k, v in diag.items()}
    if diag["rows"] <= 0:
        raise RuntimeError("training_input_contract_empty")
    if diag["signal_gate_rows"] <= 0:
        raise RuntimeError("training_input_contract_no_singularity_rows:" + json.dumps(diag, sort_keys=True))
    if diag["epi_pos_rows"] <= 0 or diag["topo_energy_pos_rows"] <= 0:
        raise RuntimeError(
            "training_input_contract_degenerate_canonical_signal_chain:" + json.dumps(diag, sort_keys=True)
        )
    print(
        "[GATE] Training input contract passed "
        f"{json.dumps(diag, ensure_ascii=False, sort_keys=True)}",
        flush=True,
    )
    return diag


def _canonical_fingerprint(args: argparse.Namespace) -> dict:
    payload = {
        "stage3_param_contract": "canonical_v64_1",
        "signal_epi_threshold": float(args.signal_epi_threshold),
        "singularity_threshold": float(args.singularity_threshold),
        "srl_resid_sigma_mult": float(args.srl_resid_sigma_mult),
        "topo_energy_min": float(args.topo_energy_min),
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    payload["sha256"] = hashlib.sha256(encoded).hexdigest()
    return payload


def _year_mask(date_series, year: str):
    import numpy as np

    vals = np.asarray(date_series, dtype=str)
    return np.char.startswith(vals, str(year))


def _top_quantile_alpha(preds, excess_returns, q: float) -> float:
    import numpy as np

    if preds.size <= 0:
        return 0.0
    cutoff = float(np.quantile(preds, q))
    mask = preds >= cutoff
    if int(np.sum(mask)) <= 0:
        return 0.0
    return float(np.mean(excess_returns[mask]))


def _average_ranks(values):
    import numpy as np

    arr = np.asarray(values, dtype=np.float64)
    if arr.size <= 0:
        return np.asarray([], dtype=np.float64)
    order = np.argsort(arr, kind="mergesort")
    sorted_vals = arr[order]
    ranks = np.empty(arr.size, dtype=np.float64)
    i = 0
    while i < arr.size:
        j = i + 1
        while j < arr.size and sorted_vals[j] == sorted_vals[i]:
            j += 1
        avg_rank = ((i + 1) + j) / 2.0
        ranks[order[i:j]] = avg_rank
        i = j
    return ranks


def _spearman_rank_ic(preds, actuals) -> float:
    import numpy as np

    pred_arr = np.asarray(preds, dtype=np.float64)
    actual_arr = np.asarray(actuals, dtype=np.float64)
    mask = np.isfinite(pred_arr) & np.isfinite(actual_arr)
    pred_arr = pred_arr[mask]
    actual_arr = actual_arr[mask]
    if pred_arr.size <= 1:
        return 0.0
    pred_rank = _average_ranks(pred_arr)
    actual_rank = _average_ranks(actual_arr)
    pred_std = float(np.std(pred_rank))
    actual_std = float(np.std(actual_rank))
    if pred_std <= 0.0 or actual_std <= 0.0:
        return 0.0
    return float(np.corrcoef(pred_rank, actual_rank)[0, 1])


def _resolve_objective_metric(metric: str) -> str:
    clean = str(metric or "").strip()
    if clean not in OBJECTIVE_METRICS:
        raise RuntimeError(f"unsupported_objective_metric: {clean}")
    return clean


def _resolve_weight_mode(mode: str) -> str:
    clean = str(mode or "").strip()
    if clean not in WEIGHT_MODES:
        raise RuntimeError(f"unsupported_weight_mode: {clean}")
    return clean


def _resolve_learner_mode(mode: str) -> str:
    clean = str(mode or "").strip()
    if clean not in LEARNER_MODES:
        raise RuntimeError(f"unsupported_learner_mode: {clean}")
    return clean


def _raw_objective_value(
    objective_metric: str,
    *,
    auc: float,
    alpha_top_decile: float,
    alpha_top_quintile: float,
) -> float:
    metric = _resolve_objective_metric(objective_metric)
    if metric == "val_auc":
        return float(auc)
    if metric == "alpha_top_decile":
        return float(alpha_top_decile)
    if metric == "alpha_top_quintile":
        return float(alpha_top_quintile)
    return float((float(alpha_top_decile) + float(alpha_top_quintile)) / 2.0)


def _objective_contract(
    objective_metric: str,
    *,
    auc: float | None,
    val_spearman_ic: float,
    alpha_top_decile: float,
    alpha_top_quintile: float,
    min_val_auc: float,
    min_val_spearman_ic: float,
    learner_mode: str,
) -> dict:
    metric = _resolve_objective_metric(objective_metric)
    raw_objective_value = _raw_objective_value(
        metric,
        auc=float(auc or 0.0),
        alpha_top_decile=alpha_top_decile,
        alpha_top_quintile=alpha_top_quintile,
    )
    auc_guardrail_min = float(min_val_auc)
    spearman_guardrail_min = float(min_val_spearman_ic)
    auc_guardrail_enabled = metric != "val_auc" and auc_guardrail_min > 0.0
    spearman_guardrail_enabled = False
    structural_metric_name = "val_auc"
    if metric == STRUCTURAL_TAIL_OBJECTIVE and learner_mode == STRUCTURAL_TAIL_REQUIRED_REGRESSION_LEARNER_MODE:
        auc_guardrail_enabled = False
        spearman_guardrail_enabled = True
        structural_metric_name = "val_spearman_ic"
    auc_guardrail_passed = float(auc or 0.0) >= auc_guardrail_min if auc_guardrail_enabled else True
    spearman_guardrail_passed = (
        float(val_spearman_ic) > spearman_guardrail_min if spearman_guardrail_enabled else True
    )
    tail_monotonicity_enabled = metric == STRUCTURAL_TAIL_OBJECTIVE
    tail_monotonicity_passed = float(alpha_top_decile) >= float(alpha_top_quintile) if tail_monotonicity_enabled else True
    structural_guardrail_passed = bool(
        auc_guardrail_passed and spearman_guardrail_passed and tail_monotonicity_passed
    )
    objective_value = raw_objective_value if structural_guardrail_passed else HARD_LOSING_OBJECTIVE_VALUE
    return {
        "objective_metric": metric,
        "objective_value": float(objective_value),
        "raw_objective_value": float(raw_objective_value),
        "val_auc": None if auc is None else float(auc),
        "val_spearman_ic": float(val_spearman_ic),
        "structural_metric_name": str(structural_metric_name),
        "auc_guardrail_min": auc_guardrail_min,
        "auc_guardrail_enabled": bool(auc_guardrail_enabled),
        "auc_guardrail_passed": bool(auc_guardrail_passed),
        "spearman_guardrail_min": spearman_guardrail_min,
        "spearman_guardrail_enabled": bool(spearman_guardrail_enabled),
        "spearman_guardrail_passed": bool(spearman_guardrail_passed),
        "tail_monotonicity_enabled": bool(tail_monotonicity_enabled),
        "tail_monotonicity_passed": bool(tail_monotonicity_passed),
        "structural_guardrail_passed": bool(structural_guardrail_passed),
    }


def _validate_objective_runtime_contract(args: argparse.Namespace) -> None:
    if args.objective_metric != STRUCTURAL_TAIL_OBJECTIVE:
        return
    if args.learner_mode == STRUCTURAL_TAIL_REQUIRED_BINARY_LEARNER_MODE:
        if args.weight_mode != STRUCTURAL_TAIL_REQUIRED_BINARY_WEIGHT_MODE:
            raise RuntimeError(
                "structural_tail_objective_requires_weight_mode:"
                f"{STRUCTURAL_TAIL_REQUIRED_BINARY_WEIGHT_MODE}"
            )
        if float(args.min_val_auc) < STRUCTURAL_TAIL_MIN_AUC_FLOOR:
            raise RuntimeError(
                "structural_tail_objective_requires_min_val_auc_at_least:"
                f"{STRUCTURAL_TAIL_MIN_AUC_FLOOR}"
            )
        return
    if args.learner_mode == STRUCTURAL_TAIL_REQUIRED_REGRESSION_LEARNER_MODE:
        if args.weight_mode != STRUCTURAL_TAIL_REQUIRED_REGRESSION_WEIGHT_MODE:
            raise RuntimeError(
                "structural_tail_objective_requires_weight_mode:"
                f"{STRUCTURAL_TAIL_REQUIRED_REGRESSION_WEIGHT_MODE}"
            )
        if float(args.min_val_auc) > 0.0:
            raise RuntimeError("path_b_structural_tail_does_not_use_auc_floor")
        if float(args.min_val_spearman_ic) < STRUCTURAL_TAIL_MIN_SPEARMAN_FLOOR:
            raise RuntimeError(
                "structural_tail_objective_requires_min_val_spearman_ic_at_least:"
                f"{STRUCTURAL_TAIL_MIN_SPEARMAN_FLOOR}"
            )
        return
    raise RuntimeError(
        "structural_tail_objective_requires_learner_mode:"
        f"{STRUCTURAL_TAIL_REQUIRED_BINARY_LEARNER_MODE}"
        f"|{STRUCTURAL_TAIL_REQUIRED_REGRESSION_LEARNER_MODE}"
    )


def _prepare_temporal_split(args: argparse.Namespace) -> dict:
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

    print("[*] Loading immutable train-only base matrix into RAM...", flush=True)
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

    print(f"[*] Orthogonalizing target using temporal key: {time_key}", flush=True)
    df = df.with_columns(
        [
            (
                pl.col("t1_fwd_return") - pl.col("t1_fwd_return").mean().over(["date", time_key])
            ).alias("t1_excess_return")
        ]
    )

    singularity = df.get_column("singularity_vector").fill_nan(0.0).fill_null(0.0).to_numpy()
    X_all = df.select(list(FEATURE_COLS)).to_numpy()
    excess_all = df.get_column("t1_excess_return").to_numpy()
    y_sign_all = (excess_all > 0).astype(int)
    date_all = df.get_column("date").cast(pl.Utf8, strict=False).to_numpy()

    physics_mask = np.abs(singularity) > float(args.singularity_threshold)
    physics_weights_all = np.abs(singularity)
    finite = np.isfinite(physics_weights_all) & (physics_weights_all > 1e-8)
    full_mask = physics_mask & finite

    X_clean = X_all[full_mask]
    y_sign_clean = y_sign_all[full_mask]
    physics_weights_clean = physics_weights_all[full_mask]
    excess_clean = excess_all[full_mask]
    date_clean = date_all[full_mask]

    del df, singularity, X_all, y_sign_all, excess_all, date_all, physics_mask, physics_weights_all, finite, full_mask
    gc.collect()

    train_mask = _year_mask(date_clean, str(args.train_year))
    val_mask = _year_mask(date_clean, str(args.val_year))

    learner_mode = _resolve_learner_mode(args.learner_mode)
    train_rows = int(np.sum(train_mask))
    val_rows = int(np.sum(val_mask))
    if train_rows <= 0 or val_rows <= 0:
        raise RuntimeError(f"temporal_split_empty: train_rows={train_rows} val_rows={val_rows}")
    train_positive_rows = int(np.sum(y_sign_clean[train_mask]))
    val_positive_rows = int(np.sum(y_sign_clean[val_mask]))
    if learner_mode == "binary_logistic_sign":
        if train_positive_rows <= 0 or train_positive_rows >= train_rows:
            raise RuntimeError(
                f"temporal_split_train_one_class: train_rows={train_rows} train_positive_rows={train_positive_rows}"
            )
        if val_positive_rows <= 0 or val_positive_rows >= val_rows:
            raise RuntimeError(
                f"temporal_split_val_one_class: val_rows={val_rows} val_positive_rows={val_positive_rows}"
            )

    train_dates = date_clean[train_mask]
    val_dates = date_clean[val_mask]
    train_max_date = str(np.max(train_dates))
    val_min_date = str(np.min(val_dates))
    if train_max_date >= val_min_date:
        raise RuntimeError(
            f"temporal_split_violation: max(train_date)={train_max_date} min(val_date)={val_min_date}"
        )

    weight_mode = _resolve_weight_mode(args.weight_mode)
    selected_weights_clean = None
    if learner_mode == STRUCTURAL_TAIL_REQUIRED_REGRESSION_LEARNER_MODE and weight_mode != "none":
        raise RuntimeError("regression_learner_requires_weight_mode:none")
    if weight_mode == "none":
        selected_weights_clean = None
    elif weight_mode == "physics_abs_singularity":
        selected_weights_clean = physics_weights_clean
    elif weight_mode == "abs_excess_return":
        selected_weights_clean = np.abs(excess_clean)
    elif weight_mode == "pow_0p875_abs_excess_return":
        selected_weights_clean = np.power(np.abs(excess_clean), 0.875)
    elif weight_mode == "pow_0p75_abs_excess_return":
        selected_weights_clean = np.power(np.abs(excess_clean), 0.75)
    elif weight_mode == "pow_0p625_abs_excess_return":
        selected_weights_clean = np.power(np.abs(excess_clean), 0.625)
    elif weight_mode == "sqrt_abs_excess_return":
        selected_weights_clean = np.sqrt(np.abs(excess_clean))
    else:
        raise RuntimeError(f"unhandled_weight_mode: {weight_mode}")

    train_weights = None
    val_weights = None
    if selected_weights_clean is not None:
        train_weights = selected_weights_clean[train_mask]
        val_weights = selected_weights_clean[val_mask]
        if not np.all(np.isfinite(train_weights)):
            raise RuntimeError("temporal_split_train_weights_non_finite")
        if not np.all(np.isfinite(val_weights)):
            raise RuntimeError("temporal_split_val_weights_non_finite")
        if float(np.sum(train_weights)) <= 0.0:
            raise RuntimeError("temporal_split_train_weights_non_positive")
        if float(np.sum(val_weights)) <= 0.0:
            raise RuntimeError("temporal_split_val_weights_non_positive")

    if learner_mode == "binary_logistic_sign":
        y_train = y_sign_clean[train_mask]
        y_val = y_sign_clean[val_mask]
    else:
        y_train = excess_clean[train_mask]
        y_val = excess_clean[val_mask]

    dtrain_kwargs = {
        "data": X_clean[train_mask],
        "label": y_train,
        "feature_names": list(FEATURE_COLS),
    }
    dval_kwargs = {
        "data": X_clean[val_mask],
        "label": y_val,
        "feature_names": list(FEATURE_COLS),
    }
    if train_weights is not None:
        dtrain_kwargs["weight"] = train_weights
    if val_weights is not None:
        dval_kwargs["weight"] = val_weights

    dtrain = xgb.DMatrix(**dtrain_kwargs)
    dval = xgb.DMatrix(**dval_kwargs)

    summary = {
        "base_matrix_uri": base_uri,
        "train_year": str(args.train_year),
        "val_year": str(args.val_year),
        "train_rows": train_rows,
        "val_rows": val_rows,
        "train_positive_rows": train_positive_rows,
        "val_positive_rows": val_positive_rows,
        "train_max_date": train_max_date,
        "val_min_date": val_min_date,
        "temporal_assertion_passed": True,
        "dtrain_build_count": 1,
        "dval_build_count": 1,
        "learner_mode": learner_mode,
        "weight_mode": weight_mode,
        "weighting_enabled": bool(train_weights is not None),
        "train_weight_sum": None if train_weights is None else float(np.sum(train_weights)),
        "val_weight_sum": None if val_weights is None else float(np.sum(val_weights)),
        "contract_diag": contract_diag,
        "feature_cols": list(FEATURE_COLS),
    }
    print("[GATE] Temporal split passed " + json.dumps(summary, ensure_ascii=False, sort_keys=True), flush=True)

    return {
        "dtrain": dtrain,
        "dval": dval,
        "y_val_sign": y_sign_clean[val_mask],
        "excess_val": excess_clean[val_mask],
        "summary": summary,
        "canonical_fingerprint": _canonical_fingerprint(args),
    }


def _trial_payload(
    trial,
    params: dict,
    auc: float | None,
    val_spearman_ic: float,
    alpha_top_decile: float,
    alpha_top_quintile: float,
    *,
    objective_metric: str = "val_auc",
    min_val_auc: float = 0.0,
    min_val_spearman_ic: float = 0.0,
    learner_mode: str = "binary_logistic_sign",
) -> dict:
    payload = {
        "trial_number": int(trial.number),
        "state": "COMPLETE",
        "val_auc": None if auc is None else float(auc),
        "val_spearman_ic": float(val_spearman_ic),
        "alpha_top_decile": float(alpha_top_decile),
        "alpha_top_quintile": float(alpha_top_quintile),
        "learner_mode": _resolve_learner_mode(learner_mode),
        "max_depth": int(params["max_depth"]),
        "num_boost_round": int(params["num_boost_round"]),
        "params": dict(params),
    }
    payload.update(
        _objective_contract(
            objective_metric,
            auc=auc,
            val_spearman_ic=val_spearman_ic,
            alpha_top_decile=alpha_top_decile,
            alpha_top_quintile=alpha_top_quintile,
            min_val_auc=float(min_val_auc),
            min_val_spearman_ic=float(min_val_spearman_ic),
            learner_mode=_resolve_learner_mode(learner_mode),
        )
    )
    return payload


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="OMEGA v643 temporal Optuna sweep payload")
    ap.add_argument("--base-matrix-uri", required=True)
    ap.add_argument("--output-uri", required=True, help="GCS or local prefix for worker outputs")
    ap.add_argument("--worker-id", default="")
    ap.add_argument("--n-trials", type=int, default=25)
    ap.add_argument("--train-year", default="2023")
    ap.add_argument("--val-year", default="2024")
    ap.add_argument("--early-stopping-rounds", type=int, default=25)
    ap.add_argument("--seed", type=int, default=42)

    ap.add_argument("--singularity-threshold", type=float, default=0.10)
    ap.add_argument("--signal-epi-threshold", type=float, default=0.5)
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=2.0)
    ap.add_argument("--topo-energy-min", type=float, default=2.0)
    ap.add_argument("--objective-metric", default="val_auc")
    ap.add_argument("--min-val-auc", type=float, default=0.0)
    ap.add_argument("--min-val-spearman-ic", type=float, default=0.0)
    ap.add_argument("--weight-mode", default="physics_abs_singularity")
    ap.add_argument("--learner-mode", default="binary_logistic_sign")

    ap.add_argument("--code-bundle-uri", default="")
    args, _ = ap.parse_known_args()
    args.objective_metric = _resolve_objective_metric(args.objective_metric)
    args.weight_mode = _resolve_weight_mode(args.weight_mode)
    args.learner_mode = _resolve_learner_mode(args.learner_mode)
    _validate_objective_runtime_contract(args)

    _install_dependencies()
    if str(args.code_bundle_uri).strip():
        _bootstrap_codebase(args.code_bundle_uri)

    import numpy as np
    import optuna
    import xgboost as xgb
    from sklearn.metrics import roc_auc_score
    from optuna.samplers import TPESampler
    from optuna.trial import TrialState

    t0 = time.time()
    datasets = _prepare_temporal_split(args)
    dtrain = datasets["dtrain"]
    dval = datasets["dval"]
    y_val_sign = datasets["y_val_sign"]
    excess_val = datasets["excess_val"]
    split_summary = datasets["summary"]
    canonical_fingerprint = datasets["canonical_fingerprint"]

    trial_rows: list[dict] = []

    def objective(trial: optuna.Trial) -> float:
        params = {
            "tree_method": "hist",
            "seed": int(args.seed),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "eta": trial.suggest_float("learning_rate", 0.01, 0.20, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "min_child_weight": trial.suggest_float("min_child_weight", 1.0, 12.0),
            "gamma": trial.suggest_float("gamma", 0.0, 5.0),
            "lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
            "alpha": trial.suggest_float("reg_alpha", 1e-4, 10.0, log=True),
            "n_jobs": -1,
        }
        if args.learner_mode == "binary_logistic_sign":
            params["objective"] = "binary:logistic"
            params["eval_metric"] = "auc"
        else:
            params["objective"] = "reg:squarederror"
            params["eval_metric"] = "rmse"
        num_boost_round = trial.suggest_int("num_boost_round", 50, 400)
        evals_result: dict = {}
        booster = xgb.train(
            params=params,
            dtrain=dtrain,
            num_boost_round=int(num_boost_round),
            evals=[(dval, "val")],
            early_stopping_rounds=int(args.early_stopping_rounds),
            evals_result=evals_result,
            verbose_eval=False,
        )
        best_iteration = getattr(booster, "best_iteration", None)
        if best_iteration is None or int(best_iteration) < 0:
            preds = booster.predict(dval)
        else:
            preds = booster.predict(dval, iteration_range=(0, int(best_iteration) + 1))
        val_spearman_ic = _spearman_rank_ic(preds, excess_val)
        auc_defined = len(np.unique(y_val_sign)) > 1
        auc = float(roc_auc_score(y_val_sign, preds)) if auc_defined else None
        alpha_top_decile = _top_quantile_alpha(preds, excess_val, 0.90)
        alpha_top_quintile = _top_quantile_alpha(preds, excess_val, 0.80)

        payload = _trial_payload(
            trial,
            params={
                "max_depth": int(params["max_depth"]),
                "learning_rate": float(params["eta"]),
                "subsample": float(params["subsample"]),
                "colsample_bytree": float(params["colsample_bytree"]),
                "min_child_weight": float(params["min_child_weight"]),
                "gamma": float(params["gamma"]),
                "reg_lambda": float(params["lambda"]),
                "reg_alpha": float(params["alpha"]),
                "num_boost_round": int(num_boost_round),
            },
            auc=auc,
            val_spearman_ic=val_spearman_ic,
            alpha_top_decile=alpha_top_decile,
            alpha_top_quintile=alpha_top_quintile,
            objective_metric=str(args.objective_metric),
            min_val_auc=float(args.min_val_auc),
            min_val_spearman_ic=float(args.min_val_spearman_ic),
            learner_mode=str(args.learner_mode),
        )
        trial_rows.append(payload)
        trial.set_user_attr("alpha_top_decile", alpha_top_decile)
        trial.set_user_attr("alpha_top_quintile", alpha_top_quintile)
        trial.set_user_attr("val_spearman_ic", float(payload["val_spearman_ic"]))
        trial.set_user_attr("learner_mode", str(args.learner_mode))
        trial.set_user_attr("objective_metric", str(payload["objective_metric"]))
        trial.set_user_attr("objective_value", float(payload["objective_value"]))
        trial.set_user_attr("raw_objective_value", float(payload["raw_objective_value"]))
        trial.set_user_attr("auc_guardrail_min", float(payload["auc_guardrail_min"]))
        trial.set_user_attr("auc_guardrail_enabled", bool(payload["auc_guardrail_enabled"]))
        trial.set_user_attr("auc_guardrail_passed", bool(payload["auc_guardrail_passed"]))
        trial.set_user_attr("spearman_guardrail_min", float(payload["spearman_guardrail_min"]))
        trial.set_user_attr("spearman_guardrail_enabled", bool(payload["spearman_guardrail_enabled"]))
        trial.set_user_attr("spearman_guardrail_passed", bool(payload["spearman_guardrail_passed"]))
        trial.set_user_attr("tail_monotonicity_enabled", bool(payload["tail_monotonicity_enabled"]))
        trial.set_user_attr("tail_monotonicity_passed", bool(payload["tail_monotonicity_passed"]))
        trial.set_user_attr("structural_guardrail_passed", bool(payload["structural_guardrail_passed"]))
        return float(payload["objective_value"])

    study = optuna.create_study(direction="maximize", sampler=TPESampler(seed=int(args.seed)))
    study.optimize(objective, n_trials=int(args.n_trials))

    completed = [t for t in study.trials if t.state == TrialState.COMPLETE]
    eligible_rows = [row for row in trial_rows if bool(row.get("structural_guardrail_passed", False))]
    auc_guardrail_rows = [row for row in trial_rows if bool(row.get("auc_guardrail_passed", False))]
    spearman_guardrail_rows = [row for row in trial_rows if bool(row.get("spearman_guardrail_passed", False))]
    best_value = float(study.best_value) if completed else None
    best_params = dict(study.best_params) if completed else {}

    output_prefix = str(args.output_uri).rstrip("/")
    local_summary = Path("study_summary.json")
    local_trials = Path("trials.jsonl")
    summary_payload = {
        "status": "completed" if completed else "no_complete_trials",
        "worker_id": str(args.worker_id),
        "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
        "best_value": best_value,
        "best_params": best_params,
        "n_trials": int(len(study.trials)),
        "n_completed": int(len(completed)),
        "n_auc_guardrail_passed": int(len(auc_guardrail_rows)),
        "n_structural_guardrail_passed": int(len(eligible_rows)),
        "n_auc_floor_passed": int(len(auc_guardrail_rows)),
        "n_spearman_floor_passed": int(len(spearman_guardrail_rows)),
        "seconds": round(time.time() - t0, 2),
        "objective_metric": str(args.objective_metric),
        "auc_guardrail_min": float(args.min_val_auc),
        "spearman_guardrail_min": float(args.min_val_spearman_ic),
        "auc_guardrail_enabled": bool(float(args.min_val_auc) > 0.0 and str(args.objective_metric) != "val_auc"),
        "spearman_guardrail_enabled": bool(
            str(args.objective_metric) == STRUCTURAL_TAIL_OBJECTIVE
            and str(args.learner_mode) == STRUCTURAL_TAIL_REQUIRED_REGRESSION_LEARNER_MODE
        ),
        "tail_monotonicity_required": bool(str(args.objective_metric) == STRUCTURAL_TAIL_OBJECTIVE),
        "learner_mode": str(args.learner_mode),
        "weight_mode": str(args.weight_mode),
        "split_summary": split_summary,
        "canonical_fingerprint": canonical_fingerprint,
        "runtime_versions": {
            "python": sys.version.split()[0],
            "numpy": _resolved_version("numpy"),
            "polars": _resolved_version("polars"),
            "xgboost": _resolved_version("xgboost"),
            "optuna": _resolved_version("optuna"),
            "scikit-learn": _resolved_version("scikit-learn"),
        },
    }
    _write_json(local_summary, summary_payload)
    _write_jsonl(local_trials, trial_rows)

    _upload_file(local_summary, f"{output_prefix}/study_summary.json")
    _upload_file(local_trials, f"{output_prefix}/trials.jsonl")
    print(json.dumps(summary_payload, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
