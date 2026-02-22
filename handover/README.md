# Handover Workspace

This is the canonical handover folder for AI session continuation.
Unified first entry for all agents:
- `ENTRYPOINT.md`

## Directory Layout

- `ENTRYPOINT.md`: single first entry for multi-agent takeover.
- `ai-direct/README.md`: AI quick-start instructions.
- `ai-direct/LATEST.md`: single source of latest status.
- `ai-direct/HANDOVER_TEMPLATE.md`: required template for each new handover note.
- `ai-direct/entries/*.md`: timestamped handover records.
- `ops/FILE_TOPOLOGY.md`: file topology and role map.
- `ops/SKILLS_TOOLS_INDEX.md`: executable skills and direct tools index.
- `ops/ACCESS_BOOTSTRAP.md`: SSH/credential bootstrap policy and commands.
- `ops/HOSTS_REGISTRY.yaml`: non-secret host metadata registry.
- `DEBUG_LESSONS.md`: cross-agent debug memory ledger for anti-regression lessons.
  - Maintained automatically by `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py`.
- `COSTLY_LESSONS.md`: **CRITICAL**. Read this to avoid burning money on failed cloud jobs.
- `V60_PRE_SUBMIT_CHECKLIST.md`: hard pre-launch gate for v60 cloud submissions.
- `index/memory_index.jsonl`: derived read-only memory index over `entries + DEBUG_LESSONS`.
- `index/memory_index.sqlite3`: same index in SQLite for fast filtered queries.
- `ai-direct/live/01_Raw_Context.md`: multi-agent raw task context.
- `ai-direct/live/02_Oracle_Insight.md`: oracle output.
- `ai-direct/live/03_Mechanic_Patch.md`: mechanic output.
- `ai-direct/live/04A_Gemini_Recursive_Audit.md`: independent auditor A output.
- `ai-direct/live/04B_Codex_Recursive_Audit.md`: independent auditor B output.
- `ai-direct/live/05_Final_Audit_Decision.md`: human final decision record.
- `ai-direct/live/00_Lesson_Recall.md`: auto-generated Top-K historical lesson recall for current task context.

## Required Workflow

1. On takeover (new AI or context loss), read `ENTRYPOINT.md`.
2. Read `ai-direct/LATEST.md`.
3. Read the newest file in `ai-direct/entries/`.
4. **CRITICAL:** Read `COSTLY_LESSONS.md` to avoid financial waste.
5. Run `bash tools/agent_handover_preflight.sh`.
6. Run `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py` to sync index + generate recall.
7. Read `ai-direct/live/00_Lesson_Recall.md` before implementation/debug to avoid repeated failures.
8. If task uses multi-agent flow, read `ai-direct/live/01..05_*.md` in order.
9. Read `DEBUG_LESSONS.md` when deeper historical detail is needed.
10. Before ending a work session, create a new entry from template.
11. Update `ai-direct/LATEST.md` to reflect the newest truth.

## AI Debug Agent Configuration

**IMPORTANT:** For automated debugging (watchdogs, CI bots), always use `gemini -y`.

- **Reason:** `gemini -y` provides full shell and network access (e.g., `gcloud logging`, internet access), which is required for diagnosing cloud-native failures (OOM, Quota, API errors) that are not visible in local logs.
- **Legacy:** Do NOT use `codex exec` for cloud infrastructure debugging as it may be sandboxed/restricted.

## Naming Rules

- Entry file name: `YYYYMMDD_HHMMSS_short_topic.md`
- Timestamp should include timezone in file body, for example `+0800`.

## Legacy Note

- Older notes may exist in `handovrt/`.
- New notes must be written to `handover/ai-direct/entries/`.
