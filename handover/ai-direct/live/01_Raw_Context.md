# 01 Raw Context

- task_id: TASK-20260218-V60-BASE-MATRIX-MEM-OPT
- git_hash: 5ca36a3
- timestamp_utc: 2026-02-18T21:11:18Z

## Constitution (Highest Authority)
- Mandatory pre-read completed: `/Users/zephryj/work/Omega_vNext/audit/constitution_v2.md`
- Immutable constraints in scope:
  - no time slicing (`chunk-days` forbidden)
  - no Float32/Float16 downcast workaround
  - base-matrix ETL remains local ticker sharding

## Objective
Optimize base-matrix execution code to reduce memory consumption while preserving performance/time ratio and keeping core physics computation flow unchanged.

## Scope Under Review
- `/Users/zephryj/work/Omega_vNext/tools/v60_forge_base_matrix_local.py`
- `/Users/zephryj/work/Omega_vNext/tools/v60_build_base_matrix.py`
- `/Users/zephryj/work/Omega_vNext/audit/runtime/v60/v60_base_matrix_memory_basis_20260218.md`

## Required Alignment
1. `/Users/zephryj/work/Omega_vNext/audit/v6.md`
2. `/Users/zephryj/work/Omega_vNext/audit/v60_vertex_objection.md`

## Gate Order
1. Official + community basis recorded.
2. Smoke gate pass.
3. Dual recursive audit pass.
4. Hold with `NO EXECUTE` until human dispatch.
