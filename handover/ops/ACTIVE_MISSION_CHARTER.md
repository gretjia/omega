# OMEGA Active Mission Charter

Status: In Progress
Task Name: V660 Regime-Segmented Replication Audit
Owner: Human Owner
Commander: Codex
Date: 2026-03-10

## 1. Objective

- Preserve the frozen V655A soft-mass candidate stream, V655B amplitude-aware daily fold, V656 transition derivations, V657 sign-aware threshold semantics, V658 blocked admission result, and the frozen V659 replication block.
- Change only the evaluation-sample partition inside the already-forged V659 replication block.
- Diagnose whether the V659 failure is regime-mixed inside deterministic month segments before any broader ML reopening.
- Keep the mission strictly non-ML.

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v660_regime_segmented_replication_audit.md`
- `audit/v659_replication_block_evidence.md`
- `audit/v659_fixed_contract_replication_audit.md`
- `handover/ai-direct/entries/20260310_171500_v660_regime_segmented_replication_spec_draft.md`
- `handover/ai-direct/entries/20260310_175353_v660_code_delta_gemini_pass.md`
- `handover/ai-direct/entries/20260310_175353_v660_regime_segmented_mission_open.md`

Supporting context:

- `OMEGA_CONSTITUTION.md`
- `tools/forge_campaign_state.py`
- `tools/run_campaign_transition_event_study.py`
- `tools/run_campaign_sign_aware_threshold_audit.py`
- `tools/run_campaign_fixed_contract_replication_audit.py`
- `tools/run_campaign_segmented_replication_audit.py`

## 3. Scope

Writable files:

- `tools/run_campaign_segmented_replication_audit.py`
- `tests/test_campaign_segmented_replication_audit.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`
- `audit/README.md`
- `audit/v660_*`

Read-only but relevant files:

- `tools/forge_campaign_state.py`
- `tools/run_campaign_transition_event_study.py`
- `tools/run_campaign_sign_aware_threshold_audit.py`
- `tools/run_campaign_fixed_contract_replication_audit.py`
- `omega_core/*`
- frozen V655B / V657 / V658 / V659 runtime evidence

Explicitly out of scope before V660 resolves:

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
- changing the V659 fixed contract
- opening broader ML before V660 resolves

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
  - audit every formula-bearing diff against the frozen V660 authority

Segmentation Auditor:

- responsibility:
  - prove month buckets are deterministic
  - prove segmentation changes only sample partition

Evaluator Reuse Engineer:

- responsibility:
  - reuse the frozen V659 fixed-contract audit semantics inside each eligible segment

Coverage Auditor:

- responsibility:
  - verify segment eligibility
  - verify segment-level threshold counts tighten monotonically
  - verify segment-level strongest-threshold baseline comparisons

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - enforce local-only / no-ML / no-cloud sequencing
  - monitor by actual process and artifact evidence only

ML Readiness Gatekeeper:

- responsibility:
  - keep broader ML / Vertex / holdout closed unless V660 resolves cleanly

## 5. Acceptance Criteria

- V660 mission-open authority exists in handover
- the active charter explicitly freezes the V660 single-axis repair boundary
- implementation preserves:
  - daily spine
  - tradable return labels
  - triple-barrier semantics
  - V655A soft-mass candidate stream
  - V655B amplitude-aware daily fold
  - V656 transition derivations
  - V657 threshold semantics
  - the V659 fixed contract
- implementation changes only:
  - sample partition into deterministic month buckets
- no learner / cloud / holdout steps are opened before V660 resolves

## 6. Runtime Preflight

Required before execution:

- V659 replication block remains frozen
- segmentation rule is deterministic
- local-only phase ordering
- fresh isolated V660 output path
- no cloud endpoints
- no holdout paths
- fixed contract only

## 7. Fail-Fast Conditions

- stop if any step changes the mathematical meaning of frozen formulas
- stop if any step changes signal family, side, or threshold ladder
- stop if any step changes forge / label / barrier semantics
- stop if any step opens ML before V660 resolves
- stop if a required formula-bearing diff has not been audited with Gemini 3.1 Pro Preview

## 8. Audits Required

Math audit must verify:

- the single change axis is exactly the evaluation-sample partition
- V655B amplitude-aware forge semantics remain intact
- V656 transition derivations remain intact
- V657 threshold semantics remain intact
- V659 fixed-contract semantics remain intact
- no learner or objective search is introduced

Runtime audit must verify:

- the fixed contract is exactly:
  - `dPsiAmpE_10d`
  - `negative`
  - `90 / 95 / 97.5`
- deterministic month buckets are emitted
- segment-level threshold metrics are emitted

## 9. Definition of Done

- V660 mission is active in handover
- segmented audit on the frozen V659 block is recorded
- a pass / block verdict is explicit
- handover updated
- Commander-only commit/push completed

## 10. Run Manifest

Record after execution:

- commit hash:
- nodes used:
- frozen replication block:
- output roots:
- math audit verdict:
- runtime audit verdict:
- segmented replication verdict:
