# OMEGA Active Mission Charter

Status: In Progress
Task Name: V654 Identity-Preserving Pulse Compression
Owner: Human Owner
Commander: Codex
Date: 2026-03-10

## 1. Objective

- Preserve the corrected V653 daily spine and tradable label stack.
- Repair only the `Intraday -> Symbol-Day` aggregation math.
- Keep Epiplexity, Topology, and SRL phase explicit through the daily fold.
- Re-run pure event study before any ML reopening.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v654_identity_preserving_pulse_compression.md`
- `audit/v653_fractal_campaign_awakening.md`
- `audit/v653_identity_preservation_gemini_verdict.md`
- `handover/ai-direct/entries/20260310_012744_v654_identity_preserving_pulse_compression_spec_draft.md`
- `handover/ai-direct/entries/20260310_013420_v654_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260310_013500_v654_identity_preserving_pulse_compression_mission_open.md`

Supporting context:

- `OMEGA_CONSTITUTION.md`
- `omega_core/kernel.py`
- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py`
- `audit/v653_h1_event_study_block_evidence.md`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py` only for signal-list compatibility or parser-safe extensions
- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`
- `audit/README.md`
- `audit/v654_*`

Read-only but relevant files:

- `omega_core/*`
- frozen V64 / V643 / V653 audit canon
- current V653 runtime evidence

Explicitly out of scope before the event-study gate passes:

- reopening Path A
- any Vertex / GCP launch
- any XGBoost tuning or ML sweep
- `2025` / `2026-01` holdout consumption
- changing the mathematical meaning of the frozen V653 daily spine / label / barrier semantics
- changing `omega_core/*` math core unless a later truth-first escalation is explicitly opened

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
  - audit every formula-bearing diff against the frozen V654 override

Campaign Forge Engineer:

- responsibility:
  - implement pulse compression and multi-channel daily aggregation

Data Contract Auditor:

- responsibility:
  - verify required L2 fields exist
  - verify stable intraday ordering exists
  - verify no hidden schema regressions

Distribution Auditor:

- responsibility:
  - verify zero-fraction remains `0.0`
  - inspect pulse-count and pulse-concentration distributions

Event Study Auditor:

- responsibility:
  - verify monotonicity, spread, and barrier asymmetry under the unchanged gate

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - enforce local-only / no-ML sequencing

ML Readiness Gatekeeper:

- responsibility:
  - block all ML until a new directional family earns the pure event-study gate

## 5. Acceptance Criteria

- V654 mission-open authority exists in handover
- the active charter explicitly freezes the V654 single-axis repair boundary
- forge implementation preserves:
  - daily spine
  - tradable return labels
  - triple-barrier semantics
  - event-study gate
- forge implementation adds:
  - event-level `E/T/Phi`
  - same-sign pulse compression
  - daily `F_epi/A_epi`, `F_topo/A_topo`, `F_phase/A_phase`
  - `pulse_count`
  - `pulse_concentration`
  - `PsiE_*`, `PsiT_*`, `PsiStar_*`
- pure event study runs before any ML work
- no ML / cloud / holdout steps are opened before the event-study gate

## 6. Runtime Preflight

Required before execution:

- local-only phase ordering
- fresh isolated runtime roots for V654 outputs
- no cloud endpoints
- no holdout paths
- fail fast if no stable intraday ordering key exists

## 7. Fail-Fast Conditions

- stop if any step changes the mathematical meaning of the frozen formulas
- stop if any step opens ML before the event-study gate
- stop if any step consumes `2025` / `2026-01` holdouts early
- stop if a required formula-bearing diff has not been audited with `gemini -p`
- stop if the forge silently degrades to unordered or single-channel daily aggregation

## 8. Audits Required

Math audit must verify:

- event-level three-channel preservation
- pulse-compression semantics
- cross-day recursion semantics
- label and barrier semantics remain unchanged

Runtime audit must verify:

- stable intraday ordering
- daily zero-fill continuity
- zero-fraction stays `0.0`
- directional signal families are emitted and scoreable

## 9. Definition of Done

- V654 mission is active in handover
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
- output roots:
- math audit verdict:
- runtime audit verdict:
- event-study verdict:
