# Linux 100G Memory Utilization RCA + Best-Practice Landing

- Timestamp: 2026-02-23 08:00:44 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- Investigate whether Linux 100G memory headroom is being wasted, identify why Linux is unstable/frequent while Windows is stable, and land best-practice aligned fixes.

## 2) Completed in This Session

- Confirmed the historical Linux crash signature is a multiprocessing semaphore rebuild storm:
  - `SemLock._rebuild -> FileNotFoundError` repeated in `audit/stage1_linux_v62.log` pre-fix section.
  - Existing stage1 code fix is active: `--workers 1` now enters single-process guardrail path (no Pool path).
- Collected live Linux cgroup and runtime evidence:
  - Host memory: `123Gi`; heavy slice `MemoryMax=100G`, `MemoryHigh=90G`.
  - `memory.events` and `memory.pressure` under heavy slice are all zero (`oom=0`, `oom_kill=0`, pressure `avg10/60/300=0.00`), so current bottleneck is not memory pressure.
- Identified structural throughput limiter:
  - `heavy-workload.slice` had `CPUQuota=95%` -> cgroup `cpu.max=95000 100000`.
  - This is effectively <1 CPU of quota, not 95% of a 32-core host.
  - `cpu.stat` showed severe historical throttling (`nr_throttled` almost equal to `nr_periods`).
- Landed host fix:
  - Updated heavy slice CPU quota to multi-core quota `CPUQuota=2400%` (~24 cores cap).
  - Verified `cpu.max=2400000 100000`.
  - Verified post-change sampling window no additional throttle growth (`nr_throttled` unchanged while `usage_usec` increased).

## 3) Current Runtime Status

- Mac: Controller active.
- Windows1:
  - Task `Omega_v62_stage1_win` is `Running`.
  - Stage1 command observed: `tools\\stage1_windows_base_etl.py ... --workers 1`.
- Linux1:
  - `omega_stage1_linux_fix_20260223_074804.service` active in `heavy-workload.slice`.
  - Stage1 process alive (`tools/stage1_linux_base_etl.py ... --workers 1`).
  - Current done files for hash `fbd5c8b`: `6` (check-point-in-time).

## 4) Critical Findings / Risks

- Core reason Linux looked “wasteful”:
  - Not memory exhaustion; it was CPU quota misconfiguration + prior multiprocessing regression.
- Why Windows appears more stable:
  - Windows path is also running `--workers 1`, but does not carry this Linux cgroup CPUQuota choke and did not hit the Linux-specific SemLock failure pattern seen in historical logs.
- Remaining risk:
  - Linux stage1 still hard-pins `POLARS_MAX_THREADS=4`; after CPU quota uncap, throughput may still underuse CPU capacity unless threads/work decomposition is tuned with benchmarks.

## 5) Artifacts / Paths

- New handover entry:
  - `handover/ai-direct/entries/20260223_080044_linux_100g_best_practice_cpuquota_rca.md`
- Runtime code references:
  - `tools/stage1_linux_base_etl.py`
  - `tools/stage1_windows_base_etl.py`
- Linux logs/evidence:
  - `/home/zepher/work/Omega_vNext/audit/stage1_linux_v62.log`
  - `/sys/fs/cgroup/heavy.slice/heavy-workload.slice/cpu.max`
  - `/sys/fs/cgroup/heavy.slice/heavy-workload.slice/cpu.stat`
  - `/sys/fs/cgroup/heavy.slice/heavy-workload.slice/memory.events`

## 6) Commands Executed (Key Only)

- `systemctl show heavy-workload.slice -p MemoryHigh -p MemoryMax -p CPUQuotaPerSecUSec`
- `cat /sys/fs/cgroup/heavy.slice/heavy-workload.slice/{cpu.max,cpu.stat,memory.events,memory.pressure}`
- `rg -n "SemLock|FileNotFoundError|RESTART|GUARDRAIL" audit/stage1_linux_v62.log`
- `sudo systemctl set-property heavy-workload.slice CPUQuota=2400%`
- `sudo sed -i "s/^CPUQuota=.*/CPUQuota=2400%/" /etc/systemd/system/heavy-workload.slice{,.d/limits.conf}`

## 7) Exact Next Steps

1. Keep current Linux run on single-process stability path until this shard completes.
2. Run one controlled benchmark matrix (`POLARS_MAX_THREADS=4/8/12`) with `workers=1` and compare day-level throughput + memory peak.
3. If stable, evaluate dual-unit sharding (`two stage1 units`, each `workers=1`) to use more of 100G safely while avoiding Pool/SemLock regressions.

## 8) External Source Index

- [Python multiprocessing docs](https://docs.python.org/3/library/multiprocessing.html)
- [Polars multiprocessing guide](https://docs.pola.rs/user-guide/misc/multiprocessing/)
- [Linux cgroup v2 admin guide](https://docs.kernel.org/5.15/admin-guide/cgroup-v2.html)
- [systemd resource control](https://www.freedesktop.org/software/systemd/man/devel/systemd.resource-control.html)
