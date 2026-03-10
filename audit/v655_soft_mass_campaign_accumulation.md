# V655 Soft-Mass Campaign Accumulation

Status: Frozen external audit authority
Date: 2026-03-10
Scope: Post-V654 repair axis

## Central Judgment

The V654 block is correct.

The widened H1 2023 runtime proved all of the following at once:

- the corrected daily spine and widened return labels eliminated the old mechanical zero-mass defect
- the tested `Psi` families are not flat
- the unchanged pure event-study gate still failed

Therefore:

- ML must remain blocked
- the next repair must stay strictly upstream of ML

## Frozen Facts From V654

Evidence:

- `audit/v654_h1_psi_event_study_block_evidence.md`
- `handover/ai-direct/entries/20260310_030400_v654_h1_psi_primary_event_study_blocked.md`
- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200/campaign_matrix.parquet.meta.json`
- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200/event_study_v654_psi_primary.json`

Frozen facts:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`
- `n_dates_scored = 51`
- `date_frac_flat_signal = 0.0` for all tested primary `Psi` signals
- all tested `PsiE_*`, `PsiT_*`, and `PsiStar_*` returned:
  - `monotonic_non_decreasing = false`

## Exact Diagnosis

This no longer primarily looks like a label-construction bug.

V654 already preserved the three-channel identity during campaign-state forging:

- `E`
- `T`
- `Phi`

and already applied:

- same-sign pulse compression
- multi-channel daily fold
- channel-specific campaign recursion

The most likely remaining blocker is narrower:

- the campaign accumulation candidate stream is still too sparse, too late, and too peak-only

Current V654 accumulation still requires the event row to pass:

- `is_signal == 1`
- and `is_physics_valid == 1`

before pulse compression and daily aggregation.

This is appropriate for row-level tactical triggering, but it may be too restrictive for a 1-to-4 week campaign-state thesis.

## V655A: Single Allowed Change Axis

Open a narrow mission:

- `V655A Soft-Mass Campaign Accumulation Audit`

Change only one axis:

- campaign accumulation candidates should no longer require `is_signal == 1`
- they should require only:
  - `is_physics_valid == 1`
  - plus the existing pulse floor
  - plus the existing same-sign pulse compression

In other words:

- keep the daily spine unchanged
- keep `entry_open_t1` unchanged
- keep `excess_ret_t1_to_Hd` unchanged
- keep triple-barrier semantics unchanged
- keep pulse compression unchanged
- keep `PsiE_*`, `PsiT_*`, `PsiStar_*` formulas unchanged
- keep the pure event-study gate unchanged
- keep ML / Vertex / holdout closed

## Why This Axis Is Correct

`is_signal` is an immediate trigger gate.

Campaign accumulation is a longer-horizon state-building task.

Early campaign buildup may remain:

- physics-valid
- low-entropy
- directionally coherent

without crossing the stricter row-level `is_signal` trigger on every contributing row.

Therefore the next truthful question is:

- if campaign-state accumulation is fed by the broader physics-valid pulse stream instead of only trigger-level peaks, does monotonic event-study structure emerge?

## V655A Success Criteria

All of the following must hold:

1. `raw_candidates` and `kept_pulses` rise materially above the V654 H1 baseline:
   - `raw_candidates = 3164`
   - `kept_pulses = 1449`
2. zero fraction remains:
   - `0.0`
3. `date_frac_flat_signal` remains near:
   - `0.0`
4. at least one tested `PsiE_*`, `PsiT_*`, or `PsiStar_*` signal returns:
   - `monotonic_non_decreasing = true`

## Contingent Fallback: V655B

Do not open this unless V655A fails.

If V655A still fails, the next allowed repair axis becomes:

- phase-amplitude daily fold

That means replacing sign-only directional folds such as:

- `F_epi = sum(E * sign(Phi))`
- `F_topo = sum(T * sign(Phi))`

with amplitude-aware folds such as:

- `F_epi_amp = sum(E * Phi)`
- `A_epi_amp = sum(E * |Phi|)`
- `F_topo_amp = sum(T * Phi)`
- `A_topo_amp = sum(T * |Phi|)`

V655B is not active in this authority.

It is only the next contingency if V655A fails under the unchanged gate.

## Barrier-Spread Interpretation Constraint

Current `barrier_win_rate` is defined as:

- `(barrier == 1).mean()`

This is not symmetric for signed directional families such as `Psi*`.

Therefore negative `barrier_win_spread_d10_minus_d1` must not override the primary block logic by itself.

Under the frozen gate, the primary blocking criterion remains:

- mean excess-return decile monotonicity

## Truth-First Escalation

If engineering translation requires it, later phases may modify:

- `tools/*`
- `omega_core/*`
- or re-run Stage2

but V655A wave 1 should remain as narrow as possible and should not expand scope unless the implementation is blocked.
