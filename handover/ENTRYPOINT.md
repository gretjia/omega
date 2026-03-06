# Agent Entrypoint

> **This file now points to the unified AI Agent Manual.**
> For the complete onboarding guide, read `handover/README.md` first.

## Quick Start (3 files)

1. `handover/README.md` — project map, rules, file locations
2. `OMEGA_CONSTITUTION.md` — physics-first principles
3. `handover/ai-direct/LATEST.md` — live runtime state

## Operational Commands

```bash
python3 tools/cluster_health.py --quick   # cluster status
python3 tools/env_verify.py --strict      # env check
python3 tools/deploy.py --dry-run         # preview deploy
```

If SSH fails, check:

- `handover/ops/ACCESS_BOOTSTRAP.md`
- `handover/ops/HOSTS_REGISTRY.yaml`

## Canonical Maps

- Agent rules: `AGENTS.md`
- Constitution: `OMEGA_CONSTITUTION.md`
- Active projects: `handover/ops/ACTIVE_PROJECTS.md`
- Debug lessons: `handover/DEBUG_LESSONS.md`
- Costly mistakes: `handover/COSTLY_LESSONS.md`
- Hosts registry: `handover/ops/HOSTS_REGISTRY.yaml`
- SSH setup: `handover/ops/SSH_NETWORK_SETUP.md`

## Session-End Checklist

1. Create entry: `handover/ai-direct/entries/YYYYMMDD_HHMMSS_<topic>.md`
2. Update `handover/ai-direct/LATEST.md`
3. Commit changes

## Secrets Policy

Never store secrets in git. Only store credential *locations* and bootstrap steps.
See `handover/ops/ACCESS_BOOTSTRAP.md` for details.

## 🚨 V64.1 Hotfix Alert (2026-03-06)
A mathematical closure hotfix (The Bourbaki Synthesis) has been applied to the downstream Python scripts (`forge_base_matrix.py`, `trainer.py`, `run_vertex_xgb_train.py`). This hotfix dynamically corrects the legacy `is_signal` column stored in the physical L2 parquet files.
**Agents must ensure a `git pull origin main` is executed on the target node before running any Stage 3 or evaluation tasks.**

