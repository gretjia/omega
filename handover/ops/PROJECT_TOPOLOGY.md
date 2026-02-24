# Project Topology (Omega v62)

This document maps the repository and distributed runtime topology.

## 1. Repository Topology (Controller View)

| Path | Role |
|---|---|
| `omega_core/` | Core ETL and physics math implementation |
| `tools/` | Operational entry scripts for Stage1/2/3 and run utilities |
| `pipeline/` | Legacy pipeline modules (active entrypoints archived/guarded) |
| `audit/` | Constitution, governance, audits, runtime policies |
| `handover/` | Agent startup, status, operations runbooks, and handoff history |
| `tests/` | Regression and behavior validation tests |
| `archive/` | Archived legacy implementations |

## 2. Runtime Topology (Distributed)

| Node | Role | Typical Work |
|---|---|---|
| `omega-vm` | control plane + monitoring + git sync + cloud supervision | monitor Stage1/2, run Stage3 submission/supervision |
| `linux1-lx` | worker | Stage1 Base_L1, optional Stage2 |
| `windows1-w1` | worker | Stage1 Base_L1, Stage2 Feature_L2 |
| `GCP Vertex` | training/backtest compute | Stage3 train jobs and cloud logs |

## 3. Pipeline Topology (v62)

1. Stage1 Base Lake ETL
   - scripts: `tools/stage1_linux_base_etl.py`, `tools/stage1_windows_base_etl.py`
   - output: `v62_base_l1`
2. Stage2 Physics Compute
   - script: `tools/stage2_physics_compute.py`
   - output: `v62_feature_l2`
3. Base Matrix Forge
   - script: `tools/forge_base_matrix.py`
   - output: base matrix parquet + optional metadata
4. Stage3 Train/Backtest
   - scripts: `tools/run_vertex_xgb_train.py`, `tools/run_local_backtest.py`

## 4. Host Output Paths

- Linux Stage1 output: `/omega_pool/parquet_data/v62_base_l1/host=linux1`
- Linux Stage2 output: `/omega_pool/parquet_data/v62_feature_l2/host=linux1`
- Windows Stage1 output: `D:\Omega_frames\v62_base_l1\host=windows1`
- Windows Stage2 output: `D:\Omega_frames\v62_feature_l2\host=windows1`

## 5. Legacy Boundary

- `pipeline_runner.py` and old framer path are archived/guarded and are not primary v62 execution paths.
- Use `tools/stage1_*`, `tools/stage2_physics_compute.py`, and Stage3 scripts as the active pipeline.

## 6. Related Docs

- File map: `handover/ops/FILE_TOPOLOGY.md`
- Active status: `handover/ops/ACTIVE_PROJECTS.md`
- Logs index: `handover/ops/PIPELINE_LOGS.md`

