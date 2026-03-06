import math
import os
import sys

import numpy as np
import polars as pl

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import load_l2_pipeline_config
from omega_core.kernel import apply_recursive_physics
from omega_core.omega_math_rolling import (
    calc_isoperimetric_topology_rolling,
    calc_srl_compression_gain_rolling,
)


def _make_kernel_frames(n: int = 16) -> pl.DataFrame:
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

    bits_linear = result.get_column("bits_linear").fill_null(0.0).fill_nan(0.0).to_numpy()
    bits_topology = result.get_column("bits_topology").fill_null(0.0).fill_nan(0.0).to_numpy()
    srl_phase = result.get_column("srl_phase").to_numpy()
    expected = (bits_linear + bits_topology) * srl_phase

    np.testing.assert_allclose(
        result.get_column("singularity_vector").to_numpy(),
        expected,
        atol=1e-9,
    )
