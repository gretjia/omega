# OMEGA Constitution: The Mathematical Trinity

> **Supreme Directive**: This document is the Single Source of Truth for all OMEGA Agents.
> All code, strategies, and decisions MUST derive from these First Principles.
> **ECONOPHYSICS SUPERSEDES SWE** — standard software engineering heuristics yield to physics.

---

## Article I: The Trinity (First Principles)

The Market is a complex system defined by three orthogonal dimensions.

### 1. Geometry (TDA — Topological Data Analysis)

- **Principle**: The market has "Shape" and "Structure", not just "Trend".
- We use **Persistent Homology** (Vietoris-Rips) on **Takens' Embedded** Point Clouds.
- A "Loop" ($H_1$) represents energy accumulation or distribution cycles.
- TDA is naturally undirected — use **Signed Area** or **SRL Residuals** for direction.

### 2. Physics (SRL — Square-Root Law)

- **Principle**: The "Gravity" of the market is invariant.
- **Law (Sato 2025)**: $\Delta P \sim \text{Sign}(OFI) \cdot Y \cdot \sqrt{Q/D}$
- **Universal Constant**: $\delta = 0.5$ is a **physical constant**, NOT a hyperparameter.
- **Prohibition**: "Race" logic (testing δ=0.33/0.5/0.66) is pseudoscience and strictly prohibited.
- **State Variable (Y)**: Structural Rigidity — the ONLY free degree of freedom. Dynamic, scales with Epiplexity.

### 3. Information (Epiplexity & MDL)

- **Principle**: Information is "Compression Gain", not just "Complexity".
- **Epiplexity ($\mathcal{E}$)**: $1 - \frac{Var(Residuals_{linear})}{Var(Data_{naive})}$ (Finzi 2026).
- **Entropy ($H$)**: The remaining incompressible noise.
- **Rule**: Trade ONLY when Compression Gain > 0 (Structure Emerging).

---

## Article II: The Four Generative Axioms

These axioms derive all correct engineering decisions from physics.
When facing any engineering challenge, test your solution against these four walls.

### Axiom 1: The Arrow of Time is Sacred (Causality > Memory)

- Financial math (EMA, Cumulative OFI) requires **unbroken causal continuity**.
- ❌ Never chunk/shard across Time to solve OOM. Never use `streaming=True` if it drops window context.
- ✅ All data scaling MUST be **Spatial** — shard by Ticker/Symbol, keep full time-history.

### Axiom 2: Topological Fidelity (Precision > Speed)

- Alpha lives in microscopic SRL residuals. Limit Up/Down are mathematical singularities (Depth→0).
- ❌ Never downcast Float64→Float32. Never `.fillna()` singularities.
- ✅ Use explicit Boolean masking (`is_physics_valid`). Solve RAM via spatial batching.

### Axiom 3: The Edge-Cloud Airgap (Asymmetric Topology)

- ❌ No enterprise bloatware (Dataflow, Vertex Pipelines, Pub/Sub, BigQuery for ETL).
- ✅ **Edge (Local, 128G RAM)**: Exclusive for tensor math + Polars ETL. Raw L2 never leaves Edge.
- ✅ **Cloud (GCP)**: Exclusive for XGBoost swarm optimization via compressed `.parquet` on GCS.

### Axiom 4: Epistemic Slicing (No "Baseline" Poisoning)

- Physics gates (`signal_epi_threshold`, `singularity_threshold`) are NOT ML hyperparameters.
- ❌ Never run "default baselines" on full data. Never re-run Edge ETL for hyperparameter sweeps.
- ✅ Base Matrix on Edge → In-Memory Boolean Masking → XGBoost DMatrix in O(1).

---

## Article III: The Methodology

### 1. Recursion

- There are NO static parameters. Thresholds are functions of distribution (e.g., `quantile(0.95)`).
- Hardcoding `threshold = 0.5` violates this article.

### 2. The Volume Clock

- Physical Time (Wall Clock) is an illusion. All math operates in **Volume Time** (Volume Bars).
- SRL is linear in Volume Time; non-linear in Physical Time.

### 3. Boundary Conditions

- Physics breaks at Limit Up/Down. SRL is undefined at $P \approx Limit$.
- Agent must detect `Regime.BOUNDARY` and suspend normal physics.

---

## Article IV: Settlement & Constraints

### T+1 Settlement

- A **Constraint**, not a Principle. We obey it because the Settlement System enforces it.
- Strategies must calculate `SettlableVolume`. If `SettlableVolume < TradeVolume`, trade is impossible.

### Execution

- Execution cost is Entropy. Minimizing impact minimizes Entropy.

---

## Article V: Configuration & Reproducibility

1. **Immutable Configuration**: `config.py` is the Baseline. Training MUST NOT write back to it.
2. **Artifact-Driven Inference**: Backtest loads `artifacts/omega_policy.pkl`, not raw `config.py`.
3. **Dataset Role Isolation**: Train/Val/Test/Backtest are mutually disjoint by construction.
   - Build role-specific manifests. Enforce overlap checks at runtime.

---

## Article VI: The Physics Audit (Cognitive Chokehold)

Before ANY engineering decision, every agent must answer:

```
<PHYSICS_AUDIT>
1. The SWE Temptation: What standard engineering trick am I tempted to use?
2. The Axiom Clash: How does this trick violate Axiom 1, 2, 3, or 4?
3. The Orthogonal Solution: How to solve using spatial sharding, GC, or masking?
4. Ring 0 Check Passed? (Yes/No)
</PHYSICS_AUDIT>
```

- If **Yes**: Proceed.
- If **No**: `[ARCHITECTURAL ESCALATION REQUIRED] Physical limits reached. Waiting for Architect.`

---

*Signed, The OMEGA Architect — February 2026*
*Merged from Trinity Constitution v1 + Axiomatic Edition v2*
