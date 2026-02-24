# Agent Entrypoint (Canonical)

This is the first file every AI agent must read before any planning, coding, or operations task.

## 0. Non-Negotiable Order

1. Read `audit/constitution_v2.md` once.
2. Read `audit/multi_agents.md`.
3. Read `handover/ENTRYPOINT.md` (this file).
4. Read `handover/ai-direct/LATEST.md` (authoritative current state).
5. Run:
   - `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair`
6. Read:
   - `handover/ai-direct/live/00_Lesson_Recall.md`
   - newest file in `handover/ai-direct/entries/`

## 1. What This Folder Guarantees

- A single operational entry for takeover on `omega-vm`.
- A strict, repeatable handover format for all agents.
- Fast location of topology, tools, credentials, logs, and active projects.
- A single current-state board in `handover/ai-direct/LATEST.md`.

## 2. 90-Second Startup Checklist

```bash
bash tools/agent_handover_preflight.sh
python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair
```

If SSH alias or key checks fail, use:
- `handover/ops/ACCESS_BOOTSTRAP.md`
- `handover/ops/HOSTS_REGISTRY.yaml`

## 3. Canonical Maps

- Folder topology: `handover/ops/FILE_TOPOLOGY.md`
- Project topology: `handover/ops/PROJECT_TOPOLOGY.md`
- Active projects board: `handover/ops/ACTIVE_PROJECTS.md`
- Skills and tools index: `handover/ops/SKILLS_TOOLS_INDEX.md`
- Credentials and access policy: `handover/ops/ACCESS_BOOTSTRAP.md`
- Hosts registry (non-secret): `handover/ops/HOSTS_REGISTRY.yaml`
- Pipeline logs and stage supervision: `handover/ops/PIPELINE_LOGS.md`
- omega-vm network/SSH reference: `handover/ops/SSH_NETWORK_SETUP.md`

## 4. LATEST.md Contract

`handover/ai-direct/LATEST.md` is the single source of truth for all agents.

Rules:
- Keep only current truth and immediate next actions.
- Put historical details in `handover/ai-direct/entries/*.md`.
- Every operational session must update `LATEST.md` before handoff.

## 5. Secrets Policy

- Never store secrets, passwords, private keys, tokens, or raw credential contents in git-tracked files.
- Only store credential *locations*, bootstrap steps, and validation commands.
- Keep all sensitive data in secure local stores (`~/.ssh`, OS keychain, cloud secret manager).

## 6. Session-End Required Outputs

1. Create one timestamped entry from `handover/ai-direct/HANDOVER_TEMPLATE.md`.
2. Update `handover/ai-direct/LATEST.md`.
3. If topology/tools/credential paths changed, update matching files under `handover/ops/`.
4. Keep handoff references concrete: host alias, absolute path, git hash, run ID, exact command.

