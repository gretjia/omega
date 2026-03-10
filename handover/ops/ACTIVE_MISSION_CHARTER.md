# OMEGA Active Mission Charter

Status: In Progress
Task Name: V655A Soft-Mass Campaign Accumulation Audit
Owner: Human Owner
Commander: Codex
Date: 2026-03-10

## 1. Objective

- Preserve the corrected V654 daily spine, tradable label stack, same-sign pulse compression, and unchanged pure event-study gate.
- Repair only the campaign accumulation candidate stream.
- Widen the candidate stream from hard `is_signal` gating to soft physics-valid gating.
- Re-run pure event study before any ML reopening.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v655_soft_mass_campaign_accumulation.md`
- `audit/v654_identity_preserving_pulse_compression.md`
- `audit/v653_fractal_campaign_awakening.md`
- `audit/v653_identity_preservation_gemini_verdict.md`
- `handover/ai-direct/entries/20260310_032850_v655a_soft_mass_campaign_accumulation_spec_draft.md`
- `handover/ai-direct/entries/20260310_033545_v655a_spec_gemini_pass.md`
- `handover/ai-direct/entries/20260310_033700_v655a_soft_mass_mission_open.md`

Supporting context:

- `OMEGA_CONSTITUTION.md`
- `omega_core/kernel.py`
- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py`
- `audit/v654_h1_psi_event_study_block_evidence.md`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/forge_campaign_state.py`
- `tests/test_campaign_state_contract.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`
- `audit/README.md`
- `audit/v655_*`

Read-only but relevant files:

- `tools/run_campaign_event_study.py`
- `omega_core/*`
- frozen V64 / V643 / V653 / V654 audit canon
- frozen V654 runtime evidence

Explicitly out of scope before the event-study gate passes:

- reopening Path A
- any Vertex / GCP launch
- any XGBoost tuning or ML sweep
- `2025` / `2026-01` holdout consumption
- changing the mathematical meaning of the frozen V654 daily spine / label / barrier semantics
- changing the same-sign pulse compression logic
- changing `PsiE_*`, `PsiT_*`, or `PsiStar_*` formulas
- changing `tools/run_campaign_event_study.py` gate semantics
- changing `omega_core/*` math core unless a later truth-first escalation is explicitly opened
- opening V655B before a separate explicit authority exists

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
  - audit every formula-bearing diff against the frozen V655A override

Campaign Forge Engineer:

- responsibility:
  - implement the soft-mass candidate-stream widening without changing the V654 fold

Candidate-Flow Auditor:

- responsibility:
  - compare `raw_candidates` and `kept_pulses` against the frozen V654 H1 baseline

Distribution Auditor:

- responsibility:
  - verify zero-fraction remains `0.0`
  - inspect pulse-count and pulse-concentration distributions
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
  - block all ML until a new directional family earns the pure event-study gate

## 5. Acceptance Criteria

- V655A mission-open authority exists in handover
- the active charter explicitly freezes the V655A single-axis repair boundary
- forge implementation preserves:
  - daily spine
  - tradable return labels
  - triple-barrier semantics
  - event-study gate
  - V654 `E/T/Phi` identity
  - same-sign pulse compression
  - daily `F_epi/A_epi`, `F_topo/A_topo`, `F_phase/A_phase`
  - `pulse_count`
  - `pulse_concentration`
  - `PsiE_*`, `PsiT_*`, `PsiStar_*`
- forge implementation changes only:
  - the live candidate-stream requirement for `is_signal`
- pure event study runs before any ML work
- no ML / cloud / holdout steps are opened before the event-study gate

## 6. Runtime Preflight

Required before execution:

- local-only phase ordering
- fresh isolated runtime roots for V655A outputs
- no cloud endpoints
- no holdout paths
- fail fast if no stable intraday ordering key exists

## 7. Fail-Fast Conditions

- stop if any step changes the mathematical meaning of the frozen formulas
- stop if any step opens ML before the event-study gate
- stop if any step consumes `2025` / `2026-01` holdouts early
- stop if a required formula-bearing diff has not been audited with `gemini -p`
- stop if the forge silently degrades to unordered or single-channel daily aggregation
- stop if V655A changes any axis beyond the `is_signal` candidate-stream requirement

## 8. Audits Required

Math audit must verify:

- the single change axis is exactly the soft-mass candidate stream
- event-level three-channel preservation remains intact
- pulse-compression semantics remain unchanged
- cross-day recursion semantics remain unchanged
- label and barrier semantics remain unchanged

Runtime audit must verify:

- stable intraday ordering
- daily zero-fill continuity
- zero-fraction stays `0.0`
- directional signal families are emitted and scoreable
- candidate mass rises relative to the frozen V654 H1 baseline

## 9. Definition of Done

- V655A mission is active in handover
- first forge code wave is implemented
- local tests pass
- first local forge / event-study probe is recorded
- a go / no-go verdict for ML reopening remains explicit
- handover updated
- Commander-only commit/push completed

## 10. Run Manifest

Record after execution:

- commit hash:
- nodes used:
- pulse mode:
- pulse min gap:
- require is signal:
- require is physics valid:
- output roots:
- math audit verdict:
- runtime audit verdict:
- event-study verdict:
