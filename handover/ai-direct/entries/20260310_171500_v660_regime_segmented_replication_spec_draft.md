# V660 Spec Draft: Regime-Segmented Replication Audit

Status: Draft
Date: 2026-03-10 17:15 UTC
Mission: V660 Regime-Segmented Replication Audit

## Why This Mission Exists

V659 already reused a disjoint contiguous replication block and the exact frozen V657 winner.

The result was mixed rather than dead:

- coverage passed
- threshold row counts tightened correctly
- hazard tightening passed
- strongest-threshold profitability passed
- strongest-threshold beat the within-side universe on both metrics

But the signed-return tightening ladder failed:

- `90.0 -> 0.006726717157738988`
- `95.0 -> 0.0025035579338235055`
- `97.5 -> 0.010067510826228237`

So the next honest question is narrower than another evaluator rewrite:

- is the V659 failure regime-mixed inside the replication block itself?

## Frozen Inputs

Keep frozen:

- `audit/v659_fixed_contract_replication_audit.md`
- `audit/v659_replication_block_evidence.md`
- `tools/forge_campaign_state.py`
- the repaired daily spine
- tradable labels and triple-barrier semantics
- the V655A soft-mass candidate stream
- the V655B amplitude-aware daily fold
- the V656 transition derivation formulas
- the V657 sign-aware threshold semantics
- the V658 blocked admission result
- the V659 fixed contract:
  - `dPsiAmpE_10d`
  - `negative`
  - thresholds `90 / 95 / 97.5`

## Single Allowed Change Axis

Change only:

- the evaluation-sample partition

Specifically:

- reuse the already-forged V659 replication matrix
- partition it into deterministic calendar-month segments
- rerun the unchanged V659 audit inside each eligible segment

## Writable Scope

- `tools/run_campaign_segmented_replication_audit.py`
- `tests/test_campaign_segmented_replication_audit.py`
- `audit/v660_*`
- `handover/ai-direct/entries/*`
- `handover/ai-direct/LATEST.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/BOARD.md`
- `audit/README.md`

## Out Of Scope

- changing forge math
- changing labels or barriers
- changing signal family
- changing side semantics
- changing threshold ladder
- changing date-neutral aggregation
- reopening ML / Vertex / holdout

## Deterministic Segmentation Rule

Let the V659 replication matrix dates be partitioned by:

- calendar-month buckets `YYYYMM`

For each month segment:

- keep only rows with `pure_date` in that month
- derive the fixed negative-side universe and threshold-selected sets exactly as V659 does

Eligible segment rule:

- each threshold must have `n_dates_scored >= 10`

## Diagnostic Objective

Use the unchanged V659 checks inside each eligible segment:

- `coverage_pass`
- `counts_non_increasing`
- `signed_return_non_decreasing`
- `hazard_non_decreasing`
- `strongest_threshold_beats_universe_on_both`
- `strongest_threshold_positive`

The mission does not change those rules.

## Mission Pass Condition

V660 passes only if:

1. at least two month segments are eligible
2. at least one eligible month segment fully passes the unchanged V659 ladder
3. at least one eligible month segment fails the unchanged V659 ladder

This would prove the current V659 failure is regime-mixed inside the replication block, not uniformly global.

## Mission Kill Condition

Kill V660 if:

- any frozen semantics drift
- fewer than two eligible month segments remain
- no eligible month segment passes the unchanged V659 ladder

## Runtime Shape

- local-only / non-ML
- reuse frozen V659 replication matrix:
  - `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/campaign_matrix.parquet`
- no forge rerun
- no holdout
- no Vertex

## Intended Deliverable

- one segmented replication JSON artifact
- one frozen evidence packet
- one explicit pass / block verdict
