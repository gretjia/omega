# V655B H1 Amp-Primary Event Study Blocked

Status: Frozen runtime checkpoint
Date: 2026-03-10 05:42 UTC
Mission: V655B Phase-Amplitude Daily Fold

## What finished

- H1 2023 V655B forge completed on `linux1-lx`
- runtime root:
  - `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315`

Key forge facts:

- `rows=271447`
- `symbols=5448`
- `min_date=20230103`
- `max_date=20230417`
- `l1_files=72`
- `l2_files=72`
- `raw_candidates=136439`
- `kept_pulses=30449`
- `seconds=2058.7`

Zero-fraction confirmation:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

## What was scored

Pure event study was run on the primary V655B amplitude-aware families only:

- `PsiAmpE_5d`
- `PsiAmpT_5d`
- `PsiAmpStar_5d`
- `PsiAmpE_10d`
- `PsiAmpT_10d`
- `PsiAmpStar_10d`
- `PsiAmpE_20d`
- `PsiAmpT_20d`
- `PsiAmpStar_20d`

Artifacts:

- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/event_study_v655b_amp_primary.json`
- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/event_study_v655b_amp_primary.out`

Shared coverage facts:

- `n_dates_scored=52`
- `date_frac_flat_signal=0.0` for every tested signal

## Verdict

No tested `PsiAmpE_*`, `PsiAmpT_*`, or `PsiAmpStar_*` horizon passed the unchanged monotonic event-study gate:

- all nine returned:
  - `monotonic_non_decreasing=false`

Selected spread facts:

- `PsiAmpE_20d`
  - `d10_minus_d1=0.012483435193323365`
  - `barrier_win_spread_d10_minus_d1=-0.02206982001616653`
- `PsiAmpStar_20d`
  - `d10_minus_d1=0.007335202955253736`
  - `barrier_win_spread_d10_minus_d1=-0.013238747404038298`

Under the frozen V655B gate, ML reopening remains blocked.

## Evidence

- `audit/v655b_h1_amp_event_study_block_evidence.md`
