---
name: ops
description: OMEGA operations workflow for v3 training, audit, and backtest execution, with legacy compatibility notes.
---

# Skill: System Operations (Ops)

## Description
Manages the lifecycle of v3/v40 runs (frame, training, audit, backtest), with resumable execution and runtime observability.

## Capabilities

### 1. v40 primary pipeline (recommended)
- Windows unified entry:
  - `powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage all`
- Fixed official split entry (preferred for full runs):
  - `powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1`
- Stage-only:
  - `-Stage frame`
  - `-Stage train`
  - `-Stage backtest`
- Resume behavior:
  - default is resumable
  - use `-NoResume` for clean rerun

### 2. Runtime observability (shared-folder friendly)
- Runtime root:
  - `audit/v40_runtime/windows/`
- Stage status:
  - `frame/frame_status.json`
  - `train/train_status.json`
  - `backtest/backtest_status.json`
- Backtest resume state:
  - `backtest/backtest_state.json`
- Mac-side monitor:
  - `python3 tools/v40_runtime_status.py`
  - `python3 tools/v40_runtime_status.py --json`

### 3. Staging-first I/O protocol (v40 default)
- All stages should run with local staging enabled by default:
  - Frame: local archive copy + local extract stage
  - Train: local parquet chunk staging
  - Backtest: local parquet chunk staging
- Disable staging only for controlled experiments:
  - Frame: `--no-copy-to-local`
  - Train/Backtest: `--no-stage-local`
- Keep cleanup enabled in normal runs; only use no-cleanup for debug snapshots:
  - Frame: `-NoCleanupFrameStage` or `--no-cleanup-stage`
  - Train/Backtest: `-NoCleanupTrainStage` / `-NoCleanupBacktestStage` or `--no-cleanup-stage`

### 4. Staging debug checklist (mandatory when throughput stalls)
- If manifest contains stale paths, do not hard fail the whole stage; warn per-file and continue.
- Verify staged chunk directories are cleaned after each chunk in normal mode.
- Use workspace-visible status/log paths (under `audit/v40_runtime/windows/`) for cross-machine monitoring.
- Reconfirm resume artifacts before rerun:
  - frame: `_audit_state.jsonl`
  - train: `checkpoint_rows_*.pkl`
  - backtest: `backtest_state.json`

### 4.2 Dataset split hard-guard (mandatory)
- Never build train/backtest lists from one wildcard without role filters.
- Require role manifests and status evidence:
  - `manifests/train_files.txt`
  - `manifests/backtest_files.txt`
  - `manifests/train_manifest_status.json`
  - `manifests/backtest_manifest_status.json`
- Default policy:
  - train: `2023,2024`
  - backtest: `2025` + `202601`
- Pipeline must fail closed on overlap unless explicit temporary override is provided.

### 4.1 Memory hard-guard (mandatory)
- In long-running stages, **never place full wildcard `scan_parquet(...).collect()` on the critical chain path**.
- Aggregate report steps must be:
  - decoupled from frame->train/backtest chaining, or
  - bounded by explicit sampling caps (`max_files`, `rows_per_file`).
- Report failure must default to non-fatal unless the operator explicitly requests fatal behavior.
- Any stage completion logic must always write terminal status (`completed`/`failed`) to status JSON; avoid silent return paths.

### 5. v40 direct script entry (advanced/manual)
- Frame:
  - `python tools/run_l2_audit_driver.py ...`
- Train:
  - `python parallel_trainer/run_parallel_v31.py ...`
- Backtest:
  - `python parallel_trainer/run_parallel_backtest_v31.py ...`

### 6. legacy compatibility flows
- Legacy serial training/backtest:
  - `python tools/run_v3_training.py`
  - `python tools/run_v3_backtest.py`
- `python run_backtest.py` and `python inspect_artifact.py` are legacy/v1 compatibility entry points.
- Use only when explicitly targeting `legacy_model/v1`.

## Verification protocol
- [ ] Use v40 pipeline/script entry unless task explicitly requests legacy.
- [ ] Train/backtest split is explicit and role manifests exist.
- [ ] Manifest status confirms expected filters and `overlap_count == 0`.
- [ ] Artifacts are loadable and version-matched.
- [ ] Runtime logs/status are continuously persisted for audit and handover.
- [ ] No unbounded `collect()` remains on critical chain paths.
