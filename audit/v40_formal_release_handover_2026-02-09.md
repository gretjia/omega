# v40 Formal Release Handover (Windows AI)

Date: 2026-02-09  
Branch: `codex/v40-race`  
Status: Ready for Windows execution (after pull/sync)

---

## 1. Purpose

This handover promotes the current v40 codebase to a formal runnable release after re-alignment against:

1. `audit/v40_race_patch_02.md`
2. `OMEGA_CONSTITUTION.md`
3. `.agent/principles.yaml`
4. Always-On Core skills:
   - `.agent/skills/math_core/SKILL.md`
   - `.agent/skills/physics/SKILL.md`
   - `.agent/skills/engineering/SKILL.md`
   - `.agent/skills/v3_mainline_guard/SKILL.md`
   - `.agent/skills/hardcode_guard/SKILL.md`
   - `.agent/skills/ops/SKILL.md`

---

## 2. Alignment Matrix

### 2.1 Patch-02 core intent -> implementation

1. Denominator Trap / false depth control  
   - Implemented via frame-side positive price contract and label-side valid-price gating.
   - Files:
     - `omega_v3_core/omega_etl.py`
     - `omega_v3_core/trainer.py`
     - `config.py`

2. Fail-closed data contract before train/backtest  
   - Implemented via close-sanity checks in compatibility preflight.
   - File:
     - `tools/check_frame_train_backtest_compat.py`

3. Engineering reliability for long runs  
   - Implemented via retryable atomic state writes in backtest runtime.
   - File:
     - `parallel_trainer/run_parallel_backtest_v31.py`

4. Throughput scaling on Windows 128GB host  
   - Implemented via hardware-tuned pipeline defaults.
   - Files:
     - `jobs/windows_v40/start_v40_pipeline_win.ps1`
     - `jobs/windows_v40/run_v40_train_backtest_win.ps1`
     - `jobs/windows_v40/README.md`
     - `audit/v40_windows_handover_runtime_2026-02-08.md`

### 2.2 Constitution / SKILL guardrails -> compliance

1. No production hardcoded trading thresholds  
   - Compliance: new thresholds are config fields (`config.py`) for data-quality/validity contracts, not ad-hoc trading literals.

2. Dataset role isolation (train/backtest disjoint)  
   - Compliance: existing v40 manifest + preflight fail-closed pipeline remains mandatory.

3. v3 mainline routing  
   - Compliance: all logic changes are in `omega_v3_core/*` and runtime scripts, not root legacy shims.

4. Ops resumability / observability  
   - Compliance: status/state write robustness improved; runtime artifacts remain under `audit/v40_runtime/windows/`.

---

## 3. Release Delta (this formal version)

1. `ret_k` extreme-value root cause fixed at source and label pipeline.
2. Frame compatibility preflight now rejects `close <= 0` samples.
3. Backtest state/status persistence hardened against Windows file-lock contention.
4. Hardware defaults upgraded for AMD AI Max 395 / 128GB profile:
   - `FrameWorkers=22`
   - `TrainWorkers=26`
   - `BacktestWorkers=20`
   - `TrainBatchRows=1000000`
   - `TrainCheckpointRows=2000000`
   - `TrainStageChunkFiles=48`
   - `BacktestStageChunkFiles=48`
   - `MemoryThreshold=88`

---

## 4. Windows Execution Commands (official)

### 4.1 Full release run (recommended, clean rerun)

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage all `
  -NoResume `
  -TrainYears "2023,2024" `
  -BacktestYears "2025" `
  -BacktestYearMonths "202601"
```

Reason for `-NoResume`:
frame/trainer data contract changed; full regeneration avoids mixing old frames with new guards.

### 4.2 Fixed split wrapper (after frame is already regenerated)

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1
```

---

## 5. Runtime Artifacts to Monitor

Root:

- `audit/v40_runtime/windows/`

Mandatory files:

1. Frame
   - `audit/v40_runtime/windows/frame/frame.log`
   - `audit/v40_runtime/windows/frame/frame_status.json`
   - `audit/v40_runtime/windows/frame/frame_compat.log`
   - `audit/v40_runtime/windows/frame/frame_compat_status.json`
2. Train
   - `audit/v40_runtime/windows/train/train.log`
   - `audit/v40_runtime/windows/train/train_status.json`
3. Backtest
   - `audit/v40_runtime/windows/backtest/backtest.log`
   - `audit/v40_runtime/windows/backtest/backtest_status.json`
   - `audit/v40_runtime/windows/backtest/backtest_state.json`
4. Split evidence
   - `audit/v40_runtime/windows/manifests/split_preflight_status.json`
   - `audit/v40_runtime/windows/manifests/train_manifest_status.json`
   - `audit/v40_runtime/windows/manifests/backtest_manifest_status.json`

---

## 6. Acceptance Gates (must pass)

1. `frame_compat_status.json`:
   - `status = completed`
   - `checks.close_positive_guard = true`
2. `split_preflight_status.json`:
   - `status = completed`
   - `overlap_count = 0`
3. `train_status.json`:
   - `status = completed`
4. `backtest_status.json`:
   - `status = completed`
   - not stale
   - no abnormal `total_pnl` explosion

If any gate fails, stop and debug before continuing.

---

## 7. Resume / Recovery

1. Default mode is resumable; do not delete state files unless intentionally resetting.
2. Resume anchors:
   - frame: `data/level2_frames_v40_win/_audit_state.jsonl`
   - train: `artifacts/checkpoint_rows_*.pkl`
   - backtest: `audit/v40_runtime/windows/backtest/backtest_state.json`
3. For clean replay, use `-NoResume`.

---

## 8. Mac-side Monitoring

```bash
python3 /Volumes/desktop-41jidl2/Omega_vNext/tools/v40_runtime_status.py
python3 /Volumes/desktop-41jidl2/Omega_vNext/tools/v40_runtime_status.py --json
```

---

## 9. Files changed in this formal release

1. `config.py`
2. `omega_v3_core/omega_etl.py`
3. `omega_v3_core/trainer.py`
4. `parallel_trainer/run_parallel_backtest_v31.py`
5. `tools/check_frame_train_backtest_compat.py`
6. `jobs/windows_v40/start_v40_pipeline_win.ps1`
7. `jobs/windows_v40/run_v40_train_backtest_win.ps1`
8. `jobs/windows_v40/README.md`
9. `audit/v40_windows_handover_runtime_2026-02-08.md`
10. `README.md`
11. `audit/v40_formal_release_handover_2026-02-09.md`

