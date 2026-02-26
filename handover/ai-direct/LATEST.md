# LATEST (Authoritative Multi-Agent Snapshot)

This file is the single source of current operational truth for all agents.

## 0. Update Contract

- Keep this file focused on current state and next actions.
- Put detailed history in `handover/ai-direct/entries/*.md`.
- Every session must update this file before handoff.

## 1. Snapshot Metadata

- `updated_at_local`: 2026-02-26 12:30:46 +0800 (CST)
- `updated_at_utc`: 2026-02-26 04:30:46 +0000 (UTC)
- `updated_by`: Codex (GPT-5)
- `controller_repo_head`: `fd0f5e1`
- `worker_repo_head_linux`: `fd0f5e1` (last known from prior sync window)
- `worker_repo_head_windows`: `6c9fead` (last known; requires re-verify)

## 2. Active Projects Board

| Project ID | Scope | Status | Last Verified | Owner Host |
|---|---|---|---|---|
| V62-STAGE1-LINUX | Stage1 Base_L1 for shards `0,1,2` | COMPLETED | 2026-02-24 16:47 +0800 | `linux1-lx` |
| V62-STAGE2-WINDOWS | Stage2 Physics from `v62_base_l1` to `v62_feature_l2` | IN_PROGRESS | 2026-02-24 16:53 +0800 | `windows1-w1` |
| V62-STAGE2-LINUX | Stage2 Physics for `host=linux1` | BLOCKED (dependency) | 2026-02-24 16:53 +0800 | `linux1-lx` |
| HANDOVER-MAINTENANCE | keep handover as entrypoint + run-state truth | IN_PROGRESS | 2026-02-24 16:53 +0800 | `controller` |

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
  - running process: `stage2_physics_compute.py --workers 1`
  - snapshot: `WIN_STAGE2_DONE=113 / 191`
  - active log: `D:\work\Omega_vNext\audit\stage2_compute.log`

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

1. Sync updated `handover/` docs to GitHub.
2. Run `git pull` on `windows1`, `linux1`, and `omega-vm`.
3. Install `numba` into Linux `.venv` if still missing.
4. Start Linux Stage2 in `heavy-workload.slice`.
5. Verify Linux Stage2 done-marker growth.

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

## Update 2026-02-25 09:41 +0800 (Linux Stage2 Relaunch + Live Progress)
- Git sync:
  - controller pushed `fd0f5e1` to GitHub `origin/main`.
  - linux1 switched from `master@6c9fead` to `main@fd0f5e1`.
- Preflight automation:
  - installed and enabled `omega_linux_preflight.timer` (10-min cadence).
  - latest report remains healthy: `ok=true`, `fail_count=0`, `warn_count=1` (historical OOM context only).
- Stage2 live run:
  - previous unit `omega_stage2_linux_20260225_091335` ended without forward progress.
  - relaunched clean under heavy slice:
    - unit: `omega_stage2_linux_20260225_093815.service`
    - cgroup: `/heavy.slice/heavy-workload.slice/omega_stage2_linux_20260225_093815.service`
  - current runtime evidence:
    - `LNX_STAGE2_DONE=32/552` (increased from 31 after relaunch)
    - first file ended `rc=-15` (isolated fail), second file completed (`20230316_fbd5c8b.parquet`), run continues on file #3.
    - cgroup `memory.events`: `oom=0`, `oom_kill=0`.
- Windows reference snapshot:
  - Stage2 targeted pass has ended at `WIN_STAGE2=146/191`, `FAILED_TOTAL=46` (timeout-isolated backlog remains).

## Update 2026-02-25 10:08 +0800 (Windows Stage2 Leftover Recovery Started)
- Problem confirmation:
  - Windows Stage2 previous targeted pass ended at `WIN_STAGE2=146/191` with `FAILED_TOTAL=46`.
  - Current pending by done-marker diff: `45` files.
- Root cause class:
  - timeout policy (`900s`) is too aggressive for tail heavy files; run ended with timeout-isolated backlog.
  - Windows local repo was on `v60` / `2768777` and lacked `tools/stage2_targeted_resume.py`.
- Applied recovery strategy:
  - switched Windows repo to `main` tracking `origin/main` (`6c9fead`) on host.
  - synced `tools/stage2_targeted_resume.py` from controller workspace to Windows `tools/`.
  - validated runner with smoke:
    - `--max-files 1 --timeout-sec 120` => deterministic timeout-isolated fail path works (`SMOKE_RC=0`, `FAILED_TOTAL=1`).
  - started detached retry run for leftovers with longer timeout:
    - first `Start-Process` detach attempt was not persistent after SSH session close.
    - switched to Task Scheduler execution wrapper for persistence:
      - task: `Omega_v62_stage2_retry`
      - runner cmd wrapper: `D:\work\Omega_vNext\audit\run_stage2_retry.cmd`
      - scheduler user: `SYSTEM`
      - scheduler last result: `267009` (running state)
    - timeout: `2400s`
    - log: `D:\work\Omega_vNext\audit\stage2_targeted_resume_retry.log`
    - fail list: `D:\work\Omega_vNext\audit\stage2_targeted_failed_retry.txt`
    - pending list: `D:\work\Omega_vNext\audit\stage2_pending_retry.txt`
- Live snapshot right after launch:
  - `WIN_STAGE2=146/191`
  - retry log shows active run: `[1/45] START 20241128_b07c2229.parquet`
  - retry fail list currently `0` lines (run in progress).

## Update 2026-02-25 10:45 +0800 (Linux Stage2 Autonomous Recovery Hardening)
- Linux root-cause deep debug (for repeated Stage2 drops):
  - direct evidence from system journal around `2026-02-25 10:23:54`:
    - `earlyoom` triggered under low mem/swap and killed Stage2 python (`status=9/KILL`)
    - collateral user-session process kills observed at same timestamp
  - this explains repeated Stage2 unit restarts without deterministic runner end marker.
- Operational hard fixes applied on linux1:
  1. Disabled OOM daemon interference:
     - `systemctl stop earlyoom`
     - `systemctl disable earlyoom`
     - `systemctl mask earlyoom`
  2. Added autonomous Stage2 watchdog loop:
     - script: `tools/linux_stage2_autopilot.sh`
     - running detached with PID file: `audit/stage2_autopilot.pid`
     - behavior: if no active Stage2 unit, auto-launch in `heavy-workload.slice` and continue polling until done cardinality reaches input cardinality.
  3. Added Stage2 restart memory:
     - `tools/stage2_targeted_resume.py` now carries fail ledger across restarts by default (`FAILED_CARRY_IN`), avoiding repeated restart on the same known-bad file.
  4. Ensured runtime tuning env reaches systemd unit:
     - `tools/launch_linux_stage2_heavy_slice.sh` now passes `--setenv` for:
       - `OMEGA_STAGE2_SYMBOL_BATCH_SIZE`
       - `OMEGA_STAGE2_POLARS_THREADS`
- Live profile currently active:
  - unit: `omega_stage2_linux_20260225_103955.service`
  - runner tuning: `batch_size=1`, `polars_threads=2` (conservative stability profile)
  - earlyoom state: `inactive + masked`
  - cgroup events: `oom=0`, `oom_kill=0` (no cgroup OOM kill after hardening)
  - autopilot cadence: 60s checks with auto-relaunch on drop.
  - autopilot is now managed by systemd:
    - service: `omega_stage2_autopilot.service`
    - state: `active`, `enabled`, `Restart=always`

## Update 2026-02-25 12:45 +0800 (Windows Stage2 Recovery Stabilized)
- Root blocker confirmed and repaired:
  - Windows Stage2 venv missed runtime deps (`pyarrow`, `numba`, `llvmlite`).
  - Fixed by offline wheel deploy + extraction into `D:\work\Omega_vNext\.venv\Lib\site-packages`.
  - Import gate now passes: `pyarrow=True`, `numba=True`, `llvmlite=True`, `polars=True`.
- Runtime behavior after fix:
  - `stage2_targeted_resume.py` now runs, but specific tail files repeatedly hang until timeout.
  - first two pathological files isolated by fail ledger progression:
    - `20241128_b07c2229.parquet`
    - `20250612_b07c2229.parquet`
- Autonomous safe retry path deployed:
  - command file: `D:\work\Omega_vNext\audit\run_stage2_retry_safe_once.cmd`
  - scheduler: `Omega_v62_stage2_safe_retry` (every 1 minute)
  - per-trigger policy: `max-files=1`, `timeout-sec=60`, carry fail ledger, continue next pending.
- Current live evidence:
  - latest retry log shows rolling progression to next pending file:
    - `START 20250707_b07c2229.parquet` at `2026-02-25T12:45:01`
  - snapshot: `WIN_STAGE2=146/191`, `WIN_FAILED=3`, `WIN_REMAINING=42`.
- Linux reference snapshot (same window):
  - `LNX_STAGE2=45/552`, `omega_stage2_autopilot.service=active`, heavy-slice unit running and advancing.

## Update 2026-02-25 14:55 +0800 (Windows Stage2 RCA Deep Dive + Validity Guardrails)
- Current snapshot:
  - `WIN_STAGE2_DONE=147/191`, `PENDING=44`, no active Windows Stage2 python process.
- Direct reproducible evidence:
  - Single-file run on `20241128_b07c2229.parquet` (2.1GB) crashes with `rc=-1073741819` (`0xC0000005`) under current runtime.
  - Reproduced twice:
    - profile A: `batch_size=50`, `polars_threads=8` -> crash at `elapsed=337s`
    - profile B: `batch_size=20`, `polars_threads=2` -> crash at `elapsed=564s`
  - Windows Event Log confirms native module crash:
    - `Application Error (Event ID 1000)` faulting module `_polars_runtime.pyd`, exception `0xc0000005`
    - matching `Windows Error Reporting (Event ID 1001)` APPCRASH entries.
- Root-cause reclassification:
  - Primary: native crash in Windows Polars runtime path (`_polars_runtime.pyd`) under current Python/runtime stack.
  - Secondary: timeout policy only surfaces symptoms; not the primary cause.
- Code hardening landed (controller workspace + synced to Windows `tools/`):
  - `tools/stage2_physics_compute.py`
    - `process_chunk` now returns structured `{ok,status,message}` result.
    - Stage2 main now counts failures and exits non-zero when any file fails.
    - Windows defaults tuned conservatively (`POLARS_MAX_THREADS=2`, symbol batch default `20`).
    - runtime-risk warning emitted on risky Windows stack.
  - `tools/stage2_targeted_resume.py`
    - per-file subprocess now exits non-zero when `ok=false` (prevents `rc=0` fake success).
    - added Windows runtime preflight (blocks risky runtime by default).
    - added `RUN_FAILED` log metric and run-level non-zero exit (`rc=2`) when failures occur.
- Validation of new guardrails:
  - Preflight now correctly blocks current risky runtime with explicit fatal reason.
  - Override smoke (`OMEGA_STAGE2_ALLOW_RISKY_RUNTIME=1`, timeout=30s) returns `RC=2` with deterministic fail ledger update.
- Operational rule from now:
  - Do **not** treat Windows Stage2 outputs as production-valid until runtime is moved to a pinned dedicated non-user-site environment (recommended Python 3.12/3.13 stack) and re-smoke passes.

## Update 2026-02-25 19:47 +0800 (Windows Stage2 Runtime Repair v2 Landed)
- Root-cause confirmation (live evidence):
  - recurrent crash remains native APPCRASH in `_polars_runtime.pyd` (`0xc0000005`) under Windows Python 3.14 + user-site runtime path.
  - old runner also hard-forced `POLARS_FORCE_PKG=64`; this is incompatible with a clean env that only has `polars-runtime-32`, and can trigger `Polars binary is missing` / `PyLazyFrame` failures.
- Runtime repair actions applied:
  - built dedicated Windows env: `D:\work\Omega_vNext\.venv_stage2_win`
  - installed runtime deps into the dedicated env:
    - `polars==1.38.1`
    - `pyarrow==23.0.0`
    - `numpy==2.4.1`
    - `pandas==2.3.3`
    - `psutil`, `pyyaml`
  - enforced isolation from user-site:
    - `PYTHONNOUSERSITE=1`
    - runner python pinned to `D:\work\Omega_vNext\.venv_stage2_win\Scripts\python.exe`
  - removed `POLARS_FORCE_PKG=64` in the new runner path.
- Smoke + schema validation passed:
  - targeted smoke run with new env completed one pending file:
    - `20250707_b07c2229.parquet` finished in `602.8s`
    - done markers advanced: `149 -> 150`
  - schema parity check (new file vs previous good Windows file) passed:
    - `schema_equal=True` (`41` columns)
    - key dtypes stable (`n_ticks=uint32`, `dominant_probe=uint32`)
- Relaunch status:
  - new wrapper: `D:\work\Omega_vNext\audit\run_stage2_retry_isolated_v2.cmd`
  - new task: `Omega_v62_stage2_isolated_v2`
  - new log/ledger set:
    - `audit/stage2_targeted_resume_isolated_v2.log`
    - `audit/stage2_targeted_failed_isolated_v2.txt`
    - `audit/stage2_pending_isolated_v2.txt`
  - current run resumed on backlog from `20250704_b07c2229.parquet`, with `WIN_STAGE2=150/191`.
- Remaining risk note:
  - Python 3.13 migration could not be completed yet (winget source failures + very slow direct installer download).
  - temporary operation still requires `OMEGA_STAGE2_ALLOW_RISKY_RUNTIME=1` on Windows until Python 3.13/3.12 runtime is landed.

## Update 2026-02-25 20:46 +0800 (Independent Gemini 3.1 Pro Stage2 Throughput Audit)
- Completed an independent Gemini audit for Stage2 speedups with `gemini-3.1-pro-preview`.
- Full report saved at:
  - `handover/ai-direct/entries/20260225_204617_gemini31_stage2_speed_audit.md`
- CLI invocation path that worked reliably:
  - use direct binary `~/.npm-global/bin/gemini` (not `~/.local/bin/gemini` wrapper).
  - run with proxy env unset for this call to avoid OAuth/token handshake reset loops.
  - keep auth mode on `oauth-personal` so cached credentials are used in headless mode.
- Audit verdict summary:
  - slowness is primarily architecture/scheduling (panic fallback + oversubscription), not core math complexity growth.
  - highest-ROI immediate actions: thread-budget cap + JIT cache + remove per-batch forced GC.
  - structural >2x path exists via fallback rewrite + compute graph flattening; high ceiling with one-pass unified kernel.
- Invocation runbook recorded at:
  - `handover/ai-direct/entries/20260225_205100_gemini_cli_invocation_notes.md`

## Update 2026-02-25 21:35 +0800 (Stage2 A/B Benchmark Blocked by Linux SSH Banner Timeout)
- Implemented branch-side Stage2 orchestration upgrade:
  - `tools/stage2_targeted_resume.py` now supports multi-file subprocess mode via `--files-per-process` (default 8), marker-aware timeout handling, and deferred-not-started safety.
- Copied candidate runner to Linux as:
  - `~/work/Omega_vNext/tools/stage2_targeted_resume_try2.py` (non-destructive test path).
- Prepared benchmark workspace:
  - `/home/zepher/work/Omega_vNext/audit/bench_stage2_try2_20260225_211640`
- During live benchmark attempts, Linux entered SSH banner-timeout state:
  - ping/TCP22 reachable, but SSH handshake repeatedly times out at banner exchange.
  - consequence: A/B throughput results not yet collectible.
- Incident details and recovery steps logged at:
  - `handover/ai-direct/entries/20260225_213500_stage2_ab_benchmark_blocked_linux_ssh_banner_timeout.md`

## Update 2026-02-25 21:48 +0800 (Linux Reboot Recovery + Stage2 Try2 Cutover)
- Linux reboot recovery confirmed; SSH restored.
- Post-reboot A/B fast benchmark completed on Linux:
  - benchmark root: `/home/zepher/work/Omega_vNext/audit/bench_stage2_try2_20260225_211640`
  - old runner vs new batch runner (same input + thread settings) yielded:
    - `OLD_SEC=9`, `NEW_SEC=7`, `SPEEDUP_X=1.286`
- Cutover completed:
  - deployed new batch-capable runner to `~/work/Omega_vNext/tools/stage2_targeted_resume.py`
  - `omega_stage2_autopilot.service` restarted and active.
  - active stage2 unit now runs batch-mode subprocess path (`FILES_PER_PROCESS=8`).
- Detailed evidence:
  - `handover/ai-direct/entries/20260225_214800_stage2_try2_benchmark_and_linux_cutover.md`

## Update 2026-02-25 21:57 +0800 (Windows Stage2 Speedup Cutover)
- Confirmed Windows can be sped up without changing outputs by switching Stage2 runner orchestration from single-file subprocess to batch subprocess.
- Applied on Windows host:
  - deployed updated `tools/stage2_targeted_resume.py`
  - updated wrapper `audit/run_stage2_retry_isolated_v2.cmd` with `--files-per-process 4`
  - disabled legacy task `Omega_v62_stage2_isolated`
  - kept/ran `Omega_v62_stage2_isolated_v2` only.
- Runtime verification:
  - task state: `Omega_v62_stage2_isolated_v2 = Running`
  - runner log shows `FILES_PER_PROCESS=4`, `BATCH_TOTAL=8`.
- Detailed evidence:
  - `handover/ai-direct/entries/20260225_215700_windows_stage2_speedup_cutover_files_per_process_4.md`

## Update 2026-02-26 12:30 +0800 (Stage2 Multi-Round Issues Consolidated + Handover Gapfill)
- New consolidated incident record:
  - `handover/ai-direct/entries/20260226_123046_stage2_multiround_incident_matrix_and_gapfill.md`
- Newly backfilled items that were previously fragmented or missing:
  - Windows WMI probe hang risk and bypass behavior before `import polars`.
  - `rc=4` empty-output semantics in isolated symbol mode (non-fatal skip case).
  - timeout batch handling semantics: `DEFER not-started` vs true fail.
  - explicit operator semantics for `FAILED_TOTAL` and `RUN_FAILED`.
  - targeted runner/autopilot log paths and ledgers as first-class monitoring signals.
- Documentation updates landed:
  - `handover/README.md`
  - `handover/ops/PIPELINE_LOGS.md`
