---
entry_id: 20260309_090713_v645_path_b_local_compare_weaker_than_path_a
task_id: TASK-V645-GC-ASYMMETRIC-LABEL-PIVOT-PATH-B
timestamp_local: 2026-03-09 09:07:13 +0000
timestamp_utc: 2026-03-09 09:07:13 +0000
operator: Codex
role: commander
branch: main
git_head: b5c3cd2
status: completed
---

# V645 Path B Local Compare: Weaker Than Path A

## 1. Objective

- Implement the minimum decisive `Path B` compare under the active V645 mission
- Keep frozen `v64.3 / v643` math and `canonical_v64_1` Stage3 gates unchanged
- Compare `Path B` only against the already-recorded local `Path A` evidence
- Do **not** promote directly to retrain or fresh holdout unless the local compare beats or materially challenges `Path A`

## 2. AgentOS Convergence Used

Two audit packets returned in time and both permitted the compare:

- Math Auditor:
  - `PASS WITH FIXES`
  - Path B may proceed if it remains a learner-interface-only change
  - remove the `AUC` guardrail entirely for the first Path B compare
- Runtime Auditor:
  - `PASS WITH FIXES`
  - run locally only
  - `1` worker
  - `10` trials
  - no retrain
  - no fresh holdout rerun
  - fresh runtime root only

Plan packet did not return before execution, so Commander continued using the narrower of:

- mission-open constraints
- Math Auditor constraints
- Runtime Auditor constraints

## 3. Code Wave Applied

Files changed:

- `tools/run_optuna_sweep.py`
- `tests/test_vertex_optuna_split.py`

What changed:

- added explicit learner modes:
  - `binary_logistic_sign`
  - `reg_squarederror_excess_return`
- Path B now uses:
  - `objective=reg:squarederror`
  - training label:
    - `t1_excess_return`
- binary sign labels are still preserved separately for diagnostics such as `AUC`
- alpha-first runs may now disable the `AUC` guardrail entirely:
  - `min_val_auc=0.0`
- trial payloads now record:
  - `learner_mode`
  - `auc_guardrail_enabled`

Local regression result:

- `12 passed in 1.39s`

## 4. Path B Run Identity

Runtime root:

- `audit/runtime/v645_path_b_local_20260309_090552`

Output root:

- `audit/runtime/v645_path_b_local_20260309_090552/worker_local`

Shape:

- local only
- `1` worker
- `10` trials
- `train_year=2023`
- `val_year=2024`
- `objective_metric=alpha_top_quintile`
- `min_val_auc=0.0`
- `auc_guardrail_enabled=false`
- `learner_mode=reg_squarederror_excess_return`
- `weight_mode=physics_abs_singularity`

## 5. Path B Result

Summary:

- `n_trials=10`
- `n_completed=10`
- `n_auc_guardrail_passed=10`
- `best_value=2.0080714362500344e-06`

Winning trial:

- `trial_number=0`
- params:
  - `max_depth=5`
  - `learning_rate=0.17254716573280354`
  - `subsample=0.892797576724562`
  - `colsample_bytree=0.8394633936788146`
  - `min_child_weight=2.716205044866802`
  - `gamma=0.7799726016810132`
  - `reg_lambda=0.0017073967431528124`
  - `reg_alpha=2.1423021757741068`
  - `num_boost_round=260`

Observed pattern:

- Path B did produce positive validation `alpha_top_quintile`
- but most trials collapsed into only two tiny outcome levels:
  - `2.0080714362500344e-06`
  - `1.244533029128729e-20`
- validation `AUC` stayed near coin-flip:
  - roughly `0.50 - 0.507`

## 6. Direct Compare Against Path A

Path A local reference:

- `handover/ai-direct/entries/20260309_080141_v645_path_a_local_micro_sweep_positive.md`

Path A local best:

- `best_value=6.299795037680448e-05`
- `weight_mode=abs_excess_return`
- `learner_mode`:
  - implicit binary logistic sign learner
- `AUC` guardrail:
  - `0.501`

Path B local best:

- `best_value=2.0080714362500344e-06`
- `weight_mode=physics_abs_singularity`
- `learner_mode=reg_squarederror_excess_return`
- `AUC` guardrail:
  - disabled

Key comparison:

- Path B is positive, so it is not falsified
- but Path B is materially weaker than Path A on the same `2023 -> 2024` local micro-sweep structure
- rough ratio:
  - Path A best objective is about `31x` larger than Path B best objective

Notable detail:

- the Path A winning hyperparameter shape also reappeared in Path B as `trial 7`
- under Path B it only produced:
  - `alpha_top_quintile=2.0080714362500344e-06`
- so the weaker result is not just a different Optuna seed artifact

## 7. Verdict

The current ordering is now clearer:

1. Path A:
   - strongest local signal so far
   - already progressed to fresh retrain and fresh holdout
2. Path B:
   - valid positive local signal
   - but materially weaker than Path A
   - not strong enough to displace Path A as the leading branch

Therefore:

- do **not** promote Path B directly to retrain / holdout yet
- do **not** reopen GC
- keep Path A as the leading branch
- treat Path B as a weaker but still informative fallback branch

## 8. Next Step

The next rational move is:

- stay local-first
- continue Path A refinement before any larger spend

If Path A stalls again, the repo can come back to Path B with a cleaner second compare, for example:

- Path B with a different weighting choice
- or Path B retrain only after a stronger local signal than this first compare
