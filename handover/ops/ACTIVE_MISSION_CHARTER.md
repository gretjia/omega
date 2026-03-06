# OMEGA Active Mission Charter

Status: Completed
Task Name: V64.3 Backtest Stall Remediation and Smoke Completion
Owner: Human Owner
Commander: Codex
Date: 2026-03-06

Current checkpoint:

- backtest remediation implemented
- isolated V64.3 smoke is green again end-to-end
- `commit + push` completed as `72f7fe9`
- post-push auditor review passed

## 1. Objective

- Complete the final missing leg of the isolated V64.3 smoke chain by fixing the local backtest stall.
- Preserve the already-passed evidence for `Stage 2 -> forge/base_matrix -> training`.
- Do not launch a new full Stage 2 run in this mission.
- After the backtest path is repaired, rerun only the missing smoke leg needed to finish the chain, then release by `commit + push` and post-push auditor review.

## 2. Canonical Spec

Primary task-level implementation authority:

- path: `audit/v643.md`
- exact section or commit: latest `[ SYSTEM ARCHITECT FINAL OVERRIDE: THE BOURBAKI COMPLETION ]`

Higher-order constraints:

- `OMEGA_CONSTITUTION.md`
- `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`
- `handover/ai-direct/LATEST.md` for live runtime state before any operational step
- `handover/ai-direct/entries/20260306_134038_v643_backtest_stall_triage.md` for the exact blocker evidence

Conflict rule:

- Earlier sections of `audit/v64.md` and `audit/v642.md` are context only. If they conflict with the Bourbaki Completion section, the Bourbaki Completion section wins.
- If the task-level spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Business Goal

- Eliminate the runtime stall in the local backtest path without reopening already-passed upstream stages.
- Keep the V64.3 mathematical closure intact while replacing or remediating the outdated multiprocessing-heavy backtest execution pattern.
- Ensure the next implementation pass is operationally stable and aligned with the handover lessons already recorded in `/handover`.

## 4. Files In Scope

Primary implementation scope:

- `config.py`
- `tools/run_local_backtest.py`
- `omega_core/trainer.py`
- `tests/verify_pipeline.py`
- `handover/ai-direct/LATEST.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`

Conditional scope only if the remediation proves a contract issue:

- `tools/forge_base_matrix.py`
- `tools/run_vertex_xgb_train.py`
- `README.md`

## 5. Out of Scope

- Recomputing Stage 2 smoke outputs
- Recomputing Stage 3 shard forge unless the backtest fix proves the current base-matrix artifact contract invalid
- Reopening kernel or rolling-math semantics without a new audit finding
- Deployment, commit, and push before the repaired smoke leg passes
- Unrelated strategy logic outside the V64.3 backtest completion path

## 6. Required Audits

Math audit:

- Engine: Gemini via `gemini -y`
- Responsibility: verify that the backtest remediation does not regress the `v643` closure semantics
- Focus: no reintroduction of stale `is_signal`, stale feature columns, or non-canonical V64.3 gating

Runtime audit:

- Engine: GPT-5 / Codex
- Responsibility: verify repository-level integration, stable CLI / config propagation, and operational safety
- Focus: no stalled multiprocessing path, no broken model-loading contract, no broken `frames-dir` consumption path, and no regression into deprecated multiprocessing-first execution patterns

## 7. Runtime and Efficiency Constraints

- Respect `handover/ai-direct/LATEST.md` before touching any live runtime path.
- Do not interrupt active long-running jobs unless the mission is explicitly escalated and reopened.
- Reuse the existing isolated smoke workspace at `/home/zepher/work/Omega_vNext_v643_smoke`.
- Reuse the already-produced smoke artifacts under `.tmp/smoke_v64_v643`.
- Prefer a bounded, observable execution path over Python `multiprocessing` fan-out in the backtest step.
- Use `linux1-lx` as the only execution node for this remediation unless a new manifest says otherwise.

## 8. Acceptance Criteria

The mission passes only when all are true:

1. The stalled backtest path is replaced or remediated without reopening Stage 2 smoke, shard forge, base-matrix merge, or training.
2. The repaired backtest produces `.tmp/smoke_v64_v643/model/local_backtest.json` in the isolated smoke workspace.
3. `config.py` remains the only active config entry for this path; no `ashare_config.py` or `config_v6.py` dependency re-enters the smoke chain.
4. The fix does not regress the V64.3 canonical feature contract consumed by training and backtest.
5. The repaired path does not depend on the deprecated multiprocessing-first execution pattern that caused the stall.
6. Runtime audit passes.
7. Math invariance audit passes if any semantics-adjacent code is touched.
8. Commander-only handover, commit, and push gates remain intact.

## 9. Stop Conditions

Stop and escalate if any of the following happens:

- a required change expands beyond the in-scope file set
- the existing `base_matrix` or model artifact contract proves invalid and forces upstream recomputation
- the live runtime state in `handover/ai-direct/LATEST.md` would be disrupted by continuing
- the closure spec and `OMEGA_CONSTITUTION.md` appear inconsistent
- an auditor finds a block that requires mission reopen or scope reassignment
