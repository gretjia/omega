import math

import numpy as np

try:
    from numba import njit
except ImportError:
    def njit(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


# [反脆弱底线] 普朗克常数守护物理奇点
PLANCK_CONSTANT = 1e-12


@njit(cache=True, nogil=True, fastmath=False)
def calc_isoperimetric_topology_rolling(
    prices: np.ndarray,
    ofis: np.ndarray,
    window: int,
    price_scale_floor: float,
    ofi_scale_floor: float,
    green_coeff: float,
    dist_to_boundary: np.ndarray,
):
    """
    V64 engineering fast path:
    - preserves the canonical closed-area / closed-perimeter topology math
    - removes per-row window slices and local cumulative-OFI allocations
    - keeps the exact Q_topo = 4*pi*|A_closed| / L_closed^2 definition
    """
    n = len(prices)
    out_area = np.zeros(n, dtype=np.float64)
    out_energy = np.zeros(n, dtype=np.float64)
    out_q = np.zeros(n, dtype=np.float64)

    if window <= 1 or n < window:
        return out_area, out_energy, out_q

    # Boundary-aware cumulative OFI. Because the canonical topology normalizes
    # with window-local mean, any per-window additive constant cancels exactly.
    cum_ofi = np.empty(n, dtype=np.float64)
    segment_cum = 0.0
    for i in range(n):
        if dist_to_boundary[i] == 0:
            segment_cum = 0.0
        segment_cum += ofis[i]
        cum_ofi[i] = segment_cum

    sum_x = 0.0
    sum_x2 = 0.0
    sum_y = 0.0
    sum_y2 = 0.0
    pair_sum = 0.0
    count = 0
    prev_x = 0.0
    prev_y = 0.0

    for i in range(n):
        if dist_to_boundary[i] == 0:
            sum_x = 0.0
            sum_x2 = 0.0
            sum_y = 0.0
            sum_y2 = 0.0
            pair_sum = 0.0
            count = 0

        x = prices[i]
        y = cum_ofi[i]

        if count > 0:
            pair_sum += prev_x * y - x * prev_y
        prev_x = x
        prev_y = y

        sum_x += x
        sum_x2 += x * x
        sum_y += y
        sum_y2 += y * y
        count += 1

        if count > window:
            out_idx = i - window
            x_out = prices[out_idx]
            y_out = cum_ofi[out_idx]
            x_next = prices[out_idx + 1]
            y_next = cum_ofi[out_idx + 1]

            pair_sum -= x_out * y_next - x_next * y_out
            sum_x -= x_out
            sum_x2 -= x_out * x_out
            sum_y -= y_out
            sum_y2 -= y_out * y_out
            count = window

        if count < window:
            continue

        mean_x = sum_x / window
        mean_y = sum_y / window
        var_x = (sum_x2 / window) - mean_x * mean_x
        var_y = (sum_y2 / window) - mean_y * mean_y

        sx = math.sqrt(var_x) if var_x > 0.0 else 0.0
        sy = math.sqrt(var_y) if var_y > 0.0 else 0.0
        if sx < price_scale_floor:
            sx = price_scale_floor
        if sy < ofi_scale_floor:
            sy = ofi_scale_floor

        start = i - window + 1
        first_x = prices[start]
        first_y = cum_ofi[start]
        raw_closed_area = pair_sum + x * first_y - first_x * y

        area_val = green_coeff * raw_closed_area / (sx * sy)
        out_area[i] = area_val

        inv_sx = 1.0 / sx
        inv_sy = 1.0 / sy
        energy_sum = 0.0

        for j in range(start, i):
            dx = (prices[j + 1] - prices[j]) * inv_sx
            dy = (cum_ofi[j + 1] - cum_ofi[j]) * inv_sy
            energy_sum += math.sqrt(dx * dx + dy * dy)

        dx_close = (first_x - x) * inv_sx
        dy_close = (first_y - y) * inv_sy
        energy_sum += math.sqrt(dx_close * dx_close + dy_close * dy_close)

        out_energy[i] = energy_sum

        if energy_sum > PLANCK_CONSTANT:
            q_val = (4.0 * math.pi * abs(area_val)) / (energy_sum * energy_sum)
            if q_val > 1.0:
                q_val = 1.0
            elif q_val < 0.0:
                q_val = 0.0
            out_q[i] = q_val

    return out_area, out_energy, out_q


@njit(cache=True, nogil=True, fastmath=False)
def calc_srl_compression_gain_rolling(
    price_change: np.ndarray,
    srl_residuals: np.ndarray,
    window: int,
    dist_to_boundary: np.ndarray,
) -> np.ndarray:
    """
    第一性原理闭合: 计算 SRL 相对均值模型的信息论压缩增益 (Prequential MDL Gain)。

    V64 engineering fast path:
    - exact same Delta k = 0 mathematics
    - O(N) boundary-aware rolling state instead of O(N*W) slicing
    - no temporary windows, no hidden allocator churn
    """
    n = len(srl_residuals)
    out = np.zeros(n, dtype=np.float64)

    if window <= 1 or n < window:
        return out

    sum_dp = 0.0
    sum_dp2 = 0.0
    sum_r = 0.0
    sum_r2 = 0.0
    count = 0

    for i in range(n):
        if dist_to_boundary[i] == 0:
            sum_dp = 0.0
            sum_dp2 = 0.0
            sum_r = 0.0
            sum_r2 = 0.0
            count = 0

        dp = price_change[i]
        resid = srl_residuals[i]

        sum_dp += dp
        sum_dp2 += dp * dp
        sum_r += resid
        sum_r2 += resid * resid
        count += 1

        if count > window:
            out_idx = i - window
            dp_out = price_change[out_idx]
            resid_out = srl_residuals[out_idx]

            sum_dp -= dp_out
            sum_dp2 -= dp_out * dp_out
            sum_r -= resid_out
            sum_r2 -= resid_out * resid_out
            count = window

        if count < window:
            continue

        mean_dp = sum_dp / window
        var_dp = (sum_dp2 / window) - (mean_dp * mean_dp)
        if var_dp < PLANCK_CONSTANT:
            out[i] = 0.0
            continue

        mean_r = sum_r / window
        var_r = (sum_r2 / window) - (mean_r * mean_r)
        safe_var_r = max(var_r, PLANCK_CONSTANT)
        ratio = var_dp / safe_var_r

        if ratio > 1.0:
            out[i] = (window / 2.0) * math.log(ratio)

    return out


@njit(cache=True, nogil=True, fastmath=False)
def calc_topology_area_rolling(
    x_arr: np.ndarray,
    y_arr: np.ndarray,
    window: int,
    x_scale_floor: float,
    y_scale_floor: float,
    green_coeff: float,
    dist_to_boundary: np.ndarray,
) -> np.ndarray:
    """
    Vectorized Green's Theorem area for arbitrary manifolds (X, Y).

    V64 engineering fast path:
    - exact open-chain normalized area
    - O(N) boundary-aware rolling state
    - endpoint correction preserves the historical centered formula exactly
    """
    n = len(x_arr)
    out_area = np.zeros(n, dtype=np.float64)

    if window <= 1 or n < window:
        return out_area

    sum_x = 0.0
    sum_x2 = 0.0
    sum_y = 0.0
    sum_y2 = 0.0
    pair_sum = 0.0
    count = 0
    prev_x = 0.0
    prev_y = 0.0

    for i in range(n):
        if dist_to_boundary[i] == 0:
            sum_x = 0.0
            sum_x2 = 0.0
            sum_y = 0.0
            sum_y2 = 0.0
            pair_sum = 0.0
            count = 0

        x = x_arr[i]
        y = y_arr[i]

        if count > 0:
            pair_sum += prev_x * y - x * prev_y
        prev_x = x
        prev_y = y

        sum_x += x
        sum_x2 += x * x
        sum_y += y
        sum_y2 += y * y
        count += 1

        if count > window:
            out_idx = i - window
            x_out = x_arr[out_idx]
            y_out = y_arr[out_idx]
            x_next = x_arr[out_idx + 1]
            y_next = y_arr[out_idx + 1]

            pair_sum -= x_out * y_next - x_next * y_out
            sum_x -= x_out
            sum_x2 -= x_out * x_out
            sum_y -= y_out
            sum_y2 -= y_out * y_out
            count = window

        if count < window:
            continue

        mean_x = sum_x / window
        mean_y = sum_y / window
        var_x = (sum_x2 / window) - (mean_x * mean_x)
        var_y = (sum_y2 / window) - (mean_y * mean_y)

        sx = math.sqrt(var_x) if var_x > 0.0 else 0.0
        sy = math.sqrt(var_y) if var_y > 0.0 else 0.0
        if sx < x_scale_floor:
            sx = x_scale_floor
        if sy < y_scale_floor:
            sy = y_scale_floor

        first_x = x_arr[i - window + 1]
        first_y = y_arr[i - window + 1]
        area_sum = pair_sum + mean_y * (x - first_x) + mean_x * (first_y - y)

        out_area[i] = green_coeff * area_sum / (sx * sy)

    return out_area
