# Windows v40 Pipeline (Legacy)

> **DEPRECATION NOTICE**: This pipeline is for OMEGA v4.0.
> For OMEGA v5.0 (Holographic Damper), please refer to the **root README.md**.
> Legacy fallback only: `python archive/legacy_v50/pipeline_runner_v50.py --stage frame`.

> Last updated: 2026-02-10 (full pipeline fixed-split launcher + pre-run clean + race winner summary output)

## Purpose
- Run v40 `frame -> train -> backtest` on Windows with:
  - detailed logs,
  - status JSON snapshots,
  - resumable execution,
  - strict train/backtest dataset split + overlap guard.
- Full-run handover note for Windows AI: `audit/v40_windows_fullrun_handover_2026-02-10.md`

## Entry
- Script: `jobs/windows_v40/start_v40_pipeline_win.ps1`
- Wrapper (train+backtest): `jobs/windows_v40/run_v40_train_backtest_win.ps1`
- Wrapper (full frame+train+backtest, fixed split): `jobs/windows_v40/run_v40_full_pipeline_fixed_split_win.ps1`
- Wrapper (smoke): `jobs/windows_v40/run_v40_smoke_win.ps1`
- Worker sweep benchmark (frame): `jobs/windows_v40/benchmark_v40_frame_win.ps1`
- Note: trainer/backtest executors keep historical filenames
  - `parallel_trainer/run_parallel_v31.py`
  - `parallel_trainer/run_parallel_backtest_v31.py`
  but are the active v40-compatible runtime path.

## Quick Start
```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_full_pipeline_fixed_split_win.ps1 -PurgeFrameOutput
```

This command is fixed to:
- train: `2023,2024`
- backtest: `2025` + `202601`
- optimized hardware defaults:
  - `FrameWorkers=12`, `FrameIoSlots=4`, `FrameSevenZipThreads=1`
  - `TrainWorkers=26`, `BacktestWorkers=20`
  - `TrainBatchRows=1000000`, `TrainCheckpointRows=2000000`
  - `Train/BacktestStageChunkFiles=48`, `Train/BacktestStageCopyWorkers=4`
  - `MemoryThreshold=88.0`
- pre-run cleanup included by default:
  - `audit/v40_runtime/windows/*` runtime artifacts
  - `C:/Omega_level2_stage`, `C:/Omega_train_stage`, `C:/Omega_backtest_stage`

Force clean rerun from scratch:
```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_full_pipeline_fixed_split_win.ps1 -PurgeFrameOutput -NoResume
```

Keep existing runtime/stage artifacts (debug only):
```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_full_pipeline_fixed_split_win.ps1 `
  -SkipRuntimeClean `
  -SkipStageClean
```

## Hassle-Free Next Step (full train+backtest)
```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_win.ps1
```
Precondition: `data/level2_frames_v40_win` already exists and frame stage is complete.
Force clean rerun (no resume):
```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_win.ps1 -NoResume
```

## Fixed Run Command (official split)
```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1
```
This command is fixed to:
- train: `2023,2024`
- backtest: `2025` + `202601`

Force fresh rerun:
```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1 -NoResume
```

## Strict Dataset Split (enforced)
- Pipeline now builds role manifests via `tools/build_dataset_manifest_v40.py`:
  - train: `audit/v40_runtime/windows/manifests/train_files.txt`
  - backtest: `audit/v40_runtime/windows/manifests/backtest_files.txt`
- Before train/backtest, pipeline runs fail-closed preflight:
  - `tools/preflight_dataset_split_v40.py`
  - output: `audit/v40_runtime/windows/manifests/split_preflight_status.json`
  - log: `audit/v40_runtime/windows/manifests/split_preflight.log`
- Default split comes from `config.py` `SplitConfig`:
  - `train_years=(2023, 2024)`
  - `test_years=(2025,)`
  - `test_year_months=(202601,)`
- Backtest manifest generation enforces no overlap with train manifest; overlap throws and stops pipeline.
- Override split when needed:
```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_win.ps1 `
  -TrainYears "2023,2024" `
  -BacktestYears "2025" `
  -BacktestYearMonths "202601"
```
- If you pass a custom `-BacktestFileList`, pipeline still performs overlap check against the train manifest by default.
- Diagnostic-only bypass (not recommended): `-AllowTrainBacktestOverlap`.
- Diagnostic-only preflight skip (not recommended): `-SkipDatasetSplitPreflight`.
- Train file-list execution is stream-scanned (chunked) to avoid large startup memory spikes on multi-million-file manifests.

## Reproducible Smoke (real frame -> train -> backtest)
```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_smoke_win.ps1 `
  -CondaExe "C:\Users\YOUR_USER\miniforge3\Scripts\conda.exe" `
  -CondaEnv OMEGA
```
Smoke outputs are isolated under `C:/Omega_v40_smoke/run_YYYYMMDD_HHMMSS/`.

## Stage-only Runs
```powershell
# frame only
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage frame

# train only
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage train

# backtest only
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage backtest
```

## Frame Benchmark (worker sweep)
Use this before full reruns to choose the best frame worker count on current machine/load:
```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\benchmark_v40_frame_win.ps1 `
  -Limit 800 `
  -Workers "12,16,20,22" `
  -IoSlots 4 `
  -FrameSevenZipThreads 1
```
Outputs:
- `audit/v40_runtime/windows/frame_bench/benchmark_summary.json`
- `audit/v40_runtime/windows/frame_bench/benchmark_summary.csv`

## Core Defaults (for 128GB unified memory)
- `FrameWorkers=12` (current benchmark winner under shared-disk pressure)
- `FrameIoSlots=4` (throttle concurrent copy+extract to reduce I/O contention)
- `FrameSevenZipThreads=1` (avoid worker*thread oversubscription in multi-process extraction)
- `FrameStageDir=C:/Omega_level2_stage`
- `TrainWorkers=26`
- `BacktestWorkers=20`
- `TrainBatchRows=1000000`
- `TrainCheckpointRows=2000000`
- `MemoryThreshold=88.0`
- `TrainStageDir=C:/Omega_train_stage`
- `TrainStageChunkFiles=48`
- `TrainStageCopyWorkers=4`
- `BacktestStageDir=C:/Omega_backtest_stage`
- `BacktestStageChunkFiles=48`
- `BacktestStageCopyWorkers=4`
- `BacktestStateSaveEveryFiles=200`
- `FrameGenerateReport=False` (default skip report to avoid frame-tail OOM/stall)
- `SkipFrameCompatibilityCheck=False` (default run compat gate before train/backtest)

Tune downward if concurrent workloads also occupy RAM.

## Frame Tail Safety (important)
- In full pipeline (`-Stage all`), frame now defaults to `--skip-report`.
- Reason: aggregate report path performs full `collect()` and may block stage chaining on huge datasets.
- Training/backtest do not depend on the report file.
- If you explicitly need the report in the same run:
```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage frame `
  -FrameGenerateReport `
  -FrameReportPath audit\level2_v3_audit_report.md
```

If you run `tools/run_l2_audit_driver.py` directly (advanced mode):
- report is now bounded by default (`--report-sample-files`, `--report-rows-per-file`)
- report failure is non-fatal by default
- use `--report-full` and `--report-fail-fatal` only when you explicitly accept memory risk

## Local C: Staging (Train/Backtest)
- `train` and `backtest` now default to local `C:` chunk staging (even when running scripts directly).
- Flow per chunk: copy parquet files to local stage -> process with workers -> remove chunk directory.
- Stage copy now supports internal copy pool (`--stage-copy-workers`), default wired by Windows wrapper:
  - train: `4`
  - backtest: `4`
- Staging copy uses file-content copy path (no metadata copy) to reduce per-file I/O overhead.
- This reduces shared-drive random I/O pressure and improves stability on long runs.
- Keep cleanup enabled by default; use `-NoCleanupTrainStage` / `-NoCleanupBacktestStage` only for debugging.
- To disable for A/B diagnostics only:
  - train: `--no-stage-local`
  - backtest: `--no-stage-local`
- Backtest state persistence is now decoupled from status cadence:
  - status heartbeat: `--save-every-files` (default `20`)
  - state snapshot: `--state-save-every-files` (default `200`)
  This reduces large JSON write pressure and lowers `WinError 5` lock-conflict probability.

## Log Encoding
- Pipeline `frame/train/backtest` logs are written as UTF-8 (instead of UTF-16), reducing log I/O volume and improving cross-platform tail/readability on macOS.

## Local C: Staging (Frame)
- `frame` also defaults to local copy + local stage; explicit local stage root is controlled by `-FrameStageDir` (default `C:/Omega_level2_stage`).
- Flow: copy archive to local stage (if `--copy-to-local`) -> extract/process -> cleanup worker dir.
- IO contention guard: `-FrameIoSlots` limits concurrent copy+extract phases; default `4`.
- Extraction scope defaults to CSV only (`--extract-csv-only`) to reduce unnecessary disk traffic. Use `-FrameExtractAll` only for diagnostics.
- Keep cleanup enabled by default; use `-NoCleanupFrameStage` only for debugging.
- To disable frame local-copy for diagnostics only: `--no-copy-to-local`.

## Default Policy
- v40 full pipeline now runs with staging enabled in all stages by default:
  - frame: local archive copy + local stage dir
  - train: local chunk staging
  - backtest: local chunk staging

Example (override stage chunk size):
```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage train `
  -TrainStageChunkFiles 32
```

## Runtime Artifacts
- Root: `audit/v40_runtime/windows/`
- Frame:
  - `audit/v40_runtime/windows/frame/frame.log`
  - `audit/v40_runtime/windows/frame/frame_status.json`
  - `audit/v40_runtime/windows/frame/frame_compat.log`
  - `audit/v40_runtime/windows/frame/frame_compat_status.json`
- Train:
  - `audit/v40_runtime/windows/train/train.log`
  - `audit/v40_runtime/windows/train/train_status.json`
- Backtest:
  - `audit/v40_runtime/windows/backtest/backtest.log`
  - `audit/v40_runtime/windows/backtest/backtest_status.json`
  - `audit/v40_runtime/windows/backtest/backtest_state.json`
  - `audit/v40_runtime/windows/backtest/race_winner_summary.json`
  - `audit/v40_runtime/windows/backtest/race_winner_summary.md`
- Manifests:
  - `audit/v40_runtime/windows/manifests/train_files.txt`
  - `audit/v40_runtime/windows/manifests/backtest_files.txt`
  - `audit/v40_runtime/windows/manifests/train_manifest_status.json`
  - `audit/v40_runtime/windows/manifests/backtest_manifest_status.json`
  - `audit/v40_runtime/windows/manifests/split_preflight_status.json`
  - `audit/v40_runtime/windows/manifests/split_preflight.log`

## Data Contract Verification (Patch-02 alignment)
Use this after frame/train kickoff to verify frame output contract satisfies train/backtest requirements:
```powershell
cd D:\Omega_vNext
python tools\verify_v40_data_contract.py
```

Strict mode (requires latest frame_compat schema including `close_positive_guard`):
```powershell
python tools\verify_v40_data_contract.py --strict-close-guard
```

## Resume Rules
- Frame: uses output dir state file `_audit_state.jsonl`.
- Train: uses `artifacts/checkpoint_rows_*.pkl` + `processed_files`.
- Backtest: uses `backtest_state.json`.
- Force fresh run with `-NoResume`.

## Frame -> Train/Backtest Compatibility Gate
- Before `train` (and before `backtest` when no custom file list is provided), pipeline runs:
  - `tools/check_frame_train_backtest_compat.py`
- It samples frame parquet files and checks:
  - raw columns needed by `_prepare_frames`/physics path
  - backtest readiness path (`raw` or `feature stack + ret_k`)
  - smoke execution of `_prepare_frames` on sampled files
- Override options (only for diagnostics):
```powershell
# skip compatibility gate (not recommended)
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage train `
  -SkipFrameCompatibilityCheck

# tune sampling depth
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage train `
  -FrameCompatibilitySampleFiles 160 `
  -FrameCompatibilityPrepareSmokeFiles 5
```

## Backtest Fail-Closed Semantics
- Full pipeline backtest now runs fail-closed by default:
  - `--max-file-errors 0`
  - `--fail-on-audit-failed`
- Meaning:
  - any worker/file error above threshold hard-fails stage
  - final audit status `FAILED` hard-fails stage
- Smoke wrapper explicitly sets `--allow-audit-failed` because tiny sample smoke is for runtime continuity validation, not production audit qualification.

## Drop/Reconnect Recovery
- If Windows disconnected unexpectedly, rerun the same stage command without `-NoResume`.
- Resume sources:
  - frame: `data/level2_frames_v40_win/_audit_state.jsonl`
  - train: `artifacts/checkpoint_rows_*.pkl`
  - backtest: `audit/v40_runtime/windows/backtest/backtest_state.json`

## Mac-side Monitoring
```bash
python3 /Volumes/desktop-41jidl2/Omega_vNext/tools/v40_runtime_status.py
python3 /Volumes/desktop-41jidl2/Omega_vNext/tools/v40_runtime_status.py --json
```
