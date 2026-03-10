# V659 Fixed-Contract Replication Audit

Status: External audit authority
Date: 2026-03-10
Mission: V659 Fixed-Contract Replication Audit

## Central Claim

After V658, the narrowest truthful remaining blocker is no longer low-level campaign-state construction, pre-ML sign-aware semantics, or the existence of raw one-sided trigger utility.

The narrowest blocker is:

- the fixed V657 winner has only been demonstrated on the same H1 2023 slice from which it was selected
- and the V658 learner did not convert that selected tail utility into a calibrated admitted-set hazard model

So the next mathematically honest question is not:

- "how do we reopen broader ML?"

It is:

- "does the exact fixed V657 contract replicate on a disjoint contiguous sample under unchanged forge, label, transition, and evaluator semantics?"

## Short Verdict

Keep broader ML closed.

V658 was a correct no-go:

- it kept the V657 contract fixed to:
  - `dPsiAmpE_10d`
  - `negative`
  - `90th` negative-tail admission
- it stayed local-only
- it still failed the constant-baseline logloss gate on both forward folds

This means broader ML / Vertex / holdout reopening is still not earned.

## What V658 Proved

By V658 time, the reused V655B campaign matrix already had:

- `rows=271447`
- `symbols=5448`
- `raw_candidates=136439`
- `kept_pulses=30449`
- widened excess-return zero fractions:
  - `0.0`
  - `0.0`
  - `0.0`

So the old low-level defects were already gone before V658 changed anything.

V658 then proved:

- the admitted set for the fixed contract is nontrivial
- the learner can sometimes improve same-count economics inside that admitted set
- but the learner still loses to the constant-baseline logloss on both folds

Therefore:

- the current surviving object is not yet a broadly admitted ML contract
- and the biggest unresolved ambiguity is now post-selection risk on the V657 winner

## Top Remaining Root Cause

The top remaining root cause is post-selection uncertainty.

V657 searched across:

- `8` signals
- `2` sides
- `3` thresholds

That is a `48`-contract evaluator surface.

The cleanest winner:

- `dPsiAmpE_10d`
- `negative`

was then reused immediately inside V658 on the same H1 2023 slice.

So the next honest move is:

- fixed-contract replication outside the selection slice

not:

- another ML objective tweak
- another learner family
- or a wider signal search

## Single Allowed Change Axis

Change only the evaluation sample.

Specifically:

- move from the selected H1 2023 slice used in V657 / V658
- to the first non-overlapping contiguous replication block available under the same frozen forge and label stack

Everything else remains frozen.

## What Must Stay Frozen

Keep frozen:

- `tools/forge_campaign_state.py`
- the repaired daily spine semantics
- the tradable label semantics:
  - `entry_open_t1`
  - `excess_ret_t1_to_Hd`
- the triple-barrier semantics
- same-sign pulse compression
- the V655A soft-mass candidate stream
- the V655B amplitude-aware daily fold
- the V656 transition derivation formulas
- the V657 sign-aware threshold semantics
- the V658 admission contract as a blocked artifact
- all broader ML / Vertex / holdout workflows

## Recommended Next Mission

Open:

- `V659 Fixed-Contract Replication Audit`

This is a non-ML mission.

It must test exactly one frozen contract:

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- thresholds:
  - `90`
  - `95`
  - `97.5`

on a disjoint contiguous replication window.

No signal search is allowed.
No learner is allowed.
No threshold search is allowed.

## Exact Mathematical Contract

Let the frozen replicated signal be:

- `x_{i,d} := dPsiAmpE_10d(i,d)`

computed under the unchanged V655B forge and V656 transition derivation.

Let the replication date set be:

- `D_rep`

with the hard rule:

- `D_rep` must be contiguous
- `D_rep` must not overlap the H1 2023 selection slice used in V657 / V658

For each date `d`, define the negative-side universe:

- `N_d := { i : x_{i,d} < -eps }`

For each frozen threshold `q in {0.90, 0.95, 0.975}`, define:

- `S_{d,q} := { i in N_d : |x_{i,d}| >= Q_q(|x_{j,d}| : j in N_d) }`

Use the existing sign-aware economic objects:

- signed return:
  - `R_{i,d} := -excess_ret_t1_to_10d(i,d)`
- signed hazard success:
  - `Y_{i,d} := 1{ barrier_10d(i,d) = -1 }`

Negative-side universe baselines:

- `Rbar^N := date-neutral mean of R over N_d`
- `Hbar^N := date-neutral mean of Y over N_d`

Threshold-selected summaries:

- `Rbar_q := date-neutral mean of R over S_{d,q}`
- `Hbar_q := date-neutral mean of Y over S_{d,q}`

This mission has:

- no learner
- no loss optimization
- no search surface beyond the frozen threshold ladder

## Pass Condition

V659 passes only if all of the following hold on `D_rep`:

1. Adequate coverage:
   - `n_dates_scored(q) >= 40`
   - for each `q in {0.90, 0.95, 0.975}`
2. Threshold tightening preserves sparsity:
   - scored-row counts are non-increasing as thresholds tighten
3. Signed-return tightening is non-decreasing:
   - `Rbar_0.90 <= Rbar_0.95 <= Rbar_0.975`
4. Sign-aware hazard tightening is non-decreasing:
   - `Hbar_0.90 <= Hbar_0.95 <= Hbar_0.975`
5. Strongest threshold beats within-side universe baseline on both metrics:
   - `Rbar_0.975 > Rbar^N`
   - `Hbar_0.975 > Hbar^N`
6. Strongest threshold remains economically positive:
   - `Rbar_0.975 > 0`

## Kill Condition

Kill V659 immediately if any of the following happen:

- the replication window overlaps the H1 2023 selection slice
- forge, label, barrier, transition, threshold, or side semantics are changed
- coverage falls below minimum usable level:
  - `< 40` scored dates at any threshold
- the tightening ladder fails on either signed return or hazard
- the strongest threshold does not beat the negative-side universe on both metrics

If V659 fails, the honest interpretation is:

- the current V657 winner is not yet replicated strongly enough to justify broader ML admission

not:

- "the next step is another objective rewrite"
