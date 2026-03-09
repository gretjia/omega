---
entry_id: 20260309_124940_v649_path_b_flat_predictor_diagnosis_spec_draft
task_id: TASK-V649-PATH-B-FLAT-PREDICTOR-DIAGNOSIS
timestamp_local: 2026-03-09 12:49:40 +0000
timestamp_utc: 2026-03-09 12:49:40 +0000
operator: Codex
role: commander
branch: main
git_head: 8c08f84
status: draft_ready_for_external_gate
---

# V649 Spec Draft: Path B Flat-Predictor Diagnosis

## 1. Why This Mission Exists

V648 completed its first bounded Path B implementation wave but failed the local smoke gate.

Frozen evidence:

- `handover/ai-direct/entries/20260309_124249_v648_local_contract_and_smoke_blocked.md`

The failure pattern is now specific:

- `10 / 10` local Path B trials completed
- `0 / 10` passed the structural gate
- `max_val_spearman_ic = 0.0`
- `max_alpha_top_decile = 1.244533029128729e-20`
- `max_alpha_top_quintile = 1.244533029128729e-20`

Additional direct data probe on the frozen `2023 -> 2024` split now shows:

- train rows after canonical physics mask:
  - `379331`
- train zero `t1_excess_return` rows:
  - `346192`
- val rows after canonical physics mask:
  - `356832`
- val zero `t1_excess_return` rows:
  - `324210`
- both train and val median absolute excess return:
  - `0.0`

Interpretation:

- Path B did not merely “underperform”
- it appears to have collapsed into an almost-flat predictor under a target that is extremely sparse at exact zero

## 2. Proposed Mission Objective

Open a new bounded local diagnosis mission that explains why the current V648 Path B contract collapses into a flat predictor before any further learner changes are proposed.

Working mission name:

- `V649 Path B Flat-Predictor Diagnosis`

Mission purpose:

- explain the collapse mechanistically
- identify whether the dominant cause is:
  - target sparsity / scale
  - hyperparameter search range
  - loss / objective mismatch
  - DMatrix / feature pipeline issue
- produce a narrow evidence-backed recommendation for the next learner adjustment

## 3. What Must Stay Frozen

- `omega_core/*`
- `canonical_v64_1` Stage3 gates
- Stage1 / Stage2 / Stage3 forge code
- the immutable `2023,2024` train base matrix
- the immutable `2025` / `2026-01` holdouts
- no GCP
- no holdout evaluation rerun
- no model promotion

This mission is diagnostic only.

## 4. Scope

Writable scope:

- one optional local diagnostic tool under `tools/` if needed
- corresponding narrow tests only if diagnostic code is added
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

Read-only but relevant:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `handover/ai-direct/entries/20260309_124249_v648_local_contract_and_smoke_blocked.md`
- the frozen training matrix:
  - `gs://omega_v52_central/omega/staging/base_matrix/latest/stage3_train_2023_2024_20260309_005839/base_matrix_train_2023_2024.parquet`

Explicitly out of scope:

- any new learner promotion
- any new GCP swarm
- any holdout consumption
- any Path A reopening
- any new Stage3 artifact generation

## 5. Required Diagnostic Questions

V649 must answer, with concrete evidence:

1. Is the collapse primarily caused by target sparsity?
2. Are the Path B predictions actually constant or near-constant?
3. Does one deterministic regression probe recover non-trivial prediction variance if the search loop is removed?
4. Is the issue mainly:
   - the raw target scale
   - the loss
   - the search space
   - or the gating logic

## 6. Minimum Decisive Diagnostic Wave

### Wave 1: read-only data diagnosis

- quantify:
  - zero-mass of `t1_excess_return`
  - non-zero mass
  - train/val scale
  - dispersion

### Wave 2: deterministic single-model probe

- train one fixed Path B regression model locally on the same frozen split
- record:
  - train prediction std
  - val prediction std
  - train Spearman
  - val Spearman
  - top-decile / top-quintile alpha
  - best iteration
  - feature importance sparsity

### Wave 3: one bounded contrast only if necessary

- optionally compare one or two tiny local variants, but still:
  - no cloud
  - no holdouts
  - no promotion

## 7. Success Condition

This mission succeeds if it can name the dominant failure mode with direct evidence and narrow the next learner change to one bounded axis.

Examples of acceptable outcomes:

- “raw target is too zero-dominated; current regression collapses to the mean”
- “search space is too regularized; deterministic probe proves non-flat predictions are possible”
- “gating is not the bottleneck; learner output is already flat before ranking”

## 8. Non-Goals

This mission does not need to prove profitability.

It only needs to explain the flat-predictor collapse well enough that the next mission does not guess blindly.

## 9. Default Commander Bias

- local only
- diagnostics before redesign
- evidence before new learner pivot
- no cloud budget until the flat-predictor collapse is actually explained
