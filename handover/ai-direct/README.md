# AI Direct-Read Guide

## Purpose

This folder is designed for fast resume when:

- a new AI takes over;
- the same AI loses context and needs to continue safely.

## 30-Second Resume Steps

1. Read `LATEST.md` to get current objective, blockers, and next action.
2. Read the newest file under `entries/` for operation details.
3. Run the quick verification commands in `LATEST.md`.
4. Continue only after verifying machine reachability and run status.

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
