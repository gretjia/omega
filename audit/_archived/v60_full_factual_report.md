# v60 Full Factual Report (Framing -> Base Matrix -> Optimization -> Training -> Backtesting)

## 0. Report Scope
- Repository: `/Users/zephryj/work/Omega_vNext`
- Run hash: `aa8abb7`
- Report type: factual only (raw outputs, raw artifacts, raw logs, raw job states)
- Evidence root: `audit/runtime/v60_factual_evidence/`

## 1. Primary Run IDs and Artifact Roots
- Autopilot run id: `20260219-030000`
- Optimization job id: `8392580415252070400`
- Training job id (completed): `6022297228557680640`
- Backtest job id (completed): `1959559432727691264`
- Base matrix URI: `gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet`
- Optimization result URI: `gs://omega_v52_central/omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json`
- Training output URI: `gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9`
- Backtest output URI: `gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`

## 2. Stage Facts (Framing)
- `autopilot_aa8abb7.status.json` reports:
  - `started_at=2026-02-19 10:59:51`
  - `windows_expected=263`, `linux_expected=484`
  - `frame.windows_done=263`, `frame.linux_done=484`, `frame.probe_ok=true`
  - `upload.gcs_counts.windows1=263`, `upload.gcs_counts.linux1=484`, `checked_at=2026-02-19 11:00:00`
- `autopilot_aa8abb7.stage_transition_excerpt.txt` records:
  - Frame stage complete
  - Upload stage complete
  - GCS counts check complete

## 3. Stage Facts (Base Matrix)
- Execution mode: `local_ticker_sharding`
- Source pattern in run log: `/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/*_aa8abb7.parquet`
- Input files: `40`
- Raw rows: `7,466,620`
- Base rows: `5,780,139`
- Symbols: `5,576`
- Batches: `112`
- Worker count: `8`
- Base matrix runtime (meta): `705.91s`
- Base matrix runtime (autopilot summary line): `940.89s`
- Artifact object metadata:
  - `base_matrix.parquet` size: `970,685,813 bytes`, creation: `2026-02-19T03:15:38+0000`
  - `base_matrix.meta.json` size: `37,260 bytes`, creation: `2026-02-19T03:15:41+0000`

## 4. Stage Facts (Optimization)
- Job id: `8392580415252070400`
- State: `JOB_STATE_SUCCEEDED`
- Machine: `e2-highmem-16`
- Time window:
  - create: `2026-02-19T03:15:48.956931Z`
  - start: `2026-02-19T03:19:50Z`
  - end: `2026-02-19T03:21:21Z`
- Raw result (`swarm_best.json`):
  - `status=completed`
  - `best_value=0.6101452643370191`
  - `n_trials=50`
  - `n_completed=20`
  - `best_params` + `feature_cols` persisted

## 5. Stage Facts (Training)
- Cancelled training job:
  - id: `4026903526469795840`
  - state: `JOB_STATE_CANCELLED`
  - machine: `n1-standard-32`
  - error message: `CANCELED`
- Completed training job:
  - id: `6022297228557680640`
  - state: `JOB_STATE_SUCCEEDED`
  - machine: `n2-standard-16`
  - create/start/end: `2026-02-19T12:54:17.783874Z` / `2026-02-19T12:56:47Z` / `2026-02-19T12:57:47Z`
- Raw `train_metrics.json`:
  - `status=completed`
  - `base_rows=5780139`
  - `mask_rows=2188`
  - `total_training_rows=2067`
  - `seconds=1.04`
  - `model_uri=.../omega_v6_xgb_final.pkl`
- Model artifact metadata:
  - size: `355,684 bytes`
  - creation: `2026-02-19T12:57:20+0000`

## 6. Stage Facts (Backtesting)
- Backtest job chain in `us-central1` (selected IDs):
  - failed: `320740100306632704`, `4665024890858897408`, `1324903728989339648`, `8385422044799434752`, `6324251159091478528`, `1475563210273718272`, `3366793578792615936`
  - cancelled: `4745526734198145024`, `6945888645156962304`
  - succeeded (smoke): `4089128737776336896`
  - succeeded (final): `1959559432727691264`
- Memory failure messages from `describe`:
  - job `6324251159091478528`: `Replicas low on memory: workerpool0. Specify a machine with larger memory and try again.`
  - job `1475563210273718272`: same message
  - job `3366793578792615936`: same message
- Final succeeded job (`1959559432727691264`):
  - state: `JOB_STATE_SUCCEEDED`
  - machine: `n2-highmem-80`
  - create/start/end: `2026-02-19T18:48:55.655224Z` / `2026-02-19T18:49:11Z` / `2026-02-19T19:09:19Z`
  - key runtime log evidence includes:
    - download progress to `263/263`
    - sort size `32368466 rows`
    - `Valid processed rows after T+1 causality shift: 8907595`
- Final raw backtest metrics:
  - `status=completed`
  - `files_used=263`
  - `day_span_used.first=20250102`
  - `day_span_used.last=20260130`
  - `total_proc_rows=8907595`
  - `seconds=1170.03`
  - `worker_plan.architecture=global_causal_materialization`
  - `worker_plan.reuse_precomputed_physics=true`
  - `summary.Topo_SNR=10.885431366882955`
  - `summary.Model_Alignment=0.49742754220434177`

## 7. Evidence Attachments Index
- Full evidence package directory: `audit/runtime/v60_factual_evidence/`
- File inventory (size + timestamp): `audit/runtime/v60_factual_evidence/manifest_ls_lh.txt`
- Source snapshot checksums: `audit/runtime/v60_factual_evidence/source_file_sha256.txt`
- Source snapshot line counts: `audit/runtime/v60_factual_evidence/source_file_line_counts.txt`

---

## Appendix A: Raw Core JSON (Copy-Paste)

### A1. `autopilot_aa8abb7.status.json`
```json
{
  "started_at": "2026-02-19 10:59:51",
  "git_hash": "aa8abb7",
  "bucket": "gs://omega_v52_central/omega",
  "windows_expected": 263,
  "linux_expected": 484,
  "stage": "vertex_train",
  "frame": {
    "linux_done": 484,
    "windows_done": 263,
    "windows_task_state": "Ready",
    "probe_linux": 484,
    "probe_windows": 263,
    "probe_ok": true,
    "updated_at": "2026-02-19 10:59:52"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-19 11:00:00"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.meta.json",
    "base_matrix_exec_mode": "local_ticker_sharding",
    "base_matrix_input_pattern": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/*_aa8abb7.parquet",
    "base_matrix_input_files": 40,
    "base_matrix_symbols_per_batch": 50,
    "base_matrix_max_workers": 8,
    "base_matrix_resume": true,
    "base_matrix_cache_key": "aa8abb7",
    "result_uri": "gs://omega_v52_central/omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json",
    "completed_at": "2026-02-19 11:21:39",
    "result": {
      "status": "completed",
      "best_params": {
        "peace_threshold": 0.5253567667772991,
        "srl_resid_sigma_mult": 1.9773888188507172,
        "topo_energy_sigma_mult": 5.427559578121958,
        "max_depth": 5,
        "learning_rate": 0.006525909043483982,
        "subsample": 0.9382970275902356,
        "colsample_bytree": 0.7855991276821759
      },
      "best_value": 0.6101452643370191,
      "n_trials": 50,
      "n_completed": 20,
      "base_matrix": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet",
      "feature_cols": [
        "sigma_eff",
        "net_ofi",
        "depth_eff",
        "epiplexity",
        "srl_resid",
        "topo_area",
        "topo_energy",
        "topo_micro",
        "topo_classic",
        "topo_trend",
        "price_change",
        "bar_duration_ms",
        "adaptive_y",
        "epi_x_srl_resid",
        "epi_x_topo_area",
        "epi_x_net_ofi"
      ],
      "seconds": 28.56,
      "job_id": "8392580415252070400"
    },
    "best_params": {
      "peace_threshold": 0.5253567667772991,
      "srl_resid_sigma_mult": 1.9773888188507172,
      "topo_energy_sigma_mult": 5.427559578121958,
      "max_depth": 5,
      "learning_rate": 0.006525909043483982,
      "subsample": 0.9382970275902356,
      "colsample_bytree": 0.7855991276821759
    }
  },
  "train": {
    "output_uri": "gs://omega_v52_central/omega/staging/models/v6/20260219-030000_aa8abb7",
    "data_pattern": "gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet",
    "overrides": {
      "peace_threshold": 0.5253567667772991,
      "srl_resid_sigma_mult": 1.9773888188507172,
      "topo_energy_sigma_mult": 5.427559578121958,
      "max_depth": 5,
      "learning_rate": 0.006525909043483982,
      "subsample": 0.9382970275902356,
      "colsample_bytree": 0.7855991276821759
    }
  },
  "backtest": {
    "machine_candidates": [
      "n2-standard-80",
      "n2-standard-64",
      "n2-standard-48",
      "n2-standard-32"
    ],
    "sync_timeout_sec": 14400,
    "takeover_log": "audit/runtime/v52/backtest_takeover_aa8abb7.log",
    "takeover_mode": "pending_train_completion",
    "worker_policy": {
      "workers": 0,
      "workers_min": 2,
      "workers_max": 0,
      "workers_start": 0,
      "workers_cpu_frac": 0.75,
      "workers_cpu_util_low": 55,
      "workers_cpu_util_high": 88,
      "workers_mem_headroom_gb": 24,
      "workers_est_mem_gb": 3,
      "workers_adjust_step": 1,
      "workers_poll_sec": 2
    }
  },
  "run_id": "20260219-030000",
  "data_pattern": "gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet",
  "orchestrator": {
    "mode": "manual_takeover_after_train",
    "updated_at": "2026-02-19 15:38:50",
    "reason": "upgrade backtest machine tier + adaptive workers",
    "watcher_pid": 63228,
    "watcher_session_id": 31165
  }
}```

### A2. `base_matrix_resume_aa8abb7.meta.json` (full)
```json
{
  "mode": "local_ticker_sharding",
  "input_file_count": 40,
  "input_files": [
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230104_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230110_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230113_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230116_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230119_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230131_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230203_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230206_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230209_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230215_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230221_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230224_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230227_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230302_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230308_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230314_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230317_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230320_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230323_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230329_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230404_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230407_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230410_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230413_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230419_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230425_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230428_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230509_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230512_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230515_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230518_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230524_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230530_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230602_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230605_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230608_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230614_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230620_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230626_aa8abb7.parquet",
    "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/20230629_aa8abb7.parquet"
  ],
  "raw_rows": 7466620,
  "base_rows": 5780139,
  "merged_rows": 5780139,
  "merged_files": 112,
  "skipped_inputs_total": 0,
  "output_parquet": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix.parquet",
  "shard_dir": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards",
  "symbols_total": 5576,
  "symbols_per_batch": 50,
  "batch_count": 112,
  "worker_count": 8,
  "requested_worker_count": 8,
  "worker_budget": 0,
  "mem_available_gb": null,
  "reserve_mem_gb": 40.0,
  "worker_mem_gb": 10.0,
  "dynamic_worker_cap": true,
  "parallel_fallback_used": false,
  "pool_error": "",
  "resume_enabled": true,
  "resumed_batches": 0,
  "processed_batches": 112,
  "total_batches": 112,
  "years": [
    "2023",
    "2024"
  ],
  "hash": "aa8abb7",
  "sample_symbols": 0,
  "physics_gates": {
    "peace_threshold": 0.1,
    "peace_threshold_baseline": 0.1,
    "srl_resid_sigma_mult": 0.5,
    "topo_energy_sigma_mult": 10.0
  },
  "dtype_invariants": {
    "strict_float64_required": true,
    "required_float_dtype": "Float64",
    "forbidden_float_dtypes": [
      "Float16",
      "Float32"
    ],
    "forbidden_float_dtypes_detected": false,
    "checked_column_count": 25
  },
  "seconds": 705.91,
  "batch_stats": [
    {
      "batch_id": 0,
      "symbols": 50,
      "raw_rows": 70839,
      "base_rows": 55830,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00000.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 1,
      "symbols": 50,
      "raw_rows": 74050,
      "base_rows": 58711,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00001.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 2,
      "symbols": 50,
      "raw_rows": 71754,
      "base_rows": 57050,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00002.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 3,
      "symbols": 50,
      "raw_rows": 68273,
      "base_rows": 54214,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00003.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 4,
      "symbols": 50,
      "raw_rows": 69112,
      "base_rows": 54682,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00004.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 5,
      "symbols": 50,
      "raw_rows": 73856,
      "base_rows": 58949,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00005.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 6,
      "symbols": 50,
      "raw_rows": 72325,
      "base_rows": 57369,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00006.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 7,
      "symbols": 50,
      "raw_rows": 72837,
      "base_rows": 57454,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00007.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 8,
      "symbols": 50,
      "raw_rows": 71494,
      "base_rows": 56340,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00008.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 9,
      "symbols": 50,
      "raw_rows": 61741,
      "base_rows": 47823,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00009.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 10,
      "symbols": 50,
      "raw_rows": 63392,
      "base_rows": 49148,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00010.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 11,
      "symbols": 50,
      "raw_rows": 74459,
      "base_rows": 58529,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00011.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 12,
      "symbols": 50,
      "raw_rows": 71407,
      "base_rows": 56577,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00012.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 13,
      "symbols": 50,
      "raw_rows": 74387,
      "base_rows": 58692,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00013.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 14,
      "symbols": 50,
      "raw_rows": 72603,
      "base_rows": 57038,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00014.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 15,
      "symbols": 50,
      "raw_rows": 74693,
      "base_rows": 58842,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00015.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 16,
      "symbols": 50,
      "raw_rows": 71871,
      "base_rows": 56634,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00016.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 17,
      "symbols": 50,
      "raw_rows": 72988,
      "base_rows": 57645,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00017.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 18,
      "symbols": 50,
      "raw_rows": 74268,
      "base_rows": 58551,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00018.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 19,
      "symbols": 50,
      "raw_rows": 72017,
      "base_rows": 56809,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00019.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 20,
      "symbols": 50,
      "raw_rows": 69450,
      "base_rows": 55405,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00020.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 21,
      "symbols": 50,
      "raw_rows": 71659,
      "base_rows": 56755,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00021.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 22,
      "symbols": 50,
      "raw_rows": 73568,
      "base_rows": 58247,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00022.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 23,
      "symbols": 50,
      "raw_rows": 70674,
      "base_rows": 55570,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00023.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 24,
      "symbols": 50,
      "raw_rows": 70574,
      "base_rows": 55086,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00024.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 25,
      "symbols": 50,
      "raw_rows": 69323,
      "base_rows": 53867,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00025.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 26,
      "symbols": 50,
      "raw_rows": 72149,
      "base_rows": 55637,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00026.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 27,
      "symbols": 50,
      "raw_rows": 70439,
      "base_rows": 54230,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00027.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 28,
      "symbols": 50,
      "raw_rows": 73174,
      "base_rows": 56400,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00028.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 29,
      "symbols": 50,
      "raw_rows": 70113,
      "base_rows": 53903,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00029.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 30,
      "symbols": 50,
      "raw_rows": 57049,
      "base_rows": 43318,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00030.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 31,
      "symbols": 50,
      "raw_rows": 42615,
      "base_rows": 31482,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00031.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 32,
      "symbols": 50,
      "raw_rows": 25676,
      "base_rows": 19423,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00032.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 33,
      "symbols": 50,
      "raw_rows": 26737,
      "base_rows": 20254,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00033.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 34,
      "symbols": 50,
      "raw_rows": 38993,
      "base_rows": 29132,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00034.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 35,
      "symbols": 50,
      "raw_rows": 53549,
      "base_rows": 39705,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00035.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 36,
      "symbols": 50,
      "raw_rows": 58454,
      "base_rows": 43091,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00036.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 37,
      "symbols": 50,
      "raw_rows": 44390,
      "base_rows": 32501,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00037.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 38,
      "symbols": 50,
      "raw_rows": 58087,
      "base_rows": 42969,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00038.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 39,
      "symbols": 50,
      "raw_rows": 60785,
      "base_rows": 44675,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00039.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 40,
      "symbols": 50,
      "raw_rows": 45301,
      "base_rows": 33468,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00040.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 41,
      "symbols": 50,
      "raw_rows": 74969,
      "base_rows": 58740,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00041.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 42,
      "symbols": 50,
      "raw_rows": 72420,
      "base_rows": 56947,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00042.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 43,
      "symbols": 50,
      "raw_rows": 73671,
      "base_rows": 57871,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00043.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 44,
      "symbols": 50,
      "raw_rows": 71385,
      "base_rows": 55695,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00044.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 45,
      "symbols": 50,
      "raw_rows": 73141,
      "base_rows": 57707,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00045.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 46,
      "symbols": 50,
      "raw_rows": 69798,
      "base_rows": 54536,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00046.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 47,
      "symbols": 50,
      "raw_rows": 70728,
      "base_rows": 55301,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00047.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 48,
      "symbols": 50,
      "raw_rows": 72591,
      "base_rows": 56220,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00048.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 49,
      "symbols": 50,
      "raw_rows": 73039,
      "base_rows": 56722,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00049.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 50,
      "symbols": 50,
      "raw_rows": 70846,
      "base_rows": 54800,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00050.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 51,
      "symbols": 50,
      "raw_rows": 70478,
      "base_rows": 54516,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00051.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 52,
      "symbols": 50,
      "raw_rows": 71535,
      "base_rows": 55277,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00052.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 53,
      "symbols": 50,
      "raw_rows": 72144,
      "base_rows": 55708,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00053.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 54,
      "symbols": 50,
      "raw_rows": 70616,
      "base_rows": 54317,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00054.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 55,
      "symbols": 50,
      "raw_rows": 73598,
      "base_rows": 56760,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00055.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 56,
      "symbols": 50,
      "raw_rows": 66515,
      "base_rows": 50604,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00056.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 57,
      "symbols": 50,
      "raw_rows": 66445,
      "base_rows": 50625,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00057.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 58,
      "symbols": 50,
      "raw_rows": 66113,
      "base_rows": 50671,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00058.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 59,
      "symbols": 50,
      "raw_rows": 65904,
      "base_rows": 50429,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00059.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 60,
      "symbols": 50,
      "raw_rows": 63398,
      "base_rows": 48155,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00060.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 61,
      "symbols": 50,
      "raw_rows": 63408,
      "base_rows": 48412,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00061.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 62,
      "symbols": 50,
      "raw_rows": 60946,
      "base_rows": 46970,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00062.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 63,
      "symbols": 50,
      "raw_rows": 62753,
      "base_rows": 48452,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00063.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 64,
      "symbols": 50,
      "raw_rows": 57243,
      "base_rows": 43921,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00064.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 65,
      "symbols": 50,
      "raw_rows": 50465,
      "base_rows": 38784,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00065.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 66,
      "symbols": 50,
      "raw_rows": 59121,
      "base_rows": 46398,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00066.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 67,
      "symbols": 50,
      "raw_rows": 75936,
      "base_rows": 59724,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00067.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 68,
      "symbols": 50,
      "raw_rows": 71826,
      "base_rows": 56603,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00068.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 69,
      "symbols": 50,
      "raw_rows": 74159,
      "base_rows": 58290,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00069.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 70,
      "symbols": 50,
      "raw_rows": 67739,
      "base_rows": 53431,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00070.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 71,
      "symbols": 50,
      "raw_rows": 69879,
      "base_rows": 54839,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00071.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 72,
      "symbols": 50,
      "raw_rows": 73437,
      "base_rows": 57776,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00072.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 73,
      "symbols": 50,
      "raw_rows": 73176,
      "base_rows": 57127,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00073.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 74,
      "symbols": 50,
      "raw_rows": 73875,
      "base_rows": 58206,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00074.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 75,
      "symbols": 50,
      "raw_rows": 72732,
      "base_rows": 56811,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00075.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 76,
      "symbols": 50,
      "raw_rows": 70650,
      "base_rows": 55070,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00076.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 77,
      "symbols": 50,
      "raw_rows": 70514,
      "base_rows": 55221,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00077.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 78,
      "symbols": 50,
      "raw_rows": 71842,
      "base_rows": 56139,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00078.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 79,
      "symbols": 50,
      "raw_rows": 70389,
      "base_rows": 55514,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00079.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 80,
      "symbols": 50,
      "raw_rows": 75815,
      "base_rows": 59023,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00080.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 81,
      "symbols": 50,
      "raw_rows": 75408,
      "base_rows": 58991,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00081.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 82,
      "symbols": 50,
      "raw_rows": 74889,
      "base_rows": 58872,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00082.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 83,
      "symbols": 50,
      "raw_rows": 76528,
      "base_rows": 60441,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00083.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 84,
      "symbols": 50,
      "raw_rows": 75222,
      "base_rows": 59592,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00084.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 85,
      "symbols": 50,
      "raw_rows": 79462,
      "base_rows": 63118,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00085.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 86,
      "symbols": 50,
      "raw_rows": 75180,
      "base_rows": 59351,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00086.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 87,
      "symbols": 50,
      "raw_rows": 69390,
      "base_rows": 52879,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00087.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 88,
      "symbols": 50,
      "raw_rows": 69152,
      "base_rows": 53197,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00088.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 89,
      "symbols": 50,
      "raw_rows": 66598,
      "base_rows": 50957,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00089.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 90,
      "symbols": 50,
      "raw_rows": 69601,
      "base_rows": 53251,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00090.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 91,
      "symbols": 50,
      "raw_rows": 71769,
      "base_rows": 54646,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00091.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 92,
      "symbols": 50,
      "raw_rows": 73421,
      "base_rows": 56183,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00092.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 93,
      "symbols": 50,
      "raw_rows": 71332,
      "base_rows": 54481,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00093.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 94,
      "symbols": 50,
      "raw_rows": 71586,
      "base_rows": 54453,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00094.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 95,
      "symbols": 50,
      "raw_rows": 71433,
      "base_rows": 54260,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00095.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 96,
      "symbols": 50,
      "raw_rows": 72168,
      "base_rows": 54760,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00096.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 97,
      "symbols": 50,
      "raw_rows": 70157,
      "base_rows": 53593,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00097.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 98,
      "symbols": 50,
      "raw_rows": 66185,
      "base_rows": 50033,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00098.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 99,
      "symbols": 50,
      "raw_rows": 67398,
      "base_rows": 51032,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00099.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 100,
      "symbols": 50,
      "raw_rows": 67514,
      "base_rows": 50934,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00100.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 101,
      "symbols": 50,
      "raw_rows": 60558,
      "base_rows": 45680,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00101.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 102,
      "symbols": 50,
      "raw_rows": 63258,
      "base_rows": 47520,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00102.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 103,
      "symbols": 50,
      "raw_rows": 61537,
      "base_rows": 46086,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00103.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 104,
      "symbols": 50,
      "raw_rows": 62541,
      "base_rows": 47251,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00104.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 105,
      "symbols": 50,
      "raw_rows": 62827,
      "base_rows": 47092,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00105.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 106,
      "symbols": 50,
      "raw_rows": 59160,
      "base_rows": 44220,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00106.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 107,
      "symbols": 50,
      "raw_rows": 54814,
      "base_rows": 41425,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00107.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 108,
      "symbols": 50,
      "raw_rows": 54034,
      "base_rows": 40532,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00108.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 109,
      "symbols": 50,
      "raw_rows": 53610,
      "base_rows": 39914,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00109.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 110,
      "symbols": 50,
      "raw_rows": 62249,
      "base_rows": 46798,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00110.parquet",
      "skipped_inputs": 0
    },
    {
      "batch_id": 111,
      "symbols": 26,
      "raw_rows": 11275,
      "base_rows": 8280,
      "output_path": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards/base_matrix_batch_00111.parquet",
      "skipped_inputs": 0
    }
  ]
}```

### A3. `swarm_best_20260219-030000_aa8abb7.json`
```json
{
  "status": "completed",
  "best_params": {
    "peace_threshold": 0.5253567667772991,
    "srl_resid_sigma_mult": 1.9773888188507172,
    "topo_energy_sigma_mult": 5.427559578121958,
    "max_depth": 5,
    "learning_rate": 0.006525909043483982,
    "subsample": 0.9382970275902356,
    "colsample_bytree": 0.7855991276821759
  },
  "best_value": 0.6101452643370191,
  "n_trials": 50,
  "n_completed": 20,
  "base_matrix": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet",
  "feature_cols": [
    "sigma_eff",
    "net_ofi",
    "depth_eff",
    "epiplexity",
    "srl_resid",
    "topo_area",
    "topo_energy",
    "topo_micro",
    "topo_classic",
    "topo_trend",
    "price_change",
    "bar_duration_ms",
    "adaptive_y",
    "epi_x_srl_resid",
    "epi_x_topo_area",
    "epi_x_net_ofi"
  ],
  "seconds": 28.56,
  "job_id": "8392580415252070400"
}```

### A4. `train_metrics_20260219-125410_78e36d9.json`
```json
{
  "status": "completed",
  "base_matrix_uri": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet",
  "base_rows": 5780139,
  "mask_rows": 2188,
  "total_training_rows": 2067,
  "seconds": 1.04,
  "job_id": "6022297228557680640",
  "model_uri": "gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl",
  "overrides": {
    "peace_threshold": 0.5253567667772991,
    "srl_resid_sigma_mult": 1.9773888188507172,
    "topo_energy_sigma_mult": 5.427559578121958,
    "xgb_max_depth": 5,
    "xgb_learning_rate": 0.006525909043483982,
    "xgb_subsample": 0.9382970275902356,
    "xgb_colsample_bytree": 0.7855991276821759,
    "num_boost_round": 150,
    "seed": 42
  }
}```

### A5. `backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`
```json
{
  "status": "completed",
  "files_matched": 263,
  "files_selected": 263,
  "files_used": 263,
  "day_span_selected": {
    "count": 263,
    "first": "20250102",
    "last": "20260130"
  },
  "day_span_used": {
    "count": 263,
    "first": "20250102",
    "last": "20260130"
  },
  "total_proc_rows": 8907595,
  "seconds": 1170.03,
  "model_uri": "gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl",
  "data_pattern": "gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet",
  "test_years": [
    "2025",
    "2026"
  ],
  "test_ym": [
    "2025",
    "202601"
  ],
  "split_guard": {
    "enforced": true,
    "test_years": [
      "2025",
      "2026"
    ],
    "test_ym": [
      "2025",
      "202601"
    ]
  },
  "overrides": {
    "peace_threshold": 0.5253567667772991,
    "srl_resid_sigma_mult": 1.9773888188507172,
    "topo_energy_sigma_mult": 5.427559578121958
  },
  "worker_plan": {
    "requested": 1,
    "min_workers": 1,
    "max_workers": 80,
    "start_workers": 80,
    "adaptive": false,
    "cpu_total": 80,
    "mem_total_gb": 629.87,
    "architecture": "global_causal_materialization",
    "reuse_precomputed_physics": true
  },
  "summary": {
    "Topo_SNR": 10.885431366882955,
    "Orthogonality": -0.0448054206835012,
    "Phys_Alignment": 0.5011822897884255,
    "Model_Alignment": 0.49742754220434177,
    "Vector_Alignment": 0.49742754220434177
  },
  "per_file_count": 1,
  "per_file": [
    {
      "source_uri": "global_continuum_manifold",
      "raw_rows": -1,
      "proc_rows": 8907595,
      "Topo_SNR": 10.885431366882955,
      "Orthogonality": -0.0448054206835012,
      "Phys_Alignment": 0.5011822897884255,
      "Model_Alignment": 0.49742754220434177,
      "Vector_Alignment": 0.49742754220434177
    }
  ]
}```

### A6. `backtest_metrics_smoke_n2std80_schemafix_20260219-164409.json`
```json
{
  "status": "completed",
  "files_matched": 263,
  "files_selected": 2,
  "files_used": 2,
  "day_span_selected": {
    "count": 2,
    "first": "20250103",
    "last": "20260128"
  },
  "day_span_used": {
    "count": 2,
    "first": "20250103",
    "last": "20260128"
  },
  "total_proc_rows": 62842,
  "seconds": 505.95,
  "model_uri": "gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl",
  "data_pattern": "gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet",
  "test_years": [
    "2025",
    "2026"
  ],
  "test_ym": [
    "2025",
    "202601"
  ],
  "split_guard": {
    "enforced": true,
    "test_years": [
      "2025",
      "2026"
    ],
    "test_ym": [
      "2025",
      "202601"
    ]
  },
  "overrides": {
    "peace_threshold": 0.5253567667772991,
    "srl_resid_sigma_mult": 1.9773888188507172,
    "topo_energy_sigma_mult": 5.427559578121958
  },
  "worker_plan": {
    "requested": 1,
    "min_workers": 1,
    "max_workers": 80,
    "start_workers": 80,
    "adaptive": false,
    "cpu_total": 80,
    "mem_total_gb": 314.87,
    "architecture": "global_causal_materialization"
  },
  "summary": {
    "Topo_SNR": 9.331698797292082,
    "Orthogonality": -0.03853562495575558,
    "Phys_Alignment": 0.514307662761667,
    "Model_Alignment": 0.4644709045515652,
    "Vector_Alignment": 0.4644709045515652
  },
  "per_file_count": 1,
  "per_file": [
    {
      "source_uri": "global_continuum_manifold",
      "raw_rows": -1,
      "proc_rows": 62842,
      "Topo_SNR": 9.331698797292082,
      "Orthogonality": -0.03853562495575558,
      "Phys_Alignment": 0.514307662761667,
      "Model_Alignment": 0.4644709045515652,
      "Vector_Alignment": 0.4644709045515652
    }
  ]
}```

---

## Appendix B: Raw Job Tables

### B1. Selected timeline (`job_timeline_selected.txt`)
```text
ID STATE CREATE START END DISPLAY
1959559432727691264  JOB_STATE_SUCCEEDED  2026-02-19T18:48:55.655224Z  2026-02-19T18:49:11Z  2026-02-19T19:09:19Z         omega-v60-run_cloud_backtest-20260220-024852
6945888645156962304  JOB_STATE_CANCELLED  2026-02-19T18:25:18.416896Z  2026-02-19T18:27:57Z  2026-02-19T18:48:34.591923Z  omega-v60-run_cloud_backtest-20260220-022514
3366793578792615936  JOB_STATE_FAILED     2026-02-19T17:40:10.099168Z  2026-02-19T17:42:34Z  2026-02-19T18:20:46Z         omega-v60-run_cloud_backtest-20260220-014005
1475563210273718272  JOB_STATE_FAILED     2026-02-19T17:20:26.977060Z  2026-02-19T17:23:48Z  2026-02-19T17:38:22Z         omega-v60-run_cloud_backtest-20260220-012023
6324251159091478528  JOB_STATE_FAILED     2026-02-19T17:03:34.035308Z  2026-02-19T17:08:28Z  2026-02-19T17:18:31Z         omega-v60-run_cloud_backtest-20260220-010330
4089128737776336896  JOB_STATE_SUCCEEDED  2026-02-19T16:44:16.666746Z  2026-02-19T16:46:40Z  2026-02-19T16:55:13Z         omega-v60-run_cloud_backtest-20260220-004413
8385422044799434752  JOB_STATE_FAILED     2026-02-19T15:41:01.221270Z  2026-02-19T15:45:48Z  2026-02-19T15:58:23Z         omega-v60-run_cloud_backtest-20260219-234057
1324903728989339648  JOB_STATE_FAILED     2026-02-19T15:24:38.556769Z  2026-02-19T15:26:45Z  2026-02-19T15:40:50Z         omega-v60-run_cloud_backtest-20260219-232435
4745526734198145024  JOB_STATE_CANCELLED  2026-02-19T13:10:48.617413Z  2026-02-19T13:13:42Z  2026-02-19T15:17:25.878592Z  omega-v60-run_cloud_backtest-20260219-211045
4665024890858897408  JOB_STATE_FAILED     2026-02-19T13:02:53.695929Z  2026-02-19T13:04:30Z  2026-02-19T13:10:02Z         omega-v60-run_cloud_backtest-20260219-210249
320740100306632704   JOB_STATE_FAILED     2026-02-19T12:58:05.025482Z  2026-02-19T13:00:36Z  2026-02-19T13:02:07Z         omega-v60-run_cloud_backtest-20260219-205801
6022297228557680640  JOB_STATE_SUCCEEDED  2026-02-19T12:54:17.783874Z  2026-02-19T12:56:47Z  2026-02-19T12:57:47Z         omega-v60-run_vertex_xgb_train-20260219-205414
4026903526469795840  JOB_STATE_CANCELLED  2026-02-19T03:21:45.491294Z  2026-02-19T03:24:24Z  2026-02-19T11:55:51.934820Z  omega-v60-run_vertex_xgb_train-20260219-112142
8392580415252070400  JOB_STATE_SUCCEEDED  2026-02-19T03:15:48.956931Z  2026-02-19T03:19:50Z  2026-02-19T03:21:21Z         omega-v60-v60_swarm_xgb-20260219-111545
```

### B2. `run_vertex_base_matrix` jobs in `us-west1` (`base_matrix_vertex_jobs_uswest1.txt`)
```text
6420510876662497280  JOB_STATE_FAILED     2026-02-18T00:11:24.408664Z  2026-02-18T08:40:11Z         2026-02-18T08:45:42Z         omega-v60-run_vertex_base_matrix-20260218-081120
686760047950168064   JOB_STATE_FAILED     2026-02-17T20:59:11.277937Z  2026-02-18T02:28:24Z         2026-02-18T08:36:50Z         omega-v60-run_vertex_base_matrix-20260218-045907
568540557731692544   JOB_STATE_FAILED     2026-02-17T20:16:03.169749Z  2026-02-17T20:19:03Z         2026-02-18T02:26:27Z         omega-v60-run_vertex_base_matrix-20260218-041559
2730549853846241280  JOB_STATE_CANCELLED  2026-02-17T14:01:49.753013Z  2026-02-17T14:02:47Z         2026-02-17T20:02:19.892680Z  omega-v60-run_vertex_base_matrix-20260217-220146
8578473969986830336  JOB_STATE_CANCELLED  2026-02-17T13:47:41.884194Z  2026-02-17T13:50:03Z         2026-02-17T14:02:08.879925Z  omega-v60-run_vertex_base_matrix-20260217-214738
7968236220478128128  JOB_STATE_FAILED     2026-02-17T13:26:08.701083Z  2026-02-17T13:26:29Z         2026-02-17T13:40:33Z         omega-v60-run_vertex_base_matrix-20260217-212604
178134765034012672   JOB_STATE_CANCELLED  2026-02-17T13:20:31.362723Z  2026-02-17T13:23:01Z         2026-02-17T13:26:09.348103Z  omega-v60-run_vertex_base_matrix-20260217-212027
5958504886764044288  JOB_STATE_FAILED     2026-02-17T12:49:03.193875Z  2026-02-17T12:51:14Z         2026-02-17T13:06:47Z         omega-v60-run_vertex_base_matrix-20260217-204858
1968315616913784832  JOB_STATE_FAILED     2026-02-17T12:35:13.742420Z  2026-02-17T12:37:33Z         2026-02-17T12:43:35Z         omega-v60-run_vertex_base_matrix-20260217-203509
2103423605734899712  JOB_STATE_FAILED     2026-02-17T12:22:51.057725Z  2026-02-17T12:24:52Z         2026-02-17T12:31:54Z         omega-v60-run_vertex_base_matrix-20260217-202247
702804121622675456   JOB_STATE_FAILED     2026-02-17T12:02:52.495460Z  2026-02-17T12:11:45Z         2026-02-17T12:18:46Z         omega-v60-run_vertex_base_matrix-20260217-200248
1715691825315971072  JOB_STATE_CANCELLED  2026-02-17T11:23:01.168289Z  2026-02-17T11:23:01.276054Z  2026-02-17T11:23:49.147190Z  omega-v60-run_vertex_base_matrix-20260217-192257
4505671794471993344  JOB_STATE_CANCELLED  2026-02-17T11:18:18.716359Z  2026-02-17T11:18:18.826597Z  2026-02-17T11:20:34.673085Z  omega-v60-run_vertex_base_matrix-20260217-191815
3749067057073750016  JOB_STATE_SUCCEEDED  2026-02-17T11:09:11.497390Z  2026-02-17T11:10:53Z         2026-02-17T11:12:23Z         omega-v60-run_vertex_base_matrix-20260217-190907
200230550705799168   JOB_STATE_FAILED     2026-02-17T11:04:47.051516Z  2026-02-17T11:07:05Z         2026-02-17T11:08:05Z         omega-v60-run_vertex_base_matrix-20260217-190443
5258898832149708800  JOB_STATE_FAILED     2026-02-17T10:59:48.169324Z  2026-02-17T11:02:13Z         2026-02-17T11:04:13Z         omega-v60-run_vertex_base_matrix-20260217-185944
8825749737027141632  JOB_STATE_FAILED     2026-02-17T10:54:16.282568Z  2026-02-17T10:57:25Z         2026-02-17T10:58:55Z         omega-v60-run_vertex_base_matrix-20260217-185412
9059936917650407424  JOB_STATE_CANCELLED  2026-02-17T10:54:03.803587Z  2026-02-17T10:54:03.921466Z  2026-02-17T10:55:19.464322Z  omega-v60-run_vertex_base_matrix-20260217-185335
4749992074256842752  JOB_STATE_CANCELLED  2026-02-17T10:51:38.757306Z  2026-02-17T10:51:38.860315Z  2026-02-17T10:52:35.197595Z  omega-v60-run_vertex_base_matrix-20260217-184803
5601172403829866496  JOB_STATE_CANCELLED  2026-02-17T10:51:19.134066Z  2026-02-17T10:51:19.242916Z  2026-02-17T10:53:27.703699Z  omega-v60-run_vertex_base_matrix-20260217-185051
```

### B3. Key fields from job describe (`job_describe_key_fields.txt`)
```text
===== 6324251159091478528 =====
2:  "createTime": "2026-02-19T17:03:34.035308Z",
3:  "displayName": "omega-v60-run_cloud_backtest-20260220-010330",
4:  "endTime": "2026-02-19T17:18:31Z",
5:  "error": {
6:    "code": 8,
7:    "message": "Replicas low on memory: workerpool0. Specify a machine with larger memory and try again."
27:          "machineType": "n2-standard-80"
34:  "startTime": "2026-02-19T17:08:28Z",
35:  "state": "JOB_STATE_FAILED",
===== 1475563210273718272 =====
2:  "createTime": "2026-02-19T17:20:26.977060Z",
3:  "displayName": "omega-v60-run_cloud_backtest-20260220-012023",
4:  "endTime": "2026-02-19T17:38:22Z",
5:  "error": {
6:    "code": 8,
7:    "message": "Replicas low on memory: workerpool0. Specify a machine with larger memory and try again."
27:          "machineType": "n2-highmem-64"
34:  "startTime": "2026-02-19T17:23:48Z",
35:  "state": "JOB_STATE_FAILED",
===== 3366793578792615936 =====
2:  "createTime": "2026-02-19T17:40:10.099168Z",
3:  "displayName": "omega-v60-run_cloud_backtest-20260220-014005",
4:  "endTime": "2026-02-19T18:20:46Z",
5:  "error": {
6:    "code": 8,
7:    "message": "Replicas low on memory: workerpool0. Specify a machine with larger memory and try again."
27:          "machineType": "n2-highmem-80"
34:  "startTime": "2026-02-19T17:42:34Z",
35:  "state": "JOB_STATE_FAILED",
===== 6945888645156962304 =====
2:  "createTime": "2026-02-19T18:25:18.416896Z",
3:  "displayName": "omega-v60-run_cloud_backtest-20260220-022514",
4:  "endTime": "2026-02-19T18:48:34.591923Z",
5:  "error": {
6:    "code": 1,
7:    "message": "CANCELED"
27:          "machineType": "n2-highmem-80"
34:  "startTime": "2026-02-19T18:27:57Z",
35:  "state": "JOB_STATE_CANCELLED",
===== 1959559432727691264 =====
2:  "createTime": "2026-02-19T18:48:55.655224Z",
3:  "displayName": "omega-v60-run_cloud_backtest-20260220-024852",
4:  "endTime": "2026-02-19T19:09:19Z",
23:          "machineType": "n2-highmem-80"
30:  "startTime": "2026-02-19T18:49:11Z",
31:  "state": "JOB_STATE_SUCCEEDED",
===== 6022297228557680640 =====
2:  "createTime": "2026-02-19T12:54:17.783874Z",
3:  "displayName": "omega-v60-run_vertex_xgb_train-20260219-205414",
4:  "endTime": "2026-02-19T12:57:47Z",
23:          "machineType": "n2-standard-16"
30:  "startTime": "2026-02-19T12:56:47Z",
31:  "state": "JOB_STATE_SUCCEEDED",
===== 4026903526469795840 =====
2:  "createTime": "2026-02-19T03:21:45.491294Z",
3:  "displayName": "omega-v60-run_vertex_xgb_train-20260219-112142",
4:  "endTime": "2026-02-19T11:55:51.934820Z",
5:  "error": {
6:    "code": 1,
7:    "message": "CANCELED"
27:          "machineType": "n1-standard-32"
34:  "startTime": "2026-02-19T03:24:24Z",
35:  "state": "JOB_STATE_CANCELLED",
===== 8392580415252070400 =====
2:  "createTime": "2026-02-19T03:15:48.956931Z",
3:  "displayName": "omega-v60-v60_swarm_xgb-20260219-111545",
4:  "endTime": "2026-02-19T03:21:21Z",
23:          "machineType": "e2-highmem-16"
30:  "startTime": "2026-02-19T03:19:50Z",
31:  "state": "JOB_STATE_SUCCEEDED",
===== 4089128737776336896 =====
2:  "createTime": "2026-02-19T16:44:16.666746Z",
3:  "displayName": "omega-v60-run_cloud_backtest-20260220-004413",
4:  "endTime": "2026-02-19T16:55:13Z",
23:          "machineType": "n2-standard-80"
30:  "startTime": "2026-02-19T16:46:40Z",
31:  "state": "JOB_STATE_SUCCEEDED",
```

---

## Appendix C: Raw Job Describe JSON (Copy-Paste)

### C1. `job_8392580415252070400.describe.json`
```json
{
  "createTime": "2026-02-19T03:15:48.956931Z",
  "displayName": "omega-v60-v60_swarm_xgb-20260219-111545",
  "endTime": "2026-02-19T03:21:21Z",
  "jobSpec": {
    "workerPoolSpecs": [
      {
        "containerSpec": {
          "args": [
            "set -euxo pipefail\npython3 -m pip install --quiet google-cloud-storage\npython3 - <<'PY'\nfrom google.cloud import storage\nimport shutil\n\ndef dl(uri: str, out: str) -> None:\n    clean = uri.replace(\"gs://\", \"\", 1)\n    bucket, blob = clean.split(\"/\", 1)\n    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)\n\ndl(\"gs://omega_v52/staging/code/omega_core.zip\", \"omega_core.zip\")\ndl(\"gs://omega_v52/staging/code/payloads/omega-v60-v60_swarm_xgb-20260219-111545_v60_swarm_xgb.py\", \"payload.py\")\nshutil.unpack_archive(\"omega_core.zip\", extract_dir=\".\")\nPY\npython3 -u payload.py --bootstrap-code --install-deps --base-matrix-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet --n-trials=50 --min-samples=2000 --seed=42 --output-uri=gs://omega_v52_central/omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json\n"
          ],
          "command": [
            "/bin/bash",
            "-lc"
          ],
          "imageUri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest"
        },
        "diskSpec": {
          "bootDiskSizeGb": 100,
          "bootDiskType": "pd-ssd"
        },
        "machineSpec": {
          "machineType": "e2-highmem-16"
        },
        "replicaCount": "1"
      }
    ]
  },
  "name": "projects/269018079180/locations/us-central1/customJobs/8392580415252070400",
  "startTime": "2026-02-19T03:19:50Z",
  "state": "JOB_STATE_SUCCEEDED",
  "updateTime": "2026-02-19T03:21:22.256317Z"
}
```

### C2. `job_4026903526469795840.describe.json`
```json
{
  "createTime": "2026-02-19T03:21:45.491294Z",
  "displayName": "omega-v60-run_vertex_xgb_train-20260219-112142",
  "endTime": "2026-02-19T11:55:51.934820Z",
  "error": {
    "code": 1,
    "message": "CANCELED"
  },
  "jobSpec": {
    "workerPoolSpecs": [
      {
        "containerSpec": {
          "args": [
            "set -euxo pipefail\npython3 -m pip install --quiet google-cloud-storage\npython3 - <<'PY'\nfrom google.cloud import storage\nimport shutil\n\ndef dl(uri: str, out: str) -> None:\n    clean = uri.replace(\"gs://\", \"\", 1)\n    bucket, blob = clean.split(\"/\", 1)\n    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)\n\ndl(\"gs://omega_v52/staging/code/omega_core.zip\", \"omega_core.zip\")\ndl(\"gs://omega_v52/staging/code/payloads/omega-v60-run_vertex_xgb_train-20260219-112142_run_vertex_xgb_train.py\", \"payload.py\")\nshutil.unpack_archive(\"omega_core.zip\", extract_dir=\".\")\nPY\npython3 -u payload.py '--data-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet' --train-years=2023,2024 --output-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-030000_aa8abb7 --max-files=0 --max-rows-per-file=0 --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958 --xgb-max-depth=5 --xgb-learning-rate=0.006525909043483982 --xgb-subsample=0.9382970275902356 --xgb-colsample-bytree=0.7855991276821759\n"
          ],
          "command": [
            "/bin/bash",
            "-lc"
          ],
          "imageUri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest"
        },
        "diskSpec": {
          "bootDiskSizeGb": 100,
          "bootDiskType": "pd-ssd"
        },
        "machineSpec": {
          "machineType": "n1-standard-32"
        },
        "replicaCount": "1"
      }
    ]
  },
  "name": "projects/269018079180/locations/us-central1/customJobs/4026903526469795840",
  "startTime": "2026-02-19T03:24:24Z",
  "state": "JOB_STATE_CANCELLED",
  "updateTime": "2026-02-19T11:55:51.934820Z"
}
```

### C3. `job_6022297228557680640.describe.json`
```json
{
  "createTime": "2026-02-19T12:54:17.783874Z",
  "displayName": "omega-v60-run_vertex_xgb_train-20260219-205414",
  "endTime": "2026-02-19T12:57:47Z",
  "jobSpec": {
    "workerPoolSpecs": [
      {
        "containerSpec": {
          "args": [
            "set -euxo pipefail\npython3 -m pip install --quiet google-cloud-storage\npython3 - <<'PY'\nfrom google.cloud import storage\nimport shutil\n\ndef dl(uri: str, out: str) -> None:\n    clean = uri.replace(\"gs://\", \"\", 1)\n    bucket, blob = clean.split(\"/\", 1)\n    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)\n\ndl(\"gs://omega_v52_central/omega/staging/code/omega_core_20260219-125410_78e36d9.zip\", \"omega_core.zip\")\ndl(\"gs://omega_v52/staging/code/payloads/omega-v60-run_vertex_xgb_train-20260219-205414_run_vertex_xgb_train.py\", \"payload.py\")\nshutil.unpack_archive(\"omega_core.zip\", extract_dir=\".\")\nPY\npython3 -u payload.py --base-matrix-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet --code-bundle-uri=gs://omega_v52_central/omega/staging/code/omega_core_20260219-125410_78e36d9.zip --output-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9 --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958 --xgb-max-depth=5 --xgb-learning-rate=0.006525909043483982 --xgb-subsample=0.9382970275902356 --xgb-colsample-bytree=0.7855991276821759\n"
          ],
          "command": [
            "/bin/bash",
            "-lc"
          ],
          "imageUri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest"
        },
        "diskSpec": {
          "bootDiskSizeGb": 100,
          "bootDiskType": "pd-ssd"
        },
        "machineSpec": {
          "machineType": "n2-standard-16"
        },
        "replicaCount": "1"
      }
    ]
  },
  "name": "projects/269018079180/locations/us-central1/customJobs/6022297228557680640",
  "startTime": "2026-02-19T12:56:47Z",
  "state": "JOB_STATE_SUCCEEDED",
  "updateTime": "2026-02-19T12:57:49.090409Z"
}
```

### C4. `job_6324251159091478528.describe.json`
```json
{
  "createTime": "2026-02-19T17:03:34.035308Z",
  "displayName": "omega-v60-run_cloud_backtest-20260220-010330",
  "endTime": "2026-02-19T17:18:31Z",
  "error": {
    "code": 8,
    "message": "Replicas low on memory: workerpool0. Specify a machine with larger memory and try again."
  },
  "jobSpec": {
    "workerPoolSpecs": [
      {
        "containerSpec": {
          "args": [
            "set -euxo pipefail\npython3 -m pip install --quiet google-cloud-storage\npython3 - <<'PY'\nfrom google.cloud import storage\nimport shutil\n\ndef dl(uri: str, out: str) -> None:\n    clean = uri.replace(\"gs://\", \"\", 1)\n    bucket, blob = clean.split(\"/\", 1)\n    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)\n\ndl(\"gs://omega_v52_central/omega/staging/code/omega_core_20260219-170326_n2fullfix.zip\", \"omega_core.zip\")\ndl(\"gs://omega_v52/staging/code/payloads/omega-v60-run_cloud_backtest-20260220-010330_run_cloud_backtest.py\", \"payload.py\")\nshutil.unpack_archive(\"omega_core.zip\", extract_dir=\".\")\nPY\npython3 -u payload.py --code-bundle-uri=gs://omega_v52_central/omega/staging/code/omega_core_20260219-170326_n2fullfix.zip '--data-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet' --test-years=2025,2026 --test-ym=2025,202601 --max-files=0 --max-rows-per-file=0 --model-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl --output-uri=gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2standard80_schemafix_full_20260219-170326.json --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958\n"
          ],
          "command": [
            "/bin/bash",
            "-lc"
          ],
          "imageUri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest"
        },
        "diskSpec": {
          "bootDiskSizeGb": 100,
          "bootDiskType": "pd-ssd"
        },
        "machineSpec": {
          "machineType": "n2-standard-80"
        },
        "replicaCount": "1"
      }
    ]
  },
  "name": "projects/269018079180/locations/us-central1/customJobs/6324251159091478528",
  "startTime": "2026-02-19T17:08:28Z",
  "state": "JOB_STATE_FAILED",
  "updateTime": "2026-02-19T17:18:50.380300Z"
}
```

### C5. `job_1475563210273718272.describe.json`
```json
{
  "createTime": "2026-02-19T17:20:26.977060Z",
  "displayName": "omega-v60-run_cloud_backtest-20260220-012023",
  "endTime": "2026-02-19T17:38:22Z",
  "error": {
    "code": 8,
    "message": "Replicas low on memory: workerpool0. Specify a machine with larger memory and try again."
  },
  "jobSpec": {
    "workerPoolSpecs": [
      {
        "containerSpec": {
          "args": [
            "set -euxo pipefail\npython3 -m pip install --quiet google-cloud-storage\npython3 - <<'PY'\nfrom google.cloud import storage\nimport shutil\n\ndef dl(uri: str, out: str) -> None:\n    clean = uri.replace(\"gs://\", \"\", 1)\n    bucket, blob = clean.split(\"/\", 1)\n    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)\n\ndl(\"gs://omega_v52_central/omega/staging/code/omega_core_20260219-172020_n2highmem64.zip\", \"omega_core.zip\")\ndl(\"gs://omega_v52/staging/code/payloads/omega-v60-run_cloud_backtest-20260220-012023_run_cloud_backtest.py\", \"payload.py\")\nshutil.unpack_archive(\"omega_core.zip\", extract_dir=\".\")\nPY\npython3 -u payload.py --code-bundle-uri=gs://omega_v52_central/omega/staging/code/omega_core_20260219-172020_n2highmem64.zip '--data-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet' --test-years=2025,2026 --test-ym=2025,202601 --max-files=0 --max-rows-per-file=0 --model-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl --output-uri=gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem64_schemafix_full_20260219-172020.json --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958\n"
          ],
          "command": [
            "/bin/bash",
            "-lc"
          ],
          "imageUri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest"
        },
        "diskSpec": {
          "bootDiskSizeGb": 100,
          "bootDiskType": "pd-ssd"
        },
        "machineSpec": {
          "machineType": "n2-highmem-64"
        },
        "replicaCount": "1"
      }
    ]
  },
  "name": "projects/269018079180/locations/us-central1/customJobs/1475563210273718272",
  "startTime": "2026-02-19T17:23:48Z",
  "state": "JOB_STATE_FAILED",
  "updateTime": "2026-02-19T17:38:42.615082Z"
}
```

### C6. `job_3366793578792615936.describe.json`
```json
{
  "createTime": "2026-02-19T17:40:10.099168Z",
  "displayName": "omega-v60-run_cloud_backtest-20260220-014005",
  "endTime": "2026-02-19T18:20:46Z",
  "error": {
    "code": 8,
    "message": "Replicas low on memory: workerpool0. Specify a machine with larger memory and try again."
  },
  "jobSpec": {
    "workerPoolSpecs": [
      {
        "containerSpec": {
          "args": [
            "set -euxo pipefail\npython3 -m pip install --quiet google-cloud-storage\npython3 - <<'PY'\nfrom google.cloud import storage\nimport shutil\n\ndef dl(uri: str, out: str) -> None:\n    clean = uri.replace(\"gs://\", \"\", 1)\n    bucket, blob = clean.split(\"/\", 1)\n    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)\n\ndl(\"gs://omega_v52_central/omega/staging/code/omega_core_20260219-174002_n2highmem80.zip\", \"omega_core.zip\")\ndl(\"gs://omega_v52/staging/code/payloads/omega-v60-run_cloud_backtest-20260220-014005_run_cloud_backtest.py\", \"payload.py\")\nshutil.unpack_archive(\"omega_core.zip\", extract_dir=\".\")\nPY\npython3 -u payload.py --code-bundle-uri=gs://omega_v52_central/omega/staging/code/omega_core_20260219-174002_n2highmem80.zip '--data-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet' --test-years=2025,2026 --test-ym=2025,202601 --max-files=0 --max-rows-per-file=0 --model-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl --output-uri=gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem80_schemafix_full_20260219-174002.json --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958\n"
          ],
          "command": [
            "/bin/bash",
            "-lc"
          ],
          "imageUri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest"
        },
        "diskSpec": {
          "bootDiskSizeGb": 100,
          "bootDiskType": "pd-ssd"
        },
        "machineSpec": {
          "machineType": "n2-highmem-80"
        },
        "replicaCount": "1"
      }
    ]
  },
  "name": "projects/269018079180/locations/us-central1/customJobs/3366793578792615936",
  "startTime": "2026-02-19T17:42:34Z",
  "state": "JOB_STATE_FAILED",
  "updateTime": "2026-02-19T18:21:15.094114Z"
}
```

### C7. `job_6945888645156962304.describe.json`
```json
{
  "createTime": "2026-02-19T18:25:18.416896Z",
  "displayName": "omega-v60-run_cloud_backtest-20260220-022514",
  "endTime": "2026-02-19T18:48:34.591923Z",
  "error": {
    "code": 1,
    "message": "CANCELED"
  },
  "jobSpec": {
    "workerPoolSpecs": [
      {
        "containerSpec": {
          "args": [
            "set -euxo pipefail\npython3 -m pip install --quiet google-cloud-storage\npython3 - <<'PY'\nfrom google.cloud import storage\nimport shutil\n\ndef dl(uri: str, out: str) -> None:\n    clean = uri.replace(\"gs://\", \"\", 1)\n    bucket, blob = clean.split(\"/\", 1)\n    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)\n\ndl(\"gs://omega_v52_central/omega/staging/code/omega_core_20260220-022511_n2highmem80_reusephysics.zip\", \"omega_core.zip\")\ndl(\"gs://omega_v52/staging/code/payloads/omega-v60-run_cloud_backtest-20260220-022514_run_cloud_backtest.py\", \"payload.py\")\nshutil.unpack_archive(\"omega_core.zip\", extract_dir=\".\")\nPY\npython3 -u payload.py --code-bundle-uri=gs://omega_v52_central/omega/staging/code/omega_core_20260220-022511_n2highmem80_reusephysics.zip '--data-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet' --test-years=2025,2026 --test-ym=2025,202601 --max-files=0 --max-rows-per-file=0 --max-eval-traces=50000 --model-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl --output-uri=gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_20260220-022511.json --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958\n"
          ],
          "command": [
            "/bin/bash",
            "-lc"
          ],
          "imageUri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest"
        },
        "diskSpec": {
          "bootDiskSizeGb": 100,
          "bootDiskType": "pd-ssd"
        },
        "machineSpec": {
          "machineType": "n2-highmem-80"
        },
        "replicaCount": "1"
      }
    ]
  },
  "name": "projects/269018079180/locations/us-central1/customJobs/6945888645156962304",
  "startTime": "2026-02-19T18:27:57Z",
  "state": "JOB_STATE_CANCELLED",
  "updateTime": "2026-02-19T18:48:34.591923Z"
}
```

### C8. `job_1959559432727691264.describe.json`
```json
{
  "createTime": "2026-02-19T18:48:55.655224Z",
  "displayName": "omega-v60-run_cloud_backtest-20260220-024852",
  "endTime": "2026-02-19T19:09:19Z",
  "jobSpec": {
    "workerPoolSpecs": [
      {
        "containerSpec": {
          "args": [
            "set -euxo pipefail\npython3 -m pip install --quiet google-cloud-storage\npython3 - <<'PY'\nfrom google.cloud import storage\nimport shutil\n\ndef dl(uri: str, out: str) -> None:\n    clean = uri.replace(\"gs://\", \"\", 1)\n    bucket, blob = clean.split(\"/\", 1)\n    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)\n\ndl(\"gs://omega_v52_central/omega/staging/code/omega_core_20260220-024848_n2highmem80_reusephysics_dw16.zip\", \"omega_core.zip\")\ndl(\"gs://omega_v52/staging/code/payloads/omega-v60-run_cloud_backtest-20260220-024852_run_cloud_backtest.py\", \"payload.py\")\nshutil.unpack_archive(\"omega_core.zip\", extract_dir=\".\")\nPY\npython3 -u payload.py --code-bundle-uri=gs://omega_v52_central/omega/staging/code/omega_core_20260220-024848_n2highmem80_reusephysics_dw16.zip '--data-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet' --test-years=2025,2026 --test-ym=2025,202601 --max-files=0 --max-rows-per-file=0 --max-eval-traces=50000 --download-workers=16 --model-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl --output-uri=gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958\n"
          ],
          "command": [
            "/bin/bash",
            "-lc"
          ],
          "imageUri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest"
        },
        "diskSpec": {
          "bootDiskSizeGb": 100,
          "bootDiskType": "pd-ssd"
        },
        "machineSpec": {
          "machineType": "n2-highmem-80"
        },
        "replicaCount": "1"
      }
    ]
  },
  "name": "projects/269018079180/locations/us-central1/customJobs/1959559432727691264",
  "startTime": "2026-02-19T18:49:11Z",
  "state": "JOB_STATE_SUCCEEDED",
  "updateTime": "2026-02-19T19:09:43.238699Z"
}
```

---

## Appendix D: Raw Key Log Extracts

### D1. Optimization (`optimization_log_key_lines.txt`)
```text
270:    "textPayload": "+ python3 -u payload.py --bootstrap-code --install-deps --base-matrix-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet --n-trials=50 --min-samples=2000 --seed=42 --output-uri=gs://omega_v52_central/omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json",
2426:    "textPayload": "Loading Base Matrix into RAM: /base_matrix.parquet",
2470:    "textPayload": "[I 2026-02-19 03:20:49,721] Trial 0 pruned. Physics collapse too severe. Insufficient signals.",
2492:    "textPayload": "[I 2026-02-19 03:20:49,817] Trial 1 pruned. Physics collapse too severe. Insufficient signals.",
2514:    "textPayload": "[I 2026-02-19 03:20:49,914] Trial 2 pruned. Physics collapse too severe. Insufficient signals.",
2536:    "textPayload": "[I 2026-02-19 03:20:50,007] Trial 3 pruned. Physics collapse too severe. Insufficient signals.",
2558:    "textPayload": "[I 2026-02-19 03:20:50,103] Trial 4 pruned. Physics collapse too severe. Insufficient signals.",
2580:    "textPayload": "[I 2026-02-19 03:20:50,189] Trial 5 pruned. Physics collapse too severe. Insufficient signals.",
2602:    "textPayload": "[I 2026-02-19 03:20:50,283] Trial 6 pruned. Physics collapse too severe. Insufficient signals.",
2624:    "textPayload": "[I 2026-02-19 03:20:50,374] Trial 7 pruned. Physics collapse too severe. Insufficient signals.",
2646:    "textPayload": "[I 2026-02-19 03:20:50,467] Trial 8 pruned. Physics collapse too severe. Insufficient signals.",
2668:    "textPayload": "[I 2026-02-19 03:20:50,560] Trial 9 pruned. Physics collapse too severe. Insufficient signals.",
2690:    "textPayload": "[I 2026-02-19 03:20:52,408] Trial 10 finished with value: 0.5654896532764886 and parameters: {'peace_threshold': 0.3373677907759919, 'srl_resid_sigma_mult': 1.3326356014894118, 'topo_energy_sigma_mult': 3.0383511234389857, 'max_depth': 7, 'learning_rate': 0.015817566588447754, 'subsample': 0.9927930003170996, 'colsample_bytree': 0.6054983291789089}. Best is trial 10 with value: 0.5654896532764886.",
2712:    "textPayload": "[I 2026-02-19 03:20:55,531] Trial 11 finished with value: 0.5607162584318046 and parameters: {'peace_threshold': 0.30160439148356666, 'srl_resid_sigma_mult': 1.3164962156190987, 'topo_energy_sigma_mult': 2.6368238389261625, 'max_depth': 7, 'learning_rate': 0.015867957910748354, 'subsample': 0.9936961443368941, 'colsample_bytree': 0.6029641975778192}. Best is trial 10 with value: 0.5654896532764886.",
2734:    "textPayload": "[I 2026-02-19 03:20:58,444] Trial 12 finished with value: 0.5553998263153069 and parameters: {'peace_threshold': 0.3227636748411618, 'srl_resid_sigma_mult': 1.073016449716213, 'topo_energy_sigma_mult': 2.070428523717874, 'max_depth': 7, 'learning_rate': 0.012049787974989136, 'subsample': 0.6070111455018068, 'colsample_bytree': 0.6119345013948678}. Best is trial 10 with value: 0.5654896532764886.",
2756:    "textPayload": "[I 2026-02-19 03:21:00,102] Trial 13 finished with value: 0.5563715978790658 and parameters: {'peace_threshold': 0.44491900137501084, 'srl_resid_sigma_mult': 2.4972315391927644, 'topo_energy_sigma_mult': 2.231624223307584, 'max_depth': 7, 'learning_rate': 0.015326537291711722, 'subsample': 0.9920859173337643, 'colsample_bytree': 0.6006721659817366}. Best is trial 10 with value: 0.5654896532764886.",
2778:    "textPayload": "[I 2026-02-19 03:21:00,195] Trial 14 pruned. Physics collapse too severe. Insufficient signals.",
2800:    "textPayload": "[I 2026-02-19 03:21:00,831] Trial 15 finished with value: 0.5752291664850757 and parameters: {'peace_threshold': 0.5655631326200726, 'srl_resid_sigma_mult': 1.8196476786009002, 'topo_energy_sigma_mult': 4.329754095342601, 'max_depth': 6, 'learning_rate': 0.007600940347097257, 'subsample': 0.9259783624244668, 'colsample_bytree': 0.6706508128403437}. Best is trial 15 with value: 0.5752291664850757.",
2822:    "textPayload": "[I 2026-02-19 03:21:00,918] Trial 16 pruned. Physics collapse too severe. Insufficient signals.",
2844:    "textPayload": "[I 2026-02-19 03:21:01,768] Trial 17 finished with value: 0.56734888940245 and parameters: {'peace_threshold': 0.419872717379817, 'srl_resid_sigma_mult': 1.9827471258358362, 'topo_energy_sigma_mult': 4.347412579100048, 'max_depth': 6, 'learning_rate': 0.008516173055229209, 'subsample': 0.8812921477523739, 'colsample_bytree': 0.7348050246485016}. Best is trial 15 with value: 0.5752291664850757.",
2866:    "textPayload": "[I 2026-02-19 03:21:01,862] Trial 18 pruned. Physics collapse too severe. Insufficient signals.",
2888:    "textPayload": "[I 2026-02-19 03:21:01,952] Trial 19 pruned. Physics collapse too severe. Insufficient signals.",
2910:    "textPayload": "[I 2026-02-19 03:21:02,402] Trial 20 finished with value: 0.6012326440752094 and parameters: {'peace_threshold': 0.524462975533486, 'srl_resid_sigma_mult': 1.932811994113962, 'topo_energy_sigma_mult': 5.502560436609094, 'max_depth': 5, 'learning_rate': 0.0055209943891839355, 'subsample': 0.9439688178671944, 'colsample_bytree': 0.7990851784951422}. Best is trial 20 with value: 0.6012326440752094.",
2932:    "textPayload": "[I 2026-02-19 03:21:03,599] Trial 21 finished with value: 0.6101452643370191 and parameters: {'peace_threshold': 0.5253567667772991, 'srl_resid_sigma_mult': 1.9773888188507172, 'topo_energy_sigma_mult': 5.427559578121958, 'max_depth': 5, 'learning_rate': 0.006525909043483982, 'subsample': 0.9382970275902356, 'colsample_bytree': 0.7855991276821759}. Best is trial 21 with value: 0.6101452643370191.",
2954:    "textPayload": "[I 2026-02-19 03:21:03,690] Trial 22 pruned. Physics collapse too severe. Insufficient signals.",
2976:    "textPayload": "[I 2026-02-19 03:21:03,781] Trial 23 pruned. Physics collapse too severe. Insufficient signals.",
2998:    "textPayload": "[I 2026-02-19 03:21:03,879] Trial 24 pruned. Physics collapse too severe. Insufficient signals.",
3020:    "textPayload": "[I 2026-02-19 03:21:05,353] Trial 25 finished with value: 0.5832707394445412 and parameters: {'peace_threshold': 0.5376513364979117, 'srl_resid_sigma_mult': 1.683472211891521, 'topo_energy_sigma_mult': 3.551148127793395, 'max_depth': 4, 'learning_rate': 0.01092045340022711, 'subsample': 0.9650004377940051, 'colsample_bytree': 0.8400441446733931}. Best is trial 21 with value: 0.6101452643370191.",
3042:    "textPayload": "[I 2026-02-19 03:21:05,799] Trial 26 finished with value: 0.577982337148635 and parameters: {'peace_threshold': 0.5197802023643474, 'srl_resid_sigma_mult': 2.3594819652649806, 'topo_energy_sigma_mult': 3.4355670325539664, 'max_depth': 4, 'learning_rate': 0.011443536258559225, 'subsample': 0.9613069928116433, 'colsample_bytree': 0.8368291567510833}. Best is trial 21 with value: 0.6101452643370191.",
3064:    "textPayload": "[I 2026-02-19 03:21:05,888] Trial 27 pruned. Physics collapse too severe. Insufficient signals.",
3086:    "textPayload": "[I 2026-02-19 03:21:05,974] Trial 28 pruned. Physics collapse too severe. Insufficient signals.",
3108:    "textPayload": "[I 2026-02-19 03:21:06,219] Trial 29 pruned. Insufficient finite weighted samples.",
3130:    "textPayload": "[I 2026-02-19 03:21:06,310] Trial 30 pruned. Physics collapse too severe. Insufficient signals.",
3152:    "textPayload": "[I 2026-02-19 03:21:06,763] Trial 31 finished with value: 0.5787813013254397 and parameters: {'peace_threshold': 0.5411381055528347, 'srl_resid_sigma_mult': 2.353905838224071, 'topo_energy_sigma_mult': 3.2530754820201193, 'max_depth': 4, 'learning_rate': 0.010722563104855408, 'subsample': 0.9723781006908048, 'colsample_bytree': 0.840960454428765}. Best is trial 21 with value: 0.6101452643370191.",
3174:    "textPayload": "[I 2026-02-19 03:21:07,331] Trial 32 finished with value: 0.5770745064948583 and parameters: {'peace_threshold': 0.5367691220117053, 'srl_resid_sigma_mult': 1.602581525166121, 'topo_energy_sigma_mult': 3.6937471614298216, 'max_depth': 4, 'learning_rate': 0.020237961375009873, 'subsample': 0.9419222707278063, 'colsample_bytree': 0.8391943527647294}. Best is trial 21 with value: 0.6101452643370191.",
3196:    "textPayload": "[I 2026-02-19 03:21:07,420] Trial 33 pruned. Physics collapse too severe. Insufficient signals.",
3218:    "textPayload": "[I 2026-02-19 03:21:07,945] Trial 34 finished with value: 0.5696158601453958 and parameters: {'peace_threshold': 0.5994101832554032, 'srl_resid_sigma_mult': 2.116579497153857, 'topo_energy_sigma_mult': 3.7573513068964486, 'max_depth': 4, 'learning_rate': 0.0401362435423388, 'subsample': 0.8628614045177675, 'colsample_bytree': 0.8871814952752444}. Best is trial 21 with value: 0.6101452643370191.",
3240:    "textPayload": "[I 2026-02-19 03:21:08,034] Trial 35 pruned. Physics collapse too severe. Insufficient signals.",
3262:    "textPayload": "[I 2026-02-19 03:21:09,176] Trial 36 finished with value: 0.5646217327051859 and parameters: {'peace_threshold': 0.3991734264867689, 'srl_resid_sigma_mult': 1.4548065502818956, 'topo_energy_sigma_mult': 2.9270727602125866, 'max_depth': 4, 'learning_rate': 0.00312643605432872, 'subsample': 0.896287552435244, 'colsample_bytree': 0.8510690149277331}. Best is trial 21 with value: 0.6101452643370191.",
3284:    "textPayload": "[I 2026-02-19 03:21:09,272] Trial 37 pruned. Physics collapse too severe. Insufficient signals.",
3306:    "textPayload": "[I 2026-02-19 03:21:09,370] Trial 38 pruned. Physics collapse too severe. Insufficient signals.",
3328:    "textPayload": "[I 2026-02-19 03:21:09,477] Trial 39 pruned. Physics collapse too severe. Insufficient signals.",
3350:    "textPayload": "[I 2026-02-19 03:21:09,568] Trial 40 pruned. Physics collapse too severe. Insufficient signals.",
3372:    "textPayload": "[I 2026-02-19 03:21:10,611] Trial 41 finished with value: 0.5851915734937709 and parameters: {'peace_threshold': 0.5297907832462997, 'srl_resid_sigma_mult': 2.2578632655736914, 'topo_energy_sigma_mult': 3.749848456978249, 'max_depth': 4, 'learning_rate': 0.006667066665765487, 'subsample': 0.9575024604178737, 'colsample_bytree': 0.8277441163292609}. Best is trial 21 with value: 0.6101452643370191.",
3394:    "textPayload": "[I 2026-02-19 03:21:11,224] Trial 42 finished with value: 0.5741478374479494 and parameters: {'peace_threshold': 0.5484562355388279, 'srl_resid_sigma_mult': 1.0011062245596642, 'topo_energy_sigma_mult': 4.978963162770565, 'max_depth': 4, 'learning_rate': 0.006429016972164092, 'subsample': 0.978086424983855, 'colsample_bytree': 0.8625698008902666}. Best is trial 21 with value: 0.6101452643370191.",
3416:    "textPayload": "[I 2026-02-19 03:21:11,314] Trial 43 pruned. Physics collapse too severe. Insufficient signals.",
3438:    "textPayload": "[I 2026-02-19 03:21:11,762] Trial 44 finished with value: 0.5622225485343807 and parameters: {'peace_threshold': 0.5051201150919743, 'srl_resid_sigma_mult': 2.018314856576082, 'topo_energy_sigma_mult': 2.761523185703272, 'max_depth': 3, 'learning_rate': 0.01873197584415883, 'subsample': 0.9532040456012921, 'colsample_bytree': 0.8506055239162873}. Best is trial 21 with value: 0.6101452643370191.",
3460:    "textPayload": "[I 2026-02-19 03:21:12,648] Trial 45 finished with value: 0.5505994734699632 and parameters: {'peace_threshold': 0.38155659379779916, 'srl_resid_sigma_mult': 2.3663016048203356, 'topo_energy_sigma_mult': 2.4726817290589764, 'max_depth': 4, 'learning_rate': 0.005311408937707575, 'subsample': 0.9417012731008391, 'colsample_bytree': 0.7973028917635265}. Best is trial 21 with value: 0.6101452643370191.",
3482:    "textPayload": "[I 2026-02-19 03:21:12,736] Trial 46 pruned. Physics collapse too severe. Insufficient signals.",
3504:    "textPayload": "[I 2026-02-19 03:21:13,373] Trial 47 finished with value: 0.5702104971323018 and parameters: {'peace_threshold': 0.6308228559785058, 'srl_resid_sigma_mult': 1.682397724002663, 'topo_energy_sigma_mult': 3.172799332399727, 'max_depth': 3, 'learning_rate': 0.012884724536193798, 'subsample': 0.6155615546802704, 'colsample_bytree': 0.9324348377467723}. Best is trial 21 with value: 0.6101452643370191.",
3526:    "textPayload": "[I 2026-02-19 03:21:13,463] Trial 48 pruned. Physics collapse too severe. Insufficient signals.",
3548:    "textPayload": "[I 2026-02-19 03:21:14,153] Trial 49 finished with value: 0.5912624420091713 and parameters: {'peace_threshold': 0.46882890101994307, 'srl_resid_sigma_mult': 2.595673761569892, 'topo_energy_sigma_mult': 4.139492462541955, 'max_depth': 4, 'learning_rate': 0.007113645181191646, 'subsample': 0.6624010881015239, 'colsample_bytree': 0.8953369811248002}. Best is trial 21 with value: 0.6101452643370191.",
3630:      "best_value": 0.6101452643370191,
3650:      "n_completed": 20,
3651:      "n_trials": 50,
3653:      "status": "completed"
3751:    "textPayload": "Job completed successfully.",
```

### D2. Training (`training_log_key_lines.txt`)
```text
--- train success 602229 ---
270:    "textPayload": "+ python3 -u payload.py --base-matrix-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet --code-bundle-uri=gs://omega_v52_central/omega/staging/code/omega_core_20260219-125410_78e36d9.zip --output-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9 --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958 --xgb-max-depth=5 --xgb-learning-rate=0.006525909043483982 --xgb-subsample=0.9382970275902356 --xgb-colsample-bytree=0.7855991276821759",
468:    "textPayload": "[*] Downloading base matrix: gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet",
688:    "textPayload": "[*] Sliced rows for training: 2067 / 5780139 (mask_rows=2188)",
763:      "mask_rows": 2188,
764:      "model_uri": "gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl",
777:      "status": "completed",
778:      "total_training_rows": 2067
854:    "textPayload": "Job completed successfully.",

--- train cancelled 402690 ---
1805:    "textPayload": "Job cancelled.",
```

### D3. Backtest failed attempts (`backtest_failed_key_lines.txt`)
```text
--- job_6324251159091478528 ---
600:    "textPayload": "2026-02-19 17:08:36,194 [INFO] Rapid downloading 263 files to local NVMe...",
1810:    "textPayload": "2026-02-19 17:17:46,145 [INFO] Parallel download complete.",
1920:    "textPayload": "2026-02-19 17:17:47,609 [INFO] Loading all raw data into a single massive RAM matrix...",
1964:    "textPayload": "2026-02-19 17:18:06,298 [INFO] Deduplicating tick collisions across hosts (linux1 vs windows1)...",

--- job_1475563210273718272 ---
600:    "textPayload": "2026-02-19 17:23:52,655 [INFO] Rapid downloading 263 files to local NVMe...",
1810:    "textPayload": "2026-02-19 17:36:31,942 [INFO] Parallel download complete.",
1920:    "textPayload": "2026-02-19 17:36:33,553 [INFO] Loading all raw data into a single massive RAM matrix...",
1964:    "textPayload": "2026-02-19 17:36:52,731 [INFO] Deduplicating tick collisions across hosts (linux1 vs windows1)...",

--- job_3366793578792615936 ---
600:    "textPayload": "2026-02-19 17:42:44,848 [INFO] Rapid downloading 263 files to local NVMe...",
1810:    "textPayload": "2026-02-19 17:54:41,559 [INFO] Parallel download complete.",
1920:    "textPayload": "2026-02-19 17:54:43,057 [INFO] Loading all raw data into a single massive RAM matrix...",
1964:    "textPayload": "2026-02-19 17:54:58,783 [INFO] Deduplicating tick collisions across hosts (linux1 vs windows1)...",
1986:    "textPayload": "2026-02-19 17:55:58,333 [INFO] Sorting multidimensional spacetime (32368466 rows)...",
2008:    "textPayload": "2026-02-19 17:56:11,718 [INFO] Applying physical engine. Polars Rust backend will saturate all CPU cores.",
2027:    "textPayload": "Replicas low on memory: workerpool0. Specify a machine with larger memory and try again.",
```

### D4. Backtest succeeded attempts (`backtest_success_key_lines.txt`)
```text
--- job_1959559432727691264 ---
622:    "textPayload": "2026-02-19 18:49:27,115 [INFO] Rapid downloading 263 files to local NVMe (workers=16)...",
644:    "textPayload": "2026-02-19 18:50:39,808 [INFO] Download progress: 20/263",
666:    "textPayload": "2026-02-19 18:51:20,382 [INFO] Download progress: 40/263",
688:    "textPayload": "2026-02-19 18:52:05,327 [INFO] Download progress: 60/263",
710:    "textPayload": "2026-02-19 18:52:50,463 [INFO] Download progress: 80/263",
732:    "textPayload": "2026-02-19 18:53:52,360 [INFO] Download progress: 100/263",
754:    "textPayload": "2026-02-19 18:54:38,729 [INFO] Download progress: 120/263",
776:    "textPayload": "2026-02-19 18:55:30,126 [INFO] Download progress: 140/263",
798:    "textPayload": "2026-02-19 18:56:20,085 [INFO] Download progress: 160/263",
820:    "textPayload": "2026-02-19 18:57:03,230 [INFO] Download progress: 180/263",
842:    "textPayload": "2026-02-19 18:58:07,268 [INFO] Download progress: 200/263",
864:    "textPayload": "2026-02-19 18:58:48,266 [INFO] Download progress: 220/263",
886:    "textPayload": "2026-02-19 18:59:33,915 [INFO] Download progress: 240/263",
974:    "textPayload": "2026-02-19 19:00:16,882 [INFO] Download progress: 260/263",
1062:    "textPayload": "2026-02-19 19:00:17,438 [INFO] Download progress: 263/263",
1084:    "textPayload": "2026-02-19 19:00:17,439 [INFO] Parallel download complete.",
1194:    "textPayload": "2026-02-19 19:00:19,314 [INFO] Loading all raw data into a single massive RAM matrix...",
1260:    "textPayload": "2026-02-19 19:00:39,898 [INFO] Deduplicating tick collisions across hosts (linux1 vs windows1)...",
1282:    "textPayload": "2026-02-19 19:01:31,641 [INFO] Sorting multidimensional spacetime (32368466 rows)...",
1304:    "textPayload": "2026-02-19 19:01:38,741 [INFO] Applying physical engine. Polars Rust backend will saturate all CPU cores.",
1348:    "textPayload": "2026-02-19 19:01:57,479 [INFO] Valid processed rows after T+1 causality shift: 8907595",
1370:    "textPayload": "2026-02-19 19:01:57,564 [INFO] Evaluating Non-Linear Oracle (Model Alignment)...",
1421:      "status": "completed",
1437:      "total_proc_rows": 8907595,
1440:        "architecture": "global_causal_materialization",
1446:        "reuse_precomputed_physics": true,
1524:    "textPayload": "Job completed successfully.",

--- job_4089128737776336896 ---
842:    "textPayload": "2026-02-19 16:49:03,803 [INFO] Valid processed rows after T+1 causality shift: 62842",
864:    "textPayload": "2026-02-19 16:49:03,853 [INFO] Evaluating Non-Linear Oracle (Model Alignment)...",
883:      "files_used": 2,
915:      "status": "completed",
931:      "total_proc_rows": 62842,
934:        "architecture": "global_causal_materialization",
1017:    "textPayload": "Job completed successfully.",
```

---

## Appendix E: Artifact Metadata and Source Snapshots

### E1. Artifact metadata summary (`object_metadata_summary.txt`)
```text
=== Artifact object metadata ===
--- object_omega_v52_central_omega_staging_base_matrix_v60_resume_aa8abb7_base_matrix.parquet.describe.json ---
{
  "bucket": "omega_v52_central",
  "name": "omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet",
  "generation": "1771470938410938",
  "metageneration": 1,
  "size": 970685813,
  "creation_time": "2026-02-19T03:15:38+0000",
  "update_time": "2026-02-19T03:15:38+0000",
  "crc32c_hash": "aL74zg==",
  "md5_hash": "byrQcQMM9wQXXTdXk9Lvqw==",
  "content_type": "application/octet-stream",
  "storage_url": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet#1771470938410938"
}
--- object_omega_v52_central_omega_staging_base_matrix_v60_resume_aa8abb7_base_matrix.meta.json.describe.json ---
{
  "bucket": "omega_v52_central",
  "name": "omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.meta.json",
  "generation": "1771470941723013",
  "metageneration": 1,
  "size": 37260,
  "creation_time": "2026-02-19T03:15:41+0000",
  "update_time": "2026-02-19T03:15:41+0000",
  "crc32c_hash": "jvpaqg==",
  "md5_hash": "sFk3UUn09IIuzwSzQfcBvg==",
  "content_type": "application/json",
  "storage_url": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.meta.json#1771470941723013"
}
--- object_omega_v52_central_omega_staging_optimization_v60_20260219-030000_aa8abb7_swarm_best.json.describe.json ---
{
  "bucket": "omega_v52_central",
  "name": "omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json",
  "generation": "1771471275520952",
  "metageneration": 1,
  "size": 900,
  "creation_time": "2026-02-19T03:21:15+0000",
  "update_time": "2026-02-19T03:21:15+0000",
  "crc32c_hash": "AvaJoQ==",
  "md5_hash": "xTeyodrlajYI1MGFgtDtgA==",
  "content_type": "application/json",
  "storage_url": "gs://omega_v52_central/omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json#1771471275520952"
}
--- object_omega_v52_central_omega_staging_models_v6_20260219-125410_78e36d9_omega_v6_xgb_final.pkl.describe.json ---
{
  "bucket": "omega_v52_central",
  "name": "omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl",
  "generation": "1771505840164429",
  "metageneration": 1,
  "size": 355684,
  "creation_time": "2026-02-19T12:57:20+0000",
  "update_time": "2026-02-19T12:57:20+0000",
  "crc32c_hash": "Zfk3jw==",
  "md5_hash": "TcZjeOK7ThYSsD08wBMk9A==",
  "content_type": "application/octet-stream",
  "storage_url": "gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl#1771505840164429"
}
--- object_omega_v52_central_omega_staging_models_v6_20260219-125410_78e36d9_train_metrics.json.describe.json ---
{
  "bucket": "omega_v52_central",
  "name": "omega/staging/models/v6/20260219-125410_78e36d9/train_metrics.json",
  "generation": "1771505840260532",
  "metageneration": 1,
  "size": 746,
  "creation_time": "2026-02-19T12:57:20+0000",
  "update_time": "2026-02-19T12:57:20+0000",
  "crc32c_hash": "u8mrQQ==",
  "md5_hash": "FaxoDx4P2OCao7ekJ3Ptcg==",
  "content_type": "application/json",
  "storage_url": "gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/train_metrics.json#1771505840260532"
}
--- object_omega_v52_central_omega_staging_backtest_v6_20260219-125410_78e36d9_backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json.describe.json ---
{
  "bucket": "omega_v52_central",
  "name": "omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json",
  "generation": "1771528134833185",
  "metageneration": 1,
  "size": 1823,
  "creation_time": "2026-02-19T19:08:54+0000",
  "update_time": "2026-02-19T19:08:54+0000",
  "crc32c_hash": "BTXpZg==",
  "md5_hash": "sktD8qGVa7Xc0VHG26wMwQ==",
  "content_type": "application/json",
  "storage_url": "gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json#1771528134833185"
}
```

### E2. Source snapshots captured
- `audit/runtime/v60_factual_evidence/source_tools_v60_build_base_matrix.py`
- `audit/runtime/v60_factual_evidence/source_tools_v60_swarm_xgb.py`
- `audit/runtime/v60_factual_evidence/source_tools_run_vertex_xgb_train.py`
- `audit/runtime/v60_factual_evidence/source_tools_run_cloud_backtest.py`
- `audit/runtime/v60_factual_evidence/source_omega_core_trainer.py`

### E3. Source SHA256 (`source_file_sha256.txt`)
```text
ec6040680a625c423b8c475ce8c1db969a4ffdfce630ee29ac136f57f883d873  audit/runtime/v60_factual_evidence/source_tools_v60_build_base_matrix.py
bb1b6eee6616f910d0edc44ec805ca931b3abbcbf84df46c86ece1901484ce25  audit/runtime/v60_factual_evidence/source_tools_v60_swarm_xgb.py
d67f0328d058cedec50ca83fd99f6e9ebbe3d0438443cc7fe02509f7a1659c6e  audit/runtime/v60_factual_evidence/source_tools_run_vertex_xgb_train.py
f6a32966668988726e2f79cefefed879aee0ece02f1b5c82940b80838d393d0e  audit/runtime/v60_factual_evidence/source_tools_run_cloud_backtest.py
2dbaab8127a5cf8a0af8474614ec1b3db140a20f9537c3e8124a6ee29c385ae3  audit/runtime/v60_factual_evidence/source_omega_core_trainer.py
```

### E4. Source line counts (`source_file_line_counts.txt`)
```text
      24 audit/runtime/v60_factual_evidence/source_tools_v60_build_base_matrix.py
     283 audit/runtime/v60_factual_evidence/source_tools_v60_swarm_xgb.py
     243 audit/runtime/v60_factual_evidence/source_tools_run_vertex_xgb_train.py
     413 audit/runtime/v60_factual_evidence/source_tools_run_cloud_backtest.py
     615 audit/runtime/v60_factual_evidence/source_omega_core_trainer.py
    1578 total
```

---

## Appendix F: Evidence Inventory (`manifest_ls_lh.txt`)
```text
-rw-r--r--@ 1 zephryj  staff    10K Feb 20 09:14 autopilot_aa8abb7.stage_transition_excerpt.txt
-rw-r--r--@ 1 zephryj  staff    16K Feb 20 09:20 source_tools_run_cloud_backtest.py
-rw-r--r--@ 1 zephryj  staff    18K Feb 20 09:08 vertex_jobs_uswest1_latest120.table.txt
-rw-r--r--@ 1 zephryj  staff    21K Feb 20 09:13 autopilot_aa8abb7.key_lines.txt
-rw-r--r--@ 1 zephryj  staff    24K Feb 20 09:20 source_omega_core_trainer.py
-rw-r--r--@ 1 zephryj  staff    26K Feb 20 09:14 autopilot_aa8abb7.train_backtest_takeover_excerpt.txt
-rw-r--r--@ 1 zephryj  staff    28B Feb 20 09:17 local_frames_linux1_count.txt
-rw-r--r--@ 1 zephryj  staff    29K Feb 20 09:16 job_6945888645156962304.logs.json
-rw-r--r--@ 1 zephryj  staff    30B Feb 20 09:17 local_frames_windows1_count.txt
-rw-r--r--@ 1 zephryj  staff    34K Feb 20 09:15 job_6022297228557680640.logs.json
-rw-r--r--@ 1 zephryj  staff    36K Feb 20 09:12 base_matrix_resume_aa8abb7.meta.json
-rw-r--r--@ 1 zephryj  staff    38K Feb 20 09:16 job_4089128737776336896.logs.json
-rw-r--r--@ 1 zephryj  staff    49K Feb 20 09:15 job_4665024890858897408.logs.json
-rw-r--r--@ 1 zephryj  staff    57K Feb 20 09:15 job_320740100306632704.logs.json
-rw-r--r--@ 1 zephryj  staff    57K Feb 20 09:16 job_1959559432727691264.logs.json
-rw-r--r--@ 1 zephryj  staff    65K Feb 20 09:08 vertex_jobs_uscentral1_latest120.json
-rw-r--r--@ 1 zephryj  staff    70K Feb 20 09:15 job_4026903526469795840.logs.json
-rw-r--r--@ 1 zephryj  staff    72B Feb 20 09:12 models_v6_prefix.list.txt
-rw-r--r--@ 1 zephryj  staff    74B Feb 20 09:12 backtest_v6_prefix.list.txt
-rw-r--r--@ 1 zephryj  staff    76K Feb 20 09:16 job_1324903728989339648.logs.json
-rw-r--r--@ 1 zephryj  staff    80K Feb 20 09:16 job_6324251159091478528.logs.json
-rw-r--r--@ 1 zephryj  staff    81K Feb 20 09:16 job_3366793578792615936.logs.json
-rw-r--r--@ 1 zephryj  staff    89K Feb 20 09:16 job_1475563210273718272.logs.json
-rw-r--r--@ 1 zephryj  staff   1.1K Feb 20 09:17 job_4026903526469795840.args_excerpt.txt
-rw-r--r--@ 1 zephryj  staff   1.2K Feb 20 09:17 job_6022297228557680640.args_excerpt.txt
-rw-r--r--@ 1 zephryj  staff   1.3K Feb 20 09:17 object_omega_v52_central_omega_staging_base_matrix_v60_resume_aa8abb7_base_matrix.parquet.describe.json
-rw-r--r--@ 1 zephryj  staff   1.3K Feb 20 09:18 object_omega_v52_central_omega_staging_base_matrix_v60_resume_aa8abb7_base_matrix.meta.json.describe.json
-rw-r--r--@ 1 zephryj  staff   1.4K Feb 20 09:12 model_omega_v6_xgb_final.pkl.describe.json
-rw-r--r--@ 1 zephryj  staff   1.4K Feb 20 09:17 job_1959559432727691264.args_excerpt.txt
-rw-r--r--@ 1 zephryj  staff   1.4K Feb 20 09:18 object_omega_v52_central_omega_staging_models_v6_20260219-125410_78e36d9_omega_v6_xgb_final.pkl.describe.json
-rw-r--r--@ 1 zephryj  staff   1.4K Feb 20 09:18 object_omega_v52_central_omega_staging_models_v6_20260219-125410_78e36d9_train_metrics.json.describe.json
-rw-r--r--@ 1 zephryj  staff   1.4K Feb 20 09:18 object_omega_v52_central_omega_staging_optimization_v60_20260219-030000_aa8abb7_swarm_best.json.describe.json
-rw-r--r--@ 1 zephryj  staff   1.5K Feb 20 09:18 object_omega_v52_central_omega_staging_backtest_v6_20260219-125410_78e36d9_backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json.describe.json
-rw-r--r--@ 1 zephryj  staff   1.7K Feb 20 09:12 backtest_metrics_smoke_n2std80_schemafix_20260219-164409.json
-rw-r--r--@ 1 zephryj  staff   1.7K Feb 20 09:13 job_8392580415252070400.describe.json
-rw-r--r--@ 1 zephryj  staff   1.8K Feb 20 09:12 backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json
-rw-r--r--@ 1 zephryj  staff   109K Feb 20 09:16 job_8385422044799434752.logs.json
-rw-r--r--@ 1 zephryj  staff   126K Feb 20 09:15 job_4745526734198145024.logs.json
-rw-r--r--@ 1 zephryj  staff   152K Feb 20 09:15 job_8392580415252070400.logs.json
-rw-r--r--@ 1 zephryj  staff   184B Feb 20 09:12 models_20260219-125410_78e36d9.list.txt
-rw-r--r--@ 1 zephryj  staff   2.0K Feb 20 09:13 job_4026903526469795840.describe.json
-rw-r--r--@ 1 zephryj  staff   2.1K Feb 20 09:13 job_4089128737776336896.describe.json
-rw-r--r--@ 1 zephryj  staff   2.1K Feb 20 09:13 job_6022297228557680640.describe.json
-rw-r--r--@ 1 zephryj  staff   2.2K Feb 20 09:13 job_320740100306632704.describe.json
-rw-r--r--@ 1 zephryj  staff   2.3K Feb 20 09:13 job_1324903728989339648.describe.json
-rw-r--r--@ 1 zephryj  staff   2.3K Feb 20 09:13 job_1475563210273718272.describe.json
-rw-r--r--@ 1 zephryj  staff   2.3K Feb 20 09:13 job_1959559432727691264.describe.json
-rw-r--r--@ 1 zephryj  staff   2.3K Feb 20 09:13 job_3366793578792615936.describe.json
-rw-r--r--@ 1 zephryj  staff   2.3K Feb 20 09:13 job_4665024890858897408.describe.json
-rw-r--r--@ 1 zephryj  staff   2.3K Feb 20 09:13 job_4745526734198145024.describe.json
-rw-r--r--@ 1 zephryj  staff   2.3K Feb 20 09:13 job_6324251159091478528.describe.json
-rw-r--r--@ 1 zephryj  staff   2.3K Feb 20 09:13 job_6945888645156962304.describe.json
-rw-r--r--@ 1 zephryj  staff   2.3K Feb 20 09:20 job_timeline_selected.txt
-rw-r--r--@ 1 zephryj  staff   2.6K Feb 20 09:13 job_8385422044799434752.describe.json
-rw-r--r--@ 1 zephryj  staff   298B Feb 20 09:12 backtest_20260219-125410_78e36d9.list.txt
-rw-r--r--@ 1 zephryj  staff   3.3K Feb 20 09:17 job_describe_key_fields.txt
-rw-r--r--@ 1 zephryj  staff   3.5K Feb 20 09:20 base_matrix_vertex_jobs_uswest1.txt
-rw-r--r--@ 1 zephryj  staff   4.0K Feb 20 09:19 object_metadata_summary.txt
-rw-r--r--@ 1 zephryj  staff   4.1K Feb 20 09:08 autopilot_aa8abb7.status.json
-rw-r--r--@ 1 zephryj  staff   4.9K Feb 20 09:08 vertex_jobs_uscentral1_latest120.table.txt
-rw-r--r--@ 1 zephryj  staff   5.8K Feb 20 09:18 fact_summary.txt
-rw-r--r--@ 1 zephryj  staff   674B Feb 20 09:20 source_file_sha256.txt
-rw-r--r--@ 1 zephryj  staff   746B Feb 20 09:12 train_metrics_20260219-125410_78e36d9.json
-rw-r--r--@ 1 zephryj  staff   8.4K Feb 20 09:20 source_tools_run_vertex_xgb_train.py
-rw-r--r--@ 1 zephryj  staff   900B Feb 20 09:12 swarm_best_20260219-030000_aa8abb7.json
-rw-r--r--@ 1 zephryj  staff   950B Feb 20 09:17 job_8392580415252070400.args_excerpt.txt
-rw-r--r--@ 1 zephryj  wheel   6.3K Feb 20 09:20 manifest_ls_lh.txt
-rwxr-xr-x@ 1 zephryj  staff   548B Feb 20 09:20 source_tools_v60_build_base_matrix.py
-rwxr-xr-x@ 1 zephryj  staff   9.6K Feb 20 09:20 source_tools_v60_swarm_xgb.py
total 3720
```
