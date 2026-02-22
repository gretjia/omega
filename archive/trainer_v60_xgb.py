"""
v6 XGBoost anchor trainer.

This module keeps the core epistemic weighting logic isolated and reusable.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import polars as pl
import xgboost as xgb


class OmegaTrainerV6_XGB:
    def __init__(self, feature_cols: Sequence[str], weight_floor: float = 1e-4):
        self.feature_cols = list(feature_cols)
        self.weight_floor = float(weight_floor)

    def build_epistemic_dmatrix(self, df: pl.DataFrame) -> xgb.DMatrix:
        missing = [c for c in self.feature_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing feature columns: {missing}")
        if "t1_fwd_return" not in df.columns:
            raise ValueError("Required label column missing: t1_fwd_return")

        X = df.select(self.feature_cols).to_numpy()
        y = (df.get_column("t1_fwd_return").to_numpy() > 0).astype(int)

        epi = np.clip(df.get_column("epiplexity").to_numpy(), 0.0, 1.0)
        topo = np.log1p(np.abs(df.get_column("topo_area").to_numpy()))
        is_signal = (
            df.get_column("is_signal").to_numpy().astype(bool)
            if "is_signal" in df.columns
            else np.ones(df.height, dtype=bool)
        )
        is_physics_valid = (
            df.get_column("is_physics_valid").to_numpy().astype(bool)
            if "is_physics_valid" in df.columns
            else np.ones(df.height, dtype=bool)
        )
        weights = epi * topo * (is_signal & is_physics_valid).astype(float)
        valid_mask = np.isfinite(weights) & (weights > self.weight_floor)
        if not np.any(valid_mask):
            raise ValueError("No valid training samples after epistemic filtering.")

        return xgb.DMatrix(
            data=X[valid_mask],
            label=y[valid_mask],
            weight=weights[valid_mask],
            feature_names=self.feature_cols,
        )
