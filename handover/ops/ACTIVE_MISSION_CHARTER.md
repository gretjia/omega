# OMEGA Active Mission Charter

Status: Completed
Task Name: V64 Stage2 ordering-contract remediation, gate hardening, and speed-route validating smoke
Owner: Human Owner
Commander: Codex
Date: 2026-03-07

Current checkpoint:

- the historical `all-zero` collapse was traced to the Stage2 ETL -> kernel ordering contract, not to Stage1 raw parquet
- the remediation repaired ordering at the Stage2 -> kernel handoff and added fail-fast input gates on the main operational path
- the validating hot-week smoke on `linux1-lx` passed on the engineered-speed route:
  - `Stage 2 -> forge -> training -> backtest`
  - non-zero canonical chain proven
  - downstream consumability proven
- both the pre-speed route and the speed route remain preserved as evidence and rollback anchors
- the local tree is ready for `commit + push`

## 1. Objective

- Repair the Stage2 ordering-contract defect without changing the approved V64.3 canonical runtime math core.
- Add fail-fast input-contract gates so expensive downstream stages do not run on degenerate or malformed inputs.
- Validate on the engineered-speed route that the canonical signal chain is non-degenerate and consumable end-to-end.

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

- Eliminate the historical `all-zero` critical defect from the V64 runtime path.
- Prove that the approved V64.3 canonical chain can generate signal, direction, and non-zero topology/compression on a real contiguous hot-week input.
- Preserve both engineering routes so future release decisions can still compare old and new execution paths.

## 4. Files In Scope

Primary implementation scope:

- `omega_core/kernel.py`
- `tools/stage2_physics_compute.py`
- `tools/forge_base_matrix.py`
- `tools/run_vertex_xgb_train.py`
- `tools/run_local_backtest.py`
- `tests/test_v64_absolute_closure.py`
- `tests/test_v64_fastpath_equivalence.py`

Evidence scope:

- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/20260307_032337_v643_stage2_ordering_fix_speed_smoke_pass.md`
- `audit/v643_all_0_root_cause.md`
- `audit/v643_stage2_remediation_plan.md`
- `audit/v643_stage2_plan_audit.md`
- `audit/v643_stage2_code_audit.md`
- `audit/v643_stage2fix_speed_smoke_pass.md`

## 5. Out of Scope

- deleting or overwriting old smoke or probe workspaces
- launching a new full Stage 2 run
- changing the approved V64.3 canonical runtime math core

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

This mission is complete when all are true:

1. the Stage2 ordering-contract root cause is identified and repaired
2. fail-fast input gates exist on the main Stage2/forge/training/backtest path
3. a contiguous hot-week smoke proves non-zero canonical chain activation
4. `forge`, `training`, and `backtest` all consume the repaired non-degenerate inputs successfully
5. fixed memory and audit artifacts are updated for release

## 9. Completion Note

The mission has completed successfully. Remaining work, if any, is release administration (`commit/push`) or later-layer signal-quality analysis, not this root-cause remediation.
