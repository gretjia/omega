# OMEGA Active Mission Charter

Status: In Progress
Task Name: V64 engineering speed patch evaluation and zero-signal diagnosis
Owner: Human Owner
Commander: Codex
Date: 2026-03-07

Current checkpoint:

- the engineering speed patch remains local-only and uncommitted
- the first speed smoke was `NO PASS`, but the dominant blocker was unfair training-parameter drift rather than a proven math regression
- a baseline-comparison smoke restored training to the historical `10.98s` contract while keeping the new backtest path fast
- non-zero slice discovery has not succeeded yet:
  - `37` monthly tiny probes
  - `5` full-day `fbd5c8b` probes
  - `5` full-day `b07c2229` probes
  all remained zero under strict V64.3 semantics
- the pre-speed baseline smoke workspace is also zero-signal, so the zero-output condition predates the engineering speed patch
- the Owner has explicitly ordered that both engineering routes remain preserved until the all-zero root cause is understood

## 1. Objective

- Evaluate the engineering speed patch against fair smoke comparisons without changing the approved V64.3 canonical runtime math core.
- Preserve the previous successful smoke workspace and every follow-on comparison workspace as rollback and evidence anchors.
- Separate two problem classes cleanly:
  1. engineering release evaluation of the speed patch
  2. long-standing zero-signal / non-informative-slice diagnosis that already existed in the baseline smoke

## 2. Canonical Spec

Primary task-level implementation authority:

- `audit/v64_audit_evolution.md` for the approved V64.3 canonical runtime math core and release logic
- `audit/v643.md` and `audit/v643_auditor_pass.md` for the final V64.3 closure and math-core release state

Higher-order constraints:

- `OMEGA_CONSTITUTION.md`
- `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`
- `handover/ai-direct/LATEST.md`

Conflict rule:

- The approved V64.3 canonical runtime math core is fixed. This mission may evaluate engineering changes around it, but it must not silently redefine it.
- If the task-level engineering evaluation conflicts with the approved canonical math core, escalate to the Commander.

## 3. Business Goal

- Determine whether the engineering speed patch can be released on fair performance grounds.
- Avoid false attribution: do not blame the speed patch for zero-signal smoke behavior that already existed in the baseline workspace.
- Preserve enough evidence so that the Owner can later decide whether to continue with:
  - a release decision on the speed patch
  - a separate mission for the older zero-signal / ordering / slice-informativeness problem
- Keep both engineering routes alive until the all-zero root cause is identified:
  - the pre-speed route as baseline / fallback
  - the speed-patch route as candidate upgrade

## 4. Files In Scope

Primary implementation scope:

- `handover/ai-direct/LATEST.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ai-direct/entries/20260307_005243_v64_engineering_speed_patch_and_zero_signal_diagnosis.md`

Evidence and diagnosis scope:

- isolated smoke workspaces on `linux1-lx`
- probe manifests and ranking artifacts under `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/`

Conditional code scope only if a new owner-approved remediation mission is opened:

- `omega_core/kernel.py`
- `omega_core/omega_math_rolling.py`
- `tools/run_vertex_xgb_train.py`
- `tools/run_local_backtest.py`

## 5. Out of Scope

- any `git commit`
- any `git push`
- deleting or overwriting old smoke or probe workspaces
- launching a new full Stage 2 run
- silently folding the long-standing zero-signal issue into the engineering speed-patch verdict

## 6. Required Audits

Math audit:

- Anchor: `audit/v64_audit_evolution.md`
- Responsibility: confirm that any future engineering-only remediation still leaves the approved V64.3 canonical math core untouched

Runtime audit:

- Responsibility: confirm rollback safety, fair smoke comparisons, and correct attribution of regressions versus long-standing baseline behavior

## 7. Runtime and Evidence Constraints

- Preserve these workspaces intact:
  - `/home/zepher/work/Omega_vNext_v643_smoke`
  - `/home/zepher/work/Omega_vNext_v643_speed_smoke`
  - `/home/zepher/work/Omega_vNext_v643_traincmp_smoke`
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke`
- Preserve both engineering routes intact in reasoning and release planning:
  - do not retire the old route
  - do not prematurely bless the speed route
- Keep the controller repo uncommitted for the engineering speed patch branch until the Owner explicitly authorizes release.
- New diagnosis runs must be isolated and must not overwrite existing evidence artifacts.

## 8. Acceptance Criteria

This mission reaches a stable checkpoint when all are true:

1. the engineering speed patch has been evaluated against fair smoke comparisons
2. the training slowdown has been correctly attributed to smoke harness drift rather than to the speed patch itself
3. the non-zero slice discovery effort and gate-chain diagnosis are fully recorded
4. the baseline smoke workspace has been checked directly, proving that the zero-signal condition predates the speed patch
5. `/handover` contains enough evidence for the Owner to split the next work into:
   - engineering release evaluation
   - long-standing zero-signal diagnosis

## 9. Stop Conditions

Stop and escalate if any of the following happens:

- a proposed remediation would require changing the approved V64.3 canonical runtime math core
- an engineering verdict attempts to treat the older baseline zero-signal condition as if it were introduced by the speed patch
- any step would overwrite preserved smoke or probe evidence
- a new code-change mission is needed before the Owner approves the next spec
