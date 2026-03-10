#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_campaign_transition_event_study import derive_transition_columns

PRIMARY_SIGNAL_COL = "dPsiAmpE_10d"
SHADOW_SIGNAL_COL = "FreshAmpStar_10d"
PRIMARY_EXCESS_COL = "excess_ret_t1_to_10d"
PRIMARY_BARRIER_COL = "barrier_10d"
ADMISSION_THRESHOLD_PCT = 90.0
SELECTION_FRACTIONS = (0.50, 0.25)
FEATURE_COLS = [
    "dPsiAmpE_10d",
    "FreshAmpStar_10d",
    "PsiAmpE_10d",
    "PsiAmpStar_10d",
    "OmegaAmpE_10d",
    "OmegaAmpStar_10d",
    "vol20d",
    "pulse_count",
    "pulse_concentration",
]
XGB_PARAMS = {
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "max_depth": 3,
    "eta": 0.05,
    "min_child_weight": 20.0,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "tree_method": "hist",
    "seed": 42,
}
NUM_BOOST_ROUND = 120
DEFAULT_SIGNAL_FLOOR = 1e-12
EPS = 1e-9


def _require_columns(df: pl.DataFrame, required: list[str] | set[str], context: str) -> None:
    missing = set(required).difference(df.columns)
    if missing:
        raise ValueError(f"missing required columns for {context}: {sorted(missing)}")


def build_admission_frame_from_derived(
    df: pl.DataFrame,
    signal_floor: float = DEFAULT_SIGNAL_FLOOR,
    threshold_pct: float = ADMISSION_THRESHOLD_PCT,
) -> tuple[pl.DataFrame, dict[str, int | float | str]]:
    required = {"pure_date", "symbol", PRIMARY_SIGNAL_COL, PRIMARY_EXCESS_COL, PRIMARY_BARRIER_COL, *FEATURE_COLS}
    _require_columns(df, required, "V658 admission frame")

    work = df.filter(pl.col(PRIMARY_SIGNAL_COL).is_not_null() & pl.col(PRIMARY_EXCESS_COL).is_not_null()).sort(
        ["symbol", "pure_date"]
    )
    negative = (
        work.filter(pl.col(PRIMARY_SIGNAL_COL) < -float(signal_floor))
        .with_columns(pl.col(PRIMARY_SIGNAL_COL).abs().alias("__admission_abs_signal"))
    )

    if negative.height == 0:
        empty = negative.with_columns(
            [
                pl.lit(False).alias("__admission_mask"),
                pl.lit(0).cast(pl.Int8).alias("__label"),
                pl.lit(0.0).alias("__signed_return"),
            ]
        )
        return empty, {
            "n_rows_input": int(work.height),
            "n_rows_negative_side": 0,
            "n_rows_admitted": 0,
            "n_dates_negative_side": 0,
            "n_dates_admitted": 0,
            "threshold_pct": float(threshold_pct),
        }

    thresholds = (
        negative.group_by("pure_date")
        .agg(pl.col("__admission_abs_signal").quantile(float(threshold_pct) / 100.0).alias("__admission_threshold"))
        .sort("pure_date")
    )

    admitted = (
        negative.join(thresholds, on="pure_date", how="inner")
        .filter(pl.col("__admission_abs_signal") >= pl.col("__admission_threshold"))
        .with_columns(
            [
                pl.lit(True).alias("__admission_mask"),
                (pl.col(PRIMARY_BARRIER_COL) == -1).cast(pl.Int8).alias("__label"),
                (-pl.col(PRIMARY_EXCESS_COL)).alias("__signed_return"),
            ]
        )
    )

    feature_exprs = [pl.col(col).cast(pl.Float64, strict=False).fill_null(0.0).fill_nan(0.0).alias(col) for col in FEATURE_COLS]
    admitted = admitted.with_columns(feature_exprs).sort(["symbol", "pure_date"])

    coverage = {
        "n_rows_input": int(work.height),
        "n_rows_negative_side": int(negative.height),
        "n_rows_admitted": int(admitted.height),
        "n_dates_negative_side": int(negative.select(pl.col("pure_date").n_unique()).item()) if negative.height > 0 else 0,
        "n_dates_admitted": int(admitted.select(pl.col("pure_date").n_unique()).item()) if admitted.height > 0 else 0,
        "threshold_pct": float(threshold_pct),
    }
    return admitted, coverage


def build_admission_frame(
    campaign_path: str,
    signal_floor: float = DEFAULT_SIGNAL_FLOOR,
    threshold_pct: float = ADMISSION_THRESHOLD_PCT,
) -> tuple[pl.DataFrame, dict[str, int | float | str]]:
    base_df = pl.read_parquet(campaign_path)
    derived = derive_transition_columns(base_df)
    return build_admission_frame_from_derived(derived, signal_floor=signal_floor, threshold_pct=threshold_pct)


def build_forward_folds(pure_dates: list[str]) -> list[dict[str, object]]:
    ordered = sorted(dict.fromkeys(pure_dates))
    n_dates = len(ordered)
    if n_dates < 5:
        raise ValueError(f"need at least 5 ordered dates for V658 folds, got {n_dates}")

    a_train_end = max(1, int(math.floor(n_dates * 0.60)))
    a_val_len = max(1, int(math.floor(n_dates * 0.20)))
    a_val_end = min(n_dates, a_train_end + a_val_len)
    if a_val_end <= a_train_end:
        a_val_end = min(n_dates, a_train_end + 1)

    b_train_end = max(a_val_end, int(math.floor(n_dates * 0.80)))
    if b_train_end >= n_dates:
        b_train_end = n_dates - 1

    folds = [
        {
            "fold_name": "fold_a",
            "train_dates": ordered[:a_train_end],
            "val_dates": ordered[a_train_end:a_val_end],
        },
        {
            "fold_name": "fold_b",
            "train_dates": ordered[:b_train_end],
            "val_dates": ordered[b_train_end:],
        },
    ]
    for fold in folds:
        if not fold["train_dates"] or not fold["val_dates"]:
            raise ValueError(f"invalid fold definition for {fold['fold_name']}")
    return folds


def _binary_logloss(y_true: np.ndarray, prob: np.ndarray) -> float:
    clipped = np.clip(prob.astype(np.float64), EPS, 1.0 - EPS)
    labels = y_true.astype(np.float64)
    return float(-(labels * np.log(clipped) + (1.0 - labels) * np.log(1.0 - clipped)).mean())


def _train_fixed_binary_logistic(train_df: pl.DataFrame) -> tuple[object | None, float]:
    y_train = train_df["__label"].to_numpy()
    base_prob = float(np.clip(float(y_train.mean()) if y_train.size > 0 else 0.0, EPS, 1.0 - EPS))
    if train_df.height <= 0 or np.unique(y_train).size < 2:
        return None, base_prob

    import xgboost as xgb

    x_train = train_df.select(FEATURE_COLS).to_numpy()
    dtrain = xgb.DMatrix(x_train, label=y_train.astype(np.float64), feature_names=FEATURE_COLS)
    booster = xgb.train(dict(XGB_PARAMS), dtrain, num_boost_round=NUM_BOOST_ROUND)
    return booster, base_prob


def _predict_prob(model: object | None, df: pl.DataFrame, base_prob: float) -> np.ndarray:
    if df.height <= 0:
        return np.zeros(0, dtype=np.float64)
    if model is None:
        return np.full(df.height, base_prob, dtype=np.float64)

    import xgboost as xgb

    x_val = df.select(FEATURE_COLS).to_numpy()
    dval = xgb.DMatrix(x_val, feature_names=FEATURE_COLS)
    return np.asarray(model.predict(dval), dtype=np.float64)


def _select_top_fraction_per_date(df: pl.DataFrame, score_col: str, alpha: float) -> pl.DataFrame:
    if df.height <= 0:
        return df
    thresholds = (
        df.group_by("pure_date")
        .agg(pl.col(score_col).quantile(1.0 - float(alpha)).alias("__score_threshold"))
        .sort("pure_date")
    )
    return (
        df.join(thresholds, on="pure_date", how="inner")
        .filter(pl.col(score_col) >= pl.col("__score_threshold"))
        .drop("__score_threshold")
    )


def _summarize_selection(df: pl.DataFrame) -> dict[str, object]:
    if df.height <= 0:
        return {
            "n_dates_scored": 0,
            "n_rows_scored": 0,
            "date_neutral_signed_return": 0.0,
            "date_neutral_hazard_win_rate": 0.0,
        }
    per_date = (
        df.group_by("pure_date")
        .agg(
            [
                pl.len().alias("n_obs"),
                pl.col("__signed_return").mean().alias("date_mean_signed_return"),
                pl.col("__label").mean().alias("date_hazard_win_rate"),
            ]
        )
        .sort("pure_date")
    )
    return {
        "n_dates_scored": int(per_date.height),
        "n_rows_scored": int(df.height),
        "date_neutral_signed_return": float(per_date["date_mean_signed_return"].mean() or 0.0),
        "date_neutral_hazard_win_rate": float(per_date["date_hazard_win_rate"].mean() or 0.0),
    }


def evaluate_selection_fraction(admitted_val_df: pl.DataFrame, alpha: float) -> dict[str, object]:
    model_selected = _select_top_fraction_per_date(admitted_val_df, "__pred_prob", alpha=float(alpha))
    raw_selected = _select_top_fraction_per_date(admitted_val_df, "__admission_abs_signal", alpha=float(alpha))
    model_summary = _summarize_selection(model_selected)
    raw_summary = _summarize_selection(raw_selected)
    return {
        "alpha": float(alpha),
        "model": model_summary,
        "raw_same_count": raw_summary,
        "model_beats_raw_on_signed_return": bool(
            model_summary["date_neutral_signed_return"] > raw_summary["date_neutral_signed_return"]
        ),
        "model_beats_raw_on_hazard": bool(
            model_summary["date_neutral_hazard_win_rate"] > raw_summary["date_neutral_hazard_win_rate"]
        ),
        "model_beats_raw_on_both": bool(
            model_summary["date_neutral_signed_return"] > raw_summary["date_neutral_signed_return"]
            and model_summary["date_neutral_hazard_win_rate"] > raw_summary["date_neutral_hazard_win_rate"]
        ),
    }


def run_fold(admitted_df: pl.DataFrame, fold_name: str, train_dates: list[str], val_dates: list[str]) -> dict[str, object]:
    train_df = admitted_df.filter(pl.col("pure_date").is_in(train_dates))
    val_df = admitted_df.filter(pl.col("pure_date").is_in(val_dates))
    if train_df.height <= 0 or val_df.height <= 0:
        raise ValueError(f"{fold_name} has empty admitted train or validation set")

    model, base_prob = _train_fixed_binary_logistic(train_df)
    y_val = val_df["__label"].to_numpy()
    pred_prob = _predict_prob(model, val_df, base_prob)
    logloss_model = _binary_logloss(y_val, pred_prob)
    logloss_constant = _binary_logloss(y_val, np.full(val_df.height, base_prob, dtype=np.float64))

    scored_val = val_df.with_columns(pl.Series("__pred_prob", pred_prob, dtype=pl.Float64))
    alpha_summaries = [evaluate_selection_fraction(scored_val, alpha=alpha) for alpha in SELECTION_FRACTIONS]
    fold_pass = bool(
        logloss_model < logloss_constant and any(item["model_beats_raw_on_both"] for item in alpha_summaries)
    )

    return {
        "fold_name": fold_name,
        "train_dates": {
            "n_dates": len(train_dates),
            "min": train_dates[0],
            "max": train_dates[-1],
        },
        "val_dates": {
            "n_dates": len(val_dates),
            "min": val_dates[0],
            "max": val_dates[-1],
        },
        "n_train_rows": int(train_df.height),
        "n_val_rows": int(val_df.height),
        "train_positive_rate": float(train_df["__label"].mean() or 0.0),
        "val_positive_rate": float(val_df["__label"].mean() or 0.0),
        "logloss_model": float(logloss_model),
        "logloss_constant": float(logloss_constant),
        "used_constant_only": bool(model is None),
        "alpha_summaries": alpha_summaries,
        "fold_pass": fold_pass,
    }


def run_ml_admission_probe(
    campaign_path: str,
    signal_floor: float = DEFAULT_SIGNAL_FLOOR,
    threshold_pct: float = ADMISSION_THRESHOLD_PCT,
) -> dict[str, object]:
    admitted_df, coverage = build_admission_frame(
        campaign_path=campaign_path,
        signal_floor=float(signal_floor),
        threshold_pct=float(threshold_pct),
    )
    if admitted_df.height <= 0:
        raise ValueError("V658 admission frame is empty")

    folds = build_forward_folds(admitted_df["pure_date"].unique().to_list())
    fold_results = [run_fold(admitted_df, fold["fold_name"], fold["train_dates"], fold["val_dates"]) for fold in folds]
    mission_pass = all(fold["fold_pass"] for fold in fold_results)
    return {
        "campaign_path": str(campaign_path),
        "primary_signal_col": PRIMARY_SIGNAL_COL,
        "shadow_signal_col": SHADOW_SIGNAL_COL,
        "side": "negative",
        "threshold_pct": float(threshold_pct),
        "selection_fractions": list(SELECTION_FRACTIONS),
        "feature_cols": list(FEATURE_COLS),
        "xgb_params": dict(XGB_PARAMS),
        "num_boost_round": int(NUM_BOOST_ROUND),
        "coverage": coverage,
        "fold_results": fold_results,
        "mission_pass": bool(mission_pass),
    }


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run V658 negative-tail hazard admission probe on the frozen V655B campaign-state matrix.")
    ap.add_argument("--campaign-path", required=True, help="Campaign-state parquet path.")
    ap.add_argument("--output-json", default="", help="Optional JSON output path.")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    result = run_ml_admission_probe(campaign_path=args.campaign_path)
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
