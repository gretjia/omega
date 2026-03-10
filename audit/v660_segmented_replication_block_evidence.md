# V660 Segmented Replication Block Evidence

Status: Frozen evidence packet
Date: 2026-03-10
Mission: V660 Regime-Segmented Replication Audit

## Scope

This file records only the concrete V660 segmented-replication runtime evidence needed to justify the current no-go result.

It does not introduce a new mission direction.

## Runtime Artifacts

Evidence:

- `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/campaign_matrix.parquet`
- `audit/runtime/v660_segmented_replication_20260310_175918/segmented_audit.json`
- `audit/runtime/v660_segmented_replication_20260310_175918/segmented_audit.out`

## Frozen Runtime Basis

V660 did not rerun forge.

It reused the frozen V659 replication matrix:

- `rows=271720`
- `symbols=5524`
- `l1_files=73`
- `l2_files=101`
- `min_date=20230508`
- `max_date=20230814`
- widened zero fractions:
  - `5d = 0.0`
  - `10d = 0.0`
  - `20d = 0.0`

## Fixed Contract Tested

V660 kept the contract frozen to:

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- thresholds:
  - `90.0`
  - `95.0`
  - `97.5`

V660 changed only the evaluation-sample partition:

- deterministic `YYYYMM` month buckets

## Segment Summary

- `n_segments_total=4`
- `n_segments_eligible=3`
- `n_segments_passing=0`
- `n_segments_failing=3`
- `eligible_segments = [202305, 202306, 202307]`
- `failing_segments = [202305, 202306, 202307]`
- `mission_pass=false`

Ineligible segment:

- `202308`
  - `n_dates_input=6`
  - below the frozen minimum:
    - `n_dates_scored >= 10` per threshold

## Eligible Segment Facts

### Segment 202305

- `n_dates_input=13`
- threshold signed returns:
  - `90.0 -> -0.000534251843241415`
  - `95.0 -> 0.006377284336937434`
  - `97.5 -> -0.0001670535903299541`
- threshold hazards:
  - `90.0 -> 0.6809116809116809`
  - `95.0 -> 0.6280753968253968`
  - `97.5 -> 0.6333333333333333`
- checks:
  - `counts_non_increasing=true`
  - `signed_return_non_decreasing=false`
  - `hazard_non_decreasing=false`
  - `strongest_threshold_beats_universe_on_both=false`
  - `strongest_threshold_positive=false`

### Segment 202306

- `n_dates_input=16`
- threshold signed returns:
  - `90.0 -> 0.0029632474540068217`
  - `95.0 -> -0.009684701261401318`
  - `97.5 -> 0.00157729553662997`
- key failure:
  - signed-return tightening breaks at the middle threshold

### Segment 202307

- `n_dates_input=18`
- threshold signed returns:
  - `90.0 -> 0.01365616318253993`
  - `95.0 -> 0.008115122205567217`
  - `97.5 -> 0.018560557712998704`
- threshold hazards:
  - `90.0 -> 0.6766351968846348`
  - `95.0 -> 0.6993277408853192`
  - `97.5 -> 0.720314253647587`
- checks:
  - `counts_non_increasing=true`
  - `signed_return_non_decreasing=false`
  - `hazard_non_decreasing=true`
  - `strongest_threshold_beats_universe_on_both=true`
  - `strongest_threshold_positive=true`

## Exact No-Go Facts

Under the frozen V660 mission gate:

1. The audit reused the frozen V659 matrix and changed only sample partition.
2. Three month segments were eligible.
3. Zero eligible month segments passed the unchanged V659 ladder.
4. Therefore the V660 diagnostic pass condition was not satisfied.
5. Therefore `mission_pass=false`.
6. Therefore broader ML / Vertex / holdout reopening remains blocked.
