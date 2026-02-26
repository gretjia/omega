---
name: ai_handover
description: Protocol for AI session handover to ensure continuity across agents and sessions.
---

# Skill: ai_handover

## When To Use

- Ending a session that has unfinished work
- Starting a new session and need to pick up where the last agent left off
- When explicitly asked to do `/handover`

## Handover File Hierarchy

```
handover/ENTRYPOINT.md          ← Start here (project state overview)
handover/ai-direct/LATEST.md    ← Runtime status snapshot
handover/ai-direct/entries/     ← Chronological session entries
handover/DEBUG_LESSONS.md       ← Searchable debug database
handover/COSTLY_LESSONS.md      ← Expensive mistakes (read before cloud jobs)
handover/ops/HOSTS_REGISTRY.yaml ← Network/node definitions
```

## When Ending a Session

1. Write a session entry to `handover/ai-direct/entries/` with format:
   `YYYYMMDD_HHMMSS_<short_topic>.md`
2. Include:
   - What was accomplished
   - What blockers remain
   - Current node status (git hashes, active processes)
   - What the next agent should do first
3. Update `handover/ai-direct/LATEST.md` with current state

## When Starting a Session

1. Read `handover/ENTRYPOINT.md` for project context
2. Read `handover/ai-direct/LATEST.md` for last known state
3. Check `handover/DEBUG_LESSONS.md` if debugging
4. Run `python3 tools/cluster_health.py --quick` for live status
5. Check current git state: `git log --oneline -5 && git status`

## Anti-Patterns

- ❌ Starting fresh analysis when the last agent already solved the problem
- ❌ Not reading COSTLY_LESSONS.md before launching cloud jobs
- ❌ Assuming node state without checking `cluster_health.py`
- ❌ Writing to vendor-specific files (gemini.md, CLAUDE.md) instead of AGENTS.md
