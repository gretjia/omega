# OMEGA Active Mission Charter

Status: In Progress
Task Name: V646 Path A refinement
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

## 1. Objective

- Accept that `Path A` is now the leading learner-interface branch.
- Refine `Path A` without reopening math-governance, `Path B`, or GC fan-out.
- Preserve all previously recorded baselines as immutable audit evidence.
- Improve the current `Path A` tradeoff:
  - keep the economic gains already achieved
  - reduce the remaining `2026-01` weakness
  - avoid drifting into a branch that only improves alpha by destroying all ranking stability

## 2. Canonical Spec

Primary task-level implementation authority:

- `handover/ai-direct/entries/20260309_091728_v646_path_a_refinement_mission_open.md`
  - exact section:
    - why the mission now splits
    - new canonical diagnosis
    - allowed refinement family
    - required runtime shape
    - frozen reference baselines

Seed authority that led to the final spec:

- `audit/v644_mediocristan_label_bottleneck.md`
- `handover/ai-direct/entries/20260309_080141_v645_path_a_local_micro_sweep_positive.md`
- `handover/ai-direct/entries/20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass.md`
- `handover/ai-direct/entries/20260309_090713_v645_path_b_local_compare_weaker_than_path_a.md`

Supporting context:

- `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`
- `OMEGA_CONSTITUTION.md`

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_train_weight_mode.py`
- `tests/test_vertex_holdout_eval.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`

Read-only but relevant files:

- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`
- `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`
- `handover/ai-direct/entries/20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass.md`
- `handover/ai-direct/entries/20260309_090713_v645_path_b_local_compare_weaker_than_path_a.md`
- `audit/v644_mediocristan_label_bottleneck.md`

Explicitly out of scope:

- `omega_core/*`
- Stage1 / Stage2 / Stage3 forge
- widening back into GC by default
- promoting `Path B` above `Path A` without new evidence
- overwriting any frozen old or new holdout outputs
- using `2025` or `2026-01` inside optimization scoring or local sweep selection

## 4. Roles

Plan Agent:

- responsibility:
  - choose the minimum decisive `Path A` refinement and map it to a bounded file-level implementation plan

Coder Agent:

- writable files only:
  - `tools/run_optuna_sweep.py`
  - `tools/run_vertex_xgb_train.py`
  - `tests/test_vertex_optuna_split.py`
  - `tests/test_vertex_train_weight_mode.py`

Math Auditor:

- audit target:
  - verify that the refinement stays inside `Path A`, outside `omega_core/*`, and preserves frozen gates

Runtime Auditor:

- audit target:
  - verify that the refinement remains local-first, fresh-prefix isolated, and does not reopen GC prematurely

## 5. Acceptance Criteria

- a concrete `Path A refinement` mission spec exists and is recorded in handover
- the frozen-baseline rule is explicit for:
  - old holdout baseline
  - fresh Path A holdout branch
  - fresh Path B local compare
- AgentOS plan/runtime/math review packets have been issued for the refinement mission
- the next live work is constrained to:
  - local-first
  - fresh output prefix only
  - bounded `Path A` refinement only
- no ambiguity remains about:
  - GC staying paused
  - `Path B` staying secondary
  - math and Stage3 gates remaining frozen

## 6. Runtime Preflight

Required before execution:

- target node:
  - controller first
  - dual-host only after a refined local candidate earns promotion
- expected commit or branch:
  - `main`
- controller-only code freshness requirement (if any):
  - worker deploy path must remain controller-managed
- worker deploy path via `tools/deploy.py` (workers never `git pull`):
  - note current Windows deploy caveat:
    - `ext::ssh windows1-w1 %S D:/work/Omega_vNext/.git`
    - controller-side push still requires `protocol.ext.allow=always`
- launcher mode:
  - no GC launcher by default for this mission
- shard assignment:
  - local-first refinement only
- thread caps:
  - keep current worker-local defaults unless the next plan changes them explicitly
- output root:
  - must be a fresh refinement prefix, not any frozen prior prefix
- host isolation check:
  - no holdout matrix enters optimization

## 7. Fail-Fast Conditions

- stop if the new mission proposes overwriting any frozen baseline
- stop if the new mission widens scope into `omega_core/*` without a separate math-governance mission
- stop if the new mission drops holdout isolation
- stop if the mission mutates Stage3 gates or `omega_core/*`
- stop if the mission widens into GC before a refined local `Path A` candidate is proven
- stop if anyone reopens `Path B` as the leading branch without new evidence
- retry allowed only after named root cause and changed condition

## 8. Audits Required

Math audit must verify:

- frozen canonical gates remain unchanged
- no hidden mutation of physics semantics outside the explicitly allowed `Path A` refinement

Runtime audit must verify:

- the refinement stays local-first
- new outputs are isolated from all frozen baseline outputs

## 9. Definition of Done

- new active mission charter instantiated
- AgentOS role packets started for the refinement mission
- AgentOS convergence achieved on the first refinement slice
- no blocking ambiguity remains about:
  - allowed refinement family
  - out-of-scope math boundary
  - GC pause
  - fresh-prefix isolation across all frozen baselines
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
- refinement branch:
  - `Path A`
- learner objective:
  - `binary:logistic`
- weight shaping:
- fresh prefix check:
  - `passed`
