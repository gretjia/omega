# Handover File Topology (Canonical)

This is the authoritative map of the `handover/` folder.

## 1. Read-First Flow

1. `audit/constitution_v2.md`
2. `audit/_archived/multi_agents.md`
3. `handover/ENTRYPOINT.md`
4. `handover/ai-direct/LATEST.md`
5. newest `handover/ai-direct/entries/*.md`
6. `handover/ai-direct/live/00_Lesson_Recall.md`

## 2. Topology by Responsibility

| Path | Responsibility | Write Policy |
|---|---|---|
| `handover/ENTRYPOINT.md` | Global startup gate for every agent | Update when startup protocol changes |
| `handover/README.md` | Handover architecture overview | Update on topology changes |
| `handover/DEBUG_LESSONS.md` | Cross-session anti-regression memory | Auto-maintained by tooling; manual append allowed |
| `handover/COSTLY_LESSONS.md` | Costly failure prevention memory | Manual update on expensive incidents |
| `handover/ai-direct/LATEST.md` | Single current-state truth | Must be updated each session |
| `handover/ai-direct/HANDOVER_TEMPLATE.md` | Required entry format | Change only with governance agreement |
| `handover/ai-direct/entries/*.md` | Append-only historical handoff records | Add new files only, no rewrite of old facts |
| `handover/ai-direct/live/01..05_*.md` | Multi-agent gate artifacts | Update per current task only |
| `handover/ops/PROJECT_TOPOLOGY.md` | Repository + pipeline topology | Update when architecture changes |
| `handover/ops/ACTIVE_PROJECTS.md` | In-flight projects board | Update on status changes |
| `handover/ops/SKILLS_TOOLS_INDEX.md` | Usable scripts/skills and command entrypoints | Update when tooling changes |
| `handover/ops/ACCESS_BOOTSTRAP.md` | Credential locations, SSH bootstrap, secret policy | Update when access patterns change |
| `handover/ops/HOSTS_REGISTRY.yaml` | Non-secret host metadata | Update on host/IP/path changes |
| `handover/ops/PIPELINE_LOGS.md` | Log paths and monitoring commands | Update when log/output locations change |
| `handover/ops/SSH_NETWORK_SETUP.md` | omega-vm networking and SSH topology | Update on network/key policy changes |
| `handover/ops/HANDOVER_BEST_PRACTICES.md` | External best-practice rationale and standards | Update when framework changes |
| `handover/index/*` | Derived memory indexes | Generated only, do not edit manually |

## 3. Project Governance Anchors

- Constitution: `audit/constitution_v2.md`
- Multi-agent contract: `audit/_archived/multi_agents.md`
- Runtime profile routing: `audit/runtime/multi_agent/agent_profiles.yaml`
- Cross-agent principles: `.agent/principles.yaml`

## 4. Hard Rules

- No secrets in `handover/`.
- `LATEST.md` must stay short and current.
- Historical detail belongs in `entries/`.
- Derived `handover/index/*` is read-only.

