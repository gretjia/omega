# OMEGA Active Mission Charter

Status: In Progress
Task Name: V644 GC swarm asymmetric-objective follow-on
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

## 1. Objective

- Open the next cloud mission after the frozen holdout verdict.
- Realign the swarm optimization target so future champions are selected for tail profitability, not just global classification quality.
- Keep `v64.3 / v643` math frozen and use this mission as the clean test of whether the remaining failure is selector-level or math-level.
- Preserve the frozen holdout verdict as immutable audit baseline while executing the next cloud-parallel search protocol.

## 2. Canonical Spec

Primary task-level implementation authority:

- `handover/ai-direct/entries/20260309_070752_v644_agentos_final_execution_spec.md`
  - exact section:
    - canonical objective for V644
    - hard guardrails
    - code-level contract
    - pilot shape
    - acceptance gates

Seed authority that led to the final spec:

- `handover/ai-direct/entries/20260309_055200_gemini_asymmetric_objective_spec.md`
- `handover/ai-direct/entries/20260309_060200_gemini_v643_alignment_on_asymmetric_mission.md`

Supporting context:

- `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`
- `handover/ai-direct/entries/20260309_050702_gc_swarm_optuna_pilot_and_champion_retrain_complete.md`
- `handover/ai-direct/entries/20260309_012152_gc_swarm_optuna_project_spec.md`
- `OMEGA_CONSTITUTION.md`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_optuna_sweep.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_swarm_aggregate.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

Read-only but relevant files:

- `tools/evaluate_xgb_on_base_matrix.py`
- `tools/run_vertex_xgb_train.py`
- `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`
- `handover/ai-direct/entries/20260309_050702_gc_swarm_optuna_pilot_and_champion_retrain_complete.md`
- `handover/ai-direct/entries/20260309_012152_gc_swarm_optuna_project_spec.md`

Explicitly out of scope:

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge
- overwriting the frozen holdout baseline outputs
- using `2025` or `2026-01` inside optimization scoring

## 4. Roles

Plan Agent:

- responsibility:
  - refine the alpha-first mission from Gemini into an executable file-level change map with guardrails

Coder Agent:

- writable files only:
  - `tools/run_optuna_sweep.py`
  - `tools/aggregate_vertex_swarm_results.py`
  - `tools/launch_vertex_swarm_optuna.py`
  - associated tests

Math Auditor:

- audit target:
  - verify that the new mission stays inside frozen `v64.1` gates and does not silently mutate canonical physics semantics

Runtime Auditor:

- audit target:
  - verify that the new cloud objective, pilot shape, and output isolation remain operationally sound

## 5. Acceptance Criteria

- a concrete alpha-first swarm spec exists and is recorded in handover
- the canonical V644 objective is fixed to:
  - `alpha_top_quintile`
- alpha-first mode keeps:
  - `val_auc` as a hard eligibility gate
- the frozen baseline rule is explicit:
  - new runs must use fresh output prefixes
  - new runs must append evidence, not overwrite old evidence
- AgentOS plan/runtime/math review packets have been issued and integrated
- the next implementation wave has bounded writable files, guardrails, and pilot gates
- the first live pilot shape is fixed to:
  - `2` workers
  - `n2-standard-16`
  - `spot`
  - `train_year=2023`
  - `val_year=2024`

## 6. Runtime Preflight

Required before execution:

- target node:
  - controller + GCP Vertex AI
- expected commit or branch:
  - `main`
- controller-only code freshness requirement (if any):
  - worker deploy path must remain controller-managed
- worker deploy path via `tools/deploy.py` (workers never `git pull`):
  - note current Windows deploy caveat:
    - `ext::ssh windows1-w1 %S D:/work/Omega_vNext/.git`
    - controller-side push still requires `protocol.ext.allow=always`
- launcher mode:
  - `gcloud` fallback remains the stable controller path until proven otherwise
- shard assignment:
  - cloud-parallel workers only
- thread caps:
  - keep current worker-local defaults unless the next plan changes them explicitly
- output root:
  - must be a fresh V644 swarm prefix, not the frozen pilot prefix
- host isolation check:
  - no holdout matrix enters optimization

## 7. Fail-Fast Conditions

- stop if the new mission proposes overwriting the frozen holdout verdict
- stop if the new mission widens scope into `omega_core/*` without a separate math-governance mission
- stop if the new mission drops holdout isolation
- stop if the mission redefines the label contract or the frozen `canonical_v64_1` gate contract
- stop if alpha-first mode runs without an explicit `val_auc` guardrail
- retry allowed only after named root cause and changed condition

## 8. Audits Required

Math audit must verify:

- frozen canonical gates remain unchanged
- no hidden redefinition of the label or signal-chain semantics

Runtime audit must verify:

- cloud-parallel value remains real and not local-only theater
- new pilot outputs are isolated from the frozen baseline outputs

## 9. Definition of Done

- Gemini follow-on spec recorded
- new active mission charter instantiated
- AgentOS role packets started and integrated
- no blocking ambiguity remains about:
  - canonical objective
  - AUC guardrail
  - first pilot shape
  - fresh-prefix isolation
- handover updated

## 10. Run Manifest

Record after execution:

- commit hash:
- node:
- shard set:
- thread caps:
- launcher mode:
- dataset role:
- math audit verdict:
- runtime audit verdict:
- objective metric:
- auc guardrail:
- fresh prefix check:
