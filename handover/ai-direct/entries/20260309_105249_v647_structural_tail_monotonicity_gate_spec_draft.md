---
entry_id: 20260309_105249_v647_structural_tail_monotonicity_gate_spec_draft
task_id: TASK-V647-STRUCTURAL-TAIL-MONOTONICITY-GATE
timestamp_local: 2026-03-09 10:52:49 +0000
timestamp_utc: 2026-03-09 10:52:49 +0000
operator: Codex
role: commander
branch: main
git_head: e601041
status: draft_pending_owner_confirmation
---

# V647 Spec Draft: Structural Tail-Monotonicity Gate

## 1. Why This Mission Exists

New recursive audit authority:

- `audit/v647_anti_classifier_paradox.md`

That verdict makes four things explicit:

1. V64 math is still frozen and not the next change surface.
2. The monotone `Path A` weight-power family is closed.
3. Both promoted branches are globally insufficient:
   - V645 `abs`
   - V646 `sqrt`
4. The next defect is no longer weight magnitude. It is the outer-loop selection rule.

## 2. Proposed Mission Objective

Open a new AgentOS mission that fixes the `Path A` objective formulation so a local winner must also preserve structural integrity.

Working mission name:

- `V647 Structural Tail-Monotonicity Gate`

## 3. Exact Axis To Change

Only change:

- the Optuna outer-loop objective formulation in `tools/run_optuna_sweep.py`
- the aggregator champion rule in `tools/aggregate_vertex_swarm_results.py`
- the launcher / tests only as needed to carry the new scoring contract

Do not change:

- `omega_core/*`
- Stage3 gates
- label semantics
- temporal splits
- holdout isolation
- the weight family

## 4. What Must Stay Frozen

- V64 `omega_core` math canon
- `canonical_v64_1` Stage3 gate contract
- Path A learner label:
  - `label = (t1_excess_return > 0)`
- temporal split:
  - train `2023`
  - validation `2024`
- holdout isolation:
  - `2025`
  - `2026-01`
- weight mode:
  - lock to `sqrt_abs_excess_return`

This draft accepts the audit verdict that `sqrt_abs_excess_return` is the local peak of the closed power family.

## 5. Proposed Objective Contract

Replace the current single-metric tail objective with a composite objective plus hard structural guardrails.

### 5.1 Structural floor

- if `val_auc < 0.505`:
  - apply a massive penalty or prune the trial

### 5.2 Tail monotonicity composite

- base score:
  - `(alpha_top_decile + alpha_top_quintile) / 2`

### 5.3 Inverted-tail penalty

- if `alpha_top_decile < alpha_top_quintile`:
  - apply a heavy penalty

Reason:

- the sharpest edge must be the most profitable
- we must prevent “anti-classifier but lucky quintile” promotion

## 6. Scope Draft

Writable:

- `tools/run_optuna_sweep.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_swarm_aggregate.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

Read-only but relevant:

- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `audit/v647_anti_classifier_paradox.md`
- `audit/v646_path_a_power_family_surface.md`
- all frozen V645 / V646 slice records

Out of scope:

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge
- Path B
- new weight exponent search
- changing label semantics

## 7. Minimal Decisive Experiment

1. implement the composite objective locally
2. regression-test the new scoring and penalty logic
3. run a bounded `20-40` trial GCP swarm with:
   - `weight_mode=sqrt_abs_excess_return`
   - unchanged train/validation split
   - tree-structure hyperparameters only
4. retrain only if a new local / swarm champion satisfies the new guardrails
5. evaluate on both frozen holdouts

## 8. Acceptance Gate Draft

Promotion is allowed only if the chosen champion simultaneously achieves:

- `AUC > 0.505`
- `alpha_top_decile > alpha_top_quintile`
- `alpha_top_quintile > 0`

on both:

- `2025` outer holdout
- `2026-01` final canary

If any of these fail, promotion is blocked.

## 9. Open Question For Owner Confirmation

This draft follows the auditor exactly on the core mechanics.

The only thing I want you to confirm before I switch the active charter and start AgentOS execution is:

- do you want the structural floor to be:
  - a hard prune / hard losing penalty at `AUC < 0.505`
- and do you want the inverted-tail condition:
  - `alpha_top_decile < alpha_top_quintile`
  to be treated as a hard losing penalty, rather than only a soft tie-break?

My default recommendation is:

- yes, treat both as hard penalties

because the audit verdict was explicit that local victory must guarantee structural integrity.
