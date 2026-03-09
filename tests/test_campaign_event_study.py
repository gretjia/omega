import sys
from pathlib import Path

import pytest

pl = pytest.importorskip("polars")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import run_campaign_event_study as event_study


def test_event_study_detects_positive_decile_spread() -> None:
    rows = []
    for date_idx, pure_date in enumerate(["20240102", "20240103"]):
        for decile in range(1, 11):
            rows.append(
                {
                    "pure_date": pure_date,
                    "symbol": f"S{date_idx:02d}{decile:02d}",
                    "Psi_10d": float(decile),
                    "excess_ret_t1_to_10d": float(decile) / 100.0,
                    "barrier_10d": 1 if decile >= 8 else (-1 if decile <= 2 else 0),
                }
            )
    df = pl.DataFrame(rows)

    summary = event_study.compute_event_study_for_signal(df, "Psi_10d")

    assert summary["d10_mean_excess_return"] > 0
    assert summary["d10_minus_d1"] > 0
    assert summary["d10_barrier_win_rate"] > summary["d1_barrier_win_rate"]
    assert summary["monotonic_non_decreasing"] is True
    assert summary["date_neutral_aggregation"] is True
    assert summary["n_dates_input"] == 2
    assert summary["n_dates_scored"] == 2
    assert summary["date_frac_lt10"] == 0.0
    assert summary["n_rows_before_signal_filter"] == 20
    assert summary["n_rows_after_signal_filter"] == 20


def test_event_study_rejects_missing_columns() -> None:
    df = pl.DataFrame([{"pure_date": "20240102", "Psi_10d": 1.0}])
    with pytest.raises(ValueError):
        event_study.compute_event_study_for_signal(df, "Psi_10d")


def test_event_study_aggregates_date_neutrally() -> None:
    rows = []
    for decile in range(1, 11):
        rows.append(
            {
                "pure_date": "20240102",
                "symbol": f"A{decile:02d}",
                "Psi_10d": float(decile),
                "excess_ret_t1_to_10d": 0.10 if decile == 10 else 0.0,
                "barrier_10d": 1 if decile == 10 else 0,
            }
        )
    for decile in range(1, 11):
        for copy_idx in range(2):
            rows.append(
                {
                    "pure_date": "20240103",
                    "symbol": f"B{decile:02d}_{copy_idx}",
                    "Psi_10d": float(decile) + (copy_idx / 1000.0),
                    "excess_ret_t1_to_10d": 0.0,
                    "barrier_10d": 0,
                }
            )

    summary = event_study.compute_event_study_for_signal(pl.DataFrame(rows), "Psi_10d")

    assert summary["n_dates_input"] == 2
    assert summary["n_dates_scored"] == 2
    assert summary["d10_mean_excess_return"] == pytest.approx(0.05)
    assert summary["d10_barrier_win_rate"] == pytest.approx(0.5)


def test_event_study_filters_zero_signal_rows_before_deciling() -> None:
    rows = []
    for pure_date in ["20240102", "20240103"]:
        for decile in range(1, 11):
            rows.append(
                {
                    "pure_date": pure_date,
                    "symbol": f"{pure_date}_{decile:02d}",
                    "Psi_10d": float(decile),
                    "excess_ret_t1_to_10d": float(decile) / 100.0,
                    "barrier_10d": 1 if decile >= 8 else 0,
                }
            )
        for zero_idx in range(5):
            rows.append(
                {
                    "pure_date": pure_date,
                    "symbol": f"{pure_date}_Z{zero_idx}",
                    "Psi_10d": 0.0,
                    "excess_ret_t1_to_10d": -1.0,
                    "barrier_10d": -1,
                }
            )

    summary = event_study.compute_event_study_for_signal(pl.DataFrame(rows), "Psi_10d")

    assert summary["n_rows_before_signal_filter"] == 30
    assert summary["n_rows_after_signal_filter"] == 20
    assert summary["n_rows_scored"] == 20
    assert summary["d10_mean_excess_return"] > 0.0
