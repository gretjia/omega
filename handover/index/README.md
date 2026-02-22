# Handover Memory Index (Derived, Read-Only)

This folder stores derived indexes generated from handover truth sources.

## Source of Truth

- `handover/ai-direct/entries/*.md`
- `handover/DEBUG_LESSONS.md`

## Derived Artifacts

- `memory_index.jsonl`: line-delimited structured records for grep/script workflows.
- `memory_index.sqlite3`: same records in SQLite for filtered queries.
- `memory_index.sha1`: deterministic content digest used for no-op rebuild detection.

## Regeneration

```bash
python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py
```

## Rule

Never edit files in this folder by hand. Update truth sources and regenerate.
