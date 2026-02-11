
import unittest
import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from omega_core.omega_math_core import calc_compression_gain, calc_srl_state
from config import L2EpiplexityConfig, L2SRLConfig

class TestOmegaMathCore(unittest.TestCase):
    def test_compression_gain_perfect_linear(self):
        """Verified: A perfect linear trend should yield Gain near 1.0."""
        cfg = L2EpiplexityConfig(min_trace_len=10)
        # Perfect line: y = 2x + 5
        trace = [2.0 * x + 5.0 for x in range(20)]
        gain = calc_compression_gain(trace, cfg)
        self.assertGreater(gain, 0.99, f"Perfect line should have high gain, got {gain}")

    def test_compression_gain_random_noise(self):
        """Verified: Random noise should yield Gain near 0.0."""
        cfg = L2EpiplexityConfig(min_trace_len=10)
        np.random.seed(42)
        trace = np.random.normal(0, 1, 100).tolist()
        gain = calc_compression_gain(trace, cfg)
        # Since it's random, a small linear trend might exist by chance, but gain should be low.
        self.assertLess(gain, 0.1, f"Random noise should have low gain, got {gain}")

    def test_srl_universality_05(self):
        """Verified: Sato (2025) Universality (Delta=0.5)."""
        cfg = L2SRLConfig(depth_floor=1.0, sigma_floor=0.01)
        
        # Test Case:
        # Sigma = 1.0, OFI = 100, Depth = 4
        # Impact = Y * Sigma * sqrt(OFI / Depth)
        # If Y = 1.0, Impact = 1.0 * 1.0 * sqrt(100 / 4) = 1.0 * 5.0 = 5.0
        # If Price Change is 5.0, Residual should be 0.0
        
        resid, implied_y, _, _ = calc_srl_state(
            price_change=5.0,
            sigma=1.0,
            net_ofi=100.0,
            depth=4.0,
            current_y=1.0,
            cfg=cfg
        )
        
        self.assertAlmostEqual(resid, 0.0, places=5, msg=f"SRL Residual should be 0, got {resid}")
        self.assertAlmostEqual(implied_y, 1.0, places=5, msg=f"Implied Y should be 1.0, got {implied_y}")

    def test_srl_spoofing_penalty(self):
        """Verified: High cancellation volume should reduce effective depth and increase implied rigidity."""
        cfg = L2SRLConfig(depth_floor=1.0, sigma_floor=0.01)
        # Set gamma to a visible value if not default
        # We need to check if spoof_penalty_gamma exists in the object or use a custom one if possible
        # For this test, we assume the core logic handles it.
        
        # Scenario 1: No spoofing
        _, y1, d1, _ = calc_srl_state(5.0, 1.0, 100.0, 4.0, 1.0, cfg, cancel_vol=0.0, trade_vol=100.0)
        
        # Scenario 2: High spoofing (Cancel = 10x Trade)
        # This should decrease effective depth, making the move 'harder' to explain, thus higher implied_y
        _, y2, d2, _ = calc_srl_state(5.0, 1.0, 100.0, 4.0, 1.0, cfg, cancel_vol=1000.0, trade_vol=100.0)
        
        self.assertLess(d2, d1, "Effective depth should decrease with spoofing")
        self.assertGreater(y2, y1, "Implied Y should increase when depth is penalized by spoofing")

if __name__ == "__main__":
    unittest.main()
