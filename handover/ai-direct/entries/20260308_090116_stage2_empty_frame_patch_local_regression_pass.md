# V643 Stage2 Empty-Frame Patch Local Regression Pass

- Entry ID: `20260308_090116_stage2_empty_frame_patch_local_regression_pass`
- Timestamp UTC: `2026-03-08 09:01:16 +0000`
- Operator: `Codex`
- Status: `local_patch_ready_for_deploy_validation`
- Mission: `V643-STAGE2-PATHO-EMPTY-FRAME-REMEDIATION`

## 1. What Changed

- Patched `tools/stage2_physics_compute.py` in two places:
  - `_iter_complete_symbol_frames_from_parquet()` now applies `_filter_pathological()` on the earlier non-tail yield path as well, making pathological-symbol filtering behavior consistent across symbol transitions.
  - `process_chunk()` now skips zero-row symbol frames before indexing `symbol[0]`, preventing the normal non-fallback path from crashing after a proactive pathological drop.
- Extended `tests/test_stage2_pathological_symbol_skip.py` with two new regressions:
  - non-tail pathological symbol yields are filtered consistently
  - `process_chunk()` skips an empty symbol frame and still completes on the next valid symbol frame

## 2. Local Verification

- `python3 -m py_compile tools/stage2_physics_compute.py tests/test_stage2_pathological_symbol_skip.py`
  - result: pass
- `uv run --python /usr/bin/python3.11 --with pytest --with pyarrow --with polars --with numpy==1.26.4 --with numba==0.60.0 pytest -q tests/test_stage2_pathological_symbol_skip.py tests/test_stage2_targeted_resume_batching.py tests/test_stage2_output_equivalence.py`
  - result: `15 passed in 5.47s`

## 3. Current State

- The local code patch and regression coverage are in place.
- Real-file validation on `linux1-lx` and the required Stage3 forge consumption proof have not been executed yet in this session.
- Per repo workflow, worker validation should go through the controller-managed `commit + push + deploy` path, not a dirty-tree runtime patch.

## 4. Exact Next Actions

1. Commit the local remediation patch.
2. Push and deploy through the controller-managed path.
3. Rerun the three unresolved files on `linux1-lx` using the normal current `v643` Stage2 path.
4. If Linux passes, rerun the two Windows-owned files on `windows1-w1` if still needed.
5. Run isolated `tools/forge_base_matrix.py --input-file-list ... --years 2023,2024,2025` validation on the repaired three-file set.
