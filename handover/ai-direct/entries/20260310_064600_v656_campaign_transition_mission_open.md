# V656 Campaign-Transition Mission Open

Status: Mission open
Date: 2026-03-10 06:46 UTC
Mission: V656 Campaign-Transition Entry Audit

## Objective

Keep the V655A soft-mass candidate stream, V655B amplitude-aware daily fold, daily spine, tradable labels, same-sign pulse compression, and unchanged pure event-study gate frozen while changing only the scored signal semantics from campaign-state level to campaign-state transition.

## Frozen

- V655A soft-mass candidate stream
- V655B amplitude-aware daily fold
- daily spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier semantics
- same-sign pulse compression
- pure event-study gate
- `tools/forge_campaign_state.py`
- `omega_core/*`
- Stage2 artifacts
- ML / Vertex / holdout closure

## Single Allowed Change Axis

- derive in-memory transition families from the existing V655B campaign matrix:
  - `dPsiAmpE_10d`
  - `dPsiAmpE_20d`
  - `dPsiAmpStar_10d`
  - `dPsiAmpStar_20d`
  - `FreshAmpE_10d`
  - `FreshAmpE_20d`
  - `FreshAmpStar_10d`
  - `FreshAmpStar_20d`

## Success Gate

- transition signals remain non-flat
- at least one transition family returns:
  - `monotonic_non_decreasing = true`
- and:
  - `d10_minus_d1 > 0`
