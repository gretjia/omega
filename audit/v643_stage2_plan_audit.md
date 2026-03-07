# V64 Stage2 Ordering-Contract Remediation Plan Audit

Date: 2026-03-07  
Author: Codex  
Status: dual-audited, approved for implementation

## Scope

Audited plan:

- [v643_stage2_remediation_plan.md](/home/zephryj/projects/omega/audit/v643_stage2_remediation_plan.md)

Mission class:

- critical-defect remediation
- Stage 2 ordering-contract repair
- input-contract gate hardening
- no Stage 1 recompute
- no canonical math changes

## Math auditor verdict

Verdict: `PASS`

Approval basis:

1. The plan preserves the approved V64.3 canonical runtime math core.
2. No formula changes are proposed for:
   - `Delta k = 0`
   - canonical SRL-relative compression
   - closed-area / closed-perimeter topology
   - `bits_srl` prohibition
   - `has_singularity` non-interference with `srl_resid`
3. The recommended repair only restores correct trajectory ordering before rolling computation.
4. The proposed gates are contract guards, not mathematical reinterpretations.

Math-audit conclusion:

- The plan is admissible because it repairs an ETL -> kernel interface defect without altering the approved mathematics.

## Engineering auditor verdict

Verdict: `PASS`

Approval basis:

1. The chosen implementation path (`Option C`) is the lowest-blast-radius repair.
2. Local reorder inside `kernel` is reversible and can be feature-flagged for rollback/A-B comparison.
3. Adding fail-fast gates at stage entrypoints directly addresses the proven validation defect: expensive stages currently accept semantically bad inputs too late.
4. The plan preserves both routes during diagnosis and keeps rollback intact.

Engineering-audit conclusion:

- The plan is safe to implement and correctly prioritizes minimal repair over global semantic churn.

## Approved implementation decision

Approved option:

- `Option C`

Meaning:

1. `kernel.py`
   - locally reorder frames into canonical rolling order before physics
   - restore original row order before returning
2. `Stage 2` entrypoint
   - add fail-fast input-contract gates
   - classify ordering defects as repairable vs non-repairable
3. downstream expensive stages
   - add minimal required-column / non-empty / contract gates before heavy work

## Guardrails

Implementation must not:

- modify Stage 1
- change canonical math formulas
- reintroduce secondary compression semantics
- bypass rollback capability

Implementation must:

- preserve output row order at the `kernel` API boundary
- fail fast on non-repairable inputs
- keep the repair scope as narrow as possible

## Next gate

Coding is approved.

After coding, the next mandatory gate is:

- post-code dual audit

No smoke planning or execution is authorized before code audit passes.
