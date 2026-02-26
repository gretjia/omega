# Handover Workspace (omega-vm Agent Gateway)

This folder is the standardized takeover gateway for all AI agents in Omega.

First file to read:
- `handover/ENTRYPOINT.md`

## 1. Design Goals

- One-file startup (`ENTRYPOINT.md`).
- One-file current truth (`ai-direct/LATEST.md`).
- Append-only history (`ai-direct/entries/*.md`).
- Split operational references by concern (topology, tools, credentials, logs, active projects).
- No secrets in repository handover docs.

Best-practice basis and sources:
- `handover/ops/HANDOVER_BEST_PRACTICES.md`

## 2. Folder Topology

```text
handover/
  ENTRYPOINT.md
  README.md
  DEBUG_LESSONS.md
  COSTLY_LESSONS.md

  ai-direct/
    README.md
    LATEST.md
    HANDOVER_TEMPLATE.md
    entries/*.md
    live/00..05_*.md

  ops/
    FILE_TOPOLOGY.md
    PROJECT_TOPOLOGY.md
    ACTIVE_PROJECTS.md
    SKILLS_TOOLS_INDEX.md
    ACCESS_BOOTSTRAP.md
    HOSTS_REGISTRY.yaml
    PIPELINE_LOGS.md
    SSH_NETWORK_SETUP.md
    HANDOVER_BEST_PRACTICES.md

  index/
    README.md
    memory_index.jsonl
    memory_index.sqlite3
    memory_index.sha1
```

## 3. Source-of-Truth Rules

- Current state: `handover/ai-direct/LATEST.md`
- Historical records: `handover/ai-direct/entries/*.md`
- Governance contract: `handover/ai-direct/live/01..05_*.md`
- Anti-regression memory: `handover/DEBUG_LESSONS.md`
- Generated index (read-only): `handover/index/*`

## 4. Required Workflow (Every Session)

1. Run startup preflight from `handover/ENTRYPOINT.md`.
2. Operate or debug.
3. Record one handover entry from template.
4. Update `handover/ai-direct/LATEST.md`.
5. Regenerate governance/memory check:
   - `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py`

## 5. Write Discipline

- Use factual, reproducible notes.
- Include exact commands and paths.
- Include verification timestamps.
- Never store secret material.

## 6. Stage2 Incident Entry Points

When the task is Stage2 monitoring/debug/recovery, start from these files:

1. `handover/ai-direct/entries/20260226_123046_stage2_multiround_incident_matrix_and_gapfill.md`
2. `handover/ai-direct/LATEST.md` (latest status board and action queue)
3. `handover/ops/PIPELINE_LOGS.md` (canonical logs, done-markers, fail/pending ledgers)

Purpose:
- Avoid re-diagnosing already fixed failure classes.
- Use consistent metric semantics (`FAILED_TOTAL`, `RUN_FAILED`, `DEFER not-started`).
- Keep all new Stage2 incidents appended under `handover/ai-direct/entries/`.
