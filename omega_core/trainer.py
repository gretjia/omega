"""
trainer_v51.py

Level-2 (v5.2) machine learning trainer & evaluator. (The Epistemic Release)
Implements:
- P1 Fix: Epistemic interaction features
- Dual-Track Alignment Fix: Shifts DoD requirement to Model's Epistemic Alignment
"""

from __future__ import annotations

import math
import pickle
import time
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np
import polars as pl
import psutil
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

from config import L2PipelineConfig
from omega_core.kernel import apply_recursive_physics, run_l2_kernel
from omega_core.omega_math_core import topo_snr_from_traces
from tools.multi_dir_loader import discover_l2_dirs


def check_memory_safe(threshold: float = 85.0, sleep_sec: float = 10.0) -> None:
    while psutil.virtual_memory().percent > threshold:
        time.sleep(sleep_sec)

class OmegaTrainerV3:
    def __init__(self, cfg: L2PipelineConfig):
        self.cfg = cfg
        self.model = SGDClassifier(loss="log_loss", penalty="l2", alpha=1e-4, average=True)
        self.scaler = StandardScaler()

        topo_race_cols = list(getattr(self.cfg.train, "topology_race_features", ()))
        raw_feature_cols = [
            "sigma_eff", "net_ofi", "depth_eff", "epiplexity", "srl_resid", 
            "topo_area", "topo_energy", *topo_race_cols, "price_change", 
            "bar_duration_ms", "adaptive_y",
            "epi_x_srl_resid", "epi_x_topo_area", "epi_x_net_ofi",
        ]
        self.feature_cols = list(dict.fromkeys(raw_feature_cols))
        self.label_col = "direction_label"
        self.is_fitted = False
        self._warned_missing_cols = False

    @staticmethod
    def _signed_log1p(expr: pl.Expr) -> pl.Expr:
        return (expr.sign() * (expr.abs() + 1.0).log()).alias(expr.meta.output_name())

    @staticmethod
    def _winsorize(df: pl.DataFrame, col: str, q_low: float, q_high: float) -> pl.DataFrame:
        if col not in df.columns:
            return df
        lo = df.select(pl.col(col).quantile(q_low)).item()
        hi = df.select(pl.col(col).quantile(q_high)).item()
        if lo is None or hi is None:
            return df
        return df.with_columns(pl.col(col).clip(lower_bound=float(lo), upper_bound=float(hi)))

    def _prepare_frames(self, df: pl.DataFrame, cfg: L2PipelineConfig) -> pl.DataFrame:
        tcfg = cfg.train

        if ("trade_vol" not in df.columns) or ("cancel_vol" not in df.columns):
            if not self._warned_missing_cols:
                print("[Warning] trade_vol/cancel_vol missing. Spoofing filter may degrade.")
                self._warned_missing_cols = True

        df = apply_recursive_physics(df, cfg)

        df = df.with_columns(
            [
                (pl.col("epiplexity") * pl.col("srl_resid")).alias("epi_x_srl_resid"),
                (pl.col("epiplexity") * pl.col("topo_area")).alias("epi_x_topo_area"),
                (pl.col("epiplexity") * pl.col("net_ofi")).alias("epi_x_net_ofi"),
            ]
        )

        horizon = int(tcfg.label_horizon_buckets)
        label_sigma_mult = float(tcfg.label_sigma_mult)
        min_valid_close = float(getattr(tcfg, "min_valid_close", 0.0))

        def _over_symbol(expr: pl.Expr) -> pl.Expr:
            if "symbol" in df.columns:
                return expr.over("symbol")
            return expr

        df = (
            df.with_columns(
                [
                    _over_symbol(pl.col("close").shift(-horizon)).alias("close_fwd"),
                ]
            )
            .with_columns(
                [
                    (pl.col("close_fwd") - pl.col("close")).alias("fwd_change"),
                ]
            )
            .with_columns(
                pl.when((pl.col("close") > min_valid_close) & (pl.col("close_fwd") > min_valid_close))
                .then(pl.col("close"))
                .otherwise(None)
                .alias("close_valid")
            )
            .with_columns(
                [
                    (pl.col("fwd_change") / pl.col("close_valid")).alias("ret_k"),
                    (pl.col("sigma_eff") / pl.col("close_valid")).alias("sigma_ret"),
                ]
            )
            .with_columns(
                pl.when(pl.col("ret_k").abs() > label_sigma_mult * pl.col("sigma_ret"))
                .then(pl.col("ret_k").sign())
                .otherwise(0.0)
                .alias(self.label_col)
            )
            .drop_nulls()
        )

        if bool(getattr(tcfg, "use_structural_filter", False)) and df.height > 0:
            ofi_q = df.select(pl.col("net_ofi").abs().quantile(float(tcfg.ofi_abs_quantile))).item()
            energy_q = df.select(pl.col("topo_energy").quantile(float(tcfg.topo_energy_quantile))).item()
            df = df.filter(
                (pl.col("is_signal") == True)
                | (pl.col("net_ofi").abs() >= float(ofi_q or 0.0))
                | (pl.col("topo_energy") >= float(energy_q or 0.0))
            )

        for col in tcfg.winsor_features:
            df = self._winsorize(df, col, float(tcfg.winsor_q_low), float(tcfg.winsor_q_high))

        exprs = [self._signed_log1p(pl.col(c)) for c in tcfg.log1p_features if c in df.columns]
        if exprs:
            df = df.with_columns(exprs)

        if bool(tcfg.drop_neutral_labels):
            df = df.filter(pl.col(self.label_col) != 0.0)

        return df

    def train(self, sample_frac: float = 1.0, checkpoint_interval: int = 500000) -> None:
        print("Starting training OMEGA v5.2...")
        dirs = discover_l2_dirs()
        if not dirs:
            return

        classes = np.array([-1, 1]) if self.cfg.train.drop_neutral_labels else np.array([-1, 0, 1])
        total_rows = 0
        last_checkpoint_rows = 0

        for d in dirs:
            files = sorted(list(d.glob("*.parquet")))
            for f in files:
                try:
                    lf = pl.scan_parquet(str(f))
                    if sample_frac < 1.0:
                        lf = lf.sample(fraction=sample_frac, seed=42)
                    df_batch = lf.collect()
                    if df_batch.height == 0:
                        continue

                    df_batch = self._prepare_frames(df_batch, self.cfg)
                    if df_batch.height == 0:
                        continue

                    missing = [c for c in self.feature_cols if c not in df_batch.columns]
                    if missing:
                        continue

                    X = df_batch.select(self.feature_cols).to_numpy()
                    y = df_batch.select(self.label_col).to_numpy().ravel()

                    weights = None
                    if self.cfg.train.sample_weight_topo and "topo_area" in df_batch.columns:
                        topo = df_batch.select("topo_area").to_numpy().ravel()
                        weights = np.log1p(np.abs(topo))
                    else:
                        weights = df_batch["epiplexity"].to_numpy()

                    self.scaler.partial_fit(X)
                    X_scaled = self.scaler.transform(X)
                    self.model.partial_fit(X_scaled, y, classes=classes, sample_weight=weights)

                    total_rows += len(y)
                    if total_rows % 200000 == 0:
                        print(f"Rows: {total_rows}")
                    if total_rows - last_checkpoint_rows >= int(checkpoint_interval):
                        self.save(
                            name=f"checkpoint_rows_{total_rows}.pkl",
                            extra_state={"total_rows": int(total_rows)},
                        )
                        last_checkpoint_rows = total_rows
                except Exception as exc:
                    print(f"Error {f.name}: {exc}")

        if total_rows > last_checkpoint_rows:
            self.save(name=f"checkpoint_rows_{total_rows}.pkl", extra_state={"total_rows": int(total_rows)})
        self.save(name="omega_v5_model_final.pkl", extra_state={"total_rows": int(total_rows)})
        self.is_fitted = True
        print(f"Training complete. Total rows: {total_rows:,}")

    def save(self, out_dir: str = "./artifacts", name: str = "omega_v5_model.pkl", extra_state: Dict | None = None) -> None:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        path = Path(out_dir) / name
        payload = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_cols": self.feature_cols,
            "features": self.feature_cols,
            "cfg": self.cfg,
        }
        if extra_state:
            payload.update(extra_state)
        with open(path, "wb") as f:
            pickle.dump(payload, f)
        print(f"Model saved: {path}")


def _safe_corr(x: np.ndarray, y: np.ndarray, eps: float = 1e-12, min_samples: int = 30) -> float:
    if x.size < int(min_samples) or y.size < int(min_samples):
        return float("nan")
    mask = np.isfinite(x) & np.isfinite(y)
    if int(np.sum(mask)) < int(min_samples):
        return float("nan")
    xv = x[mask]
    yv = y[mask]
    if np.std(xv) <= eps or np.std(yv) <= eps:
        return 0.0
    return float(np.corrcoef(xv, yv)[0, 1])


def _vector_alignment(
    frames: pl.DataFrame, 
    horizon: int, 
    min_samples: int,
    model=None,
    scaler=None,
    feature_cols=None
) -> tuple[float, float]:
    if frames.height == 0 or "direction" not in frames.columns:
        return float("nan"), float("nan")

    def _over_symbol(expr: pl.Expr) -> pl.Expr:
        if "symbol" in frames.columns:
            return expr.over("symbol")
        return expr

    merged = frames.with_columns(
        (_over_symbol(pl.col("close").shift(-int(horizon))) - pl.col("close")).alias("fwd_return")
    )

    dir_sign = np.sign(np.asarray(merged["direction"].to_numpy(), dtype=float))
    fwd_sign = np.sign(np.asarray(merged["fwd_return"].to_numpy(), dtype=float))
    
    epi = np.asarray(merged["epiplexity"].to_numpy(), dtype=float)
    if epi.size == 0 or not np.any(np.isfinite(epi)):
        return float("nan"), float("nan")
        
    epi_q = float(np.nanquantile(epi, 0.8))
    mask = np.isfinite(dir_sign) & np.isfinite(fwd_sign) & (dir_sign != 0.0) & (fwd_sign != 0.0) & (epi >= epi_q)
    
    phys_align = float("nan")
    if int(np.sum(mask)) >= int(min_samples):
        phys_align = float(np.mean(dir_sign[mask] == fwd_sign[mask]))

    model_align = float("nan")
    if model is not None and scaler is not None and feature_cols is not None:
        if "epi_x_srl_resid" not in merged.columns:
            merged = merged.with_columns([
                (pl.col("epiplexity") * pl.col("srl_resid")).alias("epi_x_srl_resid"),
                (pl.col("epiplexity") * pl.col("topo_area")).alias("epi_x_topo_area"),
                (pl.col("epiplexity") * pl.col("net_ofi")).alias("epi_x_net_ofi"),
            ])
            
        missing = [c for c in feature_cols if c not in merged.columns]
        if not missing:
            X_all = merged.select(feature_cols).to_numpy()
            X_valid = X_all[mask]
            if X_valid.shape[0] >= min_samples:
                X_scaled = scaler.transform(X_valid)
                if hasattr(model, "predict_proba"):
                    probas = model.predict_proba(X_scaled)
                    c_idx = np.where(model.classes_ == 1)[0]
                    if len(c_idx) > 0:
                        preds = np.sign(probas[:, c_idx[0]] - 0.5)
                    else:
                        preds = np.sign(model.predict(X_scaled))
                else:
                    preds = np.sign(model.predict(X_scaled))
                    
                fwd_valid = fwd_sign[mask]
                valid_m = (preds != 0) & (fwd_valid != 0)
                if np.any(valid_m):
                    model_align = float(np.mean(preds[valid_m] == fwd_valid[valid_m]))

    return phys_align, model_align


def _collect_traces(frames: pl.DataFrame, max_traces: int | None) -> List[Sequence[float]]:
    if "trace" not in frames.columns: return []
    traces = frames["trace"].to_list()
    if max_traces is None: return traces
    return traces[: int(max_traces)]


def evaluate_frames(
    frames: pl.DataFrame, 
    cfg: L2PipelineConfig,
    model=None,
    scaler=None,
    feature_cols=None
) -> Dict[str, float]:
    vcfg = cfg.validation
    traces = _collect_traces(frames, vcfg.max_traces)
    topo_snr = topo_snr_from_traces(traces, cfg.topo_snr, cfg.epiplexity)

    orth = float("nan")
    if "epiplexity" in frames.columns and "srl_resid" in frames.columns:
        orth = _safe_corr(
            np.asarray(frames["epiplexity"].to_numpy(), dtype=float),
            np.abs(np.asarray(frames["srl_resid"].to_numpy(), dtype=float)),
            eps=float(vcfg.corr_eps),
            min_samples=int(vcfg.min_samples),
        )

    phys_align, model_align = _vector_alignment(
        frames, int(vcfg.forward_return_horizon_buckets), int(vcfg.min_samples),
        model=model, scaler=scaler, feature_cols=feature_cols
    )

    final_align = model_align if not math.isnan(model_align) else phys_align

    return {
        "n_frames": float(frames.height),
        "Topo_SNR": float(topo_snr),
        "Orthogonality": float(orth),
        "Phys_Alignment": float(phys_align),
        "Model_Alignment": float(model_align),
        "Vector_Alignment": float(final_align),
    }


def evaluate_dod(metrics: Dict[str, float], cfg: L2PipelineConfig) -> bool:
    val = cfg.validation
    
    align_metric = metrics.get("Model_Alignment", float("nan"))
    if not np.isfinite(align_metric):
        align_metric = metrics.get("Phys_Alignment", float("nan"))
        
    for m in ("Topo_SNR", "Orthogonality"):
        if not np.isfinite(metrics.get(m, float("nan"))):
            return False
            
    if not np.isfinite(align_metric): 
        return False
        
    return (
        metrics["Topo_SNR"] > float(val.topo_snr_min)
        and abs(metrics["Orthogonality"]) < float(val.orthogonality_max_abs)
        and align_metric > float(val.vector_alignment_min)
    )

def get_latest_model(out_dir: str = "./artifacts") -> dict | None:
    paths = list(Path(out_dir).glob("checkpoint_rows_*.pkl"))
    if not paths:
        final_p = Path(out_dir) / "omega_v5_model_final.pkl"
        if final_p.exists():
            with open(final_p, "rb") as f: return pickle.load(f)
        return None
    paths.sort(key=lambda p: int(p.stem.split('_')[-1]))
    try:
        with open(paths[-1], "rb") as f: return pickle.load(f)
    except:
        return None

def run_l2_audit(paths: Iterable[str], cfg: L2PipelineConfig, policy_path: str | Path | None = None) -> Dict[str, float]:
    all_frames = [run_l2_kernel(p, cfg)[0] for p in paths]
    if len(all_frames) == 0: return {"n_frames": 0.0}
    frames = pl.concat(all_frames, how="vertical")
    
    model, scaler, feature_cols = None, None, None
    if policy_path and Path(policy_path).exists():
        with open(policy_path, "rb") as f:
            payload = pickle.load(f)
            model = payload.get("model")
            scaler = payload.get("scaler")
            feature_cols = payload.get("feature_cols", payload.get("features"))
    else:
        payload = get_latest_model()
        if payload:
            model = payload.get("model")
            scaler = payload.get("scaler")
            feature_cols = payload.get("feature_cols", payload.get("features"))
            
    metrics = evaluate_frames(frames, cfg, model=model, scaler=scaler, feature_cols=feature_cols)
    metrics["DoD_pass"] = float(1.0 if evaluate_dod(metrics, cfg) else 0.0)
    return metrics


def write_audit_report(metrics: Dict[str, float], cfg: L2PipelineConfig, out_path: str | Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# OMEGA L2 Audit Report (v5.2)\n\n")
        f.write("## Metrics\n| Metric | Value | Threshold |\n| :--- | :--- | :--- |\n")
        f.write(f"| **Topo_SNR** | {metrics.get('Topo_SNR', float('nan')):.6f} | > {cfg.validation.topo_snr_min} |\n")
        f.write(f"| **Orthogonality** | {metrics.get('Orthogonality', float('nan')):.6f} | < {cfg.validation.orthogonality_max_abs} |\n")
        f.write(f"| **Phys_Alignment** (Baseline) | {metrics.get('Phys_Alignment', float('nan')):.6f} | (Informational, ~0.5) |\n")
        f.write(f"| **Model_Alignment** (Epistemic) | {metrics.get('Model_Alignment', float('nan')):.6f} | > {cfg.validation.vector_alignment_min} |\n")
        f.write(f"| **n_frames** | {metrics.get('n_frames', 0.0):.0f} | (report) |\n\n")
        f.write(f"**DoD_pass**: {bool(metrics.get('DoD_pass', 0.0))}\n")
