# OMEGA Active Mission Charter

Status: In Progress
Task Name: V657 Sign-Aware Threshold Hazard Audit
Owner: Human Owner
Commander: Codex
Date: 2026-03-10

## 1. Objective

- Preserve the corrected V655A soft-mass candidate stream, V655B amplitude-aware daily fold, V656 transition derivations, daily spine, tradable label stack, and same-sign pulse compression.
- Repair only the evaluator semantics.
- Replace unconditional cross-sectional decile monotonic ranking with sign-aware one-sided threshold / hazard evaluation while leaving forge and signal logic frozen.
- Run evaluator-only scoring before any ML reopening.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v657_sign_aware_threshold_hazard_audit.md`
- `audit/v656_h1_transition_event_study_block_evidence.md`
- `audit/v656_campaign_transition_entry_audit.md`
- `audit/v655b_h1_amp_event_study_block_evidence.md`
- `audit/v655b_phase_amplitude_daily_fold.md`
- `handover/ai-direct/entries/20260310_081031_v657_sign_aware_threshold_hazard_spec_draft.md`
- `handover/ai-direct/entries/20260310_081335_v657_spec_gemini_pass.md`
- `handover/ai-direct/entries/20260310_081400_v657_sign_aware_threshold_hazard_mission_open.md`

Supporting context:

- `OMEGA_CONSTITUTION.md`
- `tools/forge_campaign_state.py`
- `tools/run_campaign_transition_event_study.py`
- `tools/run_campaign_event_study.py`
- `tools/run_campaign_sign_aware_threshold_audit.py`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_campaign_sign_aware_threshold_audit.py`
- `tests/test_campaign_sign_aware_threshold_audit.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`
- `audit/README.md`
- `audit/v657_*`

Read-only but relevant files:

- `tools/run_campaign_event_study.py`
- `tools/run_campaign_transition_event_study.py`
- `tools/forge_campaign_state.py`
- `omega_core/*`
- frozen V64 / V643 / V653 / V654 / V655A / V655B / V656 audit canon
- frozen V655B / V656 runtime evidence

Explicitly out of scope before the sign-aware threshold gate passes:

- reopening Path A
- any Vertex / GCP launch
- any XGBoost tuning or ML sweep
- `2025` / `2026-01` holdout consumption
- changing the mathematical meaning of the frozen daily spine / label / barrier semantics
- changing the same-sign pulse compression logic
- changing the V655A soft-mass candidate stream
- changing the V655B amplitude-aware daily fold
- changing the V656 transition derivation formulas
- changing forge math
- changing `omega_core/*` math core unless a later truth-first escalation is explicitly opened
- opening ML before a V657 signal-side-threshold pair earns the one-sided threshold gate

## 4. Roles

Commander:

- define scope
- integrate code and docs
- own git / push / handover

Formula Integrity Auditor:

- engine:
  - `gemini -p`
- model rule:
  - default `gemini 3.1 pro preview` only
- responsibility:
  - audit every formula-bearing diff against the frozen V657 override

Threshold Evaluator Engineer:

- responsibility:
  - implement the sign-aware one-sided evaluator without changing forge or signals

Evaluator Reuse Auditor:

- responsibility:
  - verify the only mathematical delta is the evaluator semantics
  - verify the V656 transition derivations remain unchanged
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
  - refuse ML reopening unless a V657 signal-side-threshold pair passes the one-sided threshold gate

## 5. Acceptance Criteria

- V657 mission-open authority exists in handover
- the active charter explicitly freezes the V657 single-axis repair boundary
- implementation preserves:
  - daily spine
  - tradable return labels
  - triple-barrier semantics
  - V655A soft-mass candidate stream
  - V655B amplitude-aware daily fold
  - V656 transition derivations
- implementation changes only:
  - the evaluator semantics
- sign-aware threshold audit runs before any ML work
- no ML / cloud / holdout steps are opened before the sign-aware threshold gate

## 6. Runtime Preflight

Required before execution:

- local-only phase ordering
- fresh isolated V657 output path under the existing V655B runtime authority
- no cloud endpoints
- no holdout paths
- no forge rerun
- no signal rewrite

## 7. Fail-Fast Conditions

- stop if any step changes the mathematical meaning of the frozen formulas
- stop if any step opens ML before the threshold gate
- stop if any step consumes `2025` / `2026-01` holdouts early
- stop if a required formula-bearing diff has not been audited with `gemini -p`
- stop if V657 rewrites forge math or signal derivation math
- stop if V657 changes any axis beyond the evaluator semantics

## 8. Audits Required

Math audit must verify:

- the single change axis is exactly the evaluator semantics
- V655B amplitude-aware level families remain intact
- the V656 transition derivations remain intact
- the V655A soft-mass candidate stream remains intact
- no forge rewrite occurs
- label and barrier semantics remain unchanged

Runtime audit must verify:

- sign-aware tails are emitted and scoreable
- threshold ladder summaries are emitted
- positive and negative sides are evaluated with the correct signed scoring
- threshold tightening comparisons are present

## 9. Definition of Done

- V657 mission is active in handover
- first threshold-audit code wave is implemented
- local tests pass
- first bounded sign-aware threshold audit is recorded
- a go / no-go verdict for ML reopening remains explicit
- handover updated
- Commander-only commit/push completed

## 10. Run Manifest

Record after execution:

- commit hash:
- nodes used:
- output roots:
- math audit verdict:
- runtime audit verdict:
- threshold-audit verdict:
