"""
trainer.py

Level-2 (v5) machine learning trainer.
"""

from __future__ import annotations

import pickle
import time
import os
import shutil
from pathlib import Path
from typing import Dict, List

import numpy as np
import polars as pl
import psutil
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

from config import L2PipelineConfig
from omega_core.kernel import apply_recursive_physics
from omega_core.omega_math_core import topo_snr_from_traces
from tools.multi_dir_loader import discover_l2_dirs

def check_memory_safe(threshold=85.0, sleep_sec=10):
    while psutil.virtual_memory().percent > threshold:
        time.sleep(sleep_sec)

class OmegaTrainerV3:
    def __init__(self, cfg: L2PipelineConfig):
        self.cfg = cfg
        self.model = SGDClassifier(loss="log_loss", penalty="l2", alpha=1e-4, average=True)
        self.scaler = StandardScaler()

        # v5.0 Features: Physics & Structure
        topo_race_cols = list(getattr(self.cfg.train, "topology_race_features", ()))
        
        raw_feature_cols = [
            "sigma_eff",
            "net_ofi",
            "depth_eff",
            "epiplexity",     # Compression Gain (Structure)
            "srl_resid",      # Universal 0.5 Residual
            "topo_area",
            "topo_energy",
            *topo_race_cols,
            "price_change",
            "bar_duration_ms",
            "adaptive_y"      # State
        ]
        self.feature_cols = list(dict.fromkeys(raw_feature_cols))
        self.label_col = "direction_label"

    @staticmethod
    def _signed_log1p(expr: pl.Expr) -> pl.Expr:
        return (expr.sign() * (expr.abs() + 1.0).log()).alias(expr.meta.output_name())

    @staticmethod
    def _winsorize(df: pl.DataFrame, col: str, q_low: float, q_high: float) -> pl.DataFrame:
        if col not in df.columns: return df
        lo = df.select(pl.col(col).quantile(q_low)).item()
        hi = df.select(pl.col(col).quantile(q_high)).item()
        return df.with_columns(pl.col(col).clip(lo, hi))

    def _prepare_frames(self, df: pl.DataFrame, cfg: L2PipelineConfig) -> pl.DataFrame:
        # Check if physics already applied (V5 Framer Output)
        if "epiplexity" not in df.columns or "srl_resid" not in df.columns:
             df = apply_recursive_physics(df, cfg)
        
        tcfg = cfg.train
        horizon = int(tcfg.label_horizon_buckets)
        label_sigma_mult = float(tcfg.label_sigma_mult)
        
        # Helper for window functions
        def _over_symbol(expr):
            if "symbol" in df.columns:
                return expr.over("symbol")
            return expr

        # Calculate Forward Returns (Label Generation)
        # MUST be per-symbol
        df = df.with_columns([
            (_over_symbol(pl.col("close").shift(-horizon)) - pl.col("close")).alias("fwd_change")
        ]).with_columns([
            (pl.col("fwd_change") / pl.col("close")).alias("ret_k"),
            (pl.col("sigma_eff") / pl.col("close")).alias("sigma_ret")
        ]).with_columns(
            pl.when(pl.col("ret_k").abs() > label_sigma_mult * pl.col("sigma_ret"))
            .then(pl.col("ret_k").sign())
            .otherwise(0.0)
            .alias(self.label_col)
        ).drop_nulls()
        
        for col in tcfg.winsor_features:
            df = self._winsorize(df, col, float(tcfg.winsor_q_low), float(tcfg.winsor_q_high))
            
        return df

    def train(self, sample_frac: float = 1.0):
        print(f"Starting training OMEGA v5.0...")
        dirs = discover_l2_dirs()
        if not dirs: return

        classes = np.array([-1, 0, 1])
        if self.cfg.train.drop_neutral_labels: classes = np.array([-1, 1])
        
        total_rows = 0
        for d in dirs:
            files = sorted(list(d.glob("*.parquet")))
            for f in files:
                try:
                    lf = pl.scan_parquet(str(f))
                    if sample_frac < 1.0: lf = lf.sample(fraction=sample_frac)
                    df_batch = lf.collect()
                    if df_batch.height == 0: continue
                    
                    df_batch = self._prepare_frames(df_batch, self.cfg)
                    
                    missing = [c for c in self.feature_cols if c not in df_batch.columns]
                    if missing: continue

                    X = df_batch.select(self.feature_cols).to_numpy()
                    y = df_batch.select(self.label_col).to_numpy().ravel()
                    
                    # Finzi 2026: Weight by Epiplexity (Structure)
                    # We learn more from structured regimes.
                    weights = df_batch["epiplexity"].to_numpy()
                    
                    self.scaler.partial_fit(X)
                    X_scaled = self.scaler.transform(X)
                    self.model.partial_fit(X_scaled, y, classes=classes, sample_weight=weights)
                    
                    total_rows += len(y)
                    if total_rows % 200000 == 0: print(f"Rows: {total_rows}")
                except Exception as e:
                    print(f"Error {f.name}: {e}")

        self.save()

    def save(self, out_dir: str = "./artifacts", name: str = "omega_v5_model.pkl"):
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        path = Path(out_dir) / name
        with open(path, "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler, "features": self.feature_cols}, f)
        print(f"Model saved: {path}")


def evaluate_frames(df: pl.DataFrame, cfg: L2PipelineConfig) -> Dict[str, float]:
    """
    Compute physics audit metrics (SNR, Orthogonality, Alignment).
    Safe for multi-symbol data because metrics are distributional.
    """
    # 1. Topo SNR
    if "trace" in df.columns:
        # Sample for speed (1000 traces is enough for SNR)
        sample_size = min(df.height, 1000)
        # Use simple random sampling
        sample_df = df.sample(sample_size, seed=42)
        traces = sample_df["trace"].to_list()
        
        snr = topo_snr_from_traces(traces, cfg.topo_snr, cfg.epiplexity)
    else:
        snr = float("nan")

    # 2. Orthogonality (Epi vs Residual)
    if "epiplexity" in df.columns and "srl_resid" in df.columns:
        valid = df.filter(pl.col("epiplexity").is_finite() & pl.col("srl_resid").is_finite())
        if valid.height > 10:
            orth = np.corrcoef(valid["epiplexity"].to_numpy(), valid["srl_resid"].abs().to_numpy())[0, 1]
        else:
            orth = 0.0
    else:
        orth = float("nan")

    # 3. Vector Alignment (Price vs OFI)
    if "price_change" in df.columns and "net_ofi" in df.columns:
        valid = df.filter(pl.col("price_change").is_finite() & pl.col("net_ofi").is_finite())
        if valid.height > 10:
            align = np.corrcoef(valid["price_change"].to_numpy(), valid["net_ofi"].to_numpy())[0, 1]
        else:
            align = 0.0
    else:
        align = float("nan")

    return {
        "Topo_SNR": float(snr),
        "Orthogonality": float(orth),
        "Vector_Alignment": float(align)
    }


def evaluate_dod(metrics: Dict[str, float], cfg: L2PipelineConfig) -> bool:
    """
    Check Definition of Done.
    """
    val = cfg.validation
    if metrics.get("Topo_SNR", 0) < float(val.topo_snr_min): return False
    if abs(metrics.get("Orthogonality", 1)) > float(val.orthogonality_max_abs): return False
    if metrics.get("Vector_Alignment", 0) < float(val.vector_alignment_min): return False
    return True
