# OMEGA Active Mission Charter

Status: In Progress
Task Name: V659 Fixed-Contract Replication Audit
Owner: Human Owner
Commander: Codex
Date: 2026-03-10

## 1. Objective

- Preserve the frozen V655A soft-mass candidate stream, V655B amplitude-aware daily fold, V656 transition derivations, V657 sign-aware threshold semantics, and V658 blocked admission result.
- Change only the evaluation sample.
- Replicate the exact V657 winning contract on a disjoint contiguous post-selection block before any broader ML reopening.
- Keep the mission strictly non-ML.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v659_fixed_contract_replication_audit.md`
- `audit/v658_h1_ml_admission_probe_block_evidence.md`
- `audit/v657_h1_sign_aware_threshold_pass_evidence.md`
- `audit/v657_sign_aware_threshold_hazard_audit.md`
- `handover/ai-direct/entries/20260310_111517_v659_fixed_contract_replication_audit_spec_draft.md`
- `handover/ai-direct/entries/20260310_111755_v659_spec_gemini_pass.md`
- `handover/ai-direct/entries/20260310_113335_v659_code_delta_gemini_pass.md`
- `handover/ai-direct/entries/20260310_113349_v659_fixed_contract_replication_mission_open.md`

Supporting context:

- `OMEGA_CONSTITUTION.md`
- `tools/forge_campaign_state.py`
- `tools/run_campaign_transition_event_study.py`
- `tools/run_campaign_sign_aware_threshold_audit.py`
- `tools/run_campaign_fixed_contract_replication_audit.py`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_campaign_fixed_contract_replication_audit.py`
- `tests/test_campaign_fixed_contract_replication_audit.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`
- `audit/README.md`
- `audit/v659_*`

Read-only but relevant files:

- `tools/forge_campaign_state.py`
- `tools/run_campaign_transition_event_study.py`
- `tools/run_campaign_sign_aware_threshold_audit.py`
- `omega_core/*`
- frozen V64 / V643 / V653 / V654 / V655A / V655B / V656 / V657 / V658 audit canon
- frozen V655B / V657 / V658 runtime evidence

Explicitly out of scope before V659 passes:

- reopening Path A
- any Vertex / GCP launch
- any learner / Optuna / hyperparameter sweep
- `2025` / `2026-01` holdout consumption
- changing forge math
- changing daily spine semantics
- changing label or barrier semantics
- changing same-sign pulse compression
- changing the V655A candidate stream
- changing the V655B amplitude-aware fold
- changing the V656 transition derivation formulas
- changing the V657 threshold semantics
- changing the V658 admission contract
- opening broader ML before fixed-contract replication passes

## 4. Roles

Commander:

- define scope
- integrate code and docs
- own git / push / handover

Formula Integrity Auditor:

- engine:
  - direct `/usr/bin/gemini`
- model rule:
  - `gemini 3.1 pro preview` only
- responsibility:
  - audit every formula-bearing diff against the frozen V659 authority

Replication Window Auditor:

- responsibility:
  - prove the selected replication window is contiguous enough operationally
  - prove it does not overlap the H1 2023 selection slice

Campaign Forge Reuse Engineer:

- responsibility:
  - rerun unchanged forge math on the replication block only

Sign-Aware Evaluator Engineer:

- responsibility:
  - reuse the frozen V657 evaluator semantics on the fixed contract only

Coverage Auditor:

- responsibility:
  - verify scored-date coverage
  - verify threshold counts tighten monotonically
  - verify strongest-threshold baseline comparisons

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - enforce local-only / no-ML / no-cloud sequencing
  - monitor by actual process and artifact evidence only

ML Readiness Gatekeeper:

- responsibility:
  - keep broader ML / Vertex / holdout closed unless V659 passes

## 5. Acceptance Criteria

- V659 mission-open authority exists in handover
- the active charter explicitly freezes the V659 single-axis repair boundary
- implementation preserves:
  - daily spine
  - tradable return labels
  - triple-barrier semantics
  - V655A soft-mass candidate stream
  - V655B amplitude-aware daily fold
  - V656 transition derivations
  - V657 threshold semantics
- implementation changes only:
  - replication sample
- no learner / cloud / holdout steps are opened before V659 resolves

## 6. Runtime Preflight

Required before execution:

- replication block is disjoint from H1 2023 selection slice
- replication block source coverage is recorded
- local-only phase ordering
- fresh isolated V659 output path
- no cloud endpoints
- no holdout paths
- unchanged forge math
- fixed contract only

## 7. Fail-Fast Conditions

- stop if any step changes the mathematical meaning of frozen formulas
- stop if any step changes signal family, side, or threshold ladder
- stop if any step opens ML before V659 resolves
- stop if any step consumes `2025` / `2026-01` holdouts early
- stop if a required formula-bearing diff has not been audited with Gemini 3.1 Pro Preview
- stop if the replication window overlaps the selection slice

## 8. Audits Required

Math audit must verify:

- the single change axis is exactly the evaluation sample
- V655B amplitude-aware forge semantics remain intact
- V656 transition derivations remain intact
- V657 threshold semantics remain intact
- no learner or objective search is introduced

Runtime audit must verify:

- the replication block is disjoint from the V657/V658 H1 slice
- the fixed contract is exactly:
  - `dPsiAmpE_10d`
  - `negative`
  - `90 / 95 / 97.5`
- coverage and threshold tightening metrics are emitted
- negative-side universe baselines are emitted

## 9. Definition of Done

- V659 mission is active in handover
- first replication-block forge is recorded
- fixed-contract threshold audit on that block is recorded
- a pass / block verdict is explicit
- handover updated
- Commander-only commit/push completed

## 10. Run Manifest

Record after execution:

- commit hash:
- nodes used:
- replication block:
- output roots:
- math audit verdict:
- runtime audit verdict:
- fixed-contract replication verdict:
