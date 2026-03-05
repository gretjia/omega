# OMEGA Project — AI Agent Manual

> **Read time:** ~60 seconds. This file is the single onboarding document for any AI agent.
> After reading this, you will know where everything is and what rules to follow.

## 1. Reading Order (3 files, then start)

```
1. This file           → project map + rules summary
2. OMEGA_CONSTITUTION.md  → physics-first principles (the "Bible")
3. handover/ai-direct/LATEST.md → live runtime state
```

Do NOT read anything else before starting. Expand context only as needed.

## 2. Project Identity

| Key | Value |
|---|---|
| Name | OMEGA vNext (Maxwell Edition) |
| Domain | Algorithmic trading, China A-Shares |
| Math | TDA + SRL (δ=0.5) + Epiplexity (MDL) |
| Language | Python 3.9+ (Polars, NumPy, Numba, XGBoost) |
| Architecture | 3-node cluster (Mac controller + Linux worker + Windows worker) |

## 3. File Map (find anything in <5s)

### Agent Governance

| What | Where |
|---|---|
| Agent rules (ALL agents) | `AGENTS.md` |
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
| Stage 1 ETL (Linux) | `tools/stage1_linux_base_etl.py` |
| Stage 2 Physics (both) | `tools/stage2_physics_compute.py` |

### Handover & Memory

| What | Where |
|---|---|
| **🤖 Agent Board (READ+WRITE)** | **`handover/BOARD.md`** |
| Live runtime state | `handover/ai-direct/LATEST.md` |
| Session history (40+ entries) | `handover/ai-direct/entries/` |
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

## 4. Cluster Topology

```
Mac (M4 Max, Controller)
├── Git origin, orchestration, backtesting
├── SSH → linux1-lx  (192.168.3.113, LAN)
└── SSH → windows1-w1 (192.168.3.112, SMB mount)

Linux (Ryzen, 128G RAM)
├── Stage 1 ETL + Stage 2 Physics
└── ZFS pool: /omega_pool/

Windows (Ryzen, 64G RAM)
├── Stage 1 ETL + Stage 2 Physics
└── D:\Omega_frames\
```

Workers are on **isolated LANs** — no internet, no GitHub access.

## 5. Hard Rules (Violations = Blocked)

1. **ECONOPHYSICS > SWE** — standard engineering heuristics yield to physics
2. **δ = 0.5 is a constant** — never optimize, never race exponents
3. **No time-axis sharding** — shard by ticker/symbol for OOM
4. **Float64 only** — never downcast physics math to Float32
5. **Atomic writes** — `.tmp` → `rename()` for all parquet output
6. **No SCP** — deploy via `git push` only (`tools/deploy.py`)
7. **Commit before deploy** — no dirty-tree deployments
8. **Tests before merge** — `pytest tests/ -q` must pass

## 6. Session Protocol

### Starting a session

1. Read this file + `LATEST.md`
2. Run `python3 tools/cluster_health.py --quick`
3. Check `git log --oneline -5 && git status`

### Ending a session

1. **Post debrief to `handover/BOARD.md` Section 1** (MANDATORY — use the template)
2. Create entry: `handover/ai-direct/entries/YYYYMMDD_HHMMSS_<topic>.md`
3. Update `handover/ai-direct/LATEST.md`
4. Commit changes

## 7. Skill Index

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

---

*Last updated: 2026-02-26 by Antigravity Agent*
*This file replaces the legacy ENTRYPOINT.md as the primary onboarding doc.*

## Google Docs CLI Tool
A global CLI tool `gdocs` is available to access and read Google Docs (authenticated via the user's ziqian.jia@gmail.com account).
- `gdocs list` - Lists recent documents with their IDs.
- `gdocs read <ID>` - Outputs the plain text content of a Google Doc.

AI agents can use this tool to fetch requirements, architectures, or context from the user's personal Google Drive.
