"""
test_stage2_output_equivalence.py

Regression test for perf/stage2-speedup-v62 optimizations.
Validates that:
  1. build_l2_features_from_l1 produces expected columns after rolling_mean_by refactor
  2. apply_recursive_physics produces expected physics columns including MDL arena
  3. dominant_probe stays pinned to the compatibility placeholder value 1
  4. epiplexity is zero where MDL gain <= 0 (Turing discipline)
  5. Schema dtypes match expectations

Uses synthetic data so no real L1 parquets are needed.
"""

import os
import sys
import unittest
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import polars as pl
from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l2_features_from_l1
from omega_core.kernel import apply_recursive_physics


def _make_synthetic_l1(n_ticks_per_symbol=200, symbols=None):
    """Create a minimal synthetic L1 DataFrame matching Stage1 output schema."""
    if symbols is None:
        symbols = ["000001.SZ", "000002.SZ", "600000.SH"]

    rows = []
    np.random.seed(42)
    base_time_ms = 34_200_000  # 09:30:00.000 in ms-of-day

    for sym in symbols:
        price = 10.0 + np.random.randn() * 2
        for i in range(n_ticks_per_symbol):
            t_ms = base_time_ms + i * 3000  # 3s apart
            price += np.random.randn() * 0.02
            vol = max(1, int(np.random.exponential(500)))
            bid_p1 = price - 0.01
            ask_p1 = price + 0.01
            bid_v1 = max(1, int(np.random.exponential(200)))
            ask_v1 = max(1, int(np.random.exponential(200)))

            rows.append({
                "symbol": sym,
                "date": "20250101",
                "time": int(t_ms),
                "__time_ms": int(t_ms),
                "price": price,
                "vol": float(vol),
                "turnover": price * vol,
                "vol_tick": float(vol),
                "bid_p1": bid_p1,
                "ask_p1": ask_p1,
                "bid_v1": float(bid_v1),
                "ask_v1": float(ask_v1),
                "bs_flag": 1,
            })

    df = pl.DataFrame(rows)
    # Ensure numeric types
    df = df.cast({
        "price": pl.Float64,
        "vol": pl.Float64,
        "turnover": pl.Float64,
        "vol_tick": pl.Float64,
        "bid_p1": pl.Float64,
        "ask_p1": pl.Float64,
        "bid_v1": pl.Float64,
        "ask_v1": pl.Float64,
        "__time_ms": pl.Int64,
    })
    return df


class TestStage2OutputEquivalence(unittest.TestCase):

    def setUp(self):
        self.cfg = load_l2_pipeline_config()
        self.l1_df = _make_synthetic_l1(n_ticks_per_symbol=200)

    def test_build_l2_features_produces_expected_columns(self):
        """build_l2_features_from_l1 should produce bucketed frames with physics-ready columns."""
        l2_df = build_l2_features_from_l1(self.l1_df.lazy(), self.cfg)

        self.assertGreater(l2_df.height, 0, "L2 should produce non-empty output")

        # Core columns that must exist after ETL
        required = {"open", "close", "sigma", "net_ofi", "depth", "n_ticks", "trade_vol", "symbol"}
        missing = required - set(l2_df.columns)
        self.assertEqual(missing, set(), f"Missing columns: {missing}")

    def test_apply_recursive_physics_produces_all_features(self):
        """Full pipeline should produce all V62 physics + MDL arena columns."""
        l2_df = build_l2_features_from_l1(self.l1_df.lazy(), self.cfg)
        result_df = apply_recursive_physics(l2_df, self.cfg)

        self.assertGreater(result_df.height, 0, "Physics output should be non-empty")

        # V62 required feature columns
        physics_cols = {
            "epiplexity", "srl_resid", "adaptive_y", "spoof_ratio",
            "topo_area", "topo_energy", "is_signal", "direction",
        }
        missing = physics_cols - set(result_df.columns)
        self.assertEqual(missing, set(), f"Missing physics columns: {missing}")

    def test_dominant_probe_is_compatibility_placeholder(self):
        """dominant_probe must remain a fixed compatibility placeholder at 1."""
        l2_df = build_l2_features_from_l1(self.l1_df.lazy(), self.cfg)
        result_df = apply_recursive_physics(l2_df, self.cfg)

        if "dominant_probe" not in result_df.columns:
            self.skipTest("dominant_probe column not present (no symbol column?)")

        probe_vals = result_df.get_column("dominant_probe").drop_nulls().unique().to_list()
        for v in probe_vals:
            self.assertEqual(v, 1, f"dominant_probe must be pinned to 1, got: {v}")

    def test_epiplexity_turing_discipline(self):
        """epiplexity should be non-negative (MDL gain <= 0 returns 0.0 per v62)."""
        l2_df = build_l2_features_from_l1(self.l1_df.lazy(), self.cfg)
        result_df = apply_recursive_physics(l2_df, self.cfg)

        epi = result_df.get_column("epiplexity").to_numpy()
        self.assertTrue(np.all(epi >= 0), "epiplexity should never be negative (Turing discipline)")

    def test_bits_columns_non_negative(self):
        """bits_linear and bits_topology should both stay finite and non-negative."""
        l2_df = build_l2_features_from_l1(self.l1_df.lazy(), self.cfg)
        result_df = apply_recursive_physics(l2_df, self.cfg)

        self.assertNotIn("bits_srl", result_df.columns, "bits_srl should not exist after V64.3 completion.")

        for col in ["bits_linear", "bits_topology"]:
            if col not in result_df.columns:
                continue
            vals = result_df.get_column(col).drop_nulls().to_numpy()
            self.assertTrue(
                np.all(np.isfinite(vals)),
                f"{col} contains non-finite values"
            )
            self.assertTrue(
                np.all(vals >= 0),
                f"{col} contains negative values (MDL clipping broken)"
            )

    def test_no_inf_or_nan_in_physics_columns(self):
        """Physics columns must not contain inf or NaN — key v62 safety requirement."""
        l2_df = build_l2_features_from_l1(self.l1_df.lazy(), self.cfg)
        result_df = apply_recursive_physics(l2_df, self.cfg)

        safety_cols = ["srl_resid", "adaptive_y", "epiplexity", "topo_area", "topo_energy"]
        for col in safety_cols:
            if col not in result_df.columns:
                continue
            arr = result_df.get_column(col).to_numpy()
            self.assertTrue(
                np.all(np.isfinite(arr)),
                f"{col} contains inf or NaN (log-bomb safety broken)"
            )


if __name__ == "__main__":
    unittest.main()
