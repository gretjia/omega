# LATEST

Last Updated: 2026-02-24 04:20:00 +0800 (V62 Pipeline Spec Update)
Active Mission: Linux Stage1 completion + tailnet stability hardening

## V62 Pipeline Architecture: Orthogonal Decoupling

The V62 pipeline is strictly decoupled into three stages to maximize I/O throughput and enable rapid mathematical iteration.

### Stage 1: Base Lake (Objective Extraction)
- **Goal:** Extract raw `.7z` archives to `.parquet`. Objective price/volume data only (no physics). **Run once per dataset.**
- **Files:**
  - Linux: `tools/stage1_linux_base_etl.py` (Uses `/home/zepher/framing_cache` on NVMe to bypass ZFS).
  - Windows: `tools/stage1_windows_base_etl.py` (Uses `D:\tmp\framing\`).
- **Action:** `7z x` -> Clean CSV -> Polars ETL -> `Base_L1.parquet`.
- **Primary Tooling:** `tools/build_7z_shards.py` (Generate shard lists).

### Stage 2: Physics Engine (Mathematical Modeling)
- **Goal:** Apply high-order physics (MDL, SRL, Topology) to `Base_L1.parquet`. **Run every time the math model changes.**
- **Files:**
  - `tools/stage2_physics_compute.py`
  - Core Math: `omega_core/omega_math_core.py` (Numba JIT accelerated).
- **Action:** Load Parquet -> Numba Parallel Compute -> `Feature_L2.parquet`.
- **Requirement:** High RAM (128G nodes) for in-memory compute.

### Stage 3: Training & Backtest (GCP Scale-out)
- **Goal:** Train XGBoost models and verify via backtesting.
- **Files:**
  - Training: `tools/run_vertex_xgb_train.py` (Vertex AI / GCP Batch).
  - Upload: `tools/gcp_upload.py`.
  - Backtest: `tools/run_local_backtest.py`.
- **Action:** Sync `L2.parquet` to GCS -> Spot VM Pulse (100+ nodes) -> Local validation.

## Log Monitoring Index
Detailed log guide: `handover/ops/PIPELINE_LOGS.md`

- **Stage 1 (Linux):** `tail -f audit/stage1_linux_v62.log`
- **Stage 1 (Windows):** `audit/stage1_windows_v62.log`
- **Stage 2/3:** Generally `stdout`. Recommendation: `2>&1 | tee audit/stage2.log`

---

## Update 2026-02-24 08:40:00 +0800 (Stage 1 Status Update - 90.9% Done)

- **Status Correction:** Windows (windows1) is **COMPLETED**. Prior "Critical/Down" assessment was an error due to tailnet instability and faulty probe logic.
- **Progress:**
  - **Total:** 683 / 751 files (90.9%).
  - **Linux (linux1):** 🟢 **ACTIVE**. DONE=492, processing 2025-04-25.
  - **Windows (windows1):** 🟢 **COMPLETED**. Shard 3 finished (191 files, "=== FRAMING COMPLETE ===").
- **Handover Entry:** `handover/ai-direct/entries/20260223_stage1_status.md`

## Update 2026-02-24 04:16:00 +0800 (omega-vm -> windows Reachability Fix Landed)

- Corrected diagnosis: prior `CRITICAL / DOWN` call for Windows was a false-positive caused by intermittent tailnet path rebuild, not confirmed OS crash.
- New RCA + landed-fix entry:
  - `handover/ai-direct/entries/20260224_041600_omega_vm_windows_connectivity_rca_fix.md`
- Landed stabilization:
  - Windows keepalive task `Omega_Tailscale_Keepalive` (running)
  - `C:\Omega_vNext\tools\windows_tailscale_keepalive.ps1` (120s loop keepalive)
  - `tools/check_windows_from_omega.sh` (retry/multi-signal probe, anti-false-alarm)
- Verification:
  - omega->windows repeated probe window passed (5/5 ping+tcp22)
  - Linux Stage1 still active (`DONE=426`)
  - Windows Stage1 shard complete (`DONE=191`, task `Ready`)

## Update 2026-02-23 04:05:00 +0000 (System Status Check)

- **Linux (100.64.97.113):** 🟢 **ACTIVE**. Shards 0, 1, 2 processing early 2025. 422 files completed. Stable bypassing ZFS.
- **Windows (100.123.90.25):** Historical note only. This CRITICAL conclusion was superseded by 2026-02-24 RCA (intermittent tailnet reachability, not confirmed OS crash).
- **Handover Entry:** `handover/ai-direct/entries/20260223_stage1_status.md`

## Update 2026-02-23 08:18:19 +0800 (Stage2 Repeated-Scan Fix Landed)

- New landed entry:
  - `handover/ai-direct/entries/20260223_081819_stage2_single_scan_optimization.md`
- `tools/stage2_physics_compute.py` optimized:
  - removed repeated `lf.filter(...).collect()` full-file re-scan pattern
  - added single-pass parquet row-group traversal and complete-symbol batching
  - retained `batch_size` + `gc.collect()` + atomic tmp-rename safety path.
- Verification:
  - py_compile pass
  - synthetic multi-rowgroup symbol iterator smoke pass
  - stage1 continuity unchanged (Linux service active, Windows task running).

## Update 2026-02-23 08:14:20 +0800 (Legacy Pipeline Archived + Priority Check)

- New landed entry:
  - `handover/ai-direct/entries/20260223_081420_legacy_pipeline_archived_and_fix_priorities.md`
- Archived and blocked old entry path:
  - archived: `archive/legacy_v50/pipeline_runner_v50.py`
  - archived: `archive/legacy_v50/pipeline_engine_framer_v52.py`
  - active-path guards:
    - `pipeline_runner.py` now exits with deprecation message
    - `pipeline/engine/framer.py` now raises runtime error on use
- Doc drift cleaned to reduce operator misuse:
  - `README.md`
  - `pipeline/README.md`
  - `jobs/windows_v40/README.md`
  - `archive/legacy_v50/README.md`
- Remaining issue priority decision:
  - immediate repair target: `tools/stage2_physics_compute.py` repeated scan loop
  - keep current two-stage architecture and stability guards
  - “for-loop over rows” is not primary slowdown cause (Numba JIT hot loop already in place).

## Update 2026-02-23 08:00:44 +0800 (Linux 100G Utilization RCA + CPUQuota Fix)

- New landed entry:
  - `handover/ai-direct/entries/20260223_080044_linux_100g_best_practice_cpuquota_rca.md`
- Internet best-practice + on-host evidence conclusion:
  - Linux was not memory-bound at this stage.
  - Structural bottleneck was `CPUQuota=95%` in `heavy-workload.slice`, which effectively constrained workloads to ~1 CPU.
- Live evidence captured:
  - before: `cpu.max=95000 100000`
  - after fix: `cpu.max=2400000 100000` (~24 CPU quota)
  - memory controller remained healthy (`memory.events` oom/kill all zero, memory PSI zero).
- Host landed change:
  - updated `CPUQuota=2400%` for heavy slice config (base + drop-in), then reloaded systemd.
- Runtime state after landing:
  - Linux stage1 unit remains active: `omega_stage1_linux_fix_20260223_074804.service`
  - no new SemLock storm after previous single-process guardrail
  - Windows stage1 task still `Running`.

## Update 2026-02-23 01:22:00 +0800 (Dual Stage1 + Night Watch)

- New landed entry:
  - `handover/ai-direct/entries/20260223_012200_dual_stage1_gitpull_and_night_watch.md`
- User-directed `git pull main` executed on both nodes:
  - Linux: already up to date.
  - Windows: fast-forward to `fbd5c8b`.
- Windows verification after pull:
  - `Omega_v62_stage1_win` remains `Running`.
  - `stage1_windows_base_etl.py` process present (PID observed: `14124`).
  - no restart needed/performed on Windows.
- Linux Stage1 relaunched and confirmed:
  - unit `omega_stage1_linux_sleep_20260223_011644.service`
  - running in `heavy-workload.slice`
  - stage1 process present (PID observed: `10254`).
- Linux overnight supervisor deployed and running:
  - `/home/zepher/work/Omega_vNext/tools/linux_stage1_supervisor.sh`
  - poll interval `120s`
  - auto-relaunch path uses guarded launcher
  - pidfile `/home/zepher/work/Omega_vNext/artifacts/runtime/linux_stage1_supervisor.pid`
  - log `/home/zepher/work/Omega_vNext/audit/linux_stage1_supervisor.log`.

## Update 2026-02-23 01:11:00 +0800 (Post-Reboot RCA + Hardening)

- New landed entry:
  - `handover/ai-direct/entries/20260223_011100_linux_freeze_post_reboot_rca_hardening.md`
- This recurrence root cause is confirmed as:
  - `user-1000.slice` memcg OOM regression (`MemoryMax=20G`) in crash window `2026-02-23 00:39:50` to `00:40:08` (+0800).
  - Not a new concurrent ZFS suspend event in this specific crash.
- Landed anti-regression code:
  - `tools/stage1_linux_base_etl.py`
    - hard-refuse outside `heavy-workload.slice`
    - best-effort raise `oom_score_adj` to `300` for main/workers
  - `tools/launch_linux_stage1_heavy_slice.sh`
    - enforced `OOMScoreAdjust=300`
    - run as caller UID/GID (`--uid/--gid`), not root
    - interpreter preflight (`.venv` first, `import polars` gate)
    - improved post-launch validation for short-lived units
- Landed host config cleanup (Linux):
  - Removed invalid `MemoryPressureWatch=/proc/pressure/memory` lines from:
    - `/etc/systemd/system/user-.slice.d/memory.conf`
    - `/etc/systemd/system/heavy-workload.slice.d/limits.conf`
    - `/etc/systemd/system/ssh-sessions.slice.d/limits.conf`
  - `systemctl daemon-reload` executed; no new parse warnings after `01:07:00`.
- Verification snapshot:
  - Direct stage1 execution now fails fast outside heavy slice.
  - Launcher smoke (`--years 2099`) starts in `heavy-workload.slice` and exits cleanly.
  - No active `omega_stage1*` units/processes remain.

## Update 2026-02-23 00:26:32 +0800 (Research + Landing)

- Added best-practice research entry:
  - `handover/ai-direct/entries/20260223_002256_linux_freeze_best_practice_research.md`
- Landed Linux guarded launcher:
  - `tools/launch_linux_stage1_heavy_slice.sh`
  - function: force Stage1 into `heavy-workload.slice` via `systemd-run`, avoiding `user.slice` (`20G`) memcg trap.
- Linux dry-run verification (executed on host):
  - `MemoryHigh=16G / MemoryMax=20G` for `user-1000.slice`
  - `MemoryHigh=90G / MemoryMax=100G` for `heavy-workload.slice`
  - generated command includes:
    - `--slice=heavy-workload.slice`
    - `--property=OOMPolicy=kill`
    - `StandardOutput/StandardError=append:/home/zepher/work/Omega_vNext/audit/stage1_linux_v62.log`
- Current point-in-time runtime truth:
  - Linux host is up and reachable.
  - No active Stage1 ETL process was observed during this landing window.

## Historical Status Snapshot (2026-02-22, Pre-Landing)

The block below is preserved from the prior checkpoint before this landing session.
Treat it as historical context, not current truth.

1. **Linux Node (192.168.3.113):**
   - Controlled reboot executed at `2026-02-22 23:18:40 +0800`; SSH restored at `23:19:19 +0800`.
   - Cache gate re-validated:
     - `findmnt -T /home/zepher/framing_cache` => `/home` mounted on 4T `Samsung SSD 990 PRO`.
   - Relaunched command:
     - `python3 -u tools/stage1_linux_base_etl.py --years 2023,2024,2025,2026 --total-shards 4 --shard 0,1,2 --workers 1`
   - Current signals:
     - Stage1 process alive (`PID=3779`).
     - Active processing in log (`_scan_split_l2_quotes SUCCESS` lines streaming).
     - `LOG_MTIME=2026-02-22 23:23:20 +0800`, `SIZE=496161`.
     - `DONE_HASH=0` (still first large archive/day), but semantic activity is moving.
     - SSH responsiveness stable after relaunch (`~0.16-0.25s` over 5 probes).
2. **Windows Node (192.168.3.112):**
   - Relaunched via Task Scheduler: `Omega_v62_stage1_win` with `--total-shards 4 --shard 3 --workers 1`
   - Last known status from prior checkpoint: `Running`
   - Last known progress: `DONE_HASH=44`, log updating (`audit\\stage1_windows_v62.log`).
   - This session did not refresh Windows via `ssh_ps.py` due local tunnel/proxy closure (`127.0.0.1:7897`).

## Observed Drift / Contract Notes

- Node git hashes are not aligned:
  - Linux: `3a670fe`
  - Windows: `b07c2229`
  This is acceptable for immediate rescue but must be unified before final artifact merge/comparison.
- Local controller workspace includes startup fixes (path de-hardcode + kernel import regression fix), but these fixes were not yet rolled out to workers in this run window.
- Handover control plane has been upgraded with a unified first entry:
  - `handover/ENTRYPOINT.md`
  - `handover/ops/FILE_TOPOLOGY.md`
  - `handover/ops/SKILLS_TOOLS_INDEX.md`
  - `handover/ops/ACCESS_BOOTSTRAP.md`
  - `handover/ops/HOSTS_REGISTRY.yaml`
  - `tools/agent_handover_preflight.sh`
- Preflight currently reports SSH alias gaps on controller:
  - missing `windows1-w1`
  - missing `linux1-lx`
  direct IP login still works, but alias normalization is required for unattended multi-agent handoff.

## Linux Cache Policy (MANDATORY)

- Operator hard rule: Linux Stage1/ETL temporary cache must use the 4T Samsung 990 Pro path only.
- Canonical cache path: `/home/zepher/framing_cache`
- This applies to all runtime temp surfaces:
  - `POLARS_TEMP_DIR`
  - `TMPDIR`
  - per-day extraction folders `omega_framing_*`
- Pre-launch gate (must pass before Stage1 start/restart):
  - `findmnt -T /home/zepher/framing_cache`
  - `lsblk -o NAME,SIZE,MODEL,MOUNTPOINTS | rg -n "990|framing_cache|nvme"`
- If cache path is not on the expected 4T 990 Pro device, stop launch and fix mount/bind first.

## Immediate Action Required for Next Agent

Read in order:
1. `handover/ai-direct/entries/20260223_012200_dual_stage1_gitpull_and_night_watch.md`
2. `handover/ai-direct/entries/20260223_011100_linux_freeze_post_reboot_rca_hardening.md`
3. `handover/ai-direct/entries/20260223_002256_linux_freeze_best_practice_research.md`
4. `handover/ai-direct/entries/20260223_002630_linux_freeze_best_practice_landed_updates.md`
5. `handover/ai-direct/entries/20260222_172304_dual_node_deadlock.md`
6. `handover/ai-direct/entries/20260222_192759_v62_dual_stage1_relaunch_monitor.md`
7. `handover/ai-direct/entries/20260222_223809_v62_linux_reboot_recovery.md`
8. `handover/ai-direct/entries/20260222_232306_v62_linux_redebug_reboot_relaunch.md`
9. `handover/ai-direct/entries/20260222_235519_multi_agent_unified_entrypoint.md`

**DO NOT ATTEMPT TO RUN STAGE 2 PHYSICS.**
Priority now:
1. Keep current overnight run alive: Windows task `Omega_v62_stage1_win`, Linux Stage1 unit, and Linux supervisor.
2. For any manual Linux relaunch, use only `tools/launch_linux_stage1_heavy_slice.sh` (do not start directly from interactive shell).
3. Continue low-overhead monitoring only (`done` count + log tail + launcher/process state), avoid heavy WMI/perf loops.
4. Linux guardrail: if no `DONE` increase and no log growth for >20 minutes, escalate immediately (capture process state, then controlled reboot/relaunch).
5. Normalize controller SSH aliases (`windows1-w1`, `linux1-lx`) per `handover/ops/ACCESS_BOOTSTRAP.md`.

---

## Update 2026-02-23 10:54:56 +0800 (Stage1 Non-Reset Hardening)

- Goal: fix Stage1 operational issues without restarting framing from scratch.
- Landed:
  - `tools/stage1_resume_utils.py` (cross-hash resume + marker self-heal)
  - `tools/stage1_linux_base_etl.py` (date-level hash-agnostic skip + stale marker/tmp handling)
  - `tools/stage1_windows_base_etl.py` (same hardening)
  - `tools/stage2_physics_compute.py` (same-date mixed-hash input de-dup guard)
- Tests passed:
  - `python3 tests/test_stage1_resume_utils.py`
  - `python3 tests/test_stage2_input_dedupe.py`
  - `python3 tests/test_stage1_incremental_writer_equivalence.py`
- Worker sync completed:
  - Linux: `/home/zepher/work/Omega_vNext/tools/*` patched + `py_compile` pass
  - Windows: `C:\Omega_vNext\tools\*` patched + `py_compile` pass
- Runtime snapshot (point-in-time):
  - Linux output: `64 parquet / 64 done / 0 tmp` (`fbd5c8b`)
  - Windows output: `126 parquet / 126 done / 0 tmp` (`b07c2229`)
- Detailed handover: `handover/ai-direct/entries/20260223_105456_stage1_resume_crosshash_hardening.md`

---

## Update 2026-02-23 18:50:00 +0800 (V62 Framing Rebuild Alignment Summary)

- New landed entry:
  - `handover/ai-direct/entries/20260223_185000_v62_framing_rebuild_alignment_summary.md`
- Confirmed full implementation of V62 blueprint mandates:
  - Two-Stage Orthogonal Decoupling (Stage 1 I/O vs Stage 2 Physics).
  - GIL Eradication via Numba JIT kernels (@njit parallel=True).
  - Mathematical Safety (log(0) clipping) and Time-Arrow (Temporal Rolling) enforcement.
  - Operational Stability (CPUQuota=2400% on Linux, NVMe Cache routing).
- Current Mission: Monitoring Dual Stage 1 runs on Linux and Windows.

---

## Update 2026-02-24 04:22:00 +0800 (Append-Only: omega-vm Connectivity Hardening)

- This block is append-only (no overwrite of existing LATEST content).
- Connectivity RCA and landed fixes are recorded in:
  - `handover/ai-direct/entries/20260224_041600_omega_vm_windows_connectivity_rca_fix.md`
- False-positive correction:
  - `omega-vm -> windows1-w1` intermittent timeout window is treated as transport path rebuild, not immediate OS hard-crash.
- Landed mitigations:
  - Windows keepalive task: `Omega_Tailscale_Keepalive` (running)
  - Windows keepalive script: `C:\Omega_vNext\tools\windows_tailscale_keepalive.ps1`
  - omega-vm retry probe: `tools/check_windows_from_omega.sh`
- Operational gate update:
  - Do not declare `CRITICAL / DOWN` from a single timeout sample.
  - Require retry-window + multi-signal probe (`tailscale ping`, `TCP/22`, `ssh`) before escalation.
