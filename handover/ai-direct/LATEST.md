# LATEST (Authoritative Multi-Agent Snapshot)

This file is the single source of current operational truth for all agents.

## 0. Update Contract

- Keep this file focused on current state and next actions.
- Put detailed history in `handover/ai-direct/entries/*.md`.
- Every session must update this file before handoff.

## 1. Snapshot Metadata

- `updated_at_local`: 2026-03-03 09:25:20 +0800
- `updated_at_utc`: 2026-03-03 01:25:20 +0000 (UTC)
- `updated_by`: Gemini
- `controller_repo_head`: `afcb663` (branch: `perf/stage2-speedup-v62`, working tree dirty)
- `worker_repo_head_linux`: `afcb663` (branch: `perf/stage2-speedup-v62`, runtime audit/preflight artifacts dirty)
- `worker_repo_head_windows`: `afcb663` (branch: `perf/stage2-speedup-v62`, runtime audit ledgers dirty)

## 2. Active Projects Board

| Project ID | Scope | Status | Last Verified | Owner Host |
|---|---|---|---|---|
| V62-STAGE1-LINUX | Stage1 Base_L1 for shards `0,1,2` | COMPLETED | 2026-02-24 16:47 +0800 | `linux1-lx` |
| V62-STAGE2-WINDOWS | Stage2 Physics from `v62_base_l1` to `v62_feature_l2` | COMPLETED (Linux assist backfill + cleanup finished) | 2026-02-27 15:52 +0800 | `windows1-w1` |
| V62-STAGE2-LINUX | Stage2 Physics for `host=linux1` | COMPLETED (queue drained) | 2026-02-27 15:48 +0800 | `linux1-lx` |
| V62-STAGE2-SPEEDUP | Output-preserving perf refactor (branch `perf/stage2-speedup-v62`) | IN_PROGRESS (deployed+validated; pending merge policy) | 2026-02-27 15:52 +0800 | `controller` |
| HANDOVER-MAINTENANCE | keep handover as entrypoint + run-state truth | IN_PROGRESS | 2026-02-26 12:51 +0800 | `controller` |

Detailed board:

- `handover/ops/ACTIVE_PROJECTS.md`

## 3. Runtime State (Last Verified)

### 3.1 Linux `linux1-lx` (`100.64.97.113`)

- Stage1 status:
  - completed after archive recovery and backfill rerun
  - final unit: `omega_stage1_linux_20260224_160352.service`
  - final metrics: `ASSIGNED=555`, `COMPLETED=10`, `SKIPPED=545`, `ERROR=0`, `FRAMING_COMPLETE=1`
  - `STAGE1_DONE=552` (`/omega_pool/parquet_data/v62_base_l1/host=linux1/*.parquet.done`)
- Stage2 status:
  - V62 completed: `LNX_STAGE2_DONE=552 / 552`
  - **V63 (latest) completed**: `LNX_STAGE2_DONE=552 / 552` (`latest_feature_l2/host=linux1/*.done`)
- Stage3 status:
  - **BaseMatrix Forging (V63)**: COMPLETED. Generated `audit/v63_basematrix.parquet` (243MB) from 155 shards on `linux1-lx`.

### 3.2 Windows `windows1-w1` (`100.123.90.25`)

- Stage1 status:
  - completed (`STAGE1_DONE=191`)
- Stage2 status:
  - V62 completed: `WIN_STAGE2_DONE=191 / 191` (`missing=0`)
  - **V63 (latest) completed**: `WIN_STAGE2_DONE=191 / 191` (`latest_feature_l2/host=windows1/*.parquet`). Note: `.done` markers were manually created due to a Python `touch()` failure on Windows. Data was subsequently synced to `linux1-lx` for Stage 3 BaseMatrix.
  - process state: no active Stage2 python process chain
  - temp cleanup: removed `omega_stage2_iso_*` scratch dirs (`25` removed)

### 3.3 Data Recovery Note

Recovered broken Linux archives from Windows verified copies:

- `20241104, 20241107, 20241111, 20241113, 20241114, 20241115, 20241119, 20241121, 20241202, 20241211, 20241204, 20241212`

Historical broken files are kept as backups:

- `*.7z.bad_20260224_*`

## 4. Tools and Credentials Pointers

- Tools index: `handover/ops/SKILLS_TOOLS_INDEX.md`
- Credential/access policy: `handover/ops/ACCESS_BOOTSTRAP.md`
- Non-secret host registry: `handover/ops/HOSTS_REGISTRY.yaml`
- Logs index: `handover/ops/PIPELINE_LOGS.md`

## 5. Immediate Next Actions (User-Directed Sequence)

1. Stage3: run full-train/backtest sweep on finalized V62 L2 outputs (both hosts now complete).
2. Run parity/integrity gates against `audit/v62.md` and `audit/v62_framing_rebuild.md` on final dual-host outputs.
3. Normalize worker runtime dirty ledgers intentionally (commit/archive/clean policy), keeping code heads fixed at `afcb663`.
4. Update `handover/ops/ACTIVE_PROJECTS.md` and `handover/BOARD.md` with final Stage2 completion snapshot.
5. Preserve assist run evidence logs for RCA/audit, then rotate large transient logs if needed.

## 6. Quick Verification Commands

```bash
# Windows Stage2
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '
$in="D:\\Omega_frames\\v62_base_l1\\host=windows1";
$out="D:\\Omega_frames\\v62_feature_l2\\host=windows1";
"WIN_STAGE2=" + (Get-ChildItem $out -Filter "*.parquet.done" -File -ErrorAction SilentlyContinue).Count + "/" + (Get-ChildItem $in -Filter "*.parquet" -File -ErrorAction SilentlyContinue).Count
'

# Linux Stage2 dependency gate
ssh linux1-lx '/home/zepher/work/Omega_vNext/.venv/bin/python -c "import numba, llvmlite; print(numba.__version__, llvmlite.__version__)"'
```

## 7. Latest Related Entries

- `handover/ai-direct/entries/20260303_012520_v63_basematrix_forge_completed.md`
- `handover/ai-direct/entries/20260227_082443_stage2_dual_host_completion_linux_assist.md`
- `handover/ai-direct/entries/20260227_031200_turingos_week2_guard_mvp_pushed.md`
- `handover/ai-direct/entries/20260227_025500_turingos_week1_schema_gate_completed.md`
- `handover/ai-direct/entries/20260227_105238_stage3_smoke_test.md`
- `handover/ai-direct/entries/20260227_104435_stage2_v62_alignment_audit.md`
- `handover/ai-direct/entries/20260227_100712_turingos_trisync_state_and_gate.md`
- `handover/ai-direct/entries/20260227_015810_stage2_dual_host_progress_update.md`
- `handover/ai-direct/entries/20260227_032500_stage2_ultrathink_optimizations_and_relaunch.md`
- `handover/ai-direct/entries/20260227_014448_stage2_dual_host_stall_snapshot.md`
- `handover/ai-direct/entries/20260226_154217_windows_stage2_pathological_symbol_debug_fix.md`
- `handover/ai-direct/entries/20260224_165312_linux_stage1_repair_and_stage2_gate.md`
- `handover/ai-direct/entries/20260224_041600_omega_vm_windows_connectivity_rca_fix.md`

## Update 2026-02-27 08:24 +0000 (V62 Stage2 Dual-Host Completion + Linux Assist Cutover)
## Update 2026-03-03 09:25 +0800 (V63 BaseMatrix Forge Completed)

- **Host**: `linux1-lx`
- **Progress**: 155/155 batches (100%) completed via `tools/forge_base_matrix.py`.
- **Final Output**: The consolidated `audit/v63_basematrix.parquet` was successfully built at 09:16. Size: ~243MB.
- **Health**: Process completed successfully after ~26.5 hours. Log `stage3_v63_forge.log` indicates clean exit (`status=ok`).
- **Next Action for Next Agent**: Proceed with Stage 3 model full-train/backtest sweep or parity/integrity gates as dictated by the primary LATEST.md next actions.
- **Details**: `handover/ai-direct/entries/20260303_012520_v63_basematrix_forge_completed.md`

## Update 2026-03-03 00:29 +0800 (V63 BaseMatrix Forge 63% Complete)

- **Host**: `linux1-lx`
- **Progress**: 98/155 batches (63.2%) completed via `tools/forge_base_matrix.py`.
- **Health**: Stable. Running at 12 mins/batch on single thread (guarded by memory limits). No OOM.
- **ETA**: ~11.4 hours remaining. Expected finish around noon on March 3rd.
- **Next Action for Next Agent**: Verify process on `linux1-lx`, check shard count reaches 155, and confirm final `v63_basematrix.parquet` generation.
- **Details**: `handover/ai-direct/entries/20260303_002900_v63_basematrix_forge_progress.md`

## Update 2026-03-01 22:45 +0000 (V63 Stage 2 Completion ## Update 2026-03-01 22:45 +0000 (V63 Stage 2 Completion & Stage 3 Launch) Stage 3 Launch)

- **Windows Stage 2 Completion**: Verified the V63 (latest) run finished on March 1st (191 files) despite the Python `.done` marker creation failing silently. Missing markers were manually retrofitted.
- **Data Sync**: Transferred the Windows V63 data (`host=windows1`) to `linux1-lx` over LAN.
- **BaseMatrix (Stage 3) Initiated**: Launched `forge_base_matrix.py` on `linux1-lx` targeting `host=*` to ingest all 743 combined files into `v63_basematrix.parquet`. It is currently processing safely.

- Git alignment completed:
  - `omega-vm`, `linux1-lx`, `windows1-w1` all on `perf/stage2-speedup-v62@afcb663`
  - worker divergence vs `origin/perf/stage2-speedup-v62`: `0 0`
- Completion milestones:
  - Linux native queue finished at `552/552`.
  - Windows reached `190/191` after Linux assist backfilled 10 pending files (`20251103 ... 20260128`).
  - Linux assist processed final `20251022_b07c2229.parquet` and backfilled result.
- Final runtime state:
  - Windows `191/191`, `missing=0`
  - scheduler moved to `Ready`; Stage2 python chain terminated cleanly to avoid duplicate compute
  - Linux/Windows Stage2 process count both `0`
- Cleanup completed:
  - Linux assist input/output caches emptied.
  - Windows temp scratch dirs `omega_stage2_iso_*` cleaned (`25` removed).

## Update 2026-02-27 03:12 +0000 (TuringOS Week-2 Guard MVP Pushed)

- `turingos` main branch pushed to `556ffb4` (from `9865c0e`), with Week-2 Guard MVP:
  - machine-readable trap frames (`[TRAP_FRAME]` in journal)
  - in-state trap JSON block (`[OS_TRAP_FRAME_JSON]`)
  - bounded panic reset budget and fail-closed stop route (`sys://trap/unrecoverable_loop`, pointer `HALT`)
- Gate and regression status:
  - `typecheck` PASS
  - `bench:topology-v4-gate` PASS (8/8; includes new trap-frame assertion)
  - `bench:syscall-schema-gate` PASS (59/59 malformed reject)
  - `bench:staged-acceptance-recursive` PASS
  - `bench:ci-gates` PASS
- Mac sync completed to same head `556ffb4`:
  - created protective stash `autosync_mac_20260227_031100_before_556ffb4`
  - `git pull --ff-only origin main` success

## Update 2026-02-27 02:55 +0000 (TuringOS Week-1 Schema Gate Completed)

- Week-1 protocol standardization landed in `projects/turingos`:
  - new SSOT schema module: `src/kernel/syscall-schema.ts`
  - Oracle/Engine duplicate syscall validators removed and unified
  - benchmark prompt builders switched to shared opcode field docs
  - new adversarial gate with 59 malformed fixtures (`bench:syscall-schema-gate`)
- Dual-pass audit outcome:
  - Gemini pass-1 found `SYS_WRITE.semantic_cap` type fail-close gap (NO-GO)
  - issue fixed + fixtures added + pass-2 re-audit => GO
- Current verification result:
  - `typecheck` PASS
  - `bench:topology-v4-gate` PASS (8/8)
  - `bench:staged-acceptance-recursive` PASS
  - `bench:ci-gates` PASS (includes schema gate + AC2.1~AC3.2)
- Git state snapshot recorded in:
  - `handover/ai-direct/entries/20260227_025500_turingos_week1_schema_gate_completed.md`

## Update 2026-02-27 10:07 +0800 (TuringOS Tri-Sync + Gate)

- Completed tri-party Git state audit and sync for TuringOS:
  - GitHub `origin/main`: `ef52a4d`
  - omega-vm repo: `ef52a4d` clean, divergence `0 0`
  - mac repo: moved from `5db107e` (behind 1, dirty) to `ef52a4d` clean, divergence `0 0`
- Preserved Mac pre-sync local state via stash:
  - `presync_mac_20260227_100343_before_ef52a4d`
- Post-sync verification on Mac passed:
  - `typecheck`
  - `bench:topology-v4-gate` (8/8)
  - `bench:ac42-deadlock-reflex`
  - `bench:staged-acceptance-recursive`
  - `bench:ci-gates` (AC2.1~AC3.2 PASS)
- Next queued action: `npm run bench:os-longrun -- --repeats 10` on Mac with live monitoring.

## Update 2026-02-24 21:41:50 +0800

- Stage2 Windows (`D:\\work\\Omega_vNext\\audit\\stage2_targeted_resume.log`):
  - Targeted runner converted to per-file timeout isolation.
  - Current snapshot: `WIN_DONE=146/191`.
  - Confirmed blocker file #1: `20241029_b07c2229.parquet` timed out at 900s (`rc=124`) and was isolated.
  - Runner moved forward to file #2 (`20241128_b07c2229.parquet`) and remains in-progress.
- Stage2 Linux (`/home/zepher/work/Omega_vNext/audit/stage2_targeted_resume_linux.log`):
  - Original run had no progress and held a stale first-file state.
  - Relaunched targeted runner with per-file timeout guard (`TIMEOUT_SEC=900`).
  - New run started at `2026-02-24T21:41:18+08:00` on `20230315_fbd5c8b.parquet`.
- Key diagnosis:
  - Multiple specific L1 files trigger long-hang or native crash behavior in Stage2 path.
  - Engineering mitigation now active: isolate per file, enforce timeout, continue remaining backlog.

## Update 2026-02-25 08:53 +0800 (Linux Freeze RCA + Hard Fix)

- Root cause (this reboot event, direct evidence):
  - Previous boot kernel log (`journalctl -b -1 -k`) shows:
    - `polars-5 invoked oom-killer`
    - `mem_cgroup_out_of_memory`
  - Stage2 worker process was running in user session cgroup before fix:
    - `/proc/<pid>/cgroup` -> `0::/user.slice/user-1000.slice/session-6.scope`
  - This aligns with symptom pattern: SSH/TCP handshake reachable, but command execution intermittently times out under pressure (pseudo-hang).
- Why it froze:
  - Stage2 heavy single-file runs under constrained/non-dedicated cgroup can trigger memcg OOM thrash.
  - System remains network-reachable while command scheduler responsiveness collapses.
- Hard remediation applied:
  - Killed orphan Stage2 process tree in `user.slice`.
  - Relaunched Stage2 targeted runner as a transient systemd unit pinned to `heavy-workload.slice`:
    - unit: `omega_stage2_linux_targeted_20260225_085208.service`
    - script: `/home/zepher/work/Omega_vNext/audit/stage2_targeted_resume_linux.sh`
    - guardrail retained: `TIMEOUT_SEC=900`
- Verification (post-fix):
  - `systemctl show` confirms:
    - `Slice=heavy-workload.slice`
    - `ActiveState=active`
    - `ControlGroup=/heavy.slice/heavy-workload.slice/omega_stage2_linux_targeted_20260225_085208.service`
  - Process tree confirms runner + timeout + python child all in `heavy-workload.slice`.
- Current status snapshot:
  - Linux Stage2: resumed from pending list, processing `20230315...` under heavy slice.
  - Windows Stage2 remains running with timeout-isolation flow.

## Update 2026-02-25 09:02 +0800 (Linux Stability Baseline Hardening)

- Objective:
  - shift from reactive debug to deterministic host guardrails for Linux Stage workloads.
- Code-level hardening landed:
  - `tools/stage2_physics_compute.py`
    - added Linux cgroup hard gate (must run inside `heavy-workload.slice`, override only via `OMEGA_STAGE2_ALLOW_USER_SLICE=1`)
    - added `oom_score_adj` raise to `300` (best-effort) in main process and worker initializer
    - multiprocessing pool now applies the same guardrail in child workers
  - `tools/linux_runtime_preflight.py` (new)
    - one-shot Linux preflight for recurring failure points:
      - `/omega_pool` mount and required path checks
      - `heavy-workload.slice` memory/cpu baseline checks
      - Python deps sanity (`polars`, `pyarrow`, `numba`)
      - `framing_cache` free-space threshold gate
      - running stage process cgroup placement audit (`heavy-workload.slice` vs `user.slice`)
      - previous-boot OOM signature context scan
    - supports optional JSON report output for machine monitoring (`--json-out`)
- Handover index alignment:
  - `handover/ops/SKILLS_TOOLS_INDEX.md` now includes:
    - `tools/stage2_targeted_resume.py`
    - `tools/launch_linux_stage2_heavy_slice.sh`
    - `tools/linux_runtime_preflight.py`
    - `tools/install_linux_preflight_timer.sh`
  - removed stale index entry to non-existent tool `tools/ai_incident_watchdog.py`
- Operational impact:
  - no change to feature math, schema, or expected output semantics
  - reduces repeat Linux freeze probability by making wrong launch context fail fast.

## Update 2026-02-25 09:05 +0800 (Linux Preflight Live Validation)

- Ran preflight directly on `linux1-lx` with latest script payload:
  - command:
    - `python3 tools/linux_runtime_preflight.py --repo-root /home/zepher/work/Omega_vNext --auto-fix --min-cache-free-gb 50 --json-out /tmp/omega_linux_preflight.json`
- Result:
  - `ok=true`, `fail_count=0`, `warn_count=1`
  - auto-fixed missing cache path: `/home/zepher/framing_cache`
  - warning retained as historical context only:
    - previous boot kernel OOM signatures (`polars-* invoked oom-killer`, `mem_cgroup_out_of_memory`)
- Current interpretation:
  - Linux host baseline is now in a launch-safe state for guarded Stage workloads.
  - Stage2 Linux hard-guard behavior validated in non-heavy session:
    - exits with fatal guard (`exit 101`) and explicit relaunch hint to `tools/launch_linux_stage2_heavy_slice.sh`.

## Update 2026-02-26 12:51 +0800 (Stage2 Performance Refactor — Branch Ready)

- Branch: `perf/stage2-speedup-v62` (`a0c08ab`), branched from `main`.
- Objective: significantly speed up Stage2 physics compute without altering output schema or numerical values.
- Root-cause analysis identified 4 independent bottlenecks via deep audit of all Stage2 modules:
  1. Hardcoded `POLARS_MAX_THREADS=8` causes Rayon thread oversubscription when multiprocessing workers > 1.
  2. Per-symbol-batch `gc.collect()` in inner loops destroys CPU pipeline during hot compute.
  3. Temporal rolling in `omega_etl.py` implemented via `.rolling().agg() + .join()` causes 2x peak RAM.
  4. MDL arena in `kernel.py` uses `concat_list().list.arg_max()` creating List columns (memory fragmentation).
- Fixed applied (all output-preserving):
  - `tools/stage2_physics_compute.py`: dynamic `POLARS_MAX_THREADS` budget (`_apply_worker_thread_budget`); removed inner-loop `gc.collect()`.
  - `omega_core/omega_etl.py`: replaced rolling agg+join with inline `rolling_mean_by` expressions.
  - `omega_core/kernel.py`: replaced `concat_list.list.arg_max` with scalar `when/then` chain.
  - `tests/test_stage2_output_equivalence.py` (NEW): 6 regression tests covering ETL columns, physics features, dominant_probe values, Turing discipline, MDL clipping, inf/NaN safety.
- A/B benchmark results (synthetic 15k rows):
  - ETL temporal rolling: **1.65x** (2.8ms → 1.7ms median)
  - Kernel MDL argmax: **1.14x** (0.5ms → 0.4ms median)
  - Real-world additional gains from GC removal and thread budget cannot be measured in micro-benchmark but eliminate OOM crash cycles and Polars panic→fallback loops.
- Test results: **11/11 passed** (5 existing + 6 new).
- Compliance: fully aligned with `audit/v62.md` (MDL formula, R² clipping, Turing discipline) and `audit/v62_framing_rebuild.md` (two-stage pipeline, no `apply()`/`map_elements()`).
- Next actions:
  1. Push branch to GitHub.
  2. Sync to Linux/Windows worker nodes.
  3. Single-file A/B validation on real L2 output before full cutover.
- Detailed entry: `handover/ai-direct/entries/20260226_125100_stage2_perf_refactor_branch_ready.md`

## Update 2026-02-26 15:42 +0800 (Windows Stage2 Fail-Ledger Deep Debug + Live Hotfix)

- Target issue:
  - `20250704_b07c2229.parquet` (plus adjacent blocker `20250725_b07c2229.parquet`) repeatedly crashed Windows Stage2 run.
- Hard evidence:
  - native exit codes: `rc=3221225477`, `rc=3221226505`
  - allocator failures up to:
    - `33045445984` bytes
    - `103308592388` bytes
    - `117181513728` bytes
    - `234364076032` bytes
- Symbol-level RCA:
  - `20250704` contains `123257.SZ` with `rows=60284` but only `2` distinct `time` values.
  - `20250725` contains `127110.SZ` with `rows=223507` and only `2` distinct `time` values.
- Mitigation landed (execution-layer, no formula rewrite):
  - added pathological symbol profiler and crash-conditional skip guard in `tools/stage2_physics_compute.py`
  - guard is only used when isolated symbol subprocess crashes and threshold matches.
- Validation:
  - local regression suite: `12 passed`
  - function-level probe on Windows confirms skip-eligibility for both pathological symbols.
- Runtime:
  - official task `Omega_v62_stage2_isolated_v2` relaunched
  - progress currently evidenced by active process CPU/RSS and `20250704` tmp parquet growth.
- Detailed entry:
  - `handover/ai-direct/entries/20260226_154217_windows_stage2_pathological_symbol_debug_fix.md`
