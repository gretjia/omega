import sys
from pathlib import Path

import numpy as np
import pytest

pl = pytest.importorskip("polars")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import forge_campaign_state as campaign_state


def test_compute_triple_barrier_prefers_stop_on_same_day_hit() -> None:
    sym_ids = np.asarray([1, 1, 1, 1], dtype=np.int32)
    opens = np.asarray([100.0, 100.0, 100.0, 100.0], dtype=np.float64)
    highs = np.asarray([100.0, 103.0, 101.0, 101.0], dtype=np.float64)
    lows = np.asarray([100.0, 98.0, 99.0, 99.0], dtype=np.float64)
    vol20d = np.asarray([0.01, 0.01, 0.01, 0.01], dtype=np.float64)

    labels = campaign_state.compute_triple_barrier_labels(
        sym_ids=sym_ids,
        opens=opens,
        highs=highs,
        lows=lows,
        vol20d=vol20d,
        horizon=2,
        up_mult=2.0,
        down_mult=1.0,
    )

    assert int(labels[0]) == -1


def test_build_campaign_state_frame_zero_fills_no_signal_days() -> None:
    daily_spine = pl.DataFrame(
        [
            {"symbol": "AAA", "pure_date": "20240102", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "n_ticks_day": 10},
            {"symbol": "AAA", "pure_date": "20240103", "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0, "n_ticks_day": 10},
            {"symbol": "AAA", "pure_date": "20240104", "open": 102.0, "high": 105.0, "low": 101.0, "close": 104.0, "n_ticks_day": 10},
            {"symbol": "AAA", "pure_date": "20240105", "open": 104.0, "high": 106.0, "low": 103.0, "close": 105.0, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240102", "open": 50.0, "high": 51.0, "low": 49.0, "close": 50.5, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240103", "open": 50.5, "high": 52.0, "low": 50.0, "close": 51.5, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240104", "open": 51.5, "high": 53.0, "low": 51.0, "close": 52.0, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240105", "open": 52.0, "high": 53.5, "low": 51.5, "close": 52.5, "n_ticks_day": 10},
        ]
    )
    daily_events = pl.DataFrame(
        [
            {"symbol": "AAA", "pure_date": "20240102", "F_force": 2.0, "A_action": 2.0, "N_events": 1, "day_epi_integral": 1.0, "day_topo_integral": 1.0},
            {"symbol": "AAA", "pure_date": "20240104", "F_force": 1.0, "A_action": 1.0, "N_events": 1, "day_epi_integral": 0.5, "day_topo_integral": 0.5},
            {"symbol": "BBB", "pure_date": "20240103", "F_force": -1.0, "A_action": 1.0, "N_events": 1, "day_epi_integral": 0.3, "day_topo_integral": 0.2},
        ]
    )

    out = campaign_state.build_campaign_state_frame(
        daily_spine=daily_spine,
        daily_events=daily_events,
        horizons=(2,),
        eps=1e-12,
    )

    row = out.filter((pl.col("symbol") == "AAA") & (pl.col("pure_date") == "20240103")).row(0, named=True)
    assert row["F_force"] == 0.0
    assert row["A_action"] == 0.0
    assert row["N_events"] == 0
    assert "S_2d" in out.columns
    assert "Omega_2d" in out.columns
    assert "Psi_2d" in out.columns
    assert "excess_ret_t1_to_2d" in out.columns
    assert "barrier_2d" in out.columns


def test_assert_unique_symbol_date_rejects_duplicates() -> None:
    df = pl.DataFrame(
        [
            {"symbol": "AAA", "pure_date": "20240102", "open": 1.0},
            {"symbol": "AAA", "pure_date": "20240102", "open": 2.0},
        ]
    )
    with pytest.raises(ValueError):
        campaign_state._assert_unique_symbol_date(df, frame_name="daily_spine")
