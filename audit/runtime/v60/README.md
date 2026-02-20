# Compatibility Runtime Alias (v60)

This folder is kept for backward compatibility with legacy commands.

Canonical runtime root:
- `audit/runtime/multi_agent/`
- default includes `debug_scribe=codex_medium` and `handover/DEBUG_LESSONS.md` ledger.

Do not treat `audit/runtime/v60/` as the primary source for new iterations.
Use stable scripts under:
- `.codex/skills/multi-agent-ops/scripts/`
- `deploy_and_check.py` in stable scripts auto-appends debug lessons unless `--no-auto-debug-scribe` is set.
