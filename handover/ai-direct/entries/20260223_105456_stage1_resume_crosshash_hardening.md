# Stage1 Cross-Hash Resume Hardening (No Full Reframe)

- Timestamp: 2026-02-23 10:54:56 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- Avoid restarting framing from scratch while fixing current Stage1 operational risks:
  - cross-host hash drift (`linux=fbd5c8b`, `windows=b07c2229`)
  - resume fragility when `.done` marker and parquet payload become inconsistent
  - potential Stage2 duplicate processing when mixed-hash same-date chunks coexist

## 2) Landed Code Changes (Local Repo)

1. New Stage1 resume utility module:
   - `tools/stage1_resume_utils.py`
   - Adds:
     - `find_existing_done_for_date(...)` (hash-agnostic date resume)
     - `clear_stale_done_marker(...)`
     - `ensure_done_for_existing_parquet(...)`

2. Linux Stage1 hardening:
   - `tools/stage1_linux_base_etl.py`
   - Behavior updates (no feature math change):
     - skip if current hash `.done` + parquet exists
     - remove stale `.done` if parquet missing
     - auto-repair missing `.done` for existing parquet
     - cross-hash skip by date (`YYYYMMDD_*.parquet.done`)
     - remove stale `.parquet.tmp` before writing

3. Windows Stage1 hardening:
   - `tools/stage1_windows_base_etl.py`
   - Same resume protections as Linux.

4. Stage2 input safety hardening:
   - `tools/stage2_physics_compute.py`
   - Adds date-level input de-duplication:
     - if mixed hashes produce duplicate date files, keep newest by mtime
     - drop older same-date duplicates to prevent double-processing

## 3) Tests Added / Verified

- Added:
  - `tests/test_stage1_resume_utils.py`
  - `tests/test_stage2_input_dedupe.py`
- Verified pass:
  - `python3 tests/test_stage1_resume_utils.py`
  - `python3 tests/test_stage2_input_dedupe.py`
  - `python3 tests/test_stage1_incremental_writer_equivalence.py`

## 4) Deployment to Workers

- Linux (`/home/zepher/work/Omega_vNext/tools`):
  - synced:
    - `stage1_resume_utils.py`
    - `stage1_linux_base_etl.py`
  - verified:
    - `python3 -m py_compile tools/stage1_resume_utils.py tools/stage1_linux_base_etl.py`

- Windows (`C:\Omega_vNext\tools`):
  - synced:
    - `stage1_resume_utils.py`
    - `stage1_windows_base_etl.py`
  - verified:
    - `python -m py_compile tools\stage1_resume_utils.py tools\stage1_windows_base_etl.py`

## 5) Runtime Status Snapshot

- Linux Stage1 currently running with worker=1 manual unit:
  - `omega_stage1_linux_manual_20260223_093756.service`
- Linux watchdog remains stopped (no auto-relaunch process).
- Output audit snapshots (point-in-time):
  - Linux host output:
    - root: `/omega_pool/parquet_data/v62_base_l1/host=linux1`
    - `64 parquet / 64 done / 0 tmp` (hash `fbd5c8b`)
  - Windows host output:
    - root: `D:\Omega_frames\v62_base_l1\host=windows1`
    - `126 parquet / 126 done / 0 tmp` (hash `b07c2229`)

## 6) Effect on Existing Results

- Existing parquet payloads are preserved.
- No full reframe required.
- Future restarts after hash changes can continue by date without recomputing already completed days.
- Stage2 now guards against same-date mixed-hash duplicate processing.
