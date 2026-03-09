---
entry_id: 20260309_055200_gemini_asymmetric_objective_spec
task_id: TASK-V644-GC-SWARM-ASYMMETRIC-OBJECTIVE-SPEC
timestamp_local: 2026-03-09 05:52:00 +0000
timestamp_utc: 2026-03-09 05:52:00 +0000
operator: Codex
role: commander
branch: main
status: proposed
---

# Gemini Follow-On Spec: Asymmetric Objective Swarm

## 1. Request

- Read the frozen holdout verdict and prior swarm spec.
- Explain the meaning of:
  - high holdout `AUC`
  - negative holdout `alpha_top_decile` / `alpha_top_quintile`
- Propose the next mission and an operational spec suitable for OMEGA AgentOS.

## 2. Gemini Diagnosis

Gemini's core diagnosis:

- the current model learned strong global statistical separation
- but it failed in the tail where financial execution actually lives
- high `AUC` means the model ranks the whole distribution well on average
- negative top-quantile alpha means the highest-confidence rows still have negative expected excess return

Gemini's root-cause framing:

- the ML objective and the financial objective are misaligned
- the recent swarm optimized hyperparameters for global validation `AUC`
- that objective treats all rows equally
- it does not force the model to prioritize tail profitability
- the champion is therefore:
  - a good global classifier
  - a bad tail trader

## 3. Gemini-Recommended Mission Name

- `V644-GC-SWARM-ASYMMETRIC-OBJECTIVE`

## 4. Gemini Proposed Spec

### 4.1 Scope and constraints

- retain the exact immutable `base_matrix_train_2023_2024.parquet`
- retain the frozen canonical `v64_1` gate contract
- do not change `omega_core/*`
- solve the problem through cloud optimization orchestration first

### 4.2 Outer-loop objective shift

- modify `tools/run_optuna_sweep.py`
- change the Optuna objective from validation `AUC` to:
  - `alpha_top_decile`
  - or `alpha_top_quintile`
- keep `val_auc` as a logged secondary diagnostic

### 4.3 Leaderboard redesign

- modify `tools/aggregate_vertex_swarm_results.py`
- sort the leaderboard primarily by validation alpha
- if alpha deltas are within a small epsilon:
  - prefer the simpler model
  - lower `max_depth`
  - lower `num_boost_round`

### 4.4 Cloud execution plan

- run a new swarm on GCP with `8+` workers
- keep `n2-standard-16` as the default pilot machine
- deterministically retrain the new alpha-optimized champion
- evaluate it again on:
  - `base_matrix_holdout_2025.parquet`
  - `base_matrix_holdout_2026_01.parquet`

### 4.5 Success criterion

- if holdout alpha turns positive while the canonical contract remains unchanged, the objective shift succeeded

## 5. Gemini Risks and Open Questions

- tail overfitting:
  - optimizing only top-decile alpha on one validation year may overfit 2024-specific regime structure
- metric volatility:
  - alpha is noisier than `AUC`
  - the Optuna/TPE surrogate may behave worse on a jagged small-scale objective
- inner/outer objective mismatch may remain:
  - Optuna can optimize alpha in the outer loop
  - but XGBoost still trains internally on standard binary loss
  - if hyperparameter tuning alone is insufficient, a later mission may need a custom XGBoost objective

## 6. Gemini First AgentOS Steps

1. Create a new task entry for the asymmetric-objective mission.
2. Inspect `tools/run_optuna_sweep.py` and replace the Optuna return metric with the chosen validation alpha objective.
3. Inspect `tools/aggregate_vertex_swarm_results.py` and update ranking / champion selection to match the new alpha-first contract.
4. Run a small `2`-worker Vertex pilot first to verify metric scale and sampler stability before scaling to the full swarm.

## 7. Commander Interpretation

This Gemini output is directionally strong and operationally useful.

However, the next mission should preserve two explicit guards that Gemini left implicit:

- the frozen holdout verdict remains immutable audit baseline
- the first implementation step should still keep `AUC` as a hard guardrail, not just a logged metric, so the swarm does not drift into degenerate tail-only overfitting

Therefore this Gemini spec is accepted as the seed authority for the next mission, with AgentOS review to refine:

- exact alpha objective
- exact guardrails
- pilot size
- acceptance gates
