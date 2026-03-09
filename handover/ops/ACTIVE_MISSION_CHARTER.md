# OMEGA Active Mission Charter

Status: Active
Task Name: V643 GC swarm-optuna pilot implementation and first pilot execution
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

Current checkpoint:

- The three required Stage3 artifacts are now complete and isolated:
  - `base_matrix_train_2023_2024.parquet`
  - `base_matrix_holdout_2025.parquet`
  - `base_matrix_holdout_2026_01.parquet`
- The approved cloud optimization spec remains:
  - `handover/ai-direct/entries/20260309_012152_gc_swarm_optuna_project_spec.md`
  - Gemini verdict on the spec:
    - `PASS`
- The initial live implementation foundation is now present under `tools/`:
  - `tools/run_optuna_sweep.py`
  - `tools/aggregate_vertex_swarm_results.py`
  - `tools/launch_vertex_swarm_optuna.py`
- Compatibility glue has been added so the active trainer can consume champion hyperparameters without losing searched knobs.
- Local validation passed:
  - `python3 -m py_compile ...`
  - `uv run --python /usr/bin/python3.11 --with pytest --with polars --with xgboost --with optuna pytest -q tests/test_vertex_swarm_aggregate.py tests/test_vertex_optuna_split.py`
  - result:
    - `3 passed`

## 1. Objective

- Convert the approved `gc swarm-optuna` architecture into live active tooling under `tools/`.
- Launch the first real pilot on Google Cloud against the immutable `2023,2024` training artifact.
- Preserve strict role isolation:
  - optimization only on training artifact
  - no holdout contamination
- Produce credible pilot evidence:
  - real concurrent workers
  - bounded spot-to-on-demand recovery
  - aggregated leaderboard
  - champion params that can feed the active trainer

## 2. Canonical Spec

Primary task-level authority:

- `handover/ai-direct/entries/20260309_012152_gc_swarm_optuna_project_spec.md`
- `handover/ai-direct/entries/20260309_014638_gemini_swarm_spec_audit.md`

Supporting operational context:

- `handover/ai-direct/entries/20260309_024658_three_matrix_partition_for_stage3.md`
- `handover/ai-direct/entries/20260309_034012_holdout_matrices_dual_host_execution_complete.md`
- `handover/ai-direct/LATEST.md`

Conflict rule:

- The frozen canonical Stage3 gate contract overrides any convenience shortcut.
- If a launcher/runtime choice weakens temporal isolation, worker reproducibility, or champion handoff integrity, reject it.

## 3. Business Goal

- Restore the actual cloud advantage defined by the constitution:
  - wider parallel search coverage than the controller can do locally
  - spot-aware economics
  - better intelligence through leaderboard evidence, not just one remote train job

## 4. Files In Scope

Implementation scope:

- `tools/run_optuna_sweep.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `tools/submit_vertex_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tests/test_vertex_swarm_aggregate.py`
- `tests/test_vertex_optuna_split.py`

Handover scope:

- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

## 5. Out of Scope

- changing canonical Stage3 gate semantics
- re-forging Stage1 / Stage2 / Stage3 artifacts
- using `2025` or `2026-01` inside Optuna scoring
- distributed multi-replica XGBoost
- final production backtest interpretation

## 6. Required Audits

Implementation audit:

- worker must hard-assert `max(train_date) < min(val_date)`
- worker must build `dtrain` / `dval` once per worker
- aggregator must reject canonical fingerprint mismatch
- champion artifact must include trainer-consumable overrides

Runtime audit:

- cloud pilot must show real multi-worker fan-out
- if spot worker ends non-successfully, at most one on-demand retry is allowed
- leaderboard aggregation must enforce minimum worker/trial completeness

## 7. Runtime and Evidence Constraints

- Cloud bucket authority for this mission remains live on:
  - `gs://omega_v52_central`
- Controller-side launch currently requires:
  - `uv run --with google-cloud-aiplatform --with google-cloud-storage python ...`
- Optimization input is only:
  - staged immutable `base_matrix_train_2023_2024.parquet`
- Holdout artifacts remain untouched during the pilot:
  - `2025`
  - `2026-01`

## 8. Acceptance Criteria

1. Active tooling exists under `tools/` for worker payload, launcher, and aggregation.
2. Local regression tests cover:
   - temporal split proof
   - fingerprint enforcement
   - champion complexity tie-break
3. Launcher can submit many single-replica workers and watch them to terminal state.
4. Launcher can perform at most one on-demand retry for a failed spot attempt.
5. Aggregation emits:
   - leaderboard artifact
   - champion params artifact
   - trainer-consumable override map
6. Pilot target:
   - at least `4` workers
   - at least `40` completed trials
7. Handover records exact URIs, worker counts, and verdict.

## 9. Fail-Fast Conditions

- If launcher falls back to sequential `--sync` submissions for the pilot, stop.
- If worker training/validation split is not exactly `2023` vs `2024`, stop.
- If aggregation accepts mixed canonical fingerprints, stop.
- If champion output cannot feed the active trainer without dropping searched params, stop.
- If pilot evidence cannot prove real concurrent cloud workers, stop.

## 10. Definition of Done

- code foundation committed and pushed
- pilot launched on Google Cloud
- aggregation completes or a concrete blocking fault is recorded
- handover updated with exact cloud URIs, worker counts, trial counts, and verdict
