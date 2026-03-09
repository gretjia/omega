#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import polars as pl


def _signal_to_label_columns(signal_col: str) -> tuple[str, str]:
    suffix = signal_col.split("_", 1)[-1]
    if not suffix:
        raise ValueError(f"cannot infer horizon from signal column: {signal_col}")
    horizon = suffix.replace("Psi_", "").replace("Omega_", "")
    if not horizon.endswith("d"):
        raise ValueError(f"unexpected signal horizon suffix: {signal_col}")
    return f"excess_ret_t1_to_{horizon}", f"barrier_{horizon}"


def _stable_sort_keys(df: pl.DataFrame, signal_col: str) -> list[str]:
    keys = ["pure_date", signal_col]
    if "symbol" in df.columns:
        keys.append("symbol")
    return keys


def _assign_cross_sectional_deciles(
    df: pl.DataFrame,
    signal_col: str,
    signal_floor: float,
) -> tuple[pl.DataFrame, dict[str, float | int]]:
    work = df.filter(pl.col(signal_col).is_not_null())
    n_rows_before_filter = int(work.height)
    work = work.filter(pl.col(signal_col).abs() > float(signal_floor)).sort(_stable_sort_keys(df, signal_col=signal_col))
    date_stats = (
        work.group_by("pure_date")
        .agg(
            [
                pl.len().alias("n_names"),
                pl.col(signal_col).n_unique().alias("n_unique_signal"),
            ]
        )
        .sort("pure_date")
    )
    n_dates_input = int(date_stats.height)
    date_frac_lt10 = float(date_stats.select((pl.col("n_names") < 10).mean()).item() or 0.0) if n_dates_input > 0 else 0.0
    date_frac_flat_signal = (
        float(date_stats.select((pl.col("n_unique_signal") <= 1).mean()).item() or 0.0) if n_dates_input > 0 else 0.0
    )

    work = work.with_columns(
        [
            pl.len().over("pure_date").alias("__n"),
            pl.col(signal_col).rank(method="ordinal").over("pure_date").alias("__rank"),
        ]
    )
    work = work.filter(pl.col("__n") >= 10)
    work = work.with_columns(
        (
            (((pl.col("__rank") - 1) * 10) / pl.col("__n"))
            .floor()
            .clip(0, 9)
            .cast(pl.Int8)
            + 1
        ).alias("decile")
    )
    return work.drop(["__n", "__rank"]), {
        "n_dates_input": n_dates_input,
        "n_dates_scored": int(work.select(pl.col("pure_date").n_unique()).item()) if work.height > 0 else 0,
        "n_rows_before_signal_filter": n_rows_before_filter,
        "n_rows_after_signal_filter": int(work.height),
        "date_frac_lt10": date_frac_lt10,
        "date_frac_flat_signal": date_frac_flat_signal,
    }


def compute_event_study_for_signal(df: pl.DataFrame, signal_col: str, signal_floor: float = 1e-12) -> dict[str, object]:
    excess_col, barrier_col = _signal_to_label_columns(signal_col)
    required = {"pure_date", signal_col, excess_col, barrier_col}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"missing required columns for event study: {sorted(missing)}")

    work = df.filter(pl.col(excess_col).is_not_null())
    work, coverage = _assign_cross_sectional_deciles(work, signal_col=signal_col, signal_floor=signal_floor)

    per_date = (
        work.group_by(["pure_date", "decile"])
        .agg(
            [
                pl.len().alias("n_obs"),
                pl.col(excess_col).mean().alias("date_mean_excess_return"),
                (pl.col(barrier_col) == 1).mean().alias("date_barrier_win_rate"),
                (pl.col(barrier_col) == -1).mean().alias("date_barrier_loss_rate"),
                pl.col(signal_col).mean().alias("date_mean_signal"),
            ]
        )
        .sort(["pure_date", "decile"])
    )

    deciles = (
        per_date.group_by("decile")
        .agg(
            [
                pl.len().alias("n_dates"),
                pl.col("n_obs").sum().alias("n_obs"),
                pl.col("date_mean_excess_return").mean().alias("mean_excess_return"),
                pl.col("date_barrier_win_rate").mean().alias("barrier_win_rate"),
                pl.col("date_barrier_loss_rate").mean().alias("barrier_loss_rate"),
                pl.col("date_mean_signal").mean().alias("mean_signal"),
            ]
        )
        .sort("decile")
    )

    decile_rows = deciles.to_dicts()
    decile_map = {int(row["decile"]): row for row in decile_rows}
    d1 = decile_map.get(1, {})
    d10 = decile_map.get(10, {})
    excess_values = [float(row["mean_excess_return"]) for row in decile_rows]
    monotonic_non_decreasing = all(
        excess_values[idx] >= excess_values[idx - 1] for idx in range(1, len(excess_values))
    )
    monotonic_positive_steps = sum(
        1 for idx in range(1, len(excess_values)) if excess_values[idx] >= excess_values[idx - 1]
    )

    summary = {
        "signal_col": signal_col,
        "excess_col": excess_col,
        "barrier_col": barrier_col,
        "n_rows_input": int(df.height),
        "n_rows_scored": int(work.height),
        "signal_floor": float(signal_floor),
        "n_rows_before_signal_filter": int(coverage["n_rows_before_signal_filter"]),
        "n_rows_after_signal_filter": int(coverage["n_rows_after_signal_filter"]),
        "n_dates_input": int(coverage["n_dates_input"]),
        "n_dates_scored": int(coverage["n_dates_scored"]),
        "date_frac_lt10": float(coverage["date_frac_lt10"]),
        "date_frac_flat_signal": float(coverage["date_frac_flat_signal"]),
        "date_neutral_aggregation": True,
        "deciles": decile_rows,
        "d10_mean_excess_return": float(d10.get("mean_excess_return", 0.0) or 0.0),
        "d1_mean_excess_return": float(d1.get("mean_excess_return", 0.0) or 0.0),
        "d10_minus_d1": float((d10.get("mean_excess_return", 0.0) or 0.0) - (d1.get("mean_excess_return", 0.0) or 0.0)),
        "d10_barrier_win_rate": float(d10.get("barrier_win_rate", 0.0) or 0.0),
        "d1_barrier_win_rate": float(d1.get("barrier_win_rate", 0.0) or 0.0),
        "barrier_win_spread_d10_minus_d1": float((d10.get("barrier_win_rate", 0.0) or 0.0) - (d1.get("barrier_win_rate", 0.0) or 0.0)),
        "monotonic_non_decreasing": bool(monotonic_non_decreasing),
        "monotonic_positive_steps": int(monotonic_positive_steps),
    }
    return summary


def run_event_study(campaign_path: str, signal_cols: Iterable[str], signal_floor: float = 1e-12) -> dict[str, object]:
    df = pl.read_parquet(campaign_path)
    results = [compute_event_study_for_signal(df, signal_col=signal_col, signal_floor=signal_floor) for signal_col in signal_cols]
    return {
        "campaign_path": str(campaign_path),
        "signal_cols": list(signal_cols),
        "signal_floor": float(signal_floor),
        "results": results,
    }


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run V653 pure event study on a forged campaign-state matrix.")
    ap.add_argument("--campaign-path", required=True, help="Campaign-state parquet path.")
    ap.add_argument(
        "--signal-col",
        action="append",
        required=True,
        help="Signal column(s) to test, for example Psi_10d and Psi_20d.",
    )
    ap.add_argument("--output-json", default="", help="Optional JSON output path.")
    ap.add_argument("--signal-floor", type=float, default=1e-12, help="Absolute signal floor; rows at or below this are dropped before deciling.")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    result = run_event_study(campaign_path=args.campaign_path, signal_cols=args.signal_col, signal_floor=float(args.signal_floor))
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
