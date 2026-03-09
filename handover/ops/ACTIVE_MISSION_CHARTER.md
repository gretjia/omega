# OMEGA Active Mission Charter

Status: In Progress
Task Name: V653 Fractal Campaign Awakening
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

## 1. Objective

- Accept the newest architect override as the canonical authority for the next OMEGA upgrade wave.
- Rebuild OMEGA around a real daily temporal spine plus recursive campaign-state compression.
- Prove campaign-state edge through pure event study before reopening any ML.
- Preserve the frozen mathematics while allowing truth-first engineering changes, including `omega_core/*` edits and Stage2 recomputation if required.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v653_fractal_campaign_awakening.md`
- `audit/v653_identity_preservation_gemini_verdict.md`
- `handover/ai-direct/entries/20260309_172447_v653_fractal_campaign_awakening_spec_draft.md`
- `handover/ai-direct/entries/20260309_172925_v653_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_173514_v653_identity_preservation_gemini_verdict.md`
- `handover/ai-direct/entries/20260309_174239_v653_fractal_campaign_awakening_mission_open.md`

Supporting context:

- `OMEGA_CONSTITUTION.md`
- `omega_core/kernel.py`
- `omega_core/omega_math_core.py`
- `omega_core/trainer.py`
- `tools/forge_base_matrix.py`
- `tools/stage2_physics_compute.py`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `omega_core/*` where strictly required by the frozen V653 formulas
- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py`
- `tools/forge_base_matrix.py` if a bridge is still required
- `tools/stage2_physics_compute.py` only if truth-first Stage2 recomputation becomes necessary
- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`
- `audit/README.md`
- `audit/v653_*`

Read-only but relevant files:

- `OMEGA_CONSTITUTION.md`
- frozen V64 / V643 audit canon
- frozen V645 -> V650 evidence
- current local runtime evidence and manifests

Explicitly out of scope before the event-study gate passes:

- reopening Path A
- any Vertex / GCP launch
- any XGBoost tuning or ML sweep
- `2025` / `2026-01` holdout consumption
- changing the mathematical meaning of the frozen V653 formulas

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
  - audit every formula-bearing diff against the frozen V653 formulas

Temporal Spine Engineer:

- responsibility:
  - identify or construct the real daily trading-date spine

Stage2 Integrity / Recompute Engineer:

- responsibility:
  - determine whether current Stage2 outputs are sufficient for the campaign forge
  - specify or execute recomputation if truth requires it

Campaign State Forge Engineer:

- responsibility:
  - implement the campaign-state forge

Numba Barrier Kernel Engineer:

- responsibility:
  - implement and validate the first-passage barrier kernel if required

Core Integration Engineer:

- responsibility:
  - make any necessary `omega_core/*` translation changes without formula drift

Data Contract Auditor:

- responsibility:
  - verify schema, field availability, and lineage

Distribution Auditor:

- responsibility:
  - verify zero-mass collapse is eliminated under the corrected date-only demeaning and daily spine

Event Study Auditor:

- responsibility:
  - verify decile monotonicity, spread, and barrier asymmetry

Runtime Orchestrator:

- responsibility:
  - assign nodes, keep outputs isolated, and enforce no-cloud sequencing

ML Readiness Gatekeeper:

- responsibility:
  - block all ML until the event-study gate is passed

## 5. Acceptance Criteria

- V653 mission-open authority exists in handover
- the active charter explicitly freezes the V653 formulas and truth-first boundaries
- phase-1 readiness determines:
  - where the daily spine will come from
  - whether current Stage2 outputs are sufficient
  - whether a bridge or recompute is required
- campaign-state forge implementation preserves:
  - `F`
  - `A`
  - `S`
  - `V`
  - `Omega`
  - `Psi`
  - tradable `Y_ret`
  - triple-barrier semantics
- pure event study runs before any ML work
- no ML / cloud / holdout steps are opened before the event-study gate

## 6. Runtime Preflight

Required before execution:

- controller remains the integration authority
- local-only phase ordering until event-study proof exists
- fresh isolated runtime roots for V653 outputs
- no cloud endpoints
- no holdout paths
- use `windows1-w1` first when heavy local forge throughput is beneficial
- use `linux1-lx` for parity verification or Stage2 overflow / recompute if required

## 7. Fail-Fast Conditions

- stop if any step changes the mathematical meaning of the frozen formulas
- stop if any step opens ML before the event-study gate
- stop if any step consumes `2025` / `2026-01` holdouts early
- stop if any step attempts cloud execution before local proof
- stop if a required formula-bearing diff has not been audited with `gemini -p`

## 8. Audits Required

Math audit must verify:

- formula preservation
- EMA/IIR campaign recursion semantics
- tradable label and barrier semantics

Runtime audit must verify:

- daily spine continuity
- artifact lineage and schema continuity
- isolation from cloud and holdout paths

## 9. Definition of Done

- V653 mission is active in handover
- phase-1 readiness is resolved
- campaign-state forge and event study are implemented and verified
- a go / no-go verdict for ML reopening is recorded
- no blocking findings remain
- handover updated
- Commander-only commit/push completed

## 10. Run Manifest

Record after execution:

- commit hash:
- nodes used:
- daily spine source:
- Stage2 source or recompute root:
- output roots:
- math audit verdict:
- runtime audit verdict:
- event-study verdict:
