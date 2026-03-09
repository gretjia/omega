---
entry_id: 20260309_124249_v648_local_contract_and_smoke_blocked
task_id: TASK-V648-PATH-B-CONTINUOUS-LABEL-PIVOT
timestamp_local: 2026-03-09 12:42:49 +0000
timestamp_utc: 2026-03-09 12:42:49 +0000
operator: Codex
role: commander
branch: main
git_head: c075eda
status: completed
---

# V648 First Wave: Local Contract Pass, Local Smoke Blocked

## 1. Scope Executed

This first wave stayed inside the V648 local-first boundary:

- no GCP
- no holdout rerun
- no Stage3/base-matrix rebuild
- no `omega_core/*` or Stage3 gate changes

Executed files:

- `tools/run_optuna_sweep.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_swarm_aggregate.py`
- `tests/test_vertex_train_weight_mode.py`
- `tests/test_vertex_holdout_eval.py`

## 2. Contract Changes Landed

### Path B learner contract

- `learner_mode=reg_squarederror_excess_return`
- label = raw `t1_excess_return`
- Path B sample weights removed:
  - `weight_mode=none`

### Structural metric contract

- kept the V647 structural-tail objective shape
- replaced the structural floor for Path B with:
  - `val_spearman_ic > 0`
- kept tail composite:
  - `(alpha_top_decile + alpha_top_quintile) / 2`
- kept hard losing penalty when:
  - `alpha_top_decile < alpha_top_quintile`

### Parity changes

- sweep payload now supports Spearman-based Path B structural gating
- aggregator now supports Path B structural gating
- launch contract now supports the future Path B cloud path but was not used
- retrain payload now supports Path B regression + `weight_mode=none`
- holdout evaluator now emits:
  - `spearman_ic`

## 3. AgentOS Audit Convergence

Read-only packets returned:

- Plan Agent:
  - minimum decisive wave should be local-first Path B contract/test + local smoke
- Math Auditor:
  - `PASS WITH FIXES`
  - preserve frozen V64 math, continuous label, and no sample weights
- Runtime Auditor:
  - `PASS WITH FIXES`
  - no GCP before local smoke
  - no holdouts before retrain parity / gate pass

## 4. Local Regression Results

Validation commands:

- `python3 -m py_compile tools/run_optuna_sweep.py tools/aggregate_vertex_swarm_results.py tools/launch_vertex_swarm_optuna.py tools/run_vertex_xgb_train.py tools/evaluate_xgb_on_base_matrix.py`
- `uv run --with pytest --with polars --with xgboost --with scikit-learn python -m pytest tests/test_vertex_optuna_split.py tests/test_vertex_train_weight_mode.py tests/test_vertex_holdout_eval.py tests/test_vertex_swarm_aggregate.py -q`

Result:

- `36 passed in 7.92s`
- `py_compile` passed

## 5. Local Smoke Result

Runtime root:

- `audit/runtime/v648_local_smoke_20260309_123500/workers/w00`

Command shape:

- local only
- `10` trials
- `train=2023`
- `val=2024`
- `objective_metric=structural_tail_monotonicity_gate`
- `learner_mode=reg_squarederror_excess_return`
- `weight_mode=none`
- `min_val_spearman_ic=0.0`

Observed summary:

- `n_trials=10`
- `n_completed=10`
- `n_structural_guardrail_passed=0`
- `n_spearman_floor_passed=0`
- `best_value=-1000000000.0`
- `seconds=17.34`

More important than the hard-losing score:

- `max_val_spearman_ic=0.0`
- `max_alpha_top_decile=1.244533029128729e-20`
- `max_alpha_top_quintile=1.244533029128729e-20`

Interpretation:

- all `10` trials collapsed to effectively flat predictions on the `2024` validation slice
- the new Path B local smoke gate did **not** find a single trial with:
  - `val_spearman_ic > 0`
  - `alpha_top_decile > alpha_top_quintile`
  - `alpha_top_quintile > 0`

## 6. Gate Verdict

The explicit V648 local smoke gate failed.

Therefore:

- do **not** open GCP
- do **not** retrain a fresh champion
- do **not** consume `2025` or `2026-01`

## 7. Meaning

This first wave is still useful:

- it proves the V648 Path B contract is now mechanically implemented and test-covered
- it proves the first bounded regression pivot does **not** immediately produce a structurally valid local winner under the frozen `2023 -> 2024` split

But it is a blocked wave, not a promotion.

## 8. Immediate Next Step

V648 now needs a follow-on design decision before more runtime work:

- diagnose why Path B regressed into a flat predictor under the unweighted `reg:squarederror` contract
- do not spend cloud budget until a new local gate is defined and cleared
