---
entry_id: 20260309_111100_v647_local_contract_and_smoke_pass
task_id: TASK-V647-STRUCTURAL-TAIL-MONOTONICITY-GATE
timestamp_local: 2026-03-09 11:11:00 +0000
timestamp_utc: 2026-03-09 11:11:00 +0000
operator: Codex
role: commander
branch: main
status: completed
---

# V647 Local Contract And Smoke: Pass

## 1. Objective

- Implement the first bounded V647 code wave locally.
- Enforce the new structural tail-monotonicity contract in both:
  - `tools/run_optuna_sweep.py`
  - `tools/aggregate_vertex_swarm_results.py`
- Prove the local smoke gate before any GCP swarm launch.

## 2. Code Contract Implemented

V647 now adds one new objective mode:

- `structural_tail_monotonicity_gate`

Worker and aggregator now share the same contract:

- raw score:
  - `(alpha_top_decile + alpha_top_quintile) / 2`
- hard losing penalty when:
  - `val_auc < 0.505`
- hard losing penalty when:
  - `alpha_top_decile < alpha_top_quintile`

V647 runtime lock is now explicit:

- `weight_mode=sqrt_abs_excess_return`
- `learner_mode=binary_logistic_sign`

Launcher propagation is also explicit now:

- `tools/launch_vertex_swarm_optuna.py` forwards `--learner-mode`
- launcher fails fast if a V647 run tries to launch with:
  - a non-`sqrt_abs_excess_return` weight mode
  - a non-`binary_logistic_sign` learner mode
  - `min_val_auc < 0.505`

## 3. Local Regression

Static compile:

- passed

Targeted tests:

- `23 passed in 1.25s`

Covered files:

- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_swarm_aggregate.py`

New regression intent:

- worker contract returns the mean of:
  - decile alpha
  - quintile alpha
  - only when both structural guards pass
- worker returns hard losing objective when:
  - `AUC < 0.505`
  - or tail monotonicity fails
- aggregator recomputes the same contract instead of trusting serialized objective values
- aggregator refuses:
  - sub-floor AUC trials
  - inverted-tail trials

## 4. Local Smoke Identity

Runtime root:

- `audit/runtime/v647_local_smoke_20260309_110859`

Run shape:

- local only
- `1` worker
- `10` trials
- `train_year=2023`
- `val_year=2024`
- `objective_metric=structural_tail_monotonicity_gate`
- `min_val_auc=0.505`
- `weight_mode=sqrt_abs_excess_return`
- `learner_mode=binary_logistic_sign`

## 5. Local Smoke Result

Worker summary:

- `n_trials=10`
- `n_completed=10`
- `n_auc_guardrail_passed=3`
- `best_value=0.0001092397756326582`

Local aggregator summary:

- `eligible_trials=3`
- `champion_pool_size=2`

Chosen local champion:

- `trial_number=2`
- `val_auc=0.5072357533131951`
- `alpha_top_decile=0.00011617716323408274`
- `alpha_top_quintile=0.00010230238803123366`
- `objective_value=0.0001092397756326582`

Gate interpretation:

- the local smoke produced at least one trial with:
  - `AUC >= 0.505`
  - `alpha_top_decile > alpha_top_quintile`
  - `alpha_top_quintile > 0`
- the local aggregator selected the same trial under the same composite rule

## 6. Verdict

- V647 first-wave local implementation is valid.
- The explicit escalation gate to GCP has been earned.
- The next authorized step is a fresh-prefix GCP swarm under the same frozen contract.
