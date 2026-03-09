---
entry_id: 20260309_133613_v650_local_robust_loss_kill_condition_triggered
task_id: TASK-V650-ZERO-MASS-GRAVITY-WELL
timestamp_local: 2026-03-09 13:36:13 +0000
timestamp_utc: 2026-03-09 13:36:13 +0000
operator: Codex
role: commander
branch: main
status: completed
---

# V650 Wave 1 Complete: Robust-Loss Branch Hit The Kill Condition

## 1. Scope Executed

V650 wave 1 stayed strictly inside the approved boundary:

- local-only
- sweep-only
- no GCP
- no holdouts
- no retrain execution
- no target transformation
- no Path A reopening

## 2. Files Changed

- `tools/run_optuna_sweep.py`
- `tests/test_vertex_optuna_split.py`

No other code surfaces were edited in wave 1.

## 3. Implemented Contract

Wave 1 implemented:

- new Path B learner mode:
  - `reg_pseudohuber_excess_return`
- explicit non-degeneracy guardrail:
  - `val_pred_std >= 1e-6`
  - rounded unique predictions `> 1`
  - non-zero feature-importance count `> 0`
- local continuation accounting:
  - `n_non_degeneracy_passed`
  - `n_local_continuation_passed`

## 4. Local Validation

- `python3 -m py_compile tools/run_optuna_sweep.py`
  - passed
- `uv run --with pytest --with polars --with xgboost --with scikit-learn python -m pytest tests/test_vertex_optuna_split.py -q`
  - `21 passed in 2.93s`

## 5. Local Runtime

Runtime root:

- `audit/runtime/v650_local_sweep_20260309_133400/worker_local`

Local command shape:

- `10` trials
- `objective_metric=structural_tail_monotonicity_gate`
- `learner_mode=reg_pseudohuber_excess_return`
- `weight_mode=none`
- `min_val_spearman_ic=0.02`

## 6. Result

Study summary:

- `n_trials = 10`
- `n_completed = 10`
- `n_structural_guardrail_passed = 0`
- `n_spearman_floor_passed = 0`
- `n_non_degeneracy_passed = 0`
- `n_local_continuation_passed = 0`
- `best_value = -1000000000.0`

All `10/10` trials stayed degenerate:

- `val_pred_std = 0.0` or `5.684341886080802e-14`
- rounded unique predictions:
  - `1`
- non-zero feature-importance count:
  - `0`
- `val_spearman_ic = 0.0`
- `val_auc = 0.5`

## 7. Audits

### Runtime audit

Verdict:

- `PASS`

Conclusion:

- runtime stayed within scope
- do not scale this setup to retrain, holdouts, or cloud

### Gemini `-p`

Verdict:

- `PASS`

Result verdict:

- `KILL CONDITION TRIGGERED`

Strongest interpretation returned:

- `reg:pseudohubererror` still collapses into flat predictions under the frozen raw `t1_excess_return` target
- therefore the zero-mass gravity well is not just an L2-loss artifact
- the raw 1-step continuous label contract is now the leading blocker

## 8. Operational Verdict

V650 succeeded as a diagnostic mission and failed as a continuation mission.

Per the approved V650 kill rule, this branch is now closed:

- robust loss did not escape the flat-predictor basin
- no local continuation gate was passed

## 9. Recommended Next Step

Do not open:

- retrain
- holdouts
- GCP

The next justified mission is now:

- a target-transformation mission

because the frozen raw `t1_excess_return` contract appears exhausted under Path B.
