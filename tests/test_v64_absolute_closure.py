import math
import os
import sys

import numpy as np
import polars as pl
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import load_l2_pipeline_config
from omega_core.kernel import apply_recursive_physics
from omega_core.omega_math_rolling import (
    calc_isoperimetric_topology_rolling,
    calc_srl_compression_gain_rolling,
)


def _make_kernel_frames(n: int = 128) -> pl.DataFrame:
    rows = []
    for i in range(n):
        open_px = 10.0 + 0.03 * i
        price_change = 0.25 if i % 2 == 0 else -0.18
        if i == 12:
            price_change = 0.41
        rows.append(
            {
                "symbol": "000001.SZ",
                "date": "20250101",
                "open": open_px,
                "close": open_px + price_change,
                "sigma": 0.25,
                "depth": 1000.0 + 5.0 * i,
                "net_ofi": 0.0 if i == 12 else float(((-1) ** i) * (50 + i)),
                "trade_vol": 1000.0 + 10.0 * i,
                "cancel_vol": 20.0 + i,
                "has_singularity": i == 12,
            }
        )
    return pl.DataFrame(rows)


def _make_interleaved_kernel_frames(rows_per_symbol: int = 72) -> pl.DataFrame:
    rows = []
    base_time = 34_200_000
    for i in range(rows_per_symbol):
        for sym_idx, symbol in enumerate(("000001.SZ", "000002.SZ")):
            open_px = 10.0 + 0.01 * i + 0.5 * sym_idx
            price_change = (0.18 + 0.002 * i) if sym_idx == 0 else (-0.12 - 0.001 * i)
            rows.append(
                {
                    "symbol": symbol,
                    "date": "20250101",
                    "bucket_id": i,
                    "time_end": base_time + i * 3_000,
                    "open": open_px,
                    "close": open_px + price_change,
                    "sigma": 0.2 + 0.001 * i,
                    "depth": 1000.0 + 10.0 * i,
                    "net_ofi": float(((-1) ** (i + sym_idx)) * (120 + i)),
                    "trade_vol": 1000.0 + 5.0 * i,
                    "cancel_vol": 20.0 + i,
                    "has_singularity": False,
                }
            )
    return pl.DataFrame(rows)


def test_flaw1_zero_residual_explosion():
    """Audit lock 1: MDL gain must close correctly at the variance boundary."""
    w = 60
    dist = np.full(100, 999, dtype=np.int32)

    flat_dp = np.zeros(100, dtype=np.float64)
    flat_resid = np.zeros(100, dtype=np.float64)
    gain_flat = calc_srl_compression_gain_rolling(flat_dp, flat_resid, w, dist)
    assert np.all(gain_flat == 0.0), "Hard Bug 1 Failed: zero-variance must yield 0 signal."

    rng = np.random.default_rng(42)
    huge_dp = rng.normal(10.0, 2.0, 100).astype(np.float64)
    tiny_resid = rng.normal(0.0, 1e-10, 100).astype(np.float64)
    gain_singularity = calc_srl_compression_gain_rolling(huge_dp, tiny_resid, w, dist)

    assert np.all(gain_singularity[w:] > 50.0), (
        "Hard Bug 1 Failed: perfect fit failed to explode naturally."
    )
    assert not np.any(gain_singularity == 999.0), (
        "Hard Bug 1 Failed: fake 999.0 hack detected."
    )


def test_flaw2_homologous_geometry():
    """Audit lock 2: topology area and energy must remain homologous."""
    prices = np.sin(np.linspace(0, 2 * np.pi, 100)).astype(np.float64)
    ofis = np.cos(np.linspace(0, 2 * np.pi, 100)).astype(np.float64)
    dist = np.full(100, 999, dtype=np.int32)

    area, energy, q_topo = calc_isoperimetric_topology_rolling(
        prices, ofis, 10, 1e-5, 1e-5, 0.5, dist
    )

    computed_q = (4.0 * math.pi * np.abs(area[10:])) / (energy[10:] ** 2 + 1e-12)
    np.testing.assert_almost_equal(
        q_topo[10:],
        computed_q,
        decimal=5,
        err_msg="Hard Bug 2 Failed: topology area and energy are not homologous!",
    )


def test_flaw3_gate_separation():
    """Audit lock 3: config semantics must be decoupled and modernized."""
    from config import load_l2_pipeline_config

    cfg = load_l2_pipeline_config()
    assert not hasattr(cfg.signal, "peace_threshold"), (
        "Hard Bug 3 Failed: peace_threshold must be eradicated."
    )
    assert hasattr(cfg.srl, "brownian_q_threshold"), (
        "Hard Bug 3 Failed: missing Y-update baseline gate."
    )
    assert hasattr(cfg.signal, "signal_epi_threshold"), (
        "Hard Bug 3 Failed: missing epiplexity signal gate."
    )


def test_flaw4_dimensional_consistency():
    """Audit lock 4: topology energy must remain dimensionless."""
    from config import load_l2_pipeline_config

    cfg = load_l2_pipeline_config()
    assert not hasattr(cfg.signal, "topo_energy_sigma_mult"), (
        "Hard Bug 4 Failed: dimensional violation still exists."
    )
    assert hasattr(cfg.signal, "topo_energy_min"), (
        "Hard Bug 4 Failed: missing pure dimensionless topology limit."
    )


def test_flaw5_prequential_mdl_delta_k_zero():
    """Audit lock 5: repo-wide ghost delta_k must be eradicated."""
    import inspect

    sig = inspect.signature(calc_srl_compression_gain_rolling)
    assert "delta_k" not in sig.parameters, (
        "Hard Bug 5 Failed: Ghost parameter delta_k is still alive!"
    )

    for path in [
        "omega_core/omega_math_core.py",
        "omega_core/omega_math_vectorized.py",
    ]:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "delta_k = 2.0" not in content, (
            f"Hard Bug 5 Failed: repo-wide ghost delta_k survived in {path}!"
        )


def test_flaw6_no_srl_resid_overwrite():
    """Audit lock 6: has_singularity must never manually overwrite SRL residuals."""
    with open("omega_core/kernel.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "out_srl_resid[has_singularity_mask] = 0.0" not in content, (
        "Hard Bug 6 Failed: srl_resid is being manually overridden by singularity mask!"
    )


def test_flaw7_single_compression_semantic():
    """Audit lock 7: kernel must not carry a second compression branch."""
    with open("omega_core/kernel.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "bits_srl =" not in content and "var_srl_resid / var_price_change" not in content, (
        "Hard Bug 7 Failed: schizophrenic second compression branch bits_srl detected!"
    )


def test_kernel_keeps_singularity_residual_observable():
    """Kernel must never rewrite SRL residuals to zero just because a row is tagged singular."""
    cfg = load_l2_pipeline_config()
    frames = _make_kernel_frames()
    result = apply_recursive_physics(frames, cfg)

    idx = 12
    expected_price_change = float(frames.get_column("close")[idx] - frames.get_column("open")[idx])
    resid = float(result.get_column("srl_resid")[idx])

    assert bool(result.get_column("is_physics_valid")[idx]) is False
    np.testing.assert_allclose(resid, expected_price_change, atol=1e-9)
    assert resid != 0.0, "Kernel rewrote singular residual to zero."


def test_kernel_topo_area_stays_on_canonical_isoperimetric_path():
    """topo_area must equal the canonical isoperimetric rolling output, not a manifold overwrite."""
    cfg = load_l2_pipeline_config()
    frames = _make_kernel_frames()
    result = apply_recursive_physics(frames, cfg)

    window = int(cfg.epiplexity.min_trace_len)
    dist = np.arange(frames.height, dtype=np.int32)
    expected_area, _, _ = calc_isoperimetric_topology_rolling(
        prices=frames.get_column("close").to_numpy(),
        ofis=frames.get_column("net_ofi").to_numpy(),
        window=window,
        price_scale_floor=float(cfg.topology_race.price_scale_floor),
        ofi_scale_floor=float(cfg.topology_race.ofi_scale_floor),
        green_coeff=0.5,
        dist_to_boundary=dist,
    )

    np.testing.assert_allclose(
        result.get_column("topo_area").to_numpy()[window - 1 :],
        expected_area[window - 1 :],
        atol=1e-9,
    )


def test_kernel_removes_bits_srl_double_counting():
    """The canonical compression path must not emit a second SRL compression channel."""
    cfg = load_l2_pipeline_config()
    result = apply_recursive_physics(_make_kernel_frames(), cfg)

    assert "bits_srl" not in result.columns, "bits_srl should not survive as a second compression definition."
    assert set(result.get_column("dominant_probe").drop_nulls().unique().to_list()) <= {1}, (
        "dominant_probe must remain a compatibility placeholder pinned to 1."
    )

    bits_linear = result.get_column("bits_linear").fill_null(0.0).fill_nan(0.0).to_numpy()
    bits_topology = result.get_column("bits_topology").fill_null(0.0).fill_nan(0.0).to_numpy()
    srl_phase = result.get_column("srl_phase").to_numpy()
    expected = (bits_linear + bits_topology) * srl_phase

    np.testing.assert_allclose(
        result.get_column("singularity_vector").to_numpy(),
        expected,
        atol=1e-9,
    )


def test_kernel_repairs_interleaved_symbol_order_and_restores_original_row_order():
    cfg = load_l2_pipeline_config()
    interleaved = _make_interleaved_kernel_frames()
    sorted_frames = interleaved.sort(["symbol", "date", "time_end", "bucket_id"])

    repaired = apply_recursive_physics(interleaved, cfg)
    canonical = apply_recursive_physics(sorted_frames, cfg)

    assert repaired.get_column("symbol").to_list() == interleaved.get_column("symbol").to_list()
    assert repaired.get_column("time_end").to_list() == interleaved.get_column("time_end").to_list()

    repaired_sorted = repaired.sort(["symbol", "date", "time_end", "bucket_id"])
    for col in ("topo_area", "topo_energy", "epiplexity", "srl_resid", "adaptive_y"):
        np.testing.assert_allclose(
            repaired_sorted.get_column(col).to_numpy(),
            canonical.get_column(col).to_numpy(),
            atol=1e-9,
            rtol=1e-9,
        )

    assert repaired_sorted.get_column("topo_energy").max() > 0.0


def test_kernel_ordering_fix_can_be_disabled_for_explicit_rollback(monkeypatch):
    cfg = load_l2_pipeline_config()
    interleaved = _make_interleaved_kernel_frames()

    monkeypatch.setenv("OMEGA_STAGE2_FIX_KERNEL_ORDERING", "0")
    legacy = apply_recursive_physics(interleaved, cfg)

    monkeypatch.setenv("OMEGA_STAGE2_FIX_KERNEL_ORDERING", "1")
    fixed = apply_recursive_physics(interleaved, cfg)

    assert legacy.get_column("topo_energy").max() == 0.0
    assert fixed.sort(["symbol", "date", "time_end", "bucket_id"]).get_column("topo_energy").max() > 0.0


def test_kernel_rejects_multisymbol_frames_without_order_key():
    cfg = load_l2_pipeline_config()
    broken = pl.DataFrame(
        {
            "symbol": ["000001.SZ", "000002.SZ", "000001.SZ", "000002.SZ"],
            "date": ["20250101", "20250101", "20250101", "20250101"],
            "open": [10.0, 10.5, 10.1, 10.6],
            "close": [10.1, 10.4, 10.2, 10.5],
            "sigma": [0.2, 0.2, 0.2, 0.2],
            "depth": [1000.0, 1000.0, 1000.0, 1000.0],
            "net_ofi": [10.0, -10.0, 11.0, -11.0],
            "trade_vol": [1000.0, 1000.0, 1001.0, 1001.0],
            "cancel_vol": [10.0, 10.0, 11.0, 11.0],
        }
    )

    with pytest.raises(RuntimeError, match="kernel_ordering_contract_missing_time_key"):
        apply_recursive_physics(broken, cfg)
