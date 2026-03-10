# OMEGA Active Mission Charter

Status: Blocked
Task Name: V658 Negative-Tail Hazard Admission Probe
Owner: Human Owner
Commander: Codex
Date: 2026-03-10

## 1. Objective

- Preserve the corrected V655A soft-mass candidate stream, V655B amplitude-aware daily fold, V656 transition derivations, daily spine, tradable label stack, and same-sign pulse compression.
- Repair only the admission protocol.
- Replace raw threshold trigger-only usage with a trigger-conditioned hazard learner while leaving forge, thresholds, and signal logic frozen.
- Run a narrow local-only ML-admission probe before any broader ML reopening.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v658_negative_tail_hazard_admission_probe.md`
- `audit/v657_h1_sign_aware_threshold_pass_evidence.md`
- `audit/v657_sign_aware_threshold_hazard_audit.md`
- `audit/v656_h1_transition_event_study_block_evidence.md`
- `handover/ai-direct/entries/20260310_084200_v658_negative_tail_hazard_admission_probe_spec_draft.md`
- `handover/ai-direct/entries/20260310_092918_v658_spec_gemini_pass.md`
- `handover/ai-direct/entries/20260310_093000_v658_negative_tail_hazard_admission_mission_open.md`

Supporting context:

- `OMEGA_CONSTITUTION.md`
- `tools/forge_campaign_state.py`
- `tools/run_campaign_transition_event_study.py`
- `tools/run_campaign_sign_aware_threshold_audit.py`
- `tools/run_campaign_ml_admission_probe.py`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_campaign_ml_admission_probe.py`
- `tests/test_campaign_ml_admission_probe.py`
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
- `tools/run_campaign_sign_aware_threshold_audit.py`
- `tools/forge_campaign_state.py`
- `omega_core/*`
- frozen V64 / V643 / V653 / V654 / V655A / V655B / V656 / V657 audit canon
- frozen V655B / V656 / V657 runtime evidence

Explicitly out of scope before the admission probe passes:

- reopening Path A
- any Vertex / GCP launch
- any Optuna or hyperparameter sweep
- `2025` / `2026-01` holdout consumption
- changing the mathematical meaning of the frozen daily spine / label / barrier semantics
- changing the same-sign pulse compression logic
- changing the V655A soft-mass candidate stream
- changing the V655B amplitude-aware daily fold
- changing the V656 transition derivation formulas
- changing the V657 threshold semantics
- changing forge math
- changing `omega_core/*` math core unless a later truth-first escalation is explicitly opened
- opening broader ML before V658 beats both constant-baseline logloss and raw same-count baseline economics

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
  - audit every formula-bearing diff against the frozen V658 override

Admission Probe Engineer:

- responsibility:
  - implement the fixed admitted-set learner without changing forge or signals

Leakage Auditor:

- responsibility:
  - verify admitted-set-only training
  - verify chronological forward folds
  - verify raw same-count baseline is computed inside the admitted set only

Distribution Auditor:

- responsibility:
  - verify admission-mask coverage
  - verify fold coverage and label balance
  - verify model-vs-raw selection comparisons are valid

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - enforce local-only / no-cloud / no-holdout sequencing
  - use polling agents instead of watchdog/supervisor programs

ML Readiness Gatekeeper:

- responsibility:
  - refuse any broader ML reopening unless V658 passes the narrow admission probe

## 5. Acceptance Criteria

- V658 mission-open authority exists in handover
- the active charter explicitly freezes the V658 single-axis repair boundary
- implementation preserves:
  - daily spine
  - tradable return labels
  - triple-barrier semantics
  - V655A soft-mass candidate stream
  - V655B amplitude-aware daily fold
  - V656 transition derivations
  - V657 threshold semantics
- implementation changes only:
  - the admission protocol
- admitted-set learner runs before any broader ML work
- no cloud / holdout steps are opened before the admission probe passes

## 6. Runtime Preflight

Required before execution:

- local-only phase ordering
- fresh isolated V658 output path under the existing V655B runtime authority
- no cloud endpoints
- no holdout paths
- no forge rerun
- no signal rewrite
- fixed learner only
- two forward folds only

## 7. Fail-Fast Conditions

- stop if any step changes the mathematical meaning of the frozen formulas
- stop if any step opens broader ML before the admission gate
- stop if any step consumes `2025` / `2026-01` holdouts early
- stop if a required formula-bearing diff has not been audited with `gemini -p`
- stop if V658 rewrites forge math or signal derivation math
- stop if V658 searches over signal family, side, horizon, or threshold
- stop if V658 changes any axis beyond the admission protocol

## 8. Audits Required

Math audit must verify:

- the single change axis is exactly the admission protocol
- V655B amplitude-aware level families remain intact
- the V656 transition derivations remain intact
- the V655A soft-mass candidate stream remains intact
- the V657 threshold semantics remain intact
- no forge rewrite occurs
- label and barrier semantics remain unchanged

Runtime audit must verify:

- the admitted set is built only from the fixed V657 contract:
  - `dPsiAmpE_10d`
  - `negative`
  - `90th` threshold
- training uses admitted rows only
- folds are chronological
- model-vs-raw same-count comparisons are emitted
- constant-baseline logloss comparison is emitted

## 9. Definition of Done

- V658 mission is active in handover
- first admission-probe code wave is implemented
- local tests pass
- first bounded admission probe is recorded
- a go / no-go verdict for broader ML reopening remains explicit
- handover updated
- Commander-only commit/push completed

## 10. Run Manifest

Record after execution:

- commit hash:
  - `6603e72`
- nodes used:
  - `controller`
  - `linux1-lx`
- output roots:
  - `audit/runtime/v658_ml_admission_probe_h1_2023_20260310_094420`
- math audit verdict:
  - `PASS`
- runtime audit verdict:
  - `BLOCK`
- admission-probe verdict:
  - `mission_pass=false`
