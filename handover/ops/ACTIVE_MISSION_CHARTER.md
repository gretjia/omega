# OMEGA Active Mission Charter

Status: In Progress
Task Name: V649 Path B Flat-Predictor Diagnosis
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

## 1. Objective

- Accept V648 as mechanically implemented but blocked at the local smoke gate.
- Keep V64 math, Stage3 gates, train matrix, and holdouts frozen.
- Diagnose why the current Path B regression contract collapses into a near-flat predictor on the frozen `2023 -> 2024` split.
- Produce an evidence-backed recommendation for the next bounded learner change.

## 2. Canonical Spec

Primary task-level implementation authority:

- `handover/ai-direct/entries/20260309_124249_v648_local_contract_and_smoke_blocked.md`
- `handover/ai-direct/entries/20260309_124940_v649_path_b_flat_predictor_diagnosis_spec_draft.md`
- `handover/ai-direct/entries/20260309_125400_v649_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_125420_v649_path_b_flat_predictor_diagnosis_mission_open.md`

Supporting context:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `OMEGA_CONSTITUTION.md`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- one optional local diagnostic tool under `tools/` if needed
- corresponding narrow tests only if diagnostic code is added
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

Read-only but relevant files:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- the frozen training matrix URI recorded in handover
- all frozen V648 runtime evidence

Explicitly out of scope:

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge
- any new base-matrix build
- any GCP launch
- any holdout consumption
- any model promotion
- any Path A reopening

## 4. Roles

Plan Agent:

- responsibility:
  - validate that the diagnosis wave is still minimal and local-only

Math Auditor:

- audit target:
  - verify that the diagnosis does not reopen frozen math or smuggle in new learner changes

Runtime Auditor:

- audit target:
  - verify that the diagnosis remains local-only and does not touch holdouts or cloud

## 5. Acceptance Criteria

- a concrete V649 mission-open authority exists in handover
- the active charter explicitly freezes:
  - `omega_core/*`
  - Stage3 gates
  - train matrix
  - holdouts
  - no GCP
- AgentOS plan/math/runtime packets have been issued for the first V649 wave
- the diagnosis produces concrete evidence for:
  - target sparsity / scale
  - prediction variance or collapse
  - deterministic single-model Path B behavior
- the mission ends with one bounded next-step recommendation

## 6. Runtime Preflight

Required before execution:

- controller only
- local-only commands
- fresh V649 runtime roots if any new artifacts are written
- no cloud endpoints
- no holdout paths

## 7. Fail-Fast Conditions

- stop if any step requires GCP
- stop if any step requires `2025` or `2026-01`
- stop if any step proposes a new learner branch before the collapse is explained
- stop if any step touches `omega_core/*` or Stage3 gates

## 8. Definition of Done

- V649 mission is active in handover
- the flat-predictor collapse is described with direct evidence
- one bounded next-step recommendation is produced
- handover updated
- Commander-only commit/push completed
