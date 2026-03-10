# V656 Spec Draft: Campaign-Transition Entry Audit

Status: Draft for Gemini math audit
Date: 2026-03-10 06:42 UTC
Mission candidate: V656 Campaign-Transition Entry Audit

## 1. Why This Mission Exists

V655B resolved the remaining low-level engineering ambiguity.

It showed that:

- daily spine is live
- widened tradable labels are live
- zero-mass is gone
- candidate stream is no longer sparse
- amplitude-aware daily fold is live
- the primary amplitude-aware families are non-flat

but:

- the unchanged monotonic event-study gate still does not pass

So the next truthful move is not:

- reopening ML
- changing labels
- changing the daily spine
- changing pulse compression
- changing candidate-stream breadth again
- changing daily-fold formulas again

It is to change only the signal semantics from level to transition.

## 2. Frozen Boundaries

The following stay frozen:

- the V64 / V643 / V653 / V654 / V655A / V655B mathematical canon
- the V655A soft-mass candidate stream
- the V655B amplitude-aware daily fold
- the daily temporal spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier semantics
- same-sign pulse compression
- the pure event-study gate in `tools/run_campaign_event_study.py`
- ML / Vertex / holdout closure
- `omega_core/*`
- Stage2 artifacts
- `tools/forge_campaign_state.py`

## 3. Single Allowed Change Axis

Change only the semantics of the scored signal by deriving transition columns from the existing V655B campaign matrix.

Do not change forge math.

Do not change gate math.

## 4. Canonical Transition Families

Wave 1 is restricted to:

- horizons:
  - `10d`
  - `20d`
- bases:
  - `PsiAmpE`
  - `PsiAmpStar`
  - `OmegaAmpE`
  - `OmegaAmpStar`

### 4.1 Velocity Signals

For each symbol and date:

- `dPsiAmpE_10d = PsiAmpE_10d - shift(PsiAmpE_10d, 1)`
- `dPsiAmpE_20d = PsiAmpE_20d - shift(PsiAmpE_20d, 1)`
- `dPsiAmpStar_10d = PsiAmpStar_10d - shift(PsiAmpStar_10d, 1)`
- `dPsiAmpStar_20d = PsiAmpStar_20d - shift(PsiAmpStar_20d, 1)`

### 4.2 Fresh-Entry Signals

For each symbol and date:

- `FreshAmpE_tau`
  - `= sign(PsiAmpE_tau)`
  - `* max(0, abs(PsiAmpE_tau) - abs(prev(PsiAmpE_tau)))`
  - `* max(0, OmegaAmpE_tau - prev(OmegaAmpE_tau))`

- `FreshAmpStar_tau`
  - `= sign(PsiAmpStar_tau)`
  - `* max(0, abs(PsiAmpStar_tau) - abs(prev(PsiAmpStar_tau)))`
  - `* max(0, OmegaAmpStar_tau - prev(OmegaAmpStar_tau))`

Restricted scoreable names:

- `dPsiAmpE_10d`
- `dPsiAmpE_20d`
- `dPsiAmpStar_10d`
- `dPsiAmpStar_20d`
- `FreshAmpE_10d`
- `FreshAmpE_20d`
- `FreshAmpStar_10d`
- `FreshAmpStar_20d`

## 5. Engineering Translation

### 5.1 Writable files

- `tools/run_campaign_transition_event_study.py`
- `tests/test_campaign_transition_event_study.py`
- handover and audit files for V656

### 5.2 Expected implementation delta

Create a lightweight tool:

- `tools/run_campaign_transition_event_study.py`

This tool must:

1. read the existing campaign matrix parquet
2. sort by:
   - `symbol`
   - `pure_date`
3. derive the eight transition columns in-memory
4. reuse the unchanged event-study computation from:
   - `tools/run_campaign_event_study.py`

No forge rewrite is allowed.

No gate rewrite is allowed.

### 5.3 Naming rule

The derived signal names must keep the current parser contract intact:

- the text after the first underscore must still be:
  - `10d`
  - `20d`

So names like:

- `dPsiAmpStar_10d`
- `FreshAmpStar_20d`

are allowed and should remain parser-compatible.

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
    - `audit/v656_campaign_transition_entry_audit.md`
    - `audit/v655b_h1_amp_event_study_block_evidence.md`

Transition Semantics Engineer:

- responsibility:
  - implement the transition derivations without changing forge or gate

Gate Reuse Auditor:

- responsibility:
  - verify the event-study gate remains unchanged
  - verify parser compatibility for the eight new signal names

Distribution Auditor:

- responsibility:
  - verify transition families remain non-flat
  - verify symbol-boundary-safe lagging

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - enforce local-only / no-ML sequencing
  - use polling agents instead of watchdog/supervisor programs

ML Readiness Gatekeeper:

- responsibility:
  - refuse ML reopening unless a V656 transition family passes the unchanged pure event-study gate

## 7. Execution Order

### Phase 0

- land the new audit authority
- audit this spec with `gemini -p`

### Phase 1

- implement the lightweight transition-event-study tool
- run local tests

### Phase 2

- run bounded local/cluster-local event study against the frozen V655B campaign matrix

### Phase 3

- decide go / no-go for ML reopening

## 8. Runtime Shape

Wave 1 remains:

- local / cluster-local only
- no GCP
- no holdout
- no XGBoost
- no forge rerun

Preferred first runtime target:

- existing V655B H1 runtime root on `linux1-lx`

## 9. Success Criteria

V656 earns continuation only if all of the following hold:

1. transition signals remain non-flat:
   - `date_frac_flat_signal` near `0.0`
2. at least one `dPsiAmp*` or `FreshAmp*` signal returns:
   - `monotonic_non_decreasing = true`
3. that same signal also returns:
   - `d10_minus_d1 > 0`

## 10. Kill Condition

Kill V656 and keep ML closed if:

- transition semantics are implemented cleanly
- forge and gate remain frozen
- transition families remain non-flat
- but all eight tested transition families still fail monotonicity under the unchanged gate

## 11. Definition of Done For This Draft Stage

This draft is ready for execution only when:

- the new audit authority is landed under `audit/`
- the single change axis is explicit
- the frozen boundaries are explicit
- `gemini -p` has audited the draft and any required fixes are folded in
