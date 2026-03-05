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

@njit(parallel=True, cache=True)
def calc_isoperimetric_topology_rolling(
    prices: np.ndarray,
    ofis: np.ndarray,
    window: int,
    price_scale_floor: float,
    ofi_scale_floor: float,
    green_coeff: float,
    dist_to_boundary: np.ndarray
):
    """
    V63 topology gate: Q_topo = 4*pi*|A_closed| / L_closed^2
    Note: green_coeff MUST be 0.5 at the call site for Shoelace/Green consistency.
    """
    n = len(prices)
    out_area = np.zeros(n, dtype=np.float64)
    out_energy = np.zeros(n, dtype=np.float64)  # Semantically stores L_closed
    out_q = np.zeros(n, dtype=np.float64)

    if n < window:
        return out_area, out_energy, out_q

    for i in prange(window - 1, n):
        if dist_to_boundary[i] < window - 1:
            continue

        X = prices[i - window + 1 : i + 1]

        # Local cumulative OFI inside the window, avoiding global drift contamination.
        Y = np.empty(window, dtype=np.float64)
        Y[0] = ofis[i - window + 1]
        for j in range(1, window):
            Y[j] = Y[j - 1] + ofis[i - window + 1 + j]

        mx = np.sum(X) / window
        my = np.sum(Y) / window

        sx = math.sqrt(np.sum((X - mx) ** 2) / window)
        sy = math.sqrt(np.sum((Y - my) ** 2) / window)

        if sx < price_scale_floor:
            sx = price_scale_floor
        if sy < ofi_scale_floor:
            sy = ofi_scale_floor

        Xn = (X - mx) / sx
        Yn = (Y - my) / sy

        area_sum = 0.0
        energy_sum = 0.0

        for j in range(window - 1):
            area_sum += Xn[j] * Yn[j + 1] - Xn[j + 1] * Yn[j]
            dx = Xn[j + 1] - Xn[j]
            dy = Yn[j + 1] - Yn[j]
            energy_sum += math.sqrt(dx * dx + dy * dy)

        # Close the polygon for area
        area_sum += Xn[window - 1] * Yn[0] - Xn[0] * Yn[window - 1]

        # Critical V63 fix: close the polygon for perimeter as well
        dx_close = Xn[0] - Xn[window - 1]
        dy_close = Yn[0] - Yn[window - 1]
        energy_sum += math.sqrt(dx_close * dx_close + dy_close * dy_close)

        area_val = area_sum * green_coeff
        out_area[i] = area_val
        out_energy[i] = energy_sum

        if energy_sum > 1e-12:
            q_val = (4.0 * math.pi * abs(area_val)) / (energy_sum * energy_sum)

            # Numerical guard
            if q_val > 1.0:
                q_val = 1.0
            elif q_val < 0.0:
                q_val = 0.0

            out_q[i] = q_val

    return out_area, out_energy, out_q


# [反脆弱底线] 普朗克常数守护物理奇点
PLANCK_CONSTANT = 1e-12

@njit(parallel=True, cache=True) # 严禁添加 fastmath=True! 捍卫 IEEE-754 极值
def calc_residual_epiplexity_rolling(
    srl_residuals: np.ndarray,
    window: int,
    dist_to_boundary: np.ndarray
) -> np.ndarray:
    n = len(srl_residuals)
    out = np.zeros(n, dtype=np.float64)

    if n < window:
        return out

    T = np.arange(window, dtype=np.float64)
    sum_t = np.sum(T)
    sum_t2 = np.sum(T * T)
    var_t = max(sum_t2 - (sum_t * sum_t / window), PLANCK_CONSTANT)

    for i in prange(window - 1, n):
        if dist_to_boundary[i] < window - 1:
            continue

        y = srl_residuals[i - window + 1 : i + 1]

        sum_y = np.sum(y)
        sum_y2 = np.sum(y * y)
        sum_ty = np.sum(T * y)

        cov = sum_ty - (sum_t * sum_y / window)
        var_y = sum_y2 - (sum_y * sum_y / window)

        # ==========================================
        # 🪐 奇点守护：Epiplexity 的终极觉醒
        # ==========================================
        if var_y < PLANCK_CONSTANT:
            # 绝对控盘：残差方差塌缩。
            # 【压缩即智能】：不可返回 0.0！赋予它极大的 MDL 增益（势能极值）！
            out[i] = 999.0 
            continue

        r2 = (cov * cov) / (var_t * var_y)
        
        # 拔掉 0.9999 的盖子！允许逼近1，仅保留微小底线防范 log(0)
        if r2 < 0.0: 
            r2 = 0.0
        elif r2 > 1.0 - PLANCK_CONSTANT: 
            r2 = 1.0 - PLANCK_CONSTANT

        delta_k = 3.0
        # 当 r2 逼近 1 时，mdl_gain 将呈对数爆炸，真正体现主力的智能碾压！
        mdl_gain = -(window / 2.0) * math.log(1.0 - r2) - (delta_k / 2.0) * math.log(window)

        if mdl_gain > 0.0:
            out[i] = mdl_gain

    return out
@njit(parallel=True, cache=True)
def calc_topology_area_rolling(
    x_arr: np.ndarray, 
    y_arr: np.ndarray, 
    window: int,
    x_scale_floor: float, 
    y_scale_floor: float, 
    green_coeff: float,
    dist_to_boundary: np.ndarray
) -> np.ndarray:
    """
    Vectorized Green's Theorem Area for arbitrary Manifolds (X, Y) using rolling 1D contiguous arrays.
    """
    n = len(x_arr)
    out_area = np.zeros(n, dtype=np.float64)
    
    if n < window:
        return out_area

    for i in prange(window - 1, n):
        if dist_to_boundary[i] < window - 1:
            continue

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
