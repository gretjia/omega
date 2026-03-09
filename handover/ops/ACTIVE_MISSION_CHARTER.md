# OMEGA Active Mission Charter

Status: In Progress
Task Name: V647 Structural Tail-Monotonicity Gate
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

## 1. Objective

- Accept the recursive architect verdict that the monotone `Path A` weight family is closed.
- Refuse both V645 and V646 promoted branches as globally insufficient.
- Keep V64 math, Stage3 gates, and the Path A label contract frozen.
- Fix the downstream outer-loop selection rule so local winners preserve:
  - structural validity
  - tail monotonicity
  - positive tail alpha

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v647_anti_classifier_paradox.md`
- `handover/ai-direct/entries/20260309_105249_v647_structural_tail_monotonicity_gate_spec_draft.md`
- `handover/ai-direct/entries/20260309_105540_v647_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_110100_v647_structural_tail_monotonicity_gate_mission_open.md`

Supporting context:

- `audit/v646_path_a_power_family_surface.md`
- `handover/ai-direct/entries/20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass.md`
- `handover/ai-direct/entries/20260309_094727_v646_path_a_sqrt_refinement_mixed_holdout_verdict.md`
- `OMEGA_CONSTITUTION.md`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_optuna_sweep.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_swarm_aggregate.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

Read-only but relevant files:

- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `audit/v647_anti_classifier_paradox.md`
- `audit/v646_path_a_power_family_surface.md`
- `handover/ai-direct/entries/20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass.md`
- `handover/ai-direct/entries/20260309_094727_v646_path_a_sqrt_refinement_mixed_holdout_verdict.md`

Explicitly out of scope:

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge
- Path B
- new weight-family search
- changing label semantics
- widening to GCP before the first local smoke gate passes
- overwriting any frozen V645 / V646 evidence

## 4. Roles

Plan Agent:

- responsibility:
  - choose the minimum decisive first implementation wave inside the objective/aggregator axis only

Coder Agent:

- writable files only:
  - `tools/run_optuna_sweep.py`
  - `tools/aggregate_vertex_swarm_results.py`
  - `tools/launch_vertex_swarm_optuna.py`
  - `tests/test_vertex_optuna_split.py`
  - `tests/test_vertex_swarm_aggregate.py`

Math Auditor:

- audit target:
  - verify that V647 stays inside Path A and preserves frozen V64 math, labels, splits, and gates

Runtime Auditor:

- audit target:
  - verify that the first wave stays local-first and only escalates to GCP after the local smoke gate passes

## 5. Acceptance Criteria

- a concrete V647 mission-open authority exists in handover
- the active charter explicitly freezes:
  - `omega_core/*`
  - Stage3 gates
  - Path A label
  - temporal split
  - holdout isolation
  - `weight_mode=sqrt_abs_excess_return`
- AgentOS plan/math/runtime packets have been issued for the first V647 wave
- the first wave implements:
  - `val_auc < 0.505` hard penalty / prune
  - composite score `(alpha_top_decile + alpha_top_quintile) / 2`
  - hard penalty when `alpha_top_decile < alpha_top_quintile`
- local tests pass
- one local smoke sweep passes the escalation gate before any GCP swarm is launched

## 6. Runtime Preflight

Required before execution:

- target node:
  - controller first
- expected commit or branch:
  - `main`
- launcher mode:
  - local-first only for the first wave
- output root:
  - must be a fresh V647 prefix
- host isolation check:
  - no holdout matrix enters optimization
- weight mode:
  - must be `sqrt_abs_excess_return`
- learner mode:
  - must be `binary_logistic_sign`

## 7. Fail-Fast Conditions

- stop if the implementation changes:
  - `omega_core/*`
  - Stage3 gates
  - label semantics
  - temporal split
  - holdout isolation
- stop if V647 runs can still silently use a non-`sqrt_abs_excess_return` weight mode
- stop if worker and aggregator encode different composite/penalty logic
- stop if anyone proposes GCP before the first local smoke gate passes
- retry allowed only after named root cause and changed condition

## 8. Audits Required

Math audit must verify:

- frozen canonical math remains unchanged
- V647 stays inside Path A
- weight mode remains locked to `sqrt_abs_excess_return`

Runtime audit must verify:

- first wave stays local-first
- the escalation gate to GCP is explicit
- no frozen evidence is overwritten

## 9. Definition of Done

- V647 mission is active in handover
- the first bounded code wave is implemented
- local regression tests pass
- one local smoke sweep validates the new contract
- either:
  - the escalation gate to GCP is earned
  - or the mission records why local validation blocked further escalation
- handover updated
- Commander-only commit/push completed

## 10. Run Manifest

Record after execution:

- commit hash:
- node:
- launcher mode:
- dataset role:
- math audit verdict:
- runtime audit verdict:
- objective metric:
  - `structural_tail_monotonicity_gate`
- weight mode:
  - `sqrt_abs_excess_return`
- fresh prefix check:
  - `passed`
