# OMEGA Active Mission Charter

Status: Completed
Task Name: V643 holdout base-matrix evaluation of the swarm champion
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

Current checkpoint:

- The direct holdout evaluator now exists:
  - `tools/evaluate_xgb_on_base_matrix.py`
- Regression coverage now includes direct holdout scoring:
  - `tests/test_vertex_holdout_eval.py`
  - local result:
    - `9 passed`
- The same champion retrain artifact was evaluated against both isolated holdout matrices:
  - `2025` outer holdout on `windows1-w1`
  - `2026-01` final canary on `linux1-lx`
- Both runs validated:
  - exact date-prefix scope
  - canonical Stage3 gate overrides from `train_metrics.json`
  - `stage3_param_contract=canonical_v64_1`
- Final empirical result:
  - `2025`:
    - `auc=0.8235655072013123`
    - `alpha_top_decile=-0.00011772199576048959`
    - `alpha_top_quintile=-3.151894696127132e-05`
  - `2026-01`:
    - `auc=0.8097376879061562`
    - `alpha_top_decile=-0.0008295253060950895`
    - `alpha_top_quintile=-0.0002874404451020619`
- Mission conclusion:
  - the champion still separates classes on holdout
  - but its top-quantile excess-return proxies are negative on both holdouts
  - therefore the current cloud objective / champion rule is not yet sufficient as a positive future alpha filter

## 1. Objective

- Evaluate the completed swarm champion on the isolated downstream artifacts:
  - `base_matrix_holdout_2025.parquet`
  - `base_matrix_holdout_2026_01.parquet`
- Preserve holdout isolation:
  - no retraining on holdout
  - no mixing `2025` or `2026-01` back into optimization
- Use scoring semantics that match the active training / Optuna path:
  - same feature columns
  - same `t1_excess_return` label construction
  - same singularity masking

## 2. Canonical Spec

Primary task-level authority:

- `handover/ai-direct/entries/20260309_012152_gc_swarm_optuna_project_spec.md`
- `handover/ai-direct/entries/20260309_014638_gemini_swarm_spec_audit.md`
- `handover/ai-direct/entries/20260309_024658_three_matrix_partition_for_stage3.md`

Supporting operational context:

- `handover/ai-direct/entries/20260309_034012_holdout_matrices_dual_host_execution_complete.md`
- `handover/ai-direct/entries/20260309_050702_gc_swarm_optuna_pilot_and_champion_retrain_complete.md`
- `handover/ai-direct/LATEST.md`

Conflict rule:

- Holdout evaluation must not silently change the label or mask semantics relative to active train/Optuna code.
- If an evaluation shortcut would force frame-dir backtest semantics or year-only canary broadening, reject it.

## 3. Business Goal

- Convert the completed cloud pilot into real intelligence evidence:
  - do not stop at leaderboard AUC inside `2023,2024`
  - measure whether the chosen champion preserves useful ranking behavior on truly future data

## 4. Files In Scope

Implementation scope:

- `tools/evaluate_xgb_on_base_matrix.py`
- `tests/test_vertex_holdout_eval.py`

Handover scope:

- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

## 5. Out of Scope

- changing canonical Stage3 gate semantics
- rerunning Stage1 / Stage2 / Stage3 forge
- changing the champion parameters during holdout evaluation
- strategy-level interpretation of these metrics as a full production backtest

## 6. Required Audits

Implementation audit:

- evaluator must reuse active train/sweep base-matrix semantics
- evaluator must validate exact date-prefix scope
- evaluator must support one-class masked holdouts without crashing
- evaluator should validate gate overrides from retrain `train_metrics.json`

Runtime audit:

- `2025` must be evaluated before `2026-01`
- no fake parallelism over cross-host remote parquet mounts
- same champion artifact must be used on both holdouts

## 7. Runtime and Evidence Constraints

- Holdout artifacts remain separate:
  - `2025`
  - `2026-01`
- Worker runtimes used for this mission:
  - `windows1-w1`:
    - `C:\Python314\python.exe`
  - `linux1-lx`:
    - `/home/zepher/work/Omega_vNext/.venv/bin/python`
- The controller deploy path required manual recovery:
  - restore missing `linux` / `windows` git remotes
  - use `ext::ssh ...` for Windows

## 8. Acceptance Criteria

1. A direct base-matrix holdout evaluator exists in active `tools/`.
2. Local regression tests cover:
   - exact date-prefix scope checks
   - end-to-end holdout metric writeout
   - one-class masked holdout tolerance
3. `2025` outer holdout completes and writes a metrics artifact.
4. `2026-01` final canary completes and writes a metrics artifact.
5. Both runs prove canonical override alignment with the champion retrain metrics.
6. Handover records exact artifact paths, metrics, and verdict.

## 9. Fail-Fast Conditions

- If holdout evaluation falls back to frame-dir backtest semantics, stop.
- If `2026-01` scope is widened beyond the explicit January prefix, stop.
- If the evaluated artifact differs from the recorded champion retrain artifact, stop.
- If holdout evaluation changes the masking semantics relative to train/Optuna, stop.

## 10. Definition of Done

- evaluator committed and pushed
- workers synced to the new evaluator
- `2025` metrics recorded
- `2026-01` metrics recorded
- handover updated with the final downstream evidence and verdict
