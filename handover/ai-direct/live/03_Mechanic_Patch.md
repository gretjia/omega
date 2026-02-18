# 03 Mechanic Patch

- task_id: TASK-20260218-V60-BASE-MATRIX-MEM-OPT
- git_hash: 5ca36a3
- timestamp_utc: 2026-02-18T21:11:18Z

## Scope
- `/Users/zephryj/work/Omega_vNext/tools/v60_forge_base_matrix_local.py`
- `/Users/zephryj/work/Omega_vNext/tools/v60_build_base_matrix.py`
- `/Users/zephryj/work/Omega_vNext/audit/runtime/v60/v60_base_matrix_memory_basis_20260218.md`

## Key Changes
1. Removed `to_pydict` full Python materialization in batch read path.
2. Added Arrow projection + predicate path:
   - `read_table(..., columns=select_cols, filters=[('symbol','in', ...)])`
3. Added Arrow -> Polars path + vectorized type casts:
   - `pl.from_arrow(..., rechunk=False)`
   - numeric/bool `cast(..., strict=False)`
4. Added memory cleanup points (`gc.collect`) for worker stability.
5. Added global post-concat sort on (`symbol`, `date`, `time_end`, `bucket_id`) before recursive prepare.
6. Preserved invariants:
   - no `chunk-days`
   - no float downcast workaround
   - strict Float64 checks retained
   - physics gates retained

## Smoke Evidence
- command: `python3 tools/v60_build_base_matrix.py --input-pattern='artifacts/runtime/v52/frames/host=windows1/*_aa8abb7.parquet' --years=2023 --hash=aa8abb7 --max-files=3 --sample-symbols=20 --symbols-per-batch=10 --max-workers=2 --output-parquet='artifacts/runtime/v60/smoke_memory_opt/base_matrix.parquet' --output-meta='artifacts/runtime/v60/smoke_memory_opt/base_matrix.parquet.meta.json' --no-resume`
- result: `status=ok`, `base_rows=1071`, `input_file_count=3`, `batch skipped_inputs=[0,0]`, no non-Float64 float columns.

## Remaining Risk
- Full-run memory depends on dispatch-time tuning of `symbols_per_batch` and `max_workers`.
