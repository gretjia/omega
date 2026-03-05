这是一份针对 **AI 实施架构师 (AI Implementation Architect)** 的终局架构规范（Endgame Architecture Specification）。

这份文档剥离了所有人类修辞，仅保留**数学定义**、**物理约束**和**工程指令**。请直接将此规范输入给具备代码生成能力的 AI Agent，用于生成 `omega_v3_core`。

---

# OMEGA Project: Endgame Architecture Specification (v3.0.0)

**Target:** AI Implementation Architect (Autonomous Agent)
**Context:** High-Frequency Trading (China A-Shares Level-2), 2023-2025 Full Data
**Paradigm:** Physics-Informed Deterministic System (No Blackbox ML)
**Status:** **EXECUTE IMMEDIATE**

---

## 1. System Axioms (Non-Negotiable)

1. **Spacetime Orthogonality**: All operations **MUST** occur in **Volume-Clock Space** (), never Wall-Clock Space.
* *Constraint*: Time is a feature variable, not an index. Sampling is triggered by `CumVolume`, linearizing the market execution time.


2. **Vectorization Imperative**: Python loops (`for`, `while`) are strictly forbidden in data processing. All logic must be expressed as Tensor/Matrix operations (using `Polars` Expressions or `NumPy` Broadcasting).
3. **Signal Logic**: A valid signal is the intersection of:
$$ S = \text{Structure}*{Info} \cap \text{Anomaly}*{Physics} \cap \text{Direction}_{Geometry} $$
4. **Objective Function**: Maximize **Topological SNR** and **Epistemic Orthogonality**, not PnL.

---

## 2. Mathematical Kernels (`omega_math_core.py`)

**Directive**: Implement stateless, vectorized physics engines.

### 2.1 Kernel A: Epiplexity (Information Structure)

**Objective**: Quantify "Algorithmic Rigidity" vs "Stochastic Noise".
**Definition**:

1. **Input**: Price Sequence  within a Volume Bucket.
2. **Symbolization (SAX)**: Map  to alphabet  based on local .
3. **Compression**: , .
4. **Metric**:
$$ E_{\pi} = 4 \cdot r \cdot (1 - r), \quad \text{where } r = L_{zip} / L_{raw} $$
*(Maps  to parabolic structure score. Peaked at 0.5 = Max Structure)*.

### 2.2 Kernel B: Inverse Square-Root Law (Physics Residuals)

**Objective**: Detect "Dark Matter" (Iceberg Liquidity Absorption).
**Forward Model**:
$$ \Delta P_{theo} = \text{sgn}(\Phi) \cdot Y \cdot \sigma \cdot \sqrt{\frac{|\Phi|}{D}} $$

* : Net Order Flow Imbalance (OFI).
* : Effective LOB Depth.
* : Impact Coefficient (Calibrated on 2023 data).
**Residual (The Alpha)**:
$$ R_{SRL} = \Delta P_{actual} - \Delta P_{theo} $$
* **Signal**:  implies Hidden Buy Wall (Absorption).

### 2.3 Kernel C: Symplectic Geometry (Vectorized TDA)

**Objective**: Resolve Directionality of Topology (Vector Alignment).
**Logic**: Instead of slow Persistent Homology loops, compute **Signed Phase Area**.
**Phase Space**: , .
$$ \mathcal{A} = \frac{1}{2} \sum_{i} (x_i y_{i+1} - x_{i+1} y_i) $$

* : Counter-Clockwise Loop (Accumulation).
* : Clockwise Loop (Distribution).

---

## 3. Data Engineering Pipeline (`omega_etl.py`)

**Technology**: `Polars` (Rust-based LazyFrame) is mandatory.

### 3.1 Vectorized Micro-Features

Compute at Tick Level before resampling:

1. **Micro-Price ()**: .
2. **OFI Vector ()**:
$$ \phi_t = V_t \cdot \mathbb{I}(P_t > P_{t-1}) - V_t \cdot \mathbb{I}(P_t < P_{t-1}) $$

### 3.2 Volume Clock Resampling

**Algorithm**:

1. **CumSum**: .
2. **Bucket ID**: .
3. **Aggregation Tensor **:
* `Open, Close`: First/Last .
* `Net_OFI`: .
* `Trace`: List() [For Epiplexity].
* `Vol_Realized`: .



---

## 4. Execution Logic (`kernel.py`)

**Code Skeleton (Production Ready)**:

```python
import polars as pl
import numpy as np
import zlib

# --- CONFIGURATION ---
Y_COEFF = 0.75  # Calibration Target
VOL_BUCKET_SIZE = 2000 # Hands

def omega_pipeline_l2(parquet_path: str):
    
    # 1. LAZY LOAD & MICRO-VECTORIZATION
    q = (
        pl.scan_parquet(parquet_path)
        .sort("Time")
        .with_columns([
            # Micro-Price
            ((pl.col("BidP1") * pl.col("AskV1") + pl.col("AskP1") * pl.col("BidV1")) / 
             (pl.col("BidV1") + pl.col("AskV1"))).alias("P_micro"),
             
            # Micro-OFI (Simplified Vectorized Logic)
            pl.when(pl.col("Price") > pl.col("Price").shift(1)).then(pl.col("Vol"))
              .when(pl.col("Price") < pl.col("Price").shift(1)).then(-pl.col("Vol"))
              .otherwise(0).alias("v_OFI")
        ])
    )

    # 2. VOLUME CLOCK RESAMPLING (Eager Execution Required for GroupBy)
    # Note: In production, batch this by Day to fit in RAM
    df = q.collect()
    df = df.with_columns(
        (pl.col("Vol").cum_sum() // VOL_BUCKET_SIZE).alias("BucketID")
    )

    # 3. AGGREGATION TO PHYSICS TENSOR
    frames = df.group_by("BucketID").agg([
        pl.col("P_micro").first().alias("Open"),
        pl.col("P_micro").last().alias("Close"),
        pl.col("P_micro").std().alias("Sigma"),
        pl.col("v_OFI").sum().alias("Net_OFI"),
        # Depth Proxy: Average of Bid1+Ask1 Volume
        ((pl.col("BidV1") + pl.col("AskV1"))/2).mean().alias("Depth"),
        # Capture Trace for Epiplexity/TDA
        pl.col("P_micro").alias("Trace"),
        pl.col("v_OFI").cum_sum().alias("OFI_Path")
    ])

    # 4. VECTORIZED MATH KERNELS
    
    # A. Inverse SRL Residuals
    frames = frames.with_columns(
        (
            (pl.col("Close") - pl.col("Open")) - 
            (Y_COEFF * pl.col("Sigma") * (pl.col("Net_OFI").abs() / (pl.col("Depth")+1)).sqrt() * pl.col("Net_OFI").sign())
        ).alias("SRL_Resid")
    )

    # B. Epiplexity (UDF - CPU Bound)
    def calc_epiplexity(trace):
        if len(trace) < 10: return 0.0
        # SAX Symbolization (-1, 0, 1) based on local std
        arr = np.array(trace)
        diff = np.diff(arr)
        scale = np.std(diff) + 1e-9
        symbols = np.zeros_like(diff, dtype=np.int8)
        symbols[diff > 0.5*scale] = 1
        symbols[diff < -0.5*scale] = -1
        
        # Compression Ratio
        b = symbols.tobytes()
        r = len(zlib.compress(b)) / len(b)
        return 4 * r * (1.0 - r)

    frames = frames.with_columns(
        pl.col("Trace").map_elements(calc_epiplexity, return_dtype=pl.Float64).alias("Epiplexity")
    )

    # C. Signed Symplectic Area (Vectorized TDA Proxy)
    # Area = 0.5 * Sum(x_i*y_i+1 - x_i+1*y_i)
    def calc_area(struct):
        p = np.array(struct["Trace"])
        ofi = np.array(struct["OFI_Path"])
        if len(p) != len(ofi): return 0.0
        return 0.5 * np.sum(p[:-1] * ofi[1:] - p[1:] * ofi[:-1])

    frames = frames.with_columns(
        pl.struct(["Trace", "OFI_Path"]).map_elements(calc_area, return_dtype=pl.Float64).alias("Topo_Area")
    )

    # 5. SIGNAL SYNTHESIS
    # Filter: High Structure AND High Physics Anomaly
    signals = frames.filter(
        (pl.col("Epiplexity") > 0.4) & 
        (pl.col("SRL_Resid").abs() > 2.0 * pl.col("Sigma"))
    )
    
    return signals

```

---

## 5. Validation Protocol (Definition of Done)

Execute `validate_model()` after training. The model is accepted **ONLY IF**:

1. **Topological SNR > 3.0**:
* Test: `Mean(Epiplexity_Real)` vs `Mean(Epiplexity_Shuffled)`.
* Structure must be statistically significant.


2. **Orthogonality Check**:
* .
* *Rationale*: Information Structure and Physical Impact must be independent dimensions.


3. **Vector Alignment**:
* Check: Do signals with `Topo_Area > 0` (Accumulation) result in positive forward returns?



**END SPECIFICATION.**