---
entry_id: 20260309_112400_v647_gcp_swarm_and_holdout_gate_failed
task_id: TASK-V647-STRUCTURAL-TAIL-MONOTONICITY-GATE
timestamp_local: 2026-03-09 11:24:00 +0000
timestamp_utc: 2026-03-09 11:24:00 +0000
operator: Codex
role: commander
branch: main
status: completed
---

# V647 GCP Swarm And Holdout Gate: Failed

## 1. Objective

- Execute the architect-approved V647 live experiment after the local smoke gate passed.
- Run a fresh-prefix GCP swarm under the new structural tail-monotonicity contract.
- Retrain the resulting champion under the frozen Path A / `sqrt` contract.
- Test the promotion gate on both:
  - `2025`
  - `2026-01`

## 2. GCP Swarm Identity

Results prefix:

- `gs://omega_v52_central/omega/staging/swarm_optuna/v647_pilot_20260309_111500`

Aggregate prefix:

- `gs://omega_v52_central/omega/staging/swarm_optuna/v647_pilot_20260309_111500/aggregate`

Code bundle:

- `gs://omega_v52_central/omega/staging/code/swarm_optuna/20260309_111500/omega_core.zip`

Controller launch shape:

- `2` workers
- `10` trials per worker
- `20` total trials
- `spot`
- `n2-standard-16`
- `--force-gcloud-fallback`
- `objective_metric=structural_tail_monotonicity_gate`
- `min_val_auc=0.505`
- `weight_mode=sqrt_abs_excess_return`
- `learner_mode=binary_logistic_sign`

## 3. GCP Swarm Result

Both workers emitted artifact-complete outputs:

- `w00`
  - `best_value=0.00010923977563265819`
  - `n_auc_guardrail_passed=3`
  - `seconds=9.91`
- `w01`
  - `best_value=0.00010255143863535154`
  - `n_auc_guardrail_passed=2`
  - `seconds=9.7`

Aggregate champion:

- `worker_id=w00`
- `trial_number=2`
- `best_val_auc=0.5072357725415971`
- `alpha_top_decile=0.00011617716323408273`
- `alpha_top_quintile=0.00010230238803123365`
- `objective_value=0.00010923977563265819`

Fingerprint discipline held:

- `stage3_param_contract=canonical_v64_1`
- `signal_epi_threshold=0.5`
- `singularity_threshold=0.1`
- `srl_resid_sigma_mult=2.0`
- `topo_energy_min=2.0`

Control-plane note:

- Vertex state reporting lagged one worker after artifacts were already complete.
- Manual aggregation used completed worker outputs, not a speculative partial prefix.

## 4. Deterministic Retrain

Local retrain root:

- `audit/runtime/v647_champion_retrain_20260309_111700/model`

Retrain result:

- `status=completed`
- `base_rows=736163`
- `mask_rows=736163`
- `total_training_rows=736163`
- `seconds=6.2`
- `weight_mode=sqrt_abs_excess_return`

## 5. Fresh Holdout Results

### 5.1 2025 outer holdout

Execution host:

- `windows1-w1`

Metrics output:

- `D:\work\Omega_vNext\audit\runtime\holdout_eval_v647_2025_20260309_111700\results\holdout_metrics.json`

Result:

- `auc=0.45678581566340537`
- `alpha_top_decile=2.834900301646075e-05`
- `alpha_top_quintile=4.74009864016068e-05`

Promotion-gate verdict:

- `AUC > 0.505`
  - failed
- `alpha_top_decile > alpha_top_quintile`
  - failed
- `alpha_top_quintile > 0`
  - passed

### 5.2 2026-01 final canary

Execution host:

- `linux1-lx`

Metrics output:

- `/home/zepher/work/Omega_vNext/audit/runtime/holdout_eval_v647_2026_01_20260309_111700/results/holdout_metrics.json`

Result:

- `auc=0.4480397363190845`
- `alpha_top_decile=0.0002709845808747919`
- `alpha_top_quintile=6.184377649589757e-05`

Promotion-gate verdict:

- `AUC > 0.505`
  - failed
- `alpha_top_decile > alpha_top_quintile`
  - passed
- `alpha_top_quintile > 0`
  - passed

## 6. Final Verdict

- V647 succeeded as an implementation mission.
- V647 succeeded as a local-to-cloud structural objective experiment.
- V647 did produce validation-time champions that passed the new structural-tail contract.

But V647 failed the actual promotion gate:

- `2025` failed both:
  - structural AUC floor
  - tail monotonicity
- `2026-01` failed:
  - structural AUC floor

Therefore:

- the V647 branch is **not promotable**
- the V647 result must remain frozen as new audit evidence
- this mission does **not** replace the prior frozen V645 / V646 records
- any next mission must explain why validation-time structural gating still did not survive fresh future holdouts
