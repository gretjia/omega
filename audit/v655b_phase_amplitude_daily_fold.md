# V655B Phase-Amplitude Daily Fold

Status: Frozen external audit authority
Date: 2026-03-10
Scope: Post-V655A contingent fallback

## Central Judgment

V655A produced the required diagnostic separation.

It proved all of the following simultaneously:

- widening the campaign accumulation stream from hard trigger-level peaks to soft physics-valid pulse mass materially increases candidate flow
- the corrected daily spine and widened tradable labels still eliminate the old zero-mass defect
- the directional signal families remain non-flat
- the unchanged pure event-study gate still does not pass

Therefore the active blocker is no longer:

- the candidate-stream sparsity alone

The next truthful single axis is:

- phase-amplitude daily fold

## Frozen Facts From V655A

Evidence:

- `audit/v655a_h1_soft_mass_block_evidence.md`
- `audit/runtime/v655a_probe_linux_h1_2023_20260310_034020/campaign_matrix.parquet.meta.json`
- `audit/runtime/v655a_probe_linux_h1_2023_20260310_034020/event_study_v655a_psi_primary.json`

Frozen facts:

- `raw_candidates=136439`
- `kept_pulses=30449`
- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`
- `date_frac_flat_signal=0.0` for every tested primary `Psi` signal
- all tested `PsiE_*`, `PsiT_*`, and `PsiStar_*` returned:
  - `monotonic_non_decreasing = false`

## Exact Next Axis

Do not change:

- daily temporal spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier labels
- pure event-study decile gate
- soft-mass candidate stream from V655A
- same-sign pulse compression
- ML / Vertex / holdout boundaries

Change only:

- the daily fold from sign-only directional projection to phase-amplitude directional projection for the `E` and `T` channels

## Canonical Diagnosis

Current V654/V655A daily fold still uses:

- `F_epi = sum(E * sign(Phi))`
- `A_epi = sum(E)`
- `F_topo = sum(T * sign(Phi))`
- `A_topo = sum(T)`

This preserves direction but discards phase magnitude in the `E` and `T` channels.

The `Phi` channel itself keeps amplitude, but `E` and `T` are still projected through sign only.

That means the daily fold still answers:

- which way was the phase pointing

but not yet:

- how strongly was structure or topology being pushed along that phase

## Frozen Mathematical Upgrade

### 1. Keep The Soft-Mass Candidate Stream

Continue using the V655A accumulation stream:

- require `is_physics_valid == 1`
- do not require `is_signal == 1`
- require `abs(singularity_vector) > pulse_floor`
- keep same-sign pulse compression unchanged

### 2. Replace Sign-Only Daily Projection For `E` And `T`

For the compressed pulse set `P_{i,d}`:

- `F^E_amp_{i,d} = sum_{e in P_{i,d}} E_e * Phi_e`
- `A^E_amp_{i,d} = sum_{e in P_{i,d}} E_e * |Phi_e|`

- `F^T_amp_{i,d} = sum_{e in P_{i,d}} T_e * Phi_e`
- `A^T_amp_{i,d} = sum_{e in P_{i,d}} T_e * |Phi_e|`

Keep the phase channel unchanged:

- `F^Phi_{i,d} = sum_{e in P_{i,d}} Phi_e`
- `A^Phi_{i,d} = sum_{e in P_{i,d}} |Phi_e|`

### 3. Cross-Day Recursion Remains Unchanged In Form

For each half-life `tau in {5, 10, 20}` and each channel:

- keep EMA/IIR recursion shape unchanged
- keep coherence shape unchanged
- change only the underlying `F`/`A` inputs for the `E` and `T` channels to the amplitude-aware versions

### 4. Primary Directional Families For Event Study

Preserve the unchanged event-study gate.

Primary V655B directional families should be amplitude-aware and scoreable without parser breakage.

Preferred family names:

- `PsiAmpE_5d`
- `PsiAmpT_5d`
- `PsiAmpStar_5d`
- `PsiAmpE_10d`
- `PsiAmpT_10d`
- `PsiAmpStar_10d`
- `PsiAmpE_20d`
- `PsiAmpT_20d`
- `PsiAmpStar_20d`

These names are preferred because the existing event-study parser infers the horizon from the suffix after the first underscore.

`PsiAmpStar_*` must explicitly derive its own amplitude-aware coherence support:

- `OmegaAmpE_*`
- `OmegaAmpT_*`
- `OmegaAmpStar_*`

and `OmegaAmpStar_*` must be built from the amplitude-aware action denominators rather than from legacy sign-based coherence.

The master sign for `PsiAmpStar_*` remains:

- `sign(S_phase_*)`

to preserve the established three-channel identity.

Keep the older sign-based families as baselines and diagnostics:

- `PsiE_*`
- `PsiT_*`
- `PsiStar_*`

## V655B Success Criteria

All of the following must hold:

1. zero fractions remain:
   - `0.0`
2. signal families remain non-flat:
   - `date_frac_flat_signal` near `0.0`
3. at least one tested amplitude-aware primary signal returns:
   - `monotonic_non_decreasing = true`

## V655B Kill Condition

Kill V655B and keep ML closed if:

- the phase-amplitude daily fold is implemented cleanly
- the soft-mass candidate stream remains live
- zero fractions stay eliminated
- signal families remain non-flat
- but no tested amplitude-aware primary family passes the unchanged monotonic gate

That result would justify a deeper reformulation, but not ML reopening.
