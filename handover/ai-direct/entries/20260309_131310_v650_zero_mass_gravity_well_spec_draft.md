---
entry_id: 20260309_131310_v650_zero_mass_gravity_well_spec_draft
task_id: TASK-V650-ZERO-MASS-GRAVITY-WELL
timestamp_local: 2026-03-09 13:13:10 +0000
timestamp_utc: 2026-03-09 13:13:10 +0000
operator: Codex
role: commander
branch: main
status: draft
---

# V650 Spec Draft: Path B Robust-Loss Escape From The Zero-Mass Gravity Well

## 1. Why This Mission Exists

V648 proved the first Path B continuous-label contract was mechanically implemented, but the local smoke collapsed.

V649 then isolated the failure mode:

- the frozen raw `t1_excess_return` target is heavily zero-dominated,
- the first regression search regime can collapse into a true constant predictor,
- naive variance recovery alone still does not satisfy the structural-tail contract.

The new external audit authority in:

- `audit/v650_zero_mass_gravity_well.md`

therefore recommends a narrower next mission:

- keep Path B as the leading branch,
- keep the raw `t1_excess_return` label frozen,
- add an explicit non-degeneracy gate,
- pivot the learner loss from L2 to a robust regression loss,
- stay local-only until the branch proves it can escape collapse with meaningful structure.

This is a sequence, not a contradiction:

- V649 correctly concluded that V649 evidence alone did not yet justify a new loss,
- V650 is the new authority that now explicitly justifies the bounded robust-loss pivot.

## 2. Mission Objective

Execute one bounded local Path B mission that tests whether a robust regression loss can escape the zero-mass gravity well without changing the canonical physics or the raw label contract.

The mission is successful only if the local branch can simultaneously:

- escape flat-predictor degeneration,
- recover positive structural ranking,
- and exceed random sign-direction competence.

## 3. Canonical Spec

Primary authority:

- `audit/v650_zero_mass_gravity_well.md`
- `audit/v649_path_b_flat_predictor_diagnosis.md`
- `handover/ai-direct/entries/20260309_124249_v648_local_contract_and_smoke_blocked.md`
- `handover/ai-direct/entries/20260309_125538_v649_flat_predictor_diagnosis_complete.md`

Supporting frozen canon:

- `OMEGA_CONSTITUTION.md`
- `omega_core/kernel.py`
- `omega_core/omega_math_core.py`
- `omega_core/omega_etl.py`
- `tools/forge_base_matrix.py` (read-only context only)

If this spec conflicts with `OMEGA_CONSTITUTION.md`, the constitution wins.

## 4. Frozen Constraints

These are explicitly frozen:

- `omega_core/*`
- `canonical_v64_1` Stage3 gates
- train / validation split:
  - train:
    - `2023`
  - validation:
    - `2024`
- holdout isolation:
  - `2025`
  - `2026-01`
- Path B raw label:
  - `label = t1_excess_return`
- sample weights:
  - `none`
- no GCP
- no holdout evaluation
- no Stage3 rebuild
- no Path A reopening

## 5. Single Axis To Change

Only one learner-modeling axis may change in V650:

- the XGBoost regression objective / loss function

Default choice for the first bounded wave:

- `reg:pseudohubererror`

This mission must also add an explicit non-degeneracy gate because the external audit identified flat predictors as a concrete bug in the current sweep/evaluation path.

The non-degeneracy gate is a guardrail, not a second modeling axis.

## 6. Exact Required Changes

In scope for code:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- narrow tests only for this new Path B robust-loss contract

But the first live runtime wave must remain:

- sweep-only
- local-only
- no retrain execution
- no holdout evaluation

So any `run_vertex_xgb_train.py` or `evaluate_xgb_on_base_matrix.py` changes inside V650 wave 1 are contract-parity changes only, not authorization to widen runtime scope.

Required behavior:

1. Path B local sweep must support:
   - `learner_mode=reg_pseudohuber_excess_return`
2. Path B evaluation must expose / enforce:
   - `val_pred_std`
   - non-degeneracy check:
     - if `val_pred_std < 1e-6`, the trial is hard-losing or pruned
3. Path B remains:
   - raw `t1_excess_return`
   - no sample weights
4. Path B structural metrics remain visible:
   - `val_spearman_ic`
   - `val_auc_sign`
   - `alpha_top_decile`
   - `alpha_top_quintile`
5. Non-degeneracy evidence must be visible before structural ranking is trusted:
   - rounded unique prediction count
   - non-zero feature-importance count

## 7. Roles

Plan Agent:

- responsibility:
  - confirm that this is still the minimum decisive local-only mission

Runtime Auditor:

- responsibility:
  - confirm the mission does not drift into GCP, holdouts, or base-matrix rebuilds

Math Reasoning Auditor:

- engine:
  - `gemini -p`
- responsibility:
  - audit the draft spec before execution
  - audit the code/result wave before any git close-out
  - verify that robust-loss pivot does not smuggle in label-contract or physics changes

Optional repo Math Auditor child:

- responsibility:
  - read-only check against local code/test semantics after implementation

## 8. Local Runtime Shape

Required runtime shape:

- controller only
- fresh isolated V650 runtime root
- local-only bounded sweep
- `10-20` trials total
- no cloud endpoints
- no holdout matrices
- no retrain or holdout commands in wave 1

## 9. Acceptance Gates

The bounded V650 wave earns continuation only if at least one local trial simultaneously satisfies:

- `val_pred_std >= 1e-6`
- `val_spearman_ic > 0.02`
- `val_auc_sign > 0.505`
- rounded unique predictions:
  - `> 1`
- non-zero feature-importance count:
  - `> 0`

These are local structural gates only.

`val_auc_sign > 0.505` is used here only as a continuation sanity gate for Path B.

It is not:

- a reopening of Path A classifier logic
- a promotion rule
- a holdout requirement

Even if they pass, V650 still does not automatically authorize:

- GCP
- holdouts
- promotion

It only authorizes drafting the next bounded step.

## 10. Kill Condition

This branch is killed immediately if the robust-loss plus non-degeneracy gate still yields:

- near-zero or negative `val_spearman_ic`
- and `val_auc_sign < 0.50`
- across the bounded local sweep

If that failure pattern appears, the raw `t1_excess_return` label contract should be treated as the next blocker, and the following mission must become a target-transformation mission.

## 11. Out Of Scope

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge
- any holdout rerun
- any GCP swarm
- any raw-label transformation
- any sample-weight comeback
- any Path A experiment

## 12. Definition Of Done

V650 draft is ready for owner confirmation only when:

- the external audit authority is landed
- the V650 draft exists in handover
- AgentOS read-only convergence agrees the scope is minimal
- `gemini -p` returns `PASS` or `PASS WITH FIXES` and all required fixes are folded into the draft

Only after owner confirmation may the active charter be switched and execution begin.
