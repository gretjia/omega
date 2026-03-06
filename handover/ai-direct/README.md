# AI Direct Guide

This folder is the runtime handoff surface for agent-to-agent continuation.

If you land here directly, still follow `handover/README.md` as the unified entrypoint and read `OMEGA_CONSTITUTION.md` before proceeding.

## 1. Read Order

1. `handover/README.md`
2. `handover/ai-direct/LATEST.md`
3. newest file in `handover/ai-direct/entries/`
4. `handover/ai-direct/live/00_Lesson_Recall.md`
5. `handover/ai-direct/live/01..05_*.md` (only for multi-agent gate flow)

`handover/ENTRYPOINT.md` is now a compatibility shim only.

## 2. File Roles

- `LATEST.md`: single current truth for all agents.
- `HANDOVER_TEMPLATE.md`: mandatory format for each new entry.
- `entries/*.md`: append-only session records.
- `live/01..05_*.md`: oracle/mechanic/auditor gate artifacts.

## 3. Update Rules

- At session start: read `LATEST.md` and latest `entries` note.
- At session end:
  - create one new `entries/*.md` file from template
  - update `LATEST.md`
- Keep `LATEST.md` short and current. Move detailed history to `entries/`.

The authoritative governance and routing live in:

- `handover/README.md`
- `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`
- active mission charter under `handover/ops/`

## 4. Naming Rule for Entries

`YYYYMMDD_HHMMSS_short_topic.md`

Example:
`20260224_131500_stage2_windows_eta_update.md`

## 5. Mandatory Fields (Per Entry)

- `task_id`
- `timestamp_local`
- `timestamp_utc`
- `operator`
- `git_head`
- `hosts_touched`
- `summary`
- `next_actions`

## 5. Current Mission Quick Entry

Use the current mission and runtime truth, not historical v63 artifacts:

- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ai-direct/LATEST.md`
- newest file in `handover/ai-direct/entries/`

