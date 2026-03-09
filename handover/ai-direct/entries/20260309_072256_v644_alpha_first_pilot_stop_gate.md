---
entry_id: 20260309_072256_v644_alpha_first_pilot_stop_gate
task_id: TASK-V644-GC-SWARM-ASYMMETRIC-OBJECTIVE-PILOT-1
timestamp_local: 2026-03-09 07:22:56 +0000
timestamp_utc: 2026-03-09 07:22:56 +0000
operator: Codex
role: commander
branch: main
status: completed
---

# V644 Alpha-First Pilot 1: Stop Gate Triggered

## 1. Pilot Identity

- local runtime root:
  - `audit/runtime/swarm_optuna_v644_pilot_20260309_071719`
- results prefix:
  - `gs://omega_v52_central/omega/staging/swarm_optuna/v644_pilot_20260309_071719`
- aggregate prefix:
  - `gs://omega_v52_central/omega/staging/swarm_optuna/v644_pilot_20260309_071719/aggregate`
- code bundle:
  - `gs://omega_v52_central/omega/staging/code/swarm_optuna/20260309_071719/omega_core.zip`

## 2. Fixed Pilot Shape Used

- `2` workers
- `n2-standard-16`
- `spot`
- `train_year=2023`
- `val_year=2024`
- `objective_metric=alpha_top_quintile`
- `min_val_auc=0.75`
- `objective_epsilon=1e-05`
- `--force-gcloud-fallback`
- fresh result and aggregate prefixes enforced

## 3. Runtime Outcome

- workers:
  - `2 / 2` succeeded
- completed trials:
  - `20 / 20`
- AUC-eligible trials:
  - `20 / 20`
- canonical fingerprint:
  - matched across both workers
- temporal split proof:
  - matched across both workers

Per-worker best objective values:

- `w00`
  - `best_value=-4.910318402430983e-06`
  - `best_val_auc=0.7901190890538732`
  - `seconds=24.96`
- `w01`
  - `best_value=-1.5982936182562814e-05`
  - `best_val_auc=0.7949139136484219`
  - `seconds=21.66`

## 4. Aggregate Verdict

Champion artifact:

- `gs://omega_v52_central/omega/staging/swarm_optuna/v644_pilot_20260309_071719/aggregate/champion_params.json`

Key aggregate facts:

- `objective_metric=alpha_top_quintile`
- `objective_best_value=-4.910318402430983e-06`
- `best_val_auc=0.7955525583877963`
- `positive_alpha_top_quintile_eligible_trials=0`
- `positive_alpha_top_decile_eligible_trials=0`

Chosen champion:

- `worker_id=w00`
- `trial_number=5`
- `val_auc=0.7901190890538732`
- `alpha_top_quintile=-4.910318402430983e-06`
- `alpha_top_decile=-0.00010933823951250506`

## 5. Interpretation

This pilot proved the mechanics of the new mission:

- cloud-parallel fan-out remained real
- fresh-prefix isolation worked
- AUC guardrail enforcement worked
- alpha-first selection logic worked

But it also triggered the V644 stop gate:

- no AUC-eligible trial produced positive validation `alpha_top_quintile`

So the correct next action is:

- do **not** widen to a larger swarm yet
- do **not** retrain or re-run holdouts from this pilot
- inspect why the frozen `v64.3 / v643` feature-label interface still yields entirely negative tail alpha even under alpha-first search

## 6. What This Tightens

Compared with the frozen AUC-first baseline, this pilot strengthens the diagnosis:

- the problem is not only that champion selection preferred high `AUC`
- even when the outer loop directly optimizes `alpha_top_quintile` under a healthy `AUC` floor, the validation tail alpha remained negative across all `20` trials

This does not yet force a math-governance mission, because the pilot is still small.

But it does tighten the next question:

- is the failure driven by too-small search coverage
- or by a deeper feature/label/math mismatch that a larger alpha-first sweep still will not solve
