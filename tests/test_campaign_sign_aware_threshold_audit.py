import sys
from pathlib import Path

import pytest

pl = pytest.importorskip("polars")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import run_campaign_sign_aware_threshold_audit as threshold_audit
from tools import run_campaign_transition_event_study as transition_study


def _derived_frame_for_threshold_tests() -> pl.DataFrame:
    rows = []
    for pure_date in ("20240102", "20240103"):
        positive_values = [1.0, 2.0, 3.0, 4.0]
        negative_values = [-1.0, -2.0, -3.0, -4.0]
        for idx, value in enumerate(positive_values, start=1):
            rows.append(
                {
                    "pure_date": pure_date,
                    "symbol": f"{pure_date}_P{idx}",
                    "FreshAmpE_10d": value,
                    "excess_ret_t1_to_10d": 0.08 if value >= 4.0 else 0.02,
                    "barrier_10d": 1 if value >= 4.0 else 0,
                }
            )
        for idx, value in enumerate(negative_values, start=1):
            rows.append(
                {
                    "pure_date": pure_date,
                    "symbol": f"{pure_date}_N{idx}",
                    "FreshAmpE_10d": value,
                    "excess_ret_t1_to_10d": -0.07 if value <= -4.0 else -0.01,
                    "barrier_10d": -1 if value <= -4.0 else 0,
                }
            )
    return pl.DataFrame(rows)


def test_transition_derivation_is_reused_unchanged() -> None:
    assert threshold_audit.derive_transition_columns is transition_study.derive_transition_columns


def test_positive_side_threshold_scores_long_semantics() -> None:
    summary = threshold_audit.compute_sign_aware_threshold_for_signal(
        _derived_frame_for_threshold_tests(),
        signal_col="FreshAmpE_10d",
        side="positive",
        threshold_pct=90.0,
    )

    assert summary["signed_barrier_target"] == 1
    assert summary["signed_mean_excess_return"] > 0.05
    assert summary["sign_aware_hazard_win_rate"] == pytest.approx(1.0)
    assert summary["n_dates_scored"] == 2


def test_negative_side_threshold_scores_short_semantics() -> None:
    summary = threshold_audit.compute_sign_aware_threshold_for_signal(
        _derived_frame_for_threshold_tests(),
        signal_col="FreshAmpE_10d",
        side="negative",
        threshold_pct=90.0,
    )

    assert summary["signed_barrier_target"] == -1
    assert summary["signed_mean_excess_return"] > 0.05
    assert summary["sign_aware_hazard_win_rate"] == pytest.approx(1.0)
    assert summary["n_dates_scored"] == 2


def test_tightening_summary_detects_improving_tail() -> None:
    summaries = threshold_audit.summarize_threshold_tightening(
        [
            {
                "signal_col": "FreshAmpE_10d",
                "side": "positive",
                "threshold_pct": 90.0,
                "signed_mean_excess_return": 0.01,
                "sign_aware_hazard_win_rate": 0.20,
                "n_rows_scored": 10,
            },
            {
                "signal_col": "FreshAmpE_10d",
                "side": "positive",
                "threshold_pct": 95.0,
                "signed_mean_excess_return": 0.03,
                "sign_aware_hazard_win_rate": 0.40,
                "n_rows_scored": 6,
            },
            {
                "signal_col": "FreshAmpE_10d",
                "side": "positive",
                "threshold_pct": 97.5,
                "signed_mean_excess_return": 0.05,
                "sign_aware_hazard_win_rate": 0.60,
                "n_rows_scored": 4,
            },
        ]
    )

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary["signed_mean_excess_non_decreasing"] is True
    assert summary["hazard_win_rate_non_decreasing"] is True
    assert summary["n_rows_non_increasing"] is True
    assert summary["tightening_improves_both"] is True
    assert summary["strongest_threshold_positive"] is True


def test_existing_transition_signal_names_remain_parser_compatible() -> None:
    assert threshold_audit._signal_to_label_columns("dPsiAmpE_10d") == ("excess_ret_t1_to_10d", "barrier_10d")
    assert threshold_audit._signal_to_label_columns("FreshAmpStar_20d") == ("excess_ret_t1_to_20d", "barrier_20d")
