# OMEGA Active Mission Charter

Status: In Progress
Task Name: V648 Path B Continuous-Label Pivot
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

## 1. Objective

- Accept the recursive architect verdict that Path A is structurally exhausted.
- Keep V64 math, Stage3 gates, temporal splits, and holdout isolation frozen.
- Pivot the learner interface from weighted binary classification to Path B continuous-label regression.
- Test whether the frozen physical signal can survive translation into:
  - positive structural ranking
  - monotonic positive tail alpha
  - future-holdout stability

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v648_path_a_collapse_anti_classifier_paradox.md`
- `handover/ai-direct/entries/20260309_122200_v648_path_b_continuous_label_pivot_spec_draft.md`
- `handover/ai-direct/entries/20260309_122800_v648_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_122827_v648_path_b_continuous_label_pivot_mission_open.md`

Supporting context:

- `audit/v647_anti_classifier_paradox.md`
- `handover/ai-direct/entries/20260309_112400_v647_gcp_swarm_and_holdout_gate_failed.md`
- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `OMEGA_CONSTITUTION.md`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_optuna_sweep.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_swarm_aggregate.py`
- `tests/test_vertex_train_weight_mode.py`
- `tests/test_vertex_holdout_eval.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

Read-only but relevant files:

- `audit/v648_path_a_collapse_anti_classifier_paradox.md`
- `audit/v647_anti_classifier_paradox.md`
- all frozen V645 / V646 / V647 mission records
- `omega_core/*`

Explicitly out of scope:

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge
- any base-matrix rebuild
- any Path A weighting or label experiments
- widening to GCP before the first local smoke gate passes
- touching `2025` or `2026-01` holdouts before retrain parity exists
- overwriting any frozen V645 / V646 / V647 evidence

## 4. Roles

Plan Agent:

- responsibility:
  - validate that the first wave is the minimum decisive Path B contract/test implementation

Coder Agent:

- writable files only:
  - `tools/run_optuna_sweep.py`
  - `tools/aggregate_vertex_swarm_results.py`
  - `tools/launch_vertex_swarm_optuna.py`
  - `tools/run_vertex_xgb_train.py`
  - `tools/evaluate_xgb_on_base_matrix.py`
  - `tests/test_vertex_optuna_split.py`
  - `tests/test_vertex_swarm_aggregate.py`
  - `tests/test_vertex_train_weight_mode.py`
  - `tests/test_vertex_holdout_eval.py`

Math Auditor:

- audit target:
  - verify that V648 preserves frozen V64 math and the continuous-label pivot does not reopen Path A or math-governance

Runtime Auditor:

- audit target:
  - verify that the first wave stays local-first, keeps holdouts untouched, and does not widen to GCP before the local smoke gate passes

## 5. Acceptance Criteria

- a concrete V648 mission-open authority exists in handover
- the active charter explicitly freezes:
  - `omega_core/*`
  - Stage3 gates
  - temporal split
  - holdout isolation
  - Path A closure
- AgentOS plan/math/runtime packets have been issued for the first V648 wave
- the first wave implements:
  - `learner_mode=reg_squarederror_excess_return`
  - label = raw `t1_excess_return`
  - no sample weights in Path B
  - `val_spearman_ic <= 0` hard losing penalty / prune
  - composite score `(alpha_top_decile + alpha_top_quintile) / 2`
  - hard penalty when `alpha_top_decile < alpha_top_quintile`
- local tests pass
- one local smoke sweep proves or disproves the V648 local gate before any GCP swarm is launched

## 6. Runtime Preflight

Required before execution:

- target node:
  - controller first
- expected commit or branch:
  - `main`
- launcher mode:
  - local-first only for the first wave
- output root:
  - must be a fresh V648 prefix
- host isolation check:
  - no holdout matrix enters optimization
- learner mode:
  - must be `reg_squarederror_excess_return`
- weight contract:
  - no sample weights for Path B

## 7. Fail-Fast Conditions

- stop if the implementation changes:
  - `omega_core/*`
  - Stage3 gates
  - temporal split
  - holdout isolation
- stop if V648 can still silently use Path A sample weights in regression mode
- stop if worker and aggregator encode different structural-floor or tail-monotonicity logic
- stop if anyone proposes GCP before the first local smoke gate passes
- stop if holdout evaluation is attempted before retrain parity exists
- retry allowed only after named root cause and changed condition

## 8. Audits Required

Math audit must verify:

- frozen canonical math remains unchanged
- Path B uses continuous labels without reopening Path A
- the structural metric for Path B is Spearman-based, not AUC-based

Runtime audit must verify:

- first wave stays local-first
- the escalation gate to GCP is explicit
- no frozen evidence is overwritten
- holdouts remain untouched until replay parity exists

## 9. Definition of Done

- V648 mission is active in handover
- the first bounded code wave is implemented
- local regression tests pass
- one local smoke sweep validates the new Path B contract
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
- learner mode:
  - `reg_squarederror_excess_return`
- structural metric:
  - `val_spearman_ic`
- weight contract:
  - `none`
- fresh prefix check:
  - `passed`
