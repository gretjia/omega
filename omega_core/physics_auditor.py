"""
physics_auditor.py (OMEGA v5.2)

OMEGA v5.2 Physics Auditor.
- Dual-Track Manifold Baseline Implementation.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import List

import numpy as np
import polars as pl

from config import L2PipelineConfig
from omega_core.kernel import OmegaKernel, apply_recursive_physics
from omega_core.trainer import get_latest_model, evaluate_frames


class OmegaPhysicsAuditor:
    def __init__(self, data_dir: str, output_dir: str = "./model_audit", cfg: L2PipelineConfig | None = None):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cfg = cfg or L2PipelineConfig()
        self.files = sorted(self.data_dir.glob("*.parquet"))
        self.model_payload = get_latest_model(out_dir=str(self.output_dir.parent / "artifacts"))

    def _rng(self, salt: int = 0) -> random.Random:
        seed = int(getattr(self.cfg.epiplexity, "prior_random_seed", 42))
        return random.Random(seed + int(salt))

    def _load_debug_frames(self, file_path: Path, initial_y: float, target_frames: float | None = None) -> pl.DataFrame:
        if file_path.suffix.lower() == ".parquet":
            try:
                df = pl.read_parquet(str(file_path))
                cols = set(df.columns)
                if "epiplexity" in cols and "srl_resid" in cols:
                    return df
                return apply_recursive_physics(df, self.cfg, initial_y=initial_y)
            except Exception:
                pass
        kernel = OmegaKernel(str(file_path), cfg=self.cfg)
        return kernel.run(initial_y=initial_y, target_frames=target_frames, debug_mode=True)

    def run_continuous_calibration(self, target_frames: float | None = None, sample_frac: float = 1.0) -> dict:
        priors = self.derive_market_priors()
        last_y_state = float(priors.get("ANCHOR_Y", self.cfg.srl.y_coeff))
        audit_frames: List[pl.DataFrame] = []

        for f_path in self.files:
            daily_df = self._load_debug_frames(
                f_path,
                initial_y=last_y_state,
                target_frames=target_frames,
            )
            if daily_df.is_empty():
                continue

            end_y = daily_df.select(pl.col("adaptive_y").tail(1)).item()
            if end_y is not None and math.isfinite(end_y):
                last_y_state = float(end_y)

            if sample_frac < 1.0:
                daily_df = daily_df.sample(fraction=float(sample_frac), seed=42)

            audit_frames.append(daily_df)

        if not audit_frames:
            return {"status": "no_data"}

        full_df = pl.concat(audit_frames, how="diagonal_relaxed")
        
        # Inject future_ret if missing
        if "future_ret" not in full_df.columns and "close" in full_df.columns:
            full_df = full_df.with_columns((pl.col("close").shift(-1) - pl.col("close")).alias("future_ret")).drop_nulls()

        metrics = self._generate_epistemic_report(full_df, final_y=last_y_state)
        metrics.update(
            {
                "PLANCK_SIGMA_GATE": float(priors.get("PLANCK_SIGMA_GATE", self.cfg.epiplexity.sigma_gate)),
                "ANCHOR_Y": float(priors.get("ANCHOR_Y", self.cfg.srl.anchor_y))
            }
        )
        self._export_config(target_frames, last_y_state, metrics, priors)
        return metrics

    def derive_market_priors(self) -> dict:
        if not self.files:
            return {}
        
        sample_n = int(max(1, self.cfg.epiplexity.prior_sample_files))
        sample_files = self._rng(salt=101).sample(self.files, min(sample_n, len(self.files)))
        
        all_sigmas = []
        all_implied_y = []
        lane_exp = 0.5

        for f_path in sample_files:
            df = self._load_debug_frames(f_path, initial_y=float(self.cfg.srl.anchor_y), target_frames=None)
            if df.is_empty():
                continue

            sigma = df["sigma_eff"].to_numpy() if "sigma_eff" in df.columns else df["sigma"].to_numpy()
            sigma = sigma[np.isfinite(sigma)]
            if sigma.size:
                all_sigmas.extend(sigma.tolist())

            price_change = df["price_change"].to_numpy() if "price_change" in df.columns else (df["close"] - df["open"]).to_numpy()
            net_ofi = np.asarray(df["net_ofi"].to_numpy(), dtype=float)
            depth_eff = np.asarray(df["depth_eff"].to_numpy(), dtype=float)
            sigma_eff = np.asarray(df["sigma_eff"].to_numpy(), dtype=float)

            raw_impact = sigma_eff * np.power(np.abs(net_ofi) / (depth_eff + 1e-9), lane_exp)
            valid = np.isfinite(raw_impact) & (raw_impact > 1e-6)
            
            if np.any(valid):
                implied_y = np.abs(np.asarray(price_change, dtype=float)[valid]) / raw_impact[valid]
                implied_y = implied_y[np.isfinite(implied_y)]
                if implied_y.size:
                    all_implied_y.extend(implied_y.tolist())

        sigma_gate = 0.01
        if all_sigmas:
            q = float(np.clip(float(self.cfg.epiplexity.sigma_gate_quantile), 0.0, 1.0))
            sigma_gate = float(np.quantile(np.asarray(all_sigmas, dtype=float), q))
            
        anchor_y = 0.75
        if all_implied_y:
            anchor_y = float(np.nanmedian(np.asarray(all_implied_y, dtype=float)))

        return {"PLANCK_SIGMA_GATE": sigma_gate, "ANCHOR_Y": anchor_y}

    def run_renormalization_scan(self) -> dict:
        return self.run_continuous_calibration(target_frames=None, sample_frac=1.0)

    def _generate_epistemic_report(self, df: pl.DataFrame, final_y: float) -> dict:
        model = self.model_payload.get("model") if self.model_payload else None
        scaler = self.model_payload.get("scaler") if self.model_payload else None
        feature_cols = self.model_payload.get("feature_cols", self.model_payload.get("features")) if self.model_payload else None
        
        base_metrics = evaluate_frames(df, self.cfg, model=model, scaler=scaler, feature_cols=feature_cols)
        
        return {
            "Topo_SNR": base_metrics.get("Topo_SNR", float("nan")),
            "Orthogonality": base_metrics.get("Orthogonality", float("nan")),
            "Phys_Alignment": base_metrics.get("Phys_Alignment", float("nan")),
            "Model_Alignment": base_metrics.get("Model_Alignment", float("nan")),
            "FINAL_Y": float(final_y),
        }

    def _export_config(self, target_frames, final_y, metrics, priors):
        conf = {
            "AUTO_LEARNED_PARAMS": {
                "TARGET_FRAMES_DAY": target_frames,
                "INITIAL_Y": final_y,
                "PLANCK_SIGMA_GATE": priors.get("PLANCK_SIGMA_GATE"),
                "ANCHOR_Y": priors.get("ANCHOR_Y")
            },
            "METRICS": metrics,
            "NOTE": "OMEGA v5.2 Auditor (Epistemic Metric Manifold)"
        }
        with (self.output_dir / "production_config.json").open("w") as f:
            json.dump(conf, f, indent=4)

    @staticmethod
    def _corr(x, y):
        if len(x) < 2: return 0.0
        return float(np.corrcoef(x, y)[0, 1])
