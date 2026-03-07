import math
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import load_l2_pipeline_config
from omega_core.omega_math_rolling import (
    calc_isoperimetric_topology_rolling,
    calc_srl_compression_gain_rolling,
    calc_topology_area_rolling,
)
from omega_core.trainer import OmegaTrainerV3
from tools.run_local_backtest import (
    _audit_backtest_frame_contract,
    _build_daily_close_map,
    _load_backtest_file,
)
from tools.run_vertex_xgb_train import _audit_training_base_matrix_contract
from tools.stage2_physics_compute import _apply_worker_thread_budget, _audit_stage2_feature_contract


def _make_dist_to_boundary(n: int, boundaries: tuple[int, ...]) -> np.ndarray:
    dist = np.zeros(n, dtype=np.int32)
    boundary_set = set(int(x) for x in boundaries)
    curr = 999999
    for i in range(n):
        if i in boundary_set:
            curr = 0
        else:
            curr += 1
        dist[i] = curr
    return dist


def _ref_srl(price_change, srl_residuals, window, dist_to_boundary):
    out = np.zeros(len(price_change), dtype=np.float64)
    if len(price_change) < window:
        return out
    for i in range(window - 1, len(price_change)):
        if dist_to_boundary[i] < window - 1:
            continue
        dp = price_change[i - window + 1 : i + 1]
        r = srl_residuals[i - window + 1 : i + 1]
        mean_dp = np.sum(dp) / window
        var_dp = (np.sum(dp * dp) / window) - (mean_dp * mean_dp)
        mean_r = np.sum(r) / window
        var_r = (np.sum(r * r) / window) - (mean_r * mean_r)
        if var_dp < 1e-12:
            continue
        ratio = var_dp / max(var_r, 1e-12)
        if ratio > 1.0:
            out[i] = (window / 2.0) * math.log(ratio)
    return out


def _ref_topology_area(x_arr, y_arr, window, x_scale_floor, y_scale_floor, green_coeff, dist_to_boundary):
    out = np.zeros(len(x_arr), dtype=np.float64)
    if len(x_arr) < window:
        return out
    for i in range(window - 1, len(x_arr)):
        if dist_to_boundary[i] < window - 1:
            continue
        X = x_arr[i - window + 1 : i + 1]
        Y = y_arr[i - window + 1 : i + 1]
        mx = np.sum(X) / window
        my = np.sum(Y) / window
        vx = np.sum((X - mx) ** 2) / window
        vy = np.sum((Y - my) ** 2) / window
        sx = max(math.sqrt(vx), x_scale_floor)
        sy = max(math.sqrt(vy), y_scale_floor)
        Xn = (X - mx) / sx
        Yn = (Y - my) / sy
        area_sum = 0.0
        for j in range(window - 1):
            area_sum += Xn[j] * Yn[j + 1] - Xn[j + 1] * Yn[j]
        out[i] = area_sum * green_coeff
    return out


def _ref_isoperimetric(prices, ofis, window, price_scale_floor, ofi_scale_floor, green_coeff, dist_to_boundary):
    out_area = np.zeros(len(prices), dtype=np.float64)
    out_energy = np.zeros(len(prices), dtype=np.float64)
    out_q = np.zeros(len(prices), dtype=np.float64)
    if len(prices) < window:
        return out_area, out_energy, out_q
    for i in range(window - 1, len(prices)):
        if dist_to_boundary[i] < window - 1:
            continue
        X = prices[i - window + 1 : i + 1]
        Y = np.empty(window, dtype=np.float64)
        Y[0] = ofis[i - window + 1]
        for j in range(1, window):
            Y[j] = Y[j - 1] + ofis[i - window + 1 + j]
        mx = np.sum(X) / window
        my = np.sum(Y) / window
        sx = max(math.sqrt(np.sum((X - mx) ** 2) / window), price_scale_floor)
        sy = max(math.sqrt(np.sum((Y - my) ** 2) / window), ofi_scale_floor)
        Xn = (X - mx) / sx
        Yn = (Y - my) / sy
        area_sum = 0.0
        energy_sum = 0.0
        for j in range(window - 1):
            area_sum += Xn[j] * Yn[j + 1] - Xn[j + 1] * Yn[j]
            dx = Xn[j + 1] - Xn[j]
            dy = Yn[j + 1] - Yn[j]
            energy_sum += math.sqrt(dx * dx + dy * dy)
        area_sum += Xn[window - 1] * Yn[0] - Xn[0] * Yn[window - 1]
        dx_close = Xn[0] - Xn[window - 1]
        dy_close = Yn[0] - Yn[window - 1]
        energy_sum += math.sqrt(dx_close * dx_close + dy_close * dy_close)
        area_val = area_sum * green_coeff
        out_area[i] = area_val
        out_energy[i] = energy_sum
        if energy_sum > 1e-12:
            out_q[i] = min(1.0, max(0.0, (4.0 * math.pi * abs(area_val)) / (energy_sum * energy_sum)))
    return out_area, out_energy, out_q


def _make_precomputed_frames():
    rows = []
    dates = ["20250101", "20250102", "20250103", "20250106"]
    for d_idx, date in enumerate(dates):
        for bucket in range(6):
            close = 10.0 + d_idx + 0.05 * bucket
            resid = 0.2 if bucket % 2 == 0 else -0.18
            rows.append(
                {
                    "symbol": "000001.SZ",
                    "date": date,
                    "bucket_id": bucket,
                    "time_end": 34_200_000 + bucket * 3_000,
                    "open": close - 0.02,
                    "close": close,
                    "price_change": 0.02,
                    "sigma_eff": 0.15,
                    "depth_eff": 1000.0,
                    "epiplexity": 1.0 + 0.1 * bucket,
                    "topo_area": 0.4 + 0.01 * bucket,
                    "topo_energy": 3.2,
                    "srl_resid": resid,
                    "adaptive_y": 1.0,
                    "is_signal": True,
                    "direction": 1.0 if resid > 0 else -1.0,
                    "net_ofi": 120.0 + bucket,
                    "is_energy_active": True,
                    "spoof_ratio": 0.1,
                    "trade_vol": 1000.0 + bucket,
                    "cancel_vol": 10.0,
                }
            )
    df = pl.DataFrame(rows)
    daily = (
        df.sort(["symbol", "date", "time_end"])
        .group_by(["symbol", "date"], maintain_order=True)
        .agg(pl.col("close").last().alias("_day_close"))
        .sort(["symbol", "date"])
        .with_columns(pl.col("_day_close").shift(-1).over("symbol").alias("t1_close"))
        .select(["symbol", "date", "t1_close"])
    )
    return df, daily


def _make_stage2_feature_frames(rows_per_symbol: int = 64, *, interleaved: bool) -> pl.DataFrame:
    ordered_rows = []
    for symbol_idx, symbol in enumerate(("000001.SZ", "000002.SZ")):
        for i in range(rows_per_symbol):
            ordered_rows.append(
                {
                    "symbol": symbol,
                    "date": "20250101",
                    "time_end": 34_200_000 + i * 3_000,
                    "bucket_id": i,
                    "open": 10.0 + 0.02 * i + 0.5 * symbol_idx,
                    "close": 10.1 + 0.02 * i + 0.5 * symbol_idx,
                    "sigma": 0.2,
                    "depth": 1000.0,
                    "net_ofi": float(((-1) ** (i + symbol_idx)) * (80 + i)),
                    "trade_vol": 1000.0 + i,
                    "cancel_vol": 10.0,
                }
            )
    if not interleaved:
        return pl.DataFrame(ordered_rows)

    sym0 = [row for row in ordered_rows if row["symbol"] == "000001.SZ"]
    sym1 = [row for row in ordered_rows if row["symbol"] == "000002.SZ"]
    rows = []
    for left, right in zip(sym0, sym1):
        rows.append(left)
        rows.append(right)
    return pl.DataFrame(rows)


def test_srl_fast_path_matches_reference_with_boundaries():
    rng = np.random.default_rng(7)
    n = 256
    window = 60
    dist = _make_dist_to_boundary(n, boundaries=(73, 180))
    price_change = rng.normal(0.0, 1.0, n).astype(np.float64)
    srl_residuals = rng.normal(0.0, 0.75, n).astype(np.float64)

    ref = _ref_srl(price_change, srl_residuals, window, dist)
    got = calc_srl_compression_gain_rolling(price_change, srl_residuals, window, dist)

    np.testing.assert_allclose(got, ref, atol=1e-10, rtol=1e-10)


def test_topology_area_fast_path_matches_reference_with_boundaries():
    rng = np.random.default_rng(11)
    n = 192
    window = 48
    dist = _make_dist_to_boundary(n, boundaries=(0, 91, 143))
    x_arr = rng.normal(size=n).astype(np.float64)
    y_arr = rng.normal(size=n).astype(np.float64)

    ref = _ref_topology_area(x_arr, y_arr, window, 0.01, 0.01, 0.5, dist)
    got = calc_topology_area_rolling(x_arr, y_arr, window, 0.01, 0.01, 0.5, dist)

    np.testing.assert_allclose(got, ref, atol=1e-10, rtol=1e-10)


def test_isoperimetric_fast_path_matches_reference_with_boundaries():
    rng = np.random.default_rng(19)
    n = 220
    window = 50
    dist = _make_dist_to_boundary(n, boundaries=(0, 87, 171))
    prices = (10.0 + rng.normal(scale=0.2, size=n).cumsum()).astype(np.float64)
    ofis = rng.normal(scale=5.0, size=n).astype(np.float64)

    ref_area, ref_energy, ref_q = _ref_isoperimetric(prices, ofis, window, 0.01, 1.0, 0.5, dist)
    got_area, got_energy, got_q = calc_isoperimetric_topology_rolling(prices, ofis, window, 0.01, 1.0, 0.5, dist)

    np.testing.assert_allclose(got_area, ref_area, atol=1e-10, rtol=1e-10)
    np.testing.assert_allclose(got_energy, ref_energy, atol=1e-10, rtol=1e-10)
    np.testing.assert_allclose(got_q, ref_q, atol=1e-10, rtol=1e-10)


def test_trainer_accepts_prejoined_t1_close_without_rebuilding_targets():
    os.environ["OMEGA_REUSE_PRECOMPUTED_PHYSICS"] = "1"
    cfg = load_l2_pipeline_config()
    trainer = OmegaTrainerV3(cfg)

    base_df, daily_map = _make_precomputed_frames()

    direct = trainer._prepare_frames(base_df, cfg).sort(["symbol", "date", "bucket_id"])
    prejoined = trainer._prepare_frames(
        base_df.join(daily_map, on=["symbol", "date"], how="left"),
        cfg,
    ).sort(["symbol", "date", "bucket_id"])

    compare_cols = ["symbol", "date", "bucket_id", "close_fwd", "fwd_change", "direction_label", "t1_fwd_return"]
    for col in compare_cols:
        left = direct.get_column(col).to_numpy() if col not in {"symbol", "date"} else direct.get_column(col).to_list()
        right = prejoined.get_column(col).to_numpy() if col not in {"symbol", "date"} else prejoined.get_column(col).to_list()
        if col in {"symbol", "date"}:
            assert left == right
        else:
            np.testing.assert_allclose(left, right, atol=1e-12, rtol=1e-12)


def test_backtest_daily_close_map_preserves_cross_file_t1_labels(tmp_path):
    base_df, daily_map = _make_precomputed_frames()
    parquet_files = []
    for date in sorted(base_df.get_column("date").unique().to_list()):
        path = tmp_path / f"{date}.parquet"
        base_df.filter(pl.col("date") == date).write_parquet(path)
        parquet_files.append(str(path))

    built_map = _build_daily_close_map(parquet_files, ())
    built_map = built_map.sort(["symbol", "date"])
    expected_map = daily_map.sort(["symbol", "date"])

    assert built_map is not None
    np.testing.assert_allclose(
        built_map.get_column("t1_close").fill_null(-1.0).to_numpy(),
        expected_map.get_column("t1_close").fill_null(-1.0).to_numpy(),
        atol=1e-12,
        rtol=1e-12,
    )

    loaded = _load_backtest_file(parquet_files[0], (), built_map.lazy()).sort(["symbol", "date", "bucket_id"])
    expected_join = (
        base_df.filter(pl.col("date") == "20250101")
        .join(expected_map, on=["symbol", "date"], how="left")
        .sort(["symbol", "date", "bucket_id"])
    )
    np.testing.assert_allclose(
        loaded.get_column("t1_close").fill_null(-1.0).to_numpy(),
        expected_join.get_column("t1_close").fill_null(-1.0).to_numpy(),
        atol=1e-12,
        rtol=1e-12,
    )


def test_backtest_file_stream_refuses_mixed_t1_join_semantics(tmp_path):
    broken = pl.DataFrame(
        {
            "close": [10.0, 10.1],
            "bucket_id": [0, 1],
            "time_end": [1, 2],
        }
    )
    broken_path = tmp_path / "broken.parquet"
    broken.write_parquet(broken_path)

    daily_map = pl.DataFrame(
        {
            "symbol": ["000001.SZ"],
            "date": ["20250101"],
            "t1_close": [10.5],
        }
    )

    with pytest.raises(RuntimeError, match="missing_symbol_date_for_t1_join"):
        _load_backtest_file(
            str(broken_path),
            (),
            daily_map.lazy(),
            require_global_t1_join=True,
        )


def test_stage2_thread_budget_harmonizes_native_caps(monkeypatch):
    monkeypatch.setenv("POLARS_MAX_THREADS", "8")
    monkeypatch.setenv("NUMBA_NUM_THREADS", "16")
    for name in (
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OMP_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        monkeypatch.setenv(name, "7")

    _apply_worker_thread_budget(workers=4)

    assert int(os.environ["POLARS_MAX_THREADS"]) <= 8
    assert int(os.environ["NUMBA_NUM_THREADS"]) <= 16
    for name in (
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OMP_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        assert os.environ[name] == "1"


def test_stage2_feature_contract_detects_repairable_interleaving():
    feat_df = _make_stage2_feature_frames(interleaved=True)
    report = _audit_stage2_feature_contract(feat_df, window_len=60)

    assert report["eligible_groups"] == 2
    assert report["disordered_groups"] == 2
    assert report["repairable_by_kernel_reorder"] is True


def test_stage2_feature_contract_rejects_unwarmed_inputs():
    feat_df = _make_stage2_feature_frames(rows_per_symbol=12, interleaved=False)
    with pytest.raises(RuntimeError, match="no_groups_reach_window"):
        _audit_stage2_feature_contract(feat_df, window_len=60)


def test_stage2_feature_contract_allows_unwarmed_batches_in_diagnostic_mode():
    feat_df = _make_stage2_feature_frames(rows_per_symbol=12, interleaved=False)
    report = _audit_stage2_feature_contract(
        feat_df,
        window_len=60,
        require_window_reachable=False,
    )
    assert report["eligible_groups"] == 0
    assert report["max_group_rows"] == 12


def test_training_input_contract_rejects_all_zero_signal_chain():
    base_df, _ = _make_precomputed_frames()
    zero_df = base_df.with_columns([
        pl.lit(0.0).alias("epiplexity"),
        pl.lit(0.0).alias("topo_energy"),
        pl.lit(0.0).alias("singularity_vector"),
    ])
    with pytest.raises(RuntimeError, match="training_input_contract"):
        _audit_training_base_matrix_contract(zero_df, singularity_threshold=0.1)


def test_backtest_input_contract_rejects_all_zero_signal_chain(tmp_path):
    base_df, _ = _make_precomputed_frames()
    zero_df = base_df.with_columns([
        pl.lit(0.0).alias("epiplexity"),
        pl.lit(0.0).alias("topo_energy"),
        pl.lit(0.0).alias("singularity_vector"),
    ])
    one = tmp_path / "zero.parquet"
    zero_df.write_parquet(one)

    with pytest.raises(RuntimeError, match="backtest_input_contract"):
        _audit_backtest_frame_contract([str(one)], ())
