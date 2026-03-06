# LATEST (Authoritative Multi-Agent Snapshot)

> 🚨 **[CRITICAL SYSTEM OVERRIDE - AGENT WAKE-UP DIRECTIVE]** 🚨
> **V64.3 "Bourbaki Completion" patch set is the active release candidate in the local repo!**
> If you are a new AI agent waking up to execute Stage 3 (Base Matrix), Training, or Backtesting, your **IMMEDIATE FIRST ACTION MUST BE to verify code freshness through the controller-managed deploy path**. Use `tools/deploy.py` from the controller, then verify the target worker state through the deploy workflow. **Workers never run `git pull`.**
> The physical L2 parquet files on disk may still contain older `is_signal` semantics from pre-v64.3 runs. The active Python code reconstructs the canonical gate in-memory. **DO NOT run downstream stages until the deployed code state is confirmed on the target node.**
> If you invoke Stage 3 outside the supervisor, you must preserve the canonical in-memory gates exactly (`signal_epi_threshold`, `srl_resid_sigma_mult`, `topo_area_min_abs`, `topo_energy_min`) or call the canonical forge/training entrypoints as scripted.

This file is the single source of current operational truth for all agents.

## 0. Update Contract

- **FIRST ACTION PROTOCOL:** Before taking ANY operational action, you MUST read this file.
- **EXIT CONTRACT:** Before ending any agent session or task, you MUST update this file with the new state. This guarantees flawless handover.
- Do NOT rewrite or delete older sections without reason; append the latest status or clearly mark phases as `[DONE]`.
- Always reference explicit Entry IDs for deep-dives.

---

## 1. Project Phase
**Current Macro Status: V64.3 RELEASE CANDIDATE - FULL SMOKE PASSED, READY FOR COMMIT/PUSH**

The repo-alignment mission is complete. The isolated V64.3 smoke is now green again after the backtest remediation. `Stage 2 -> forge/base_matrix -> training -> backtest` have all passed on `linux1-lx` in the isolated smoke workspace. The next gate is `commit + push`, followed by post-push auditor review. No new full `Stage 2` launch is authorized in this mission.

---

## 2. Global State Matrix

| Track | Task | Sub-Task | Node | Status | Last Checked | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage1-ETL** | Base Parquet Synthesis | Ticks -> Base_L1 | `linux1-lx`,`windows1-w1`,`omega-vm`,`mac` | `[DONE]` | 2026-03-06 07:15 UTC | All four nodes are synced to commit `52c3b62`; both workers have the full `743`-file Stage 1 corpus locally. |
| **Stage2-MATH** | L2 Feature Injection | `kernel.py` & V64 Vectors | `linux1-lx` | `[BLOCKED]` | 2026-03-06 08:00 UTC | Full run remains intentionally stopped. The old `stage2_full_20260306` outputs and ledgers were deleted cleanly by Owner request during v64.2 triage. No relaunch is authorized in this mission. |
| **Stage2-MATH** | L2 Feature Injection | `kernel.py` & V64 Vectors | `windows1-w1` | `[BLOCKED]` | 2026-03-06 08:00 UTC | Full run remains intentionally stopped. The old `stage2_full_20260306` outputs and ledgers were deleted cleanly by Owner request during v64.2 triage. No relaunch is authorized in this mission. |
| **Stage3-BASEMATRIX** | Feature Forging | `forge_base_matrix.py` | `linux1-lx` | `[PENDING]` | - | Will start only after both Stage 2 halves finish and Windows L2 is shadowed/copied back to Linux. |
| **Stage3-BASEMATRIX** | AI Model Training | `run_vertex_xgb_train.py` | GCP / Vertex AI | `[PENDING]` | - | XGBoost (tree_method=hist) with `singularity_vector`. |
| **Stage3-BASEMATRIX** | Local Backtest Evaluation | `evaluate_frames()` | `linux1-lx` | `[DONE]` | 2026-03-06 13:56 UTC | Backtest remediation applied. Isolated V64.3 smoke backtest completed `109/109` batches in `94.19s` and wrote `local_backtest.json`. |

---

## 3. Immediate Next Actions
*(What the next agent should do immediately upon waking up)*

1. **Do not resume or relaunch Stage 2:**
   - The isolated V64.3 smoke is already complete.
   - A future full Stage 2 launch is a separate mission.
2. **Current release gate:**
   - commit the current local tree
   - push to `origin/main`
   - send the pushed tree for post-push auditor review
3. **Preserve the successful smoke evidence:**
   - smoke workspace: `/home/zepher/work/Omega_vNext_v643_smoke`
   - final backtest artifact: `.tmp/smoke_v64_v643/model/local_backtest.json`
4. **Do not reopen the backtest stall scope unless post-push review finds a new blocker.**

---

## 4. Operational Guardrails

- **V64.3 Completion Rule:** Downstream stages must preserve the Bourbaki Completion semantics now live in code: MDL gain is based on `Var(ΔP) / Var(R)` with `Delta k = 0`, `Zero-variance -> zero signal`, `srl_resid` must never be rewritten by `has_singularity`, and no second compression branch may re-enter Stage 3 or later paths.
- **Multi-Threading Constraints:** Always use `os.environ["POLARS_MAX_THREADS"] = str(max(1, os.cpu_count() // 2))` on 128G UMA machines to prevent ZFS ARC IO-thrashing. Linux must run under `heavy-workload.slice`. The same bounded-thread guidance applies to Stage 3 local backtest on `linux1-lx`.

---

## 5. Latest Related Entries (Handover Archive)
*The most recent deep-dive logs available in `handover/ai-direct/entries/`*

- `20260306_074851_stage2_full_run_launch_and_contiguous_smoke` - Four-node sync complete; contiguous-day and wrapper-level smoke passed; full Stage 2 launched on contiguous-half manifests.
- `20260306_094148_v642_dual_audit_and_full_smoke_pass` - V64.2 dual-audit closure finished; full smoke chain passed on `linux1-lx`; no new full Stage 2 launch authorized in this mission.
- `20260306_135658_v643_backtest_remediation_smoke_pass` - Backtest remediation applied; isolated V64.3 smoke passed end-to-end again; ready for commit/push and post-push auditor review.
- `20260306_134038_v643_backtest_stall_triage` - V64.3 isolated smoke reached training, then stalled in local backtest; Stage 2/forge/training preserved as pass evidence; active mission narrowed to backtest remediation.
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

## Update: 2026-03-06 11:35 UTC
- **V64.3 mission active:** the current repo patch is now governed by `audit/v643.md`, exact section `[ SYSTEM ARCHITECT FINAL OVERRIDE: THE BOURBAKI COMPLETION ]`.
- **Repo delta versus V64.2:** canonical `delta_k` removal remains in force; `dominant_probe` is now a compatibility placeholder pinned to `1`; `L2EpiplexityConfig` has been stripped of the old LZ/SAX runtime fields; `README` authority now points to `v643`.
- **Release evidence rule:** the `2026-03-06 09:41 UTC` V64.2 smoke pass remains historical evidence only. It must not be used as release evidence for V64.3.
- **Owner-approved validation exception:** the fresh V64.3 smoke may run on an isolated remote smoke workspace before `commit + push`, because it is validation-only and does not deploy or authorize any live worker repo state.
- **Current release gate:** finish V64.3 dual audit, rerun the full smoke chain (`Stage 2 -> Stage 3 -> base matrix -> training -> backtest`) on the V64.3 code state, then `commit + push`, then post-push auditor review.
- **Operational rule remains unchanged:** do **not** launch a new full Stage 2 run in this mission.

## Update: 2026-03-06 13:40 UTC
- **Stage 2 / forge / training evidence preserved:** the isolated V64.3 smoke on `linux1-lx` has already passed Stage 2, shard forge, base-matrix merge, and local training in `/home/zepher/work/Omega_vNext_v643_smoke`.
- **Backtest blocker identified:** `tools/run_local_backtest.py` entered a no-progress stall during the smoke backtest leg. The run discovered `5409` symbols, built `109` batches, started two workers, then stopped making any forward progress.
- **Runtime diagnosis:** all backtest processes parked in `futex_do_wait`, no `local_backtest.json` was produced, and a 15-second `/proc` delta sample showed zero I/O and zero context-switch movement across the parent and both worker processes.
- **Operational action:** the stalled backtest was stopped. No active `run_local_backtest.py` process remains in the smoke workspace.
- **Active mission narrowed:** the release path is now blocked only by `V64.3 Backtest Stall Remediation and Smoke Completion`. Do not rerun full Stage 2 or rebuild smoke artifacts unless the remediation proves the current base-matrix contract invalid.

## Update: 2026-03-06 13:56 UTC
- **Backtest remediation:** `tools/run_local_backtest.py` now defaults to sequential batch execution; Python multiprocessing is no longer the default local backtest path and remains explicit opt-in only.
- **Runtime hardening:** batch progress logging was added, and the output parent directory is created before writing the final JSON artifact.
- **Targeted audits:** runtime audit `PASS`; V64.3 math invariance audit `PASS`.
- **Backtest rerun:** PASS on `linux1-lx` in `/home/zepher/work/Omega_vNext_v643_smoke`.
  - `109/109` batches completed
  - `n_frames = 891331`
  - `seconds = 94.19`
  - output: `.tmp/smoke_v64_v643/model/local_backtest.json`
- **Mission state:** the isolated V64.3 smoke is now fully green. Next gate is `commit + push`, then post-push auditor review.

## Update: 2026-03-06 14:00 UTC
- **Commit pushed:** `72f7fe9` `fix(v64.3): resolve backtest stall and unify config entry`
- **Post-push runtime review:** `PASS`
- **Post-push Gemini review:** `PASS`
- **Release state:** V64.3 smoke, audits, push, and post-push review are all complete. The repo is no longer blocked by the local backtest stall.
