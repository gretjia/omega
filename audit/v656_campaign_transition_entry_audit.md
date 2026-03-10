# V656 Campaign-Transition Entry Audit

Status: Frozen external audit authority
Date: 2026-03-10
Scope: Post-V655B contingent upgrade

## Central Judgment

The V655B block is correct.

V655B proved all of the following simultaneously:

- the daily spine repair remains intact
- the widened tradable label contract remains intact
- the zero-mass defect remains eliminated
- the candidate stream is no longer sparse
- the amplitude-aware fold is live on real data
- the primary amplitude-aware signal families remain non-flat
- the unchanged pure event-study gate still does not pass

Therefore the active blocker is no longer:

- label construction
- daily spine continuity
- candidate-stream sparsity
- phase-amplitude daily fold

The next truthful single axis is:

- signal semantics
- specifically:
  - campaign-state transition
  - rather than campaign-state level

## Frozen Facts From V655B

Evidence:

- `audit/v655b_h1_amp_event_study_block_evidence.md`
- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet.meta.json`
- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/event_study_v655b_amp_primary.json`

Frozen facts:

- `rows=271447`
- `symbols=5448`
- `raw_candidates=136439`
- `kept_pulses=30449`
- all three widened excess-return zero fractions remain:
  - `0.0`
- all tested primary amplitude-aware signals remain non-flat:
  - `date_frac_flat_signal=0.0`
- all tested `PsiAmpE_*`, `PsiAmpT_*`, and `PsiAmpStar_*` still returned:
  - `monotonic_non_decreasing = false`

## Canonical Diagnosis

The current event study is still scoring level signals:

- `PsiAmp*`
- `OmegaAmp*`

These are EMA/IIR state variables.

High state levels do not necessarily represent:

- fresh campaign formation

They may mix:

- early campaign build
- mid-campaign continuation
- late crowded or exhausted states

For a `1-4` week campaign thesis, the more truthful object is:

- transition
- acceleration
- fresh coherent entry

rather than:

- raw state level

## Exact Next Axis

Do not change:

- `tools/forge_campaign_state.py`
- daily temporal spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier labels
- same-sign pulse compression
- the V655A soft-mass candidate stream
- the V655B amplitude-aware daily fold
- the pure event-study gate
- ML / Vertex / holdout boundaries

Change only:

- derive transition semantics from the already-forged V655B campaign matrix
- score those transition signals under the unchanged event-study gate

## Frozen Mathematical Upgrade

Restrict wave 1 to horizons:

- `10d`
- `20d`

Do not open `5d` in wave 1.

### 1. Velocity Signals

For `X in {AmpE, AmpStar}` and `tau in {10, 20}`:

- `dPsi^X_tau(t) = Psi^X_tau(t) - Psi^X_tau(t-1)`

Preferred scoreable names:

- `dPsiAmpE_10d`
- `dPsiAmpE_20d`
- `dPsiAmpStar_10d`
- `dPsiAmpStar_20d`

### 2. Fresh-Entry Signals

For `X in {AmpE, AmpStar}` and `tau in {10, 20}`:

- `Fresh^X_tau(t) = sign(Psi^X_tau(t))`
  `* max(0, |Psi^X_tau(t)| - |Psi^X_tau(t-1)|)`
  `* max(0, Omega^X_tau(t) - Omega^X_tau(t-1))`

Preferred scoreable names:

- `FreshAmpE_10d`
- `FreshAmpE_20d`
- `FreshAmpStar_10d`
- `FreshAmpStar_20d`

### 3. Barrier Interpretation

Keep the existing barrier outputs unchanged.

`barrier_win_spread_d10_minus_d1` remains:

- diagnostic
- secondary

It is not the reopening gate.

## V656 Success Criteria

All of the following must hold:

1. no forge rewrite is required
2. no gate rewrite is required
3. transition signals remain non-flat:
   - `date_frac_flat_signal` near `0.0`
4. at least one tested transition family returns:
   - `monotonic_non_decreasing = true`
5. that same family also returns:
   - `d10_minus_d1 > 0`

## V656 Kill Condition

Kill V656 and keep ML closed if:

- transition semantics are derived cleanly from the existing V655B campaign matrix
- the unchanged event-study gate is preserved
- the transition families remain non-flat
- but all eight tested transition families still return:
  - `monotonic_non_decreasing = false`

That result would justify a deeper reframing of the scoring target, but not ML reopening.
