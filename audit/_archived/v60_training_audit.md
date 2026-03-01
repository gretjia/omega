# v60 Training Audit Evidence Package

- Generated(Local): 2026-02-19 19:16:52 CST +0800
- Generated(UTC): 2026-02-19T11:16:52Z
- Purpose: Submit complete evidence bundle to independent auditor.
- Rule: All code/log/json blocks below are direct copy-paste from source files/commands (no paraphrase in block).

## 0) Index
1. Optimization result JSON (GCS original)
2. Runtime status snapshot JSON
3. Autopilot critical log excerpt
4. Current training job describe JSON
5. Current training job state quick line
6. Backtest submission state evidence
7. Source code: tools/v60_swarm_xgb.py
8. Source code: tools/run_vertex_xgb_train.py
9. Source code: tools/run_cloud_backtest.py
10. Source code: /tmp/backtest_takeover_aa8abb7.sh
11. Source code: tools/submit_vertex_sweep.py
12. Config anchor: config.py + config_v6.py

## 1) Optimization Result JSON (GCS Original)
备注：该文件是优化阶段最终输出，记录 best_params / best_value / n_trials / n_completed。
来源：gs://omega_v52_central/omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json
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
}
```

## 2) Runtime Status Snapshot JSON
备注：编排状态总览，包含 optimization/train/backtest 配置与阶段。
来源：/Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
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

## 3) Autopilot Critical Log Excerpt
备注：关键时段（base_matrix完成 -> optimization提交/完成 -> train提交）的日志证据。
来源：/Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log (line 3260-3365)
```text
  3260	[2026-02-19 10:59:51] Spot plan base=False opt=False train=False backtest=False
  3261	[2026-02-19 10:59:51] Data caps base(symbols_per_batch=50, max_workers=8, sample_symbols=0) train(max_files=0, max_rows_per_file=0) backtest(max_files=0, max_rows_per_file=0)
  3262	[2026-02-19 10:59:51] Base-matrix local input pattern=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/*_aa8abb7.parquet files=40
  3263	[2026-02-19 10:59:51] Backtest month guard enabled: 2025,202601
  3264	[2026-02-19 10:59:51] Recursive audit passed at node=bootstrap
  3265	[2026-02-19 10:59:52] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
  3266	[2026-02-19 10:59:52] Frame stage complete.
  3267	[2026-02-19 10:59:52] Recursive audit passed at node=frame_complete
  3268	[2026-02-19 10:59:56] GCS progress linux1=484/484 windows1=263/263
  3269	[2026-02-19 10:59:56] Upload stage complete.
  3270	[2026-02-19 11:00:00] GCS counts linux1=484 windows1=263
  3271	[2026-02-19 11:00:00] Building v60 base matrix on local AMD nodes via ticker sharding...
  3272	[2026-02-19 11:00:00] Recursive audit passed at node=pre_base_matrix
  3273	[2026-02-19 11:00:00] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/v60_build_base_matrix.py --input-pattern=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v52/frames/host=windows1/*_aa8abb7.parquet --years=2023,2024 --hash=aa8abb7 --peace-threshold=0.1 --peace-threshold-baseline=0.1 --srl-resid-sigma-mult=0.5 --symbols-per-batch=50 --max-workers=8 --output-parquet=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix.parquet --output-meta=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix.parquet.meta.json --shard-dir=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix_shards --output-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet --output-meta-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.meta.json --seed=42
  3274	[2026-02-19 11:00:01] [INFO] forge scheduling: total_batches=112, pre_resumed=0, pending=112, max_workers=8
  3275	[2026-02-19 11:00:01] [INFO] worker plan: requested=8, effective=8, worker_budget=0, mem_available_gb=None
  3276	[2026-02-19 11:11:48] Copying file:///Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix.parquet to gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet
  3277	[2026-02-19 11:11:48]   
  3278	[2026-02-19 11:15:38] .........................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
  3279	[2026-02-19 11:15:38] 
  3280	[2026-02-19 11:15:38] Average throughput: 4.1MiB/s
  3281	[2026-02-19 11:15:40] Copying file:///Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix.parquet.meta.json to gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.meta.json
  3282	[2026-02-19 11:15:40]   
  3283	[2026-02-19 11:15:41] ........
  3284	[2026-02-19 11:15:42] {"status": "ok", "mode": "local_ticker_sharding", "output_parquet": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix.parquet", "output_meta": "/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix.parquet.meta.json", "output_uri": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet", "output_meta_uri": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.meta.json", "base_rows": 5780139, "input_file_count": 40, "symbols_total": 5576, "batch_count": 112, "worker_count": 8, "seconds": 940.89}
  3285	[2026-02-19 11:15:42] Recursive audit passed at node=post_base_matrix
  3286	[2026-02-19 11:15:42] Submitting v60 swarm optimization job (sync mode)...
  3287	[2026-02-19 11:15:42] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/v60_swarm_xgb.py --machine-type e2-highmem-16 --sync --sync-timeout-sec=10800 --force-gcloud-fallback --script-arg=--bootstrap-code --script-arg=--install-deps --script-arg=--base-matrix-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet --script-arg=--n-trials=50 --script-arg=--min-samples=2000 --script-arg=--seed=42 --script-arg=--output-uri=gs://omega_v52_central/omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json
  3288	[2026-02-19 11:15:42] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  3289	[2026-02-19 11:15:42]   warnings.warn(
  3290	[2026-02-19 11:15:43] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
  3291	[2026-02-19 11:15:43]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
  3292	[2026-02-19 11:15:43] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
  3293	[2026-02-19 11:15:45] [+] Code bundle uploaded successfully.
  3294	[2026-02-19 11:15:45] [*] Submitting Custom Job: omega-v60-v60_swarm_xgb-20260219-111545
  3295	[2026-02-19 11:15:45] [*] Forcing gcloud fallback submission path.
  3296	[2026-02-19 11:15:49] [+] Fallback submit succeeded: projects/269018079180/locations/us-central1/customJobs/8392580415252070400
  3297	[2026-02-19 11:15:50]     [Fallback] state=JOB_STATE_PENDING elapsed=0s
  3298	[2026-02-19 11:16:22]     [Fallback] state=JOB_STATE_PENDING elapsed=31s
  3299	[2026-02-19 11:16:53]     [Fallback] state=JOB_STATE_PENDING elapsed=63s
  3300	[2026-02-19 11:17:25]     [Fallback] state=JOB_STATE_PENDING elapsed=94s
  3301	[2026-02-19 11:17:57]     [Fallback] state=JOB_STATE_PENDING elapsed=126s
  3302	[2026-02-19 11:18:28]     [Fallback] state=JOB_STATE_PENDING elapsed=157s
  3303	[2026-02-19 11:19:00]     [Fallback] state=JOB_STATE_PENDING elapsed=189s
  3304	[2026-02-19 11:19:31]     [Fallback] state=JOB_STATE_PENDING elapsed=221s
  3305	[2026-02-19 11:20:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=252s
  3306	[2026-02-19 11:20:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=284s
  3307	[2026-02-19 11:21:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=315s
  3308	[2026-02-19 11:21:38]     [Fallback] state=JOB_STATE_SUCCEEDED elapsed=347s
  3309	[2026-02-19 11:21:39] Optimization complete best_params={'peace_threshold': 0.5253567667772991, 'srl_resid_sigma_mult': 1.9773888188507172, 'topo_energy_sigma_mult': 5.427559578121958, 'max_depth': 5, 'learning_rate': 0.006525909043483982, 'subsample': 0.9382970275902356, 'colsample_bytree': 0.7855991276821759}
  3310	[2026-02-19 11:21:39] Recursive audit passed at node=post_optimize
  3311	[2026-02-19 11:21:39] Submitting Vertex train job (sync mode)...
  3312	[2026-02-19 11:21:39] Recursive audit passed at node=pre_train
  3313	[2026-02-19 11:21:39] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_xgb_train.py --machine-type n1-standard-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--data-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--train-years=2023,2024 --script-arg=--output-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-030000_aa8abb7 --script-arg=--max-files=0 --script-arg=--max-rows-per-file=0 --script-arg=--peace-threshold=0.5253567667772991 --script-arg=--srl-resid-sigma-mult=1.9773888188507172 --script-arg=--topo-energy-sigma-mult=5.427559578121958 --script-arg=--xgb-max-depth=5 --script-arg=--xgb-learning-rate=0.006525909043483982 --script-arg=--xgb-subsample=0.9382970275902356 --script-arg=--xgb-colsample-bytree=0.7855991276821759
  3314	[2026-02-19 11:21:39] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  3315	[2026-02-19 11:21:39]   warnings.warn(
  3316	[2026-02-19 11:21:40] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
  3317	[2026-02-19 11:21:40]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
  3318	[2026-02-19 11:21:40] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
  3319	[2026-02-19 11:21:42] [+] Code bundle uploaded successfully.
  3320	[2026-02-19 11:21:42] [*] Submitting Custom Job: omega-v60-run_vertex_xgb_train-20260219-112142
  3321	[2026-02-19 11:21:42] [*] Forcing gcloud fallback submission path.
  3322	[2026-02-19 11:21:45] [+] Fallback submit succeeded: projects/269018079180/locations/us-central1/customJobs/4026903526469795840
  3323	[2026-02-19 11:21:47]     [Fallback] state=JOB_STATE_QUEUED elapsed=0s
  3324	[2026-02-19 11:22:18]     [Fallback] state=JOB_STATE_PENDING elapsed=31s
  3325	[2026-02-19 11:22:50]     [Fallback] state=JOB_STATE_PENDING elapsed=62s
  3326	[2026-02-19 11:23:21]     [Fallback] state=JOB_STATE_PENDING elapsed=94s
  3327	[2026-02-19 11:23:53]     [Fallback] state=JOB_STATE_PENDING elapsed=126s
  3328	[2026-02-19 11:24:25]     [Fallback] state=JOB_STATE_PENDING elapsed=157s
  3329	[2026-02-19 11:24:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=189s
  3330	[2026-02-19 11:25:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=221s
  3331	[2026-02-19 11:26:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=253s
  3332	[2026-02-19 11:26:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=284s
  3333	[2026-02-19 11:27:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=316s
  3334	[2026-02-19 11:27:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=347s
  3335	[2026-02-19 11:28:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=379s
  3336	[2026-02-19 11:28:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=410s
  3337	[2026-02-19 11:29:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=442s
  3338	[2026-02-19 11:29:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=474s
  3339	[2026-02-19 11:30:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=504s
  3340	[2026-02-19 11:30:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=536s
  3341	[2026-02-19 11:31:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=568s
  3342	[2026-02-19 11:31:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=599s
  3343	[2026-02-19 11:32:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=631s
  3344	[2026-02-19 11:32:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=662s
  3345	[2026-02-19 11:33:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=694s
  3346	[2026-02-19 11:33:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=726s
  3347	[2026-02-19 11:34:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=757s
  3348	[2026-02-19 11:34:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=789s
  3349	[2026-02-19 11:35:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=820s
  3350	[2026-02-19 11:35:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=852s
  3351	[2026-02-19 11:36:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=883s
  3352	[2026-02-19 11:37:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=915s
  3353	[2026-02-19 11:37:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=947s
  3354	[2026-02-19 11:38:05]     [Fallback] state=JOB_STATE_RUNNING elapsed=978s
  3355	[2026-02-19 11:38:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=1010s
  3356	[2026-02-19 11:39:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=1041s
  3357	[2026-02-19 11:39:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=1073s
  3358	[2026-02-19 11:40:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=1105s
  3359	[2026-02-19 11:40:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=1136s
  3360	[2026-02-19 11:41:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=1168s
  3361	[2026-02-19 11:41:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=1199s
  3362	[2026-02-19 11:42:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=1231s
  3363	[2026-02-19 11:42:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=1262s
  3364	[2026-02-19 11:43:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=1294s
  3365	[2026-02-19 11:43:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=1325s
```

## 4) Current Training Job Describe JSON
备注：Vertex当前训练任务完整描述（容器命令、参数、机器类型）。
来源：gcloud ai custom-jobs describe projects/269018079180/locations/us-central1/customJobs/4026903526469795840
```json
{
  "createTime": "2026-02-19T03:21:45.491294Z",
  "displayName": "omega-v60-run_vertex_xgb_train-20260219-112142",
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
  "state": "JOB_STATE_RUNNING",
  "updateTime": "2026-02-19T03:24:37.028732Z"
}
```

## 5) Current Training Job State Quick Line
备注：快速核验训练是否结束。
来源：gcloud ai custom-jobs describe ... --format='value(state,startTime,endTime,updateTime)'
```text
JOB_STATE_RUNNING	2026-02-19T03:24:24Z		2026-02-19T03:24:37.028732Z
```

## 6) Backtest Submission State Evidence
备注：回测是否已提交，以及watcher是否仍在等待train完成。
6.1 custom-jobs list (filter=backtest)
```text
```
6.2 backtest takeover watcher tail
来源：/Users/zephryj/work/Omega_vNext/audit/runtime/v52/backtest_takeover_aa8abb7.log
```text
[2026-02-19 17:13:52 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:14:54 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:15:55 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:16:57 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:17:58 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:19:00 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:20:02 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:21:03 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:22:05 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:23:06 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:24:08 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:25:10 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:26:11 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:27:13 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:28:14 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:29:16 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:30:17 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:31:18 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:32:20 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:33:21 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:34:23 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:35:25 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:36:26 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:37:28 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:38:29 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:39:31 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:40:32 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:41:34 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:42:35 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:43:37 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:44:39 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:45:40 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:46:42 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:47:43 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:48:45 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:49:46 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:50:48 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:51:49 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:52:51 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:53:53 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:54:55 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:55:56 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:56:58 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:57:59 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 17:59:01 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:00:02 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:01:04 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:02:05 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:03:07 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:04:08 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:05:10 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:06:11 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:07:13 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:08:15 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:09:16 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:10:18 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:11:19 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:12:21 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:13:23 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:14:24 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:15:26 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:16:27 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:17:29 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:18:30 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:19:32 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:20:33 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:21:35 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:22:37 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:23:38 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:24:40 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:25:41 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:26:43 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:27:44 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:28:46 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:29:48 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:30:49 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:31:51 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:32:52 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:33:54 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:34:55 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:35:57 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:36:58 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:38:00 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:39:02 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:40:03 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:41:05 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:42:06 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:43:08 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:44:09 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:45:11 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:46:12 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:47:14 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:48:16 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:49:17 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:50:19 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:51:20 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:52:22 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:53:23 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:54:25 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:55:26 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:56:28 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:57:30 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:58:31 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 18:59:33 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:00:34 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:01:36 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:02:37 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:03:39 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:04:41 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:05:42 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:06:44 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:07:45 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:08:47 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:09:49 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:10:50 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:11:52 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:12:53 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:13:55 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:14:56 CST] train_state=JOB_STATE_RUNNING
[2026-02-19 19:15:58 CST] train_state=JOB_STATE_RUNNING
```

## 7) Source Code: tools/v60_swarm_xgb.py
备注：Optimization核心实现（Optuna + 物理门控 + XGBoost CV目标）。
来源：/Users/zephryj/work/Omega_vNext/tools/v60_swarm_xgb.py
```python
#!/usr/bin/env python3
"""
v60 in-memory manifold slicing swarm (Optuna + XGBoost).

Key constraints from v60 optimization audit:
- Never rerun ETL per trial.
- Search physics gates + XGBoost hyperparameters jointly.
- Use in-memory boolean slicing for O(1)-style trial filtering.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _download_file(gcs_uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.check_call(["gsutil", "cp", gcs_uri, str(local_path)])
        return
    except Exception:
        pass

    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))


def _upload_json(payload: dict, gcs_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    tmp = Path("v60_swarm_result.json")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(tmp))


def _install_dependencies() -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "optuna",
            "xgboost",
            "numpy",
            "polars",
            "google-cloud-storage",
            "gcsfs",
            "fsspec",
            "psutil",
        ]
    )


def _bootstrap_codebase(code_bundle_uri: str) -> None:
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())


class EpistemicSwarmV6:
    def __init__(self, base_matrix_path: str, feature_cols: list[str]):
        import polars as pl

        print(f"Loading Base Matrix into RAM: {base_matrix_path}", flush=True)
        self.df = pl.read_parquet(base_matrix_path)

        required = [
            "epiplexity",
            "srl_resid_050",
            "sigma_eff",
            "topo_area",
            "topo_energy",
            "t1_fwd_return",
        ]
        missing = [c for c in required if c not in self.df.columns]
        if missing:
            raise ValueError(f"Base matrix missing required columns: {missing}")

        feat_missing = [c for c in feature_cols if c not in self.df.columns]
        if feat_missing:
            raise ValueError(f"Base matrix missing feature columns: {feat_missing}")

        self.feature_cols = list(feature_cols)
        self.epi = self.df.get_column("epiplexity").to_numpy()
        self.srl = self.df.get_column("srl_resid_050").to_numpy()
        self.sigma = self.df.get_column("sigma_eff").to_numpy()
        self.topo_area = self.df.get_column("topo_area").to_numpy()
        self.topo_energy = self.df.get_column("topo_energy").to_numpy()

        self.X = self.df.select(self.feature_cols).to_numpy()
        self.y = (self.df.get_column("t1_fwd_return").to_numpy() > 0).astype(int)

    def objective(
        self,
        trial,
        min_samples: int,
        nfold: int,
        early_stopping_rounds: int,
        num_boost_round: int,
        seed: int,
    ) -> float:
        import optuna
        import xgboost as xgb

        peace_threshold = trial.suggest_float("peace_threshold", 0.30, 0.95)
        srl_mult = trial.suggest_float("srl_resid_sigma_mult", 1.0, 8.0)
        topo_energy_mult = trial.suggest_float("topo_energy_sigma_mult", 2.0, 15.0)

        xgb_params = {
            "max_depth": trial.suggest_int("max_depth", 3, 7),
            "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.1, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "tree_method": "hist",
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "n_jobs": -1,
            "seed": int(seed),
        }

        physics_mask = (
            (self.epi > peace_threshold)
            & (np.abs(self.srl) > srl_mult * self.sigma)
            & (self.topo_energy > topo_energy_mult * self.sigma)
        )

        n_mask = int(np.sum(physics_mask))
        if n_mask < int(min_samples):
            raise optuna.TrialPruned("Physics collapse too severe. Insufficient signals.")

        X_clean = self.X[physics_mask]
        y_clean = self.y[physics_mask]
        weights_clean = (self.epi * np.log1p(np.abs(self.topo_area)))[physics_mask]

        finite = np.isfinite(weights_clean) & (weights_clean > 1e-8)
        if int(np.sum(finite)) < int(min_samples):
            raise optuna.TrialPruned("Insufficient finite weighted samples.")

        X_clean = X_clean[finite]
        y_clean = y_clean[finite]
        weights_clean = weights_clean[finite]

        dtrain = xgb.DMatrix(X_clean, label=y_clean, weight=weights_clean, feature_names=self.feature_cols)

        cv_results = xgb.cv(
            params=xgb_params,
            dtrain=dtrain,
            num_boost_round=int(num_boost_round),
            nfold=int(nfold),
            early_stopping_rounds=int(early_stopping_rounds),
            seed=int(seed),
        )
        if cv_results.empty:
            raise optuna.TrialPruned("Empty CV result.")
        return float(cv_results["test-auc-mean"].max())


def _resolve_base_matrix_path(path_or_uri: str) -> str:
    if path_or_uri.startswith("gs://"):
        local = Path("base_matrix.parquet").resolve()
        _download_file(path_or_uri, local)
        return str(local)
    p = Path(path_or_uri)
    if not p.exists():
        raise FileNotFoundError(f"Base matrix not found: {path_or_uri}")
    return str(p)


def main() -> int:
    ap = argparse.ArgumentParser(description="v60 swarm optimizer (in-memory manifold slicing)")
    ap.add_argument("--base-matrix", default="")
    ap.add_argument("--base-matrix-uri", default="")
    ap.add_argument("--n-trials", type=int, default=50)
    ap.add_argument("--min-samples", type=int, default=2000)
    ap.add_argument("--nfold", type=int, default=5)
    ap.add_argument("--early-stopping-rounds", type=int, default=15)
    ap.add_argument("--num-boost-round", type=int, default=150)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--output-local", default="")
    ap.add_argument("--output-uri", default="")
    ap.add_argument("--install-deps", action="store_true")
    ap.add_argument("--bootstrap-code", action="store_true")
    ap.add_argument("--code-bundle-uri", default="gs://omega_v52/staging/code/omega_core.zip")
    args = ap.parse_args()

    if args.install_deps:
        _install_dependencies()

    if args.bootstrap_code:
        _bootstrap_codebase(args.code_bundle_uri)

    from config_v6 import FEATURE_COLS
    import optuna
    from optuna.trial import TrialState

    base_matrix_ref = args.base_matrix_uri.strip() or args.base_matrix.strip()
    if not base_matrix_ref:
        raise SystemExit("Either --base-matrix or --base-matrix-uri is required.")

    base_matrix_path = _resolve_base_matrix_path(base_matrix_ref)
    swarm = EpistemicSwarmV6(base_matrix_path=base_matrix_path, feature_cols=list(FEATURE_COLS))

    t0 = time.time()
    study = optuna.create_study(direction="maximize")
    study.optimize(
        lambda trial: swarm.objective(
            trial,
            min_samples=int(args.min_samples),
            nfold=int(args.nfold),
            early_stopping_rounds=int(args.early_stopping_rounds),
            num_boost_round=int(args.num_boost_round),
            seed=int(args.seed),
        ),
        n_trials=int(args.n_trials),
    )

    completed_trials = [t for t in study.trials if t.state == TrialState.COMPLETE]
    if completed_trials:
        result = {
            "status": "completed",
            "best_params": dict(study.best_params),
            "best_value": float(study.best_value),
            "n_trials": int(len(study.trials)),
            "n_completed": int(len(completed_trials)),
            "base_matrix": str(base_matrix_ref),
            "feature_cols": list(FEATURE_COLS),
            "seconds": round(time.time() - t0, 2),
            "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
        }
    else:
        result = {
            "status": "no_complete_trials",
            "best_params": {},
            "best_value": None,
            "n_trials": int(len(study.trials)),
            "n_completed": 0,
            "base_matrix": str(base_matrix_ref),
            "feature_cols": list(FEATURE_COLS),
            "seconds": round(time.time() - t0, 2),
            "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
            "message": "All trials pruned; relax min-samples or use a larger base matrix.",
        }

    if args.output_local:
        out = Path(args.output_local)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.output_uri:
        _upload_json(result, args.output_uri)

    print("--- V60 SWARM RESULT JSON START ---")
    print(json.dumps(result, ensure_ascii=False))
    print("--- V60 SWARM RESULT JSON END ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 8) Source Code: tools/run_vertex_xgb_train.py
备注：当前训练payload实现（文件循环训练、进度日志、模型与metrics上传）。
来源：/Users/zephryj/work/Omega_vNext/tools/run_vertex_xgb_train.py
```python
#!/usr/bin/env python3
"""
OMEGA v6 Vertex payload: train XGBoost on framed signal parquet from GCS.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path


def _install_dependencies() -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "polars",
            "gcsfs",
            "fsspec",
            "numpy",
            "pandas",
            "xgboost",
            "scikit-learn",
            "google-cloud-storage",
            "psutil",
        ]
    )


def _bootstrap_codebase(code_bundle_uri: str) -> None:
    try:
        subprocess.check_call(["gsutil", "cp", code_bundle_uri, "omega_core.zip"])
    except Exception:
        from google.cloud import storage

        uri = code_bundle_uri.replace("gs://", "", 1)
        bucket_name, blob_name = uri.split("/", 1)
        storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename("omega_core.zip")

    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    sys.path.append(os.getcwd())


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _upload_file(local_path: Path, gcs_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(local_path))


def _extract_day_key(path_or_uri: str) -> str:
    name = path_or_uri.rsplit("/", 1)[-1]
    m = re.match(r"^(\d{8})_", name)
    return m.group(1) if m else ""


def _day_summary(uris: list[str]) -> dict:
    days = sorted({d for d in (_extract_day_key(x) for x in uris) if d})
    if not days:
        return {"count": 0, "first": None, "last": None}
    return {"count": int(len(days)), "first": days[0], "last": days[-1]}


def _iter_selected_files(fs, data_pattern: str, years: list[str]) -> list[str]:
    files = sorted(fs.glob(data_pattern))
    out: list[str] = []
    for item in files:
        uri = item if str(item).startswith("gs://") else f"gs://{item}"
        if not years:
            out.append(uri)
            continue
        day = _extract_day_key(uri)
        if day and day[:4] in years:
            out.append(uri)
    return out


def _apply_cfg_overrides(cfg, args: argparse.Namespace):
    sig = cfg.signal
    mdl = cfg.model

    if args.peace_threshold is not None:
        sig = replace(sig, peace_threshold=float(args.peace_threshold))
    if args.srl_resid_sigma_mult is not None:
        sig = replace(sig, srl_resid_sigma_mult=float(args.srl_resid_sigma_mult))
    if args.topo_energy_sigma_mult is not None:
        sig = replace(sig, topo_energy_sigma_mult=float(args.topo_energy_sigma_mult))

    if args.xgb_max_depth is not None:
        mdl = replace(mdl, xgb_max_depth=int(args.xgb_max_depth))
    if args.xgb_learning_rate is not None:
        mdl = replace(mdl, xgb_eta=float(args.xgb_learning_rate))
    if args.xgb_subsample is not None:
        mdl = replace(mdl, xgb_subsample=float(args.xgb_subsample))
    if args.xgb_colsample_bytree is not None:
        mdl = replace(mdl, xgb_colsample_bytree=float(args.xgb_colsample_bytree))

    return replace(cfg, signal=sig, model=mdl)


def run_training(args: argparse.Namespace) -> None:
    import gcsfs
    import numpy as np
    import polars as pl
    import psutil
    import xgboost as xgb

    from config import L2PipelineConfig
    from omega_core.trainer import OmegaTrainerV3

    cfg = L2PipelineConfig()
    cfg = replace(cfg, model=replace(cfg.model, model_type="xgboost"))
    cfg = _apply_cfg_overrides(cfg, args)

    trainer = OmegaTrainerV3(cfg)
    xgb_params = {
        "objective": str(cfg.model.xgb_objective),
        "eval_metric": str(cfg.model.xgb_eval_metric),
        "max_depth": int(cfg.model.xgb_max_depth),
        "eta": float(cfg.model.xgb_eta),
        "subsample": float(cfg.model.xgb_subsample),
        "colsample_bytree": float(cfg.model.xgb_colsample_bytree),
        "verbosity": 1,
    }
    rounds = int(max(1, cfg.model.xgb_num_boost_round))

    fs = gcsfs.GCSFileSystem()
    train_files = _iter_selected_files(fs, args.data_pattern, args.train_years)
    if not train_files:
        raise RuntimeError("No training files matched data pattern/year filters.")
    matched_count = int(len(train_files))
    if int(args.max_files) > 0 and len(train_files) > int(args.max_files):
        idx = np.linspace(0, len(train_files) - 1, num=int(args.max_files), dtype=int).tolist()
        train_files = [train_files[int(i)] for i in idx]

    total_rows = 0
    files_used = 0
    used_uris: list[str] = []
    proc = psutil.Process(os.getpid())
    max_rows_per_file = int(max(0, args.max_rows_per_file))
    start = time.time()
    for file_idx, uri in enumerate(train_files, 1):
        df_raw = None
        df_proc = None
        dtrain = None
        try:
            lf = pl.scan_parquet(uri)
            if max_rows_per_file > 0:
                lf = lf.head(max_rows_per_file)
            df_raw = lf.collect()
            if df_raw.height == 0:
                continue
            df_proc = trainer._prepare_frames(df_raw, cfg)
            if df_proc.height == 0:
                continue
            dtrain = trainer.build_epistemic_dmatrix(df_proc)
            if dtrain is None:
                continue
            trainer.model = xgb.train(xgb_params, dtrain, num_boost_round=rounds, xgb_model=trainer.model)
            total_rows += int(dtrain.num_row())
            files_used += 1
            used_uris.append(uri)
        except Exception as exc:
            print(f"[Warn] Skip {uri}: {exc}", flush=True)
        finally:
            del df_raw, df_proc, dtrain
            gc.collect()

        if file_idx % 10 == 0 or file_idx == len(train_files):
            rss_gb = proc.memory_info().rss / float(1024 ** 3)
            print(
                f"[TrainProgress] files={file_idx}/{len(train_files)} used={files_used} "
                f"rows={total_rows} rss_gb={rss_gb:.2f}",
                flush=True,
            )

    if trainer.model is None or total_rows == 0:
        raise RuntimeError("Training produced no valid rows/model.")

    out_dir = Path(".")
    model_name = "omega_v6_xgb_final.pkl"
    trainer.save(out_dir=str(out_dir), name=model_name, extra_state={"total_rows": total_rows, "files_used": files_used})

    output_prefix = args.output_uri.rstrip("/")
    model_uri = f"{output_prefix}/{model_name}"
    metrics_uri = f"{output_prefix}/train_metrics.json"

    _upload_file(out_dir / model_name, model_uri)
    metrics = {
        "total_rows": total_rows,
        "files_matched": matched_count,
        "files_selected": int(len(train_files)),
        "files_used": files_used,
        "train_years": list(args.train_years),
        "day_span_selected": _day_summary(train_files),
        "day_span_used": _day_summary(used_uris),
        "seconds": round(time.time() - start, 2),
        "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
        "overrides": {
            "peace_threshold": args.peace_threshold,
            "srl_resid_sigma_mult": args.srl_resid_sigma_mult,
            "topo_energy_sigma_mult": args.topo_energy_sigma_mult,
            "xgb_max_depth": args.xgb_max_depth,
            "xgb_learning_rate": args.xgb_learning_rate,
            "xgb_subsample": args.xgb_subsample,
            "xgb_colsample_bytree": args.xgb_colsample_bytree,
            "max_files": args.max_files,
            "max_rows_per_file": args.max_rows_per_file,
        },
    }
    metrics_path = out_dir / "train_metrics.json"
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    _upload_file(metrics_path, metrics_uri)
    print(json.dumps({"model_uri": model_uri, "metrics_uri": metrics_uri, **metrics}, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser(description="OMEGA v6 XGBoost Trainer Payload")
    ap.add_argument("--code-bundle-uri", default="gs://omega_v52/staging/code/omega_core.zip")
    ap.add_argument("--data-pattern", default="gs://omega_v52/omega/v52/frames/host=*/*.parquet")
    ap.add_argument("--train-years", default="2023,2024")
    ap.add_argument("--output-uri", required=True, help="GCS prefix, e.g. gs://bucket/staging/models/v6")
    ap.add_argument("--max-files", type=int, default=0, help="0 means use all matched files.")
    ap.add_argument("--max-rows-per-file", type=int, default=0, help="0 means use all rows from each file.")
    ap.add_argument("--peace-threshold", type=float, default=None)
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=None)
    ap.add_argument("--topo-energy-sigma-mult", type=float, default=None)
    ap.add_argument("--xgb-max-depth", type=int, default=None)
    ap.add_argument("--xgb-learning-rate", type=float, default=None)
    ap.add_argument("--xgb-subsample", type=float, default=None)
    ap.add_argument("--xgb-colsample-bytree", type=float, default=None)
    args = ap.parse_args()
    args.train_years = [x.strip() for x in str(args.train_years).split(",") if x.strip()]

    _install_dependencies()
    _bootstrap_codebase(args.code_bundle_uri)
    run_training(args)


if __name__ == "__main__":
    main()
```

## 9) Source Code: tools/run_cloud_backtest.py
备注：当前回测payload实现（含flexible worker policy/adaptive concurrency）。
来源：/Users/zephryj/work/Omega_vNext/tools/run_cloud_backtest.py
```python
#!/usr/bin/env python3
"""
OMEGA v6 Cloud Backtest Payload
-------------------------------
Runs backtest metrics on GCS parquet frames and (optionally) a trained model.
"""

from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import gc
import json
import logging
import math
import numpy as np
import os
import pickle
import re
import shutil
import subprocess
import sys
import threading
import time
import warnings
from dataclasses import replace
from pathlib import Path


warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("omega_backtest")


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _download_file(gcs_uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.check_call(["gsutil", "cp", gcs_uri, str(local_path)])
        return
    except Exception:
        pass

    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))


def _upload_json(payload: dict, gcs_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    tmp = Path("backtest_metrics.json")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(tmp))


def install_dependencies() -> None:
    logger.info("Installing dependencies...")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "polars",
            "gcsfs",
            "fsspec",
            "scikit-learn",
            "numpy",
            "pandas",
            "google-cloud-storage",
            "psutil",
            "xgboost",
        ]
    )


def bootstrap_codebase(code_bundle_uri: str) -> None:
    logger.info("Bootstrapping code from %s ...", code_bundle_uri)
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    sys.path.append(os.getcwd())
    logger.info("Codebase bootstrapped.")


def _extract_day_key(path_or_uri: str) -> str:
    name = path_or_uri.rsplit("/", 1)[-1]
    m = re.match(r"^(\d{8})_", name)
    return m.group(1) if m else ""


def _day_summary(uris: list[str]) -> dict:
    days = sorted({d for d in (_extract_day_key(x) for x in uris) if d})
    if not days:
        return {"count": 0, "first": None, "last": None}
    return {"count": int(len(days)), "first": days[0], "last": days[-1]}


def _iter_selected_files(fs, data_pattern: str, years: list[str], test_ym: list[str]) -> list[str]:
    files = sorted(fs.glob(data_pattern))
    if years:
        kept = []
        for p in files:
            day = _extract_day_key(p)
            if day and day[:4] in years:
                kept.append(p)
        files = kept
    ym = [x.strip() for x in (test_ym or []) if x.strip()]
    if ym:
        kept = []
        for p in files:
            day = _extract_day_key(p)
            if day and any(day.startswith(prefix) for prefix in ym):
                kept.append(p)
        files = kept
    return ["gs://" + p for p in files]


def _load_model_payload(model_uri: str) -> tuple[object | None, object | None, list[str] | None]:
    if not model_uri:
        return None, None, None
    local_path = Path("omega_model.pkl")
    _download_file(model_uri, local_path)
    with open(local_path, "rb") as f:
        payload = pickle.load(f)
    model = payload.get("model")
    scaler = payload.get("scaler")
    features = payload.get("feature_cols", payload.get("features"))
    return model, scaler, list(features) if features else None


def _apply_cfg_overrides(cfg, args: argparse.Namespace):
    sig = cfg.signal
    if args.peace_threshold is not None:
        sig = replace(sig, peace_threshold=float(args.peace_threshold))
    if args.srl_resid_sigma_mult is not None:
        sig = replace(sig, srl_resid_sigma_mult=float(args.srl_resid_sigma_mult))
    if args.topo_energy_sigma_mult is not None:
        sig = replace(sig, topo_energy_sigma_mult=float(args.topo_energy_sigma_mult))
    return replace(cfg, signal=sig)


def _resolve_worker_plan(args: argparse.Namespace, cpu_total: int, mem_total_gb: float) -> dict:
    requested = int(max(0, args.workers))
    min_workers = int(max(1, args.workers_min))

    if requested > 0:
        auto_max = requested
    else:
        auto_max = int(max(1, math.floor(float(cpu_total) * float(args.workers_cpu_frac))))

    if int(args.workers_max) > 0:
        auto_max = min(auto_max, int(args.workers_max))

    if float(args.workers_mem_headroom_gb) > 0 and float(args.workers_est_mem_gb) > 0:
        mem_budget = max(0.0, float(mem_total_gb) - float(args.workers_mem_headroom_gb))
        mem_cap = int(max(1, math.floor(mem_budget / float(args.workers_est_mem_gb)))) if mem_budget > 0 else 1
        auto_max = min(auto_max, mem_cap)

    max_workers = int(max(min_workers, auto_max))
    if int(args.workers_start) > 0:
        start_workers = int(args.workers_start)
    else:
        start_workers = int(max(min_workers, math.ceil(max_workers * 0.35)))
    start_workers = int(min(max_workers, max(min_workers, start_workers)))

    adaptive = bool(max_workers > min_workers and int(args.workers_adjust_step) > 0)
    return {
        "requested": requested,
        "min_workers": min_workers,
        "max_workers": max_workers,
        "start_workers": start_workers,
        "adaptive": adaptive,
    }


def run_backtest(args: argparse.Namespace) -> dict:
    import polars as pl
    import gcsfs
    import psutil
    from config import L2PipelineConfig
    from omega_core.trainer import OmegaTrainerV3, evaluate_frames

    fs = gcsfs.GCSFileSystem()
    files = _iter_selected_files(fs, args.data_pattern, args.test_years, args.test_ym)
    if not files:
        raise RuntimeError(
            f"No test files matched data pattern={args.data_pattern} years={args.test_years} test_ym={args.test_ym}"
        )

    max_files = int(max(0, args.max_files))
    if max_files <= 0 or len(files) <= max_files:
        selected = list(files)
    else:
        # Uniformly sample across the full period to avoid head-only date bias.
        idx = np.linspace(0, len(files) - 1, num=max_files, dtype=int)
        selected = [files[int(i)] for i in idx.tolist()]
    logger.info(
        "Matched %d test files, using %d (max_files=%d, 0 means full)",
        len(files),
        len(selected),
        max_files,
    )

    cfg = L2PipelineConfig()
    cfg = _apply_cfg_overrides(cfg, args)
    model, scaler, feature_cols = _load_model_payload(args.model_uri)

    metric_keys = ["Topo_SNR", "Orthogonality", "Phys_Alignment", "Model_Alignment", "Vector_Alignment"]
    weighted_sum = {k: 0.0 for k in metric_keys}
    total_weight = 0
    per_file: list[dict] = []
    started = time.time()
    proc = psutil.Process(os.getpid())
    max_rows_per_file = int(max(0, args.max_rows_per_file))
    used_uris: list[str] = []

    cpu_total = int(psutil.cpu_count(logical=True) or 1)
    mem_total_gb = float(psutil.virtual_memory().total / (1024 ** 3))
    worker_plan = _resolve_worker_plan(args, cpu_total=cpu_total, mem_total_gb=mem_total_gb)
    target_workers = int(worker_plan["start_workers"])
    min_workers = int(worker_plan["min_workers"])
    max_workers = int(worker_plan["max_workers"])
    adaptive = bool(worker_plan["adaptive"])
    adjust_step = int(max(1, args.workers_adjust_step))
    poll_sec = float(max(0.5, args.workers_poll_sec))

    logger.info(
        "Worker plan requested=%d min=%d max=%d start=%d adaptive=%s cpu_total=%d mem_total_gb=%.1f",
        int(worker_plan["requested"]),
        min_workers,
        max_workers,
        target_workers,
        adaptive,
        cpu_total,
        mem_total_gb,
    )
    logger.info(
        "Adaptive thresholds cpu_low=%.1f cpu_high=%.1f mem_headroom_gb=%.1f est_mem_per_worker_gb=%.1f",
        float(args.workers_cpu_util_low),
        float(args.workers_cpu_util_high),
        float(args.workers_mem_headroom_gb),
        float(args.workers_est_mem_gb),
    )

    thread_local = threading.local()

    def _ctx() -> dict:
        local = getattr(thread_local, "ctx", None)
        if local is None:
            local = {
                "trainer": OmegaTrainerV3(cfg),
                "model": model,
                "scaler": scaler,
                "feature_cols": feature_cols,
            }
            thread_local.ctx = local
        return local

    def consume(uri: str) -> dict:
        df_raw = None
        df_proc = None
        try:
            local = _ctx()
            trainer = local["trainer"]
            lf = pl.scan_parquet(uri)
            if max_rows_per_file > 0:
                lf = lf.head(max_rows_per_file)
            df_raw = lf.collect()
            if df_raw.height == 0:
                return {"ok": False, "source_uri": uri, "error": "empty_raw"}
            df_proc = trainer._prepare_frames(df_raw, cfg)
            if df_proc.height == 0:
                return {"ok": False, "source_uri": uri, "error": "empty_processed"}

            metrics = evaluate_frames(
                df_proc,
                cfg,
                model=local["model"],
                scaler=local["scaler"],
                feature_cols=local["feature_cols"],
            )
            return {
                "ok": True,
                "source_uri": uri,
                "raw_rows": int(df_raw.height),
                "proc_rows": int(df_proc.height),
                "metrics": {k: float(metrics.get(k, float("nan"))) for k in metric_keys},
            }
        except Exception as exc:
            return {"ok": False, "source_uri": uri, "error": str(exc)}
        finally:
            del df_raw, df_proc
            gc.collect()

    def _apply_result(item: dict) -> None:
        nonlocal total_weight
        if not bool(item.get("ok")):
            logger.warning("Skip %s: %s", item.get("source_uri"), item.get("error", "unknown_error"))
            return
        weight = int(item.get("proc_rows", 0))
        total_weight += weight
        for key in metric_keys:
            v = item.get("metrics", {}).get(key)
            if v is None or (isinstance(v, float) and not math.isfinite(v)):
                continue
            weighted_sum[key] += float(v) * weight
        per_file.append(
            {
                "source_uri": item.get("source_uri"),
                "raw_rows": int(item.get("raw_rows", 0)),
                "proc_rows": int(item.get("proc_rows", 0)),
                **{k: float(item.get("metrics", {}).get(k, float("nan"))) for k in metric_keys},
            }
        )
        used_uris.append(str(item.get("source_uri")))

    pending = list(selected)
    inflight = {}
    completed_files = 0
    last_adjust_ts = time.time()
    psutil.cpu_percent(interval=None)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        while pending or inflight:
            if adaptive and (time.time() - last_adjust_ts) >= poll_sec:
                cpu_now = float(psutil.cpu_percent(interval=0.0))
                mem_now = psutil.virtual_memory()
                mem_available_gb = float(mem_now.available / (1024 ** 3))
                old_target = target_workers
                if cpu_now >= float(args.workers_cpu_util_high) or mem_available_gb < float(args.workers_mem_headroom_gb):
                    target_workers = int(max(min_workers, target_workers - adjust_step))
                elif cpu_now <= float(args.workers_cpu_util_low) and mem_available_gb > (
                    float(args.workers_mem_headroom_gb) + float(args.workers_est_mem_gb)
                ):
                    target_workers = int(min(max_workers, target_workers + adjust_step))
                if target_workers != old_target:
                    rss_gb = proc.memory_info().rss / float(1024 ** 3)
                    logger.info(
                        "Adaptive worker target %d -> %d (cpu=%.1f%% avail_gb=%.1f rss_gb=%.2f inflight=%d pending=%d)",
                        old_target,
                        target_workers,
                        cpu_now,
                        mem_available_gb,
                        rss_gb,
                        len(inflight),
                        len(pending),
                    )
                last_adjust_ts = time.time()

            while pending and len(inflight) < target_workers:
                uri = pending.pop(0)
                fut = pool.submit(consume, uri)
                inflight[fut] = uri

            if not inflight:
                continue

            done, _ = wait(list(inflight.keys()), timeout=poll_sec, return_when=FIRST_COMPLETED)
            if not done:
                continue

            for fut in done:
                src = inflight.pop(fut, None)
                completed_files += 1
                try:
                    item = fut.result()
                except Exception as exc:
                    logger.warning("Skip %s: %s", src, exc)
                    continue
                _apply_result(item)

                if completed_files % 8 == 0 or completed_files == len(selected):
                    rss_gb = proc.memory_info().rss / float(1024 ** 3)
                    logger.info(
                        "Backtest progress files=%d/%d inflight=%d target=%d used=%d rows=%d rss_gb=%.2f",
                        completed_files,
                        len(selected),
                        len(inflight),
                        target_workers,
                        len(per_file),
                        total_weight,
                        rss_gb,
                    )

    if not per_file and len(files) > len(selected):
        logger.warning("No valid frames in initial selection; expanding scan until first valid frame.")
        picked = set(selected)
        for uri in files:
            if uri in picked:
                continue
            item = consume(uri)
            _apply_result(item)
            if per_file:
                break

    if not per_file:
        raise RuntimeError("Backtest produced no valid processed frames.")

    summary_metrics = {}
    for key in metric_keys:
        if total_weight > 0:
            summary_metrics[key] = weighted_sum[key] / float(total_weight)
        else:
            summary_metrics[key] = float("nan")

    result = {
        "status": "completed",
        "files_matched": int(len(files)),
        "files_selected": int(len(selected)),
        "files_used": int(len(per_file)),
        "day_span_selected": _day_summary(selected),
        "day_span_used": _day_summary(used_uris),
        "total_proc_rows": int(total_weight),
        "seconds": round(time.time() - started, 2),
        "model_uri": args.model_uri or None,
        "data_pattern": args.data_pattern,
        "test_years": args.test_years,
        "test_ym": args.test_ym,
        "overrides": {
            "peace_threshold": args.peace_threshold,
            "srl_resid_sigma_mult": args.srl_resid_sigma_mult,
            "topo_energy_sigma_mult": args.topo_energy_sigma_mult,
        },
        "worker_plan": {
            "requested": int(worker_plan["requested"]),
            "min_workers": min_workers,
            "max_workers": max_workers,
            "start_workers": int(worker_plan["start_workers"]),
            "adaptive": adaptive,
            "cpu_total": cpu_total,
            "mem_total_gb": round(mem_total_gb, 2),
            "cpu_util_low": float(args.workers_cpu_util_low),
            "cpu_util_high": float(args.workers_cpu_util_high),
            "mem_headroom_gb": float(args.workers_mem_headroom_gb),
            "est_mem_per_worker_gb": float(args.workers_est_mem_gb),
        },
        "summary": summary_metrics,
        "per_file": per_file[:200],
    }
    return result


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="OMEGA v6 cloud backtest payload")
    ap.add_argument("--code-bundle-uri", default="gs://omega_v52/staging/code/omega_core.zip")
    ap.add_argument("--data-pattern", default="gs://omega_v52/omega/v52/frames/host=*/*.parquet")
    ap.add_argument("--test-years", default="2025,2026")
    ap.add_argument(
        "--test-ym",
        default="",
        help="Optional comma-separated date prefixes (YYYY or YYYYMM, e.g. 2025,202601). Applied after --test-years.",
    )
    ap.add_argument("--model-uri", default="", help="Optional trained model pkl in GCS")
    ap.add_argument("--max-files", type=int, default=0, help="0 means use all matched files.")
    ap.add_argument("--max-rows-per-file", type=int, default=0, help="0 means use all rows from each file.")
    ap.add_argument("--output-uri", required=True, help="GCS json path, e.g. gs://bucket/path/backtest_metrics.json")
    ap.add_argument("--peace-threshold", type=float, default=None)
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=None)
    ap.add_argument("--topo-energy-sigma-mult", type=float, default=None)
    ap.add_argument("--workers", type=int, default=0, help="0 means auto based on host CPU+RAM. >0 sets max workers.")
    ap.add_argument("--workers-min", type=int, default=1, help="Minimum active workers during adaptive control.")
    ap.add_argument("--workers-max", type=int, default=0, help="Optional hard cap. 0 means no extra cap.")
    ap.add_argument("--workers-start", type=int, default=0, help="Optional initial workers. 0 means auto warm start.")
    ap.add_argument("--workers-cpu-frac", type=float, default=0.70, help="Auto max workers = cpu_count * this fraction.")
    ap.add_argument("--workers-cpu-util-low", type=float, default=55.0, help="Scale up when CPU util below this.")
    ap.add_argument("--workers-cpu-util-high", type=float, default=88.0, help="Scale down when CPU util above this.")
    ap.add_argument("--workers-mem-headroom-gb", type=float, default=12.0, help="Keep at least this free RAM headroom.")
    ap.add_argument(
        "--workers-est-mem-gb",
        type=float,
        default=3.0,
        help="Estimated RAM per worker used for initial cap and scale-up guard.",
    )
    ap.add_argument("--workers-adjust-step", type=int, default=1, help="Adaptive worker changes per control tick.")
    ap.add_argument("--workers-poll-sec", type=float, default=2.0, help="Adaptive control and scheduler tick interval.")
    args = ap.parse_args()
    args.test_years = [x.strip() for x in str(args.test_years).split(",") if x.strip()]
    args.test_ym = [x.strip() for x in str(args.test_ym).split(",") if x.strip()]
    args.workers_min = max(1, int(args.workers_min))
    if float(args.workers_cpu_frac) <= 0:
        args.workers_cpu_frac = 0.70
    if float(args.workers_cpu_util_high) <= float(args.workers_cpu_util_low):
        args.workers_cpu_util_high = float(args.workers_cpu_util_low) + 5.0
    args.workers_adjust_step = max(1, int(args.workers_adjust_step))
    args.workers_poll_sec = max(0.5, float(args.workers_poll_sec))
    return args


def main() -> None:
    args = parse_args()
    install_dependencies()
    bootstrap_codebase(args.code_bundle_uri)
    result = run_backtest(args)
    _upload_json(result, args.output_uri)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

## 10) Source Code: /tmp/backtest_takeover_aa8abb7.sh
备注：train完成后接管回测提交脚本（机器fallback + worker策略参数）。
来源：/tmp/backtest_takeover_aa8abb7.sh
```bash
#!/usr/bin/env bash
set -u
set -o pipefail

cd /Users/zephryj/work/Omega_vNext || exit 11

TRAIN_JOB="projects/269018079180/locations/us-central1/customJobs/4026903526469795840"
DATA_PATTERN="gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet"
MODEL_URI="gs://omega_v52_central/omega/staging/models/v6/20260219-030000_aa8abb7/omega_v6_xgb_final.pkl"
OUTPUT_URI="gs://omega_v52_central/omega/staging/backtest/v6/20260219-030000_aa8abb7/backtest_metrics.json"
PT="0.5253567667772991"
SRL="1.9773888188507172"
TOPO="5.427559578121958"

# Flexible worker policy (auto scale by CPU+RAM inside run_cloud_backtest.py)
W_MIN="2"
W_MAX="0"
W_START="0"
W_CPU_FRAC="0.75"
W_CPU_LOW="55"
W_CPU_HIGH="88"
W_MEM_HEADROOM_GB="24"
W_EST_MEM_GB="3"
W_ADJUST_STEP="1"
W_POLL_SEC="2"

log(){ printf "[%s] %s\n" "$(date "+%Y-%m-%d %H:%M:%S %Z")" "$*"; }

log "manual backtest takeover watcher started"

while true; do
  STATE=$(gcloud ai custom-jobs describe "$TRAIN_JOB" --region=us-central1 --format="value(state)" 2>/dev/null || true)
  log "train_state=$STATE"

  if [[ "$STATE" == "JOB_STATE_SUCCEEDED" ]]; then
    break
  fi

  if [[ "$STATE" == "JOB_STATE_FAILED" || "$STATE" == "JOB_STATE_CANCELLED" || "$STATE" == "JOB_STATE_EXPIRED" || "$STATE" == "JOB_STATE_PAUSED" ]]; then
    log "train ended non-success; aborting backtest submit"
    exit 20
  fi

  sleep 60
done

for MT in n2-standard-80 n2-standard-64 n2-standard-48 n2-standard-32; do
  log "submit backtest machine=$MT workers(auto) min=$W_MIN cpu_frac=$W_CPU_FRAC"

  if python3 tools/submit_vertex_sweep.py \
    --script tools/run_cloud_backtest.py \
    --machine-type "$MT" \
    --sync \
    --sync-timeout-sec=14400 \
    --force-gcloud-fallback \
    --script-arg="--data-pattern=$DATA_PATTERN" \
    --script-arg="--test-years=2025,2026" \
    --script-arg="--max-files=0" \
    --script-arg="--max-rows-per-file=0" \
    --script-arg="--test-ym=2025,202601" \
    --script-arg="--model-uri=$MODEL_URI" \
    --script-arg="--output-uri=$OUTPUT_URI" \
    --script-arg="--peace-threshold=$PT" \
    --script-arg="--srl-resid-sigma-mult=$SRL" \
    --script-arg="--topo-energy-sigma-mult=$TOPO" \
    --script-arg="--workers=0" \
    --script-arg="--workers-min=$W_MIN" \
    --script-arg="--workers-max=$W_MAX" \
    --script-arg="--workers-start=$W_START" \
    --script-arg="--workers-cpu-frac=$W_CPU_FRAC" \
    --script-arg="--workers-cpu-util-low=$W_CPU_LOW" \
    --script-arg="--workers-cpu-util-high=$W_CPU_HIGH" \
    --script-arg="--workers-mem-headroom-gb=$W_MEM_HEADROOM_GB" \
    --script-arg="--workers-est-mem-gb=$W_EST_MEM_GB" \
    --script-arg="--workers-adjust-step=$W_ADJUST_STEP" \
    --script-arg="--workers-poll-sec=$W_POLL_SEC"; then
    log "backtest completed machine=$MT"
    exit 0
  fi

  rc=$?
  log "backtest failed machine=$MT rc=$rc ; trying lower tier"
  sleep 5
done

log "all machine candidates failed"
exit 30
```

## 11) Source Code: tools/submit_vertex_sweep.py
备注：Vertex提交器（fallback路径、sync等待、timeout行为）。
来源：/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py
```python
#!/usr/bin/env python3
"""
OMEGA v5.2 Vertex AI Sweep Submitter (With Code Injection)
----------------------------------------------------------
1. Zips the local 'omega_core' module.
2. Uploads it to GCS.
3. Submits the 'run_optuna_sweep.py' payload to Vertex AI.

Usage:
    python tools/submit_vertex_sweep.py --script tools/run_optuna_sweep.py
"""

import argparse
import sys
import shutil
import os
import zipfile
import time
import shlex
import subprocess
import tempfile
import textwrap
import warnings
# Suppress annoying Google Cloud Python 3.9 deprecation warnings
warnings.filterwarnings("ignore", ".*Python version 3.9 past its end of life.*")
warnings.filterwarnings("ignore", ".*non-supported Python version.*")

from datetime import datetime
from google.cloud import aiplatform
from google.cloud import storage
from google.cloud.aiplatform_v1.types import custom_job as custom_job_types
from google.api_core import exceptions as gax_exceptions

# Defaults
PROJECT_ID = "gen-lang-client-0250995579"
REGION = "us-central1"
STAGING_BUCKET = "gs://omega_v52_central/staging"
CODE_BUCKET_PATH = "gs://omega_v52/staging/code/omega_core.zip"
PAYLOAD_BUCKET_PREFIX = "gs://omega_v52/staging/code/payloads"

def zip_and_upload_code(repo_root, gcs_uri):
    """
    Builds a self-contained bundle with the modules required by cloud payloads.
    Includes:
      - omega_core/
      - tools/
      - config.py
      - config_v6.py (if present)
    """
    print(f"[*] Packaging code from repo root: {repo_root}", flush=True)

    include_paths = ["omega_core", "tools", "config.py", "config_v6.py"]
    archive_path = os.path.join(repo_root, "omega_core.zip")
    if os.path.exists(archive_path):
        os.remove(archive_path)

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in include_paths:
            abs_path = os.path.join(repo_root, rel)
            if not os.path.exists(abs_path):
                if rel == "config_v6.py":
                    continue
                print(f"[!] Warning: missing bundle path: {abs_path}", flush=True)
                continue

            if os.path.isdir(abs_path):
                for dirpath, _, filenames in os.walk(abs_path):
                    for fn in filenames:
                        if fn.endswith((".pyc", ".pyo")):
                            continue
                        if fn == ".DS_Store":
                            continue
                        full = os.path.join(dirpath, fn)
                        arcname = os.path.relpath(full, repo_root)
                        zf.write(full, arcname=arcname)
            else:
                zf.write(abs_path, arcname=rel)

    print(f"    Created archive: {archive_path}", flush=True)
    
    # Upload
    print(f"[*] Uploading to {gcs_uri}...", flush=True)
    storage_client = storage.Client(project=PROJECT_ID)
    
    # Parse bucket/blob
    bucket_name = gcs_uri.replace("gs://", "").split("/")[0]
    blob_name = "/".join(gcs_uri.replace("gs://", "").split("/")[1:])
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(archive_path)
    
    print("[+] Code bundle uploaded successfully.", flush=True)
    
    # Cleanup local zip
    os.remove(archive_path)

def _is_transient_submit_error(exc: Exception) -> bool:
    if isinstance(exc, (gax_exceptions.ServiceUnavailable, gax_exceptions.DeadlineExceeded)):
        return True
    msg = str(exc).lower()
    if "statuscode.unavailable" in msg or "failed to connect to all addresses" in msg:
        return True
    return False


def _gcs_parse(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket = clean.split("/", 1)[0]
    blob = clean.split("/", 1)[1]
    return bucket, blob


def _upload_payload_script(script_path: str, job_name: str) -> str:
    stem = os.path.splitext(os.path.basename(script_path))[0]
    payload_uri = f"{PAYLOAD_BUCKET_PREFIX}/{job_name}_{stem}.py"
    bucket_name, blob_name = _gcs_parse(payload_uri)
    client = storage.Client(project=PROJECT_ID)
    client.bucket(bucket_name).blob(blob_name).upload_from_filename(script_path)
    return payload_uri


def _render_fallback_shell(code_bundle_uri: str, payload_uri: str, script_args: list[str]) -> str:
    args_joined = " ".join(shlex.quote(str(x)) for x in script_args)
    return textwrap.dedent(
        f"""
        set -euxo pipefail
        python3 -m pip install --quiet google-cloud-storage
        python3 - <<'PY'
        from google.cloud import storage
        import shutil

        def dl(uri: str, out: str) -> None:
            clean = uri.replace("gs://", "", 1)
            bucket, blob = clean.split("/", 1)
            storage.Client().bucket(bucket).blob(blob).download_to_filename(out)

        dl("{code_bundle_uri}", "omega_core.zip")
        dl("{payload_uri}", "payload.py")
        shutil.unpack_archive("omega_core.zip", extract_dir=".")
        PY
        python3 -u payload.py {args_joined}
        """
    ).strip()


def _submit_via_gcloud_fallback(
    script_path: str,
    machine_type: str,
    script_args: list[str],
    sync: bool,
    job_name: str,
    spot: bool = False,
    sync_timeout_sec: int = 0,
) -> None:
    payload_uri = _upload_payload_script(script_path, job_name)
    shell_script = _render_fallback_shell(CODE_BUCKET_PATH, payload_uri, script_args)
    cfg = textwrap.dedent(
        f"""
        workerPoolSpecs:
        - machineSpec:
            machineType: {machine_type}
          replicaCount: 1
          diskSpec:
            bootDiskType: pd-ssd
            bootDiskSizeGb: 100
          containerSpec:
            imageUri: us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest
            command:
            - /bin/bash
            - -lc
            args:
            - |
        """
    ).rstrip("\n")
    indented_shell = "\n".join(("      " + line) if line else "      " for line in shell_script.splitlines())
    cfg = cfg + "\n" + indented_shell + "\n"
    if spot:
        cfg += "scheduling:\n  strategy: SPOT\n"

    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tf:
        tf.write(cfg)
        cfg_path = tf.name

    try:
        cmd = [
            "gcloud",
            "ai",
            "custom-jobs",
            "create",
            f"--project={PROJECT_ID}",
            f"--region={REGION}",
            f"--display-name={job_name}",
            f"--config={cfg_path}",
            "--format=value(name)",
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Fallback submit failed. stderr:\n{e.stderr}", flush=True)
            raise e

        resource_name = (res.stdout or "").strip().splitlines()[-1]
        print(f"[+] Fallback submit succeeded: {resource_name}", flush=True)

        if not sync:
            return

        terminal_ok = {"JOB_STATE_SUCCEEDED"}
        terminal_fail = {
            "JOB_STATE_FAILED",
            "JOB_STATE_CANCELLED",
            "JOB_STATE_EXPIRED",
            "JOB_STATE_PAUSED",
        }
        started_at = time.time()
        describe_fail_streak = 0
        max_describe_fail_streak = 10
        last_state = "JOB_STATE_UNKNOWN"
        while True:
            elapsed = int(max(0, time.time() - started_at))
            if int(sync_timeout_sec) > 0 and elapsed >= int(sync_timeout_sec):
                cancel_cmd = [
                    "gcloud",
                    "ai",
                    "custom-jobs",
                    "cancel",
                    resource_name,
                    f"--project={PROJECT_ID}",
                    f"--region={REGION}",
                ]
                try:
                    subprocess.run(cancel_cmd, capture_output=True, text=True, check=False)
                except Exception:
                    pass
                raise RuntimeError(
                    f"Fallback custom job timed out after {elapsed}s (timeout={sync_timeout_sec}s), "
                    f"resource={resource_name}, last_state={last_state}"
                )

            state_cmd = [
                "gcloud",
                "ai",
                "custom-jobs",
                "describe",
                resource_name,
                f"--project={PROJECT_ID}",
                f"--region={REGION}",
                "--format=value(state)",
            ]
            sres = subprocess.run(state_cmd, capture_output=True, text=True, check=False)
            if sres.returncode != 0:
                describe_fail_streak += 1
                err_tail = ((sres.stderr or "").strip().splitlines() or [""])[-1]
                print(
                    f"    [Fallback] describe error rc={sres.returncode} "
                    f"streak={describe_fail_streak}/{max_describe_fail_streak} elapsed={elapsed}s "
                    f"msg={err_tail}",
                    flush=True,
                )
                if describe_fail_streak >= max_describe_fail_streak:
                    raise RuntimeError(
                        f"Fallback custom job state polling failed {describe_fail_streak} times in a row "
                        f"for resource={resource_name}; last_error={err_tail or 'unknown'}"
                    )
                time.sleep(30)
                continue

            state = (sres.stdout or "").strip()
            if not state:
                describe_fail_streak += 1
                print(
                    f"    [Fallback] describe returned empty state "
                    f"streak={describe_fail_streak}/{max_describe_fail_streak} elapsed={elapsed}s",
                    flush=True,
                )
                if describe_fail_streak >= max_describe_fail_streak:
                    raise RuntimeError(
                        f"Fallback custom job state polling returned empty state "
                        f"{describe_fail_streak} times in a row for resource={resource_name}"
                    )
                time.sleep(30)
                continue

            describe_fail_streak = 0
            last_state = state
            print(f"    [Fallback] state={state} elapsed={elapsed}s", flush=True)
            if state in terminal_ok:
                return
            if state in terminal_fail:
                raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
            time.sleep(30)
    finally:
        try:
            os.remove(cfg_path)
        except Exception:
            pass


def submit_job(
    script_path,
    machine_type="c2-standard-60",
    script_args=None,
    sync=False,
    spot: bool = False,
    force_gcloud_fallback: bool = False,
    max_submit_retries: int = 5,
    sync_timeout_sec: int = 0,
):
    """Submits the job."""
    if script_args is None:
        script_args = []
    if not script_args and os.path.basename(script_path) == "run_optuna_sweep.py":
        script_args = ["--n-trials", "50"]
    
    aiplatform.init(
        project=PROJECT_ID,
        location=REGION,
        staging_bucket=STAGING_BUCKET
    )

    script_stem = os.path.splitext(os.path.basename(script_path))[0]
    job_name = f"omega-v60-{script_stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"[*] Submitting Custom Job: {job_name}", flush=True)
    if spot:
        print("[*] Scheduling strategy: SPOT", flush=True)
    if force_gcloud_fallback:
        print("[*] Forcing gcloud fallback submission path.", flush=True)
        _submit_via_gcloud_fallback(
            script_path=script_path,
            machine_type=machine_type,
            script_args=list(script_args),
            sync=bool(sync),
            job_name=job_name,
            spot=bool(spot),
            sync_timeout_sec=int(sync_timeout_sec),
        )
        return

    job = aiplatform.CustomJob.from_local_script(
        display_name=job_name,
        script_path=script_path,
        container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.0-23:latest",
        replica_count=1,
        machine_type=machine_type,
        args=script_args,
    )

    for attempt in range(1, int(max_submit_retries) + 1):
        try:
            run_kwargs = {"sync": bool(sync)}
            if spot:
                run_kwargs["scheduling_strategy"] = custom_job_types.Scheduling.Strategy.SPOT
            job.run(**run_kwargs)
            break
        except Exception as exc:
            transient = _is_transient_submit_error(exc)
            if not transient:
                raise
            if attempt >= int(max_submit_retries):
                print("[Warn] Vertex SDK submit retries exhausted. Switching to gcloud fallback submit...", flush=True)
                _submit_via_gcloud_fallback(
                    script_path=script_path,
                    machine_type=machine_type,
                    script_args=list(script_args),
                    sync=bool(sync),
                    job_name=job_name,
                    spot=bool(spot),
                    sync_timeout_sec=int(sync_timeout_sec),
                )
                return
            sleep_sec = min(120, 10 * attempt)
            print(
                f"[Warn] Vertex submit transient failure ({attempt}/{max_submit_retries}): {exc}. "
                f"Retrying in {sleep_sec}s...",
                flush=True,
            )
            time.sleep(sleep_sec)
    
    print(f"\n[+] Job submitted! Check Cloud Console.", flush=True)
    try:
        dashboard = getattr(job, "dashboard_uri", "")
    except Exception:
        dashboard = ""
    resource = ""
    try:
        resource = job.resource_name or ""
    except Exception:
        resource = ""
    if not resource:
        try:
            resource = getattr(job, "name", "") or ""
        except Exception:
            resource = ""
    if dashboard:
        print(f"    Dashboard: {dashboard}", flush=True)
    if resource:
        print(f"    Resource : {resource}", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, help="Payload script")
    parser.add_argument("--machine-type", default="c2-standard-60")
    parser.add_argument("--max-submit-retries", type=int, default=5)
    parser.add_argument("--spot", action="store_true", help="Use Spot scheduling strategy for lower cost.")
    parser.add_argument(
        "--force-gcloud-fallback",
        action="store_true",
        help="Skip Vertex SDK submission and submit directly via gcloud custom-jobs create.",
    )
    parser.add_argument(
        "--script-arg",
        action="append",
        default=[],
        help="Argument forwarded to payload script (repeatable).",
    )
    parser.add_argument("--sync", action="store_true", help="Wait until Vertex job completes")
    parser.add_argument(
        "--sync-timeout-sec",
        type=int,
        default=0,
        help="When --sync is set, cancel and fail if terminal state not reached within timeout seconds (0=disabled).",
    )
    args = parser.parse_args()

    # 1. Inject Code
    # Assumes omega_core is in CWD or ../omega_core
    # We look for it relative to this script or CWD
    repo_root = os.getcwd() # Assumption: running from repo root
    code_path = os.path.join(repo_root, "omega_core")
    
    if not os.path.exists(code_path):
        print(f"[!] Error: omega_core not found at {code_path}")
        sys.exit(1)
        
    zip_and_upload_code(repo_root, CODE_BUCKET_PATH)

    # 2. Submit Job
    submit_job(
        args.script,
        args.machine_type,
        script_args=args.script_arg,
        sync=args.sync,
        spot=bool(args.spot),
        force_gcloud_fallback=bool(args.force_gcloud_fallback),
        max_submit_retries=int(args.max_submit_retries),
        sync_timeout_sec=int(args.sync_timeout_sec),
    )
```

## 12) Config Anchors
备注：训练默认XGBoost轮数等参数锚点 + v6特征列锚点。
12.1 /Users/zephryj/work/Omega_vNext/config.py (xgb defaults excerpt)
```python
    model_type: str = "xgboost"  # {"xgboost", "sgd_logistic", "sgd_regression"}

    # SGD hyperparameters (sklearn-style)
    loss: str = "log_loss"
    penalty: str = "l2"
    alpha: float = 1e-4               # L2 regularization strength
    l1_ratio: float = 0.15            # only for elasticnet
    max_iter: int = 1                 # we control epochs ourselves
    tol: Optional[float] = None
    learning_rate: str = "optimal"
    eta0: float = 0.01
    power_t: float = 0.5
    average: bool = True              # Polyak averaging helps stability

    # Training loop
    epochs: int = 3
    batch_size: int = 512
    shuffle_within_file: bool = False

    # Probability to act (evaluation) margin
    decision_margin: float = 0.05

    # XGBoost (v6 default)
    xgb_objective: str = "binary:logistic"
    xgb_eval_metric: str = "logloss"
    xgb_max_depth: int = 6
    xgb_eta: float = 0.1
    xgb_subsample: float = 0.9
    xgb_colsample_bytree: float = 0.9
    xgb_num_boost_round: int = 60


@dataclass(frozen=True)
class BacktestConfig:
    """
    Lightweight evaluation config on windowed samples.
    """
    cost_weight: float = 1.0
    annualization_factor: float = 252.0  # for sharpe proxy, if you interpret a "day" as one unit

    # When computing PnL per window, you can clip extremes to stabilize stats.
    pnl_clip: Optional[float] = None


@dataclass(frozen=True)
class TrainingStageConfig:
    """
    Curriculum stage: train for some epochs on a set of sources.
    """
    name: str
    sources: Sequence[DataSourceConfig]
    epochs: int


@dataclass(frozen=True)
class TrainerConfig:
    """
    Full trainer configuration.
    """
    csv: CSVParseConfig = field(default_factory=CSVParseConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
```
12.2 /Users/zephryj/work/Omega_vNext/config_v6.py (feature anchor excerpt/full)
```python
"""
v6-specific configuration anchors for A-share microstructure.

These dataclasses mirror the architecture constraints in audit/v6.md and
provide a conversion bridge to the runtime `config.L2PipelineConfig`.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Sequence

from config import (
    AShareMicrostructureConfig as RuntimeAShareMicrostructureConfig,
    AShareSessionConfig as RuntimeAShareSessionConfig,
    L2PipelineConfig,
)


@dataclass(frozen=True)
class AShareSessionConfig:
    morning_start_ms: int = 34_200_000   # 09:30:00
    morning_end_ms: int = 41_400_000     # 11:30:00
    afternoon_start_ms: int = 46_800_000 # 13:00:00
    afternoon_end_ms: int = 54_000_000   # 15:00:00

    @property
    def total_duration_ms(self) -> float:
        return float(
            (self.morning_end_ms - self.morning_start_ms)
            + (self.afternoon_end_ms - self.afternoon_start_ms)
        )


@dataclass(frozen=True)
class AShareMicrostructureConfig:
    limit_singularity_eps: float = 1e-5
    t_plus_1_horizon_days: int = 1


@dataclass(frozen=True)
class L2PipelineConfigV6:
    session: AShareSessionConfig = field(default_factory=AShareSessionConfig)
    micro: AShareMicrostructureConfig = field(default_factory=AShareMicrostructureConfig)
    base: L2PipelineConfig = field(default_factory=L2PipelineConfig)

    def to_runtime_config(self) -> L2PipelineConfig:
        runtime_session = RuntimeAShareSessionConfig(
            morning_start_ms=self.session.morning_start_ms,
            morning_end_ms=self.session.morning_end_ms,
            afternoon_start_ms=self.session.afternoon_start_ms,
            afternoon_end_ms=self.session.afternoon_end_ms,
        )
        runtime_micro = RuntimeAShareMicrostructureConfig(
            limit_singularity_eps=self.micro.limit_singularity_eps,
            t_plus_1_horizon_days=self.micro.t_plus_1_horizon_days,
        )
        return replace(self.base, ashare_session=runtime_session, micro=runtime_micro)


def v6_feature_cols(cfg: L2PipelineConfig | None = None) -> list[str]:
    """
    Canonical v6 feature list for tree models and swarm optimizers.
    Keep this centralized so scripts do not hard-code column names.
    """
    runtime_cfg = cfg or L2PipelineConfig()
    topo_race_cols: Sequence[str] = tuple(getattr(runtime_cfg.train, "topology_race_features", ()))
    cols = [
        "sigma_eff",
        "net_ofi",
        "depth_eff",
        "epiplexity",
        "srl_resid",
        "topo_area",
        "topo_energy",
        *topo_race_cols,
        "price_change",
        "bar_duration_ms",
        "adaptive_y",
        "epi_x_srl_resid",
        "epi_x_topo_area",
        "epi_x_net_ofi",
    ]
    return list(dict.fromkeys(cols))


# Architectural anchor used by v60 swarm scripts.
FEATURE_COLS = tuple(v6_feature_cols())
```

## 13) Auditor Notes (Non-source summary)
- This package intentionally embeds raw source/log/json for independent verification.
- No recovery/restart operation was executed while generating this package.
