---
name: config_promotion_protocol
description: Govern promotion of train/test-discovered parameters into config.py with audit evidence, approval gates, and reproducibility guarantees.
---

# Config Promotion Protocol

Use this skill when someone proposes moving discovered parameters from experiments or artifacts into `config.py`.

## Core Principle

- `config.py` is baseline configuration, not a runtime write target.
- Promotion into `config.py` is allowed only as an audited, explicit governance action.

## Promotion Gates (all required)

1. Evidence:
   - baseline vs candidate metrics are documented
   - data window and evaluation method are documented
2. Reproducibility:
   - candidate values exist in a versioned artifact snapshot
   - exact commands/config used for discovery are recorded
3. Risk review:
   - no violation of T+1, boundary, or volume-clock constraints
   - no hidden hardcoded thresholds left outside config/artifact loading
4. Approval:
   - explicit user approval before editing `config.py`

## Mandatory Workflow

1. Create a proposal note in `audit/`, for example:
   - `audit/vXXXX_config_promotion.md`
2. Include:
   - fields to promote
   - current value, proposed value, rationale
   - baseline and candidate metrics
   - rollback plan
3. Keep discovered values in artifacts first.
4. After approval, patch `config.py` in one focused change.
5. Update handover with:
   - promoted fields
   - evidence path
   - affected modules

## Prohibited

- Writing to `config.py` during training/backtest runtime.
- Promoting parameters without audit evidence and explicit approval.
