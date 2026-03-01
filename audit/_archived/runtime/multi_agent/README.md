# Multi-Agent Runtime (Stable Path)

This folder is the canonical, version-agnostic runtime config root for multi-agent operation.
Guiding principles are anchored in `audit/v60_multi_agents.md`.

## Canonical Files

- `agent_profiles.yaml`: active model profiles and role routing.
- `recursive_audit_prompts.md`: shared recursive-audit prompt templates for independent auditors.

Default active policy:
- `oracle=codex_xhigh` (overall scheduling/planning/skill orchestration)
- `mechanic=gemini_flash` (code implementation)
- `debug_scribe=codex_medium` (debug lesson recording to `handover/DEBUG_LESSONS.md`)
- `auditor_primary=gemini_pro` + `auditor_secondary=codex_xhigh` (final dual audit)

## Operational Rules

1. Update canonical files here first.
2. Keep profile switches through:
   - `python3 .codex/skills/multi-agent-ops/scripts/switch_profile.py ...`
3. Validate setup through:
   - `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair`
   - Auto behavior: writes deduplicated debug lessons to `handover/DEBUG_LESSONS.md` when live context is valid.
   - Bypass only for troubleshooting: `--no-auto-debug-scribe`

## Compatibility

- Legacy path `audit/runtime/v60/` is maintained as compatibility mirror.
- New iterations must not introduce new versioned runtime roots for multi-agent control-plane files.
