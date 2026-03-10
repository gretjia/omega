# V656 H1 Transition Event-Study Block Evidence

Status: Frozen evidence packet
Date: 2026-03-10
Mission: V656 Campaign-Transition Entry Audit

## Scope

This file records only the concrete H1 2023 V656 runtime evidence needed to justify the current no-go result for the transition-semantics branch.

It does not introduce new opinions or new mission directions.

## Runtime Artifacts

Evidence:

- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet`
- `audit/runtime/v656_transition_event_study_h1_2023_20260310_065013.json`
- `audit/runtime/v656_transition_event_study_h1_2023_20260310_065013.out`

## Frozen Runtime Basis

V656 did not rerun forge.

It reused the frozen V655B H1 campaign matrix:

- `rows=271447`
- `symbols=5448`
- `min_date=20230103`
- `max_date=20230417`
- `raw_candidates=136439`
- `kept_pulses=30449`
- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

## Transition Signal Family Tested

The bounded V656 runtime scored only:

- `dPsiAmpE_10d`
- `dPsiAmpE_20d`
- `dPsiAmpStar_10d`
- `dPsiAmpStar_20d`
- `FreshAmpE_10d`
- `FreshAmpE_20d`
- `FreshAmpStar_10d`
- `FreshAmpStar_20d`

## Event-Study Results

- `dPsiAmpE_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.0018636415316508632`
  - `barrier_win_spread_d10_minus_d1=0.016077627889375612`
  - `date_frac_flat_signal=0.0`
  - `n_dates_scored=51`
- `dPsiAmpE_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.005539094351094599`
  - `barrier_win_spread_d10_minus_d1=0.022361468875950363`
  - `date_frac_flat_signal=0.0`
  - `n_dates_scored=51`
- `dPsiAmpStar_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.001732611828707265`
  - `barrier_win_spread_d10_minus_d1=0.01740530268310414`
  - `date_frac_flat_signal=0.0`
  - `n_dates_scored=51`
- `dPsiAmpStar_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.009933468598393516`
  - `barrier_win_spread_d10_minus_d1=0.02240169706649414`
  - `date_frac_flat_signal=0.0`
  - `n_dates_scored=51`
- `FreshAmpE_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.0032813001265780636`
  - `barrier_win_spread_d10_minus_d1=0.0980978260869565`
  - `date_frac_flat_signal=0.0`
  - `n_dates_scored=46`
- `FreshAmpE_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.004375280933147704`
  - `barrier_win_spread_d10_minus_d1=0.08224637681159419`
  - `date_frac_flat_signal=0.0`
  - `n_dates_scored=46`
- `FreshAmpStar_10d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=0.0004144596430242656`
  - `barrier_win_spread_d10_minus_d1=0.02241715399610139`
  - `date_frac_flat_signal=0.0`
  - `n_dates_scored=48`
- `FreshAmpStar_20d`
  - `monotonic_non_decreasing=false`
  - `d10_minus_d1=-0.0025719187904036586`
  - `barrier_win_spread_d10_minus_d1=-0.020461744639376223`
  - `date_frac_flat_signal=0.0`
  - `n_dates_scored=48`

## Exact No-Go Facts

Under the frozen V656 mission gate:

1. Transition semantics were derived cleanly from the existing V655B campaign matrix.
2. Forge and gate semantics remained unchanged.
3. All eight tested transition families remained non-flat.
4. All eight tested transition families still returned `monotonic_non_decreasing=false`.
5. Therefore the pure event-study gate is still not passed.
6. Therefore ML reopening remains blocked.
