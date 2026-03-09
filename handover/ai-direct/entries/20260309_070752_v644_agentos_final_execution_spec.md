---
entry_id: 20260309_070752_v644_agentos_final_execution_spec
task_id: TASK-V644-GC-SWARM-ASYMMETRIC-OBJECTIVE-FINAL-SPEC
timestamp_local: 2026-03-09 07:07:52 +0000
timestamp_utc: 2026-03-09 07:07:52 +0000
operator: Codex
role: commander
branch: main
status: active
---

# V644 AgentOS Final Execution Spec

## 1. Why This Mission Exists

The frozen holdout verdict is now fixed audit evidence:

- `2025` holdout:
  - `auc=0.8235655072013123`
  - `alpha_top_decile=-0.00011772199576048959`
  - `alpha_top_quintile=-3.151894696127132e-05`
- `2026-01` holdout:
  - `auc=0.8097376879061562`
  - `alpha_top_decile=-0.0008295253060950895`
  - `alpha_top_quintile=-0.0002874404451020619`

Interpretation:

- current swarm produced a strong global classifier
- but not a positive future alpha ranker
- the next clean test is to keep `v64.3 / v643` math frozen and change only the cloud outer-loop selector

## 2. AgentOS Convergence

Plan, Math, and Runtime review all converged on the same narrowing:

- do not open math-governance yet
- do not touch `omega_core/*`
- choose one canonical alpha objective, not an ambiguous `decile or quintile`
- keep `AUC` as a hard eligibility guardrail
- keep new outputs on fresh prefixes only
- run a small pilot first before a wider cloud fan-out

## 3. Canonical Objective For V644

This mission now fixes one canonical primary objective:

- `objective_metric = alpha_top_quintile`

Supporting diagnostics remain:

- `alpha_top_decile`
- `val_auc`

Reason:

- `alpha_top_quintile` is less sparse and less jagged than `alpha_top_decile`
- it is still tail-focused enough to reflect ranking quality where execution matters

## 4. Hard Guardrails

These are mandatory in V644:

1. Frozen math and gates remain unchanged:
   - `signal_epi_threshold=0.5`
   - `singularity_threshold=0.1`
   - `srl_resid_sigma_mult=2.0`
   - `topo_energy_min=2.0`
   - `stage3_param_contract=canonical_v64_1`
2. Label contract remains unchanged:
   - `t1_excess_return = t1_fwd_return - mean(t1_fwd_return over [date, time_key])`
   - `label = (t1_excess_return > 0)`
3. `2025` and `2026-01` remain outside optimization.
4. The frozen holdout verdict remains immutable.
5. Alpha-first is explicit opt-in, not a silent default flip.
6. `val_auc` becomes a hard eligibility gate for alpha-first ranking.

## 5. Code-Level Contract

### 5.1 Worker payload

`tools/run_optuna_sweep.py` must support:

- `--objective-metric`
  - allowed:
    - `val_auc`
    - `alpha_top_quintile`
    - `alpha_top_decile`
- `--min-val-auc`

Required runtime behavior:

- if `objective_metric=val_auc`:
  - preserve legacy maximize-`AUC` behavior
- if `objective_metric` is alpha-based:
  - still compute all metrics
  - mark each trial as:
    - `auc_guardrail_passed=true/false`
  - if the trial fails `min_val_auc`, return a hard losing objective score
  - still persist the raw alpha diagnostics for audit

Each trial row must emit:

- `objective_metric`
- `objective_value`
- `raw_objective_value`
- `auc_guardrail_min`
- `auc_guardrail_passed`
- `val_auc`
- `alpha_top_quintile`
- `alpha_top_decile`

### 5.2 Aggregator

`tools/aggregate_vertex_swarm_results.py` must:

- accept the same `--objective-metric`
- accept the same `--min-val-auc`
- rank only AUC-eligible rows when alpha-first mode is active
- choose champion primarily by the canonical objective
- use an objective-scale epsilon, not the old AUC-scale `0.001`, for alpha-first tie windows
- break ties by:
  - lower `max_depth`
  - lower `num_boost_round`
  - higher `val_auc`

For the first V644 pilot:

- `objective_metric=alpha_top_quintile`
- `objective_epsilon=1e-05`
- `min_val_auc=0.75`

### 5.3 Launcher

`tools/launch_vertex_swarm_optuna.py` must:

- forward `--objective-metric`
- forward `--min-val-auc`
- forward the new objective epsilon to aggregation
- support fresh-prefix enforcement for:
  - results prefix
  - aggregate output prefix

The stable controller path remains:

- `--force-gcloud-fallback`

## 6. Pilot Shape

First live V644 pilot is intentionally small:

- `2` workers
- `n2-standard-16`
- `spot`
- async fan-out plus `--watch`
- immutable training artifact only:
  - `base_matrix_train_2023_2024.parquet`
- temporal split only:
  - `train_year=2023`
  - `val_year=2024`

## 7. Acceptance Gates

### 7.1 Implementation gates

- backward compatibility holds when `--objective-metric=val_auc`
- alpha-first payload emits explicit objective and AUC-guardrail fields
- aggregator can prefer higher alpha over higher AUC when both pass the guardrail
- aggregator excludes AUC-ineligible rows from champion selection
- launcher can reject reused output prefixes when asked

### 7.2 Pilot gates

- all workers prove the same frozen canonical fingerprint
- at least one completed trial is:
  - `auc_guardrail_passed=true`
  - and positive on `alpha_top_quintile`
- if no such validation trial exists, stop and inspect before widening the swarm

### 7.3 Mission-success gate

After a successful pilot:

- retrain the alpha-first champion on the same immutable `2023,2024` train artifact
- evaluate it on fresh runtime roots for:
  - `2025`
  - `2026-01`
- compare against the frozen baseline without overwriting it

## 8. What This Mission Can Prove

If the alpha-first champion improves future holdout alpha while the math contract remains frozen, the strongest conclusion is:

- `v64.3 / v643` math was already broadly usable
- the main failure lived in cloud objective selection

If alpha-first still fails on frozen holdouts, the next conclusion tightens:

- the issue is not just selector mismatch
- the next version may need a true math-governance mission
