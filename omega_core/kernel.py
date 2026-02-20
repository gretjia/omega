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
import numpy as np
import polars as pl

from config import L2PipelineConfig, load_l2_pipeline_config
from omega_core.omega_etl import build_l2_frames
from omega_core.omega_math_vectorized import (
    calc_epiplexity_vectorized,
    calc_topology_area_vectorized,
    calc_holographic_topology_vectorized,
    calc_srl_recursion_loop
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

    peace_threshold = float(getattr(sig, "peace_threshold", getattr(sig, "epiplexity_min", 0.5)))
    spoofing_ratio_max = float(getattr(sig, "spoofing_ratio_max", 2.5))
    min_ofi_for_y = float(getattr(sig, "min_ofi_for_y_update", 100.0))
    topo_energy_sigma_mult = float(getattr(sig, "topo_energy_sigma_mult", 10.0))

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
    
    open_px = frames.get_column("open").fill_null(0.0).to_numpy()
    close_px = frames.get_column("close").fill_null(0.0).to_numpy()
    price_change = close_px - open_px

    sigma_raw = frames.get_column("sigma").fill_nan(0.0).fill_null(0.0).to_numpy()
    sigma_eff = np.maximum(sigma_raw, float(srl.sigma_floor))
    
    depth_raw = frames.get_column("depth").fill_nan(0.0).fill_null(0.0).to_numpy()
    depth_eff = np.maximum(depth_raw, float(srl.depth_floor))
    
    net_ofi = frames.get_column("net_ofi").fill_null(0.0).to_numpy()
    trade_vol = frames.get_column("trade_vol").fill_null(0.0).to_numpy()
    cancel_vol = frames.get_column("cancel_vol").fill_null(0.0).to_numpy()

    def _safe_list_col(col_name: str) -> list:
        if col_name in frames.columns:
            return frames.get_column(col_name).to_list()
        return [None] * n_rows

    trace_col = _safe_list_col("trace")
    ofi_list_col = _safe_list_col("ofi_list")
    ofi_trace_col = _safe_list_col("ofi_trace")
    vol_list_col = _safe_list_col("vol_list")
    vol_trace_col = _safe_list_col("vol_trace")
    time_trace_col = _safe_list_col("time_trace")

    # --- Vectorized Pre-computation (Batch) ---
    out_is_active = (not sigma_gate_enabled) | (sigma_eff >= sigma_gate)
    
    # Calculate Epiplexity in ONE GO
    out_epi = calc_epiplexity_vectorized(trace_col, min_len=int(epi_cfg.min_trace_len), fallback=float(epi_cfg.fallback_value))
    # Apply gate mask (zero out inactive)
    out_epi = np.where(out_is_active, out_epi, float(epi_cfg.fallback_value))

    # Calculate Holographic Topology in ONE GO
    out_topo_area, out_topo_energy = calc_holographic_topology_vectorized(
        trace_col, ofi_list_col,
        price_scale_floor=float(topo_cfg.price_scale_floor),
        ofi_scale_floor=float(topo_cfg.ofi_scale_floor),
        green_coeff=float(topo_cfg.green_coeff)
    )

    manifolds = getattr(topo_cfg, "manifolds", ())
    out_manifolds = {}
    
    trace_sources = {
        "trace": trace_col,
        "ofi_trace": ofi_trace_col, # Note: Vectorized func expects list of lists
        "vol_trace": vol_trace_col,
        "time_trace": time_trace_col
    }
    
    # Fix: fill None with empty list for vectorized calls if needed, but pad_traces handles empty lists
    
    for feat in manifolds:
        feat_name, x_col, y_col, x_scale_attr, y_scale_attr = feat
        x_scale = float(getattr(topo_cfg, x_scale_attr, topo_cfg.price_scale_floor))
        y_scale = float(getattr(topo_cfg, y_scale_attr, topo_cfg.ofi_scale_floor))
        
        arr_x = trace_sources.get(x_col, [])
        arr_y = trace_sources.get(y_col, [])
        
        # If columns missing, fill zeros
        if not arr_x: arr_x = [[]] * n_rows
        if not arr_y: arr_y = [[]] * n_rows
            
        out_manifolds[str(feat_name)] = calc_topology_area_vectorized(
            arr_x, arr_y, x_scale, y_scale, float(topo_cfg.green_coeff)
        )

    # --- Sequential Recursion (Vectorized/JIT) ---
    initial_y_val = float(srl.y_coeff) if initial_y is None else float(initial_y)

    # Prioritize contiguous float64 for Numba speed
    pc_arr = np.ascontiguousarray(price_change, dtype=np.float64)
    sigma_arr = np.ascontiguousarray(sigma_eff, dtype=np.float64)
    ofi_arr = np.ascontiguousarray(net_ofi, dtype=np.float64)
    depth_arr = np.ascontiguousarray(depth_eff, dtype=np.float64)
    cancel_arr = np.ascontiguousarray(cancel_vol, dtype=np.float64)
    trade_arr = np.ascontiguousarray(trade_vol, dtype=np.float64)
    active_arr = np.ascontiguousarray(out_is_active, dtype=bool)
    epi_arr = np.ascontiguousarray(out_epi, dtype=np.float64)
    
    print(f"    Running Recursive Physics (JIT) on {n_rows} rows...", flush=True)
    
    out_srl_resid, out_y, out_spoof = calc_srl_recursion_loop(
        n_rows,
        pc_arr, sigma_arr, ofi_arr, depth_arr, cancel_arr, trade_arr,
        initial_y_val,
        # Params
        float(getattr(srl, "depth_floor", 1.0)), 
        float(getattr(srl, "sigma_floor", 0.01)), 
        float(getattr(srl, "spoof_ratio_eps", 1e-9)), 
        float(getattr(srl, "spoof_penalty_gamma", 0.5)),
        float(getattr(srl, "implied_y_min_impact", 1e-9)), 
        float(getattr(srl, "implied_y_min_penalty", 0.5)),
        float(getattr(srl, "y_min", 0.1)), 
        float(getattr(srl, "y_max", 5.0)), 
        float(getattr(srl, "y_ema_alpha", 0.05)), 
        float(getattr(srl, "anchor_y", srl.y_coeff)), 
        float(anchor_w),
        float(clip_lo), 
        float(clip_hi),
        active_arr, epi_arr, 
        float(peace_threshold), 
        float(min_ofi_for_y)
    )

    # --- Assembly ---
    # Overwrite topo_area with micro feature if present
    if str(topo_cfg.micro_feature) in out_manifolds:
        out_topo_area = out_manifolds[str(topo_cfg.micro_feature)]

    columns_to_add = [
        pl.Series("price_change", price_change),
        pl.Series("sigma_eff", sigma_eff),
        # depth_eff calculated below
    ]
    
    # Vectorized Depth Eff
    spoof_gamma = float(getattr(srl, "spoof_penalty_gamma", 0.0))
    depth_eff_arr = np.maximum(depth_eff * np.exp(-spoof_gamma * out_spoof), float(srl.depth_floor))
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
        pl.lit(float(sigma_gate)).alias("sigma_gate"),
    ])
    
    for m_name, m_arr in out_manifolds.items():
        if m_name != str(topo_cfg.micro_feature):
            columns_to_add.append(pl.Series(m_name, m_arr))
            
    res_df = frames.with_columns(columns_to_add)

    res_df = res_df.with_columns([
        (
            (pl.col("is_energy_active") == True)
            & (pl.col("epiplexity") > peace_threshold) 
            & (pl.col("srl_resid").abs() > float(sig.srl_resid_sigma_mult) * pl.col("sigma_eff"))
            & (pl.col("topo_area").abs() > float(sig.topo_area_min_abs))
            & (pl.col("topo_energy") > pl.col("sigma_eff") * topo_energy_sigma_mult)
            & (pl.col("spoof_ratio") < spoofing_ratio_max)
        ).alias("is_signal"),
        (-pl.col("srl_resid").sign()).alias("direction"),
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
    frames = build_l2_frames(path, cfg, target_frames=target_frames)
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
