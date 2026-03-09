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


def test_event_study_rejects_missing_columns() -> None:
    df = pl.DataFrame([{"pure_date": "20240102", "Psi_10d": 1.0}])
    with pytest.raises(ValueError):
        event_study.compute_event_study_for_signal(df, "Psi_10d")
