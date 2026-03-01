# v60 Base Matrix Memory Optimization Basis (Official + Community)

- timestamp_utc: 2026-02-18T00:00:00Z
- scope: `tools/v60_forge_base_matrix_local.py` memory/performance rebalance
- hard constraints:
  - align with `audit/v6.md`
  - align with `audit/v60_vertex_objection.md`

## 1) Constraint Alignment (v6 + v60 objection)

1. No time-axis chunking (`chunk-days` forbidden); only ticker/symbol sharding.
2. Keep Float64 fidelity; no Float32/Float16 downcast as OOM workaround.
3. Keep base-matrix ETL local (edge), not cloud ETL expansion.
4. Preserve physics gates (`is_physics_valid`, `epiplexity`) and causal ordering.

## 2) Official Sources (Primary)

1. PyArrow `read_table` supports `columns` projection and `filters` predicate pushdown; this allows loading fewer columns/rows into memory.
   - https://arrow.apache.org/docs/python/generated/pyarrow.parquet.read_table.html
2. Arrow Python cookbook documents the same column/row-subset read pattern for Parquet as the memory-safe read path.
   - https://arrow.apache.org/cookbook/py/io.html
3. PyArrow `Table.to_pydict()` converts Arrow columns into Python objects (dict/list), which is a known high-overhead representation versus Arrow-native buffers.
   - https://arrow.apache.org/docs/python/generated/pyarrow.Table.html
4. Polars `from_arrow` is zero-copy for most supported types, so Arrow->Polars path is preferable to Python object materialization.
   - https://docs.pola.rs/py-polars/html/reference/api/polars.from_arrow.html
5. Polars casting with `strict=False` converts non-castable values to null without Python row loops, enabling vectorized sanitization.
   - https://docs.pola.rs/user-guide/expressions/casting/
6. Python multiprocessing docs note objects are pickled/re-created across process boundaries, so avoiding oversized Python object graphs is important for worker memory/latency.
   - https://docs.python.org/3/library/multiprocessing.html

## 3) Community Sources (Supplementary)

1. Apache Arrow issue: large Parquet reads can spike memory in real workloads.
   - https://github.com/apache/arrow/issues/38552
2. Apache Arrow issue: memory pressure appears around Arrow->Pandas object conversion pathways.
   - https://github.com/apache/arrow/issues/44472
3. Polars issue: some operations can trigger unexpected copies and memory growth on big datasets.
   - https://github.com/pola-rs/polars/issues/11546
4. StackOverflow discussion: practical mitigations focus on avoiding heavy object conversion paths and using constrained read parameters.
   - https://stackoverflow.com/questions/53016802/memory-leak-from-pyarrow

## 4) Recorded Design Decisions for This Patch

1. Replace `pyarrow -> to_pydict -> Python row/filter loops` with Arrow-native projection/filter + Polars vectorized pipeline.
2. Read only required columns (`columns=...`) and target-symbol rows (`filters=[('symbol','in',...)]`) per file.
3. Convert Arrow table to Polars via `pl.from_arrow(..., rechunk=False)` to reduce copy/object expansion.
4. Use vectorized `cast(..., strict=False)` for numeric/bool cleanup instead of Python per-row conversion.
5. Keep sorting on `symbol/date/time_end/bucket_id` in-batch to preserve causal order assumptions.
6. Keep strict Float64 invariant checks and physics gate checks unchanged.
7. Add periodic `gc.collect()` and batch-end cleanup to reduce long-lived worker memory.
8. Optimize symbol discovery using `pyarrow.compute.unique` to avoid full-column Python list expansion.

## 5) Pass Criteria (before execute)

1. Smoke gate must pass on local sample input.
2. Dual independent recursive audits must return `VERDICT: PASS`.
3. Final decision remains `NO EXECUTE` until human dispatches run.
