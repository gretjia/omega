# V64 Stage2 Ordering-Contract Remediation Code Audit

Date: 2026-03-07  
Author: Codex  
Status: dual-audited, code approved for smoke-spec drafting

## Scope audited

Implementation files:

- [kernel.py](/home/zephryj/projects/omega/omega_core/kernel.py)
- [stage2_physics_compute.py](/home/zephryj/projects/omega/tools/stage2_physics_compute.py)
- [forge_base_matrix.py](/home/zephryj/projects/omega/tools/forge_base_matrix.py)
- [run_vertex_xgb_train.py](/home/zephryj/projects/omega/tools/run_vertex_xgb_train.py)
- [run_local_backtest.py](/home/zephryj/projects/omega/tools/run_local_backtest.py)
- [test_v64_absolute_closure.py](/home/zephryj/projects/omega/tests/test_v64_absolute_closure.py)
- [test_v64_fastpath_equivalence.py](/home/zephryj/projects/omega/tests/test_v64_fastpath_equivalence.py)

Plan gates:

- [v643_stage2_remediation_plan.md](/home/zephryj/projects/omega/audit/v643_stage2_remediation_plan.md)
- [v643_stage2_plan_audit.md](/home/zephryj/projects/omega/audit/v643_stage2_plan_audit.md)

## Math auditor result

Verdict: `PASS`

Conclusion:

1. The patch preserves the approved V64.3 canonical runtime math core.
2. `kernel` local reordering restores correct trajectory semantics without changing any canonical formulas.
3. The added gates are contract guards and do not introduce a new mathematical interpretation.
4. Explicit rollback/off-path tests improve validation without changing semantics.

Math-audit bottom line:

- code is mathematically safe for smoke validation.

## Engineering auditor result

Verdict: `PASS`

Conclusion:

1. The implementation remains inside the approved remediation boundary.
2. Stage 2 now hard-fails duplicate symbol partition defects on both the normal and isolated subprocess paths.
3. `kernel` now refuses ambiguous multisymbol/multidate frames that cannot be deterministically reordered.
4. Input-contract gates now fail early for:
   - Stage 2 raw/input-feature contracts
   - forge L2 contracts
   - training base-matrix contracts
   - backtest frame contracts
5. No remaining hard engineering blockers were identified for this fix slice.

Engineering-audit bottom line:

- code is operationally admissible for targeted smoke planning.

## Implementation summary

### 1. Root-cause repair

`kernel.py` now performs a local internal reorder by:

- `symbol`
- `date`
- `time_end` or fallback `bucket_id`
- original row index as tie-breaker

Then restores original row order before returning.

This repairs the proven ETL -> kernel ordering-contract defect without changing the public row-order contract.

### 2. Stage 2 fail-fast hardening

`stage2_physics_compute.py` now:

- rejects raw inputs missing the identity/time keys needed by Stage 2
- audits feature-frame ordering/window feasibility before physics
- treats repairable ordering violations as admissible only when kernel reorder is enabled
- hard-fails duplicate symbol partition defects in both normal and isolated paths

### 3. Downstream fail-fast hardening

`forge_base_matrix.py`, `run_vertex_xgb_train.py`, and `run_local_backtest.py` now reject degenerate canonical signal chains before expensive downstream work proceeds.

### 4. Regression coverage added

Tests now cover:

- kernel repair of interleaved symbol order while preserving original output order
- explicit rollback mode via `OMEGA_STAGE2_FIX_KERNEL_ORDERING=0`
- hard failure on ambiguous multi-symbol/no-time-key kernel inputs
- Stage 2 feature-contract ordering/window gates
- training/backtest degenerate all-zero input gates

## Current gate state

Allowed next step:

- draft smoke spec and get Owner confirmation

Not yet done:

- no smoke executed in this mission
- no `git commit`
- no `git push`
