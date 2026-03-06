"""
kernel.py (OMEGA v5.2)

Level-2 (v5.2) deterministic kernel pipeline. (The Epistemic Release)
Implements:
- Algebraic Dimensionality Reduction (Zero-Memory-Explosion IIR Operator)
- Universal SRL (Fixed Delta=0.5)
- Epiplexity (Compression Gain)
- Holographic Damper (Adaptive Y)
"""

from __future__ import annotations

import math
import os
import numpy as np
import polars as pl

from config import L2PipelineConfig, load_l2_pipeline_config
from omega_core.omega_etl import build_l2_features_from_l1, scan_l2_quotes
from omega_core.omega_math_core import (
    calc_srl_state,
)

def _apply_recursive_physics(
    frames: pl.DataFrame,
    cfg: L2PipelineConfig,
    initial_y: float | None = None,
) -> pl.DataFrame:
    if frames.height == 0:
        return frames

    srl = cfg.srl
    sig = cfg.signal
    epi_cfg = cfg.epiplexity
    topo_cfg = cfg.topology_race

    signal_epi_threshold = float(getattr(sig, "signal_epi_threshold", 0.5))
    brownian_q_threshold = float(getattr(srl, "brownian_q_threshold", 0.5))
    topo_energy_min = float(getattr(sig, "topo_energy_min", 2.0))
    spoofing_ratio_max = float(getattr(sig, "spoofing_ratio_max", 2.5))
    min_ofi_for_y = float(getattr(sig, "min_ofi_for_y_update", 100.0))

    y_min = float(getattr(srl, "y_min", 0.1))
    y_max = float(getattr(srl, "y_max", 5.0))
    y_alpha = float(getattr(srl, "y_ema_alpha", 0.05))
    anchor_y = float(getattr(srl, "anchor_y", srl.y_coeff))
    anchor_w = float(np.clip(float(getattr(srl, "anchor_weight", 0.0)), 0.0, 1.0))
    
    clip_lo = min(float(getattr(srl, "anchor_clip_min", y_min)), float(getattr(srl, "anchor_clip_max", y_max)))
    clip_hi = max(float(getattr(srl, "anchor_clip_min", y_min)), float(getattr(srl, "anchor_clip_max", y_max)))

    sigma_gate_enabled = bool(getattr(epi_cfg, "sigma_gate_enabled", False))
    sigma_gate = float(getattr(epi_cfg, "sigma_gate", 0.0))

    # =========================================================================
    # v5.2 Fix: O(1) Memory Array Projection (Avoids to_dicts MemoryError)
    # =========================================================================
    n_rows = frames.height

    def _to_f64(v: object, default: float = 0.0) -> float:
        if v is None:
            return float(default)
        if isinstance(v, (int, float, np.integer, np.floating)):
            out = float(v)
            return out if np.isfinite(out) else float(default)
        s = str(v).strip().replace(",", "")
        if not s:
            return float(default)
        if s.lower() in {"nan", "none", "null", "na", "nat", "inf", "+inf", "-inf"}:
            return float(default)
        try:
            out = float(s)
            return out if np.isfinite(out) else float(default)
        except Exception:
            return float(default)

    def _safe_f64_col(col_name: str, default: float = 0.0) -> np.ndarray:
        if col_name not in frames.columns:
            return np.full(n_rows, float(default), dtype=np.float64)
        arr = frames.get_column(col_name).cast(pl.Float64, strict=False).fill_null(default).fill_nan(default).to_numpy()
        # Ring-0 Physics Shield: Cleanse all infinities that Polars ignores
        return np.nan_to_num(arr, nan=default, posinf=default, neginf=default)

    def _to_bool(v: object) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return False
        if isinstance(v, (int, np.integer)):
            return int(v) != 0
        s = str(v).strip().lower()
        return s in {"1", "true", "t", "yes", "y"}

    def _safe_bool_col(col_name: str) -> np.ndarray:
        if col_name not in frames.columns:
            return np.zeros(n_rows, dtype=bool)
        return frames.get_column(col_name).cast(pl.Boolean, strict=False).fill_null(False).to_numpy()

    open_px = _safe_f64_col("open", default=0.0)
    close_px = _safe_f64_col("close", default=0.0)
    price_change = close_px - open_px

    sigma_raw = _safe_f64_col("sigma", default=0.0)
    sigma_eff = np.maximum(sigma_raw, float(srl.sigma_floor))

    depth_raw = _safe_f64_col("depth", default=0.0)
    depth_eff = np.maximum(depth_raw, float(srl.depth_floor))

    net_ofi = _safe_f64_col("net_ofi", default=0.0)
    trade_vol = _safe_f64_col("trade_vol", default=0.0)
    cancel_vol = _safe_f64_col("cancel_vol", default=0.0)

    # Codex Correction: List-columns are OOM vectors and cannot cross the Python GIL.
    # We strictly use 1-D contiguous primitive arrays (e.g. close_px) and Numba sliding windows.
    # Removed _safe_list_col entirely.

    # --- Vectorized Pre-computation (Batch) ---
    out_is_active = (not sigma_gate_enabled) | (sigma_eff >= sigma_gate)
    
    # v6.0: A-Share Singularity Mask
    if "has_singularity" in frames.columns:
        has_singularity = _safe_bool_col("has_singularity")
        # Disable physics active state during singularity
        out_is_active = out_is_active & (~has_singularity)
    else:
        has_singularity = np.zeros(n_rows, dtype=bool)
    
    # --- Vectorized Fast Boundary Detect ---
    # Overnight Phase Transition — yesterday's resistance state must NOT contaminate today's opening auction
    is_boundary = np.zeros(n_rows, dtype=bool)
    if n_rows > 1 and "symbol" in frames.columns and "date" in frames.columns:
        syms_srs = frames.get_column("symbol")
        dates_srs = frames.get_column("date")
        boundary_srs = (syms_srs != syms_srs.shift(1)) | (dates_srs != dates_srs.shift(1))
        is_boundary = boundary_srs.fill_null(False).to_numpy()

    # ULTRATHINK: O(N) precompute distance to last boundary for O(1) rolling window checks
    dist_to_boundary = np.zeros(n_rows, dtype=np.int32)
    curr_dist = 999999
    for i in range(n_rows):
        if is_boundary[i]:
            curr_dist = 0
        else:
            curr_dist += 1
        dist_to_boundary[i] = curr_dist

    window_len = int(epi_cfg.min_trace_len)

    # 1) Topology first
    from omega_core.omega_math_rolling import calc_isoperimetric_topology_rolling
    out_topo_area, out_topo_energy, out_q_topo = calc_isoperimetric_topology_rolling(
        prices=close_px,
        ofis=net_ofi,
        window=window_len,
        price_scale_floor=float(topo_cfg.price_scale_floor),
        ofi_scale_floor=float(topo_cfg.ofi_scale_floor),
        green_coeff=0.5,  # Must be 0.5 for shoelace/Green consistency
        dist_to_boundary=dist_to_boundary,
    )

    # 2) Ensure Y cannot update before topology becomes valid (Warm-up Mask)
    srl_is_active = out_is_active.copy()
    srl_is_active[dist_to_boundary < window_len - 1] = False

    base_y = float(srl.y_coeff) if initial_y is None else float(initial_y)

    if os.environ.get("OMEGA_KERNEL_VERBOSE") == "1":
        print(f"    Running Recursive Physics on {n_rows} rows...", flush=True)

    # 3) SRL recursion second
    from omega_core.omega_math_vectorized import calc_srl_recursion_loop_v63
    out_srl_resid, out_y, out_spoof = calc_srl_recursion_loop_v63(
        n_rows=n_rows,
        price_change=price_change,
        sigma_eff=sigma_eff,
        net_ofi=net_ofi,
        depth_eff=depth_eff,
        cancel_vol=cancel_vol,
        trade_vol=trade_vol,
        base_y=base_y,
        is_boundary=is_boundary,
        depth_floor=float(srl.depth_floor),
        sigma_floor=float(srl.sigma_floor),
        spoof_ratio_eps=float(srl.spoof_ratio_eps),
        spoof_penalty_gamma=float(srl.spoof_penalty_gamma),
        implied_y_min_impact=float(srl.implied_y_min_impact),
        implied_y_min_penalty=float(srl.implied_y_min_penalty),
        y_min=y_min,
        y_max=y_max,
        y_alpha=y_alpha,
        anchor_y=anchor_y,
        anchor_w=anchor_w,
        clip_lo=clip_lo,
        clip_hi=clip_hi,
        out_is_active=srl_is_active,
        out_q_topo=out_q_topo,
        chaos_threshold=brownian_q_threshold, 
        min_ofi_for_y=min_ofi_for_y,
    )

    # V64.2 closure: singularity labels may gate activity, but must never rewrite
    # the residual that feeds the compression score.

    # 4) True Compression Gain third
    from omega_core.omega_math_rolling import calc_srl_compression_gain_rolling
    out_epi_raw = calc_srl_compression_gain_rolling(
        price_change=price_change,             # [闭环] 传入原始价格基准
        srl_residuals=out_srl_resid,
        window=window_len,
        dist_to_boundary=dist_to_boundary,
    )
    
    # Apply the activity mask without reintroducing any secondary threshold semantics.
    out_epi = np.where(out_is_active, out_epi_raw, float(epi_cfg.fallback_value))

    from omega_core.omega_math_rolling import calc_topology_area_rolling
    manifolds = getattr(topo_cfg, "manifolds", ())
    out_manifolds = {}
    
    # We use sequential indices for time_trace proxy since buckets are ordered
    time_trace_proxy = np.arange(n_rows, dtype=np.float64)
    
    trace_sources = {
        "trace": close_px,
        "ofi_trace": net_ofi,
        "vol_trace": trade_vol,
        "time_trace": time_trace_proxy
    }
    
    for feat in manifolds:
        feat_name, x_col, y_col, x_scale_attr, y_scale_attr = feat
        x_scale = float(getattr(topo_cfg, x_scale_attr, topo_cfg.price_scale_floor))
        y_scale = float(getattr(topo_cfg, y_scale_attr, topo_cfg.ofi_scale_floor))
        
        arr_x = trace_sources.get(x_col, np.zeros(n_rows, dtype=np.float64))
        arr_y = trace_sources.get(y_col, np.zeros(n_rows, dtype=np.float64))
            
        out_manifolds[str(feat_name)] = calc_topology_area_rolling(
            arr_x, arr_y, window=window_len,
            x_scale_floor=x_scale, y_scale_floor=y_scale, green_coeff=0.5,
            dist_to_boundary=dist_to_boundary
        )

    # --- Assembly ---
    # Removed topo_area micro feature overwrite (V64.1 Absolute Closure)

    columns_to_add = [
        pl.Series("price_change", price_change),
        pl.Series("sigma_eff", sigma_eff),
        # depth_eff calculated below
    ]
    
    # Vectorized Depth Eff
    spoof_gamma = float(getattr(srl, "spoof_penalty_gamma", 0.0))
    depth_eff_arr = depth_eff * np.exp(-spoof_gamma * out_spoof)
    columns_to_add.append(pl.Series("depth_eff", depth_eff_arr))

    columns_to_add.extend([
        pl.Series("epiplexity", out_epi),
        pl.Series("topo_area", out_topo_area),
        pl.Series("topo_energy", out_topo_energy),
        pl.Series("srl_resid", out_srl_resid),
        pl.Series("srl_resid_050", out_srl_resid),
        pl.Series("adaptive_y", out_y),
        pl.Series("spoof_ratio", out_spoof),
        pl.Series("is_energy_active", out_is_active),
        pl.Series("is_physics_valid", ~has_singularity),
        pl.lit(float(sigma_gate)).alias("sigma_gate"),
    ])
    
    # Emit all manifold features (including micro). `topo_area` is the canonical
    # alias (kept for backward compatibility), but training expects explicit
    # `topo_micro/topo_classic/topo_trend` columns as configured in `config.py`.
    for m_name, m_arr in out_manifolds.items():
        columns_to_add.append(pl.Series(m_name, m_arr))
            
    res_df = frames.with_columns(columns_to_add)

    res_df = res_df.with_columns([
        (
            (pl.col("is_energy_active") == True)
            & (pl.col("epiplexity") > signal_epi_threshold) 
            & (pl.col("srl_resid").abs() > float(sig.srl_resid_sigma_mult) * pl.col("sigma_eff"))
            & (pl.col("topo_area").abs() > float(sig.topo_area_min_abs))
            & (pl.col("topo_energy") > topo_energy_min)
            & (pl.col("spoof_ratio") < spoofing_ratio_max)
        ).alias("is_signal"),
        (pl.col("srl_resid").sign()).alias("direction"),
    ])

    # === V64.3 BOURBAKI COMPLETION: 单一压缩语义收敛 ===
    # 系统只保留唯一正统的 canonical epiplexity，并将 dominant_probe 降级为兼容占位符。
    
    if "symbol" in res_df.columns:
        group_expr = pl.col("symbol")
        
        # 1. Canonical prequential compression gain
        canonical_epi = pl.col("epiplexity").forward_fill().over(group_expr)

        # 2. Bits Topology (高维拓扑：被折叠的空间)
        compactness = (4.0 * math.pi * pl.col("topo_area").abs()) / (pl.col("topo_energy")**2 + 1e-12)
        bits_topo = (compactness * math.log(window_len)).forward_fill().over(group_expr).clip(lower_bound=0.0)

        # 3. SRL Phase (主力算法单的微观破缺方向)
        srl_phase = pl.col("srl_resid").sign() * pl.col("srl_resid").abs().sqrt()

        main_force_singularity = (
            canonical_epi.fill_null(0.0) + 
            bits_topo.fill_null(0.0)
        ) * srl_phase
        
        res_df = res_df.with_columns([
            canonical_epi.alias("bits_linear"),
            bits_topo.alias("bits_topology"),
            srl_phase.alias("srl_phase"),
            main_force_singularity.alias("singularity_vector"),
            pl.lit(1).alias("dominant_probe"),
        ])
        
    return res_df

def apply_recursive_physics(
    frames: pl.DataFrame,
    cfg: L2PipelineConfig,
    initial_y: float | None = None,
) -> pl.DataFrame:
    return _apply_recursive_physics(frames, cfg, initial_y=initial_y)

def run_l2_kernel(
    path: str,
    cfg: L2PipelineConfig,
    initial_y: float | None = None,
    target_frames: float | None = None,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    lf = scan_l2_quotes(path, cfg)
    if lf is None:
        frames = pl.DataFrame()
    else:
        frames = build_l2_features_from_l1(lf, cfg, target_frames=target_frames)
    frames = _apply_recursive_physics(frames, cfg, initial_y=initial_y)
    signals = frames.filter(pl.col("is_signal") == True)
    return frames, signals

class OmegaKernel:
    def __init__(self, file_path: str, cfg: L2PipelineConfig | None = None):
        self.file_path = file_path
        self.cfg = cfg or load_l2_pipeline_config()

    def run(
        self,
        initial_y: float | None = None,
        target_frames: float | None = None,
        debug_mode: bool = False,
    ) -> pl.DataFrame:
        frames, _ = run_l2_kernel(
            self.file_path,
            self.cfg,
            initial_y=initial_y,
            target_frames=target_frames,
        )
        if debug_mode:
            return frames
        return frames
