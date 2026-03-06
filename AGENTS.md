# AGENTS.md — OMEGA Unified Agent Entry Point

> **This is the ONE file all AI agents must read first, regardless of IDE or CLI.**
> It is IDE-agnostic — the same rules apply to Gemini, Claude, Codex, Cursor, or any future agent.
> After this file, the authoritative unified entrypoint is `handover/README.md`.
> Repo entrypoint: `AGENTS.md`. Handover entrypoint: `handover/README.md`.

## Quick Start

Quick Start is equivalent to the canonical reading order in `handover/README.md` and `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`.


1. Read this file
2. Read `handover/README.md` for unified onboarding, governance, and handover routing
3. Read `OMEGA_CONSTITUTION.md` before any task
4. Read `handover/ai-direct/LATEST.md` for live runtime state
5. For substantial work, identify the active mission charter under `handover/ops/` or instantiate one from `handover/ops/MISSION_CHARTER_TEMPLATE.md`

## Scope

**OMEGA vNext** — a high-fidelity algorithmic trading system for China A-Shares.
Built on the Mathematical Trinity: TDA, SRL (δ=0.5), Epiplexity (MDL).

## Core Architecture

| Layer | Location | Description |
| --- | --- | --- |
| Math engines | `omega_core/` | `kernel.py`, `omega_math_core.py`, `omega_etl.py` |
| Pipeline tools | `tools/` | Stage1 ETL, Stage2 Physics, deploy, health checks |
| Configuration | `config.py`, `configs/` | Math params + node-specific paths |
| Tests | `tests/` | Math invariant tests, logging tests |
| Governance | `.agent/`, `handover/` | Skills, principles, handover state |
| Logging | `omega_core/omega_log.py` | Structured logger + progress tracker |

## Hard Rules

1. **Constitution First**: Read `OMEGA_CONSTITUTION.md` before any task. It is immutable.
2. **ECONOPHYSICS > SWE**: Physics supersedes standard engineering heuristics.
3. **δ = 0.5 is a constant**: Never optimize, never race exponents.
4. **No Hardcoded Paths**: Use `configs/node_paths.py` for hosts, `config.py` for math.
5. **Volume Clock**: Prefer volume bars over time bars. No time-axis sharding.
6. **Float64 Only**: Never downcast physics math.
7. **Dataset Isolation**: Train/val/test/backtest are disjoint by construction.
8. **Canonical Core**: `omega_core/*` is the single source of truth for math.
9. **Tests Before Merge**: `python3 -m pytest tests/ -q` must pass.

## Security

- **No secrets in git.** Keys, tokens, passwords are in `~/.ssh/`, OS keychain, or cloud secret manager.
- **Credential locations only.** See `handover/ops/ACCESS_BOOTSTRAP.md` for bootstrap.
- **No raw IPs in code.** Use SSH aliases from `handover/ops/HOSTS_REGISTRY.yaml`.

## Git Workflow

- **Commit before deploy.** No dirty-tree deployments.
- **No SCP.** Deploy via `git push` only (`python3 tools/deploy.py`).
- **Workers are read-only.** They receive code via `git push`, never `git pull`.
- **Atomic writes only.** Use `.tmp` + `rename()` semantics where applicable; see `handover/README.md` for the handover-level rule.
- **Branch naming:** `feature/<name>`, `fix/<name>`, `perf/<name>`.

## Deployment Protocol

```bash
# Step 1: Commit
git add . && git commit -m "..." && git push origin HEAD

# Step 2: Deploy to workers
python3 tools/deploy.py                # or: --nodes linux --dry-run

# Step 3: Verify
python3 tools/cluster_health.py        # all nodes synced?
python3 tools/env_verify.py --strict   # deps match?
```

## Skills

Skills live in `.agent/skills/`. Each has a `SKILL.md` with domain-specific rules.

| Skill | Trigger |
| --- | --- |
| `math_core` | SRL/TDA/Epiplexity kernel changes |
| `physics` | Physics model changes |
| `engineering` | Refactoring, testing, code standards |
| `hardcode_guard` | Reviewing for hardcoded values |
| `data_integrity_guard` | Data pipeline and schema changes |
| `ops` | Deployment and infrastructure |
| `omega_development` | Development workflow |
| `ai_handover` | Session handover |

## Testing

```bash
python3 -m pytest tests/test_omega_math_core.py -q   # Math (28 tests, <0.2s)
python3 -m pytest tests/test_omega_log.py -q          # Logging (16 tests)
python3 tools/env_verify.py                            # Environment
python3 tools/cluster_health.py --quick                # Cluster
```

## Handover

- `handover/README.md` — unified `/handover` entrypoint (READ THIS)
- `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md` — permanent OMEGA multi-agent governance layer
- `handover/ops/MISSION_CHARTER_TEMPLATE.md` — task-level execution charter template
- `handover/ai-direct/LATEST.md` — live runtime state
- `handover/DEBUG_LESSONS.md` — searchable debug database
- `handover/COSTLY_LESSONS.md` — expensive mistakes ledger
