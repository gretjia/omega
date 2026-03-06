# LATEST (Authoritative Multi-Agent Snapshot)

> 🚨 **[CRITICAL SYSTEM OVERRIDE - AGENT WAKE-UP DIRECTIVE]** 🚨
> **V64.1 "Bourbaki Synthesis" Hotfix is LIVE in the codebase!** 
> If you are a new AI agent waking up to execute Stage 3 (Base Matrix), Training, or Backtesting, your **IMMEDIATE FIRST ACTION MUST BE `git pull origin main`** on the target execution node (`linux1-lx` or `windows1-w1`). 
> The physical L2 parquet files on disk contain the V64.0 (flawed) `is_signal` column. The Python code in `main` contains a hotfix that dynamically patches this column in-memory using absolute mathematical closure. **DO NOT run downstream stages without pulling this code first.**

This file is the single source of current operational truth for all agents.

## 0. Update Contract

- **FIRST ACTION PROTOCOL:** Before taking ANY operational action, you MUST read this file.
- **EXIT CONTRACT:** Before ending any agent session or task, you MUST update this file with the new state. This guarantees flawless handover.
- Do NOT rewrite or delete older sections without reason; append the latest status or clearly mark phases as `[DONE]`.
- Always reference explicit Entry IDs for deep-dives.

---

## 1. Project Phase
**Current Macro Status: V64 FULL PIPELINE RUN (The Epistemic Trinity) 🔴 ACTIVE**

We are transitioning from mathematical prototyping into full-scale production. The legacy `epiplexity` has been replaced with `singularity_vector`. No Z-Score, no extreme truncation.

---

## 2. Global State Matrix

| Track | Task | Sub-Task | Node | Status | Last Checked | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage1-ETL** | Base Parquet Synthesis | Ticks -> Base_L1 | Any | `[DONE]` | - | Base data `latest_base_l1` exists on all nodes. |
| **Stage2-MATH** | L2 Feature Injection | `kernel.py` & V64 Vectors | `linux1-lx` | `[RUNNING]` | 2026-03-05 20:30 UTC | Started `stage2_targeted_resume.py` in `heavy-workload.slice`. Processing 552 days for 2023-2026. |
| **Stage2-MATH** | L2 Feature Injection | `kernel.py` & V64 Vectors | `windows1-w1` | `[RUNNING]` | 2026-03-05 20:30 UTC | Started `stage2_physics_compute.py` with 4 workers. Processing 382 days. |
| **Stage3-BASEMATRIX** | Feature Forging | `forge_base_matrix.py` | `linux1-lx` | `[PENDING]` | - | Will start once Stage 2 completes and Windows data is shadowed. |
| **Stage3-BASEMATRIX** | AI Model Training | `run_vertex_xgb_train.py` | GCP / Vertex AI | `[PENDING]` | - | XGBoost (tree_method=hist) with `singularity_vector`. |
| **Stage3-BASEMATRIX** | Local Backtest Evaluation | `evaluate_frames()` | `linux1-lx` | `[PENDING]` | - | Will evaluate trained model on 2025/2026 data. |

---

## 3. Immediate Next Actions
*(What the next agent should do immediately upon waking up)*

1. **Monitor Stage 2 Progress:** 
   - Wait ~30 mins and use Gemini CLI to poll the nodes (`linux1-lx`, `windows1-w1`) to verify `stage2` processes haven't crashed and log files (`audit/stage2_targeted_resume_linux.log` / `audit/stage2_windows.log`) show `__BATCH_OK__` completion messages.
   - If bugs appear during this initial window, halt execution, fix the code natively (preserving V64 mandates), and restart the process via `launch_linux_stage2_heavy_slice.sh` / `powershell`.
2. **Post-Stage 2 Shadowing:**
   - Once Windows completes, transfer the results to Linux (`v64_feature_l2`).
3. **Stage 3 Flow:**
   - Trigger `forge_base_matrix.py` (V64 zero-copy streaming) on Linux, push `base_matrix.parquet` to GCS `gs://omega_central/omega/staging/`.
4. **Train and Backtest:**
   - Run the Vertex XGBoost submitter and the local backtester.

---

## 4. Operational Guardrails

- **V64 Singularity Rule:** We absolutely DO NOT apply Z-Score clipping, normalization, or smooth `NaN` boundaries on the upper bounds. `999.0` represents an epistemic physical singularity.
- **Multi-Threading Constraints:** Always use `os.environ["POLARS_MAX_THREADS"] = str(max(1, os.cpu_count() // 2))` on 128G UMA machines to prevent ZFS ARC IO-thrashing. Linux must run under `heavy-workload.slice`.

---

## 5. Latest Related Entries (Handover Archive)
*The most recent deep-dive logs available in `handover/ai-direct/entries/`*

- `20260305_201500_v64_preflight_smoke_tests` - End-to-end smoke test completed successfully; pipeline updated for `singularity_vector`.
- `20260305_142336_v63_training_backtest_alignment_audit` - Legacy post-mortem on sample collapse and threshold hyper-sensitivity.
- `20260227_104435_stage2_v62_alignment_audit` - Past audit confirming rolling operations compliance.

## Update: 2026-03-06 03:00 UTC
- **V64.1 Hotfix Deployed:** The Bourbaki Synthesis updates (absolute geometric closure, dimension matching, and decoupling of `peace_threshold`) have been propagated downstream to `run_vertex_xgb_train.py` and `trainer.py` (which powers `run_local_backtest.py`). 
- **Methodology:** We compute the new, strict `is_signal_v641` purely in-memory at load time. This ensures total mathematical continuity across the pipeline without stalling or restarting the ongoing, multi-hour Stage 2 runs on Windows and Linux.

## Update: 2026-03-06 03:27 UTC
- **Bourbaki Closure Repo Alignment: PASS** The repository is now aligned to the final `Bourbaki Closure` override in `audit/v64.md`.
- **Canonical runtime semantics are primary:** `signal_epi_threshold`, `brownian_q_threshold`, `topo_energy_min`, `singularity_threshold`.
- **Legacy names survive only as compatibility surfaces:** CLI aliases, resume-context normalization, and explicit `legacy_compat` metadata blocks.
- **Validation:** `py_compile` passed on changed Python files; `uv run --python /usr/bin/python3.11 --with pytest --with numpy==1.26.4 --with numba==0.60.0 pytest tests/test_v64_absolute_closure.py tests/test_omega_math_core.py -q` passed with `32 passed`; external Gemini audit verdict: `PASS`.
- **Operational note:** Stage 2 remains the active runtime track. When Stage 3 starts, use canonical parameter names first and treat old `peace_threshold` / `topo_energy_sigma_mult` names as compatibility aliases only.
