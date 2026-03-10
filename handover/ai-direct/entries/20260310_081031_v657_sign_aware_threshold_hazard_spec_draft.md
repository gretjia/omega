# V657 Spec Draft: Sign-Aware Threshold Hazard Audit

Status: Draft for Gemini math audit
Date: 2026-03-10 08:10 UTC
Mission candidate: V657 Sign-Aware Threshold Hazard Audit

## 1. Why This Mission Exists

V655B and V656 jointly falsified the current pre-ML evaluator as a sufficient gate for OMEGA campaign-state signals.

They showed:

- zero-mass is gone
- candidate mass is no longer sparse
- amplitude-aware state families are live
- transition families are live
- both families are non-flat

but:

- neither family behaves like a clean unconditional cross-sectional monotonic ranker

So the next truthful move is not:

- another forge rewrite
- another signal-family rewrite
- reopening ML

It is to change only the evaluator semantics.

## 2. Frozen Boundaries

The following stay frozen:

- the V64 / V643 / V653 / V654 / V655A / V655B / V656 mathematical canon
- the V655A soft-mass candidate stream
- the V655B amplitude-aware daily fold
- the V656 transition derivation formulas
- the daily temporal spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier semantics
- same-sign pulse compression
- `tools/forge_campaign_state.py`
- ML / Vertex / holdout closure
- `omega_core/*`
- Stage2 artifacts

## 3. Single Allowed Change Axis

Change only the pre-ML evaluator semantics.

Replace:

- unconditional date-neutral cross-sectional decile monotonic ranking

with:

- sign-aware one-sided threshold / hazard evaluation

No new signal family in wave 1.

## 4. Canonical Evaluation Families

Wave 1 is restricted to the existing V656 transition signals:

- `dPsiAmpE_10d`
- `dPsiAmpE_20d`
- `dPsiAmpStar_10d`
- `dPsiAmpStar_20d`
- `FreshAmpE_10d`
- `FreshAmpE_20d`
- `FreshAmpStar_10d`
- `FreshAmpStar_20d`

## 5. Canonical Threshold Semantics

For each signal, evaluate:

- positive side only
- negative side only

Threshold ladder:

- `90th`
- `95th`
- `97.5th`

### 5.1 Positive-Side Evaluation

- select rows whose signal lies in the positive upper tail for that date
- score with:
  - `excess_ret_t1_to_Hd`
  - positive hazard:
    - `barrier_Hd == 1`

### 5.2 Negative-Side Evaluation

- select rows whose signal lies in the negative lower tail for that date
- score with:
  - `-excess_ret_t1_to_Hd`
  - negative hazard:
    - `barrier_Hd == -1`

### 5.3 Aggregation

Keep date-neutral aggregation.

Do not reuse the decile-monotonic gate as the primary criterion for this mission.

The new question is:

- does edge improve as thresholds tighten on the relevant side?

## 6. Engineering Translation

### 6.1 Writable files

- `tools/run_campaign_sign_aware_threshold_audit.py`
- `tests/test_campaign_sign_aware_threshold_audit.py`
- handover and audit files for V657

### 6.2 Expected implementation delta

Create a lightweight evaluator-only tool:

- `tools/run_campaign_sign_aware_threshold_audit.py`

This tool must:

1. read the existing V655B campaign matrix
2. derive the existing V656 transition columns in-memory
3. evaluate one-sided tails for each signal and threshold
4. report signed excess-return and sign-aware hazard summaries

No forge rewrite is allowed.

No new signal family is allowed.

### 6.3 Required outputs

For each signal / horizon / side / threshold:

- `n_dates_scored`
- `n_rows_scored`
- signed mean excess return
- sign-aware hazard win rate
- threshold tightening comparison

## 7. AgentOS Team

Commander:

- owns scope, integration, git, and handover

Formula Integrity Auditor:

- engine:
  - `gemini -p`
- model rule:
  - default `gemini 3.1 pro preview` only
- responsibility:
  - audit every formula-bearing diff against:
    - `audit/v657_sign_aware_threshold_hazard_audit.md`
    - `audit/v656_h1_transition_event_study_block_evidence.md`

Threshold Evaluator Engineer:

- responsibility:
  - implement the sign-aware one-sided evaluator without changing forge or signals

Evaluator Reuse Auditor:

- responsibility:
  - verify frozen signal derivations remain unchanged
  - verify side handling and sign handling are correct

Distribution Auditor:

- responsibility:
  - verify tails are non-empty and date-neutral
  - verify threshold tightening comparisons are valid

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - enforce local-only / no-ML sequencing
  - use polling agents instead of watchdog/supervisor programs

ML Readiness Gatekeeper:

- responsibility:
  - refuse ML reopening unless a V657 signal-side-threshold pair passes the new one-sided threshold gate

## 8. Execution Order

### Phase 0

- land the new audit authority
- audit this spec with `gemini -p`

### Phase 1

- implement the evaluator-only tool
- run local tests

### Phase 2

- run bounded evaluator-only runtime on the frozen V655B campaign matrix

### Phase 3

- decide go / no-go for ML reopening

## 9. Runtime Shape

Wave 1 remains:

- local / cluster-local only
- no GCP
- no holdout
- no XGBoost
- no forge rerun

Preferred runtime basis:

- existing V655B H1 campaign matrix on `linux1-lx`

## 10. Success Criteria

V657 earns continuation only if:

1. at least one signal / side / horizon pair shows:
   - positive signed excess-return
   - positive sign-aware hazard edge
2. that pair improves as thresholds tighten

## 11. Kill Condition

Kill V657 and keep ML closed if:

- evaluator semantics are changed cleanly
- forge and signal derivations remain frozen
- but no signal-side-horizon pair shows a positive signed edge that strengthens as thresholds tighten

## 12. Definition of Done For This Draft Stage

This draft is ready for execution only when:

- the new audit authority is landed under `audit/`
- the single evaluator-only change axis is explicit
- the frozen boundaries are explicit
- `gemini -p` has audited the draft and any required fixes are folded in
