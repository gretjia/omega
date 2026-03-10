import sys
from pathlib import Path

import pytest

pl = pytest.importorskip("polars")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import run_campaign_event_study as event_study
from tools import run_campaign_transition_event_study as transition_study


def _base_transition_frame() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "symbol": "AAA",
                "pure_date": "20240102",
                "PsiAmpE_10d": 1.0,
                "PsiAmpE_20d": 0.5,
                "PsiAmpStar_10d": 0.5,
                "PsiAmpStar_20d": 0.25,
                "OmegaAmpE_10d": 0.2,
                "OmegaAmpE_20d": 0.1,
                "OmegaAmpStar_10d": 0.1,
                "OmegaAmpStar_20d": 0.05,
                "excess_ret_t1_to_10d": 0.01,
                "excess_ret_t1_to_20d": 0.02,
                "barrier_10d": 0,
                "barrier_20d": 0,
            },
            {
                "symbol": "AAA",
                "pure_date": "20240103",
                "PsiAmpE_10d": 3.0,
                "PsiAmpE_20d": 2.0,
                "PsiAmpStar_10d": 2.0,
                "PsiAmpStar_20d": 1.5,
                "OmegaAmpE_10d": 0.6,
                "OmegaAmpE_20d": 0.4,
                "OmegaAmpStar_10d": 0.5,
                "OmegaAmpStar_20d": 0.3,
                "excess_ret_t1_to_10d": 0.03,
                "excess_ret_t1_to_20d": 0.04,
                "barrier_10d": 1,
                "barrier_20d": 1,
            },
            {
                "symbol": "BBB",
                "pure_date": "20240102",
                "PsiAmpE_10d": 10.0,
                "PsiAmpE_20d": 9.0,
                "PsiAmpStar_10d": 8.0,
                "PsiAmpStar_20d": 7.0,
                "OmegaAmpE_10d": 0.8,
                "OmegaAmpE_20d": 0.7,
                "OmegaAmpStar_10d": 0.6,
                "OmegaAmpStar_20d": 0.5,
                "excess_ret_t1_to_10d": -0.01,
                "excess_ret_t1_to_20d": -0.02,
                "barrier_10d": -1,
                "barrier_20d": -1,
            },
        ]
    )


def test_transition_derivatives_respect_symbol_boundaries() -> None:
    derived = transition_study.derive_transition_columns(_base_transition_frame())

    aaa_second = derived.filter((pl.col("symbol") == "AAA") & (pl.col("pure_date") == "20240103")).row(0, named=True)
    bbb_first = derived.filter((pl.col("symbol") == "BBB") & (pl.col("pure_date") == "20240102")).row(0, named=True)

    assert aaa_second["dPsiAmpE_10d"] == pytest.approx(2.0)
    assert bbb_first["dPsiAmpE_10d"] is None
    assert bbb_first["FreshAmpStar_10d"] is None


def test_fresh_entry_score_is_zero_when_state_does_not_strengthen() -> None:
    df = pl.DataFrame(
        [
            {
                "symbol": "AAA",
                "pure_date": "20240102",
                "PsiAmpE_10d": 2.0,
                "PsiAmpE_20d": 2.0,
                "PsiAmpStar_10d": 2.0,
                "PsiAmpStar_20d": 2.0,
                "OmegaAmpE_10d": 0.4,
                "OmegaAmpE_20d": 0.4,
                "OmegaAmpStar_10d": 0.4,
                "OmegaAmpStar_20d": 0.4,
                "excess_ret_t1_to_10d": 0.01,
                "excess_ret_t1_to_20d": 0.01,
                "barrier_10d": 0,
                "barrier_20d": 0,
            },
            {
                "symbol": "AAA",
                "pure_date": "20240103",
                "PsiAmpE_10d": 1.5,
                "PsiAmpE_20d": 1.5,
                "PsiAmpStar_10d": 2.0,
                "PsiAmpStar_20d": 2.0,
                "OmegaAmpE_10d": 0.6,
                "OmegaAmpE_20d": 0.6,
                "OmegaAmpStar_10d": 0.4,
                "OmegaAmpStar_20d": 0.4,
                "excess_ret_t1_to_10d": 0.02,
                "excess_ret_t1_to_20d": 0.02,
                "barrier_10d": 1,
                "barrier_20d": 1,
            },
        ]
    )

    derived = transition_study.derive_transition_columns(df)
    row = derived.filter(pl.col("pure_date") == "20240103").row(0, named=True)

    assert row["FreshAmpE_10d"] == pytest.approx(0.0)
    assert row["FreshAmpStar_10d"] == pytest.approx(0.0)


def test_fresh_entry_score_positive_when_abs_psi_and_omega_both_rise() -> None:
    derived = transition_study.derive_transition_columns(_base_transition_frame())
    row = derived.filter((pl.col("symbol") == "AAA") & (pl.col("pure_date") == "20240103")).row(0, named=True)

    assert row["FreshAmpE_10d"] > 0.0
    assert row["FreshAmpStar_10d"] > 0.0


def test_existing_event_study_gate_is_unchanged() -> None:
    assert transition_study.compute_event_study_for_signal is event_study.compute_event_study_for_signal
