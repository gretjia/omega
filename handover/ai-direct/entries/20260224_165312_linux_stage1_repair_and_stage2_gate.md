---
entry_id: 20260224_165312_linux_stage1_repair_and_stage2_gate
task_id: TASK-V62-STAGE1-ARCHIVE-RECOVERY
timestamp_local: 2026-02-24 16:53:12 +0800
timestamp_utc: 2026-02-24 08:53:12 +0000
operator: Codex (GPT-5)
role: operator
branch: main
git_head: e682bf5
hosts_touched: [linux1-lx, windows1-w1, controller]
status: in_progress
---

## 1. Objective

- Verify Linux Stage1 completion state.
- Recover failed Linux raw archives from Windows good copies.
- Re-run Linux Stage1 to backfill failed dates.
- Check Windows Stage2 progress and decide Linux Stage2 launch timing.

## 2. Scope

- In scope: Linux/Windows operational recovery, archive replacement, Stage1 backfill verification, Stage2 readiness gate.
- Out of scope: Stage2 algorithm/code changes.

## 3. Actions Taken

1. Verified Linux Stage1 status and parsed latest run block.
2. Confirmed 12 Linux input archives were failing with `7z` `Headers Error`.
3. Verified corresponding 12 archives on Windows were healthy (`7z l` rc=0).
4. Copied healthy archives from Windows to Linux as `.restore` files, validated size + `7z l`, then atomically swapped originals to `.bad_<timestamp>` backups.
5. Relaunched Linux Stage1 twice (first for spot repair, second for full backfill consistency).
6. Final Linux Stage1 backfill run finished with `ERROR=0` and `FRAMING_COMPLETE=1`.
7. Checked Windows Stage2 progress.
8. Tested Linux Stage2 launch and found runtime dependency blocker (`No module named 'numba'`), then stopped failing unit.

## 4. Evidence

- Linux Stage1 final backfill unit:
  - `omega_stage1_linux_20260224_160352.service`
  - `Result=success`, `FRAMING_COMPLETE=1`
  - run block metrics: `ASSIGNED=555`, `COMPLETED=10`, `SKIPPED=545`, `ERROR=0`
- Recovered date set (all DONE=1 after backfill):
  - `20241104, 20241107, 20241111, 20241113, 20241114, 20241115, 20241119, 20241121, 20241202, 20241211, 20241204, 20241212`
- Windows Stage2 snapshot at `2026-02-24 16:53 +0800`:
  - `WIN_STAGE2_INPUT=191`
  - `WIN_STAGE2_DONE=113`
  - process active: `stage2_physics_compute.py --workers 1`
- Linux Stage2 gate:
  - attempted unit: `omega_stage2_linux_20260224_165032`
  - failure pattern in log: repeated `CRITICAL Error: No module named 'numba'`
  - dependency check: `NUMBA_IMPORT_RC=1`

## 5. Risks / Open Issues

- Linux Stage2 cannot proceed until `numba` is installed in `/home/zepher/work/Omega_vNext/.venv`.
- Worker git hashes are currently drifted (`linux1: e26f3dc`, `windows1: b42f110`) and should be normalized after controller push.

## 6. Changes Made

- Data-plane operational changes only:
  - Replaced broken Linux raw archives with verified Windows copies.
  - Preserved old broken files as `*.7z.bad_20260224_*` backups.
- No code changes in this entry.

## 7. Next Actions (Exact)

1. Update `handover/ai-direct/LATEST.md` and `handover/ops/ACTIVE_PROJECTS.md` with this snapshot.
2. Commit/push updated handover docs to GitHub.
3. Pull latest repo on windows1 + linux1 + omega-vm.
4. Install `numba` on linux1 `.venv` if still missing.
5. Launch Linux Stage2 in `heavy-workload.slice` and verify done-marker growth.

## 8. LATEST.md Delta

- Refresh metadata timestamps.
- Mark Linux Stage1 as `COMPLETED` after archive recovery.
- Update Windows Stage2 progress to `113/191` in-progress.
- Add Linux Stage2 blocker: missing `numba`.

