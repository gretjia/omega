---
name: innovation_sandbox
description: Enable high-freedom strategy experimentation in isolated sandbox paths while enforcing strict gates before promotion to mainline.
---

# Innovation Sandbox

Use this skill when exploring new ideas, model heuristics, or architecture experiments that are not yet production-ready.

## Objective

Preserve creative freedom without contaminating mainline.

## Sandbox Boundary

- Allowed sandbox locations:
  - `archive/`
  - `jobs/`
  - ad-hoc drivers under `tools/`
- Mainline protected paths:
  - `omega_v3_core/*`
  - `config.py`
  - generated rule files (`.codex/rules.md`, `.gemini/context.md`, `.trae/instruction.md`, `.cursorrules`)

Rule:
- Fast prototypes can use temporary simplifications in sandbox files.
- Production paths cannot absorb those simplifications directly.

## Mandatory Workflow

1. Hypothesis first:
   - write one-sentence hypothesis and success metric.
2. Isolated implementation:
   - keep prototype code outside protected mainline paths.
3. Evidence capture:
   - record commands, dataset window, metrics, and artifacts.
4. Decision:
   - promote, iterate, or discard.
5. Promotion (if selected):
   - pass `hardcode_guard`
   - pass `config_promotion_protocol` if config fields change
   - then merge into `omega_v3_core/*`

## Quick Checklist

- [ ] Prototype code is isolated from mainline.
- [ ] Metrics and evidence are stored under `audit/` or artifacts.
- [ ] Promotion path and rollback are defined before merge.
