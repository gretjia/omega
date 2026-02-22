# Handover File Topology

This document is the compact map for where each type of multi-agent context lives.

## A) Required Reading Flow

1. `audit/constitution_v2.md`
2. `handover/ENTRYPOINT.md`
3. `handover/ai-direct/LATEST.md`
4. latest file in `handover/ai-direct/entries/`
5. `handover/ai-direct/live/00_Lesson_Recall.md`

## B) Directory Responsibilities

- `handover/ai-direct/LATEST.md`
  - single source of current truth (mission, status, next actions).
- `handover/ai-direct/entries/*.md`
  - append-only operational notes, timestamped.
- `handover/ai-direct/live/01..05_*.md`
  - cross-agent contract bus (oracle -> mechanic -> dual auditors -> final human decision).
- `handover/DEBUG_LESSONS.md`
  - anti-regression memory ledger (auto-maintained by `deploy_and_check.py`).
- `handover/COSTLY_LESSONS.md`
  - expensive-failure prevention ledger.
- `handover/index/memory_index.jsonl`
  - searchable memory index (generated).
- `handover/index/memory_index.sqlite3`
  - SQL memory index (generated).

## C) Governance and Profiles

- `audit/multi_agents.md`
  - canonical multi-agent architecture and role contract.
- `audit/runtime/multi_agent/agent_profiles.yaml`
  - active profile routing and hot-switch source.
- `.agent/principles.yaml`
  - cross-agent principle baseline.

## D) Skills and Execution

- `.codex/skills/multi-agent-ops/SKILL.md`
  - multi-agent deployment/check/governance operations.
- `.codex/skills/omega-run-ops/SKILL.md`
  - Windows/Linux distributed run operations.
- `.agent/skills/*`
  - mostly policy templates (not primary executable workflows in this repo).

