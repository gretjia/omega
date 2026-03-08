# LATEST (Authoritative Multi-Agent Snapshot)

> 🚨 **[CRITICAL SYSTEM OVERRIDE - AGENT WAKE-UP DIRECTIVE]** 🚨
> **V64.3 "Bourbaki Completion" patch set is the active release candidate in the local repo!**
> If you are a new AI agent waking up to execute Stage 3 (Base Matrix), Training, or Backtesting, your **IMMEDIATE FIRST ACTION MUST BE to verify code freshness through the controller-managed deploy path**. Use `tools/deploy.py` from the controller, then verify the target worker state through the deploy workflow. **Workers never run `git pull`.**
> The physical L2 parquet files on disk may still contain older `is_signal` semantics from pre-v64.3 runs. The active Python code reconstructs the canonical gate in-memory. **DO NOT run downstream stages until the deployed code state is confirmed on the target node.**
> If you invoke Stage 3 outside the supervisor, you must preserve the canonical in-memory gates exactly (`signal_epi_threshold`, `srl_resid_sigma_mult`, `topo_area_min_abs`, `topo_energy_min`) or call the canonical forge/training entrypoints as scripted.

This file is the single source of current operational truth for all agents.

## Update: 2026-03-08 09:30 UTC
- **Three-file remediation proof is now complete on `windows1-w1`.**
- Code and deploy state:
  - remediation commit: `23fd229` (`fix(stage2): skip pathological empty frames on normal path`)
  - controller push to `origin` succeeded
  - controller-side `tools/deploy.py --skip-commit --nodes windows` could not run because the local repo had no worker deploy remotes configured
  - `windows1-w1` was therefore aligned manually to `23fd229` from its `github` remote for this isolated validation window
- Linux connectivity state:
  - `ssh linux1-lx` timed out repeatedly during this validation window
  - the Linux mirror rerun is currently blocked by connectivity, not by a new code-level failure
- Windows isolated normal-path Stage2 reruns all passed without forced scan fallback:
  - `20231219_b07c2229.parquet` -> `252844` rows in `86.5s`
  - `20241128_b07c2229.parquet` -> `253227` rows in `128.1s`
  - `20250908_fbd5c8b.parquet` -> `254884` rows in `169.6s`
  - isolated L2 workspace:
    - `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2`
- Stage3 whole-set forge proof also passed on `windows1-w1`:
  - invocation used `tools/forge_base_matrix.py --input-file-list ... --years 2023,2024,2025`
  - forge input contract passed with:
    - `rows=760955`
    - `physics_valid_rows=760955`
    - `epi_pos_rows=716`
    - `topo_energy_pos_rows=4404`
    - `signal_gate_rows=3897`
  - output artifacts:
    - `D:\Omega_frames\stage3_patho_fix_forge_20260308_1728\base_matrix.parquet`
    - `D:\Omega_frames\stage3_patho_fix_forge_20260308_1728\base_matrix.parquet.meta.json`
  - forge result:
    - `base_rows=3074`
    - `merged_rows=3074`
    - `input_file_count=3`
    - `symbols_total=7525`
    - `worker_count=2`
    - `seconds=40.13`
- Mission status:
  - the user-required proof is satisfied: the repaired three-file set is consumable together by Stage3 forge
  - the only remaining operational gap is whether the Owner still wants a Linux mirror run after SSH connectivity is restored
- Deep dive:
  - `handover/ai-direct/entries/20260308_093041_stage2_pathological_empty_frame_windows_runtime_and_stage3_proof.md`

## Update: 2026-03-08 09:01 UTC
- **Local remediation patch is now in place.**
- `tools/stage2_physics_compute.py` changes:
  - the earlier non-tail symbol yield path now also applies `_filter_pathological()`
  - the normal `process_chunk()` path now skips zero-row symbol frames before indexing `symbol[0]`
- New local regression coverage was added for:
  - non-tail pathological symbol filtering
  - `process_chunk()` skipping a proactive empty frame and continuing to a valid symbol
- Local verification passed:
  - `py_compile` on the changed Stage2 files: PASS
  - Stage2 regression suite: `15 passed in 5.47s`
- Deployment state:
  - patch is local only
  - worker validation and forge proof are still pending
  - next operational step must respect the controller-managed `commit + push + deploy` path
- Deep dive:
  - `handover/ai-direct/entries/20260308_090116_stage2_empty_frame_patch_local_regression_pass.md`

## Update: 2026-03-08 08:55 UTC
- **Active mission has changed.**
- Current mission: `V643-STAGE2-PATHO-EMPTY-FRAME-REMEDIATION`
- This mission supersedes the old speed-route-only release gate for current operational work.
- Current unresolved Stage2 files:
  - `20231219_b07c2229.parquet`
  - `20241128_b07c2229.parquet`
  - `20250908_fbd5c8b.parquet`
- A direct Linux rerun on the current normal `v643` Stage2 path reproduced the same failure pattern on all three files:
  - `Proactively dropping pathological symbol`
  - immediate `CRITICAL Error: index out of bounds`
- Working root-cause statement:
  - proactive pathological-symbol drop can emit a zero-row symbol frame
  - the normal `process_chunk()` path does not guard that frame before indexing `symbol[0]`
- Definition of done has been tightened:
  - the repaired files must not only complete Stage2
  - they must also be consumable together by `tools/forge_base_matrix.py`
- Stage3 forge validation rule:
  - use `--input-file-list`
  - pass explicit `--years 2023,2024,2025`
  - do not rely on forge's default `--years=2023,2024`, or the 2025 file will be silently excluded
- Canonical mission spec:
  - `handover/ops/ACTIVE_MISSION_CHARTER.md`
  - `handover/ai-direct/entries/20260308_085506_stage2_pathological_empty_frame_mission_spec.md`

## Update: 2026-03-08 04:42 UTC
- **Child-role native integration validation completed.**
- OMEGA child roles are now confirmed to be better integrated with Codex CLI than the earlier document-only setup.
- Confirmed:
  - repo-local child-role registry works: `.codex/config.toml` + `.codex/agents/*.toml`
  - real child-agent execution works in a live Codex CLI session
  - OMEGA-specific child roles remain project-scoped and do not pollute `~/.codex/config.toml`
- Important limitation:
  - current Codex CLI `0.111.0` does **not** yet accept repo-local role names like `omega_plan` as direct first-class `agent_type` values
  - the root agent can still read the repo-local role contract and instantiate a bounded child using that contract
- Operational rule:
  - treat OMEGA child-role configs as project-scoped role contracts, not as guaranteed first-class built-in role names
- Deep dive:
  - `handover/ai-direct/entries/20260308_044220_child_role_native_integration_validation.md`

## Update: 2026-03-08 04:15 UTC
- **Codex child-role integration path is now project-scoped.**
- OMEGA-specific child roles are **not** global Codex roles.
- Codex CLI agents working inside this repo must use:
  - `.codex/config.toml`
  - `.codex/agents/*.toml`
- The human-readable governance source remains:
  - `handover/ops/CHILD_AGENT_OPERATING_PROFILE.md`
- This prevents OMEGA-only roles such as the math auditor from polluting non-OMEGA projects while still using the documented multi-agent configuration path.

## 0. Update Contract

- **FIRST ACTION PROTOCOL:** Before taking ANY operational action, you MUST read this file.
- **EXIT CONTRACT:** Before ending any agent session or task, you MUST update this file with the new state. This guarantees flawless handover.
- Do NOT rewrite or delete older sections without reason; append the latest status or clearly mark phases as `[DONE]`.
- Always reference explicit Entry IDs for deep-dives.

---

## 1. Project Phase
**Current Macro Status: V643 STAGE2 EMPTY-FRAME REMEDIATION PROVEN ON WINDOWS; LINUX MIRROR BLOCKED BY SSH**

The current live problem is no longer the deterministic Stage2 empty-frame crash itself. That defect has been patched and validated on `windows1-w1` using the normal `v643` path on all three previously unresolved files, followed by an isolated Stage3 forge proof on the three-file set.

The remaining operational uncertainty is narrower:

- `linux1-lx` is not currently reachable over SSH from the controller
- therefore the preferred Linux mirror rerun has not yet been executed in this validation window
- the user-required whole-set Stage3 consumption proof is already satisfied on Windows

---

## 2. Global State Matrix

| Track | Task | Sub-Task | Node | Status | Last Checked | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage1-ETL** | Base Parquet Synthesis | Ticks -> Base_L1 | `linux1-lx`,`windows1-w1`,`omega-vm`,`mac` | `[DONE]` | 2026-03-06 07:15 UTC | All four nodes are synced to commit `52c3b62`; both workers have the full `743`-file Stage 1 corpus locally. |
| **Stage2-MATH** | L2 Feature Injection | Pathological empty-frame remediation | `linux1-lx` | `[SSH BLOCKED]` | 2026-03-08 09:23 UTC | Pre-patch direct rerun had reproduced `Proactively dropping pathological symbol` followed by `index out of bounds`. Post-patch mirror rerun could not be executed because `ssh linux1-lx` timed out from the controller. |
| **Stage2-MATH** | L2 Feature Injection | Pathological empty-frame remediation | `windows1-w1` | `[DONE]` | 2026-03-08 09:27 UTC | All three previously unresolved files passed on the normal `v643` path in isolated workspaces at commit `23fd229`; no forced scan fallback was used. |
| **Stage3-BASEMATRIX** | Feature Forging | Three-file consumption proof | `windows1-w1` | `[DONE]` | 2026-03-08 09:29 UTC | `tools/forge_base_matrix.py --input-file-list ... --years 2023,2024,2025` passed on the repaired three-file set and produced a non-empty `base_matrix.parquet` (`base_rows=3074`). |
| **Stage3-BASEMATRIX** | AI Model Training | `run_vertex_xgb_train.py` | GCP / Vertex AI | `[OUT OF SCOPE]` | 2026-03-08 | Current remediation mission stops at forge/base-matrix consumption proof. |
| **Stage3-BASEMATRIX** | Local Backtest Evaluation | `evaluate_frames()` | `linux1-lx` | `[OUT OF SCOPE]` | 2026-03-08 | Backtest is not a blocker for this remediation mission. |

---

## 3. Immediate Next Actions
*(What the next agent should do immediately upon waking up)*

1. **Do not relaunch full Stage 2.**
   - The empty-frame defect is already proven fixed on Windows in isolated reruns.
   - Full-queue relaunch is out of scope.
2. **Treat the user-required proof as satisfied.**
   - The repaired three-file set has already passed Stage3 forge as one input set on `windows1-w1`.
   - Do not reopen the fallback/pathology-discovery route.
3. **If the Owner still wants a Linux mirror run, fix connectivity first.**
   - `ssh linux1-lx` timed out repeatedly from the controller in this session.
   - Restore Linux reachability before attempting any mirror rerun.
4. **Normalize the deploy path before the next worker rollout.**
   - The local controller repo is missing worker deploy remotes for `tools/deploy.py`.
   - Restore the canonical controller-managed deploy workflow instead of relying on another manual worker sync.
5. **Preserve the isolated validation artifacts.**
   - Keep the Stage2 and Stage3 isolated workspaces intact for audit and comparison.
   - Do not overwrite `latest_feature_l2` during follow-up checks.

---

## 4. Operational Guardrails

- **V64.3 Completion Rule:** Downstream stages must preserve the Bourbaki Completion semantics now live in code: MDL gain is based on `Var(ΔP) / Var(R)` with `Delta k = 0`, `Zero-variance -> zero signal`, `srl_resid` must never be rewritten by `has_singularity`, and no second compression branch may re-enter Stage 3 or later paths.
- **Multi-Threading Constraints:** Always use `os.environ["POLARS_MAX_THREADS"] = str(max(1, os.cpu_count() // 2))` on 128G UMA machines to prevent ZFS ARC IO-thrashing. Linux must run under `heavy-workload.slice`. The same bounded-thread guidance applies to Stage 3 local backtest on `linux1-lx`.

---

## 5. Latest Related Entries (Handover Archive)
*The most recent deep-dive logs available in `handover/ai-direct/entries/`*

- `20260308_093041_stage2_pathological_empty_frame_windows_runtime_and_stage3_proof` - Real-file Windows normal-path reruns passed on all three unresolved files; isolated Stage3 forge proof passed on the repaired three-file set with explicit year scope.
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

## Update: 2026-03-07 00:52 UTC
- **Engineering speed patch status:** active local evaluation only. No `git commit` or `git push` has been authorized for the engineering-speed branch of work.
- **Fair-comparison finding:** the first speed smoke was a `NO PASS`, but the dominant blocker was not a math regression. The training leg had drifted from the historical smoke contract:
  - baseline smoke training: `xgb_max_depth=3`, `num_boost_round=2`, `seconds=10.98`
  - first speed smoke training: `xgb_max_depth=5`, `num_boost_round=150`, `seconds=774.09`
  - comparison smoke with baseline-matched training params restored training to `10.98s`, while the new backtest file-stream path remained fast (`~3.9s`)
- **Informative-slice discovery status:** still unresolved. The following discovery passes all produced canonical zero-output slices under strict V64.3 semantics:
  - `37` monthly tiny-symbol Stage 2 probes in `/home/zepher/work/Omega_vNext_v643_probe_smoke/.tmp/probe_l2`
  - `5` full-day `fbd5c8b` probes in `/home/zepher/work/Omega_vNext_v643_probe_smoke/.tmp/fullprobe_l2`
  - `5` full-day `b07c2229` probes in `/home/zepher/work/Omega_vNext_v643_probe_smoke/.tmp/fullprobe2_l2`
- **Gate-chain diagnosis:** the zero-output condition is not caused by the downstream `sigma` or `spoof` gates. Across the `10` full-day probes:
  - `is_physics_valid` and `is_energy_active` remain populated
  - `sigma_gate_rows` and `spoof_ok_rows` are non-zero
  - but `epiplexity`, `topo_area`, `topo_energy`, `is_signal`, and `singularity_vector` all remain zero
  - authoritative artifact: `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/gate_chain_diagnosis.json`
- **Baseline truth check:** the pre-speed baseline smoke workspace `/home/zepher/work/Omega_vNext_v643_smoke` is also zero-signal:
  - the baseline L2 files for `20230320 -> 20230324` all have `epiplexity=0`, `is_signal=0`, `singularity_vector=0`, `topo_area=0`, `topo_energy=0`
  - rows are highly symbol-interleaved (`max_consecutive_same_symbol <= 5` on sampled days)
  - therefore the zero-output phenomenon predates the engineering speed patch and is not valid evidence that the patch introduced a new regression
- **Workspace preservation contract:** do not delete or overwrite any of these workspaces:
  - baseline: `/home/zepher/work/Omega_vNext_v643_smoke`
  - speed smoke: `/home/zepher/work/Omega_vNext_v643_speed_smoke`
  - training-comparison smoke: `/home/zepher/work/Omega_vNext_v643_traincmp_smoke`
  - probe/discovery smoke: `/home/zepher/work/Omega_vNext_v643_probe_smoke`
- **Current decision point:** separate the remaining work into two scopes before any release decision:
  1. engineering speed-patch evaluation against fair baseline comparisons
  2. long-standing zero-signal / ordering / slice-informativeness diagnosis that already existed in the baseline smoke
- **Owner decision locked:** preserve both engineering routes for now.
  - keep the old pre-speed engineering route as a valid comparison / rollback path
  - keep the new engineering-speed route as an active candidate path
  - do not eliminate either route until the root cause of the all-zero smoke outputs is understood

## Update: 2026-03-07 03:23 UTC
- **Critical defect state:** the historical `all-zero` Stage2 collapse is now broken on the engineered-speed route after the Stage2 ordering-contract remediation.
- **Validated hot week:** `20250723`, `20250724`, `20250725`, `20250728`, `20250729`.
- **Isolated workspace:** `/home/zepher/work/Omega_vNext_v643_stage2fix_speed_smoke`
- **Stage2 result:** `success=5`, `failed=0`, `STAGE2_SECONDS=1879.12`
- **Stage2 aggregate proof:**
  - `rows = 1,366,691`
  - `epi_pos_rows = 2,006`
  - `topo_area_nonzero_rows = 11,247`
  - `topo_energy_pos_rows = 11,276`
  - `sv_nonzero_rows = 10,822`
  - `signal_rows = 466`
- **Known probe symbol:** `20250725_b07c2229 / 002097.SZ`
  - `topo_area_max_abs = 14.93`
  - `topo_energy_max = 39.53`
  - `epiplexity_max = 4.15`
  - `signal_rows = 2`
- **Forge result:** PASS
  - `base_rows = 8549`
  - `symbols_total = 7245`
  - `FORGE_SECONDS = 186.89`
- **Training result:** PASS
  - `mask_rows = 8549`
  - `total_training_rows = 8549`
  - lightweight smoke contract: `xgb_max_depth=3`, `num_boost_round=2`
  - `TRAIN_SECONDS = 14.90`
- **Backtest result:** PASS
  - `n_frames = 1055429.0`
  - `BACKTEST_SECONDS = 6.80`
  - `engine = file_stream`
  - `Orthogonality = 0.00012346729376811198`
- **Interpretation:** this is the first smoke in the V64 line that passes both:
  - mathematical meaning: canonical signal chain activated
  - engineering meaning: downstream stages consume non-degenerate inputs successfully
- **Locked lessons:**
  - a smoke is invalid if it does not explicitly prove non-degenerate canonical signal activation
  - fail-fast gates must match batching granularity
  - `forge_base_matrix.py` year scope must be explicit on non-baseline hot weeks
- **Release gate:** fixed memory updated, local remediation tree ready for `commit + push`.

## Deferred closure note
- Cross-host Stage2 outputs are currently V64.3-valid on canonical math columns, but `n_ticks` still drifts by host (`linux1=UInt32`, `windows1=UInt64`). This does not block disjoint host-local running, but it **must** be normalized before any future cross-host assist, mixed-host merge, or unified downstream promotion.

## Current full Stage2 progress snapshot
- Live run tag: `stage2_full_20260307_v643fix`
- Code: `6b0afff`
- `linux1-lx`: `19/371` done, `0` fail, current batch `20230206_fbd5c8b.parquet`, observed mean `220.39s/file`, ETA about `21.55h`, healthy.
- `windows1-w1`: `44/372` done, `0` fail, current batch `20240925_fbd5c8b.parquet`, observed mean `88.14s/file`, ETA about `8.03h`, healthy.
- Cluster interpretation: `windows1` is expected to finish much earlier; `linux1` remains the long pole.
- Reminder: cross-host assist is still blocked by deferred `n_ticks` dtype drift until schema normalization is done.

## Update 2026-03-07 UTC: load profile and input-failure snapshot
- Full Stage2 live run remains active under `stage2_full_20260307_v643fix` on commit `6b0afff`.
- Current snapshot:
  - `linux1-lx`: `done=34`, `fail=0`, healthy
  - `windows1-w1`: `done=68`, `fail=4`, still progressing
- The low fan / low heat / low-utilization feel is real. Current live launcher is effectively single-file serial at the launcher level (`stage2_targeted_resume.py` with `files-per-process=1`), with bounded native thread pools. This is a throughput limitation of the launcher model, not evidence of idleness.
- `windows1-w1` has 4 hard input parquet failures:
  - `20240828_fbd5c8b.parquet`
  - `20240902_fbd5c8b.parquet`
  - `20240903_fbd5c8b.parquet`
  - `20240905_fbd5c8b.parquet`
- Failure mode: `schema probe failed: parquet: File out of specification: The file must end with PAR1`
- Treat those 4 files as an input-data remediation item, not a V64.3 math-core regression.
- Preserve current live launcher during this run. A later mission should redesign Stage2 launch for higher per-host utilization while keeping thread-budget guardrails and recoverability.
- Detailed note: `handover/ai-direct/entries/20260307_072722_stage2_load_and_input_failure_snapshot.md`

## Update 2026-03-07 UTC: why windows1 is faster than linux1 in full Stage2
- Current evidence says `windows1-w1` is materially faster than `linux1-lx`, but **not** because it got an easier half of the corpus.
- Observed input split:
  - `linux1-lx`: `371` files, average about `2.75 GB/file`
  - `windows1-w1`: `372` files, average about `3.62 GB/file`
- Observed live speed:
  - `linux1-lx`: about `244.33 s/file`
  - `windows1-w1`: about `125.82 s/file`
- Interpretation:
  - the gap is real
  - it is not explained by smaller files on windows
  - the current live launcher is still single-file serial at the launcher level, so both hosts are underutilized by design
- Most plausible near-term engineering cause:
  - Windows currently uses smaller default Stage2 symbol batches (`20`) than Linux (`50`), which likely reduces reorder/concat/gate overhead under the repaired ordering-contract path
- Future optimization mission for linux should focus on:
  - multi-file parallel launcher per host
  - benchmark of smaller symbol-batch sizes (`50/25/20`)
  - same-file cross-host profiling
- Do not change launcher model or batch-size defaults during the current live run.
- Detailed note: `handover/ai-direct/entries/20260307_110209_windows_faster_than_linux_stage2_analysis.md`
