# System Architect Recursive Audit Verdict: The Zero-Mass Gravity Well

Status: Frozen external audit authority
Date: 2026-03-09
Scope: Frozen V64 canon + V648 blocked Path B smoke + V649 flat-predictor diagnosis

## Central Claim

Verdict:

- `PARTIAL ONLY`

Interpretation:

- the V64 math canon still successfully extracts the physical footprint of `Epiplexity`,
- but downstream intelligence translation remains unproven,
- because the current Path B learner can still collapse into mathematical paralysis.

## Short Verdict

Path B in V648 did not fail because continuous labels are conceptually wrong.

It failed because the learner fell into a **Zero-Mass Gravity Well**:

- about `91.2%` of train labels are exactly `0.0`,
- standard `reg:squarederror` is therefore incentivized to prune all trees and predict the median dead-zone,
- and when regularization is relaxed enough to recover variance, the model still learns micro-noise rather than stable structure.

## Ranked Root Causes

1. **Feature-label mismatch / timescale disconnect**
   - the V64 physics stack captures a 60-tick macroscopic compression process,
   - but Path B currently forces that to resolve into a microscopic `t1_excess_return` outcome,
   - which creates extreme zero-mass and timing hostility.
2. **Target sparsity / zero-mass gravity**
   - with roughly `91%` exact zeros, standard L2 loss strongly prefers dead-zone predictions.
3. **Regression search-space degeneracy**
   - the Path A-derived regularization/search regime mechanically permits or encourages no-split basins for this sparse continuous target.

## Concrete Bugs Or Weak Assumptions

- Weak assumption:
  - 60-tick topological compression should resolve reliably in exactly one tick.
- Weak assumption:
  - `reg:squarederror` is mathematically well matched to a zero-inflated, fat-tailed target.
- Concrete bug:
  - the current Path B sweep/evaluation path lacks an explicit non-degeneracy gate for flat predictors.

## Recommended Next Mission

Stay inside Path B, but change one axis only:

- keep the raw `t1_excess_return` label contract frozen,
- keep all physics and holdout isolation frozen,
- add an explicit non-degeneracy gate,
- pivot the learner objective from standard L2 to a robust regression loss such as:
  - `reg:pseudohubererror`
  - or `reg:absoluteerror`

## Exact Minimum Decisive Experiment

1. Add a variance-floor / non-degeneracy gate:
   - if `val_pred_std < 1e-6`, return a massive penalty or prune immediately.
2. Replace `reg:squarederror` with a robust regression loss while keeping:
   - raw `t1_excess_return`
   - no sample weights
3. Run a local-only `10-20` trial sweep.

## Convergence Plan

Freeze:

- `omega_core/*`
- `canonical_v64_1` gates
- `2023 -> 2024` split
- `2025` / `2026-01` holdout isolation
- raw `t1_excess_return` label

Change one axis:

- learner objective / loss function
- plus explicit variance-floor gate

Metrics that must improve together:

- `val_pred_std` must reliably escape zero,
- `val_spearman_ic` should become distinctly positive:
  - target `> 0.02`
- `val_auc_sign` should structurally exceed:
  - `0.505`

Immediate kill condition:

- if robust loss plus non-degeneracy gate still yields near-zero or negative `val_spearman_ic` and `val_auc_sign < 0.50` across the board,
- then the raw 1-tick label contract itself should be considered exhausted,
- and the next mission must become a target-transformation mission.

## Branch Decision

Path B should remain the leading branch.

Reason:

- Path A is already mathematically exhausted as the leading learner family,
- and the current Path B failure pattern is still explainable as a mechanical loss/sparsity mismatch,
- not as proof that continuous magnitude modeling is wrong.
