# V654 H1 Psi-Primary Event-Study Block Evidence

Status: Frozen evidence packet
Date: 2026-03-10
Mission: V654 Identity-Preserving Pulse Compression

## Scope

This file records only the concrete H1 2023 V654 runtime evidence needed to justify the current block on ML reopening.

It does not introduce new opinions or new mission directions.

## Runtime Root

- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200`

## Forge Completion Facts

Evidence:

- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200/forge.out`
- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200/campaign_matrix.parquet.meta.json`

Recorded forge facts:

- `rows=271447`
- `symbols=5448`
- `min_date=20230103`
- `max_date=20230417`
- `l1_files=72`
- `l2_files=98`
- `raw_candidates=3164`
- `kept_pulses=1449`
- `seconds=2052.6`

Zero-fraction facts:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

## Primary Psi Event-Study Artifacts

Evidence:

- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200/event_study_v654_psi_primary.json`
- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200/event_study_v654_psi_primary.out`

Signal family tested:

- `PsiE_5d`
- `PsiT_5d`
- `PsiStar_5d`
- `PsiE_10d`
- `PsiT_10d`
- `PsiStar_10d`
- `PsiE_20d`
- `PsiT_20d`
- `PsiStar_20d`

Shared scoring coverage facts:

- `n_dates_input=52`
- `n_dates_scored=51` for every tested signal
- `date_frac_flat_signal=0.0` for every tested signal

## Event-Study Results

### 5d Horizon

- `PsiE_5d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.005855469870880244`
  - `barrier_win_spread_d10_minus_d1=0.024345207681937653`
- `PsiT_5d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.0014078972709505905`
  - `barrier_win_spread_d10_minus_d1=-0.012851690086113254`
- `PsiStar_5d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0022823599985441166`
  - `barrier_win_spread_d10_minus_d1=0.0033681845587910098`

### 10d Horizon

- `PsiE_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0015289400109256032`
  - `barrier_win_spread_d10_minus_d1=-0.041688053445143536`
- `PsiT_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0008908149709625579`
  - `barrier_win_spread_d10_minus_d1=-0.052652183999796376`
- `PsiStar_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.007810853807582885`
  - `barrier_win_spread_d10_minus_d1=-0.01884973340647539`

### 20d Horizon

- `PsiE_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.0019292397070648296`
  - `barrier_win_spread_d10_minus_d1=-0.0559294460051164`
- `PsiT_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.013091856875210577`
  - `barrier_win_spread_d10_minus_d1=-0.05463573005994288`
- `PsiStar_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.007854023102070118`
  - `barrier_win_spread_d10_minus_d1=-0.052733492835084605`

## Exact Block Facts

Under the frozen V654 mission gate:

1. The H1 forge completed successfully.
2. The mechanical zero-mass defect stayed eliminated.
3. The primary directional `Psi` family was scored under the unchanged pure event-study gate.
4. All nine tested `PsiE_*`, `PsiT_*`, and `PsiStar_*` signals returned `monotonic_non_decreasing=false`.
5. Therefore the pure event-study gate is not passed.
6. Therefore ML reopening remains blocked.
