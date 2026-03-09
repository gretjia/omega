---
entry_id: 20260309_050702_gc_swarm_optuna_pilot_and_champion_retrain_complete
task_id: TASK-V643-GC-SWARM-OPTUNA-REVIVAL-IMPLEMENTATION
timestamp_local: 2026-03-09 05:07:02 +0000
timestamp_utc: 2026-03-09 05:07:02 +0000
operator: Codex
role: commander
branch: main
status: completed
---

# GC Swarm-Optuna Pilot And Champion Retrain: Complete

## 1. Objective

- Execute the first real cloud-parallel Optuna pilot on the immutable `2023,2024` training artifact.
- Aggregate one leaderboard and one champion artifact under the frozen canonical Stage3 gate contract.
- Prove the champion can feed the active trainer and produce a deterministic retrain artifact.

## 2. Final Pilot Run

Pilot prefix:

- `gs://omega_v52_central/omega/staging/swarm_optuna/pilot_20260309_045700`

Controller launch mode:

- `uv run --python /usr/bin/python3.11 --with google-cloud-aiplatform --with google-cloud-storage python tools/launch_vertex_swarm_optuna.py ...`
- live submit path:
  - `--force-gcloud-fallback`

Why this was the stable mode:

- Vertex SDK `from_local_script()` was not reliable in the transient `uv` environment because local packaging expected `setuptools`
- the `gcloud` fallback path was the stable controller path for this session

## 3. Pilot Result

Completed workers:

- `4 / 4`

Completed trials:

- `40 / 40`

Worker evidence:

- `w00`
  - `best_value=0.7909889965715975`
  - `seconds=23.71`
- `w01`
  - `best_value=0.7955525583877963`
  - `seconds=20.32`
- `w02`
  - `best_value=0.7930865773688195`
  - `seconds=28.88`
- `w03`
  - `best_value=0.7931670013136721`
  - `seconds=19.14`

All workers emitted identical canonical fingerprint:

- `stage3_param_contract=canonical_v64_1`
- `signal_epi_threshold=0.5`
- `singularity_threshold=0.1`
- `srl_resid_sigma_mult=2.0`
- `topo_energy_min=2.0`
- `sha256=c77437f3eb3e8347f6bc1ae177dbec83fa4c3e41a10fc9e792f13561a2a230b1`

All workers also proved the temporal split contract:

- `train_year=2023`
- `val_year=2024`
- `train_rows=379331`
- `val_rows=356832`
- `train_max_date=20231229`
- `val_min_date=20240102`
- `dtrain_build_count=1`
- `dval_build_count=1`

## 4. Aggregate Verdict

Aggregate output:

- `gs://omega_v52_central/omega/staging/swarm_optuna/pilot_20260309_045700/aggregate/swarm_leaderboard.json`
- `gs://omega_v52_central/omega/staging/swarm_optuna/pilot_20260309_045700/aggregate/champion_params.json`

Aggregate summary:

- `total_workers=4`
- `total_trials=40`
- `completed_trials=40`
- `champion_pool_size=3`
- `best_val_auc=0.7955525583877963`

Chosen champion under the configured complexity tie-break:

- `worker_id=w01`
- `trial_number=1`
- `best_val_auc=0.7949139136484219`
- params:
  - `max_depth=7`
  - `learning_rate=0.032646890363780275`
  - `subsample=0.9208188474514666`
  - `colsample_bytree=0.7017684503439517`
  - `min_child_weight=1.6257343031626696`
  - `gamma=4.333243204496001`
  - `reg_lambda=0.007658010959494786`
  - `reg_alpha=0.010591250507775794`
  - `num_boost_round=160`

Alpha diagnostics for the chosen champion:

- `alpha_top_decile=-6.836242911392269e-05`
- `alpha_top_quintile=-1.5982936182562814e-05`

## 5. Deterministic Champion Retrain

Retrain output prefix:

- `gs://omega_v52_central/omega/staging/swarm_optuna/pilot_20260309_045700/champion_retrain`

Model artifact:

- `gs://omega_v52_central/omega/staging/swarm_optuna/pilot_20260309_045700/champion_retrain/omega_xgb_final.pkl`

Metrics artifact:

- `gs://omega_v52_central/omega/staging/swarm_optuna/pilot_20260309_045700/champion_retrain/train_metrics.json`

Retrain metrics:

- `status=completed`
- `base_rows=736163`
- `mask_rows=736163`
- `total_training_rows=736163`
- `seconds=3.34`
- `job_id=249734395299102720`

## 6. Runtime Lessons

1. Worker payload bug:
   - first live attempt failed because `Trial` does not expose `.state` inside the objective path
   - fixed in:
     - commit `3647d9c`
2. Search-diversity bug:
   - second live attempt initially wasted cloud breadth because all workers shared the same seed
   - fixed by per-worker seed offsets in:
     - commit `6a31f5a`
3. Retrain quota lesson:
   - default `c2-standard-60` retrain hit Vertex quota limits
   - stable retrain machine for this session:
     - `n2-standard-16`
4. Fallback payload lesson:
   - `run_vertex_xgb_train.py` requires `--code-bundle-uri`
   - when using `gcloud` fallback submit, that arg must be forwarded explicitly into the payload args

## 7. Verdict

- The first live `gc swarm-optuna` pilot is complete.
- It satisfied the pilot target:
  - real multi-worker fan-out
  - `40` completed trials
  - canonical fingerprint enforcement
  - champion artifact
  - trainer-consumable override map
  - deterministic retrain artifact
- The next logical mission is no longer implementation bootstrap.
- The next logical mission is evaluation:
  - outer holdout on `base_matrix_holdout_2025.parquet`
  - final canary on `base_matrix_holdout_2026_01.parquet`
