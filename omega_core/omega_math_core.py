"""
omega_math_core.py

Level-2 (v5) deterministic math kernels (vectorized).
Physics: Sato & Kanazawa (2025) - Strict SRL Universality (delta=0.5)
Info: Finzi et al. (2026) - Epiplexity as Structural Compression Gain
"""

from __future__ import annotations

from typing import Iterable, List, Sequence

import math
import numpy as np

from config import L2EpiplexityConfig, L2SRLConfig, L2TopoSNRConfig, L2TopologyRaceConfig

_TOPO_DEFAULTS = L2TopologyRaceConfig()


def calc_epiplexity(trace: Sequence[float], cfg: L2EpiplexityConfig) -> float:
    """
    v5.0 Entry Point: Compression Gain.
    Replaces LZ76. Measures structural information S_T.
    """
    return calc_compression_gain(trace, cfg)


def calc_compression_gain(trace: Sequence[float], cfg: L2EpiplexityConfig) -> float:
    """
    v5.0 Epiplexity: Compression Gain (Finzi et al., 2026).
    
    Measures structural information (S_T) by comparing the error of a 
    Linear Predictor vs a Naive (Mean/Random Walk) Predictor.
    
    Gain = 1 - (Variance_Residual / Variance_Total)
    
    Gain > 0 implies extractable structure (Signal).
    Gain <= 0 implies pure entropy (Noise).
    """
    arr = np.asarray(trace, dtype=float)
    n = arr.size
    min_len = int(getattr(cfg, "min_trace_len", 10))
    
    if n < min_len:
        return float(cfg.fallback_value)
    
    # 1. Null Model (Entropy Baseline)
    # Null Hypothesis: Process is unstructured noise around a mean.
    # Error = Total Sum of Squares (Variance)
    var_total = np.var(arr)
    
    if var_total < 1e-12:
        # Zero energy = Zero structure (Dead/Flat)
        return 0.0

    # 2. Time-Bounded Model (Linear Predictor)
    # We fit y = mx + c analytically (O(N)).
    # This represents the simplest "Computational Observer".
    t = np.arange(n, dtype=float)
    t_mean = (n - 1) / 2.0
    x_mean = np.mean(arr)
    
    # Covariance / Variance_T
    numerator = np.sum((t - t_mean) * (arr - x_mean))
    denominator = np.sum((t - t_mean) ** 2)
    
    if denominator < 1e-9:
        slope = 0.0
    else:
        slope = numerator / denominator
        
    intercept = x_mean - slope * t_mean
    
    # 3. Compression Gain
    # Calculate residual variance after removing linear structure
    trend = slope * t + intercept
    residuals = arr - trend
    var_resid = np.mean(residuals ** 2)

    # Gain = 1 - (Unexplained_Entropy / Total_Entropy)
    # Equivalent to R-squared for the linear fit.
    ratio = var_resid / var_total
    R_squared = float(np.clip(1.0 - ratio, 0.0, 0.9999))
    
    # V62 Upgrade: Time-Bounded Minimum Description Length (MDL) Gain
    # delta_k = 2 for linear probe (slope, intercept)
    delta_k = 2.0
    
    # Turing Discipline: Require enough degrees of freedom
    if n < 3:
        return 0.0
        
    mdl_gain_bits = -(n / 2.0) * np.log(1.0 - R_squared) - (delta_k / 2.0) * np.log(n)
    
    # Turing Discipline: If the model costs more bits to describe than the raw data itself, it is pure noise.
    if mdl_gain_bits <= 0:
        return 0.0
        
    return float(mdl_gain_bits)


def calc_srl_state(
    price_change: float,
    sigma: float,
    net_ofi: float,
    depth: float,
    current_y: float,
    cfg: L2SRLConfig,
    cancel_vol: float = 0.0,
    trade_vol: float = 0.0,
) -> tuple[float, float, float, float]:
    """
    v5.0 Universal Physics Kernel (Sato 2025).
    
    Enforces Delta = 0.5 (Universal Constant).
    No Race. Physics is invariant.
    
    Returns:
    - srl_resid: The violation of the law (Force).
    - implied_y: The instantaneous Y required to explain the move.
    - effective_depth: Depth adjusted for spoofing.
    - spoof_ratio: Cancel/Trade ratio.
    """
    # 1. Safety Floors
    safe_depth = max(float(depth), float(cfg.depth_floor))
    safe_sigma = max(float(sigma), float(cfg.sigma_floor))

    # 2. Spoofing Penalty (Microstructure Correction)
    eps = float(getattr(cfg, "spoof_ratio_eps", 1e-9))
    safe_trade = max(float(trade_vol), eps)
    spoof_ratio = max(float(cancel_vol), 0.0) / safe_trade

    gamma = float(getattr(cfg, "spoof_penalty_gamma", 0.0))
    penalty = math.exp(-gamma * spoof_ratio)
    effective_depth = max(safe_depth * penalty, float(cfg.depth_floor))

    # 3. The Square Root Law (Delta = 0.5 Hardcoded)
    # Impact = Y * Sigma * sqrt(|OFI| / Depth)
    q_over_d = abs(float(net_ofi)) / effective_depth
    
    # Sato 2025: "delta is exactly 0.5"
    raw_impact_unit = safe_sigma * math.sqrt(q_over_d) 
    
    sign = float(np.sign(float(net_ofi)))
    
    # Theoretical Impact based on current structural rigidity (Y)
    theory_impact = sign * float(current_y) * raw_impact_unit
    
    # Residual: How much did Price violate Physics?
    srl_resid = float(price_change) - float(theory_impact)

    # 4. Implied Y (Inverse Problem)
    min_impact = float(getattr(cfg, "implied_y_min_impact", 0.0))
    min_penalty = float(getattr(cfg, "implied_y_min_penalty", 0.0))

    if raw_impact_unit > min_impact and penalty > min_penalty:
        # Y = |dP| / (Sigma * sqrt(Q/D))
        implied_y = abs(float(price_change)) / (raw_impact_unit + 1e-9)
    else:
        # Signal too weak to update Y, hold state.
        implied_y = float(current_y)

    return srl_resid, implied_y, effective_depth, float(spoof_ratio)


def calc_srl_race(*args, **kwargs):
    """
    DEPRECATED in v5.0.
    The 'Race' is cancelled. Physics won. Delta is 0.5.
    Redirects to single-lane calculation for backward compatibility.
    """
    resid, imp_y, eff_d, spoof = calc_srl_state(*args, **kwargs)
    # Return list format to satisfy legacy unpacking expected by v4 callers
    return [resid], imp_y, eff_d, spoof


def calc_topology_area(
    x_trace: Sequence[float],
    y_trace: Sequence[float],
    x_scale_floor: float,
    y_scale_floor: float,
    green_coeff: float,
) -> float:
    """
    Manifold Area (Green's Theorem proxy).
    """
    x = np.asarray(x_trace, dtype=float)
    y = np.asarray(y_trace, dtype=float)
    if x.size < 2 or y.size < 2:
        return 0.0

    n = min(x.size, y.size)
    x = x[:n]
    y = y[:n]

    x_std = max(float(np.std(x)), float(x_scale_floor))
    y_std = max(float(np.std(y)), float(y_scale_floor))
    x_norm = (x - float(np.mean(x))) / x_std
    y_norm = (y - float(np.mean(y))) / y_std

    cross_terms = x_norm[:-1] * y_norm[1:] - x_norm[1:] * y_norm[:-1]
    return float(green_coeff) * float(np.sum(cross_terms))


def calc_holographic_topology(
    trace: List[float],
    ofi_list: List[float],
    price_scale_floor: float | None = None,
    ofi_scale_floor: float | None = None,
    green_coeff: float | None = None,
) -> tuple[float, float]:
    """
    Holographic Topology: Signed Area and Energy.
    """
    if len(trace) < 2:
        return 0.0, 0.0

    p = np.array(trace)
    ofi_flow = np.array(ofi_list)
    q = np.cumsum(ofi_flow)

    x = p
    y = q
    n = min(len(x), len(y))
    x = x[:n]
    y = y[:n]

    if price_scale_floor is None:
        price_scale_floor = float(_TOPO_DEFAULTS.price_scale_floor)
    if ofi_scale_floor is None:
        ofi_scale_floor = float(_TOPO_DEFAULTS.ofi_scale_floor)
    if green_coeff is None:
        green_coeff = float(_TOPO_DEFAULTS.green_coeff)

    x_std = max(float(np.std(x)), float(price_scale_floor))
    y_std = max(float(np.std(y)), float(ofi_scale_floor))
    x = (x - float(np.mean(x))) / x_std
    y = (y - float(np.mean(y))) / y_std

    cross_terms = x[:-1] * y[1:] - x[1:] * y[:-1]
    signed_area = float(green_coeff) * float(np.sum(cross_terms))

    d_x = np.diff(x)
    d_y = np.diff(y)
    energy = float(np.sum(np.sqrt(d_x * d_x + d_y * d_y)))

    return signed_area, energy


def topo_snr_from_traces(traces: Iterable[Sequence[float]], cfg: L2TopoSNRConfig, epi_cfg: L2EpiplexityConfig) -> float:
    traces_list = list(traces)
    if len(traces_list) == 0:
        return float("nan")

    real_vals: List[float] = []
    for t in traces_list:
        real_vals.append(calc_epiplexity(t, epi_cfg))

    rng = np.random.default_rng(cfg.seed)
    shuffled_vals: List[float] = []
    n_shuffle = int(cfg.n_shuffle)
    for _ in range(n_shuffle):
        for t in traces_list:
            arr = np.asarray(t, dtype=float)
            if arr.size == 0:
                continue
            idx = rng.permutation(arr.size)
            shuffled_vals.append(calc_epiplexity(arr[idx], epi_cfg))

    if len(shuffled_vals) < int(cfg.min_shuffles):
        return float("nan")

    mu = float(np.mean(shuffled_vals))
    sd = float(np.std(shuffled_vals))
    sd = max(sd, float(cfg.std_floor))
    return float((np.mean(real_vals) - mu) / sd)