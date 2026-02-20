---
name: v60-multi-agent-ops
description: Compatibility alias for legacy commands. Delegates to .codex/skills/multi-agent-ops (stable, version-agnostic path).
---

# v60 Multi-Agent Ops (Compatibility Alias)

Use the stable skill instead:
- `/Users/zephryj/work/Omega_vNext/.codex/skills/multi-agent-ops/SKILL.md`

Legacy commands remain supported via wrapper scripts:
- `python3 .codex/skills/v60-multi-agent-ops/scripts/deploy_and_check.py ...`
- `python3 .codex/skills/v60-multi-agent-ops/scripts/switch_profile.py ...`
- `python3 .codex/skills/v60-multi-agent-ops/scripts/log_debug_experience.py ...`

Behavior note:
- `deploy_and_check.py` now auto-appends deduplicated debug lessons from live context unless `--no-auto-debug-scribe` is set.

These wrappers forward to:
- `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py ...`
- `python3 .codex/skills/multi-agent-ops/scripts/switch_profile.py ...`
- `python3 .codex/skills/multi-agent-ops/scripts/log_debug_experience.py ...`
