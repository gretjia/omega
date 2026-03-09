---
entry_id: 20260309_153149_v651_target_timescale_alignment_pivot_spec_draft
task_id: TASK-V651-TARGET-TIMESCALE-ALIGNMENT-PIVOT
timestamp_local: 2026-03-09 15:31:49 +0000
timestamp_utc: 2026-03-09 15:31:49 +0000
operator: Codex
role: commander
branch: main
git_head: 365a36f
status: draft_pending_owner_confirmation
---

# V651 Spec Draft: Target Timescale Alignment Pivot

## 1. Why This Mission Exists

New external audit authority:

- `audit/v651_target_timescale_disconnect.md`

That verdict closes a full diagnostic sequence:

1. Path A proved the physics signal can create structural leverage, but Path A is now exhausted.
2. Path B with `reg:squarederror` collapsed into a flat predictor.
3. Path B with `reg:pseudohubererror` also collapsed under the same raw `t1_excess_return` target.

Therefore the next bounded mission is not:

- another weight search,
- another loss swap,
- another Path A rescue,
- or a cloud expansion.

The next bounded axis is:

- **target horizon alignment**

The owner has also made the intended trading philosophy explicit:

- not ultra-short high-frequency behavior
- preference for several days to multi-week release windows
- practical interest in horizons that reach at least about 4 trading weeks

So V651 must test whether the frozen V64 physical signal becomes learnable when the target horizon is widened to match the slower release of compressed market energy.

## 2. Mission Objective

Open a new AgentOS mission that keeps Path B continuous regression as the leading branch, but replaces the microscopic `t1` target with a bounded multi-horizon ladder.

Working mission name:

- `V651 Target Timescale Alignment Pivot`

Mission purpose:

- keep the frozen V64 physics extraction intact,
- keep the current non-degeneracy discipline intact,
- change only the target horizon,
- and test whether a slower release window restores continuous target variance and positive rank structure.

## 3. Single Axis To Change

Only one modeling axis may change in V651:

- the forward target horizon

Everything else stays fixed at the V650 local Path B contract unless explicitly listed otherwise.

## 4. Frozen Constraints

These remain frozen:

- `omega_core/*`
- `delta = 0.5`
- `canonical_v64_1` Stage3 gates
- Path B continuous regression intent
- learner mode:
  - `reg_pseudohuber_excess_return`
- weight mode:
  - `none`
- non-degeneracy gates in the sweep path
- train / validation split:
  - train:
    - `2023`
  - validation:
    - `2024`
- holdout isolation:
  - `2025`
  - `2026-01`
- no Path A reopening
- no GCP in wave 1

## 5. Horizon Ladder

The initial bounded ladder is:

- `t5`
- `t10`
- `t20`

Interpretation:

- `t5`:
  - about 1 trading week
- `t10`:
  - about 2 trading weeks
- `t20`:
  - about 4 trading weeks

These horizons must be treated as separate fixed contracts.

V651 must not:

- blend multiple horizons into one label,
- average horizons together,
- or run multi-head prediction.

The mission is a ladder comparison, not a joint-target redesign.

## 6. Proposed Data Contract Change

The current train base matrix cannot supply this experiment as-is, because the active Stage3 contract only carries:

- `t1_fwd_return`

and the active training/evaluation entrypoints derive:

- `t1_excess_return`

from that one-step field.

So V651 wave 1 requires a new **train-only target-expanded base-matrix contract** for `2023,2024` that emits:

- `t5_fwd_return`
- `t10_fwd_return`
- `t20_fwd_return`

and preserves the frozen feature block unchanged.

Implementation note:

- these forward-return fields must be calculated inside:
  - `tools/forge_base_matrix.py`
- by extracting future daily closes from the loaded `raw_df`
- and joining the resulting horizon-aligned forward-return fields onto `base_df`
- so that:
  - `omega_core/trainer.py` remains completely frozen

Writable scope for this contract is expected to include:

- `tools/forge_base_matrix.py`
- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- narrow tests for the new target fields and horizon selection path

This mission must not modify:

- `omega_core/kernel.py`
- `omega_core/omega_math_core.py`
- `omega_core/omega_etl.py`

## 7. Runtime Shape

### Wave 1

Wave 1 is strictly:

- local-first
- train/validation only
- no holdouts
- no GCP
- no promotion

### Resource plan

Because Stage3/base-matrix forging has historically been faster on `windows1-w1`, and both nodes are currently idle, the default commander bias is:

- `windows1-w1`:
  - primary node for building the new train-only `2023,2024` target-expanded matrix
- controller:
  - local Optuna sweeps and comparison analysis
- `linux1-lx`:
  - reserved for parity verification only if a horizon clears the local gates

### Fresh artifact rule

All V651 artifacts must use fresh isolated prefixes and must not overwrite:

- frozen V645 / V646 / V647 / V648 / V649 / V650 evidence
- existing train / holdout base-matrix artifacts

## 8. Exact Required Changes

V651 wave 1 must implement:

1. a train-only Stage3/base-matrix contract that can carry separate forward-return fields for:
   - `t5`
   - `t10`
   - `t20`
2. a sweep contract that chooses one fixed horizon per run
3. a continuous regression evaluation path that computes horizon-matched excess returns per run
4. the existing non-degeneracy gates, unchanged:
   - `val_pred_std >= 1e-6`
   - rounded unique prediction count
   - non-zero feature-importance count
5. target diagnostics per horizon:
   - row count
   - `std`
   - `abs_mean`
   - `abs_median`
   - zero fraction

V651 wave 1 must not change:

- the learner loss
- the sample-weight contract
- the Optuna objective family
- the physics feature set

## 9. Roles

Plan Agent:

- responsibility:
  - confirm that V651 changes only the target horizon and the minimal data contract required to support it

Runtime Auditor:

- responsibility:
  - confirm that wave 1 remains local-only and train-only
  - confirm whether a new train-only matrix artifact is required

Math Reasoning Auditor:

- engine:
  - `gemini -p`
- responsibility:
  - verify that the horizon ladder is mathematically coherent with frozen V64 canon
  - verify that V651 does not reopen canonical math or label transformations beyond horizon expansion

## 10. Local Acceptance Gates

For V651 to earn continuation beyond wave 1, at least one horizon in:

- `t5`
- `t10`
- `t20`

must simultaneously satisfy:

- target zero fraction is lower than the frozen `t1` baseline
- `val_pred_std >= 1e-6`
- rounded unique predictions:
  - `> 1`
- non-zero feature-importance count:
  - `> 0`
- `val_spearman_ic > 0.02`

Diagnostic but not primary gate in V651 wave 1:

- `val_auc_sign`

It may be recorded for continuity, but it is not the primary continuation authority.

## 11. Kill Condition

Kill the branch immediately if the bounded ladder:

- still collapses to flat prediction,
- or fails to produce positive rank structure,
- across all three fixed horizons.

Concretely, V651 should be treated as failed if no horizon clears:

- `val_pred_std >= 1e-6`
- rounded unique predictions `> 1`
- non-zero feature-importance count `> 0`
- `val_spearman_ic > 0.02`

If this happens, the next mission is no longer another horizon search.

It must become:

- a deeper target-transformation mission
- or a learner-family redesign mission

## 12. Out Of Scope

- `omega_core/*`
- Path A
- sample weights
- loss-function swaps
- Stage1 / Stage2
- holdout evaluation in wave 1
- GCP in wave 1
- joint-horizon labels
- blended multi-horizon objectives

## 13. AgentOS Convergence Used In This Draft

Repo Math child returned:

- `PASS WITH FIXES`

Folded fixes:

- define the ladder in trading days
- keep each horizon as a separate fixed experiment
- treat joint or blended horizons as scope drift

Commander runtime/plan convergence folded into this draft:

- current train base matrix cannot supply `t5/t10/t20` as-is
- therefore a new train-only target-expanded matrix contract is required
- wave 1 must remain local-only and train-only

Math alignment for final draft approval is delegated to:

- `gemini -p`

## 14. Definition Of Done For Draft Stage

This draft is ready for owner confirmation only when:

- the new external audit authority is landed in `audit/`
- the V651 spec draft exists in handover
- AgentOS read-only convergence has been folded into the draft
- `gemini -p` returns `PASS` or `PASS WITH FIXES` and all required fixes are folded in

Only after owner confirmation may:

- `handover/ops/ACTIVE_MISSION_CHARTER.md` be switched
- V651 execution begin
