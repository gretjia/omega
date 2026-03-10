# V654 H1 Psi-Primary Event Study Blocked

Status: Frozen runtime checkpoint
Date: 2026-03-10 03:04 UTC
Mission: V654 Identity-Preserving Pulse Compression

## What finished

- H1 2023 V654 forge completed on `linux1-lx`
- runtime root:
  - `audit/runtime/v654_probe_linux_h1_2023_20260310_015200`

Key forge facts:

- `rows=271447`
- `symbols=5448`
- `min_date=20230103`
- `max_date=20230417`
- `raw_candidates=3164`
- `kept_pulses=1449`
- `seconds=2052.6`

Zero-fraction confirmation:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

## What was scored

Pure event study was run on the primary directional V654 families only:

- `PsiE_5d`
- `PsiT_5d`
- `PsiStar_5d`
- `PsiE_10d`
- `PsiT_10d`
- `PsiStar_10d`
- `PsiE_20d`
- `PsiT_20d`
- `PsiStar_20d`

Artifacts:

- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200/event_study_v654_psi_primary.json`
- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200/event_study_v654_psi_primary.out`

Shared coverage facts:

- `n_dates_input=52`
- `n_dates_scored=51`
- `date_frac_flat_signal=0.0` for every tested signal

## Verdict

No tested `PsiE_*`, `PsiT_*`, or `PsiStar_*` horizon passed the unchanged monotonic event-study gate:

- all nine returned:
  - `monotonic_non_decreasing=false`

Selected spread facts:

- `PsiStar_10d`
  - `d10_minus_d1=0.007810853807582885`
  - `barrier_win_spread_d10_minus_d1=-0.01884973340647539`
- `PsiT_20d`
  - `d10_minus_d1=0.013091856875210577`
  - `barrier_win_spread_d10_minus_d1=-0.05463573005994288`

Under the frozen V654 gate, ML reopening remains blocked.

## Evidence

- `audit/v654_h1_psi_event_study_block_evidence.md`
