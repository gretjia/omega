#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_campaign_sign_aware_threshold_audit import (
    NEGATIVE_SIDE,
    compute_sign_aware_threshold_for_signal,
)
from tools.run_campaign_transition_event_study import derive_transition_columns

PRIMARY_SIGNAL_COL = "dPsiAmpE_10d"
PRIMARY_EXCESS_COL = "excess_ret_t1_to_10d"
PRIMARY_BARRIER_COL = "barrier_10d"
DEFAULT_SIGNAL_FLOOR = 1e-12
THRESHOLD_PCTS = (90.0, 95.0, 97.5)
MIN_DATES_SCORED = 40


def _negative_side_universe_summary(
    df: pl.DataFrame,
    signal_col: str = PRIMARY_SIGNAL_COL,
    signal_floor: float = DEFAULT_SIGNAL_FLOOR,
) -> dict[str, object]:
    required = {"pure_date", signal_col, PRIMARY_EXCESS_COL, PRIMARY_BARRIER_COL}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"missing required columns for V659 universe summary: {sorted(missing)}")

    negative = (
        df.filter(pl.col(signal_col).is_not_null() & pl.col(PRIMARY_EXCESS_COL).is_not_null())
        .filter(pl.col(signal_col) < -float(signal_floor))
        .sort(["symbol", "pure_date"])
    )
    if negative.height == 0:
        return {
            "n_rows_scored": 0,
            "n_dates_scored": 0,
            "date_neutral_signed_return": 0.0,
            "date_neutral_hazard_win_rate": 0.0,
        }

    per_date = (
        negative.group_by("pure_date")
        .agg(
            [
                pl.len().alias("n_obs"),
                (-pl.col(PRIMARY_EXCESS_COL)).mean().alias("date_mean_signed_return"),
                (pl.col(PRIMARY_BARRIER_COL) == -1).mean().alias("date_hazard_win_rate"),
            ]
        )
        .sort("pure_date")
    )
    return {
        "n_rows_scored": int(negative.height),
        "n_dates_scored": int(per_date.height),
        "date_neutral_signed_return": float(per_date["date_mean_signed_return"].mean() or 0.0),
        "date_neutral_hazard_win_rate": float(per_date["date_hazard_win_rate"].mean() or 0.0),
    }


def run_fixed_contract_replication_audit_from_derived(
    df: pl.DataFrame,
    signal_floor: float = DEFAULT_SIGNAL_FLOOR,
) -> dict[str, object]:
    threshold_results = [
        compute_sign_aware_threshold_for_signal(
            df,
            signal_col=PRIMARY_SIGNAL_COL,
            side=NEGATIVE_SIDE,
            threshold_pct=threshold_pct,
            signal_floor=signal_floor,
        )
        for threshold_pct in THRESHOLD_PCTS
    ]
    threshold_results = sorted(threshold_results, key=lambda row: float(row["threshold_pct"]))
    universe = _negative_side_universe_summary(df, signal_col=PRIMARY_SIGNAL_COL, signal_floor=signal_floor)

    scored_date_counts = [int(row["n_dates_scored"]) for row in threshold_results]
    scored_row_counts = [int(row["n_rows_scored"]) for row in threshold_results]
    signed_returns = [float(row["signed_mean_excess_return"]) for row in threshold_results]
    hazard_rates = [float(row["sign_aware_hazard_win_rate"]) for row in threshold_results]

    coverage_pass = all(value >= MIN_DATES_SCORED for value in scored_date_counts)
    counts_non_increasing = all(scored_row_counts[idx] <= scored_row_counts[idx - 1] for idx in range(1, len(scored_row_counts)))
    signed_return_non_decreasing = all(signed_returns[idx] >= signed_returns[idx - 1] for idx in range(1, len(signed_returns)))
    hazard_non_decreasing = all(hazard_rates[idx] >= hazard_rates[idx - 1] for idx in range(1, len(hazard_rates)))
    strongest_beats_universe_on_both = (
        signed_returns[-1] > float(universe["date_neutral_signed_return"])
        and hazard_rates[-1] > float(universe["date_neutral_hazard_win_rate"])
    )
    strongest_positive = signed_returns[-1] > 0.0

    mission_pass = all(
        [
            coverage_pass,
            counts_non_increasing,
            signed_return_non_decreasing,
            hazard_non_decreasing,
            strongest_beats_universe_on_both,
            strongest_positive,
        ]
    )

    return {
        "signal_col": PRIMARY_SIGNAL_COL,
        "side": NEGATIVE_SIDE,
        "threshold_pcts": list(THRESHOLD_PCTS),
        "signal_floor": float(signal_floor),
        "negative_side_universe": universe,
        "threshold_results": threshold_results,
        "checks": {
            "coverage_pass": coverage_pass,
            "counts_non_increasing": counts_non_increasing,
            "signed_return_non_decreasing": signed_return_non_decreasing,
            "hazard_non_decreasing": hazard_non_decreasing,
            "strongest_threshold_beats_universe_on_both": strongest_beats_universe_on_both,
            "strongest_threshold_positive": strongest_positive,
        },
        "mission_pass": mission_pass,
    }


def run_fixed_contract_replication_audit(
    campaign_path: str,
    signal_floor: float = DEFAULT_SIGNAL_FLOOR,
) -> dict[str, object]:
    base_df = pl.read_parquet(campaign_path)
    derived = derive_transition_columns(base_df)
    result = run_fixed_contract_replication_audit_from_derived(derived, signal_floor=signal_floor)
    return {
        "campaign_path": str(campaign_path),
        **result,
    }


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run V659 fixed-contract replication audit on a forged campaign-state matrix.")
    ap.add_argument("--campaign-path", required=True, help="Campaign-state parquet path.")
    ap.add_argument("--output-json", default="", help="Optional JSON output path.")
    ap.add_argument("--signal-floor", type=float, default=DEFAULT_SIGNAL_FLOOR, help="Absolute signal floor for negative-side selection.")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    result = run_fixed_contract_replication_audit(
        campaign_path=args.campaign_path,
        signal_floor=float(args.signal_floor),
    )
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
