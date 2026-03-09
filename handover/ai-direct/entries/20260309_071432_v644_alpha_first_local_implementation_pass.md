---
entry_id: 20260309_071432_v644_alpha_first_local_implementation_pass
task_id: TASK-V644-GC-SWARM-ASYMMETRIC-OBJECTIVE-LOCAL-PASS
timestamp_local: 2026-03-09 07:14:32 +0000
timestamp_utc: 2026-03-09 07:14:32 +0000
operator: Codex
role: commander
branch: main
status: completed
---

# V644 Alpha-First Local Implementation Pass

## 1. Scope Completed

The bounded V644 code wave is now implemented locally on:

- `tools/run_optuna_sweep.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_swarm_aggregate.py`

## 2. What Changed

### 2.1 Worker payload

`tools/run_optuna_sweep.py` now supports:

- `--objective-metric`
  - `val_auc`
  - `alpha_top_quintile`
  - `alpha_top_decile`
- `--min-val-auc`

Each trial row now records:

- `objective_metric`
- `objective_value`
- `raw_objective_value`
- `auc_guardrail_min`
- `auc_guardrail_passed`
- existing `val_auc`
- existing alpha diagnostics

Alpha-first mode is explicit:

- if `objective_metric != val_auc` and `min_val_auc <= 0`, the payload hard-fails
- AUC-ineligible alpha trials get a hard losing objective score, but still emit their raw metrics for audit

### 2.2 Aggregator

`tools/aggregate_vertex_swarm_results.py` now:

- accepts `--objective-metric`
- accepts `--min-val-auc`
- accepts `--objective-epsilon`
- ranks only AUC-eligible rows
- chooses champion on the selected objective metric
- breaks ties by:
  - lower `max_depth`
  - lower `num_boost_round`
  - higher `val_auc`
- emits objective and guardrail metadata in:
  - `swarm_leaderboard.json`
  - `champion_params.json`

### 2.3 Launcher

`tools/launch_vertex_swarm_optuna.py` now:

- forwards `--objective-metric`
- forwards `--min-val-auc`
- forwards `--objective-epsilon`
- can enforce fresh output roots via:
  - `--require-empty-results-prefix`
  - `--require-empty-aggregate-output-uri`

## 3. Local Regression Proof

### Swarm regression suite

Command:

```bash
uv run --python /usr/bin/python3.11 --with pytest --with polars --with xgboost --with optuna pytest -q \
  tests/test_vertex_optuna_split.py \
  tests/test_vertex_swarm_aggregate.py
```

Result:

- `9 passed in 1.28s`

Coverage added / preserved:

- alpha-first payload records objective and AUC-guardrail fields
- AUC guardrail can demote a high-alpha but ineligible trial
- aggregator can choose higher alpha over higher AUC when both are eligible
- fresh-prefix guard rejects non-empty local prefixes
- legacy AUC-first path still works

### Holdout evaluator compatibility

Command:

```bash
uv run --python /usr/bin/python3.11 --with pytest --with polars --with xgboost --with optuna --with scikit-learn pytest -q \
  tests/test_vertex_holdout_eval.py
```

Result:

- `4 passed in 2.25s`

Meaning:

- the frozen holdout-evaluation path still imports and runs against the patched payload helpers

## 4. Operational Next Step

The next live step is now clear:

- launch the first V644 pilot on GCP with:
  - `2` workers
  - `n2-standard-16`
  - `spot`
  - `objective_metric=alpha_top_quintile`
  - `min_val_auc=0.75`
  - `objective_epsilon=1e-05`
  - `--force-gcloud-fallback`
  - `--watch`
  - fresh prefixes only

This pilot must not reuse:

- the frozen old pilot prefix
- the frozen holdout evaluation roots

## 5. Interpretation

At this point the mission is no longer blocked on ambiguous spec or missing code.

The remaining uncertainty is live runtime behavior only:

- whether alpha-first validation can produce at least one AUC-eligible positive `alpha_top_quintile` trial
- and whether that later converts into improved frozen-holdout alpha without touching the math layer
