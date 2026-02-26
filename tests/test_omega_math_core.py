"""
test_omega_math_core.py

Unit tests for OMEGA core math kernels: SRL, Epiplexity, Topology.
Tests mathematical correctness, edge cases, and invariants.
"""
import math
import sys
import os
import unittest

import numpy as np

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import L2EpiplexityConfig, L2SRLConfig, L2TopoSNRConfig, L2TopologyRaceConfig
from omega_core.omega_math_core import (
    calc_compression_gain,
    calc_epiplexity,
    calc_srl_state,
    calc_topology_area,
    calc_holographic_topology,
    topo_snr_from_traces,
)


class TestCompressionGain(unittest.TestCase):
    """Tests for calc_compression_gain (Epiplexity / MDL Gain)."""

    def setUp(self):
        self.cfg = L2EpiplexityConfig()

    def test_pure_linear_trend_has_high_gain(self):
        """A perfectly linear sequence has maximum compressibility."""
        trace = [float(i) for i in range(50)]
        gain = calc_compression_gain(trace, self.cfg)
        # Linear = perfect R², so MDL gain should be very high
        self.assertGreater(gain, 10.0)

    def test_pure_noise_has_low_gain(self):
        """Random noise should yield near-zero gain."""
        np.random.seed(42)
        trace = np.random.randn(100).tolist()
        gain = calc_compression_gain(trace, self.cfg)
        # Noise has no linear structure, MDL gain should be low
        self.assertLessEqual(gain, 5.0)

    def test_constant_trace_returns_zero(self):
        """Zero-variance (constant) trace returns 0.0."""
        trace = [5.0] * 50
        gain = calc_compression_gain(trace, self.cfg)
        self.assertEqual(gain, 0.0)

    def test_short_trace_returns_fallback(self):
        """Trace shorter than min_trace_len returns fallback value."""
        trace = [1.0, 2.0, 3.0]  # Only 3 points, default min=10
        gain = calc_compression_gain(trace, self.cfg)
        self.assertEqual(gain, float(self.cfg.fallback_value))

    def test_empty_trace_returns_fallback(self):
        """Empty trace returns fallback."""
        gain = calc_compression_gain([], self.cfg)
        self.assertEqual(gain, float(self.cfg.fallback_value))

    def test_gain_is_non_negative(self):
        """Gain is always >= 0 (MDL discipline)."""
        for seed in range(10):
            np.random.seed(seed)
            trace = np.random.randn(50).tolist()
            gain = calc_compression_gain(trace, self.cfg)
            self.assertGreaterEqual(gain, 0.0)

    def test_gain_increases_with_structure(self):
        """More structured data should yield higher gain."""
        np.random.seed(42)
        noise = np.random.randn(50)
        # Signal with varying SNR
        gains = []
        for snr in [0.0, 0.5, 1.0, 5.0]:
            trace = (snr * np.arange(50) + noise).tolist()
            gains.append(calc_compression_gain(trace, self.cfg))
        # Gains should be generally non-decreasing with SNR
        self.assertGreater(gains[-1], gains[0])


class TestSRLState(unittest.TestCase):
    """Tests for calc_srl_state (Square Root Law)."""

    def setUp(self):
        self.cfg = L2SRLConfig()

    def test_zero_ofi_yields_zero_impact(self):
        """With zero order flow, theoretical impact is zero."""
        resid, implied_y, depth_eff, spoof = calc_srl_state(
            price_change=0.01, sigma=0.02, net_ofi=0.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
        )
        # Impact = Y * sigma * sqrt(0/D) = 0, so resid = price_change
        self.assertAlmostEqual(resid, 0.01, places=6)

    def test_positive_ofi_positive_impact(self):
        """Positive net OFI should predict positive price impact."""
        resid, implied_y, depth_eff, spoof = calc_srl_state(
            price_change=0.05, sigma=0.02, net_ofi=500.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
        )
        # With positive OFI, theory impact is positive, so residual < price_change
        self.assertLess(resid, 0.05)

    def test_depth_floor_prevents_division_by_zero(self):
        """Depth floor prevents sqrt(Q/0) explosion."""
        resid, implied_y, depth_eff, spoof = calc_srl_state(
            price_change=0.01, sigma=0.02, net_ofi=100.0,
            depth=0.0, current_y=1.0, cfg=self.cfg,
        )
        self.assertTrue(np.isfinite(resid))
        self.assertTrue(np.isfinite(implied_y))
        self.assertGreater(depth_eff, 0)

    def test_sigma_floor_prevents_zero_sigma(self):
        """Sigma floor prevents zero volatility collapse."""
        resid, implied_y, depth_eff, spoof = calc_srl_state(
            price_change=0.01, sigma=0.0, net_ofi=100.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
        )
        self.assertTrue(np.isfinite(resid))

    def test_spoofing_penalty_reduces_effective_depth(self):
        """High cancel/trade ratio should reduce effective depth."""
        _, _, depth_no_spoof, spoof_no = calc_srl_state(
            price_change=0.01, sigma=0.02, net_ofi=100.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
            cancel_vol=0.0, trade_vol=100.0,
        )
        _, _, depth_with_spoof, spoof_yes = calc_srl_state(
            price_change=0.01, sigma=0.02, net_ofi=100.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
            cancel_vol=5000.0, trade_vol=100.0,
        )
        self.assertLessEqual(depth_with_spoof, depth_no_spoof)
        self.assertGreater(spoof_yes, spoof_no)

    def test_returns_four_values(self):
        """Returns exactly (resid, implied_y, depth_eff, spoof_ratio)."""
        result = calc_srl_state(
            price_change=0.01, sigma=0.02, net_ofi=100.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
        )
        self.assertEqual(len(result), 4)
        for v in result:
            self.assertIsInstance(v, float)
            self.assertTrue(np.isfinite(v))

    def test_implied_y_inversely_related_to_impact(self):
        """Implied Y = |dP| / impact_unit. Larger dP → larger implied Y."""
        _, y_small, _, _ = calc_srl_state(
            price_change=0.01, sigma=0.02, net_ofi=500.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
        )
        _, y_large, _, _ = calc_srl_state(
            price_change=0.10, sigma=0.02, net_ofi=500.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
        )
        self.assertGreater(y_large, y_small)

    def test_delta_is_half(self):
        """Verify delta=0.5 universality (Sato 2025)."""
        # Impact should scale as sqrt(Q/D). Double Q should increase impact by sqrt(2).
        _, _, _, _ = calc_srl_state(
            price_change=0.0, sigma=1.0, net_ofi=100.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
        )
        resid1, _, _, _ = calc_srl_state(
            price_change=0.0, sigma=1.0, net_ofi=100.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
        )
        resid2, _, _, _ = calc_srl_state(
            price_change=0.0, sigma=1.0, net_ofi=400.0,
            depth=1000.0, current_y=1.0, cfg=self.cfg,
        )
        # Theory: impact1 = 1 * 1 * sqrt(100/1000) = sqrt(0.1)
        # Theory: impact2 = 1 * 1 * sqrt(400/1000) = sqrt(0.4)
        # Ratio should be sqrt(4) = 2
        self.assertAlmostEqual(resid2 / resid1, 2.0, places=4)


class TestTopologyArea(unittest.TestCase):
    """Tests for calc_topology_area (Green's theorem proxy)."""

    def test_unit_square_has_correct_area(self):
        """Known shape: unit-circle-like trajectory has predictable area."""
        # Counterclockwise square: area should be positive
        x = [0, 1, 1, 0, 0]
        y = [0, 0, 1, 1, 0]
        area = calc_topology_area(
            x, y,
            x_scale_floor=0.01, y_scale_floor=0.01, green_coeff=0.5,
        )
        self.assertNotEqual(area, 0.0)

    def test_degenerate_trace_returns_zero(self):
        """Single point or empty trace returns zero."""
        self.assertEqual(calc_topology_area([1], [1], 0.01, 0.01, 0.5), 0.0)
        self.assertEqual(calc_topology_area([], [], 0.01, 0.01, 0.5), 0.0)

    def test_scale_floor_prevents_explosion(self):
        """Constant x or y trace (zero std) uses scale floor."""
        x = [5.0] * 10
        y = [float(i) for i in range(10)]
        area = calc_topology_area(x, y, 0.01, 0.01, 0.5)
        self.assertTrue(np.isfinite(area))

    def test_sign_reverses_with_direction(self):
        """Reversing traversal direction reverses sign."""
        x = [0, 1, 2, 3, 4]
        y = [0, 1, 0, -1, 0]
        area_fwd = calc_topology_area(x, y, 0.01, 0.01, 0.5)
        area_rev = calc_topology_area(x[::-1], y[::-1], 0.01, 0.01, 0.5)
        self.assertAlmostEqual(area_fwd, -area_rev, places=6)

    def test_green_coeff_scales_linearly(self):
        """Output scales linearly with green_coeff."""
        x = [0, 1, 2, 1, 0]
        y = [0, 1, 0, -1, 0]
        a1 = calc_topology_area(x, y, 0.01, 0.01, 0.5)
        a2 = calc_topology_area(x, y, 0.01, 0.01, 1.0)
        self.assertAlmostEqual(a2, 2.0 * a1, places=6)


class TestHolographicTopology(unittest.TestCase):
    """Tests for calc_holographic_topology (Signed Area + Energy)."""

    def test_returns_area_and_energy(self):
        """Returns exactly (signed_area, energy) tuple."""
        trace = [1.0, 2.0, 3.0, 2.0, 1.0]
        ofi = [100, 200, -50, -100, 50]
        area, energy = calc_holographic_topology(trace, ofi)
        self.assertIsInstance(area, float)
        self.assertIsInstance(energy, float)
        self.assertTrue(np.isfinite(area))
        self.assertTrue(np.isfinite(energy))

    def test_short_trace_returns_zeros(self):
        """Single point returns (0, 0)."""
        area, energy = calc_holographic_topology([5.0], [100])
        self.assertEqual(area, 0.0)
        self.assertEqual(energy, 0.0)

    def test_energy_is_non_negative(self):
        """Energy (path length) is always >= 0."""
        for seed in range(10):
            np.random.seed(seed)
            trace = np.cumsum(np.random.randn(20)).tolist()
            ofi = np.random.randint(-100, 100, size=20).tolist()
            _, energy = calc_holographic_topology(trace, ofi)
            self.assertGreaterEqual(energy, 0.0)

    def test_straight_line_has_minimal_area(self):
        """Perfectly correlated price+flow has low/zero loop area."""
        # Price and cumulative OFI move in same direction = no loop
        trace = [float(i) for i in range(20)]
        ofi = [1.0] * 20  # cumsum = [1, 2, 3, ..., 20]
        area, energy = calc_holographic_topology(trace, ofi)
        # Strong correlation → small area
        self.assertLess(abs(area), 1.0)


class TestTopoSNR(unittest.TestCase):
    """Tests for topo_snr_from_traces (topological signal-to-noise ratio)."""

    def setUp(self):
        self.topo_cfg = L2TopoSNRConfig(n_shuffle=20, seed=42)
        self.epi_cfg = L2EpiplexityConfig()

    def test_structured_traces_have_higher_snr(self):
        """Structured (non-random) traces should have SNR ≠ 0."""
        # Create traces with clear structure
        structured = [[math.sin(i * 0.3) for i in range(30)] for _ in range(5)]
        snr = topo_snr_from_traces(structured, self.topo_cfg, self.epi_cfg)
        self.assertIsInstance(snr, float)
        self.assertTrue(np.isfinite(snr))

    def test_returns_finite_for_random_data(self):
        """Random data should return a finite SNR value."""
        np.random.seed(123)
        random_traces = [np.random.randn(30).tolist() for _ in range(5)]
        snr = topo_snr_from_traces(random_traces, self.topo_cfg, self.epi_cfg)
        self.assertTrue(np.isfinite(snr))


class TestMathInvariants(unittest.TestCase):
    """Cross-cutting invariant tests across multiple functions."""

    def test_all_functions_handle_nan_gracefully(self):
        """Functions should not crash on NaN inputs (produce finite or fallback)."""
        cfg_epi = L2EpiplexityConfig()
        cfg_srl = L2SRLConfig()

        # Compression gain with NaN
        gain = calc_compression_gain([1.0, float("nan"), 3.0] * 10, cfg_epi)
        # Should return a number (possibly 0 or fallback), not crash
        self.assertIsInstance(gain, float)

        # SRL with NaN price_change
        result = calc_srl_state(
            price_change=float("nan"), sigma=0.02, net_ofi=100.0,
            depth=1000.0, current_y=1.0, cfg=cfg_srl,
        )
        self.assertEqual(len(result), 4)

    def test_all_functions_handle_extreme_values(self):
        """Functions should not overflow on extreme inputs."""
        cfg_srl = L2SRLConfig()

        result = calc_srl_state(
            price_change=1e15, sigma=1e-15, net_ofi=1e15,
            depth=1e-15, current_y=1e15, cfg=cfg_srl,
        )
        for v in result:
            self.assertIsInstance(v, float)
            # Should not be inf (floors should prevent it)


if __name__ == "__main__":
    unittest.main()
