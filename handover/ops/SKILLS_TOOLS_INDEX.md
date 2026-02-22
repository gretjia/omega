# Skills and Tools Index

This is the operational index for "what can be used directly now".

## 1) Executable Skills (Primary)

- `.codex/skills/multi-agent-ops/SKILL.md`
  - scripts:
    - `.codex/skills/multi-agent-ops/scripts/deploy_and_check.py`
    - `.codex/skills/multi-agent-ops/scripts/switch_profile.py`
    - `.codex/skills/multi-agent-ops/scripts/log_debug_experience.py`
- `.codex/skills/omega-run-ops/SKILL.md`
  - scripts:
    - `.codex/skills/omega-run-ops/scripts/ssh_ps.py`
- `.codex/skills/v60-multi-agent-ops/SKILL.md`
  - compatibility alias for `multi-agent-ops`.

## 2) Policy Templates (Secondary)

- `.agent/skills/*`
  - use as policy references.
  - do not treat as the main executable skill surface in this repository.

## 3) Operational Tools (Direct Use)

Multi-agent governance:

```bash
python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair
python3 .codex/skills/multi-agent-ops/scripts/switch_profile.py --oracle codex_xhigh --mechanic gemini_flash --auditor-primary gemini_pro --auditor-secondary codex_xhigh --debug-scribe codex_medium
```

Windows over SSH PowerShell:

```bash
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command 'hostname; whoami'
```

Linux direct:

```bash
ssh linux1-lx 'hostname; whoami; uptime'
```

## 4) Pipeline Entry Scripts

- Stage 1 Linux:
  - `tools/stage1_linux_base_etl.py`
- Stage 1 Windows:
  - `tools/stage1_windows_base_etl.py`
- Stage 2 physics:
  - `tools/stage2_physics_compute.py`
- Mac gateway upload:
  - `tools/mac_gateway_sync.py`
- Incident watchdog:
  - `tools/ai_incident_watchdog.py`

## 5) Recommended Startup Sequence for Any Agent

1. `bash tools/agent_handover_preflight.sh`
2. `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair`
3. Read `handover/ai-direct/LATEST.md`
4. Continue using skill-specific workflow docs.

