---
name: multi_agent_rule_sync
description: Governance policy skill for syncing multi-agent rules. For executable deployment/switch operations, delegate to .codex/skills/multi-agent-ops.
---

# Skill: multi_agent_rule_sync

## Intent
- Keep cross-agent governance consistent.
- Prevent policy drift between Constitution, AGENTS.md, and runtime profile config.

## Execution Boundary
- This skill is policy-level.
- Do not treat this file as executable runbook.
- Use `/Users/zephryj/work/Omega_vNext/.codex/skills/multi-agent-ops/SKILL.md` for deploy/check/switch actions.
- Keep `/Users/zephryj/work/Omega_vNext/audit/v60_multi_agents.md` as guiding-principle baseline.

## Required Checks
1. `/Users/zephryj/work/Omega_vNext/AGENTS.md` exists and routes operations to codex executable skills.
2. `/Users/zephryj/work/Omega_vNext/.agent/principles.yaml` core paths match real repository structure.
3. `/Users/zephryj/work/Omega_vNext/audit/runtime/multi_agent/agent_profiles.yaml` role/profile map is valid.
4. `/Users/zephryj/work/Omega_vNext/audit/v60_multi_agents.md` remains the principle source.
5. `/Users/zephryj/work/Omega_vNext/handover/DEBUG_LESSONS.md` exists as debug memory ledger.

## Standard Delegation
- Run:
```bash
python3 /Users/zephryj/work/Omega_vNext/.codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair
```
`deploy_and_check.py` auto-appends a deduplicated entry to `/Users/zephryj/work/Omega_vNext/handover/DEBUG_LESSONS.md` when live context is valid.
- Emergency bypass:
```bash
python3 /Users/zephryj/work/Omega_vNext/.codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair --no-auto-debug-scribe
```
- Optional profile switch:
```bash
python3 /Users/zephryj/work/Omega_vNext/.codex/skills/multi-agent-ops/scripts/switch_profile.py --oracle codex_xhigh --mechanic gemini_flash --auditor-primary gemini_pro --auditor-secondary codex_xhigh --debug-scribe codex_medium
```

- Optional debug lesson append:
```bash
python3 /Users/zephryj/work/Omega_vNext/.codex/skills/multi-agent-ops/scripts/log_debug_experience.py --title "example_issue" --task-id "TASK-000" --git-hash "abc1234" --symptom "what failed" --root-cause "why it failed" --fix "what changed" --guardrail "how recurrence is blocked" --refs "path/to/file.py,python3 tools/example.py --smoke"
```
