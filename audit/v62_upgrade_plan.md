# OMEGA V62 Comprehensive Upgrade Plan (Maestro/Orchestrator Blueprint)

**Date:** 2026-02-22
**Status:** DRAFT (Planning Phase)
**Goal:** Execute the V62 "From Heuristics to Rigorous MDL" upgrade and the "Anti-Fragile Framing" architectural overhaul, broken down into strictly bounded context phases for safe AI-Partner execution.

---

## The Core Philosophy (First Principles)

The V62 upgrade addresses two lethal bottlenecks discovered during V61:

1. **Engineering Disaster**: The framing pipeline coupled raw I/O (7z extraction) with heavy CPU math (MDL, SRL), triggering Python GIL death and ZFS NVMe deadlocks, resulting in 72-hour execution times.
2. **Mathematical Disaster**: The Optuna Swarm collapsed the dataset into 2000 over-fitted noise vectors because the `R_squared` epiplexity metric rewarded raw fit without penalizing model complexity (inviting "Dataset Collapse").

## Phased Execution Strategy

To ensure absolute safety and prevent LLM Context Collapse during code generation, the upgrade MUST be executed in these isolated phases. **Each phase must be committed and verified before proceeding to the next.**

---

### PRE-EXECUTION AUDIT PHASE: The Multi-Agent Audit Protocol (Maestro Directive)

Before a single line of V62 code is executed, the Orchestrator MUST dispatch the following specialized agent workflows to rigorously audit this blueprint:

1. **The Mathematical Audit (`Gemini 3.1 Pro - Principal Quant`)**:
   - **Role:** Deep theoretical scrutiny.
   - **Task:** Review `audit/v62.md`, `omega_core/omega_math_core.py`, and PHASE 1 & 5 of this blueprint.
   - **Mandate:** Prove that the `- (delta_k / 2.0) * np.log(N)` term correctly penalizes spurious noise, and ensure `N < 3` and the `0.9999` `R_squared` clip create a mathematically sound Time-Bounded Minimum Description Length (MDL).

2. **The Engineering & Compute Audit (`Execution Codex Fleet - Distributed Systems Engineers`)**:
   - **Role:** High-concurrency I/O and hardware constraint validation.
   - **Task:** Review `audit/v62_framing_rebuild.md`, `handover/COSTLY_LESSONS.md`, and PHASE 2, 3, 4, 6 of this blueprint.
   - **Mandate:** Verify that the Two-Stage Framing (RAM Disk bypass), the Numba `@njit` GIL eradication, and the heavy trace-dropping (`ofi_list`) memory guardrails are technically viable on the target hardware (128GB Mac/Linux, `n2-highmem-80` GCP).

3. **The Supreme Aggregation (`Gemini 3.1 Pro - Chief Auditor`)**:
   - **Role:** Final Go/No-Go Decision Maker.
   - **Task:** Collect the independent reports from the Mathematical and Engineering unities. Consolidate any fatal flaws or structural leaks into a singular final report, and inject any necessary course corrections back into this `v62_upgrade_plan.md` document before giving the absolute green light for Phase 0 execution.

---

### PHASE 1: The Epistemic Math Upgrade (Strictly `omega_math_core.py`)

**Focus:** Eradicate the Optuna target collapse by formalizing Time-Bounded MDL.
**Context Required:** `omega_core/omega_math_core.py`, `audit/v62.md`
**Actions:**

- [ ] Refactor `calc_compression_gain` to compute **MDL Gain (Bits Saved)** using the BIC formulation: `-(N / 2.0) * np.log(1.0 - np.clip(R_squared, 0.0, 0.9999)) - (delta_k / 2.0) * np.log(N)`
- [ ] Enforce Turing discipline: If `N < 3` or `MDL Gain <= 0`, strictly return `0.0`.
- [ ] Validate unit tests for math core stability.

### PHASE 2: The Data Layer Orthogonal Decoupling (Strictly Framing Scripts)

**Focus:** Split the monolithic 72-hour framing job into a `Two-Stage Pipeline`.
**Context Required:** `tools/v61_linux_framing.py`, `tools/v61_windows_framing.py`, `audit/v62_framing_rebuild.md`
**Actions:**

- [ ] Create **Stage 1 (Base Lake)**: Extract 7z -> Parse CSV -> Clean Timestamps -> Write `Base_L1.parquet`. (Strictly NO physics math). Implement RAM-Disk / 4TB NVMe cache bypass. *(Codex Correction: /dev/shm is Linux-only and finite. Must implement fallback to robust local NVMe temp dirs for macOS compatibility).*
- [ ] Create **Stage 2 (Physics Engine)**: Read `Base_L1.parquet` into memory *(Codex Correction: DO NOT load full universe into memory simultaneously. Must implement symbol-batch or chunked lazy-loading)* -> Apply V62 Mathematics (MDL, SRL, Topo) -> Write `Feature_L2.parquet`.

### PHASE 3: Eradicate Python GIL via Numba JIT (Strictly `omega_math_core.py` & Stage 2)

**Focus:** Unleash the AMD 32-core physical processors using LLVM compilation.
**Context Required:** `omega_core/omega_math_core.py`, `stage2_physics_compute.py`, `audit/v62_framing_rebuild.md`
**Actions:**

- [ ] Strip Polars `.apply()` and `.map_elements()` from the Stage 2 physics engine.
- [ ] Rewrite core physics aggregations using pure NumPy arrays mapped to `@numba.njit(parallel=True, fastmath=True)`. *(Chief Auditor Note: explicitly enforce contiguous `.to_numpy()` before Numba handoff to avoid object pointer overhead).*
- [ ] Ensure list-columns (`ofi_list`, etc.) are eliminated from DataFrames, using `numpy.lib.stride_tricks.sliding_window_view` for rolling topological matrices.

### PHASE 4: Event-Time Manifold Corrections (Strictly `omega_etl.py`)

**Focus:** Fix the "Time ruler distortion" where tick-count rolling means corrupted physical time during market frenzy/dead-zones.
**Context Required:** `omega_core/omega_etl.py`, `audit/v62_framing_rebuild.md`
**Actions:**

- [ ] Migrate all naive `rolling_mean(window_size=N)` physics filters.
- [ ] Implement STRICT temporal rolling: `.rolling(index_column="timestamp", period="Ns", closed="left")`. *(Chief Auditor Note: `closed="left"` is mathematically critical here to prevent microsecond look-ahead bias during high-frequency volatility).*

### PHASE 5: The "Dynamic Model Arena" (Optional / Advanced Edge)

**Focus:** Real-time reverse compilation of the dominant market force.
**Context Required:** `omega_core/omega_math_core.py`, `omega_core/omega_etl.py`
**Actions:**

- [ ] Implement the parallel MDL competition: Calculate $Bits_{Linear}$, $Bits_{SRL}$, $Bits_{Topology}$ simultaneously. *(Chief Auditor Note: Strict NaN forward-filling must be enforced across all three probe vectors before comparison, otherwise argmax will hallucinate).*
- [ ] Select the dominant theoretical probe at microsecond $t$ based on $\text{argmax}(Bits\_Saved)$.

### PHASE 6: The Handover Defense (Anti-Fragile Cloud Guards)

**Focus:** Implement strict cost and memory guardrails extracted from historical OOMs and cloud burn events (`handover/COSTLY_LESSONS.md`).
**Context Required:** `tools/run_cloud_backtest.py`, `tools/run_vertex_xgb_train.py`, `omega_core/trainer.py`
**Actions:**

- [ ] **Memory Defenses:** Ensure heavy trace columns (`ofi_list`, `vol_list`, `time_trace`) are explicitly dropped before ML sorting/preparation to prevent `n2-highmem-80` OOMs. *(Codex Correction: Add explicit trace caps and canary gates before blind full-universe load).*
- [ ] **Preflight Schema Contract:** Dynamically resolve causal time keys (`time | time_end | bucket_id`) to prevent deterministic cloud crashes. *(Codex Correction: Never auto-restart a JOB_STATE_FAILED task. Halt and diagnose.)*
- [ ] **Physics Reuse:** Enforce `reuse_precomputed_physics=true` down the pipeline so the backtester doesn't recompute what Phase 2 just generated.
- [ ] **Data Gravity:** Hardcode environment checks to ensure compute spins up exclusively in `us-central1` matching `gs://omega_v52_central`.

---

## Orchestrator Directives for Execution Bots

When assigning a Phase to an execution AI, provide **ONLY** the "Context Required" files for that specific phase. This strict context scoping guarantees 0-hallucination code generation and localized commits.
