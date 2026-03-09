---
entry_id: 20260309_110100_v647_structural_tail_monotonicity_gate_mission_open
task_id: TASK-V647-STRUCTURAL-TAIL-MONOTONICITY-GATE
timestamp_local: 2026-03-09 11:01:00 +0000
timestamp_utc: 2026-03-09 11:01:00 +0000
operator: Codex
role: commander
branch: main
git_head: 738964c
status: active
---

# V647 Mission Open: Structural Tail-Monotonicity Gate

## 1. Objective

- Accept the recursive architect verdict in:
  - `audit/v647_anti_classifier_paradox.md`
- Refuse both V645 and V646 promoted branches as globally insufficient
- Keep V64 math and Path A label contract frozen
- Fix the downstream outer-loop objective so local winners preserve:
  - structural validity
  - tail monotonicity
  - positive tail alpha

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v647_anti_classifier_paradox.md`
- `handover/ai-direct/entries/20260309_105249_v647_structural_tail_monotonicity_gate_spec_draft.md`
- `handover/ai-direct/entries/20260309_105540_v647_spec_draft_gemini_pass.md`

Owner confirmation:

- confirmed to execute after Gemini `PASS`

## 3. Mission Boundary

Change only:

- `tools/run_optuna_sweep.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py` only if contract propagation requires it
- corresponding tests

Keep frozen:

- `omega_core/*`
- `canonical_v64_1` Stage3 gates
- Path A label:
  - `t1_excess_return > 0`
- temporal split:
  - `2023 -> 2024`
- holdout isolation:
  - `2025`
  - `2026-01`
- `weight_mode=sqrt_abs_excess_return`

## 4. Required First Wave

First wave is a bounded contract-and-tests wave:

- implement the composite objective locally
- implement the same contract in the aggregator
- validate locally
- run one local smoke sweep

Do not widen to GCP until the first local smoke clears the escalation gate.

## 5. Composite Objective Contract

Hard structural floor:

- if `val_auc < 0.505`:
  - hard losing penalty or prune

Tail monotonicity composite:

- score:
  - `(alpha_top_decile + alpha_top_quintile) / 2`

Inverted-tail penalty:

- if `alpha_top_decile < alpha_top_quintile`:
  - hard losing penalty

## 6. Promotion Gate

Any promoted champion must satisfy on both:

- `2025`
- `2026-01`

all three:

- `AUC > 0.505`
- `alpha_top_decile > alpha_top_quintile`
- `alpha_top_quintile > 0`

If any condition fails, promotion is blocked.
