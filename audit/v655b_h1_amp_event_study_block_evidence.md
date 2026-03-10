# V655B H1 Amplitude Event-Study Block Evidence

Status: Frozen evidence packet
Date: 2026-03-10
Mission: V655B Phase-Amplitude Daily Fold

## Scope

This file records only the concrete H1 2023 V655B runtime evidence needed to justify the current no-go result for the phase-amplitude daily-fold branch.

It does not introduce new opinions or new mission directions.

## Runtime Root

- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315`

## Forge Completion Facts

Evidence:

- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/forge.out`
- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet.meta.json`

Recorded forge facts:

- `rows=271447`
- `symbols=5448`
- `min_date=20230103`
- `max_date=20230417`
- `l1_files=72`
- `l2_files=72`
- `raw_candidates=136439`
- `kept_pulses=30449`
- `seconds=2058.7`

Zero-fraction facts:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

## Primary Amplitude Event-Study Artifacts

Evidence:

- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/event_study_v655b_amp_primary.json`
- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/event_study_v655b_amp_primary.out`

Signal family tested:

- `PsiAmpE_5d`
- `PsiAmpT_5d`
- `PsiAmpStar_5d`
- `PsiAmpE_10d`
- `PsiAmpT_10d`
- `PsiAmpStar_10d`
- `PsiAmpE_20d`
- `PsiAmpT_20d`
- `PsiAmpStar_20d`

Shared scoring coverage facts:

- `n_dates_scored=52` for every tested signal
- `date_frac_flat_signal=0.0` for every tested signal

## Event-Study Results

### 5d Horizon

- `PsiAmpE_5d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0006018862897953828`
  - `barrier_win_spread_d10_minus_d1=0.028404971420487035`
- `PsiAmpT_5d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0013381364955484874`
  - `barrier_win_spread_d10_minus_d1=0.0027734430571029756`
- `PsiAmpStar_5d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.0016404231353104241`
  - `barrier_win_spread_d10_minus_d1=0.025598384081239878`

### 10d Horizon

- `PsiAmpE_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.00143617973095501`
  - `barrier_win_spread_d10_minus_d1=-0.00385255974874138`
- `PsiAmpT_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=7.095916519856294e-05`
  - `barrier_win_spread_d10_minus_d1=-0.004268708387174691`
- `PsiAmpStar_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.0005494605819370374`
  - `barrier_win_spread_d10_minus_d1=0.017923248656336932`

### 20d Horizon

- `PsiAmpE_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.012483435193323365`
  - `barrier_win_spread_d10_minus_d1=-0.02206982001616653`
- `PsiAmpT_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0040510473807739405`
  - `barrier_win_spread_d10_minus_d1=-0.002344900504386016`
- `PsiAmpStar_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.007335202955253736`
  - `barrier_win_spread_d10_minus_d1=-0.013238747404038298`

## Exact No-Go Facts

Under the frozen V655B mission gate:

1. The phase-amplitude forge completed successfully.
2. The V655A soft-mass candidate stream remained live.
3. The mechanical zero-mass defect stayed eliminated.
4. The primary amplitude-aware `PsiAmp*` family was scored under the unchanged pure event-study gate.
5. All nine tested `PsiAmpE_*`, `PsiAmpT_*`, and `PsiAmpStar_*` signals returned `monotonic_non_decreasing=false`.
6. Therefore the pure event-study gate is still not passed.
7. Therefore ML reopening remains blocked.
