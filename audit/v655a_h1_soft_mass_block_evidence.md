# V655A H1 Soft-Mass Block Evidence

Status: Frozen evidence packet
Date: 2026-03-10
Mission: V655A Soft-Mass Campaign Accumulation Audit

## Scope

This file records only the concrete H1 2023 V655A runtime evidence needed to justify the current no-go result for the soft-mass candidate-stream branch.

It does not introduce new opinions or new mission directions.

## Runtime Root

- `audit/runtime/v655a_probe_linux_h1_2023_20260310_034020`

## Forge Completion Facts

Evidence:

- `audit/runtime/v655a_probe_linux_h1_2023_20260310_034020/forge.out`
- `audit/runtime/v655a_probe_linux_h1_2023_20260310_034020/campaign_matrix.parquet.meta.json`

Recorded forge facts:

- `rows=271447`
- `symbols=5448`
- `min_date=20230103`
- `max_date=20230417`
- `l1_files=72`
- `l2_files=72`
- `raw_candidates=136439`
- `kept_pulses=30449`
- `seconds=2023.8`

Frozen V654 H1 comparison baseline:

- `raw_candidates=3164`
- `kept_pulses=1449`

Zero-fraction facts:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

## Primary Psi Event-Study Artifacts

Evidence:

- `audit/runtime/v655a_probe_linux_h1_2023_20260310_034020/event_study_v655a_psi_primary.json`

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
- `n_dates_scored=52` for every tested signal
- `date_frac_flat_signal=0.0` for every tested signal

## Event-Study Results

### 5d Horizon

- `PsiE_5d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0008635421605353813`
  - `barrier_win_spread_d10_minus_d1=0.0470116259621024`
- `PsiT_5d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.002053525742377266`
  - `barrier_win_spread_d10_minus_d1=0.009553895321434525`
- `PsiStar_5d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0028972701327285386`
  - `barrier_win_spread_d10_minus_d1=0.025943722718016482`

### 10d Horizon

- `PsiE_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.004088470854795381`
  - `barrier_win_spread_d10_minus_d1=0.006178186002161801`
- `PsiT_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.00253194992127`
  - `barrier_win_spread_d10_minus_d1=0.014692383648653773`
- `PsiStar_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.0030575397784101035`
  - `barrier_win_spread_d10_minus_d1=0.011012754965586291`

### 20d Horizon

- `PsiE_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.0008104959213473106`
  - `barrier_win_spread_d10_minus_d1=0.0014211861853448693`
- `PsiT_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.007152374815900409`
  - `barrier_win_spread_d10_minus_d1=0.01623460580201974`
- `PsiStar_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0044035652991915334`
  - `barrier_win_spread_d10_minus_d1=0.00028995223572925166`

## Exact No-Go Facts

Under the frozen V655A mission gate:

1. The soft-mass forge completed successfully.
2. Candidate mass rose materially above the frozen V654 H1 baseline.
3. The mechanical zero-mass defect stayed eliminated.
4. The primary directional `Psi` family was scored under the unchanged pure event-study gate.
5. All nine tested `PsiE_*`, `PsiT_*`, and `PsiStar_*` signals returned `monotonic_non_decreasing=false`.
6. Therefore the pure event-study gate is still not passed.
7. Therefore ML reopening remains blocked.
