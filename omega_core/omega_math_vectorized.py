"""
omega_math_vectorized.py

Vectorized implementations of OMEGA math kernels to avoid Python loops.
Optimized for batch processing of variable-length traces using NaN padding.
"""

import numpy as np
from typing import List, Sequence

def pad_traces(traces: List[Sequence[float]], max_len: int = None) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert list of variable-length traces to (N, L) array with NaN padding.
    Returns:
        padded_array: (N, L) float array
        lengths: (N,) int array
    """
    n = len(traces)
    if n == 0:
        return np.zeros((0, 0)), np.zeros(0)
        
    lens = np.array([len(t) for t in traces])
    L = max_len if max_len is not None else (lens.max() if n > 0 else 0)
    
    arr = np.full((n, L), np.nan, dtype=np.float64)
    for i, t in enumerate(traces):
        if len(t) > 0:
            arr[i, :len(t)] = t
            
    return arr, lens

def calc_epiplexity_vectorized(traces: List[Sequence[float]], min_len: int = 10, fallback: float = 0.0) -> np.ndarray:
    """
    Vectorized Compression Gain (Epiplexity).
    G = 1 - Var(Resid) / Var(Total) = R^2 of Linear Fit.
    
    Computes R^2 for N traces simultaneously.
    """
    n = len(traces)
    if n == 0: return np.array([])
    
    # 1. Pad
    # Optimization: Chunking could be used if N is huge, but for 1 day (100k rows) it fits in RAM.
    X, lengths = pad_traces(traces)
    L = X.shape[1]
    
    # 2. Time Index T (0, 1, 2...)
    # T is (1, L), broadcasted to (N, L)
    T = np.arange(L, dtype=np.float64)
    
    # Mask for valid values
    mask = ~np.isnan(X)
    
    # Counts (N,)
    cnt = lengths.astype(np.float64)
    
    # Filter short traces
    valid_mask = (lengths >= min_len)
    
    # We only compute for valid rows to save time/warnings, but masking logic handles it.
    # To avoid div by zero, we set invalid counts to infinity or handle at end.
    safe_cnt = np.where(valid_mask, cnt, np.inf)
    
    # --- Statistics ---
    
    # Sums
    Sx = np.nansum(X, axis=1)
    St = np.sum(np.where(mask, T, 0), axis=1) # Sum of indices present
    
    # Means
    Mx = Sx / safe_cnt
    Mt = St / safe_cnt
    
    # Centered T and X (Implicitly)
    # Cov(X, T) = E[X*T] - E[X]E[T]
    # Var(X) = E[X^2] - E[X]^2
    
    Sxx = np.nansum(X**2, axis=1)
    Stt = np.sum(np.where(mask, T**2, 0), axis=1)
    Sxt = np.nansum(X * T, axis=1)
    
    # Numerators for Covariance/Variance
    # Cov * N = Sxt - Sx * Mt (approx, careful with sums)
    # Using Sum of Squares formula: Sum((x-mx)(t-mt)) = Sum(xt) - Sum(x)Sum(t)/n
    
    num_cov = Sxt - (Sx * St / safe_cnt)
    num_var_x = Sxx - (Sx**2 / safe_cnt)
    num_var_t = Stt - (St**2 / safe_cnt)
    
    # R^2 = Cov(X,T)^2 / (Var(X) * Var(T))
    #     = num_cov^2 / (num_var_x * num_var_t)
    
    # Denominator
    denom = num_var_x * num_var_t
    
    # Avoid div by zero or almost zero
    # Var(T) is 0 if len < 2. Var(X) is 0 if constant.
    with np.errstate(divide='ignore', invalid='ignore'):
        r2 = (num_cov**2) / denom
        
    # Result
    out = np.full(n, fallback, dtype=np.float64)
    
    # Valid where length ok AND denominator > eps
    is_computable = valid_mask & (denom > 1e-12)
    
    out[is_computable] = r2[is_computable]
    
    # Clip [0, 1] (R^2 definition)
    out = np.clip(out, 0.0, 1.0)
    
    return out

def calc_topology_area_vectorized(
    x_traces: List[Sequence[float]], 
    y_traces: List[Sequence[float]], 
    x_scale: float, 
    y_scale: float, 
    green_coeff: float
) -> np.ndarray:
    """
    Vectorized Green's Theorem Area.
    Area = sum(x[i]*y[i+1] - x[i+1]*y[i])
    """
    n = len(x_traces)
    if n == 0: return np.array([])
    
    # Pad both
    # Note: x and y must be same length per row
    X, lx = pad_traces(x_traces)
    Y, ly = pad_traces(y_traces)
    
    # Lengths should match, take min
    lens = np.minimum(lx, ly)
    L = X.shape[1]
    
    # Normalize (Vectorized)
    # Mean and Std per row
    # Keep dims for broadcasting: (N, 1)
    
    # Mask
    mask = ~np.isnan(X) & ~np.isnan(Y)
    cnt = np.sum(mask, axis=1)
    safe_cnt = np.where(cnt > 1, cnt, np.inf)
    
    mx = np.nansum(X, axis=1) / safe_cnt
    my = np.nansum(Y, axis=1) / safe_cnt
    
    sx = np.nanstd(X, axis=1)
    sy = np.nanstd(Y, axis=1)
    
    # Apply floors
    sx = np.maximum(sx, x_scale)
    sy = np.maximum(sy, y_scale)
    
    # Normalize: (X - mx) / sx
    Xn = (X - mx[:, None]) / sx[:, None]
    Yn = (Y - my[:, None]) / sy[:, None]
    
    # Cross terms: x[i] * y[i+1] - x[i+1] * y[i]
    # Slice views
    x_i = Xn[:, :-1]
    x_ip1 = Xn[:, 1:]
    y_i = Yn[:, :-1]
    y_ip1 = Yn[:, 1:]
    
    cross = x_i * y_ip1 - x_ip1 * y_i
    
    # Sum (Green's Area)
    # Handle NaNs: if any component is NaN, cross is NaN. nansum treats as 0.
    # We must ensure we don't sum garbage padding.
    # Padding is NaN. NaNs propagate.
    # nansum is correct IF valid data is contiguous.
    
    area = np.nansum(cross, axis=1) * green_coeff
    
    # Where count < 2, area = 0
    area[cnt < 2] = 0.0
    
    return area

def calc_holographic_topology_vectorized(
    trace: List[Sequence[float]],
    ofi_list: List[Sequence[float]],
    price_scale_floor: float,
    ofi_scale_floor: float,
    green_coeff: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Vectorized Holographic Topology (Area + Energy).
    x = trace (Price)
    y = cumsum(ofi_list) (Flow)
    """
    n = len(trace)
    if n == 0: return np.zeros(0), np.zeros(0)
    
    # 1. Prepare Y (Cumulative Flow)
    # Since ofi_list is variable length, we must pad then cumsum.
    # But cumsum on NaNs is tricky.
    # Better: pad, replace NaN with 0, cumsum, then mask back.
    # Wait, ofi_list is list of lists.
    
    Y_raw, ly = pad_traces(ofi_list)
    # Mask NaNs
    mask_y = ~np.isnan(Y_raw)
    Y_filled = np.nan_to_num(Y_raw, nan=0.0)
    Y_cum = np.cumsum(Y_filled, axis=1)
    # Restore NaNs (optional, but normalization handles it)
    Y = np.where(mask_y, Y_cum, np.nan)
    
    X, lx = pad_traces(trace)
    
    # Lengths should match
    mask = ~np.isnan(X) & ~np.isnan(Y)
    cnt = np.sum(mask, axis=1)
    safe_cnt = np.where(cnt > 1, cnt, np.inf)
    
    # Normalize
    mx = np.nansum(X, axis=1) / safe_cnt
    my = np.nansum(Y, axis=1) / safe_cnt
    sx = np.maximum(np.nanstd(X, axis=1), price_scale_floor)
    sy = np.maximum(np.nanstd(Y, axis=1), ofi_scale_floor)
    
    Xn = (X - mx[:, None]) / sx[:, None]
    Yn = (Y - my[:, None]) / sy[:, None]
    
    # Area (Cross Product)
    x_i, x_ip1 = Xn[:, :-1], Xn[:, 1:]
    y_i, y_ip1 = Yn[:, :-1], Yn[:, 1:]
    cross = x_i * y_ip1 - x_ip1 * y_i
    area = np.nansum(cross, axis=1) * green_coeff
    area[cnt < 2] = 0.0
    
    # Energy (Path Length)
    dx = np.diff(Xn, axis=1)
    dy = np.diff(Yn, axis=1)
    # ds = sqrt(dx^2 + dy^2)
    ds = np.sqrt(dx**2 + dy**2)
    energy = np.nansum(ds, axis=1)
    energy[cnt < 2] = 0.0
    
    return area, energy
