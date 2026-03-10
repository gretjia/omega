# V655A Spec Draft: Soft-Mass Campaign Accumulation Audit

Status: Draft for Gemini math audit
Date: 2026-03-10 03:28 UTC
Mission candidate: V655A Soft-Mass Campaign Accumulation Audit

## 1. Why This Mission Exists

V654 proved three important facts:

1. the daily spine and widened tradable label contract eliminated the old mechanical zero-mass defect
2. the new `Psi` families are not flat
3. the unchanged pure event-study gate still blocks ML reopening

So the next truthful move is not:

- reopening ML
- changing labels
- changing the daily spine
- changing the event-study gate

It is to widen only the campaign accumulation candidate stream while preserving the V654 identity-preserving fold.

## 2. Frozen Boundaries

The following stay frozen:

- the V64 / V643 / V653 / V654 mathematical canon
- the daily temporal spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier semantics
- same-sign pulse compression
- `PsiE_*`, `PsiT_*`, `PsiStar_*` formulas
- the pure event-study gate in `tools/run_campaign_event_study.py`
- ML / Vertex / holdout closure

Wave 1 also keeps frozen:

- sign-based daily channel folds
- `omega_core/*`
- Stage2 artifacts

Those may only be revisited later if V655A is blocked by implementation truth, or if V655A fails and V655B is explicitly opened.

## 3. Single Allowed Change Axis

Change only the campaign accumulation candidate filter.

Current V654 candidate rule effectively requires:

- `is_physics_valid == 1`
- `is_signal == 1`
- `abs(singularity_vector) > pulse_floor`

V655A changes this to:

- `is_physics_valid == 1`
- `abs(singularity_vector) > pulse_floor`

and explicitly stops requiring:

- `is_signal == 1`

This is a soft-mass candidate stream, not a trigger-only peak stream.

## 4. Canonical Rationale

`is_signal` is a row-level tactical trigger.

Campaign accumulation is a slower state-building process.

Therefore the accumulation stream should admit physics-valid low-entropy pressure that may remain below the stricter trigger threshold during early campaign buildup.

The mission question is:

- does the broader physics-valid candidate stream allow the same V654 fold to produce monotonic directional event-study structure?

## 5. Engineering Translation

### 5.1 Writable files

- `tools/forge_campaign_state.py`
- `tests/test_campaign_state_contract.py`
- handover and audit files for V655A

### 5.2 Expected implementation delta

In `tools/forge_campaign_state.py`:

- keep `_collect_intraday_candidates_from_l2()`
- keep same-sign compression logic unchanged
- keep channel identities unchanged
- keep daily fold formulas unchanged
- keep cross-day recursion unchanged
- change the live forge invocation defaults so V655A accumulation no longer requires `is_signal`

Wave-1 preferred contract:

- `require_is_signal = 0`
- `require_is_physics_valid = 1`

Implementation should preserve CLI control so the old stricter mode remains available for comparison.

### 5.3 Required observability

V655A runtime evidence must continue to record:

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
    - `audit/v655_soft_mass_campaign_accumulation.md`
    - `audit/v654_identity_preserving_pulse_compression.md`

Campaign Forge Engineer:

- responsibility:
  - implement the soft-mass candidate-stream change without touching pulse compression or recursion semantics

Candidate-Flow Auditor:

- responsibility:
  - compare `raw_candidates` and `kept_pulses` against the frozen V654 baseline

Distribution Auditor:

- responsibility:
  - verify zero-fraction remains `0.0`
  - verify signal families remain non-flat

Event Study Auditor:

- responsibility:
  - verify monotonicity under the unchanged gate

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - enforce no-ML sequencing
  - use polling agents instead of watchdog/supervisor programs

ML Readiness Gatekeeper:

- responsibility:
  - refuse ML reopening unless V655A passes the unchanged pure event-study gate

## 7. Execution Order

### Phase 0

- land the new audit authority
- audit this spec with `gemini -p`

### Phase 1

- implement the candidate-stream widening
- run local tests

### Phase 2

- run a bounded local/worker forge probe
- record:
  - `raw_candidates`
  - `kept_pulses`
  - zero fractions

### Phase 3

- run pure event study only on:
  - `PsiE_*`
  - `PsiT_*`
  - `PsiStar_*`

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

because the V654 H1 forge is already there and gives the correct comparison baseline.

## 9. Success Criteria

V655A earns continuation only if all of the following hold:

1. `raw_candidates` and `kept_pulses` rise materially above the frozen V654 H1 baseline:
   - `raw_candidates = 3164`
   - `kept_pulses = 1449`
2. zero fractions remain:
   - `0.0`
3. `date_frac_flat_signal` stays near:
   - `0.0`
4. at least one `PsiE_*`, `PsiT_*`, or `PsiStar_*` signal returns:
   - `monotonic_non_decreasing = true`

## 10. Kill Condition

Kill V655A and keep ML closed if:

- the widened candidate stream materially increases pulse mass
- but no tested `Psi` family passes monotonicity under the unchanged gate

That result would justify opening:

- `V655B Phase-Amplitude Daily Fold`

but only after a separate explicit authority and spec audit.

## 11. Definition of Done For This Draft Stage

This draft is ready for execution only when:

- the V655A audit authority is landed in `audit/`
- the spec is audited with `gemini -p`
- any required Gemini fixes are folded in
- the active charter is switched only after the math audit passes
