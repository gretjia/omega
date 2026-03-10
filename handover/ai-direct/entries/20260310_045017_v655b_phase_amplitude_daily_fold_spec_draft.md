# V655B Spec Draft: Phase-Amplitude Daily Fold

Status: Draft for Gemini math audit
Date: 2026-03-10 04:50 UTC
Mission candidate: V655B Phase-Amplitude Daily Fold

## 1. Why This Mission Exists

V655A answered the candidate-stream question directly.

It showed that widening the candidate stream:

- massively raises `raw_candidates`
- massively raises `kept_pulses`
- keeps zero fraction at `0.0`
- keeps the primary directional families non-flat

but still does not pass the unchanged monotonic event-study gate.

So the next truthful move is not:

- reopening ML
- changing labels
- changing the daily spine
- changing the event-study gate
- changing candidate-stream breadth again

It is to change only the daily fold so the `E` and `T` channels retain SRL phase amplitude rather than only phase sign.

## 2. Frozen Boundaries

The following stay frozen:

- the V64 / V643 / V653 / V654 / V655A mathematical canon
- the V655A soft-mass candidate stream
- the daily temporal spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier semantics
- same-sign pulse compression
- the pure event-study gate in `tools/run_campaign_event_study.py`
- ML / Vertex / holdout closure

Wave 1 also keeps frozen:

- `omega_core/*`
- Stage2 artifacts

## 3. Single Allowed Change Axis

Change only the daily fold for the `E` and `T` channels.

Current V655A fold:

- `F_epi = sum(E * sign(Phi))`
- `A_epi = sum(E)`
- `F_topo = sum(T * sign(Phi))`
- `A_topo = sum(T)`

V655B fold:

- `F_epi_amp = sum(E * Phi)`
- `A_epi_amp = sum(E * abs(Phi))`
- `F_topo_amp = sum(T * Phi)`
- `A_topo_amp = sum(T * abs(Phi))`

The phase channel remains unchanged:

- `F_phase = sum(Phi)`
- `A_phase = sum(abs(Phi))`

## 4. Canonical Rationale

The V655A soft-mass result suggests the blocker is no longer “not enough candidate flow.”

The remaining issue is that the current fold still lets the `E` and `T` channels know only:

- direction

but not:

- directional amplitude

The next truthful question is:

- if structure and topology are folded with phase amplitude rather than phase sign only, does monotonic directional event-study structure emerge?

## 5. Engineering Translation

### 5.1 Writable files

- `tools/forge_campaign_state.py`
- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`
- handover and audit files for V655B

### 5.2 Expected implementation delta

In `tools/forge_campaign_state.py`:

- keep `_collect_intraday_candidates_from_l2()`
- keep same-sign compression logic unchanged
- keep the V655A soft-mass candidate stream unchanged
- keep legacy sign-based daily fold outputs for comparison if feasible
- add amplitude-aware daily fold outputs for the `E` and `T` channels
- run the same EMA/IIR recursion shape over the amplitude-aware `E` and `T` channels

Preferred scoreable names:

- `PsiAmpE_*`
- `PsiAmpT_*`
- `PsiAmpStar_*`

These names are preferred because the current event-study parser can still infer `5d/10d/20d` from them.

`PsiAmpStar_*` must explicitly derive its own amplitude-aware coherence support:

- `OmegaAmpE_*`
- `OmegaAmpT_*`
- `OmegaAmpStar_*`

and `OmegaAmpStar_*` must be built from amplitude-aware action denominators rather than from legacy sign-based coherence.

The master sign for `PsiAmpStar_*` remains:

- `sign(S_phase_*)`

to preserve the established three-channel identity.

Legacy diagnostic preservation is mandatory:

- keep `PsiE_*`, `PsiT_*`, and `PsiStar_*` alongside the new amplitude-aware families so V655A vs V655B remains directly comparable.

### 5.3 Required observability

V655B runtime evidence must continue to record:

- `raw_candidates`
- `kept_pulses`
- zero fractions
- scored dates
- `date_frac_flat_signal`

## 6. AgentOS Team

Commander:

- owns scope, integration, git, and handover

Formula Integrity Auditor:

- engine:
  - `gemini -p`
- model rule:
  - default `gemini 3.1 pro preview` only
- responsibility:
  - audit every formula-bearing diff against:
    - `audit/v655b_phase_amplitude_daily_fold.md`
    - `audit/v655_soft_mass_campaign_accumulation.md`

Campaign Forge Engineer:

- responsibility:
  - implement the amplitude-aware fold without changing candidate stream, daily spine, labels, or gate

Fold-Delta Auditor:

- responsibility:
  - verify the only mathematical delta is the `E`/`T` phase-amplitude fold

Distribution Auditor:

- responsibility:
  - verify zero fractions remain `0.0`
  - verify signal families remain non-flat

Event Study Auditor:

- responsibility:
  - verify monotonicity under the unchanged gate

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - enforce local-only / no-ML sequencing
  - use polling agents instead of watchdog/supervisor programs

ML Readiness Gatekeeper:

- responsibility:
  - refuse ML reopening unless a V655B amplitude-aware family passes the unchanged pure event-study gate

## 7. Execution Order

### Phase 0

- land the new audit authority
- audit this spec with `gemini -p`

### Phase 1

- implement the amplitude-aware daily fold
- run local tests

### Phase 2

- deploy and run a bounded local/worker forge probe
- record:
  - `raw_candidates`
  - `kept_pulses`
  - zero fractions

### Phase 3

- run pure event study only on:
  - `PsiAmpE_*`
  - `PsiAmpT_*`
  - `PsiAmpStar_*`

### Phase 4

- decide go / no-go for ML reopening

## 8. Runtime Shape

Wave 1 remains:

- local / cluster-local only
- no GCP
- no holdout
- no XGBoost

Preferred first runtime target:

- `linux1-lx`

because V655A already established the immediate comparison baseline there.

## 9. Success Criteria

V655B earns continuation only if all of the following hold:

1. zero fractions remain:
   - `0.0`
2. `date_frac_flat_signal` stays near:
   - `0.0`
3. at least one `PsiAmpE_*`, `PsiAmpT_*`, or `PsiAmpStar_*` signal returns:
   - `monotonic_non_decreasing = true`

## 10. Kill Condition

Kill V655B and keep ML closed if:

- the amplitude-aware fold is implemented cleanly
- zero fractions stay eliminated
- signal families remain non-flat
- but no tested amplitude-aware primary family passes monotonicity under the unchanged gate

## 11. Definition of Done For This Draft Stage

This draft is ready for execution only when:

- the V655B audit authority is landed in `audit/`
- the spec is audited with `gemini -p`
- any required Gemini fixes are folded in
- the active charter is switched only after the math audit passes
