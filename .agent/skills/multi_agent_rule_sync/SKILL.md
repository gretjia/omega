---
name: multi_agent_rule_sync
description: Keep Codex, Gemini, Trae, and Cursor rules synchronized from a single source of truth.
---

# Multi-Agent Rule Sync

Use this skill when changing cross-agent rules, core path definitions, or governance principles.

## Single Source of Truth

- Source: `.agent/principles.yaml`
- Generated targets:
  - `.codex/rules.md`
  - `.gemini/context.md`
  - `.trae/instruction.md`
  - `.cursorrules`

Do not manually edit generated targets unless there is an emergency hotfix.

## Mandatory Workflow

1. Edit only `.agent/principles.yaml`.
2. Sync:
   - `python3 tools/sync_agent_rules.py`
3. Validate:
   - `python3 tools/sync_agent_rules.py --check`
4. Confirm targets contain the auto-generated header and no drift remains.
5. Record changes in handover/audit notes when behavior changes.

## Failure Handling

- If sync fails due permission errors on hidden files, rerun the same command with elevated permission.
- If target format is changed, update `tools/sync_agent_rules.py` and re-sync immediately.
