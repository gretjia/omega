# OMEGA Active Mission Charter

Status: Completed
Task Name: V64 Bourbaki Closure Repo Alignment
Owner: Human Owner
Commander: Codex
Date: 2026-03-06

## 1. Objective

- Align the V64 codebase to the final Bourbaki Closure specification, starting from Stage 2.
- Propagate the closure from Stage 2 through runtime glue, Stage 3, config, documentation, training, and backtest consumers.
- Prepare the repository for PLAN -> CODING -> dual-audit execution under the permanent OMEGA Multi-Agent OS.

## 2. Canonical Spec

Primary task-level implementation authority:

- path: `audit/v64.md`
- exact section or commit: `[ SYSTEM ARCHITECT ABSOLUTE OVERRIDE: THE BOURBAKI CLOSURE ]`

Higher-order constraints:

- `OMEGA_CONSTITUTION.md`
- `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`
- `handover/ai-direct/LATEST.md` for live runtime state before any operational step

Conflict rule:

- Earlier sections of `audit/v64.md` are context only. If they conflict with the Bourbaki Closure section, the Bourbaki Closure section wins.
- If the task-level spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Business Goal

- Eliminate semantic drift between the V64 mathematical definition, the Stage 2 outputs, and the downstream Stage 3 / training / backtest pipeline.
- Ensure the next implementation pass is mathematically correct, operationally stable, and aligned with the handover lessons already recorded in `/handover`.

## 4. Files In Scope

Primary implementation scope:

- `omega_core/omega_math_rolling.py`
- `omega_core/kernel.py`
- `config.py`
- `README.md`
- `tests/test_v64_absolute_closure.py`

Stage 2 execution scope:

- `tools/stage2_physics_compute.py`

Downstream closure scope:

- `tools/stage3_full_supervisor.py`
- `omega_core/trainer.py`
- `tools/forge_base_matrix.py`
- `tools/run_vertex_xgb_train.py`
- `tools/run_local_backtest.py`

Possible audit-followup scope if findings require it:

- `tests/test_kernel_srl_numba.py`
- `tests/verify_pipeline.py`
- `tests/test_stage2_output_equivalence.py`
- `tools/run_v64_smoke_backtest.py`

## 5. Out of Scope

- Historical handover entries except as context
- Artifact regeneration without explicit mission-phase approval
- Deployment, commit, and push before dual-audit pass
- Unrelated strategy logic outside the V64 closure chain
- Behavioral changes to `tools/stage2_targeted_resume.py` while live Stage 2 jobs are active

## 6. Required Audits

Math audit:

- Engine: Gemini via `gemini -y`
- Responsibility: verify strict alignment to `[ SYSTEM ARCHITECT ABSOLUTE OVERRIDE: THE BOURBAKI CLOSURE ]`
- Focus: formula choice, gate separation, dimensional consistency, geometry homology, regression locks

Runtime audit:

- Engine: GPT-5 / Codex
- Responsibility: verify repository-level integration, stable CLI / config propagation, and operational safety
- Focus: no stale parameter semantics, no broken Stage 3 / training / backtest chain, no regression into deprecated multiprocessing-first execution patterns

## 7. Runtime and Efficiency Constraints

- Respect `handover/ai-direct/LATEST.md` before touching any live runtime path.
- Do not interrupt active long-running jobs unless the mission is explicitly escalated and reopened.
- Treat Stage 2 as the execution starting boundary for this mission; Stage 1 is out of scope.
- Prefer machine-level parallelism and bounded threading over Python `multiprocessing` fan-out.
- Use `linux1-lx` for long-lived pipeline / matrix / backtest workloads unless a mission-specific manifest says otherwise.
- Use `windows1-w1` only for disjoint workloads with isolated outputs and explicit handoff boundaries.

## 8. Acceptance Criteria

The mission passes only when all are true:

1. `omega_core/omega_math_rolling.py` uses the Bourbaki Closure MDL gain based on `Var(ΔP) / Var(R)`, with `Zero-variance -> zero signal` and no `999.0` pseudo-singularity in the MDL compression-gain path.
2. `omega_core/kernel.py` separates `signal_epi_threshold`, `brownian_q_threshold`, and `topo_energy_min`, removes the topology override path that breaks geometry homology, and retains `topo_area_min_abs` plus `srl_resid_sigma_mult` in the final `is_signal` gate.
3. Stage 2 entrypoints and outputs remain operationally stable without disrupting currently running live jobs.
4. `config.py` and repo-facing docs expose the new semantics and do not reintroduce deprecated configuration meanings into Stage 2 code paths.
5. Legacy parameter aliases, if retained, are constrained to Stage 3 CLIs and trainer evaluation helpers; canonical names remain the only source of truth for config and runtime semantics.
6. Downstream consumers (`stage3_full_supervisor`, `trainer`, `forge_base_matrix`, Vertex training path) preserve the V64.1 in-memory reconstruction path and do not regress to stale V64 gate semantics.
7. Stage 3 training and local backtest operate on explicitly disjoint data windows or equivalent by-construction isolation, rather than implicitly sharing the same Stage 2 corpus.
8. Artifact naming and training provenance remain consistent across Vertex training, local model loading, and handover records.
9. Regression coverage exists for the closure-specific hard bugs described by the architect.
10. Math audit passes.
11. Runtime audit passes.
12. Commander-only integration, handover, commit, and push gates remain intact.

## 9. Stop Conditions

Stop and escalate if any of the following happens:

- a required change expands beyond the in-scope file set
- the live runtime state in `handover/ai-direct/LATEST.md` would be disrupted by continuing
- the closure spec and `OMEGA_CONSTITUTION.md` appear inconsistent
- an auditor finds a block that requires mission reopen or scope reassignment
