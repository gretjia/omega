# OMEGA Multi-Agents Guiding Principles (v60 Baseline)

This document is the principle baseline for multi-agent architecture decisions.
It remains valid across `v6.x+` and is intentionally kept as a stable guidance reference.

## P1. Human Final Authority
- Human is the only final merge authority.
- Agents may propose, implement, and audit; they do not auto-merge.

## P2. Single Writer Discipline
- Only one writer role may modify workspace per task window.
- All other agents remain read-only for that window.

## P3. Markdown Handoff Bus
- Inter-agent relay is text-first and explicit through handoff files.
- Handoff state must be inspectable without proprietary tools.

## P4. Dual Independent Recursive Audit
- At least two independent auditors.
- Both must reason from first principles first, then implementation.
- Recursive depth minimum 2 (direct defect -> second-order impact).
- Auditors must not read each other's result before finalizing.

## P5. Constitution Anchoring
- Audit and implementation must map to:
  - `OMEGA_CONSTITUTION.md`
  - repository baseline engineering constraints
  - reproducibility and role-isolation rules

## P6. Stable Paths Over Version Paths
- Canonical multi-agent files must be version-agnostic.
- Versioned paths may exist only as compatibility aliases.

## P7. Hot-Switch Capability
- Model profiles must be switchable without workflow rewrite.
- Required switch examples:
  - Gemini: Pro <-> Flash
  - Codex: xhigh <-> medium reasoning effort

## P8. Backward Compatibility
- Legacy commands should not hard-fail after upgrades.
- Compatibility wrappers/aliases are allowed and should forward to canonical paths.

## P9. Minimal Automation
- Prefer deterministic, stoppable scripts.
- Avoid hidden queues/lock managers unless operationally necessary.

## P10. Continuous Evolution Rule
- Future iterations update canonical files in place.
- New architecture ideas must satisfy P1-P9 before adoption.
