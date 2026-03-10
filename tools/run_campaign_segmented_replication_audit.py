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

from tools.run_campaign_fixed_contract_replication_audit import (
    DEFAULT_SIGNAL_FLOOR,
    THRESHOLD_PCTS,
    run_fixed_contract_replication_audit_from_derived,
)
from tools.run_campaign_transition_event_study import derive_transition_columns

MIN_DATES_SCORED_PER_SEGMENT = 10


def _with_month_bucket(df: pl.DataFrame) -> pl.DataFrame:
    required = {"pure_date"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"missing required columns for month segmentation: {sorted(missing)}")
    return df.with_columns(pl.col("pure_date").cast(pl.String).str.slice(0, 6).alias("__month_bucket"))


def _segment_is_eligible(segment_result: dict[str, object], min_dates_scored: int) -> bool:
    threshold_results = segment_result.get("threshold_results", [])
    if not threshold_results:
        return False
    return all(int(row["n_dates_scored"]) >= int(min_dates_scored) for row in threshold_results)


def summarize_segmented_results(
    segment_results: list[dict[str, object]],
    min_dates_scored: int = MIN_DATES_SCORED_PER_SEGMENT,
) -> dict[str, object]:
    eligible = [row for row in segment_results if bool(row["eligible"])]
    passing = [row for row in eligible if bool(row["segment_pass"])]
    failing = [row for row in eligible if not bool(row["segment_pass"])]
    return {
        "min_dates_scored_per_segment": int(min_dates_scored),
        "n_segments_total": int(len(segment_results)),
        "n_segments_eligible": int(len(eligible)),
        "n_segments_passing": int(len(passing)),
        "n_segments_failing": int(len(failing)),
        "eligible_segments": [str(row["segment_key"]) for row in eligible],
        "passing_segments": [str(row["segment_key"]) for row in passing],
        "failing_segments": [str(row["segment_key"]) for row in failing],
        "mission_pass": bool(len(eligible) >= 2 and len(passing) >= 1 and len(failing) >= 1),
    }


def _segment_passes_shape_checks(segment_result: dict[str, object]) -> bool:
    checks = dict(segment_result.get("checks", {}))
    return all(
        [
            bool(checks.get("counts_non_increasing", False)),
            bool(checks.get("signed_return_non_decreasing", False)),
            bool(checks.get("hazard_non_decreasing", False)),
            bool(checks.get("strongest_threshold_beats_universe_on_both", False)),
            bool(checks.get("strongest_threshold_positive", False)),
        ]
    )


def run_segmented_replication_audit(
    campaign_path: str,
    min_dates_scored: int = MIN_DATES_SCORED_PER_SEGMENT,
    signal_floor: float = DEFAULT_SIGNAL_FLOOR,
) -> dict[str, object]:
    base_df = pl.read_parquet(campaign_path)
    derived = derive_transition_columns(base_df)
    work = _with_month_bucket(derived).sort(["__month_bucket", "symbol", "pure_date"])
    month_keys = work.select(pl.col("__month_bucket").unique().sort()).to_series().to_list()

    segment_results: list[dict[str, object]] = []
    for month_key in month_keys:
        segment_df = work.filter(pl.col("__month_bucket") == month_key).drop("__month_bucket")
        segment_result = run_fixed_contract_replication_audit_from_derived(
            segment_df,
            signal_floor=float(signal_floor),
        )
        eligible = _segment_is_eligible(segment_result, min_dates_scored=min_dates_scored)
        segment_results.append(
            {
                "segment_key": str(month_key),
                "n_rows_input": int(segment_df.height),
                "n_dates_input": int(segment_df.select(pl.col("pure_date").n_unique()).item()) if segment_df.height else 0,
                "eligible": bool(eligible),
                "segment_pass": bool(eligible and _segment_passes_shape_checks(segment_result)),
                **segment_result,
            }
        )

    summary = summarize_segmented_results(segment_results, min_dates_scored=min_dates_scored)
    return {
        "campaign_path": str(campaign_path),
        "threshold_pcts": list(THRESHOLD_PCTS),
        "signal_floor": float(signal_floor),
        **summary,
        "segment_results": segment_results,
    }


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run V660 regime-segmented replication audit on the frozen V659 campaign matrix.")
    ap.add_argument("--campaign-path", required=True, help="Campaign-state parquet path.")
    ap.add_argument("--output-json", default="", help="Optional JSON output path.")
    ap.add_argument(
        "--min-dates-scored-per-segment",
        type=int,
        default=MIN_DATES_SCORED_PER_SEGMENT,
        help="Minimum scored dates required for each threshold inside a segment.",
    )
    ap.add_argument("--signal-floor", type=float, default=DEFAULT_SIGNAL_FLOOR, help="Absolute signal floor.")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    result = run_segmented_replication_audit(
        campaign_path=args.campaign_path,
        min_dates_scored=int(args.min_dates_scored_per_segment),
        signal_floor=float(args.signal_floor),
    )
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
