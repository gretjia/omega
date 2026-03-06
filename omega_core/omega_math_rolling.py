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

@njit(parallel=True, cache=True)
def calc_srl_compression_gain_rolling(
    price_change: np.ndarray,     # [V64 绝对闭合] 引入原始价格波动 (Null Model)
    srl_residuals: np.ndarray,    # [V64 绝对闭合] SRL 残差 (Alternative Model)
    window: int,
    dist_to_boundary: np.ndarray,
    delta_k: float = 2.0          # [次级问题修复] 统一参数，与标量版本 \Delta k = 2.0 绝对对齐
) -> np.ndarray:
    """
    第一性原理闭合: 计算 SRL 相对均值模型的信息论压缩增益 (MDL Gain)。
    当 SRL 完美解释价格波动时，残差方差 -> 0，信息增益自然发散至正无穷大。
    """
    n = len(srl_residuals)
    out = np.zeros(n, dtype=np.float64)

    if n < window:
        return out

    for i in prange(window - 1, n):
        if dist_to_boundary[i] < window - 1:
            continue

        dp = price_change[i - window + 1 : i + 1]
        r = srl_residuals[i - window + 1 : i + 1]

        # 零假设方差: 原始价格的波动能量
        mean_dp = np.sum(dp) / window
        var_dp = (np.sum(dp * dp) / window) - (mean_dp * mean_dp)

        # 备择假设方差: SRL 吸收冲击后的残差能量
        mean_r = np.sum(r) / window
        var_r = (np.sum(r * r) / window) - (mean_r * mean_r)

        # 【第一性原理底线】：Zero-variance -> zero signal
        # 如果价格原本就是死水，没有任何可压缩的智能
        if var_dp < PLANCK_CONSTANT:
            out[i] = 0.0
            continue

        safe_var_r = max(var_r, PLANCK_CONSTANT)
        ratio = var_dp / safe_var_r
        
        # 只有模型提供了正向压缩(ratio > 1)，才计算对数增益
        if ratio > 1.0:
            mdl_gain = (window / 2.0) * math.log(ratio) - (delta_k / 2.0) * math.log(window)
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
