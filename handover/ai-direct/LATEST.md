# LATEST (Authoritative Multi-Agent Snapshot)

> 🚨 **[CRITICAL SYSTEM OVERRIDE - AGENT WAKE-UP DIRECTIVE]** 🚨
> **V64.1 "Bourbaki Synthesis" Hotfix is LIVE in the codebase!**
> If you are a new AI agent waking up to execute Stage 3 (Base Matrix), Training, or Backtesting, your **IMMEDIATE FIRST ACTION MUST BE to verify code freshness through the controller-managed deploy path**. Use `tools/deploy.py` from the controller, then verify the target worker state through the deploy workflow. **Workers never run `git pull`.**
> The physical L2 parquet files on disk contain the V64.0 (flawed) `is_signal` column. The Python code in `main` contains a hotfix that dynamically patches this column in-memory using absolute mathematical closure. **DO NOT run downstream stages until the deployed code state is confirmed on the target node.**
> If you invoke Stage 3 outside the supervisor, you must preserve the V64.1 in-memory hotfix gates exactly (`signal_epi_threshold`, `srl_resid_sigma_mult`, `topo_area_min_abs`, `topo_energy_min`) or call the canonical forge/training entrypoints as scripted.

This file is the single source of current operational truth for all agents.

## 0. Update Contract

- **FIRST ACTION PROTOCOL:** Before taking ANY operational action, you MUST read this file.
- **EXIT CONTRACT:** Before ending any agent session or task, you MUST update this file with the new state. This guarantees flawless handover.
- Do NOT rewrite or delete older sections without reason; append the latest status or clearly mark phases as `[DONE]`.
- Always reference explicit Entry IDs for deep-dives.

---

## 1. Project Phase
**Current Macro Status: V64 STAGE 2 FULL RUN ⏸️ PAUSED FOR AUDIT FINDINGS**

The repo-alignment mission is complete. The active mission is now `V64.2 Closure Finalization, Smoke Validation, and Release`. The full `Stage 2` build remains blocked pending dual-audit completion, smoke-only validation, and release sign-off. The legacy `epiplexity` path remains superseded by `singularity_vector`, and downstream stages must still preserve the V64.1 in-memory closure gates.

---

## 2. Global State Matrix

| Track | Task | Sub-Task | Node | Status | Last Checked | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage1-ETL** | Base Parquet Synthesis | Ticks -> Base_L1 | `linux1-lx`,`windows1-w1`,`omega-vm`,`mac` | `[DONE]` | 2026-03-06 07:15 UTC | All four nodes are synced to commit `52c3b62`; both workers have the full `743`-file Stage 1 corpus locally. |
| **Stage2-MATH** | L2 Feature Injection | `kernel.py` & V64 Vectors | `linux1-lx` | `[BLOCKED]` | 2026-03-06 08:00 UTC | Full run remains intentionally stopped. The old `stage2_full_20260306` outputs and ledgers were deleted cleanly by Owner request during v64.2 triage. No relaunch is authorized in this mission. |
| **Stage2-MATH** | L2 Feature Injection | `kernel.py` & V64 Vectors | `windows1-w1` | `[BLOCKED]` | 2026-03-06 08:00 UTC | Full run remains intentionally stopped. The old `stage2_full_20260306` outputs and ledgers were deleted cleanly by Owner request during v64.2 triage. No relaunch is authorized in this mission. |
| **Stage3-BASEMATRIX** | Feature Forging | `forge_base_matrix.py` | `linux1-lx` | `[PENDING]` | - | Will start only after both Stage 2 halves finish and Windows L2 is shadowed/copied back to Linux. |
| **Stage3-BASEMATRIX** | AI Model Training | `run_vertex_xgb_train.py` | GCP / Vertex AI | `[PENDING]` | - | XGBoost (tree_method=hist) with `singularity_vector`. |
| **Stage3-BASEMATRIX** | Local Backtest Evaluation | `evaluate_frames()` | `linux1-lx` | `[PENDING]` | - | Will evaluate trained model on 2025/2026 data. |

---

## 3. Immediate Next Actions
*(What the next agent should do immediately upon waking up)*

1. **Do not resume Stage 2 yet:**
   - The mission is in v64.2 fix-and-verify mode after the architect and auditor overrides.
   - Do not launch a new full run in this session.
2. **Treat the previous `stage2_full_20260306` run as historical, not resumable:**
   - The old run roots and ledgers were intentionally deleted cleanly on controller, Linux, and Windows by Owner request.
   - Any future full Stage 2 run must start from a fresh manifest and fresh output roots after the current code path is signed off.
3. **Current gate order is fixed:**
   - finish v64.2 code triage
   - pass dual audit
   - rerun the full v64 smoke chain from `Stage 2 -> Stage 3 -> base matrix -> training -> backtest`
   - only then consider `git commit + push`
4. **Do not relaunch Stage 2 after smoke in this mission:**
   - The Owner explicitly requested smoke-only validation after dual audit.
   - A future run decision is separate and must start from a clean launch plan.

---

## 4. Operational Guardrails

- **V64.1 Closure Rule:** Downstream stages must preserve the Bourbaki Closure semantics now live in code: MDL gain is based on `Var(ΔP) / Var(R)`, `Zero-variance -> zero signal`, and the old `999.0` pseudo-singularity must not be reintroduced into Stage 3 or later paths.
- **Multi-Threading Constraints:** Always use `os.environ["POLARS_MAX_THREADS"] = str(max(1, os.cpu_count() // 2))` on 128G UMA machines to prevent ZFS ARC IO-thrashing. Linux must run under `heavy-workload.slice`. The same bounded-thread guidance applies to Stage 3 local backtest on `linux1-lx`.

---

## 5. Latest Related Entries (Handover Archive)
*The most recent deep-dive logs available in `handover/ai-direct/entries/`*

- `20260306_074851_stage2_full_run_launch_and_contiguous_smoke` - Four-node sync complete; contiguous-day and wrapper-level smoke passed; full Stage 2 launched on contiguous-half manifests.
- `20260306_094148_v642_dual_audit_and_full_smoke_pass` - V64.2 dual-audit closure finished; full smoke chain passed on `linux1-lx`; no new full Stage 2 launch authorized in this mission.
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

## Update: 2026-03-06 05:20 UTC
- **Dual Audit: PASS** Final Bourbaki Closure repo alignment passed both math and engineering audit.
- **Math audit verdict:** `PASS` via `gemini -y`, including downstream verification that `trainer._prepare_frames`, `forge_base_matrix.py`, `run_vertex_xgb_train.py`, and `LATEST.md` remain aligned to the final `Bourbaki Closure`.
- **Engineering audit verdict:** `PASS` on the Stage 2 onward release path after closing the last blockers:
  - `configs/node_paths.py` now points Stage 3 defaults at `latest_feature_l2`
  - `forge_base_matrix.py` preserves `is_energy_active` and `spoof_ratio` for downstream V64.1 reconstruction
  - `trainer._prepare_frames` rebuilds V64.1 `is_signal` before structural filtering, preventing stale on-disk V64.0 gate leakage into backtest/training prep
  - `stage3_full_supervisor.py` keeps explicit `train_years` / `backtest_years` separation with overlap fail-fast
- **Operational release note:** Do not interrupt running Stage 2 jobs. Use controller-side `tools/deploy.py` to propagate this repo state before any Stage 3 / training / backtest action.

## Update: 2026-03-06 07:48 UTC
- **Four-node sync: PASS.** `omega-vm`, `mac`, `linux1-lx`, and `windows1-w1` are aligned to commit `52c3b62`.
- **Corpus readiness: PASS.** Both workers hold the same full `743`-file Stage 1 corpus locally (`552` original Linux files + `191` original Windows files).
- **Continuous smoke gate: PASS.**
  - Linux passed an end-to-end `Stage 2 -> Stage 3 -> base matrix -> training -> backtest` smoke using the real production `tools/stage2_targeted_resume.py` wrapper and a **strict contiguous 5-day block** (`20230103` -> `20230109`).
  - Required V64 columns were verified in both L2 and base matrix outputs.
  - Windows passed a Stage 2 wrapper probe on `20240717_b07c2229.parquet`, producing `__BATCH_OK__` in `96.0s`.
- **Full Stage 2 launched.**
  - `linux1-lx`: contiguous first half, `371` files, `20230103_fbd5c8b.parquet -> 20240716_fbd5c8b.parquet`
  - `windows1-w1`: contiguous second half, `372` files, `20240717_b07c2229.parquet -> 20260130_fbd5c8b.parquet`
  - This split intentionally preserves temporal continuity within each worker's assigned range and keeps manual takeover simple.
- **Run roots (authoritative for this run):**
  - Linux input: `/omega_pool/parquet_data/stage2_full_20260306/input_linux1`
  - Linux output: `/omega_pool/parquet_data/stage2_full_20260306/l2/host=linux1`
  - Windows input: `D:\\Omega_frames\\stage2_full_20260306\\input_windows1`
  - Windows output: `D:\\Omega_frames\\stage2_full_20260306\\l2\\host=windows1`

## Update: 2026-03-06 08:00 UTC [SUPERSEDED BY 08:35 UTC CLEAN-DELETE OVERRIDE]
- **Run state changed from RUNNING to PAUSED.** The Owner requested an immediate stop after an auditor surfaced additional issues.
- **Pause state is clean:**
  - `linux1-lx`: service stopped, `2` `.done` files retained, `0` fail ledger entries
  - `windows1-w1`: runner processes stopped, `10` `.done` files retained, `0` fail ledger entries
- **Important:** The run-specific manifests, logs, and outputs under `stage2_full_20260306` are now the authoritative resume point. Do not delete or overwrite them before triage.

## Update: 2026-03-06 08:35 UTC
- **Owner override applied:** the paused `stage2_full_20260306` outputs, ledgers, and local controller mirrors were deleted cleanly during v64.2 triage. The previous pause-state resume contract is no longer active.
- **Current mission mode:** fix the v64.2 closure path, pass dual audit, then rerun the full v64 smoke chain (`Stage 2 -> Stage 3 -> base matrix -> training -> backtest`) on the corrected code.
- **Release discipline:** after smoke passes, `commit + push` first; send the updated state to the auditor after the push; do **not** launch a new full Stage 2 run in this mission.

## Update: 2026-03-06 09:41 UTC
- **Math audit:** PASS on the V64.2 closure path.
- **Engineering blockers closed before release:** restored active `tools/multi_dir_loader.py`, hardened stale-`.done` handling in `tools/stage2_targeted_resume.py`, added Stage 2 control-plane regression coverage, and made the kernel smoke gate collectable under pytest.
- **Full V64 smoke chain:** PASS on `linux1-lx` using a remote smoke workspace rooted at `/home/zepher/work/Omega_vNext_v642_smoke`.
  - `Stage 2`: wrapper-level smoke passed on a real contiguous 5-day Stage 1 block (`20230320` -> `20230324`) with full L2 schema gates.
  - `Stage 3 / base matrix`: PASS with `base_rows=924489`, `symbols_total=5409`, `worker_count=1`.
  - `Training`: PASS with model output `omega_xgb_final.pkl`.
  - `Local backtest`: PASS with output `audit/runtime/v642_full_smoke/local_backtest.json`.
- **Mission state:** ready for `commit + push`, then post-push auditor review.
- **Operational rule remains unchanged:** do **not** launch a new full Stage 2 run in this mission.
