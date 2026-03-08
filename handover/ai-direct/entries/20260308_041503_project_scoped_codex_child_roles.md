# 2026-03-08 04:15 UTC — Project-scoped Codex child-role integration

## Summary

OMEGA child-agent governance has been split into:

- human-readable governance
- CLI-consumed role configuration

The goal is to let Codex CLI use OMEGA-specific child roles without polluting global user configuration.

## What changed

### Human-readable governance source

- `handover/ops/CHILD_AGENT_OPERATING_PROFILE.md`

This remains the canonical explanation of:

- authority limits
- delegation packet requirements
- role contracts
- stop conditions
- Commander-only integration authority

### Codex CLI project-scoped configuration

- `.codex/config.toml`
- `.codex/agents/omega_plan.toml`
- `.codex/agents/omega_coder.toml`
- `.codex/agents/omega_math_auditor.toml`
- `.codex/agents/omega_runtime_auditor.toml`
- `.codex/agents/omega_runtime_watcher.toml`

These files define OMEGA-only child roles through the documented multi-agent configuration path.

## Governance rule

OMEGA-specific child roles must not be added to:

- `~/.codex/config.toml`

Reason:

- OMEGA math and runtime roles are project-specific
- they should not alter Codex behavior in unrelated repositories

## Entry-point updates

The following entry documents now point agents to the project-scoped child-role path:

- `AGENTS.md`
- `handover/README.md`
- `handover/ai-direct/LATEST.md`

## Operational interpretation

If a Codex CLI session inside OMEGA will use child roles, the expected reading and configuration chain is:

1. `AGENTS.md`
2. `handover/README.md`
3. `handover/ops/CHILD_AGENT_OPERATING_PROFILE.md`
4. `.codex/config.toml`
5. `.codex/agents/*.toml`

This preserves:

- repo-local specialization
- global Codex neutrality
- auditable role behavior
