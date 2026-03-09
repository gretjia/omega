---
entry_id: 20260309_122200_v648_path_b_continuous_label_pivot_spec_draft
task_id: TASK-V648-PATH-B-CONTINUOUS-LABEL-PIVOT
timestamp_local: 2026-03-09 12:22:00 +0000
timestamp_utc: 2026-03-09 12:22:00 +0000
operator: Codex
role: commander
branch: main
git_head: 5850ff7
status: draft_pending_owner_confirmation
---

# V648 Spec Draft: Path B Continuous-Label Pivot

## 1. Why This Mission Exists

New recursive audit authority:

- `audit/v648_path_a_collapse_anti_classifier_paradox.md`

That verdict makes six things explicit:

1. V64 math remains closed and is not the next change surface.
2. V647 is frozen as a failed promotion but a successful diagnostic mission.
3. Path A is structurally exhausted:
   - weighted binary classification is no longer a valid leading branch
4. The monotone Path A power family remains closed.
5. The next change surface is no longer weighting or classifier-side guardrails.
6. The next bounded mission must pivot to a continuous-label learner interface:
   - `Path B`

## 2. Proposed Mission Objective

Open a new AgentOS mission that stops forcing a binary classifier to imitate asymmetric magnitudes.

Working mission name:

- `V648 Path B Continuous-Label Pivot`

Mission purpose:

- keep the frozen V64 physics extraction intact
- replace the broken Path A learner interface with a continuous-label regression contract
- test whether the frozen physical signal can survive translation into a structurally valid economic ranker

## 3. Exact Axis To Change

Change only the learner-mode and downstream scoring interface needed to support Path B.

Writable scope:

- `tools/run_optuna_sweep.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_swarm_aggregate.py`
- `tests/test_vertex_train_weight_mode.py`
- `tests/test_vertex_holdout_eval.py`
- handover docs for the new mission only after owner confirmation

Do not change:

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge code
- base-matrix artifacts
- temporal split years
- holdout artifacts
- any Path A weighting family

## 4. What Must Stay Frozen

- V64 `omega_core` math canon
- `canonical_v64_1` Stage3 gate contract
- temporal split:
  - train `2023`
  - validation `2024`
- holdout isolation:
  - `2025`
  - `2026-01`
- V647-style structural-tail outer-loop shape
- all frozen V645 / V646 / V647 runtime evidence

This draft accepts the new audit verdict that:

- Path A is dead
- Path B is the only justified next pivot

## 5. Proposed Learner Contract

### 5.1 Learner mode

- lock learner mode to:
  - `reg_squarederror_excess_return`

### 5.2 Label contract

- label becomes raw continuous magnitude:
  - `t1_excess_return`

### 5.3 Weight contract

- remove sample weights entirely for Path B
- do not inject:
  - `abs_excess_return`
  - `sqrt_abs_excess_return`
  - any other Path A weight mode

Reason:

- the audit verdict is explicit that magnitude is already present in the continuous target
- external weighting is now treated as harmful rather than helpful

## 6. Proposed Objective Contract

Keep the V647 structural-tail shape, but swap the structural metric from classifier AUC to rank correlation.

### 6.1 Structural floor

- compute validation `Spearman IC` on:
  - predicted expected return
  - versus actual `t1_excess_return`
- if `val_spearman_ic <= 0`:
  - apply a hard losing penalty or prune the trial

### 6.2 Tail composite score

- base score:
  - `(alpha_top_decile + alpha_top_quintile) / 2`

### 6.3 Tail-monotonicity gate

- if `alpha_top_decile < alpha_top_quintile`:
  - apply a hard losing penalty

### 6.4 Legacy classifier metrics

- any sign-style `AUC` may remain as a diagnostic field only
- `AUC` is no longer a structural floor for Path B

## 7. Execution Shape

This draft follows the architect verdict and the AgentOS read-only packets:

- local-first
- fresh-prefix only
- no holdout rerun before local contract and local smoke are both passed
- no cloud expansion before local smoke proves at least one structurally valid Path B trial exists

## 8. Minimal Decisive Experiment

### Wave 1: contract-and-tests only

- add Path B regression support to:
  - sweep
  - retrain
  - holdout evaluation
- add regression-side tests for:
  - continuous label contract
  - no-weight DMatrix construction
  - Spearman IC scoring
  - structural-tail aggregation

### Wave 2: local smoke only

- one fresh local micro-sweep
- `10` trials
- `train=2023`, `val=2024`
- `learner_mode=reg_squarederror_excess_return`
- no sample weights
- validation ranking by predicted expected return

### Wave 3: optional cloud pilot only if local smoke passes

- `10-20` total trials
- local or GCP is allowed by the architect verdict
- default commander bias:
  - only open GCP after the local smoke proves Path B can produce at least one structurally valid trial

## 9. Local Smoke Gate

Escalation beyond the local smoke is allowed only if at least one completed local trial achieves all of:

- `val_spearman_ic > 0`
- `alpha_top_decile > alpha_top_quintile`
- `alpha_top_quintile > 0`

If this local gate fails:

- stop
- do not open GCP
- do not touch holdouts

## 10. Promotion Gate Draft

Promotion is allowed only if the chosen Path B champion simultaneously achieves on both:

- `2025`
- `2026-01`

all of:

- `spearman_ic > 0`
- `alpha_top_decile > alpha_top_quintile`
- `alpha_top_quintile > 0`

If any one fails, promotion is blocked.

## 11. Explicit Non-Goals

This draft does not authorize:

- reopening Path A
- more Path A weight slicing
- reopening math-governance
- changing the frozen holdout artifacts
- rebuilding Stage3 base matrices
- using sample weights in Path B

## 12. AgentOS Convergence Used In This Draft

Read-only AgentOS packets that shaped this draft:

- Plan Agent:
  - Path B already partially exists in `run_optuna_sweep.py`
  - minimum decisive wave should first prove a regression-side structural gate locally
- Runtime Auditor:
  - do not open cloud before local smoke passes
  - do not consume holdouts before retrain parity exists

Math alignment for this draft is delegated to:

- `gemini -p`

## 13. Open Confirmation Question For Owner

This draft follows the architect verdict exactly on the branch decision:

- Path A closed
- Path B next

The only governance confirmation still required before switching the active charter is:

- do we treat `val_spearman_ic <= 0` as a hard prune / hard losing penalty
- and do we keep GCP closed until the local smoke clears that floor

My default recommendation is:

- yes to both

because the audit verdict is explicit that Path A failed by looking locally clever and holdout-fragile.
