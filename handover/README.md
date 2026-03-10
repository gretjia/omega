# OMEGA Unified Agent Entry and Handover Manual

> **This is the unified entrypoint under `/handover` for all OMEGA agent work.**
> It consolidates onboarding, governance routing, runtime state, and handover discipline.
> `handover/ENTRYPOINT.md` now exists only as a compatibility shim.

## 1. Reading Order (unified)

```
1. This file                                   → unified entrypoint
2. OMEGA_CONSTITUTION.md                       → long-lived project invariants
3. handover/ai-direct/LATEST.md                → live runtime state
4. handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md → permanent multi-agent governance
5. handover/ops/CHILD_AGENT_OPERATING_PROFILE.md → delegated sub-agent protocol (only when child agents are used)
6. .codex/config.toml                           → Codex CLI project-scoped child-role registry (only when Codex child roles are used)
7. Active mission charter (if present)         → task-level canonical spec
```

This reading order is equivalent to the repo-level order in `AGENTS.md` and the permanent governance order in `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`.

If no mission charter exists for substantial work, instantiate one from:

- `handover/ops/MISSION_CHARTER_TEMPLATE.md`

Do not expand further until the task-level canonical spec is identified.

## 1.1 Current Live Frontier (2026-03-10)

The current live frontier is no longer “broad ML reopen” or “default Vertex training”.

As of the latest frozen evidence:

- `V657` passed a **one-sided, sign-aware threshold / hazard** gate.
- `V658` kept broader ML blocked because the narrow admitted-set learner did not beat the constant-baseline logloss gate.
- `V659` kept broader ML blocked because the fixed winning contract did not fully replicate its signed-return tightening on a disjoint replication block.
- `V660` kept broader ML blocked because deterministic month-segment replication also failed to pass the frozen ladder.

Therefore:

- broad ML / Vertex / holdout remain closed
- the active frontier is still **non-ML campaign-state truth-finding**
- the single operational truth source remains `handover/ai-direct/LATEST.md`
- the current task-level source of truth remains `handover/ops/ACTIVE_MISSION_CHARTER.md`
- the wider project context remains `handover/ops/ACTIVE_PROJECTS.md`

## 2. Project Identity

| Key | Value |
|---|---|
| Name | OMEGA vNext (Maxwell Edition) |
| Domain | Algorithmic trading, China A-Shares |
| Math | TDA + SRL (δ=0.5) + Epiplexity (MDL) |
| Language | Python 3.9+ (Polars, NumPy, Numba, XGBoost) |
| Architecture | 3-node cluster (Mac controller + Linux worker + Windows worker) |

## 3. Governance Layers

OMEGA now separates permanent governance from task-specific execution.

### Layer 0: Constitution

- `OMEGA_CONSTITUTION.md`
- Long-lived project invariants

### Layer 1: Multi-Agent Operating System

- `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`
- Permanent team structure, authority, gates, runtime discipline
- `handover/ops/CHILD_AGENT_OPERATING_PROFILE.md`
- Delegated child-agent authority and packet discipline
- `.codex/config.toml` + `.codex/agents/*.toml`
- Project-scoped Codex CLI child-role wiring for OMEGA only; not a global Codex role registry

### Layer 2: Mission Charter

- Active task-level canonical spec
- Instantiate from `handover/ops/MISSION_CHARTER_TEMPLATE.md`

### Layer 3: Run Manifest and Handover

- `handover/ai-direct/LATEST.md`
- `handover/BOARD.md`
- `handover/ai-direct/entries/`

## 4. What `/handover` now owns

`/handover` is the unified home for:

- agent entry
- multi-agent governance
- runtime truth
- handoff state
- debug memory
- costly lessons
- task charters

## 5. File Map (find anything in <5s)

### Agent Governance

| What | Where |
|---|---|
| Agent rules (ALL agents) | `AGENTS.md` |
| Unified handover entrypoint | `handover/README.md` |
| Multi-agent operating system | `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md` |
| Child-agent operating profile | `handover/ops/CHILD_AGENT_OPERATING_PROFILE.md` |
| Codex child-role registry (project-scoped) | `.codex/config.toml` |
| Codex child-role configs | `.codex/agents/*.toml` |
| Gemini sub-agent runbook | `handover/ops/GEMINI_SUBAGENT_BEST_PRACTICES.md` |
| Mission charter template | `handover/ops/MISSION_CHARTER_TEMPLATE.md` |
| Physics constitution | `OMEGA_CONSTITUTION.md` |
| Machine-readable principles | `.agent/principles.yaml` |
| Skills (8 active) | `.agent/skills/{name}/SKILL.md` |

### Code

| What | Where |
|---|---|
| Math kernels (source of truth) | `omega_core/omega_math_core.py` |
| Physics engine | `omega_core/kernel.py` |
| ETL pipeline | `omega_core/omega_etl.py` |
| All configuration | `config.py` |
| Node-specific paths | `configs/node_paths.py` |
| Structured logging | `omega_core/omega_log.py` |

### Operations

| What | Where |
|---|---|
| Deploy code to workers | `python3 tools/deploy.py` |
| Cluster health check | `python3 tools/cluster_health.py` |
| Environment verification | `python3 tools/env_verify.py` |
| Campaign-state forge (current default entry) | `tools/forge_campaign_state.py` |
| Pure event study | `tools/run_campaign_event_study.py` |
| Transition event study | `tools/run_campaign_transition_event_study.py` |
| Sign-aware threshold audit | `tools/run_campaign_sign_aware_threshold_audit.py` |
| Fixed-contract replication audit | `tools/run_campaign_fixed_contract_replication_audit.py` |
| Segmented replication audit | `tools/run_campaign_segmented_replication_audit.py` |
| Narrow ML-admission probe (currently blocked) | `tools/run_campaign_ml_admission_probe.py` |
| Stage 1 ETL (base-chain rebuild) | `tools/stage1_linux_base_etl.py` |
| Stage 2 Physics (base-chain rebuild) | `tools/stage2_physics_compute.py` |

### Handover & Memory

| What | Where |
|---|---|
| **🤖 Agent Board (READ+WRITE)** | **`handover/BOARD.md`** |
| Unified `/handover` entrypoint | `handover/README.md` |
| Permanent agent governance | `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md` |
| Mission charter template | `handover/ops/MISSION_CHARTER_TEMPLATE.md` |
| Live runtime state | `handover/ai-direct/LATEST.md` |
| Session history (40+ entries) | `handover/ai-direct/entries/` |
| V64 audit evolution canon | `audit/v64_audit_evolution.md` |
| Audit index | `audit/README.md` |
| Debug lessons (searchable) | `handover/DEBUG_LESSONS.md` |
| Costly mistakes ($43 ledger) | `handover/COSTLY_LESSONS.md` |
| Network topology | `handover/ops/HOSTS_REGISTRY.yaml` |
| SSH setup | `handover/ops/SSH_NETWORK_SETUP.md` |
| Active projects board | `handover/ops/ACTIVE_PROJECTS.md` |

### Credentials & Access

| What | Where |
|---|---|
| SSH keys | `~/.ssh/` (never in repo) |
| Access bootstrap guide | `handover/ops/ACCESS_BOOTSTRAP.md` |
| Host aliases & IPs | `handover/ops/HOSTS_REGISTRY.yaml` |
| GCP credentials | `~/.config/gcloud/` (never in repo) |

> **Secrets policy:** NEVER store secrets in git. Only store *locations* and *bootstrap steps*.

### Testing

| What | Command |
|---|---|
| Math invariants (28 tests) | `python3 -m pytest tests/test_omega_math_core.py -q` |
| Logging tests (16 tests) | `python3 -m pytest tests/test_omega_log.py -q` |
| All tests | `python3 -m pytest tests/ -q` |
| Environment check | `python3 tools/env_verify.py --strict` |

## 6. Cluster Topology

```
Mac (M4 Max, Controller)
├── Git origin, orchestration, backtesting
├── SSH → linux1-lx  (alias first; 192.168.3.113 informational only)
└── SSH → windows1-w1 (alias first; 192.168.3.112 informational only; source of truth: `handover/ops/HOSTS_REGISTRY.yaml`)

Linux (Ryzen, 128G RAM)
├── Stage 1 ETL + Stage 2 Physics
└── ZFS pool: /omega_pool/

Windows (Ryzen, 64G RAM)
├── Stage 1 ETL + Stage 2 Physics
└── D:\Omega_frames\
```

Workers are on **isolated LANs** — no internet, no GitHub access.

## 7. Hard Rules (Violations = Blocked)

1. **ECONOPHYSICS > SWE** — standard engineering heuristics yield to physics
2. **δ = 0.5 is a constant** — never optimize, never race exponents
3. **No time-axis sharding** — shard by ticker/symbol for OOM
4. **Float64 only** — never downcast physics math to Float32
5. **Atomic writes** — `.tmp` → `rename()` for all parquet output
6. **No SCP** — deploy via `git push` only (`tools/deploy.py`)
7. **Commit before deploy** — no dirty-tree deployments
8. **Tests before merge** — `pytest tests/ -q` must pass

## 8. Session Protocol

### Starting a session

1. Read this file
2. Read `OMEGA_CONSTITUTION.md`
3. Read `handover/ai-direct/LATEST.md`
4. For multi-agent or substantial work, read `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`
5. Identify the active mission charter, or create one from `handover/ops/MISSION_CHARTER_TEMPLATE.md`
6. Run `python3 tools/cluster_health.py --quick`
7. Check `git log --oneline -5 && git status`

### Ending a session

1. **Post debrief to `handover/BOARD.md` Section 1** (MANDATORY — use the template)
2. Create entry: `handover/ai-direct/entries/YYYYMMDD_HHMMSS_<topic>.md`
3. Update `handover/ai-direct/LATEST.md`
4. Commit changes

## 9. Skill Index

| Skill | Trigger |
|---|---|
| `math_core` | Modifying SRL/TDA/Epiplexity math |
| `physics` | Physics model or adaptive Y changes |
| `engineering` | Refactoring, testing, code standards |
| `hardcode_guard` | Reviewing for hardcoded paths/IPs |
| `data_integrity_guard` | Parquet schema or pipeline changes |
| `ops` | Deployment, cluster operations |
| `omega_development` | Development workflow, branching |
| `ai_handover` | Session handover protocol |

Read skill details: `.agent/skills/{name}/SKILL.md`

## 9.1 Codex Child-Role Integration

For Codex CLI only:

- OMEGA-specific child roles are configured at the repo level in `.codex/config.toml`
- Repo-local `[features] child_agents_md = true` is required so delegated Codex children inherit the scoped `AGENTS.md` chain without depending on user-global config
- Role-specific configs live in `.codex/agents/*.toml`
- These roles are project-scoped and must not be copied into `~/.codex/config.toml` as global roles
- The human-readable governance source remains `handover/ops/CHILD_AGENT_OPERATING_PROFILE.md`
- The CLI-consumed role wiring remains `.codex/config.toml` + `.codex/agents/*.toml`

## 9.2 Gemini Sub-Agent Invocation

For Gemini CLI sub-agent calls:

- Call `/usr/bin/gemini` directly from the parent agent or orchestrator, not through the user-local `gemini` shell wrapper and not through a repo-local Python wrapper
- Prefer read-only math/audit mode (`--approval-mode plan`) when Gemini CLI has `experimental.plan` enabled; otherwise use `--approval-mode default`
- Prefer `--output-format stream-json` so the parent agent can distinguish `init`/result events from a merely silent model turn
- Use one fresh Gemini process per bounded role packet; keep prompts short and file-bounded
- Use a long wall-clock budget for serious reasoning; `1800s` is the OMEGA default direct-call budget
- Do not treat the first long silent window as failure; inspect `stream-json` events and `~/.gemini/tmp/<project>/chats/` before killing the run
- On GCP VMs, prefer Vertex/ADC authentication if you want cloud-native auth behavior; running on GCP does not change Gemini CLI behavior when `~/.gemini/settings.json` still points at personal OAuth
- Full runbook: `handover/ops/GEMINI_SUBAGENT_BEST_PRACTICES.md`

## 10. Audit Canon

For V64 specifically, the fastest reliable way to reconstruct the math and audit history is:

1. `audit/v64_audit_evolution.md`
2. `audit/v64.md`
3. `audit/v642.md`
4. `audit/v643.md`
5. `audit/v643_auditor_pass.md`

Use `audit/v64_audit_evolution.md` as the narrative overview, then drill into the versioned audit files for the raw source text.

---

*Last updated: 2026-03-10*
*This file is the unified `/handover` entrypoint. `handover/ENTRYPOINT.md` remains only as a compatibility shim.*

## Google Docs CLI Tool
A global CLI tool `gdocs` is available to access and read Google Docs (authenticated via the user's ziqian.jia@gmail.com account).
- `gdocs list` - Lists recent documents with their IDs.
- `gdocs read <ID>` - Outputs the plain text content of a Google Doc.

AI agents can use this tool to fetch requirements, architectures, or context from the user's personal Google Drive.

- **`archive/`** - Archived tools, scripts, and audit reports from legacy versions (e.g., v62). Check here for historical rollbacks or context on deprecated pipelines.
