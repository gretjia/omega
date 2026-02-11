# v40 Full Pipeline Handover (Windows AI)

Date: 2026-02-10  
Owner intent: run full `frame -> train -> backtest` and use full-run result to confirm v40 race winners for Patch-02.

## 1) Scope and fixed policy

- Design baseline: `audit/v40_race_patch_02.md`
- Split is strict and fixed:
  - Train years: `2023,2024`
  - Backtest years: `2025`
  - Backtest year-months: `202601`
- Fail-closed rules are kept enabled:
  - train/backtest overlap guard
  - backtest `--max-file-errors 0` + `--fail-on-audit-failed`

## 2) Cleanup already done on repository side

The following test/smoke artifacts were removed to avoid contamination:
- `audit/v40_smoke_mac_20260209_235421/`
- `audit/v40_smoke_mac_20260209_235432/`
- `audit/v40_smoke_report.json`
- `data/level2/smokev40_mac/`

Runtime residues were also cleaned:
- `audit/v40_runtime/windows/frame/*`
- `audit/v40_runtime/windows/train/*`
- `audit/v40_runtime/windows/backtest/*`
- `audit/v40_runtime/windows/manifests/*`
- `audit/v40_runtime/windows/frame_bench/*`
- root loose runtime logs under `audit/v40_runtime/windows/` (launcher/probe temp logs)

## 3) Official Windows run command (one command)

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_full_pipeline_fixed_split_win.ps1 -PurgeFrameOutput
```

If you want forced fresh rerun with no resume:

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_full_pipeline_fixed_split_win.ps1 -PurgeFrameOutput -NoResume
```

## 4) What the launcher fixes in code (no manual args needed)

Script: `jobs/windows_v40/run_v40_full_pipeline_fixed_split_win.ps1`

- Stage: `all`
- Frame:
  - `FrameWorkers=12`
  - `FrameIoSlots=4`
  - `FrameSevenZipThreads=1`
  - `FrameStageDir=C:/Omega_level2_stage`
  - output dir: `data/level2_frames_v40_win`
- Train:
  - `TrainWorkers=26`
  - `TrainBatchRows=1000000`
  - `TrainCheckpointRows=2000000`
  - `TrainPlanningProgressEveryLines=50000`
  - `TrainStageDir=C:/Omega_train_stage`
  - `TrainStageChunkFiles=48`
  - `TrainStageCopyWorkers=4`
- Backtest:
  - `BacktestWorkers=20`
  - `BacktestPlanningProgressEveryLines=50000`
  - `BacktestStateSaveEveryFiles=200`
  - `BacktestStageDir=C:/Omega_backtest_stage`
  - `BacktestStageChunkFiles=48`
  - `BacktestStageCopyWorkers=4`
- Memory:
  - `MemoryThreshold=88.0`
- Fixed split:
  - `TrainYears=2023,2024`
  - `BacktestYears=2025`
  - `BacktestYearMonths=202601`
- Post-run automatic output:
  - `tools/extract_v40_race_winner.py` is invoked
  - writes race winner summary json/md under `audit/v40_runtime/windows/backtest/`

## 5) Logs and status to monitor (Windows + Mac)

Runtime root:
- `audit/v40_runtime/windows/`

Stage logs:
- frame log: `audit/v40_runtime/windows/frame/frame.log`
- train log: `audit/v40_runtime/windows/train/train.log`
- backtest log: `audit/v40_runtime/windows/backtest/backtest.log`

Stage status JSON:
- `audit/v40_runtime/windows/frame/frame_status.json`
- `audit/v40_runtime/windows/train/train_status.json`
- `audit/v40_runtime/windows/backtest/backtest_status.json`
- `audit/v40_runtime/windows/backtest/backtest_state.json`

Split and manifests:
- `audit/v40_runtime/windows/manifests/train_files.txt`
- `audit/v40_runtime/windows/manifests/backtest_files.txt`
- `audit/v40_runtime/windows/manifests/split_preflight_status.json`

Race winner output:
- `audit/v40_runtime/windows/backtest/race_winner_summary.json`
- `audit/v40_runtime/windows/backtest/race_winner_summary.md`

## 6) Acceptance criteria for this run

- Frame completed (`frame_status.json.status == completed`)
- Train completed (`train_status.json.status == completed`)
- Backtest completed (`backtest_status.json.status == completed`)
- Backtest final audit is passed (`final_audit_status == PASSED`)
- Split preflight completed and overlap count is 0
- Race winner summary files exist and are readable

## 7) Notes for Windows AI operator

- Do not bypass split/overlap guard in normal run.
- Do not disable staging in normal run.
- Do not disable fail-closed backtest flags in normal run.
- If run is interrupted, rerun the same command; use `-NoResume` only for full restart intent.
