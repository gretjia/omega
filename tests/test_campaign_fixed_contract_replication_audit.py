import sys
from pathlib import Path

import pytest

pl = pytest.importorskip("polars")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import run_campaign_fixed_contract_replication_audit as replication_audit


def _derived_replication_frame() -> pl.DataFrame:
    rows = []
    dates = [f"202401{day:02d}" for day in range(2, 47)]
    symbols = ["AAA", "BBB", "CCC", "DDD"]
    for idx, pure_date in enumerate(dates):
        aaa = -(10 + idx)
        bbb = -(7 + idx)
        ccc = -(4 + idx)
        ddd = -(1 + idx)
        values = {
            "AAA": aaa,
            "BBB": bbb,
            "CCC": ccc,
            "DDD": ddd,
        }
        for symbol, value in values.items():
            rows.append(
                {
                    "symbol": symbol,
                    "pure_date": pure_date,
                    "dPsiAmpE_10d": float(value),
                    "FreshAmpStar_10d": float(value) / 2.0,
                    "PsiAmpE_10d": float(value) * 1.5,
                    "PsiAmpStar_10d": float(value) * 1.2,
                    "OmegaAmpE_10d": abs(float(value)) / 10.0,
                    "OmegaAmpStar_10d": abs(float(value)) / 12.0,
                    "barrier_10d": -1 if symbol == "AAA" else 0,
                    "excess_ret_t1_to_10d": -0.08 if symbol == "AAA" else (-0.04 if symbol == "BBB" else -0.01),
                }
            )
    return pl.DataFrame(rows)


def test_negative_side_universe_is_sign_aware() -> None:
    universe = replication_audit._negative_side_universe_summary(_derived_replication_frame())

    assert universe["n_rows_scored"] > 0
    assert universe["n_dates_scored"] == 45
    assert universe["date_neutral_signed_return"] > 0.0
    assert universe["date_neutral_hazard_win_rate"] > 0.0


def test_counts_shrink_as_threshold_tightens() -> None:
    result = replication_audit.run_fixed_contract_replication_audit_from_derived(_derived_replication_frame())

    counts = [row["n_rows_scored"] for row in result["threshold_results"]]
    assert counts[0] >= counts[1] >= counts[2]
    assert result["checks"]["counts_non_increasing"] is True


def test_pass_requires_strongest_threshold_to_beat_negative_universe() -> None:
    result = replication_audit.run_fixed_contract_replication_audit_from_derived(_derived_replication_frame())

    assert result["checks"]["coverage_pass"] is True
    assert result["checks"]["signed_return_non_decreasing"] is True
    assert result["checks"]["hazard_non_decreasing"] is True
    assert result["checks"]["strongest_threshold_beats_universe_on_both"] is True
    assert result["mission_pass"] is True


def test_fail_when_coverage_is_too_low() -> None:
    short_df = _derived_replication_frame().filter(pl.col("pure_date") < "20240120")
    result = replication_audit.run_fixed_contract_replication_audit_from_derived(short_df)

    assert result["checks"]["coverage_pass"] is False
    assert result["mission_pass"] is False
