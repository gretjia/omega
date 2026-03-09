# OMEGA Active Mission Charter

Status: Completed
Task Name: V650 Zero-Mass Gravity Well
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

## 1. Objective

- Accept the external zero-mass verdict as the new canonical authority for Path B.
- Keep V64 math, Stage3 gates, raw label contract, train split, and holdouts frozen.
- Test whether a robust regression loss plus an explicit non-degeneracy gate can escape the zero-mass collapse without changing the raw `t1_excess_return` contract.
- Restrict wave 1 to a local-only, sweep-only proof before any retrain, holdout, or cloud work.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v650_zero_mass_gravity_well.md`
- `handover/ai-direct/entries/20260309_131310_v650_zero_mass_gravity_well_spec_draft.md`
- `handover/ai-direct/entries/20260309_131707_v650_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_132836_v650_zero_mass_gravity_well_mission_open.md`

Supporting context:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `OMEGA_CONSTITUTION.md`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_train_weight_mode.py`
- `tests/test_vertex_holdout_eval.py` (only if required for contract parity)
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

Read-only but relevant files:

- `OMEGA_CONSTITUTION.md`
- `omega_core/*`
- the frozen training matrix URI recorded in handover
- all frozen V648 / V649 runtime evidence

Explicitly out of scope:

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge
- any GCP launch
- any holdout consumption
- any model promotion
- any Path A reopening
- any target transformation
- any sample-weight comeback

## 4. Roles

Plan Agent:

- responsibility:
  - validate that wave 1 remains the minimum decisive local-only sweep

Math Auditor:

- audit target:
  - verify that the robust-loss pivot preserves frozen label/physics/split contracts

Runtime Auditor:

- audit target:
  - verify that wave 1 stays local-only, sweep-only, and does not touch holdouts or cloud

## 5. Acceptance Criteria

- a concrete V650 mission-open authority exists in handover
- the active charter explicitly freezes:
  - `omega_core/*`
  - Stage3 gates
  - raw `t1_excess_return`
  - split and holdouts
  - no sample weights
  - no GCP
- AgentOS plan/math/runtime packets have been issued for V650 wave 1
- code implements:
  - robust regression learner mode
  - explicit non-degeneracy gate
- local tests pass
- one local-only bounded sweep is executed
- the continuation gate is evaluated from real local output
- result has been recorded as:
  - kill condition triggered

## 6. Runtime Preflight

Required before execution:

- controller only
- local-only commands
- fresh V650 runtime root
- no cloud endpoints
- no holdout paths
- wave 1 must remain sweep-only

## 7. Fail-Fast Conditions

- stop if any step requires GCP
- stop if any step requires `2025` or `2026-01`
- stop if any step reopens target transformation
- stop if any step reopens Path A
- stop if any step adds sample weights back into Path B
- stop if any step touches `omega_core/*` or Stage3 gates

## 8. Definition of Done

- V650 mission is active in handover
- robust-loss Path B wave 1 is implemented
- local tests pass
- one bounded local sweep is executed
- result is recorded with a continuation / kill verdict
- handover updated
- Commander-only commit/push completed
