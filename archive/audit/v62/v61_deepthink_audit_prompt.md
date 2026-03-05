# OMEGA v61 Codebase Audit Prompt for Gemini 3 Pro DeepThink

**[SYSTEM DIRECTIVE TO GEMINI 3 PRO DEEPTHINK]**
You are the Chief Reliability Engineer and Quant Architect. Please audit the following OMEGA v61 codebase constraints against the provided architectural blueprint (`v61.md`).
Specifically, verify if the four catastrophic mathematical/logic misalignments identified in v60 have been correctly resolved in the v61 codebase below.

1. The Dataset Collapse (XGBoost & Physics Gates)
2. Mean-Reversion Bug (Inverted Momentum for A-Shares)
3. Beta Contamination (Subtracting market mean)
4. 3-Second Snapshot Aliasing (Low-Pass Filter)

## 1. Empirical Evidence (v60 Validation Failure)

Before analyzing the fixes, you must understand the exact failure mode of v60 that prompted this architectural rescue.

### 1.1 The Physical Engine Success (Topo_SNR)

The v60 deterministic physics engine successfully extracted **`"Topo_SNR": 10.8854`**.
This means during signal triggers, the topological compression of the A-share micro-orderbook was mathematically 10.88x stronger than a random brownian walk. The physical premise ("Compression = Intelligence") was perfectly validated.

### 1.2 The Machine Learning Collapse (Alignment & Overfitting)

Despite the physical validation, the XGBoost downstream alignment failed with a coin-flip prediction rate (**`Model_Alignment = 0.4974`**).
The root causes extracted from the training logs (`train_metrics_20260219-125410_78e36d9.json`):

* `base_rows`: **5,780,139** (total underlying market states)
* `total_training_rows`: **2,067** (rows passed to XGBoost)

The optimizer (Optuna) discovered a "shortcut" to maximize AUC by pushing the physical gates incredibly high (`peace_threshold=0.525`, `topo_mult=5.42`). This violently collapsed the 5.7M row continuous manifold into just 2,000 isolated extreme outliers. XGBoost memorized these outliers, leading to out-of-sample catastrophic failure when exposed to normal market regimes.

Furthermore, we discovered the baseline directional math was inverted (designed for mean-reversion, not momentum following), the binary target was contaminated by macro-market Beta, and 3-second snapshot aliasing noise was bleeding into the features.

## 2. The Mathematical Core (v61 Physics Foundation)

OMEGA v61 is built on a deterministic physics engine that enforces the "Compression = Intelligence" thesis. The core math operates directly on Level-2 orderbook traces before any Machine Learning is applied. Here are the three pillars:

### 2.1 Epiplexity (Structural Compression Gain)

Epiplexity measures if a micro-price trace has extractable structure (Signal) or is pure entropy (Noise). It computes the $R^2$ of a simplest Linear Predictor against the Null Hypothesis (Random Walk).

* Gain > 0: Structured intervention by Main Force.
* Gain <= 0: Brownian noise.

```python
# From omega_core/omega_math_core.py
def calc_compression_gain(trace: Sequence[float], cfg: L2EpiplexityConfig) -> float:
    # 1. Null Model (Entropy Baseline) - Variance
    var_total = np.var(arr)
    # 2. Time-Bounded Model (Linear Predictor)
    # We fit y = mx + c analytically (O(N)).
    slope = numerator / denominator
    intercept = x_mean - slope * t_mean
    # 3. Compression Gain
    trend = slope * t + intercept
    residuals = arr - trend
    var_resid = np.mean(residuals ** 2)
    # Gain = 1 - (Unexplained_Entropy / Total_Entropy)
    return float(np.clip(1.0 - (var_resid / var_total), 0.0, 1.0))
```

### 2.2 Universal Square Root Law (SRL)

Derived from Sato & Kanazawa (2025), this enforces a strict $\Delta = 0.5$ universality. The engine calculates the expected price impact of a given Order Flow Imbalance (OFI) under current market rigidity ($Y$). The `srl_resid` represents the violation of this physical law (i.e., hidden momentum).

```python
# From omega_core/omega_math_core.py
def calc_srl_state(price_change, sigma, net_ofi, depth, current_y, cfg, cancel_vol, trade_vol):
    # 2. Spoofing Penalty (Microstructure Correction)
    spoof_ratio = max(float(cancel_vol), 0.0) / max(float(trade_vol), eps)
    penalty = math.exp(-gamma * spoof_ratio)
    effective_depth = max(safe_depth * penalty, float(cfg.depth_floor))

    # 3. The Square Root Law (Delta = 0.5 Hardcoded)
    # Impact = Y * Sigma * sqrt(|OFI| / Depth)
    q_over_d = abs(float(net_ofi)) / effective_depth
    raw_impact_unit = safe_sigma * math.sqrt(q_over_d) 
    
    sign = float(np.sign(float(net_ofi)))
    theory_impact = sign * float(current_y) * raw_impact_unit
    
    # Residual: How much did Price violate Physics?
    srl_resid = float(price_change) - float(theory_impact)
    # ... calculates implied_y for next state
    return srl_resid, implied_y, effective_depth, float(spoof_ratio)
```

### 2.3 Holographic Topology (Area & Energy)

Treats the order book as a 2D manifold where X = Price and Y = Cumulative OFI (Flow). It uses Green's Theorem to calculate the signed topological area, capturing non-linear market making behaviors.

```python
# From omega_core/omega_math_vectorized.py
def calc_holographic_topology_vectorized(trace, ofi_list, price_scale_floor, ofi_scale_floor, green_coeff):
    # Normalize X (Price) and Y (Cumulative OFI)
    Xn = (X - mx[:, None]) / sx[:, None]
    Yn = (Y - my[:, None]) / sy[:, None]
    
    # Area (Cross Product via Green's Theorem)
    x_i, x_ip1 = Xn[:, :-1], Xn[:, 1:]
    y_i, y_ip1 = Yn[:, :-1], Yn[:, 1:]
    cross = x_i * y_ip1 - x_ip1 * y_i
    area = np.nansum(cross, axis=1) * green_coeff
    
    # Energy (Path Length)
    dx = np.diff(Xn, axis=1)
    dy = np.diff(Yn, axis=1)
    energy = np.nansum(np.sqrt(dx**2 + dy**2), axis=1)
    
    return area, energy
```

---

## 3. Architectural Blueprint: `audit/v61.md`

```markdown
[SYSTEM DIRECTIVE: CHIEF ARCHITECT -> SOLO QUANT (PRINCIPAL)]

这是一份在物理层面上极其伟大，但在机器学习（ML）层面上极其惨烈的实盘确证报告。

不要因为 Model_Alignment = 0.4974（相当于掷硬币）而感到挫败。请把目光死死盯住证据包中的这个数字：
"Topo_SNR": 10.8854

在量化金融这一充满高熵噪音的深水区，信噪比能突破 3 就已经是圣杯级别。10.88 意味着，在你系统触发的瞬间，A股微观订单簿的拓扑结构压缩强度，是纯随机游走的整整 11 倍！

为什么最终方向预测会迷路？因为遭遇了四个灾难级的数学/逻辑错位。

### 核心死因剖析与 V6.1 修护计划

### ACTION 1: Stop Dataset Collapse
Optuna 作弊把门控推得太高，导致 578 万行只保留 2000 行。必须限制门控下限，约束树深。

### ACTION 2: Fix the Momentum Sign (`omega_core/kernel.py`)
A 股是顺势跟随主力的市场。
错误逻辑：`(-pl.col("srl_resid").sign()).alias("direction")`
正确修复：`(pl.col("srl_resid").sign()).alias("direction")`

### ACTION 3: Orthogonalize the Target / Excess Return (`run_vertex_xgb_train.py`)
剔除宏观 Beta 污染，改为预测 Excess Return：
```python
df = df.with_columns([
    (pl.col("t1_fwd_return") - pl.col("t1_fwd_return").mean().over("date")).alias("t1_excess_return")
])
self.y = (df.get_column("t1_excess_return").to_numpy() > 0).astype(int)
```

### ACTION 4: Pass the 3-Second Snapshot Audit (`omega_core/omega_etl.py`)

增加低通滤波器解决快照混叠：

```python
lf = lf.with_columns([
    pl.col("v_ofi").rolling_mean(window_size=3, min_periods=1).alias("v_ofi"),
    pl.col("depth").rolling_mean(window_size=3, min_periods=1).alias("depth")
])
```

```


---

## 2. Core Physics Engine: `omega_core/kernel.py`

```python
import numpy as np
import polars as pl
from config import L2PipelineConfig

def _apply_recursive_physics(frames: pl.DataFrame, cfg: L2PipelineConfig, initial_y: float | None = None) -> pl.DataFrame:
    # [Omitted boilerplate...]
    res_df = res_df.with_columns([
        (
            (pl.col("is_energy_active") == True)
            & (pl.col("epiplexity") > peace_threshold) 
            & (pl.col("srl_resid").abs() > float(sig.srl_resid_sigma_mult) * pl.col("sigma_eff"))
            & (pl.col("topo_area").abs() > float(sig.topo_area_min_abs))
            & (pl.col("topo_energy") > pl.col("sigma_eff") * topo_energy_sigma_mult)
            & (pl.col("spoof_ratio") < spoofing_ratio_max)
        ).alias("is_signal"),
        (pl.col("srl_resid").sign()).alias("direction"), # ACTION 2: Fixed Momentum Sign
    ])
    return res_df
```

---

## 3. Data Extraction Pipeline: `omega_core/omega_etl.py`

```python
import polars as pl

def build_l2_frames(path, cfg, target_frames=None) -> pl.DataFrame:
    # [Omitted grouping, filtering, schema logic ...]
    
    # Phase 1: 3-second snapshot aggregation handling (Anti-Aliasing Low-Pass Filter)
    if group_col:
        lf = lf.with_columns([
            pl.col("v_ofi").rolling_mean(window_size=3, min_periods=1).over(group_col).alias("v_ofi"),
            pl.col("depth").rolling_mean(window_size=3, min_periods=1).over(group_col).alias("depth")
        ])
    else:
        lf = lf.with_columns([
            pl.col("v_ofi").rolling_mean(window_size=3, min_periods=1).alias("v_ofi"),
            pl.col("depth").rolling_mean(window_size=3, min_periods=1).alias("depth")
        ])
    # ...
```

---

## 4. Model Training: `tools/run_vertex_xgb_train.py`

```python
import polars as pl

def run_global_training(args):
    df = pl.read_parquet(local_matrix)
    
    # v6.1: Calculate Excess Return Target (Alpha)
    print("[*] Orthogonalizing target (Excess Return)...", flush=True)
    df = df.with_columns([
        (pl.col("t1_fwd_return") - pl.col("t1_fwd_return").mean().over("date")).alias("t1_excess_return")
    ])
    
    # Use Excess Return for label
    y_all = (df.get_column("t1_excess_return").to_numpy() > 0).astype(int)
    
    # [Omitted XGBoost initialization and filtering...]
```

---

## 5. Sharding/Framing Driver: `tools/v61_linux_framing.py`

```python
import hashlib
from multiprocessing import get_context

os.environ["POLARS_MAX_THREADS"] = "8" # ANTI-FRAGILE MEMORY FIX

def get_shard(filename, total_shards):
    h = hashlib.md5(filename.encode()).hexdigest()
    return int(h, 16) % total_shards
    
# [Omitted parallel framework ...]
```

---

**[INSTRUCTIONS FOR DEEPTHINK]**
Review the provided snippets against the 4 directives from the Chief Architect.
Are there any logical flaws, missing links, or unexpected side-effects introduced by these changes? Please provide a detailed response pointing out any potential dangers before we migrate this codebase to GCP.
