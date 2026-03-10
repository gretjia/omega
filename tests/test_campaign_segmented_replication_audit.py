import sys
from pathlib import Path

import pytest

pl = pytest.importorskip("polars")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import run_campaign_segmented_replication_audit as segmented_audit


def test_month_bucket_partition_uses_pure_date_prefix() -> None:
    df = pl.DataFrame(
        {
            "symbol": ["AAA", "AAA", "AAA"],
            "pure_date": ["20230509", "20230531", "20230601"],
        }
    )
    out = segmented_audit._with_month_bucket(df)
    assert out["__month_bucket"].to_list() == ["202305", "202305", "202306"]


def test_segment_eligibility_requires_min_dates_for_each_threshold() -> None:
    segment_result = {
        "threshold_results": [
            {"n_dates_scored": 10},
            {"n_dates_scored": 10},
            {"n_dates_scored": 9},
        ]
    }
    assert segmented_audit._segment_is_eligible(segment_result, min_dates_scored=10) is False


def test_summary_requires_mixed_pass_and_fail_among_eligible_segments() -> None:
    summary = segmented_audit.summarize_segmented_results(
        [
            {"segment_key": "202305", "eligible": True, "segment_pass": True},
            {"segment_key": "202306", "eligible": True, "segment_pass": False},
            {"segment_key": "202307", "eligible": False, "segment_pass": False},
        ],
        min_dates_scored=10,
    )
    assert summary["n_segments_eligible"] == 2
    assert summary["n_segments_passing"] == 1
    assert summary["n_segments_failing"] == 1
    assert summary["mission_pass"] is True


def test_summary_fails_when_no_eligible_segment_passes() -> None:
    summary = segmented_audit.summarize_segmented_results(
        [
            {"segment_key": "202305", "eligible": True, "segment_pass": False},
            {"segment_key": "202306", "eligible": True, "segment_pass": False},
        ],
        min_dates_scored=10,
    )
    assert summary["mission_pass"] is False


def test_segment_pass_uses_shape_checks_not_block_level_coverage_flag() -> None:
    segment_result = {
        "checks": {
            "coverage_pass": False,
            "counts_non_increasing": True,
            "signed_return_non_decreasing": True,
            "hazard_non_decreasing": True,
            "strongest_threshold_beats_universe_on_both": True,
            "strongest_threshold_positive": True,
        }
    }
    assert segmented_audit._segment_passes_shape_checks(segment_result) is True
