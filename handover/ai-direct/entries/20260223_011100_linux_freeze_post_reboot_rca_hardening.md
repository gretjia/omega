# Linux Freeze Post-Reboot RCA + Hardening Landing

- Timestamp: 2026-02-23 01:11:00 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- After manual Linux reboot, identify why freeze recurred and land concrete anti-regression fixes.

## 2) Root Cause Confirmed (This Crash)

- Crash boot window: `2026-02-23 00:39:50` to `00:40:08` (+0800).
- Direct trigger: repeated memcg OOM in `user.slice/user-1000.slice` with hard cap `MemoryMax=20G`.
- Kernel evidence:
  - `memory: usage 24222012kB, limit 20971520kB`
  - `oom_memcg=/user.slice/user-1000.slice`
  - repeated `systemd invoked oom-killer` and desktop-session victims.
- Two large `python3` tasks stayed with `oom_score_adj=-1000`, which biased OOM victim selection away from these workers and amplified desktop freeze symptoms.
- In this crash window, no concurrent `zio ... error=5` / `pool suspended` signatures were observed.

## 3) Landed Code Changes (Repo)

1. `tools/stage1_linux_base_etl.py`
   - Added hard guardrail: refuse execution unless cgroup path is under `heavy-workload.slice` (override only via `OMEGA_STAGE1_ALLOW_USER_SLICE=1`).
   - Added OOM safety: raise process `oom_score_adj` to `300` (best effort), including worker initializer.
   - Added clear fatal diagnostics with launch instruction.
2. `tools/launch_linux_stage1_heavy_slice.sh`
   - Added `--property=OOMScoreAdjust=300`.
   - Added runtime validation logic to avoid false negatives on short-lived units.
   - Added interpreter selection:
     - prefer `<repo>/.venv/bin/python`
     - fallback `/usr/bin/python3`
     - preflight `import polars` check.
   - Added explicit `--uid $(id -u) --gid $(id -g)` so transient unit runs as operator user, not root.

## 4) Landed Host Config Changes (Linux)

- Removed invalid `MemoryPressureWatch=/proc/pressure/memory` from:
  - `/etc/systemd/system/user-.slice.d/memory.conf`
  - `/etc/systemd/system/heavy-workload.slice.d/limits.conf`
  - `/etc/systemd/system/ssh-sessions.slice.d/limits.conf`
- Executed `sudo systemctl daemon-reload`.
- Result: no new parse warnings after `2026-02-23 01:07:00 +0800`.

## 5) Verification Results

- Direct stage1 run from normal user session now hard-fails as expected:
  - fatal message reports current cgroup under `user.slice` and exits.
- Launcher dry-run shows enforced properties:
  - `--slice=heavy-workload.slice`
  - `--uid 1000 --gid 1000`
  - `--property=OOMScoreAdjust=300`
  - Python path resolved to `/home/zepher/work/Omega_vNext/.venv/bin/python`.
- Smoke run (`--years 2099`) via launcher:
  - unit started in `heavy-workload.slice`
  - clean deactivation with no stage1 error.
- Current state:
  - no loaded `omega_stage1*` units
  - no active stage1 ETL process.

## 6) Operational Rule (Must Keep)

- Linux Stage1 must be launched only by:
  - `bash tools/launch_linux_stage1_heavy_slice.sh -- <args>`
- Direct interactive execution of `tools/stage1_linux_base_etl.py` is intentionally blocked.
