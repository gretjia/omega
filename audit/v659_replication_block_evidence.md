# V659 Fixed-Contract Replication Block Evidence

Status: Frozen evidence packet
Date: 2026-03-10
Mission: V659 Fixed-Contract Replication Audit

## Scope

This file records only the concrete V659 replication runtime evidence needed to justify the current no-go result.

It does not introduce a new mission direction.

## Runtime Artifacts

Evidence:

- `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/campaign_matrix.parquet`
- `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/campaign_matrix.parquet.meta.json`
- `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/forge.out`
- `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/replication_audit.json`
- `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/replication_audit.out`

## Frozen Replication Basis

V659 forged a new campaign matrix on the frozen replication block:

- `20230508 -> 20230927`

Observed forged output:

- `rows=271720`
- `symbols=5524`
- `l1_files=73`
- `l2_files=101`
- `min_date=20230508`
- `max_date=20230814`
- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

## Fixed Contract Tested

V659 kept the contract frozen to:

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- thresholds:
  - `90.0`
  - `95.0`
  - `97.5`

Negative-side universe summary:

- `n_rows_scored=13457`
- `n_dates_scored=52`
- `date_neutral_signed_return=-0.000932702001837508`
- `date_neutral_hazard_win_rate=0.6469217806341062`

## Threshold Results

### Threshold 90.0

- `n_dates_scored=52`
- `n_rows_scored=1390`
- `signed_mean_excess_return=0.006726717157738988`
- `sign_aware_hazard_win_rate=0.6641637964153685`

### Threshold 95.0

- `n_dates_scored=52`
- `n_rows_scored=724`
- `signed_mean_excess_return=0.0025035579338235055`
- `sign_aware_hazard_win_rate=0.6771849450903277`

### Threshold 97.5

- `n_dates_scored=52`
- `n_rows_scored=385`
- `signed_mean_excess_return=0.010067510826228237`
- `sign_aware_hazard_win_rate=0.6902806595114286`

## Exact No-Go Facts

Under the frozen V659 mission gate:

1. Coverage passed:
   - `coverage_pass=true`
2. Threshold row counts tightened correctly:
   - `counts_non_increasing=true`
3. Hazard win rate tightened correctly:
   - `hazard_non_decreasing=true`
4. The strongest threshold beat the within-side universe on both metrics:
   - `strongest_threshold_beats_universe_on_both=true`
5. The strongest threshold remained economically positive:
   - `strongest_threshold_positive=true`
6. But the signed-return tightening ladder failed:
   - `signed_return_non_decreasing=false`
7. Therefore the frozen V659 pass condition was not satisfied.
8. Therefore `mission_pass=false`.
9. Therefore broader ML / Vertex / holdout reopening remains blocked.
