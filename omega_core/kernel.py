"""
kernel.py

Level-2 (v5) deterministic kernel pipeline.
Implements:
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
from omega_core.omega_math_core import (
    calc_epiplexity,
    calc_holographic_topology,
    calc_srl_state,
    calc_topology_area,
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

    peace_threshold = float(getattr(sig, "peace_threshold", sig.epiplexity_min))
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

    epi_cfg = cfg.epiplexity
    sigma_gate_enabled = bool(getattr(epi_cfg, "sigma_gate_enabled", False))
    sigma_gate = float(getattr(epi_cfg, "sigma_gate", 0.0))

    current_y = float(srl.y_coeff) if initial_y is None else float(initial_y)
    rows = frames.to_dicts()
    results = []

    for row in rows:
        trace = row.get("trace") or []
        ofi_list = row.get("ofi_list") or []
        ofi_trace = row.get("ofi_trace") or []
        vol_list = row.get("vol_list") or []
        vol_trace = row.get("vol_trace") or []
        time_trace = row.get("time_trace") or []

        open_px = float(row.get("open") or 0.0)
        close_px = float(row.get("close") or 0.0)
        price_change = close_px - open_px

        sigma = float(row.get("sigma") or 0.0)
        if not math.isfinite(sigma): sigma = 0.0
        sigma_eff = max(sigma, float(srl.sigma_floor))

        depth = float(row.get("depth") or 0.0)
        if not math.isfinite(depth): depth = 0.0
        depth_eff = max(depth, float(srl.depth_floor))

        net_ofi = float(row.get("net_ofi") or 0.0)
        trade_vol = float(row.get("trade_vol") or 0.0)
        cancel_vol = float(row.get("cancel_vol") or 0.0)

        # 1. Energy Gate
        is_energy_active = (not sigma_gate_enabled) or (sigma_eff >= sigma_gate)
        
        if is_energy_active:
            # v5.0: Epiplexity is now Compression Gain [0, 1]
            epiplexity = calc_epiplexity(trace, epi_cfg)
        else:
            epiplexity = float(epi_cfg.fallback_value)

        if len(ofi_trace) == 0 and len(ofi_list) > 0:
            ofi_trace = np.cumsum(np.asarray(ofi_list, dtype=float)).tolist()
        if len(vol_trace) == 0 and len(vol_list) > 0:
            vol_trace = np.cumsum(np.asarray(vol_list, dtype=float)).tolist()
        if len(time_trace) == 0 and len(trace) > 0:
            time_trace = np.arange(len(trace), dtype=float).tolist()

        topo_cfg = cfg.topology_race
        trace_sources = {
            "trace": trace,
            "ofi_trace": ofi_trace,
            "vol_trace": vol_trace,
            "time_trace": time_trace,
        }

        def _trace_from_col(col_name: str) -> list[float]:
            seq = trace_sources.get(str(col_name), [])
            return list(seq) if isinstance(seq, (list, np.ndarray)) else []

        topo_features: dict[str, float] = {}
        for feature_name, x_col, y_col, x_scale_attr, y_scale_attr in getattr(
            topo_cfg,
            "manifolds",
            (),
        ):
            x_trace = _trace_from_col(x_col)
            y_trace = _trace_from_col(y_col)
            x_scale = float(getattr(topo_cfg, x_scale_attr, topo_cfg.price_scale_floor))
            y_scale = float(getattr(topo_cfg, y_scale_attr, topo_cfg.ofi_scale_floor))
            topo_features[str(feature_name)] = float(
                calc_topology_area(
                    x_trace,
                    y_trace,
                    x_scale_floor=x_scale,
                    y_scale_floor=y_scale,
                    green_coeff=float(topo_cfg.green_coeff),
                )
            )

        for default_feature in (
            topo_cfg.micro_feature,
            topo_cfg.classic_feature,
            topo_cfg.trend_feature,
        ):
            topo_features.setdefault(str(default_feature), 0.0)

        topo_area, topo_energy = calc_holographic_topology(
            trace,
            ofi_list,
            price_scale_floor=float(topo_cfg.price_scale_floor),
            ofi_scale_floor=float(topo_cfg.ofi_scale_floor),
            green_coeff=float(topo_cfg.green_coeff),
        )

        # 2. Universal SRL (Delta=0.5)
        srl_resid, implied_y, effective_depth, spoof_ratio = calc_srl_state(
            price_change=price_change,
            sigma=sigma_eff,
            net_ofi=net_ofi,
            depth=depth_eff,
            current_y=current_y,
            cfg=srl,
            cancel_vol=cancel_vol,
            trade_vol=trade_vol,
        )
        
        # Legacy map for trainer compatibility
        srl_lane_map = {
            "srl_resid_050": srl_resid,
        }

        # 3. Adaptive Y Update (The Damper)
        # Only update Y if structure (Epiplexity) is visible.
        if is_energy_active and epiplexity > peace_threshold and abs(net_ofi) > min_ofi_for_y:
            new_y = float(np.clip(implied_y, y_min, y_max))
            current_y = (1.0 - y_alpha) * current_y + y_alpha * new_y
            
        if anchor_w > 0.0:
            current_y = (1.0 - anchor_w) * current_y + anchor_w * anchor_y
        current_y = float(np.clip(current_y, clip_lo, clip_hi))

        topo_area_for_signal = float(topo_features.get(topo_cfg.micro_feature, topo_area))

        row.update(
            {
                "price_change": price_change,
                "sigma_eff": sigma_eff,
                "depth_eff": float(effective_depth),
                "epiplexity": epiplexity,
                "topo_area": topo_area_for_signal,
                "topo_energy": float(topo_energy),
                "srl_resid": srl_resid,
                "adaptive_y": float(current_y),
                "spoof_ratio": float(spoof_ratio),
                "is_energy_active": bool(is_energy_active),
                "sigma_gate": float(sigma_gate),
                **srl_lane_map,
                **topo_features,
            }
        )
        results.append(row)

    res_df = pl.DataFrame(results)

    # 4. Signal Gate
    res_df = res_df.with_columns(
        [
            (
                (pl.col("is_energy_active") == True)
                & (pl.col("epiplexity") > peace_threshold) 
                # v5.1 P0: symmetric triggering for both overbought/oversold excursions
                & (pl.col("srl_resid").abs() > float(sig.srl_resid_sigma_mult) * pl.col("sigma_eff"))
                & (pl.col("topo_area").abs() > float(sig.topo_area_min_abs))
                & (pl.col("topo_energy") > pl.col("sigma_eff") * topo_energy_sigma_mult)
                & (pl.col("spoof_ratio") < spoofing_ratio_max)
            ).alias("is_signal"),
            # v5.1 P0: damper restitution direction, opposite to SRL residual
            (-pl.col("srl_resid").sign()).alias("direction"),
        ]
    )
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
