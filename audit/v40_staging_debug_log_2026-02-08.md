# v40 Staging Debug Log (2026-02-08)

## Scope
- Project: OMEGA v40 pipeline
- Stages covered: `frame`, `train`, `backtest`
- Goal: make local staging first-class, resumable, and observable under shared-drive pressure

## Runtime Context
- Mac side used for code updates and audit verification
- Windows target runtime: AMD AI Max 395, 128GB unified memory
- Data/source access includes shared path pressure and intermittent high disk contention

## Initial Problems Observed
1. `train/backtest` had no frame-equivalent local staging in the v40 Windows unified entry.
2. When manifest pointed to stale parquet paths, staging copy threw `FileNotFoundError` and could terminate the run path.
3. Chunk cleanup logic had a corner case: when copy failed and code fell back to source path, cleanup could target the wrong directory and leave `chunk_*` behind.
4. Staging behavior was enabled in pipeline entry but not guaranteed as script-level defaults when direct scripts were invoked.

## Root Cause Summary
1. Staging capability mismatch:
- `frame` already had archive-localization logic.
- `train/backtest` previously assumed direct reads and lacked chunk-local staging workflow.

2. Error handling mismatch:
- Copy failure path in chunk staging treated as fatal behavior in early implementation.
- Manifest quality (stale file list) was not isolated from executor robustness.

3. Cleanup target derivation bug:
- Cleanup inferred chunk dir from staged file paths, which can be wrong after fallback-to-source.

4. Default policy drift risk:
- Operator could accidentally run direct script without staging flags and bypass intended I/O model.

## Engineering Changes Applied

### A. Train/Backtest gained frame-equivalent local staging
- Added staged chunk controls to both scripts:
  - `--stage-local`
  - `--stage-dir`
  - `--stage-chunk-files`
  - `--no-cleanup-stage`
- Added staging metadata to status output.

### B. Copy failure hardened to fallback mode
- If chunk copy fails for a file:
  - emit warning
  - fallback to source path
  - continue processing remaining files
- Avoid full-stage collapse on a single stale path.

### C. Cleanup fixed to explicit chunk dir contract
- `_stage_chunk` now returns both staged list and explicit `chunk_dir`.
- `_cleanup_chunk` now deletes only that explicit `chunk_dir`.
- Eliminates residual `chunk_*` caused by fallback path ambiguity.

### D. Frame script promoted to same policy level
- Added explicit stage controls:
  - `--stage-dir`
  - `--no-cleanup-stage`
  - `--no-copy-to-local`
- Set frame copy behavior default to enabled (`copy_to_local=True`) with explicit opt-out.
- Added status fields: `copy_to_local`, `stage_dir`, `cleanup_stage`.

### E. Full-flow defaults standardized
- Scripts now default to staging-first behavior:
  - frame: local copy + stage extraction (default on)
  - train: local chunk staging (default on)
  - backtest: local chunk staging (default on)
- Explicit disable switches kept for controlled comparison:
  - frame: `--no-copy-to-local`
  - train/backtest: `--no-stage-local`

## Files Updated
1. `tools/run_l2_audit_driver.py`
2. `parallel_trainer/run_parallel_v31.py`
3. `parallel_trainer/run_parallel_backtest_v31.py`
4. `jobs/windows_v40/start_v40_pipeline_win.ps1`
5. `jobs/windows_v40/README.md`
6. `.agent/skills/ops/SKILL.md`

## Verification and Smoke Evidence

### 1) Script-level parameter verification
- `--help` confirmed for all three scripts:
  - frame shows `--copy-to-local | --no-copy-to-local`, `--stage-dir`, `--no-cleanup-stage`
  - train/backtest show `--stage-local | --no-stage-local`, `--stage-dir`, `--stage-chunk-files`, `--no-cleanup-stage`

### 2) Frame real-data smoke
- Sample: `year=202301`, `limit=1`, `workers=1`
- Result: one archive processed, output parquet count `5357`
- With cleanup enabled: stage worker dirs removed as expected
- With `--no-cleanup-stage`: stage worker dirs retained as expected

### 3) Train/Backtest minimal real run smoke
- Sample manifest: one valid parquet from `data/level2_frames_v40_win`
- Train completed and checkpoint saved
- Backtest completed with report block and no staging path errors

### 4) Stale manifest path resilience
- Used manifests containing missing historical parquet paths
- Expected behavior achieved:
  - copy warning emitted
  - fallback to source path
  - stage continues without hard crash

### 5) Cleanup regression retest after fix
- Re-ran fallback-path scenarios
- `chunk_*` no longer leaked; only stage root remains

## Operational Lessons
1. Staging is an I/O topology strategy, not math logic.
- It should improve throughput/stability without changing model math.

2. Manifest quality and executor robustness must be decoupled.
- Missing files should degrade gracefully (warn + continue), not break the full stage.

3. Cleanup must be based on explicit ownership objects (`chunk_dir`), not inferred file paths.

4. Status paths should remain under shared, observable runtime roots for cross-machine monitoring.

## Runbook Additions (for future AI operators)
1. Prefer unified entry:
- `powershell -ExecutionPolicy Bypass -File jobs\\windows_v40\\start_v40_pipeline_win.ps1 -Stage all`

2. Keep cleanup on in production-like runs.

3. Turn off staging only for controlled A/B diagnostics.

4. If throughput stalls:
- inspect runtime status JSON timestamps
- inspect stage logs tail
- verify no stale manifest waves are dominating warnings

5. Before handover:
- report stage, last status timestamp, files done/remaining, latest checkpoint/state path, and top warnings

## Skill Sync
- Engineering operations skill updated:
  - `.agent/skills/ops/SKILL.md`
- Added staging-first policy and staging debug checklist as reusable guardrails.

## Additional Incident: frame tail stall blocked train/backtest chaining

### Symptom
1. `frame_status.json` reached:
   - `archives_completed_in_run == archives_run_now`
   - `archives_remaining_in_run == 0`
2. But stage status stayed `running`, and `train_status.json` / `backtest_status.json` were not created.
3. Runtime showed low CPU/memory utilization and no active python process after interruption.

### Root cause
1. `run_l2_audit_driver.py` aggregate report path performs full `scan_parquet(...).collect()`.
2. On very large frame outputs this step can become the effective bottleneck (or fail/interrupt), while report itself is not a dependency for train/backtest.

### Fixes applied
1. `jobs/windows_v40/start_v40_pipeline_win.ps1`
   - Default behavior changed to pass `--skip-report` to frame stage.
   - Added explicit opt-in:
     - `-FrameGenerateReport`
     - `-FrameReportPath`
2. Added frame->train/backtest compatibility preflight:
   - New script: `tools/check_frame_train_backtest_compat.py`
   - Pipeline runs it before train (and before backtest when using default frame dir manifest).
   - Outputs:
     - `audit/v40_runtime/windows/frame/frame_compat.log`
     - `audit/v40_runtime/windows/frame/frame_compat_status.json`

### Why this is safe
1. Train/backtest do not consume the frame aggregate report markdown.
2. The new preflight checks real downstream requirements:
   - physics raw columns expected by `_prepare_frames`
   - backtest-ready path (`raw` or `feature stack + ret_k`)
   - sampled `_prepare_frames` smoke execution

### Operator notes
1. For production pipeline chaining, keep default (`skip report`) and run report separately if needed.
2. Do not disable compatibility preflight unless diagnosing.

### Additional hardening (postmortem fix)
1. `tools/run_l2_audit_driver.py` now has bounded report mode by default:
   - `--report-sample-files` (default 200)
   - `--report-rows-per-file` (default 2000)
   - full collect requires explicit `--report-full`
2. Report failure is non-fatal by default (can be promoted via `--report-fail-fatal`).
3. Empty report input path now writes terminal completed status instead of silent return.

### Root-cause in process terms
1. Memory guard existed for archive processing loop but was not treated as an end-to-end invariant.
2. SKILL rules previously emphasized staging/resume, but did not explicitly forbid chain-critical unbounded `collect()`.
3. Fix was applied at both layers:
   - code guardrails in `run_l2_audit_driver.py`
   - explicit SKILL hard-guard in `.agent/skills/ops/SKILL.md` and `.agent/skills/engineering/SKILL.md`
