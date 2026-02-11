# v40 Pipeline Debug - Phase 1 + Phase 2 Closure (2026-02-08)

## Scope
- Entrypoint/orchestration hardening for Windows v40 pipeline
- Train/backtest runner startup and fail-closed robustness
- No edits to math core (`omega_v3_core/kernel.py`, `omega_v3_core/omega_math_core.py`)

## Phase 1 - Orchestration Hardening

### 1) Entrypoint execution safety
- File: `jobs/windows_v40/start_v40_pipeline_win.ps1`
- Changes:
  - Wrapped root `Push-Location` with `try/finally` to guarantee `Pop-Location` on failure.
  - Added dependency prechecks (`Assert-RepoPathExists`) for required runtime scripts.

### 2) Dataset split preflight gating
- File: `jobs/windows_v40/start_v40_pipeline_win.ps1`
- Changes:
  - Added explicit preflight stage invocation (`tools/preflight_dataset_split_v40.py`) before train/backtest.
  - Added switch passthrough `-SkipDatasetSplitPreflight` in wrapper.

### 3) Overlap guard path normalization
- File: `jobs/windows_v40/start_v40_pipeline_win.ps1`
- Changes:
  - Custom manifest overlap checks now normalize relative entries to absolute paths.
  - Added BOM trim on manifest entries to avoid false misses / path parse issues.

### 4) Startup observability knobs
- Files:
  - `jobs/windows_v40/start_v40_pipeline_win.ps1`
  - `jobs/windows_v40/run_v40_train_backtest_win.ps1`
- Changes:
  - Added `TrainPlanningProgressEveryLines` + `BacktestPlanningProgressEveryLines` parameters (default 50,000).
  - Wired to train/backtest runner CLI planning heartbeat.

## Phase 2 - Runner Robustness

### 1) Train runner stream manifest processing
- File: `parallel_trainer/run_parallel_v31.py`
- Changes:
  - Replaced full-manifest task materialization with chunked stream iterator (`_iter_manifest_task_chunks`).
  - Prevents multi-million `Path` list buildup before worker start.
  - Added planning heartbeat status during scan.

### 2) Train fail-closed worker/schema error semantics
- File: `parallel_trainer/run_parallel_v31.py`
- Changes:
  - Worker now returns structured result tags (`ok`, `empty_*`, `missing_features`, `worker_exception:*`).
  - Added `--max-worker-errors` (default `0`), with hard-fail status emission on exceed.
  - Status JSON now exposes `files_schema_errors` and `files_worker_errors`.

### 3) Backtest runner fail-closed semantics
- File: `parallel_trainer/run_parallel_backtest_v31.py`
- Changes:
  - Added `--max-file-errors` (default `0`) and hard-fail when exceeded.
  - Added `--fail-on-audit-failed` / `--allow-audit-failed` (default fail-closed).
  - Final audit `FAILED` now hard-fails by default in production path.

### 4) Backtest policy provenance hardening
- File: `parallel_trainer/run_parallel_backtest_v31.py`
- Changes:
  - Removed hardcoded fallback `artifacts/checkpoint_rows_31793682.pkl`.
  - If `--policy` absent: auto-select latest `checkpoint_rows_*.pkl`.

### 5) Backtest stream manifest processing
- File: `parallel_trainer/run_parallel_backtest_v31.py`
- Changes:
  - Added chunked stream file-list mode (`_iter_file_list_chunks`) with planning heartbeat.
  - Avoids preloading massive file-list into memory before processing.

### 6) Smoke compatibility with fail-closed backtest defaults
- File: `jobs/windows_v40/run_v40_smoke_win.ps1`
- Change:
  - Smoke backtest now passes `--allow-audit-failed` to keep tiny-sample smoke focused on runtime continuity.

### 7) BOM-safe manifest parsing
- Files:
  - `parallel_trainer/run_parallel_v31.py`
  - `parallel_trainer/run_parallel_backtest_v31.py`
  - `jobs/windows_v40/start_v40_pipeline_win.ps1`
- Change:
  - Manifest line parsing now strips UTF-8 BOM on first-line paths.

## Verification Evidence

### Static gates
- `python -m py_compile parallel_trainer/run_parallel_v31.py parallel_trainer/run_parallel_backtest_v31.py tools/preflight_dataset_split_v40.py` -> PASS
- `python tools/check_readme_sync.py` -> PASS
- PowerShell syntax parse:
  - `jobs/windows_v40/start_v40_pipeline_win.ps1` -> PASS
  - `jobs/windows_v40/run_v40_train_backtest_win.ps1` -> PASS
  - `jobs/windows_v40/run_v40_smoke_win.ps1` -> PASS

### Runtime probes (elevated)
1. Train stream startup probe (`max-files=1`) -> PASS
   - immediate `[Plan] loading file list (stream mode)`
   - no long pre-start stall
   - status: `completed` with `files_worker_errors=0`

2. Train invalid-path probe (`max-files=1`) -> EXPECTED FAIL-CLOSED
   - status: `failed`
   - error: worker/schema errors exceeded threshold

3. Backtest probe (default fail-on-audit) -> EXPECTED FAIL-CLOSED
   - final audit `FAILED` -> process exits non-zero
   - status JSON `status=failed`

4. Backtest probe (`--allow-audit-failed`) -> PASS (runtime continuity mode)
   - process exits zero with `final_audit_status=FAILED`

5. Backtest auto-policy probe (no `--policy`) -> PASS
   - selected latest checkpoint (no hardcoded legacy fallback)

6. BOM manifest probe -> PASS after patch
   - first-line BOM path no longer causes os error 123

## Files Changed In This Phase
- `jobs/windows_v40/start_v40_pipeline_win.ps1`
- `jobs/windows_v40/run_v40_train_backtest_win.ps1`
- `jobs/windows_v40/run_v40_smoke_win.ps1`
- `jobs/windows_v40/README.md`
- `parallel_trainer/run_parallel_v31.py`
- `parallel_trainer/run_parallel_backtest_v31.py`

## Phase Gate Decision
- Phase 1: PASS
- Phase 2: PASS
- Ready for overall recursive audit and user approval gate before full train/backtest rerun.
