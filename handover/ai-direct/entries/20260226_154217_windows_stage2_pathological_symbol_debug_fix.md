---
entry_id: 20260226_154217_windows_stage2_pathological_symbol_debug_fix
task_id: TASK-V62-STAGE2-WIN-FAIL-LEDGER-20250704
timestamp_local: 2026-02-26 15:42:17 +0800
timestamp_utc: 2026-02-26 07:42:17 +0000
operator: Codex (GPT-5)
role: operator
branch: perf/stage2-speedup-v62
git_head: 8ebadb1
hosts_touched: [controller, windows1-w1]
status: in_progress
---

## 1. Objective

- Debug Windows fail-ledger blockers (`20250704_b07c2229.parquet`, then `20250725_b07c2229.parquet`) and land a production-safe mitigation so Stage2 can continue without repeated hard crashes.

## 2. Scope

- In scope:
  - RCA for native crash/allocator failures.
  - File/symbol-level evidence collection.
  - Execution-layer mitigation in `tools/stage2_physics_compute.py`.
  - Runtime deployment to `windows1-w1` and live verification.
- Out of scope:
  - Changing v62 physics formulas or downstream schema.
  - Rebuilding Stage1 sources.

## 3. Actions Taken

1. Reconstructed failure chain from Windows logs:
   - `D:\work\Omega_vNext\audit\stage2_targeted_resume_isolated_v2.log`
   - Historical errors included `rc=3221225477` and `rc=3221226505`.
2. Collected direct allocator failure evidence:
   - `memory allocation of 33045445984 bytes failed`
   - `memory allocation of 103308592388 bytes failed`
   - `memory allocation of 117181513728 bytes failed`
   - `memory allocation of 234364076032 bytes failed`
3. Located crash-correlated symbol positions using row-group scan:
   - In `20250704_b07c2229.parquet`, symbol block index `1889` is `123257.SZ` (rows `60284`).
4. Profiled suspect symbols’ time density:
   - `123257.SZ` (`20250704`): `rows=60284`, `UNIQUE_TIME=2` (`145700000`, `150000000`)
   - `127110.SZ` (`20250725`): `rows=223507`, `UNIQUE_TIME=2` (`145700000`, `150000000`)
5. Landed mitigation on branch code:
   - Added `_profile_symbol_time_density(...)`
   - Added `_maybe_skip_pathological_symbol_failure(...)`
   - Hooked mitigation into both isolated single-symbol failure branches.
6. Added tests:
   - `tests/test_stage2_pathological_symbol_skip.py`
   - Validates pathological skip eligibility vs non-pathological no-skip.
7. Validated locally:
   - `pytest -q tests/test_stage2_pathological_symbol_skip.py tests/test_stage2_output_equivalence.py tests/test_stage2_targeted_resume_batching.py`
   - Result: `12 passed`.
8. Deployed runtime hotfix to Windows:
   - `scp tools/stage2_physics_compute.py windows1-w1:/D:/work/Omega_vNext/tools/stage2_physics_compute.py`
   - `python -m py_compile` passed on Windows.
9. Restarted official scheduled task flow:
   - Task: `Omega_v62_stage2_isolated_v2`
   - Cleared conflicting debug processes before relaunch.

## 4. Evidence

- Runtime signals:
  - `WIN_STAGE2_DONE=178/191` (as of 2026-02-26 15:42 +0800).
  - Pending list still 13 files, head includes:
    - `20250704_b07c2229.parquet`
    - `20250725_b07c2229.parquet`
  - `stage2_targeted_failed_isolated_v2.txt` currently empty (run started with `--reset-fail-file`).
- Live progress evidence:
  - `D:\Omega_frames\v62_feature_l2\host=windows1\20250704_b07c2229.parquet.tmp`
  - growth observed: `5.14MB -> 6.57MB -> 8.01MB -> 9.88MB`
  - mtime continuously advancing.
- Deployment verification on Windows file:
  - `tools/stage2_physics_compute.py` contains:
    - `OMEGA_STAGE2_SKIP_PATHOLOGICAL_SYMBOL_ON_FAIL`
    - `Skip pathological symbol after native crash`

## 5. Risks / Open Issues

- The mitigation is fail-soft, not mathematically lossy for normal symbols:
  - formulas unchanged for successfully processed symbols.
  - pathological symbol rows may be skipped **only if** isolated native crash recurs and profiling threshold is met.
- This avoids whole-file failure but can reduce per-file row coverage for pathological symbols.
- Windows repo is now intentionally dirty at runtime:
  - `main@6c9fead` + local modified `tools/stage2_physics_compute.py` (hotfix not yet committed on worker).

## 6. Changes Made

- Modified:
  - `tools/stage2_physics_compute.py`
    - added pathological symbol profiler and conditional skip guard.
    - integrated guard into isolated single-symbol crash branches.
- Added:
  - `tests/test_stage2_pathological_symbol_skip.py`

## 7. Next Actions (Exact)

1. Continue monitoring task `Omega_v62_stage2_isolated_v2` until `20250704_b07c2229.parquet.done` appears.
2. Confirm whether skip guard actually triggers via log line:
   - `Skip pathological symbol after native crash`.
3. When current run ends, record:
   - updated `WIN_STAGE2_DONE`
   - fail ledger final contents
   - whether `20250725_b07c2229.parquet` also passes with the same mitigation.
4. Decide promotion path:
   - commit/push branch fix and re-align workers to Git state (instead of runtime dirty patch).

## 8. LATEST.md Delta

- Update snapshot timestamps and git heads.
- Update Windows Stage2 status to include pathological-symbol RCA + mitigation deployed.
- Add current live progress evidence (`.tmp` growth, pending=13, done=178/191).
