# Active Projects Board

This file tracks in-flight initiatives. `handover/ai-direct/LATEST.md` remains the single current-state summary; this board stores deeper operational context.

## 1. Snapshot Metadata

- `updated_at_local`: 2026-03-08 08:55:06 +0000
- `updated_at_utc`: 2026-03-08 08:55:06 +0000
- `updated_by`: Codex (GPT-5)

## 2. In-Flight Work

### Project: V643-STAGE2-PATHO-EMPTY-FRAME-REMEDIATION

- Status: `IN_PROGRESS`
- Hosts: `controller`, `linux1-lx`, `windows1-w1`
- Goal: fix the normal `v643` Stage2 crash triggered after proactive pathological-symbol drop and prove the repaired three-file set is consumable by Stage3 forge as one input set
- Last signals:
  - unresolved files:
    - `20231219_b07c2229.parquet`
    - `20241128_b07c2229.parquet`
    - `20250908_fbd5c8b.parquet`
  - direct Linux rerun on the normal Stage2 path reproduces:
    - `Proactively dropping pathological symbol`
    - immediate `CRITICAL Error: index out of bounds`
  - local patch status:
    - `tools/stage2_physics_compute.py` hardened for zero-row symbol frames
    - local Stage2 regression suite passed: `15 passed in 5.47s`
  - forced fallback / pathology-discovery mode is explicitly out of scope for this remediation
- Active gates:
  - commit + push + deploy the local remediation patch
  - rerun unresolved files on Linux normal path
  - prove Stage3 forge consumption with `tools/forge_base_matrix.py --input-file-list ... --years 2023,2024,2025`
- Risks:
  - forge default year filter would silently drop the 2025 file if not overridden
  - mission is not complete unless the repaired files pass forge together, not just Stage2 individually

### Project: V62-STAGE1-LINUX

- Status: `COMPLETED`
- Host: `linux1-lx`
- Goal: complete Stage1 Base_L1 for shards `0,1,2`
- Last signals:
  - Stage1 recovery run finished with `Result=success`
  - run block: `ASSIGNED=555`, `COMPLETED=10`, `SKIPPED=545`, `ERROR=0`, `FRAMING_COMPLETE=1`
  - repaired archive dates all backfilled to done markers
- Notes:
  - repaired archives replaced from Windows copies
  - old broken files retained as `*.7z.bad_20260224_*`

### Project: V62-STAGE2-WINDOWS

- Status: `IN_PROGRESS`
- Host: `windows1-w1`
- Goal: produce Feature_L2 from completed Stage1 Base_L1
- Last signals (2026-02-24 16:53 +0800):
  - process active: `stage2_physics_compute.py --workers 1`
  - progress: `WIN_STAGE2_DONE=113 / 191`
  - log path in use: `D:\work\Omega_vNext\audit\stage2_compute.log`
- Risks:
  - throughput is moderate with single-worker mode

### Project: V62-STAGE2-LINUX

- Status: `BLOCKED`
- Host: `linux1-lx`
- Goal: produce Feature_L2 for `host=linux1` (input count `552`)
- Last signals:
  - stage2 unit launch tested
  - blocker hit immediately: `ModuleNotFoundError: No module named 'numba'`
  - unit stopped to avoid no-op churn
- Required action:
  - install `numba` in `/home/zepher/work/Omega_vNext/.venv`
  - relaunch stage2 under `heavy-workload.slice`

### Project: HANDOVER-MAINTENANCE

- Status: `IN_PROGRESS`
- Host: `controller`
- Goal: keep handover as canonical operational gateway
- Current task:
  - sync latest stage recovery + stage2 gate status
  - push docs to GitHub and normalize worker git state

## 3. Completed Recently

- Linux Stage1 bad-archive recovery and full backfill completion.
- `20241204` and `20241212` user-priority archives recovered and reprocessed successfully.

## 4. Update Rules

- Update this board when project state changes materially.
- Keep exact verification timestamps and host evidence.
- Mirror high-level status in `handover/ai-direct/LATEST.md`.
