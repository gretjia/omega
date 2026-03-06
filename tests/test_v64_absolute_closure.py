import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from omega_core.omega_math_rolling import (
    calc_isoperimetric_topology_rolling,
    calc_srl_compression_gain_rolling,
)


def test_flaw1_zero_residual_explosion():
    """Audit lock 1: MDL gain must close correctly at the variance boundary."""
    w = 60
    dist = np.full(100, 999, dtype=np.int32)

    flat_dp = np.zeros(100, dtype=np.float64)
    flat_resid = np.zeros(100, dtype=np.float64)
    gain_flat = calc_srl_compression_gain_rolling(flat_dp, flat_resid, w, dist, 2.0)
    assert np.all(gain_flat == 0.0), "Hard Bug 1 Failed: zero-variance must yield 0 signal."

    rng = np.random.default_rng(42)
    huge_dp = rng.normal(10.0, 2.0, 100).astype(np.float64)
    tiny_resid = rng.normal(0.0, 1e-10, 100).astype(np.float64)
    gain_singularity = calc_srl_compression_gain_rolling(huge_dp, tiny_resid, w, dist, 2.0)

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
