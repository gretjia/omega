# V655A Soft-Mass Mission Open

Status: Mission open
Date: 2026-03-10 03:37 UTC
Mission: V655A Soft-Mass Campaign Accumulation Audit

## Objective

Keep the full V654 daily spine, label stack, pulse compression, and event-study gate frozen while widening the campaign accumulation candidate stream from hard `is_signal` gating to soft physics-valid gating.

## Frozen

- daily spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier semantics
- same-sign pulse compression
- `PsiE_*`, `PsiT_*`, `PsiStar_*` formulas
- pure event-study gate
- ML / Vertex / holdout closure

## Single Allowed Change Axis

- do not require:
  - `is_signal == 1`
- still require:
  - `is_physics_valid == 1`
  - `abs(singularity_vector) > pulse_floor`

## Success Gate

- candidate mass must rise above the frozen V654 H1 baseline
- zero fractions must remain `0.0`
- `date_frac_flat_signal` must stay near `0.0`
- at least one primary `Psi` family must return:
  - `monotonic_non_decreasing = true`
