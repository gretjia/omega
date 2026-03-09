# 2026-03-09 01:10 UTC - Train Base-Matrix Complete And Vertex Baseline Success

## Scope
- Confirm completion and readiness of the `2023,2024` Linux training base matrix.
- Launch one baseline Vertex training job from that finished base matrix.

## Base-Matrix Completion
- output parquet:
  - `/omega_pool/parquet_data/stage3_base_matrix_train_20260308_095850/base_matrix_train_2023_2024.parquet`
- output meta:
  - `/omega_pool/parquet_data/stage3_base_matrix_train_20260308_095850/base_matrix_train_2023_2024.parquet.meta.json`
- forge terminal line:
  - `{"status": "ok", ... "base_rows": 736163, "input_file_count": 484, "symbols_total": 7708, "batch_count": 155, "worker_count": 1, "seconds": 50691.92}`

## Downstream Contract Checks
- Year scope from final parquet:
  - `year_min=2023`
  - `year_max=2024`
  - `year_count=2`
- Required training schema:
  - no missing required columns relative to `tools/run_vertex_xgb_train.py`
- Training gate diagnostics at active default `singularity_threshold=0.10`:
  - `rows=736163`
  - `epi_pos_rows=96955`
  - `topo_energy_pos_rows=736163`
  - `signal_gate_rows=736163`

## GCS Staging
- staged base matrix:
  - `gs://omega_v52_central/omega/staging/base_matrix/latest/stage3_train_2023_2024_20260309_005839/base_matrix_train_2023_2024.parquet`
- staged meta:
  - `gs://omega_v52_central/omega/staging/base_matrix/latest/stage3_train_2023_2024_20260309_005839/base_matrix_train_2023_2024.parquet.meta.json`

## Baseline Vertex Train
- submit path:
  - `uv run --with google-cloud-aiplatform --with google-cloud-storage python tools/submit_vertex_sweep.py ...`
- reason for `uv run`:
  - controller `python3` lacked `google-cloud-aiplatform`
- job:
  - `projects/269018079180/locations/us-central1/customJobs/5549661916156133376`
  - `displayName=omega-v60-run_vertex_xgb_train-20260309-010052`
  - `state=JOB_STATE_SUCCEEDED`
  - `createTime=2026-03-09T01:00:54.744284Z`
  - `startTime=2026-03-09T01:04:49Z`
  - `endTime=2026-03-09T01:05:49Z`

## Training Outputs
- model:
  - `gs://omega_v52_central/omega/staging/models/latest/stage3_train_2023_2024_20260309_005839/omega_xgb_final.pkl`
- metrics:
  - `gs://omega_v52_central/omega/staging/models/latest/stage3_train_2023_2024_20260309_005839/train_metrics.json`
- metrics content:
  - `status=completed`
  - `base_rows=736163`
  - `mask_rows=736163`
  - `total_training_rows=736163`
  - payload `seconds=2.82`

## Important Architectural Note
- This session proves:
  - the finished `2023,2024` base matrix is trainable
  - the current active Vertex path works as a baseline
- This session does **not** prove:
  - that current cloud training meaningfully exploits cloud-parallel swarm/Optuna advantages
- The live train path remains single-job, single-replica offload.

## Additional Live Drift
- `tools/stage3_full_supervisor.py` currently targets `gs://omega_central/...`
- that bucket is absent in the live environment
- successful staging/training in this session still required `gs://omega_v52_central/...`
