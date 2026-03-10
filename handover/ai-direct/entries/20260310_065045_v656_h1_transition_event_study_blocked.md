# V656 H1 Transition Event Study Blocked

Status: Frozen runtime checkpoint
Date: 2026-03-10 06:50 UTC
Mission: V656 Campaign-Transition Entry Audit

## What finished

- V656 reused the frozen V655B H1 campaign matrix on `linux1-lx`
- no forge rerun was performed
- runtime artifacts:
  - `audit/runtime/v656_transition_event_study_h1_2023_20260310_065013.json`
  - `audit/runtime/v656_transition_event_study_h1_2023_20260310_065013.out`

## What was scored

Pure event study was run on the transition families only:

- `dPsiAmpE_10d`
- `dPsiAmpE_20d`
- `dPsiAmpStar_10d`
- `dPsiAmpStar_20d`
- `FreshAmpE_10d`
- `FreshAmpE_20d`
- `FreshAmpStar_10d`
- `FreshAmpStar_20d`

## Verdict

No tested transition family passed the unchanged monotonic event-study gate:

- all eight returned:
  - `monotonic_non_decreasing=false`

Selected spread facts:

- `FreshAmpE_20d`
  - `d10_minus_d1=0.004375280933147704`
  - `barrier_win_spread_d10_minus_d1=0.08224637681159419`
- `FreshAmpStar_10d`
  - `d10_minus_d1=0.0004144596430242656`
  - `barrier_win_spread_d10_minus_d1=0.02241715399610139`

Under the frozen V656 gate, ML reopening remains blocked.

## Evidence

- `audit/v656_h1_transition_event_study_block_evidence.md`
