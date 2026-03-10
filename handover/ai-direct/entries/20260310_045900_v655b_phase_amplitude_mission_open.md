# V655B Phase-Amplitude Mission Open

Status: Mission open
Date: 2026-03-10 04:59 UTC
Mission: V655B Phase-Amplitude Daily Fold

## Objective

Keep the V655A daily spine, tradable label stack, soft-mass candidate stream, same-sign pulse compression, and unchanged pure event-study gate frozen while changing only the daily fold for the `E` and `T` channels from sign-only projection to phase-amplitude projection.

## Frozen

- daily spine
- V655A soft-mass candidate stream
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier semantics
- same-sign pulse compression
- pure event-study gate
- ML / Vertex / holdout closure
- `omega_core/*`
- Stage2 artifacts

## Single Allowed Change Axis

- replace:
  - `F_epi = sum(E * sign(Phi))`
  - `A_epi = sum(E)`
  - `F_topo = sum(T * sign(Phi))`
  - `A_topo = sum(T)`
- with:
  - `F_epi_amp = sum(E * Phi)`
  - `A_epi_amp = sum(E * abs(Phi))`
  - `F_topo_amp = sum(T * Phi)`
  - `A_topo_amp = sum(T * abs(Phi))`

## Success Gate

- zero fractions must remain `0.0`
- `date_frac_flat_signal` must stay near `0.0`
- at least one `PsiAmpE_*`, `PsiAmpT_*`, or `PsiAmpStar_*` family must return:
  - `monotonic_non_decreasing = true`
