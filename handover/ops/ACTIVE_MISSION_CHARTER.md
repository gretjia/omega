# OMEGA Active Mission Charter

Status: In Progress
Task Name: V655B Phase-Amplitude Daily Fold
Owner: Human Owner
Commander: Codex
Date: 2026-03-10

## 1. Objective

- Preserve the corrected V655A daily spine, tradable label stack, soft-mass candidate stream, same-sign pulse compression, and unchanged pure event-study gate.
- Repair only the daily fold for the `E` and `T` channels.
- Replace sign-only directional projection with phase-amplitude directional projection while leaving the rest of the campaign-state pipeline frozen.
- Re-run pure event study before any ML reopening.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v655b_phase_amplitude_daily_fold.md`
- `audit/v655a_h1_soft_mass_block_evidence.md`
- `audit/v655_soft_mass_campaign_accumulation.md`
- `audit/v654_identity_preserving_pulse_compression.md`
- `audit/v653_fractal_campaign_awakening.md`
- `audit/v653_identity_preservation_gemini_verdict.md`
- `handover/ai-direct/entries/20260310_045017_v655b_phase_amplitude_daily_fold_spec_draft.md`
- `handover/ai-direct/entries/20260310_045808_v655b_spec_gemini_pass.md`
- `handover/ai-direct/entries/20260310_045900_v655b_phase_amplitude_mission_open.md`

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
- changing the V655A soft-mass candidate stream
- changing `tools/run_campaign_event_study.py` gate semantics
- changing `omega_core/*` math core unless a later truth-first escalation is explicitly opened
- opening ML before a V655B amplitude-aware family earns the pure event-study gate

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
  - audit every formula-bearing diff against the frozen V655B override

Campaign Forge Engineer:

- responsibility:
  - implement the amplitude-aware fold without changing the daily spine, labels, candidate stream, or same-sign compression

Fold-Delta Auditor:

- responsibility:
  - verify the only mathematical delta is the `E` / `T` phase-amplitude fold

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

- V655B mission-open authority exists in handover
- the active charter explicitly freezes the V655B single-axis repair boundary
- forge implementation preserves:
  - daily spine
  - tradable return labels
  - triple-barrier semantics
  - event-study gate
  - V655A `E/T/Phi` identity
  - V655A soft-mass candidate stream
  - same-sign pulse compression
  - daily `F_epi/A_epi`, `F_topo/A_topo`, `F_phase/A_phase`
  - legacy `PsiE_*`, `PsiT_*`, `PsiStar_*`
  - `pulse_count`
  - `pulse_concentration`
  - amplitude-aware `PsiAmpE_*`, `PsiAmpT_*`, `PsiAmpStar_*`
- forge implementation changes only:
  - the daily fold for the `E` and `T` channels
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
- stop if V655B changes any axis beyond the `E` / `T` phase-amplitude daily fold

## 8. Audits Required

Math audit must verify:

- the single change axis is exactly the phase-amplitude daily fold for `E` / `T`
- event-level three-channel preservation remains intact
- the V655A soft-mass candidate stream remains intact
- pulse-compression semantics remain unchanged
- cross-day recursion semantics remain unchanged
- label and barrier semantics remain unchanged

Runtime audit must verify:

- stable intraday ordering
- daily zero-fill continuity
- zero-fraction stays `0.0`
- directional signal families are emitted and scoreable
- amplitude-aware signal families remain non-flat and scoreable under the unchanged gate

## 9. Definition of Done

- V655B mission is active in handover
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
