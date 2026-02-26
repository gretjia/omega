---
name: omega_development
description: Development workflow, branching, and pipeline execution for OMEGA.
---

# Skill: omega_development

## When To Use

- Starting new feature development
- Running the 2-stage pipeline (Stage 1 ETL → Stage 2 Physics)
- Working on training, backtesting, or model evaluation

## Pipeline Architecture

```
Raw 7z/CSV  ──Stage 1──>  Base L1 Parquet  ──Stage 2──>  Feature L2 Parquet  ──>  Training
  (Level-2)     (ETL)       (ticks/frames)    (Physics)     (+SRL,TDA,Epi)         (XGBoost)
```

| Stage | Script | Node | Output |
|---|---|---|---|
| Stage 1 | `tools/stage1_linux_base_etl.py` | Linux | `v62_base_l1/host=linux1/` |
| Stage 1 | `tools/stage1_windows_base_etl.py` | Windows | `v62_base_l1/host=windows1/` |
| Stage 2 | `tools/stage2_physics_compute.py` | Both | `v62_feature_l2/host=...` |
| Backtest | `tools/run_local_backtest.py` | Mac | `artifacts/` |

## Development Workflow

1. **Branch**: Create feature branch from `main`
2. **Develop**: Edit on Mac controller
3. **Test locally**: `pytest tests/test_omega_math_core.py -v`
4. **Deploy**: `python3 tools/deploy.py --dry-run` then `--skip-commit`
5. **Monitor**: `python3 tools/cluster_health.py`
6. **Merge**: After all nodes show same git hash and tests pass

## Configuration Hierarchy

```
config.py          ← Math/physics parameters (ALL agents read this)
configs/node_paths.py  ← Host-specific paths (auto-detected)
HOSTS_REGISTRY.yaml    ← SSH aliases and network topology
requirements.lock      ← Pinned dependencies
```

## Key Rules

- **Volume Clock**: Always use volume bars, never time bars. Config: `L2VolumeClockConfig`
- **A-Share sessions**: Filter to 09:30-11:30, 13:00-15:00 CST. Config: `L2SessionConfig`
- **T+1 settlement**: Labels require next-day data. Single-day processing breaks causality.
- **Dataset isolation**: Train (2023-2024), Test (2025), Backtest (2026.01). No overlap.
