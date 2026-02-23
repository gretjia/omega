# Stage2 Single-Scan Optimization Landed (Repeated Scan Fix)

- Timestamp: 2026-02-23 08:18:19 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- Fix the high-impact Stage2 inefficiency where one parquet file was repeatedly re-scanned per symbol batch.

## 2) Completed in This Session

- Refactored `tools/stage2_physics_compute.py`:
  - Replaced per-batch `lf.filter(...).collect()` repeated scan loop.
  - Added single-pass parquet iterator:
    - `_iter_complete_symbol_frames_from_parquet(l1_file)`
    - reads row-groups once and reconstructs complete symbol blocks in order.
  - Added batched compute/write helper:
    - `_run_feature_physics_batch(...)`
    - runs `build_l2_features_from_l1` + `apply_recursive_physics` on symbol batches and appends to parquet writer.
  - Kept stability protections:
    - bounded symbol batch (`batch_size=50`)
    - iterative `gc.collect()`
    - atomic `.tmp -> final` rename path.
- Kept fallback behavior:
  - if no `symbol` column exists, process the file once via eager parquet read path.

## 3) Verification

- Syntax check passed:
  - `python3 -m py_compile tools/stage2_physics_compute.py`
- Logic smoke (local synthetic parquet with multiple row groups) passed:
  - iterator returned complete symbol blocks in order (`A/B/C`) with correct row counts.
- Runtime continuity check:
  - Linux stage1 service remains active and healthy.
  - Windows stage1 task remains `Running`.

## 4) Impact Assessment

- Fixed item:
  - Stage2 repeated full-file scan per batch (high-value performance bug).
- Not changed in this patch:
  - two-stage architecture itself (kept)
  - stage1 conservative workers policy (kept)
  - feature payload complexity (kept).

## 5) Artifacts / Paths

- Modified:
  - `tools/stage2_physics_compute.py`
- Related context:
  - `handover/ai-direct/entries/20260223_081420_legacy_pipeline_archived_and_fix_priorities.md`
  - `handover/ai-direct/LATEST.md`

## 6) Commands Executed (Key Only)

- `python3 -m py_compile tools/stage2_physics_compute.py pipeline_runner.py pipeline/engine/framer.py`
- local synthetic test for `_iter_complete_symbol_frames_from_parquet`
- Linux/Windows stage1 liveness spot checks.

## 7) Exact Next Steps

1. Run one real Stage2 benchmark (before/after wall time + CPU + read bytes) on a representative L1 file.
2. Tune `batch_size` and `POLARS_MAX_THREADS` jointly under current cgroup settings.
3. If stable gains hold, apply same optimization strategy to any remaining multi-pass parquet loops.
