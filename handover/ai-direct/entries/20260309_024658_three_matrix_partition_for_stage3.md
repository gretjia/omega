---
entry_id: 20260309_024658_three_matrix_partition_for_stage3
task_id: TASK-V643-GC-SWARM-OPTUNA-REVIVAL-SPEC
timestamp_local: 2026-03-09 02:46:58 +0000
timestamp_utc: 2026-03-09 02:46:58 +0000
operator: Codex
role: architect
branch: main
status: completed
---

# Stage3 Three-Matrix Partition For Optimal Allocation

## 1. Decision

The optimal data-allocation scheme for the current corpus is now locked as a three-artifact Stage3 partition:

1. Training artifact:
   - `base_matrix_train_2023_2024.parquet`
2. Outer holdout artifact:
   - `base_matrix_holdout_2025.parquet`
3. Final canary artifact:
   - `base_matrix_holdout_2026_01.parquet`

This replaces any ambiguous notion that a single mixed `2023-2026` base matrix could support the full optimization + validation protocol.

## 2. Verification Of Current State

Direct checks on `linux1-lx` confirmed the currently finished Stage3 artifact is training-only:

- file:
  - `/omega_pool/parquet_data/stage3_base_matrix_train_20260308_095850/base_matrix_train_2023_2024.parquet`
- meta:
  - `years=['2023', '2024']`
- parquet scan:
  - `year_min=2023`
  - `year_max=2024`
  - `year_count=2`
  - `rows=736163`

So the train artifact already exists and is correctly scoped.

## 3. Why Separate Holdout Artifacts Are Required

- Optuna and champion selection must only read the training artifact.
- `2025` must remain a true outer holdout, not a hidden extension of the tuning domain.
- `2026-01` must remain the last untouched canary slice.
- If `2025` gets folded back into tuning decisions, it ceases to be holdout evidence and the protocol must be declared as changed.

This is a governance requirement, not a storage preference.

## 4. Required Generation Order

1. Confirm `base_matrix_train_2023_2024.parquet`
2. Forge `base_matrix_holdout_2025.parquet`
3. Forge `base_matrix_holdout_2026_01.parquet`
4. Run cloud optimization only on artifact 1
5. Run outer holdout evaluation on artifact 2
6. Retrain the approved champion on the chosen final training horizon
7. Run the final untouched canary check on artifact 3

## 5. Operational Consequence

The project is not blocked on training data anymore.

It is now blocked on:

- forging the `2025` holdout base matrix cleanly
- forging the `2026-01` holdout base matrix cleanly
- especially solving January-only date scoping, because current active entrypoints are still year-only

## 6. Implementation Constraint

Any implementation that evaluates `2025` or `2026-01` from the training artifact instead of separate holdout artifacts should be treated as invalid.
