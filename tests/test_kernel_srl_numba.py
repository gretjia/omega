
import unittest
import numpy as np
import math
import time
import sys

try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    print("Numba not installed. Skipping Numba tests.")

# --- Pure Python Baseline (from omega_math_core.py & kernel.py) ---

def py_calc_srl_state(
    price_change: float,
    sigma: float,
    net_ofi: float,
    depth: float,
    current_y: float,
    depth_floor: float,
    sigma_floor: float,
    spoof_ratio_eps: float,
    spoof_penalty_gamma: float,
    implied_y_min_impact: float,
    implied_y_min_penalty: float,
    cancel_vol: float,
    trade_vol: float,
):
    # 1. Safety Floors
    safe_depth = max(float(depth), float(depth_floor))
    safe_sigma = max(float(sigma), float(sigma_floor))

    # 2. Spoofing Penalty
    safe_trade = max(float(trade_vol), float(spoof_ratio_eps))
    spoof_ratio = max(float(cancel_vol), 0.0) / safe_trade

    penalty = math.exp(-float(spoof_penalty_gamma) * spoof_ratio)
    effective_depth = max(safe_depth * penalty, float(depth_floor))

    # 3. Square Root Law (Delta=0.5)
    # Impact = Y * Sigma * sqrt(|OFI| / Depth)
    q_over_d = abs(float(net_ofi)) / effective_depth
    
    # Sato 2025: "delta is exactly 0.5"
    raw_impact_unit = safe_sigma * math.sqrt(q_over_d) 
    
    sign = 1.0 if net_ofi > 0 else (-1.0 if net_ofi < 0 else 0.0)
    
    # Theoretical Impact
    theory_impact = sign * float(current_y) * raw_impact_unit
    
    # Residual
    srl_resid = float(price_change) - float(theory_impact)

    # 4. Implied Y
    if raw_impact_unit > implied_y_min_impact and penalty > implied_y_min_penalty:
        implied_y = abs(float(price_change)) / (raw_impact_unit + 1e-9)
    else:
        implied_y = float(current_y)

    return srl_resid, implied_y, effective_depth, float(spoof_ratio)

def py_run_srl_loop(
    n_rows,
    price_change,
    sigma_eff,
    net_ofi,
    depth_eff,
    cancel_vol,
    trade_vol,
    initial_y,
    # Config params
    depth_floor, sigma_floor, spoof_ratio_eps, spoof_penalty_gamma,
    implied_y_min_impact, implied_y_min_penalty,
    y_min, y_max, y_alpha, anchor_y, anchor_w, clip_lo, clip_hi,
    out_is_active, out_epi, peace_threshold, min_ofi_for_y
):
    out_srl_resid = np.zeros(n_rows, dtype=np.float64)
    out_y = np.zeros(n_rows, dtype=np.float64)
    out_spoof = np.zeros(n_rows, dtype=np.float64)
    # Note: depth_eff array is updated based on calculation? 
    # Actually kernel.py creates `depth_eff_arr` AFTER the loop based on spoof. 
    # But `calc_srl_state` takes `depth` and returns `effective_depth`.
    # In kernel.py loop:
    # resid, imp_y, eff_d, spoof = calc_srl_state(..., depth=depth_eff[i], ...)
    
    current_y = float(initial_y)

    for i in range(n_rows):
        resid, imp_y, eff_d, spoof = py_calc_srl_state(
            price_change[i], sigma_eff[i], net_ofi[i], depth_eff[i],
            current_y,
            depth_floor, sigma_floor, spoof_ratio_eps, spoof_penalty_gamma,
            implied_y_min_impact, implied_y_min_penalty,
            cancel_vol[i], trade_vol[i]
        )
        out_srl_resid[i] = resid
        out_spoof[i] = spoof
        
        # Adaptive Y Update
        if out_is_active[i] and out_epi[i] > peace_threshold and abs(net_ofi[i]) > min_ofi_for_y:
            new_y = float(np.clip(imp_y, y_min, y_max))
            current_y = (1.0 - y_alpha) * current_y + y_alpha * new_y
            
        if anchor_w > 0.0:
            current_y = (1.0 - anchor_w) * current_y + anchor_w * anchor_y
            
        current_y = float(np.clip(current_y, clip_lo, clip_hi))
        out_y[i] = current_y
        
    return out_srl_resid, out_y, out_spoof

# --- Numba Implementation (Target) ---

if NUMBA_AVAILABLE:
    @njit(cache=True, fastmath=True)
    def nb_run_srl_loop(
        n_rows,
        price_change,
        sigma_eff,
        net_ofi,
        depth_eff,
        cancel_vol,
        trade_vol,
        initial_y,
        # Config params as scalars
        depth_floor, sigma_floor, spoof_ratio_eps, spoof_penalty_gamma,
        implied_y_min_impact, implied_y_min_penalty,
        y_min, y_max, y_alpha, anchor_y, anchor_w, clip_lo, clip_hi,
        out_is_active, out_epi, peace_threshold, min_ofi_for_y
    ):
        out_srl_resid = np.zeros(n_rows, dtype=np.float64)
        out_y = np.zeros(n_rows, dtype=np.float64)
        out_spoof = np.zeros(n_rows, dtype=np.float64)
        
        current_y = float(initial_y)
        
        # Inline calc_srl_state logic for maximum speed
        for i in range(n_rows):
            # 1. Safety Floors
            safe_depth = max(depth_eff[i], depth_floor)
            safe_sigma = max(sigma_eff[i], sigma_floor)

            # 2. Spoofing Penalty
            safe_trade = max(trade_vol[i], spoof_ratio_eps)
            c_vol = max(cancel_vol[i], 0.0)
            spoof_ratio = c_vol / safe_trade

            penalty = math.exp(-spoof_penalty_gamma * spoof_ratio)
            effective_depth = max(safe_depth * penalty, depth_floor)

            # 3. SRL
            q_over_d = abs(net_ofi[i]) / effective_depth
            raw_impact_unit = safe_sigma * math.sqrt(q_over_d) 
            
            sign = 1.0 if net_ofi[i] > 0 else (-1.0 if net_ofi[i] < 0 else 0.0)
            theory_impact = sign * current_y * raw_impact_unit
            
            resid = price_change[i] - theory_impact
            
            # 4. Implied Y
            implied_y = current_y
            if raw_impact_unit > implied_y_min_impact and penalty > implied_y_min_penalty:
                implied_y = abs(price_change[i]) / (raw_impact_unit + 1e-9)

            out_srl_resid[i] = resid
            out_spoof[i] = spoof_ratio
            
            # Adaptive Y Update
            # Numba handles boolean indexing efficiently? Here it's scalar bool
            # out_is_active[i] is bool or int
            if out_is_active[i] and out_epi[i] > peace_threshold and abs(net_ofi[i]) > min_ofi_for_y:
                # Clip new_y
                if implied_y < y_min: implied_y = y_min
                elif implied_y > y_max: implied_y = y_max
                
                current_y = (1.0 - y_alpha) * current_y + y_alpha * implied_y
                
            if anchor_w > 0.0:
                current_y = (1.0 - anchor_w) * current_y + anchor_w * anchor_y
                
            if current_y < clip_lo: current_y = clip_lo
            elif current_y > clip_hi: current_y = clip_hi
            
            out_y[i] = current_y
            
        return out_srl_resid, out_y, out_spoof

class TestKernelSRLNumba(unittest.TestCase):
    def setUp(self):
        self.n_rows = 1000
        np.random.seed(42)
        self.price_change = np.random.randn(self.n_rows).astype(np.float64)
        self.sigma_eff = np.random.rand(self.n_rows).astype(np.float64) + 0.01
        self.net_ofi = np.random.randn(self.n_rows).astype(np.float64) * 100
        self.depth_eff = np.random.rand(self.n_rows).astype(np.float64) * 10 + 1.0
        self.cancel_vol = np.random.rand(self.n_rows).astype(np.float64) * 50
        self.trade_vol = np.random.rand(self.n_rows).astype(np.float64) * 100 + 10
        self.initial_y = 1.0
        
        self.out_is_active = np.random.randint(0, 2, self.n_rows).astype(bool)
        self.out_epi = np.random.rand(self.n_rows).astype(np.float64)
        
        # Params
        self.params = {
            "depth_floor": 1.0, "sigma_floor": 0.01, 
            "spoof_ratio_eps": 1e-9, "spoof_penalty_gamma": 0.1,
            "implied_y_min_impact": 0.001, "implied_y_min_penalty": 0.5,
            "y_min": 0.1, "y_max": 5.0, "y_alpha": 0.05, 
            "anchor_y": 1.0, "anchor_w": 0.01, 
            "clip_lo": 0.4, "clip_hi": 1.5,
            "peace_threshold": 0.5, "min_ofi_for_y": 10.0
        }

    def test_correctness(self):
        if not NUMBA_AVAILABLE: return
        
        # Python Run
        res_py = py_run_srl_loop(
            self.n_rows, self.price_change, self.sigma_eff, self.net_ofi, self.depth_eff,
            self.cancel_vol, self.trade_vol, self.initial_y,
            self.params["depth_floor"], self.params["sigma_floor"], self.params["spoof_ratio_eps"], self.params["spoof_penalty_gamma"],
            self.params["implied_y_min_impact"], self.params["implied_y_min_penalty"],
            self.params["y_min"], self.params["y_max"], self.params["y_alpha"], self.params["anchor_y"], self.params["anchor_w"], 
            self.params["clip_lo"], self.params["clip_hi"],
            self.out_is_active, self.out_epi, self.params["peace_threshold"], self.params["min_ofi_for_y"]
        )
        
        # Numba Run
        # Warmup
        nb_run_srl_loop(
            10, self.price_change[:10], self.sigma_eff[:10], self.net_ofi[:10], self.depth_eff[:10],
            self.cancel_vol[:10], self.trade_vol[:10], self.initial_y,
            self.params["depth_floor"], self.params["sigma_floor"], self.params["spoof_ratio_eps"], self.params["spoof_penalty_gamma"],
            self.params["implied_y_min_impact"], self.params["implied_y_min_penalty"],
            self.params["y_min"], self.params["y_max"], self.params["y_alpha"], self.params["anchor_y"], self.params["anchor_w"], 
            self.params["clip_lo"], self.params["clip_hi"],
            self.out_is_active[:10], self.out_epi[:10], self.params["peace_threshold"], self.params["min_ofi_for_y"]
        )
        
        res_nb = nb_run_srl_loop(
            self.n_rows, self.price_change, self.sigma_eff, self.net_ofi, self.depth_eff,
            self.cancel_vol, self.trade_vol, self.initial_y,
            self.params["depth_floor"], self.params["sigma_floor"], self.params["spoof_ratio_eps"], self.params["spoof_penalty_gamma"],
            self.params["implied_y_min_impact"], self.params["implied_y_min_penalty"],
            self.params["y_min"], self.params["y_max"], self.params["y_alpha"], self.params["anchor_y"], self.params["anchor_w"], 
            self.params["clip_lo"], self.params["clip_hi"],
            self.out_is_active, self.out_epi, self.params["peace_threshold"], self.params["min_ofi_for_y"]
        )
        
        # Assert Close
        np.testing.assert_allclose(res_py[0], res_nb[0], rtol=1e-5, err_msg="SRL Resid Mismatch")
        np.testing.assert_allclose(res_py[1], res_nb[1], rtol=1e-5, err_msg="Y Mismatch")
        np.testing.assert_allclose(res_py[2], res_nb[2], rtol=1e-5, err_msg="Spoof Mismatch")

    def test_benchmark(self):
        if not NUMBA_AVAILABLE: return
        
        N = 100000
        # Larger arrays - Force contiguous
        pc = np.ascontiguousarray(np.tile(self.price_change, N // self.n_rows))
        se = np.ascontiguousarray(np.tile(self.sigma_eff, N // self.n_rows))
        no = np.ascontiguousarray(np.tile(self.net_ofi, N // self.n_rows))
        de = np.ascontiguousarray(np.tile(self.depth_eff, N // self.n_rows))
        cv = np.ascontiguousarray(np.tile(self.cancel_vol, N // self.n_rows))
        tv = np.ascontiguousarray(np.tile(self.trade_vol, N // self.n_rows))
        oa = np.ascontiguousarray(np.tile(self.out_is_active, N // self.n_rows))
        oe = np.ascontiguousarray(np.tile(self.out_epi, N // self.n_rows))
        
        # Warmup Numba with the EXACT same arrays (slice) to ensure compilation matches
        nb_run_srl_loop(
            100, pc[:100], se[:100], no[:100], de[:100], cv[:100], tv[:100], self.initial_y,
            self.params["depth_floor"], self.params["sigma_floor"], self.params["spoof_ratio_eps"], self.params["spoof_penalty_gamma"],
            self.params["implied_y_min_impact"], self.params["implied_y_min_penalty"],
            self.params["y_min"], self.params["y_max"], self.params["y_alpha"], self.params["anchor_y"], self.params["anchor_w"], 
            self.params["clip_lo"], self.params["clip_hi"],
            oa[:100], oe[:100], self.params["peace_threshold"], self.params["min_ofi_for_y"]
        )
        
        # Python Time
        t0 = time.time()
        py_run_srl_loop(
            N, pc, se, no, de, cv, tv, self.initial_y,
            self.params["depth_floor"], self.params["sigma_floor"], self.params["spoof_ratio_eps"], self.params["spoof_penalty_gamma"],
            self.params["implied_y_min_impact"], self.params["implied_y_min_penalty"],
            self.params["y_min"], self.params["y_max"], self.params["y_alpha"], self.params["anchor_y"], self.params["anchor_w"], 
            self.params["clip_lo"], self.params["clip_hi"],
            oa, oe, self.params["peace_threshold"], self.params["min_ofi_for_y"]
        )
        t_py = time.time() - t0
        
        # Numba Time
        t0 = time.time()
        nb_run_srl_loop(
            N, pc, se, no, de, cv, tv, self.initial_y,
            self.params["depth_floor"], self.params["sigma_floor"], self.params["spoof_ratio_eps"], self.params["spoof_penalty_gamma"],
            self.params["implied_y_min_impact"], self.params["implied_y_min_penalty"],
            self.params["y_min"], self.params["y_max"], self.params["y_alpha"], self.params["anchor_y"], self.params["anchor_w"], 
            self.params["clip_lo"], self.params["clip_hi"],
            oa, oe, self.params["peace_threshold"], self.params["min_ofi_for_y"]
        )
        t_nb = time.time() - t0
        
        print(f"\nBenchmark N={N}: Python={t_py:.4f}s, Numba={t_nb:.4f}s. Speedup={t_py/(t_nb+1e-9):.1f}x")
        self.assertLess(t_nb, t_py * 0.5, "Numba should be at least 2x faster (expect >50x)")

if __name__ == "__main__":
    unittest.main()
