# OMEGA Active Mission Charter

Status: In Progress
Task Name: V656 Campaign-Transition Entry Audit
Owner: Human Owner
Commander: Codex
Date: 2026-03-10

## 1. Objective

- Preserve the corrected V655A soft-mass candidate stream, V655B amplitude-aware daily fold, daily spine, tradable label stack, same-sign pulse compression, and unchanged pure event-study gate.
- Repair only the scored signal semantics.
- Replace campaign-state level scoring with campaign-state transition scoring while leaving forge and gate logic frozen.
- Re-run pure event study before any ML reopening.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v656_campaign_transition_entry_audit.md`
- `audit/v655b_h1_amp_event_study_block_evidence.md`
- `audit/v655b_phase_amplitude_daily_fold.md`
- `audit/v655a_h1_soft_mass_block_evidence.md`
- `audit/v655_soft_mass_campaign_accumulation.md`
- `audit/v654_identity_preserving_pulse_compression.md`
- `audit/v653_fractal_campaign_awakening.md`
- `audit/v653_identity_preservation_gemini_verdict.md`
- `handover/ai-direct/entries/20260310_064256_v656_campaign_transition_entry_spec_draft.md`
- `handover/ai-direct/entries/20260310_064500_v656_spec_gemini_pass.md`
- `handover/ai-direct/entries/20260310_064600_v656_campaign_transition_mission_open.md`

Supporting context:

- `OMEGA_CONSTITUTION.md`
- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py`
- `tools/run_campaign_transition_event_study.py`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_campaign_transition_event_study.py`
- `tests/test_campaign_transition_event_study.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`
- `audit/README.md`
- `audit/v655_*`

Read-only but relevant files:

- `tools/run_campaign_event_study.py`
- `tools/forge_campaign_state.py`
- `omega_core/*`
- frozen V64 / V643 / V653 / V654 / V655A / V655B audit canon
- frozen V655B runtime evidence

Explicitly out of scope before the event-study gate passes:

- reopening Path A
- any Vertex / GCP launch
- any XGBoost tuning or ML sweep
- `2025` / `2026-01` holdout consumption
- changing the mathematical meaning of the frozen daily spine / label / barrier semantics
- changing the same-sign pulse compression logic
- changing the V655A soft-mass candidate stream
- changing the V655B amplitude-aware daily fold
- changing `tools/run_campaign_event_study.py` gate semantics
- changing `omega_core/*` math core unless a later truth-first escalation is explicitly opened
- opening ML before a V656 transition family earns the pure event-study gate

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
  - audit every formula-bearing diff against the frozen V656 override

Transition Semantics Engineer:

- responsibility:
  - implement the transition derivations without changing forge or gate

Gate Reuse Auditor:

- responsibility:
  - verify the only mathematical delta is the level-to-transition semantic shift
  - verify the event-study gate remains unchanged
  - verify parser compatibility for the eight new signal names

Distribution Auditor:

- responsibility:
  - verify transition families remain non-flat
  - verify symbol-boundary-safe lagging

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
  - block all ML until a new directional family earns the pure event-study gate

## 5. Acceptance Criteria

- V656 mission-open authority exists in handover
- the active charter explicitly freezes the V656 single-axis repair boundary
- implementation preserves:
  - daily spine
  - tradable return labels
  - triple-barrier semantics
  - event-study gate
  - V655A soft-mass candidate stream
  - V655B amplitude-aware daily fold
  - same-sign pulse compression
  - existing `PsiAmpE_*`, `PsiAmpStar_*`, `OmegaAmpE_*`, `OmegaAmpStar_*`
- implementation changes only:
  - the scored signal semantics derived from existing V655B level columns
- pure event study runs before any ML work
- no ML / cloud / holdout steps are opened before the event-study gate

## 6. Runtime Preflight

Required before execution:

- local-only phase ordering
- fresh isolated V656 output path under the existing V655B runtime authority
- no cloud endpoints
- no holdout paths
- no forge rerun

## 7. Fail-Fast Conditions

- stop if any step changes the mathematical meaning of the frozen formulas
- stop if any step opens ML before the event-study gate
- stop if any step consumes `2025` / `2026-01` holdouts early
- stop if a required formula-bearing diff has not been audited with `gemini -p`
- stop if V656 rewrites forge math or gate math
- stop if V656 changes any axis beyond the level-to-transition semantic shift

## 8. Audits Required

Math audit must verify:

- the single change axis is exactly the level-to-transition semantic shift
- V655B amplitude-aware level families remain intact
- the V655A soft-mass candidate stream remains intact
- no forge rewrite occurs
- no gate rewrite occurs
- label and barrier semantics remain unchanged

Runtime audit must verify:

- transition families are emitted and scoreable
- transition families remain non-flat and scoreable under the unchanged gate
- symbol-boundary-safe lagging is preserved

## 9. Definition of Done

- V656 mission is active in handover
- first transition-tool code wave is implemented
- local tests pass
- first bounded transition event-study probe is recorded
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
- event-study verdict:
