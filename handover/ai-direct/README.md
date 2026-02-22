# AI Direct-Read Guide

## Purpose

This folder is designed for fast resume when:

- a new AI takes over;
- the same AI loses context and needs to continue safely.

## 30-Second Resume Steps

1. Read `LATEST.md` to get current objective, blockers, and next action.
2. Read the newest file under `entries/` for operation details.
3. Run `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py` to sync memory index and generate pre-task recall.
4. Read `live/00_Lesson_Recall.md` first (Top-K by task_id/keywords/components).
5. For multi-agent tasks, read `live/01_Raw_Context.md` -> `live/05_Final_Audit_Decision.md` in order.
6. Read `../DEBUG_LESSONS.md` for full historical detail if needed.
7. Run the quick verification commands in `LATEST.md`.
8. Continue only after verifying machine reachability and run status.

## Session-End Rules

1. Create a new note in `entries/` using `HANDOVER_TEMPLATE.md`.
2. Update `LATEST.md` with:
   - latest timestamp;
   - what is done;
   - what is pending;
   - exact next command(s).
3. Keep references concrete (paths, host aliases, commit hashes, run IDs).

## Scope Discipline

- Put only operational facts and reproducible commands here.
- Do not store secrets, passwords, or private keys.
- In `live/` files, always include `task_id`, `git_hash`, `timestamp_utc`.
