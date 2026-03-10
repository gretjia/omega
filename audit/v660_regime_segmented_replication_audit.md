# V660 Regime-Segmented Replication Audit

Status: Commander audit authority
Date: 2026-03-10
Mission: V660 Regime-Segmented Replication Audit

## Central Claim

After V659, the narrowest truthful remaining blocker is no longer forge math, label construction, candidate mass, transition derivation, sign-aware evaluator semantics, or broad ML admission.

The narrowest blocker is:

- the fixed V657 / V659 winner did not satisfy the frozen signed-return tightening ladder on the disjoint replication block
- but it still retained:
  - adequate coverage
  - monotone threshold counts
  - monotone hazard tightening
  - strongest-threshold profitability
  - strongest-threshold outperformance versus the within-side universe

That pattern is narrower than "the contract is dead" and narrower than "the evaluator is wrong."

The next mathematically honest question is:

- does the V659 failure come from regime-mixed sample aggregation inside the replication block itself?

## Short Verdict

Do not reopen ML.

Do not change forge.

Do not change label, barrier, signal, side, threshold ladder, or sign-aware semantics.

Change only:

- the partition of the already-forged V659 replication sample

The next mission must remain non-ML and must diagnose whether the fixed contract behaves differently across deterministic contiguous subsegments of the replication block.

## Why This Is The Narrowest Repair Axis

V659 already established:

- `coverage_pass=true`
- `counts_non_increasing=true`
- `hazard_non_decreasing=true`
- `strongest_threshold_beats_universe_on_both=true`
- `strongest_threshold_positive=true`

and failed only:

- `signed_return_non_decreasing=false`

with:

- `90.0 -> 0.006726717157738988`
- `95.0 -> 0.0025035579338235055`
- `97.5 -> 0.010067510826228237`

So the current failure shape is:

- not flat
- not coverage-starved
- not hazard-broken
- not economically dead at the strongest threshold

This makes a broad evaluator rewrite too aggressive, and an exact-same-count/tie-handling tweak too weak.

## Single Allowed Change Axis

Change only the evaluation-sample partition.

Specifically:

- keep the fixed V659 forged matrix
- keep the fixed V659 contract
- keep the fixed V659 pass checks
- partition the replication sample into deterministic contiguous calendar-month segments

No other axis may move.

## What Must Stay Frozen

Keep frozen:

- `tools/forge_campaign_state.py`
- the repaired daily spine
- the tradable labels:
  - `entry_open_t1`
  - `excess_ret_t1_to_Hd`
- the triple-barrier semantics
- same-sign pulse compression
- the V655A soft-mass candidate stream
- the V655B amplitude-aware daily fold
- the V656 transition derivation formulas
- the V657 sign-aware threshold / hazard semantics
- the V658 blocked admission contract
- the V659 fixed contract:
  - `dPsiAmpE_10d`
  - `negative`
  - thresholds `90 / 95 / 97.5`
- all broader ML / Vertex / holdout workflows

## Recommended Next Mission

Open:

- `V660 Regime-Segmented Replication Audit`

This is a non-ML mission.

It must:

1. reuse the already-forged V659 replication matrix
2. reuse the exact fixed contract from V659
3. partition scored dates by deterministic calendar-month buckets
4. rerun the unchanged V659 threshold audit inside each eligible month segment

The mission is diagnostic and narrowing:

- it does not prove ML readiness
- it does not widen signal search
- it does not alter thresholds or side semantics

## Exact Mathematical Contract

Let the frozen signal be:

- `x_{i,d} := dPsiAmpE_10d(i,d)`

Let the fixed side be:

- `negative`

Let the frozen thresholds be:

- `q in {0.90, 0.95, 0.975}`

Let the frozen sign-aware objects remain:

- `R_{i,d} := -excess_ret_t1_to_10d(i,d)`
- `Y_{i,d} := 1{ barrier_10d(i,d) = -1 }`

Let the already-forged V659 replication sample be partitioned into deterministic month segments:

- `M = {YYYYMM buckets present in the replication matrix}`

For each month segment `m in M`, define the month-restricted date set:

- `D_m := { d : month(d) = m }`

Within each `D_m`, rerun the unchanged V659 contract:

- same negative-side universe
- same threshold-selected sets
- same date-neutral means
- same pass checks

## Segment Eligibility

A month segment is eligible only if all three thresholds satisfy:

- `n_dates_scored(q, m) >= 10`

This keeps the segmentation deterministic while discarding trivially tiny edge cases.

## V660 Diagnostic Pass Condition

V660 passes only if all of the following hold:

1. At least two month segments are eligible.
2. At least one eligible month segment fully passes the unchanged V659 ladder.
3. At least one eligible month segment fails the unchanged V659 ladder.

This means the replication-block failure is not uniformly global; it is regime-mixed inside the block.

## V660 Kill Condition

Kill V660 immediately if any of the following occur:

- any forge / label / barrier / transition / side / threshold semantics change
- the fixed contract changes
- fewer than two eligible month segments remain
- no eligible month segment passes the unchanged V659 ladder

If V660 fails, the honest interpretation is:

- the fixed V657 / V659 winner still lacks strong enough out-of-selection replication

not:

- "we should widen ML anyway"
