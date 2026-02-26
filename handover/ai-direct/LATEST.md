# LATEST (Authoritative Multi-Agent Snapshot)

This file is the single source of current operational truth for all agents.

## 0. Update Contract

- Keep this file focused on current state and next actions.
- Put detailed history in `handover/ai-direct/entries/*.md`.
- Every session must update this file before handoff.

## 1. Snapshot Metadata

- `updated_at_local`: 2026-02-26 15:42:17 +0800 (CST)
- `updated_at_utc`: 2026-02-26 07:42:17 +0000 (UTC)
- `updated_by`: Codex (GPT-5)
- `controller_repo_head`: `8ebadb1` (branch: `perf/stage2-speedup-v62`)
- `worker_repo_head_linux`: `fd0f5e1` (branch: `main`)
- `worker_repo_head_windows`: `6c9fead` (branch: `main`, runtime hotfix file dirty)

## 2. Active Projects Board

| Project ID | Scope | Status | Last Verified | Owner Host |
|---|---|---|---|---|
| V62-STAGE1-LINUX | Stage1 Base_L1 for shards `0,1,2` | COMPLETED | 2026-02-24 16:47 +0800 | `linux1-lx` |
| V62-STAGE2-WINDOWS | Stage2 Physics from `v62_base_l1` to `v62_feature_l2` | IN_PROGRESS (targeted resume + pathological-symbol guard) | 2026-02-26 15:42 +0800 | `windows1-w1` |
| V62-STAGE2-LINUX | Stage2 Physics for `host=linux1` | BLOCKED (dependency) | 2026-02-24 16:53 +0800 | `linux1-lx` |
| V62-STAGE2-SPEEDUP | Output-preserving perf refactor (branch `perf/stage2-speedup-v62`) | PARTIALLY_DEPLOYED (runtime hotfix on Windows) | 2026-02-26 15:42 +0800 | `controller` |
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
  - currently not running
  - blocker: `.venv` missing `numba` (`ModuleNotFoundError`)
  - `LNX_STAGE2_DONE=0`

### 3.2 Windows `windows1-w1` (`100.123.90.25`)

- Stage1 status:
  - completed (`STAGE1_DONE=191`)
- Stage2 status:
  - scheduler task running: `Omega_v62_stage2_isolated_v2` (targeted resume, per-file isolation)
  - snapshot: `WIN_STAGE2_DONE=178 / 191`
  - pending list: `13` files (`audit/stage2_pending_isolated_v2.txt`)
  - current blockers under active processing: `20250704_b07c2229.parquet`, `20250725_b07c2229.parquet`
  - mitigation deployed in runtime:
    - `tools/stage2_physics_compute.py` now includes pathological-symbol crash guard
    - key knob: `OMEGA_STAGE2_SKIP_PATHOLOGICAL_SYMBOL_ON_FAIL`
  - progress evidence while log is quiet (subprocess stdout capture mode):
    - `D:\Omega_frames\v62_feature_l2\host=windows1\20250704_b07c2229.parquet.tmp` growth observed (`5.14MB -> 6.57MB -> 8.01MB -> 9.88MB`)
  - current fail ledger file (`audit/stage2_targeted_failed_isolated_v2.txt`) is empty in this run (started with `--reset-fail-file`)
  - git state note:
    - worker repo head remains `main@6c9fead`
    - runtime hotfix file is locally modified: `M tools/stage2_physics_compute.py`

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

1. Continue monitoring `Omega_v62_stage2_isolated_v2` until `20250704_b07c2229.parquet.done` appears.
2. Confirm whether skip guard line appears in log:
   - `Skip pathological symbol after native crash`.
3. Verify next blocker `20250725_b07c2229.parquet` status and update fail ledger outcome.
4. Commit/push hotfix from branch and normalize worker git state (avoid long-term runtime dirty patch).
5. After Windows blockers clear, return to Linux Stage2 dependency unblock (`numba`) and relaunch.

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

- `handover/ai-direct/entries/20260226_154217_windows_stage2_pathological_symbol_debug_fix.md`
- `handover/ai-direct/entries/20260224_165312_linux_stage1_repair_and_stage2_gate.md`
- `handover/ai-direct/entries/20260224_041600_omega_vm_windows_connectivity_rca_fix.md`

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
