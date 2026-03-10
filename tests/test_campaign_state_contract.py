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


def test_same_sign_overlap_collapses_to_one_peak() -> None:
    candidates = pl.DataFrame(
        [
            {"symbol": "AAA", "pure_date": "20240102", "__order_txt": "0001", "__singularity": 2.0, "__sv_sign": 1, "E": 1.0, "T": 0.5, "Phi": 1.0, "__ord": 0},
            {"symbol": "AAA", "pure_date": "20240102", "__order_txt": "0002", "__singularity": 5.0, "__sv_sign": 1, "E": 3.0, "T": 1.5, "Phi": 1.0, "__ord": 10},
        ]
    )

    out = campaign_state._pulse_compress_and_aggregate_daily(candidates, pulse_min_gap=30)
    row = out.row(0, named=True)

    assert row["pulse_count"] == 1
    assert row["F_epi"] == pytest.approx(3.0)
    assert row["A_epi"] == pytest.approx(3.0)
    assert row["F_topo"] == pytest.approx(1.5)
    assert row["A_topo"] == pytest.approx(1.5)
    assert row["pulse_concentration"] == pytest.approx(1.0)


def test_opposite_sign_close_peaks_both_survive() -> None:
    candidates = pl.DataFrame(
        [
            {"symbol": "AAA", "pure_date": "20240102", "__order_txt": "0001", "__singularity": 4.0, "__sv_sign": 1, "E": 2.0, "T": 1.0, "Phi": 1.0, "__ord": 0},
            {"symbol": "AAA", "pure_date": "20240102", "__order_txt": "0002", "__singularity": -3.0, "__sv_sign": -1, "E": 1.0, "T": 2.0, "Phi": -1.0, "__ord": 5},
        ]
    )

    out = campaign_state._pulse_compress_and_aggregate_daily(candidates, pulse_min_gap=30)
    row = out.row(0, named=True)

    assert row["pulse_count"] == 2
    assert row["F_epi"] == pytest.approx(1.0)
    assert row["A_epi"] == pytest.approx(3.0)
    assert row["F_topo"] == pytest.approx(-1.0)
    assert row["A_topo"] == pytest.approx(3.0)
    assert row["F_phase"] == pytest.approx(0.0)
    assert row["A_phase"] == pytest.approx(2.0)


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
    assert "PsiE_2d" in out.columns
    assert "PsiT_2d" in out.columns
    assert "PsiStar_2d" in out.columns


def test_day_epi_and_day_topo_flow_into_campaign_state() -> None:
    daily_spine = pl.DataFrame(
        [
            {"symbol": "AAA", "pure_date": "20240102", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "n_ticks_day": 10},
            {"symbol": "AAA", "pure_date": "20240103", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "n_ticks_day": 10},
            {"symbol": "AAA", "pure_date": "20240104", "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240102", "open": 50.0, "high": 51.0, "low": 49.0, "close": 50.0, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240103", "open": 50.0, "high": 51.0, "low": 49.0, "close": 50.1, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240104", "open": 50.1, "high": 51.0, "low": 49.5, "close": 50.2, "n_ticks_day": 10},
        ]
    )
    daily_events = pl.DataFrame(
        [
            {
                "symbol": "AAA",
                "pure_date": "20240102",
                "F_force": 0.0,
                "A_action": 0.0,
                "N_events": 0,
                "day_epi_integral": 0.0,
                "day_topo_integral": 0.0,
                "F_epi": 2.0,
                "A_epi": 2.0,
                "F_topo": 1.0,
                "A_topo": 1.0,
                "F_phase": 1.0,
                "A_phase": 1.0,
                "pulse_count": 1,
                "pulse_concentration": 1.0,
            }
        ]
    )

    out = campaign_state.build_campaign_state_frame(daily_spine=daily_spine, daily_events=daily_events, horizons=(1,), eps=1e-12)
    row = out.filter((pl.col("symbol") == "AAA") & (pl.col("pure_date") == "20240102")).row(0, named=True)

    assert row["Psi_1d"] == pytest.approx(0.0)
    assert row["PsiE_1d"] > 0.0
    assert row["PsiT_1d"] > 0.0
    assert row["PsiStar_1d"] > 0.0


def test_missing_intraday_order_key_fails_fast(tmp_path: Path) -> None:
    l2_path = tmp_path / "20240102_deadbee.parquet"
    pl.DataFrame(
        [
            {
                "symbol": "AAA",
                "date": "20240102",
                "singularity_vector": 1.0,
                "epiplexity": 0.5,
                "bits_topology": 0.25,
                "srl_phase": 1.0,
                "is_signal": True,
                "is_physics_valid": True,
            }
        ]
    ).write_parquet(l2_path)

    with pytest.raises(ValueError):
        campaign_state._collect_intraday_candidates_from_l2(
            l2_files=[str(l2_path)],
            pulse_floor=1e-12,
            require_is_signal=True,
            require_is_physics_valid=True,
            eps=1e-12,
        )


def test_zero_fraction_remains_zero_after_v654_forge() -> None:
    daily_spine = pl.DataFrame(
        [
            {"symbol": "AAA", "pure_date": "20240102", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "n_ticks_day": 10},
            {"symbol": "AAA", "pure_date": "20240103", "open": 100.0, "high": 103.0, "low": 99.0, "close": 102.0, "n_ticks_day": 10},
            {"symbol": "AAA", "pure_date": "20240104", "open": 102.0, "high": 106.0, "low": 101.0, "close": 105.0, "n_ticks_day": 10},
            {"symbol": "AAA", "pure_date": "20240105", "open": 105.0, "high": 108.0, "low": 104.0, "close": 107.0, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240102", "open": 50.0, "high": 50.5, "low": 49.5, "close": 50.0, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240103", "open": 50.0, "high": 50.4, "low": 49.6, "close": 50.1, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240104", "open": 50.1, "high": 50.4, "low": 49.8, "close": 50.0, "n_ticks_day": 10},
            {"symbol": "BBB", "pure_date": "20240105", "open": 50.0, "high": 50.2, "low": 49.7, "close": 49.9, "n_ticks_day": 10},
        ]
    )
    daily_events = pl.DataFrame(
        [
            {"symbol": "AAA", "pure_date": "20240102", "F_force": 2.0, "A_action": 2.0, "N_events": 1, "day_epi_integral": 1.0, "day_topo_integral": 0.5, "F_epi": 2.0, "A_epi": 2.0, "F_topo": 0.5, "A_topo": 0.5, "F_phase": 1.0, "A_phase": 1.0, "pulse_count": 1, "pulse_concentration": 1.0},
            {"symbol": "BBB", "pure_date": "20240102", "F_force": -1.0, "A_action": 1.0, "N_events": 1, "day_epi_integral": 0.2, "day_topo_integral": 0.1, "F_epi": -1.0, "A_epi": 1.0, "F_topo": -0.1, "A_topo": 0.1, "F_phase": -1.0, "A_phase": 1.0, "pulse_count": 1, "pulse_concentration": 1.0},
        ]
    )

    out = campaign_state.build_campaign_state_frame(daily_spine=daily_spine, daily_events=daily_events, horizons=(2,), eps=1e-12)
    zero_frac = out.select((pl.col("excess_ret_t1_to_2d").fill_null(0.0).fill_nan(0.0) == 0.0).mean()).item()

    assert zero_frac == 0.0


def test_assert_unique_symbol_date_rejects_duplicates() -> None:
    df = pl.DataFrame(
        [
            {"symbol": "AAA", "pure_date": "20240102", "open": 1.0},
            {"symbol": "AAA", "pure_date": "20240102", "open": 2.0},
        ]
    )
    with pytest.raises(ValueError):
        campaign_state._assert_unique_symbol_date(df, frame_name="daily_spine")
