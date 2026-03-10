# V659 Fixed-Contract Replication Audit Blocked

Status: Frozen runtime checkpoint
Date: 2026-03-10 17:09 UTC
Mission: V659 Fixed-Contract Replication Audit

## What finished

- deployed commit:
  - `90147a0`
- remote runtime root:
  - `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408`
- forged replication block:
  - `20230508 -> 20230927`
- fixed replication contract:
  - `dPsiAmpE_10d`
  - `negative`
  - thresholds `90 / 95 / 97.5`

## Runtime result

The fixed-contract replication audit did **not** pass.

Forged matrix summary:

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

Negative-side universe:

- `n_rows_scored=13457`
- `n_dates_scored=52`
- `date_neutral_signed_return=-0.000932702001837508`
- `date_neutral_hazard_win_rate=0.6469217806341062`

Threshold ladder:

- `90.0`
  - `n_rows_scored=1390`
  - `signed_mean_excess_return=0.006726717157738988`
  - `sign_aware_hazard_win_rate=0.6641637964153685`
- `95.0`
  - `n_rows_scored=724`
  - `signed_mean_excess_return=0.0025035579338235055`
  - `sign_aware_hazard_win_rate=0.6771849450903277`
- `97.5`
  - `n_rows_scored=385`
  - `signed_mean_excess_return=0.010067510826228237`
  - `sign_aware_hazard_win_rate=0.6902806595114286`

Checks:

- `coverage_pass=true`
- `counts_non_increasing=true`
- `signed_return_non_decreasing=false`
- `hazard_non_decreasing=true`
- `strongest_threshold_beats_universe_on_both=true`
- `strongest_threshold_positive=true`

Mission result:

- `mission_pass=false`

## Consequence

- V659 did not replicate the frozen V657 winning contract strongly enough under the unchanged pass ladder
- the blocker was not coverage, not hazard tightening, and not strongest-threshold profitability
- the blocker was the failed signed-return tightening condition:
  - `0.006726717157738988 -> 0.0025035579338235055 -> 0.010067510826228237`
- broader ML / Vertex / holdout reopening remains blocked

## Evidence

- `audit/v659_replication_block_evidence.md`
- `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/campaign_matrix.parquet.meta.json`
- `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/replication_audit.json`
