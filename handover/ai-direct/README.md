# AI Direct Guide

This folder is the runtime handoff surface for agent-to-agent continuation.

## 1. Read Order

1. `handover/ENTRYPOINT.md`
2. `handover/ai-direct/LATEST.md`
3. newest file in `handover/ai-direct/entries/`
4. `handover/ai-direct/live/00_Lesson_Recall.md`
5. `handover/ai-direct/live/01..05_*.md` (only for multi-agent gate flow)

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

