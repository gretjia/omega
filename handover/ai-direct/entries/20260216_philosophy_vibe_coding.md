# Handover: The GEMINI Protocol (Vibe Coding Philosophy)
**Date:** 2026-02-16
**Source:** Gemini 3 Pro (The Architect)
**Topic:** The "Solo Quant" Operating System

## 1. The Core Axiom: "Vibe Coding"
We are not just writing Python; we are encoding **Market Physics**.
- **Rule 1:** **Compression is Intelligence.** If a strategy cannot be described in 3 sentences or 5 lines of math (`omega_math_vectorized.py`), it is overfitting.
- **Rule 2:** **No Boilerplate.** Use SQL (BigQuery), Cloud APIs (Vertex), and existing libraries (`Polars`, `XGBoost`) to replace thousands of lines of manual Python.
- **Rule 3:** **First Principles.** Code must mirror reality. (e.g., The "Lunch Break" in A-shares isn't just a pause; it's a spacetime fold. Code it as `time_fraction` suspension).

## 2. The Infrastructure: "The Barbell"
We operate a **Hybrid Edge-Cloud Cluster**.
- **The Edge (Left Bell):**
  - **Hardware:** 2x AMD AI Max 395 (128GB Unified Memory).
  - **Role:** The "Physics Forge". Massive ETL, Vectorized Kernel (`kernel.py`), High-Frequency Signal Generation.
  - **Philosophy:** Data Gravity. Move code to data (`linux1`, `windows1`), don't move TBs of data to cloud unless necessary.
- **The Cloud (Right Bell):**
  - **Hardware:** Google Vertex AI + BigQuery.
  - **Role:** The "Oracle". Non-Linear Training (`XGBoost`), Hyperparameter Swarms (`Optuna`).
  - **Philosophy:** Infinite Scale. Spin up 15 workers for 20 minutes to find the truth, then kill them.

## 3. The Math: "Epistemic Physics"
- **Topology (`topo_energy`):** The market has shape. Use TDA (Topological Data Analysis) to find loops (accumulation/distribution).
- **Physics (`srl_resid`):** The market has mass and impact. The Square-Root Law is invariant. Deviations are signals.
- **Entropy (`epiplexity`):** The market is mostly noise. Only trade when entropy collapses (high compressibility).

## 4. Operational "Blood Rules"
1.  **Strict Handover:** Every session MUST end with a commit to `handover/ai-direct/entries/` and an update to `LATEST.md`.
2.  **Manifest Deployment:** Never assume the cloud environment matches local. Explicitly zip `config.py` and `tools/` with your code bundle.
3.  **Data Clocks:** Never use `CURRENT_DATE()` in analytics. Use `MAX(trade_date)`.
4.  **Singularity Masking:** A-Shares have Limit Up/Down. These are black holes where physics breaks. You MUST mask them (`has_singularity`) or your models will explode.

---
**Directive:** Future agents, read this. If you violate the "Vibe", you will fail the "DeepThink Audit".
