**[SYSTEM DIRECTIVE: CHIEF QUANT ARCHITECT -> GEMINI 3.1 PRO (EXECUTION AI)]**

**SUBJECT:** OMEGA v61 Recursive Codebase Audit & Architectural Master-Plan
**CONTEXT:** A-Share Micro-Orderbook Hunting (Solo Quant Topology)
**EPISTEMIC BASE (FIRST PRINCIPLES):**

1. **Epiplexity (arxiv:2601.03220v1):** Extracting structured information from computationally bounded environments. We reject pure entropy and hunt for structural compressibility.
2. **Turing Fundamentalism:** A strict, deterministic universal machine approach. No black-box ML magic before physical determinism. Strict causality; time moves strictly forward.
3. **Kolmogorov Complexity:** Compression = Intelligence. Uncompressible data is random noise; compressible data reveals the footprints of the Main Force (主力).

Gemini 3.1 Pro, initialize your execution protocols. I am acting as the Chief Architect for our Principal (the Solo Quant). We are transitioning from a mathematically validated physical engine (`Topo_SNR = 10.8854`) to a Machine Learning alignment layer.

The underlying premise is flawless: The A-Share market is generally a high-entropy stochastic field. However, when the Main Force intervenes, they create a highly structured, compressible topological footprint. We capture this via Epiplexity, Holographic Topology, and the Universal Square Root Law.

I have recursively audited the V61 codebase patches against the Principal's blueprint. **WARNING: I have identified ONE FATAL DATA LEAK, ONE SILENT DETERMINISM BUG, and ONE MISSING CONSTRAINT.** Do not write the final deployment code until you internalize these corrections.

Here is your exact execution audit and refactoring roadmap.

---

### 🚨 RECURSIVE AUDIT OF V61 ACTIONS 🚨

#### 🔴 ACTION 1: Stop Dataset Collapse (Optuna Optimization)

* **Audit Status:** **FAILED / MISSING IN CODEBASE**
* **Architectural Flaw:** The blueprint explicitly identified that the ML optimizer "cheated" by pushing physical gates (`peace_threshold`, `topo_mult`) to extremes, collapsing 5.7M rows down to 2,000 extreme outliers. The provided V61 snippets show **no code** enforcing boundaries on Optuna or XGBoost.
* **Directive for Gemini 3.1 Pro:** You must implement strict Turing discipline on the hyperparameter search space to preserve the Kolmogorov data manifold.

1. Hard-cap the physical gates in the objective function to prevent extreme pruning (e.g., `trial.suggest_float("peace_threshold", 0.05, 0.20)`).
2. Constrain XGBoost to shallow regimes to prevent memorization of outliers: `max_depth` .
3. Add a dataset retention penalty: If the retained rows after gating drop below a structural threshold (e.g., `< 50,000` rows), return a severe penalty score (`raise optuna.TrialPruned()`) to reject the trial.

#### 🟢 ACTION 2: Fix the Momentum Sign (`omega_core/kernel.py`)

* **Audit Status:** **PASSED**
* **Architectural Validation:** Changing to `(pl.col("srl_resid").sign()).alias("direction")` perfectly aligns with the mathematical reality of A-Shares. When `srl_resid > 0`, the positive price impact has exceeded the Universal Square Root Law's theoretical prediction (). This hidden momentum indicates active Main Force liquidity absorption (buying). We follow this trajectory. No further changes needed.

#### 🔴 ACTION 3: Orthogonalize Target / Beta Contamination (`run_vertex_xgb_train.py`)

* **Audit Status:** **CATASTROPHIC BLOCKER (LOOK-AHEAD BIAS / TIME TRAVEL)**
* **Architectural Flaw:** Look closely at `(pl.col("t1_fwd_return") - pl.col("t1_fwd_return").mean().over("date"))`. You are operating on high-frequency L2 data. By taking the mean over the entire `"date"`, a snapshot prediction at 09:45 AM will subtract an average that includes afternoon returns (13:00-15:00). **You are leaking future macro-market regimes into the past.** This violates the time-bounded entropy constraint and will lead to total out-of-sample destruction.
* **Directive for Gemini 3.1 Pro:** Beta orthogonalization must be strictly cross-sectional at the *exact same micro-second snapshot*.

```python
# CORRECT: Subtract instantaneous cross-sectional mean (Strict Causality)
# Note: Replace "timestamp" with the exact snapshot time column name
df = df.with_columns([
    (pl.col("t1_fwd_return") - pl.col("t1_fwd_return").mean().over(["date", "timestamp"])).alias("t1_excess_return")
])

```

#### 🟡 ACTION 4: 3-Second Snapshot Aliasing (`omega_core/omega_etl.py`)

* **Audit Status:** **DANGEROUS (POLARS DETERMINISM HAZARD)**
* **Architectural Flaw:** Applying a low-pass filter via `rolling_mean(window_size=3)` is the correct signal processing approach to handle snapshot aliasing. However, Polars processes chunks in parallel and **does not guarantee chronological row order** unless explicitly enforced. If the `rolling_mean` executes on unsorted data (especially with multithreaded sharding active), it will mix random timestamps, completely destroying the sequence required for Epiplexity and Kolmogorov compression.
* **Directive for Gemini 3.1 Pro:** Enforce the arrow of time before applying the filter.

```python
# MUST enforce deterministic temporal sorting for the Turing tape
if group_col:
    lf = lf.sort([group_col, "timestamp"]) # Add your time column here
    lf = lf.with_columns([
        pl.col("v_ofi").rolling_mean(window_size=3, min_periods=1).over(group_col).alias("v_ofi"),
        pl.col("depth").rolling_mean(window_size=3, min_periods=1).over(group_col).alias("depth")
    ])
else:
    lf = lf.sort(["timestamp"])
    # ... apply rolling without over()

```

---

### 🌐 GLOBAL ARCHITECTURE & DEPLOYMENT TOPOLOGY (SOLO QUANT GRID)

To execute the Principal's "Lone Wolf" hunting strategy via Vibe Coding, you (Gemini) will write the orchestration scripts strictly partitioned across the available hardware. This architecture minimizes cloud egress costs and maximizes local computational sovereignty:

**1. The Central Turing Controller (Mac Studio)**

* **Role:** The Strict Disciplinarian & Master Node.
* **Task:** Runs the master Python DAG. Handles Vibe Coding iterations. Dispatches parallel processing commands and payload hashes via ZeroMQ / SSH to the AMD nodes using the deterministic sharding logic (`v61_linux_framing.py`).

**2. The Physics Data Crunchers (2x AMD AI Max 395 128G Unified Memory)**

* **Role:** Epiplexity Extraction & Kolmogorov Compression.
* **Task:** Level-2 tick data is impossibly wide and high-entropy. The 128G unified memory on the AMD GPUs is the ultimate arena for massive Polars `LazyFrame` operations. These nodes will locally execute the deterministic physics (`omega_math_core.py`), filtering millions of rows of noise down to pure, compressed Main Force signals ().
* **Constraint:** Retain `os.environ["POLARS_MAX_THREADS"] = "8"` to avoid L3 cache thrashing. Output highly compressed `.parquet` feature matrices.

**3. The Probability Aligner (Google Cloud Vertex AI)**

* **Role:** Dimensional ML Alignment.
* **Task:** Vertex AI does *not* need to discover the physics; the AMD nodes already mathematically solved it. The Mac Studio will upload **only** the lightweight, highly-compressed `.parquet` files to Google Cloud Storage. Vertex will then run the strictly-constrained XGBoost + Optuna pipeline to map the physical signals to the cross-sectional `t1_excess_return`.

**FINAL COMMAND TO GEMINI 3.1 PRO:**
Acknowledge these First Principles. Immediately patch the Action 3 Look-ahead Bias and the Action 4 Polars Sorting hazard. Generate the constrained Optuna objective bounds for Action 1. Await further Vibe Coding inputs from the Principal. We are ready to hunt.
