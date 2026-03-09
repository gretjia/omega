# OMEGA Active Mission Charter

Status: In Progress
Task Name: V645 GC asymmetric-label pivot
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

## 1. Objective

- Accept the external architect verdict that the bottleneck now sits at the ML label / objective interface.
- Run the minimum decisive pivot experiment without reopening math-governance.
- Keep `v64.3 / v643` math frozen while testing whether magnitude-aware learning flips validation tail alpha positive.
- Preserve the frozen holdout verdict as immutable audit baseline while executing the new pivot experiment.
- First-wave path is now resolved:
  - Path A first
  - local-first
  - micro-sweep before retrain or fresh holdout evaluation

## 2. Canonical Spec

Primary task-level implementation authority:

- `handover/ai-direct/entries/20260309_074955_asymmetric_label_pivot_mission_open.md`
  - exact section:
    - new canonical diagnosis
    - allowed experiment family
    - execution rule
    - required runtime shape
    - success gate

Seed authority that led to the final spec:

- `audit/v644_mediocristan_label_bottleneck.md`
- `handover/ai-direct/entries/20260309_072256_v644_alpha_first_pilot_stop_gate.md`
- `handover/ai-direct/entries/20260309_072941_external_ai_auditor_prompt_gc_runs.md`

Supporting context:

- `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`
- `handover/ai-direct/entries/20260309_050702_gc_swarm_optuna_pilot_and_champion_retrain_complete.md`
- `handover/ai-direct/entries/20260309_012152_gc_swarm_optuna_project_spec.md`
- `OMEGA_CONSTITUTION.md`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_optuna_sweep.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_swarm_aggregate.py`
- `tests/test_vertex_holdout_eval.py`
- `audit/README.md`
- `audit/v644_mediocristan_label_bottleneck.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

Read-only but relevant files:

- `tools/run_vertex_xgb_train.py`
- `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`
- `handover/ai-direct/entries/20260309_050702_gc_swarm_optuna_pilot_and_champion_retrain_complete.md`
- `handover/ai-direct/entries/20260309_070752_v644_agentos_final_execution_spec.md`
- `audit/v643.md`
- `audit/v643_auditor_pass.md`

Explicitly out of scope:

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge
- overwriting the frozen holdout baseline outputs
- using `2025` or `2026-01` inside optimization scoring

## 4. Roles

Plan Agent:

- responsibility:
  - choose the minimum decisive pivot path and map it to a bounded file-level implementation plan

Coder Agent:

- writable files only:
  - `tools/run_optuna_sweep.py`
  - `tools/launch_vertex_swarm_optuna.py`
  - `tests/test_vertex_optuna_split.py`

Math Auditor:

- audit target:
  - verify that the pivot stays outside `omega_core/*`, preserves frozen gates, and does not silently mutate canonical physics semantics beyond the allowed learner interface pivot

Runtime Auditor:

- audit target:
  - verify that the pivot experiment is operationally minimal, fresh-prefix isolated, and does not waste cloud budget before the interface hypothesis is tested

## 5. Acceptance Criteria

- the external architect verdict is recorded in `audit/`
- a concrete pivot mission spec exists and is recorded in handover
- the first implementation wave is bounded to the learner interface
- AgentOS has resolved the minimum decisive first path to:
  - `Path A`
  - `weight_mode=abs_excess_return`
  - `min_val_auc=0.501`
  - local `10`-trial micro-sweep
- the frozen baseline rule is explicit:
  - new runs must use fresh output prefixes
  - new runs must append evidence, not overwrite old evidence
- AgentOS plan/runtime/math review packets have been issued for the pivot mission
- the first live experiment is constrained to:
  - `10-20` trials
  - local or `1`-worker GCP
  - fresh output prefix only
- the first live experiment has now completed with:
  - positive validation `alpha_top_quintile`

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
  - must be a fresh pivot-experiment prefix, not the frozen V644 prefixes
- host isolation check:
  - no holdout matrix enters optimization

## 7. Fail-Fast Conditions

- stop if the new mission proposes overwriting the frozen holdout verdict
- stop if the new mission widens scope into `omega_core/*` without a separate math-governance mission
- stop if the new mission drops holdout isolation
- stop if the mission mutates Stage3 gates or `omega_core/*`
- stop if the mission widens into multi-worker cloud search before the interface pivot is validated
- stop if anyone reopens Path B before exploiting the now-positive Path A signal on retrain + fresh holdout evaluation
- retry allowed only after named root cause and changed condition

## 8. Audits Required

Math audit must verify:

- frozen canonical gates remain unchanged
- no hidden mutation of physics semantics outside the explicitly allowed learner interface pivot

Runtime audit must verify:

- the first pivot experiment is operationally minimal
- new outputs are isolated from the frozen baseline outputs

## 9. Definition of Done

- external architect verdict recorded
- new active mission charter instantiated
- AgentOS role packets started for the pivot mission
- AgentOS convergence achieved on the first path
- no blocking ambiguity remains about:
  - allowed pivot family
  - out-of-scope math boundary
  - first micro-sweep shape
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
- pivot path:
  - `Path A`
- learner objective:
  - `binary:logistic`
- weighting mode:
  - `abs_excess_return`
- fresh prefix check:
  - `passed`
