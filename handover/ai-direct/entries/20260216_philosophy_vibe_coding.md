# Handover: The GEMINI Protocol (Vibe Coding Philosophy)
**Date:** 2026-02-16
**Source:** Gemini 3 Pro (The Architect)
**Context:** Based on `audit/v6.md` (Chief Architect Blueprint)

## 1. The Core Axiom: "Compression is Intelligence" (压缩即智能)
We are not just writing Python; we are encoding **Market Physics**.
- **The Axiom:** The market is mostly random (Max Entropy). When "Main Force" (Smart Money) intervenes, the structure collapses into a low-entropy, compressible manifold.
- **The Metric:** **Epiplexity**. If data compression gain is high, intelligence is present. If compression fails, it is noise. We DO NOT trade noise.
- **The Law:** **Universal SRL (Square-Root Law).** The impact exponent $\delta = 0.5$ is a physical constant, not a parameter. `srl_resid` measures the "Anti-Gravity" force of manipulation.

## 2. The Infrastructure: "The Hybrid Barbell"
We operate a specific Edge-Cloud topology designed for A-Share Hunting.
- **Node A (Brain):** Mac Studio. Command & Control. Risk Management.
- **Node B/C (Forges):** 2x AMD AI Max 395 (128GB Unified Memory).
  - **Task:** Massive Vectorized ETL & Physics Engine (`omega_math_vectorized.py`).
  - **Why:** Zero-copy NumPy tensor math on 128GB RAM is required to process TBs of L2 ticks.
- **Node D (Oracle):** Google Vertex AI + BigQuery.
  - **Task:** Non-Linear Epistemic Training (`XGBoost`).
  - **Why:** To capture the interaction between Topology and Entropy that linear models (`SGD`) miss.

## 3. The Physics: A-Share Specifics
Reality has boundary conditions. Code must match reality.
- **Time Folding:** The 1.5-hour lunch break (11:30-13:00) is a wormhole. Time fraction must pause.
- **Singularity Masking:** Limit Up/Down (10%/20%) are black holes where Depth $\to$ 0. Physics breaks here. We must mask these singularities (`has_singularity`) to prevent infinite residual explosions.
- **T+1 Causality:** Intraday signals must be strong enough to survive the overnight gap.

## 4. Operational "Blood Rules"
1.  **Strict Handover:** Every session MUST end with a commit to `handover/ai-direct/entries/` and an update to `LATEST.md`.
2.  **Manifest Deployment:** Cloud workers are blank slates. Explicitly zip `config.py` and `tools/` with your code bundle.
3.  **Data Clocks:** Never use `CURRENT_DATE()` in analytics. Use `MAX(trade_date)`.
4.  **No Versioned Files:** Do not create `trainer_v60.py`. Refactor `trainer.py` in place. Use Git tags for history.

---
**Directive:** Future agents, align with `audit/v6.md`. This is the blueprint.
