---
entry_id: 20260309_074955_asymmetric_label_pivot_mission_open
task_id: TASK-V645-GC-ASYMMETRIC-LABEL-PIVOT
timestamp_local: 2026-03-09 07:49:55 +0000
timestamp_utc: 2026-03-09 07:49:55 +0000
operator: Codex
role: commander
branch: main
status: active
---

# V645 Mission Open: Asymmetric Label Pivot

## 1. Why The Previous Mission Stops Here

The V644 alpha-first pilot proved:

- cloud fan-out works
- alpha-first aggregation works
- fresh-prefix isolation works

But it also hit its explicit stop gate:

- `20 / 20` trials were AUC-eligible
- `0 / 20` trials had positive validation `alpha_top_quintile`

The external architect audit now treats this as a stronger bottleneck than simple leaderboard selection.

## 2. New Canonical Diagnosis

Accepted external verdict from:

- `audit/v644_mediocristan_label_bottleneck.md`

Core claim:

- the bottleneck is now the ML label / objective interface
- not the frozen `v64.3 / v643` math core

## 3. Mission Objective

Run the minimum decisive experiment that can test the external verdict without reopening math-governance.

That means:

- keep `omega_core/*` frozen
- keep Stage3 gates frozen
- keep frozen holdout outputs immutable
- pivot the XGBoost training interface so the learner can see return magnitude

## 4. Allowed Experiment Family

This mission is restricted to two candidate interface pivots:

### Path A

- keep `binary:logistic`
- keep `label = (t1_excess_return > 0)`
- inject magnitude through training weights:
  - `sample_weight = abs(t1_excess_return)`
- remove the hard `AUC` floor
  - or collapse it to a near-null gate such as `0.501`

### Path B

- switch model objective to `reg:squarederror`
- switch label to:
  - `label = t1_excess_return`
- rank validation tails by predicted expected return magnitude
- do not preserve the old `AUC` floor as a gating condition

## 5. Execution Rule

The next implementation wave must choose the **minimum decisive** path, not both at once, unless AgentOS proves that a dual-path compare is cheaper and cleaner than a single-path test.

Default commander preference before AgentOS review:

- prefer **Path A first**

Reason:

- narrower patch surface
- cheaper rollback
- cleaner test of the audit claim that magnitude blindness alone is the bottleneck

## 6. Required Runtime Shape

The first live test under this mission must be:

- a micro-sweep
- `10-20` trials total
- local or `1`-worker GCP
- fresh output prefix only

This mission must not:

- widen cloud budget before the pivot is validated
- rerun frozen holdouts until a new pivot champion exists

## 7. What Success Looks Like

The first success gate is narrow:

- the pivoted micro-sweep produces at least one validation trial with positive `alpha_top_quintile`

Only after that should the mission consider:

- champion retrain
- fresh holdout evaluation on `2025`
- fresh holdout evaluation on `2026-01`

## 8. What Would Falsify The External Verdict

If the pivoted micro-sweep still yields only negative validation tail alpha under a magnitude-aware learner interface, then the external verdict weakens and the repo should seriously consider:

- feature/label mismatch beyond simple weighting
- or a deeper follow-on mission on math / representation adequacy
