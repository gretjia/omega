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


def _assign_cross_sectional_deciles(df: pl.DataFrame, signal_col: str) -> pl.DataFrame:
    work = df.filter(pl.col(signal_col).is_not_null())
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
    return work.drop(["__n", "__rank"])


def compute_event_study_for_signal(df: pl.DataFrame, signal_col: str) -> dict[str, object]:
    excess_col, barrier_col = _signal_to_label_columns(signal_col)
    required = {"pure_date", signal_col, excess_col, barrier_col}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"missing required columns for event study: {sorted(missing)}")

    work = df.filter(pl.col(excess_col).is_not_null())
    work = _assign_cross_sectional_deciles(work, signal_col=signal_col)

    deciles = (
        work.group_by("decile")
        .agg(
            [
                pl.len().alias("n_obs"),
                pl.col(excess_col).mean().alias("mean_excess_return"),
                (pl.col(barrier_col) == 1).mean().alias("barrier_win_rate"),
                (pl.col(barrier_col) == -1).mean().alias("barrier_loss_rate"),
                pl.col(signal_col).mean().alias("mean_signal"),
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


def run_event_study(campaign_path: str, signal_cols: Iterable[str]) -> dict[str, object]:
    df = pl.read_parquet(campaign_path)
    results = [compute_event_study_for_signal(df, signal_col=signal_col) for signal_col in signal_cols]
    return {
        "campaign_path": str(campaign_path),
        "signal_cols": list(signal_cols),
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
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    result = run_event_study(campaign_path=args.campaign_path, signal_cols=args.signal_col)
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
