import numpy as np
import math

try:
    from numba import njit, prange
except ImportError:
    def njit(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    prange = range

# Use numpy's 1.20+ sliding window view to create 2D strides with 0 memory copies
from numpy.lib.stride_tricks import sliding_window_view 

@njit(parallel=True, fastmath=True, cache=True)
def calc_epiplexity_rolling(prices: np.ndarray, window: int) -> np.ndarray:
    """
    Computes Time-Bounded MDL Gain (R^2 of linear fit) using Numba array operations.
    Replaces the list-based intra-bucket trace logic.
    """
    n = len(prices)
    out = np.zeros(n, dtype=np.float64)
    if n < window:
        return out
        
    T = np.arange(window, dtype=np.float64)
    sum_t = np.sum(T)
    sum_t2 = np.sum(T**2)
    var_t = sum_t2 - (sum_t**2 / window)
    
    if var_t < 1e-12:
        return out

    for i in prange(window - 1, n):
        # The window slice
        y = prices[i - window + 1 : i + 1]
        
        sum_y = np.sum(y)
        sum_y2 = np.sum(y**2)
        sum_ty = np.sum(T * y)
        
        cov = sum_ty - (sum_t * sum_y / window)
        var_y = sum_y2 - (sum_y**2 / window)
        
        if var_y < 1e-12:
            out[i] = 0.0
            continue
            
        r2 = (cov**2) / (var_t * var_y)
        if r2 < 0.0: r2 = 0.0
        if r2 > 0.9999: r2 = 0.9999
        
        # Bits Saved MDL
        delta_k = 2.0
        mdl_gain = -(window / 2.0) * math.log(1.0 - r2) - (delta_k / 2.0) * math.log(window)
        
        if mdl_gain > 0.0:
            out[i] = mdl_gain
            
    return out

@njit(parallel=True, fastmath=True, cache=True)
def calc_holographic_topology_rolling(
    prices: np.ndarray, 
    ofis: np.ndarray, 
    window: int,
    price_scale_floor: float,
    ofi_scale_floor: float,
    green_coeff: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    Vectorized Holographic Topology Area and Energy using rolling 1D contiguous arrays.
    """
    n = len(prices)
    out_area = np.zeros(n, dtype=np.float64)
    out_energy = np.zeros(n, dtype=np.float64)
    
    if n < window:
        return out_area, out_energy

    for i in prange(window - 1, n):
        X = prices[i - window + 1 : i + 1]
        # We need cumulative OFI within the window window to form the 'Y' shape coordinate
        Y = np.zeros(window, dtype=np.float64)
        Y[0] = ofis[i - window + 1]
        for j in range(1, window):
            Y[j] = Y[j-1] + ofis[i - window + 1 + j]

        mx = np.sum(X) / window
        my = np.sum(Y) / window
        
        # Stdev
        vx = np.sum((X - mx)**2) / window
        vy = np.sum((Y - my)**2) / window
        sx = math.sqrt(vx)
        sy = math.sqrt(vy)
        
        if sx < price_scale_floor: sx = price_scale_floor
        if sy < ofi_scale_floor: sy = ofi_scale_floor
        
        # Normalize
        Xn = (X - mx) / sx
        Yn = (Y - my) / sy
        
        area_sum = 0.0
        energy_sum = 0.0
        for j in range(window - 1):
            # Area cross product: x[j]*y[j+1] - x[j+1]*y[j]
            area_sum += Xn[j] * Yn[j+1] - Xn[j+1] * Yn[j]
            # Energy path length
            dx = Xn[j+1] - Xn[j]
            dy = Yn[j+1] - Yn[j]
            energy_sum += math.sqrt(dx*dx + dy*dy)
            
        out_area[i] = area_sum * green_coeff
        out_energy[i] = energy_sum
        
    return out_area, out_energy

@njit(parallel=True, fastmath=True, cache=True)
def calc_topology_area_rolling(
    x_arr: np.ndarray, 
    y_arr: np.ndarray, 
    window: int,
    x_scale_floor: float, 
    y_scale_floor: float, 
    green_coeff: float
) -> np.ndarray:
    """
    Vectorized Green's Theorem Area for arbitrary Manifolds (X, Y) using rolling 1D contiguous arrays.
    """
    n = len(x_arr)
    out_area = np.zeros(n, dtype=np.float64)
    
    if n < window:
        return out_area

    for i in prange(window - 1, n):
        X = x_arr[i - window + 1 : i + 1]
        Y = y_arr[i - window + 1 : i + 1]
        
        mx = np.sum(X) / window
        my = np.sum(Y) / window
        
        vx = np.sum((X - mx)**2) / window
        vy = np.sum((Y - my)**2) / window
        sx = math.sqrt(vx)
        sy = math.sqrt(vy)
        
        if sx < x_scale_floor: sx = x_scale_floor
        if sy < y_scale_floor: sy = y_scale_floor
        
        Xn = (X - mx) / sx
        Yn = (Y - my) / sy
        
        area_sum = 0.0
        for j in range(window - 1):
            area_sum += Xn[j] * Yn[j+1] - Xn[j+1] * Yn[j]
            
        out_area[i] = area_sum * green_coeff
        
    return out_area
