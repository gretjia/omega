# Handover First Entrypoint (Multi-Agent)

This file is the single first entry for any AI agent taking over work in this repo.

## 0) Mandatory Order (Do Not Skip)

1. Read `audit/constitution_v2.md` (immutable, highest authority).
2. Read this file: `handover/ENTRYPOINT.md`.
3. Read latest runtime truth: `handover/ai-direct/LATEST.md`.
4. Run memory/index sync:
   - `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair`
5. Read:
   - `handover/ai-direct/live/00_Lesson_Recall.md`
   - newest note in `handover/ai-direct/entries/`

## 1) Why This Exists

Problem observed: agents can execute code but fail to locate operational context quickly (host aliases, SSH access assumptions, skill entrypoints, live handoff contract).

This entrypoint normalizes that into one place.

## 2) Fast Preflight (60 Seconds)

Run:

```bash
bash tools/agent_handover_preflight.sh
```

If preflight reports missing SSH aliases, use:
- `handover/ops/ACCESS_BOOTSTRAP.md`

## 3) Canonical Map

- File topology:
  - `handover/ops/FILE_TOPOLOGY.md`
- Skill + tool index:
  - `handover/ops/SKILLS_TOOLS_INDEX.md`
- Access + credentials bootstrap:
  - `handover/ops/ACCESS_BOOTSTRAP.md`
- Non-secret host registry:
  - `handover/ops/HOSTS_REGISTRY.yaml`

## 4) SSH Credentials Discovery Order

Credentials are intentionally not stored in `handover/` or git-tracked files.

Use this resolution order:

1. `~/.ssh/config` for aliases:
   - `windows1-w1`
   - `linux1-lx`
2. If alias missing, use direct targets from `handover/ops/HOSTS_REGISTRY.yaml`.
3. If key login fails, bootstrap from:
   - `audit/20260212_mac_ssh_handover.md`
   - `audit/20260212_windows_ssh_handover.md`
   - `tools/setup_linux_ssh.ps1`

Security rule:
- Never write passwords/private keys into `handover/` files.
- Only store connection metadata (host/ip/user/path), never secrets.

## 5) Directly Usable Tools (Project-Level)

Core executable skills:
- `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair`
- `python3 .codex/skills/multi-agent-ops/scripts/switch_profile.py ...`
- `python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '...'`

Core runtime scripts:
- `tools/stage1_linux_base_etl.py`
- `tools/stage1_windows_base_etl.py`
- `tools/stage2_physics_compute.py`
- `tools/mac_gateway_sync.py`
- `tools/ai_incident_watchdog.py`

Full matrix:
- `handover/ops/SKILLS_TOOLS_INDEX.md`

## 6) Multi-Agent Live Contract

For oracle/mechanic/auditor pipeline, keep handoff in:
- `handover/ai-direct/live/01_Raw_Context.md`
- `handover/ai-direct/live/02_Oracle_Insight.md`
- `handover/ai-direct/live/03_Mechanic_Patch.md`
- `handover/ai-direct/live/04A_Gemini_Recursive_Audit.md`
- `handover/ai-direct/live/04B_Codex_Recursive_Audit.md`
- `handover/ai-direct/live/05_Final_Audit_Decision.md`

Each file must include:
- `task_id`
- `git_hash`
- `timestamp_utc`

## 7) External Best-Practice Baseline

OpenAI official:
- [Building agents](https://platform.openai.com/docs/guides/agents)
- [Tools](https://platform.openai.com/docs/guides/tools)
- [Model Context Protocol (MCP)](https://platform.openai.com/docs/guides/mcp)
- [Conversation state](https://platform.openai.com/docs/guides/conversation-state)

Internet/industry:
- [12-Factor App - Config](https://12factor.net/config)
- [Kubernetes Secrets good practices](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Model Context Protocol specification](https://modelcontextprotocol.io/specification/2025-06-18)
- [GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

