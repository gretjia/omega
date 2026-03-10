#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_campaign_event_study import _signal_to_label_columns
from tools.run_campaign_transition_event_study import DEFAULT_SIGNAL_COLS, derive_transition_columns

DEFAULT_THRESHOLD_PCTS = [90.0, 95.0, 97.5]
POSITIVE_SIDE = "positive"
NEGATIVE_SIDE = "negative"
DEFAULT_SIDES = [POSITIVE_SIDE, NEGATIVE_SIDE]


def _validate_side(side: str) -> str:
    normalized = side.strip().lower()
    if normalized not in {POSITIVE_SIDE, NEGATIVE_SIDE}:
        raise ValueError(f"unsupported sign-aware side: {side}")
    return normalized


def _side_barrier_value(side: str) -> int:
    return 1 if side == POSITIVE_SIDE else -1


def _prepare_side_frame(
    df: pl.DataFrame,
    signal_col: str,
    side: str,
    threshold_pct: float,
    signal_floor: float,
) -> tuple[pl.DataFrame, dict[str, int | float | str]]:
    excess_col, barrier_col = _signal_to_label_columns(signal_col)
    required = {"pure_date", signal_col, excess_col, barrier_col}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"missing required columns for sign-aware audit: {sorted(missing)}")

    side = _validate_side(side)
    work = df.filter(pl.col(signal_col).is_not_null() & pl.col(excess_col).is_not_null())
    n_rows_input = int(work.height)
    if side == POSITIVE_SIDE:
        work = work.filter(pl.col(signal_col) > float(signal_floor))
    else:
        work = work.filter(pl.col(signal_col) < -float(signal_floor))
    n_rows_side_input = int(work.height)

    if work.height == 0:
        return work, {
            "signal_col": signal_col,
            "side": side,
            "threshold_pct": float(threshold_pct),
            "n_rows_input": n_rows_input,
            "n_rows_side_input": n_rows_side_input,
            "n_dates_input": 0,
            "n_dates_scored": 0,
            "n_rows_scored": 0,
        }

    work = work.with_columns(pl.col(signal_col).abs().alias("__abs_signal"))
    thresholds = (
        work.group_by("pure_date")
        .agg(
            [
                pl.len().alias("__n_side"),
                pl.col("__abs_signal").quantile(float(threshold_pct) / 100.0).alias("__abs_threshold"),
            ]
        )
        .sort("pure_date")
    )
    selected = (
        work.join(thresholds, on="pure_date", how="inner")
        .filter(pl.col("__abs_signal") >= pl.col("__abs_threshold"))
        .drop(["__abs_signal", "__n_side", "__abs_threshold"])
    )
    coverage = {
        "signal_col": signal_col,
        "side": side,
        "threshold_pct": float(threshold_pct),
        "n_rows_input": n_rows_input,
        "n_rows_side_input": n_rows_side_input,
        "n_dates_input": int(thresholds.height),
        "n_dates_scored": int(selected.select(pl.col("pure_date").n_unique()).item()) if selected.height > 0 else 0,
        "n_rows_scored": int(selected.height),
    }
    return selected, coverage


def compute_sign_aware_threshold_for_signal(
    df: pl.DataFrame,
    signal_col: str,
    side: str,
    threshold_pct: float,
    signal_floor: float = 1e-12,
) -> dict[str, object]:
    side = _validate_side(side)
    excess_col, barrier_col = _signal_to_label_columns(signal_col)
    selected, coverage = _prepare_side_frame(
        df,
        signal_col=signal_col,
        side=side,
        threshold_pct=float(threshold_pct),
        signal_floor=float(signal_floor),
    )

    if selected.height == 0:
        return {
            "signal_col": signal_col,
            "side": side,
            "threshold_pct": float(threshold_pct),
            "excess_col": excess_col,
            "barrier_col": barrier_col,
            "date_neutral_aggregation": True,
            "signed_barrier_target": int(_side_barrier_value(side)),
            **coverage,
            "signed_mean_excess_return": 0.0,
            "sign_aware_hazard_win_rate": 0.0,
            "per_date": [],
        }

    if side == POSITIVE_SIDE:
        signed_excess_expr = pl.col(excess_col)
    else:
        signed_excess_expr = -pl.col(excess_col)
    target_barrier = _side_barrier_value(side)

    per_date = (
        selected.group_by("pure_date")
        .agg(
            [
                pl.len().alias("n_obs"),
                signed_excess_expr.mean().alias("date_mean_signed_excess_return"),
                (pl.col(barrier_col) == target_barrier).mean().alias("date_sign_aware_hazard_win_rate"),
                pl.col(signal_col).mean().alias("date_mean_signal"),
            ]
        )
        .sort("pure_date")
    )

    summary = {
        "signal_col": signal_col,
        "side": side,
        "threshold_pct": float(threshold_pct),
        "excess_col": excess_col,
        "barrier_col": barrier_col,
        "signed_barrier_target": int(target_barrier),
        "date_neutral_aggregation": True,
        **coverage,
        "signed_mean_excess_return": float(per_date["date_mean_signed_excess_return"].mean() or 0.0),
        "sign_aware_hazard_win_rate": float(per_date["date_sign_aware_hazard_win_rate"].mean() or 0.0),
        "per_date": per_date.to_dicts(),
    }
    return summary


def summarize_threshold_tightening(results: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in results:
        grouped.setdefault((str(row["signal_col"]), str(row["side"])), []).append(row)

    summaries: list[dict[str, object]] = []
    for (signal_col, side), group_rows in sorted(grouped.items()):
        ordered = sorted(group_rows, key=lambda row: float(row["threshold_pct"]))
        excess_values = [float(row["signed_mean_excess_return"]) for row in ordered]
        hazard_values = [float(row["sign_aware_hazard_win_rate"]) for row in ordered]
        n_rows_values = [int(row["n_rows_scored"]) for row in ordered]
        summaries.append(
            {
                "signal_col": signal_col,
                "side": side,
                "thresholds": [float(row["threshold_pct"]) for row in ordered],
                "signed_mean_excess_returns": excess_values,
                "sign_aware_hazard_win_rates": hazard_values,
                "n_rows_scored": n_rows_values,
                "signed_mean_excess_non_decreasing": all(
                    excess_values[idx] >= excess_values[idx - 1] for idx in range(1, len(excess_values))
                ),
                "hazard_win_rate_non_decreasing": all(
                    hazard_values[idx] >= hazard_values[idx - 1] for idx in range(1, len(hazard_values))
                ),
                "n_rows_non_increasing": all(
                    n_rows_values[idx] <= n_rows_values[idx - 1] for idx in range(1, len(n_rows_values))
                ),
                "tightening_improves_both": all(
                    excess_values[idx] >= excess_values[idx - 1] and hazard_values[idx] >= hazard_values[idx - 1]
                    for idx in range(1, len(excess_values))
                ),
                "strongest_threshold_positive": bool(excess_values[-1] > 0.0 and hazard_values[-1] > 0.0),
            }
        )
    return summaries


def run_sign_aware_threshold_audit(
    campaign_path: str,
    signal_cols: Iterable[str] | None = None,
    threshold_pcts: Iterable[float] | None = None,
    sides: Iterable[str] | None = None,
    signal_floor: float = 1e-12,
) -> dict[str, object]:
    base_df = pl.read_parquet(campaign_path)
    derived = derive_transition_columns(base_df)
    active_signal_cols = list(signal_cols) if signal_cols else list(DEFAULT_SIGNAL_COLS)
    active_threshold_pcts = list(threshold_pcts) if threshold_pcts else list(DEFAULT_THRESHOLD_PCTS)
    active_sides = [_validate_side(side) for side in (sides or DEFAULT_SIDES)]

    results: list[dict[str, object]] = []
    for signal_col in active_signal_cols:
        for side in active_sides:
            for threshold_pct in active_threshold_pcts:
                results.append(
                    compute_sign_aware_threshold_for_signal(
                        derived,
                        signal_col=signal_col,
                        side=side,
                        threshold_pct=float(threshold_pct),
                        signal_floor=float(signal_floor),
                    )
                )

    series_summaries = summarize_threshold_tightening(results)
    return {
        "campaign_path": str(campaign_path),
        "signal_cols": active_signal_cols,
        "threshold_pcts": [float(value) for value in active_threshold_pcts],
        "sides": active_sides,
        "signal_floor": float(signal_floor),
        "results": results,
        "series_summaries": series_summaries,
    }


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run V657 sign-aware threshold / hazard audit on the frozen V655B campaign-state matrix.")
    ap.add_argument("--campaign-path", required=True, help="Campaign-state parquet path.")
    ap.add_argument(
        "--signal-col",
        action="append",
        default=[],
        help="Optional transition signal column(s) to test. Defaults to the canonical V656 eight-signal set.",
    )
    ap.add_argument(
        "--threshold-pct",
        action="append",
        type=float,
        default=[],
        help="Optional threshold percentile(s). Defaults to 90, 95, 97.5.",
    )
    ap.add_argument(
        "--side",
        action="append",
        default=[],
        help="Optional sides to test: positive and/or negative. Defaults to both.",
    )
    ap.add_argument("--output-json", default="", help="Optional JSON output path.")
    ap.add_argument("--signal-floor", type=float, default=1e-12, help="Absolute signal floor used before side-specific thresholding.")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    result = run_sign_aware_threshold_audit(
        campaign_path=args.campaign_path,
        signal_cols=args.signal_col,
        threshold_pcts=args.threshold_pct,
        sides=args.side,
        signal_floor=float(args.signal_floor),
    )
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
