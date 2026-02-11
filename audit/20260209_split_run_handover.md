# 2026-02-09 v40 Split Run Handover

## 1) Scope and User Request
- User requested full v40 fixed-split `train+backtest` run, after confirming framing does not need redo.
- User then requested cleanup of smoke/test logs to avoid contamination and a complete handover for another AI.

## 2) v40 Key Runtime Info
- Project root: `D:\Omega_vNext`
- Main fixed-split command:
  - `powershell -ExecutionPolicy Bypass -File .\jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1 -NoResume`
- Fixed split policy:
  - Train years: `2023,2024`
  - Backtest years: `2025`
  - Backtest year-months: `202601`
- Runtime root:
  - `audit/v40_runtime/windows/`
- Entry orchestration script:
  - `jobs/windows_v40/start_v40_pipeline_win.ps1`
- Train/backtest Python entry scripts (name legacy, behavior current):
  - `parallel_trainer/run_parallel_v31.py`
  - `parallel_trainer/run_parallel_backtest_v31.py`

## 3) Core Code Patches Completed Before Full Run Attempt

### 3.1 Prior export completed (requested finding #1)
- Added export of `EPI_BLOCK_MIN_LEN` and `EPI_SYMBOL_THRESH` in:
  - `omega_v3_core/physics_auditor.py:138`
  - `omega_v3_core/physics_auditor.py:139`
  - `omega_v3_core/physics_auditor.py:213`
  - `omega_v3_core/physics_auditor.py:214`
  - `omega_v3_core/physics_auditor.py:341`
  - `omega_v3_core/physics_auditor.py:342`
- Loader already consumed these keys:
  - `config.py:786`
  - `config.py:787`

### 3.2 Topology mapping moved to config declaration (requested finding #2)
- Added declarative manifold mapping:
  - `config.py:640`
- Kernel uses manifolds config instead of code-wired mapping:
  - `omega_v3_core/kernel.py:124`

### 3.3 Legacy epiplexity compatibility removed (requested finding #3)
- Trainer now uses only canonical feature:
  - `omega_v3_core/trainer.py:45`
- Math core now exposes only active epiplexity path (LZ76):
  - `omega_v3_core/omega_math_core.py:33`
  - `omega_v3_core/omega_math_core.py:83`
- Legacy emit columns removed from kernel (no `epiplexity_zlib` / `epiplexity_perm`).

### 3.4 Runner stderr hardening
- Converted merged native output to plain strings to avoid noisy `NativeCommandError` wrappers while preserving logs:
  - `jobs/windows_v40/start_v40_pipeline_win.ps1:89`
  - `jobs/windows_v40/run_v40_smoke_win.ps1:52`

### 3.5 Validation after patch set
- `python -m py_compile ...` passed for modified core files.
- `python tools/v40_recursive_audit.py` passed (`status=PASS`).

## 4) Evidence That Framing Rebuild Is Not Required
- Frame compatibility continues to pass on the full frame corpus.
- Latest compatibility output:
  - `audit/v40_runtime/windows/frame/frame_compat_status.json`
  - Contains `Parquet files seen: 4758369`, `raw-ready=96/96`, `backtest-ready=96/96`, `prepare smoke ok=3/3`.

## 5) Smoke/Probe Results (Successful)
- One-file train smoke completed:
  - `audit/v40_runtime/windows/_archive_before_fullrun_20260209_001507/audit/v40_runtime/windows/train/train_status_smoke1.json`
- One-file backtest smoke completed:
  - `audit/v40_runtime/windows/_archive_before_fullrun_20260209_001507/audit/v40_runtime/windows/backtest/backtest_status_smoke1.json`
- One-file frame compatibility post-patch passed:
  - `audit/v40_runtime/windows/_archive_before_fullrun_20260209_001507/audit/v40_runtime/windows/frame/frame_compat_status_post_patch.json`

## 6) Cleanup Per User Request
- Smoke/test/probe/stale runtime artifacts were moved to:
  - `audit/v40_runtime/windows/_archive_before_fullrun_20260209_001507`
- Purpose: keep active runtime directories clean for full production run.

## 7) Full-Run Blocking Problem (Current Incident)

### 7.1 Observed behavior
- Full run log starts correctly, passes frame compatibility, then stops at dataset split preflight command.
- Current launcher log:
  - `audit/v40_runtime/windows/pipeline_launcher.out.log`
- Last logged step:
  - `CMD: python tools/preflight_dataset_split_v40.py ...`
- No generated status/manifest/train files afterward:
  - Missing: `audit/v40_runtime/windows/manifests/split_preflight_status.json`
  - Missing: `audit/v40_runtime/windows/manifests/train_manifest_status.json`
  - Missing: `audit/v40_runtime/windows/train/train.log`
  - Missing: `audit/v40_runtime/windows/train/train_status.json`

### 7.2 Why this can look frozen
- `tools/preflight_dataset_split_v40.py` scans all frame files with `os.scandir`:
  - `tools/preflight_dataset_split_v40.py:101`
  - `tools/preflight_dataset_split_v40.py:108`
- It writes `status-json` only at the end (success/failure), not during scan:
  - `tools/preflight_dataset_split_v40.py:249`
  - `tools/preflight_dataset_split_v40.py:259`
- So for multi-million-file input, there is no heartbeat file update during execution.

### 7.3 Supporting runtime logs
- `audit/v40_runtime/windows/pipeline_launcher.out.log` shows:
  - `2026-02-09 00:42:45` preflight command started.
  - No subsequent lines.
- `audit/v40_runtime/windows/manifests/split_preflight.log` tail contains only command lines (no completion line).

## 8) Process Visibility Limitations Encountered
- In this environment, some process-inspection commands were blocked/denied:
  - `Get-CimInstance Win32_Process` -> access denied.
  - `tasklist` -> access denied.
- `Get-Process` visibility was inconsistent for child Python processes in detached scenarios, so live process certainty is limited.

## 9) What Has Been Tried for the Full Run
- Foreground full run execution: confirmed startup path and transition into split preflight.
- Detached/redirected launcher attempts: log reaches preflight command, then no further progress evidence.
- Manual split-preflight direct invocation with 120s tool timeout: timed out before completion, and no status file written in that window.

## 10) Working Hypotheses (Ranked)
1. Split preflight is executing but appears stalled because it has no progress heartbeat and scans a very large directory.
2. Split preflight exits or gets interrupted before completion/status write, and wrapper has insufficient post-command diagnostics.
3. Environment-specific process/IO constraints are affecting long-running detached executions.

## 11) Recommended Handover Debug Plan (No Math-Core Changes)

### Phase A: Isolate split preflight deterministically
1. Run preflight directly in foreground and wait to completion with long timeout.
2. Add heartbeat progress into `tools/preflight_dataset_split_v40.py`:
   - Emit progress every N files (e.g., 100k) to stdout and optional interim status JSON (`status=running`).
3. Re-run preflight and verify `split_preflight_status.json` appears and updates.

### Phase B: Re-run full train/backtest
1. Keep framing as-is (no frame rebuild).
2. Run fixed split with `-NoResume`.
3. Watch:
   - `audit/v40_runtime/windows/manifests/split_preflight_status.json`
   - `audit/v40_runtime/windows/manifests/train_manifest_status.json`
   - `audit/v40_runtime/windows/train/train_status.json`

### Phase C: Fallback path if preflight remains bottleneck
1. Run one full attempt with preflight disabled (controlled debug only):
   - `jobs/windows_v40/run_v40_train_backtest_win.ps1 -SkipDatasetSplitPreflight -NoResume`
2. Keep manifest overlap checks active in backtest stage to preserve fail-closed safety.

## 12) Commands for Next AI
- Full run (fixed split):
```powershell
powershell -ExecutionPolicy Bypass -File .\jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1 -NoResume
```

- Split preflight only:
```powershell
python tools/preflight_dataset_split_v40.py `
  --input-dir D:\Omega_vNext\data\level2_frames_v40_win `
  --status-json D:\Omega_vNext\audit\v40_runtime\windows\manifests\split_preflight_status.json `
  --train-years 2023,2024 `
  --backtest-years 2025 `
  --backtest-year-months 202601
```

- Controlled fallback (skip split preflight):
```powershell
powershell -ExecutionPolicy Bypass -File .\jobs\windows_v40\run_v40_train_backtest_win.ps1 `
  -TrainYears "2023,2024" `
  -BacktestYears "2025" `
  -BacktestYearMonths "202601" `
  -SkipDatasetSplitPreflight `
  -NoResume
```

## 13) Constraints to Preserve
- Keep v40 design alignment with patch_02 precedence.
- Do not change math core semantics.
- Continue using `-NoResume` for first full run after feature-space changes.

