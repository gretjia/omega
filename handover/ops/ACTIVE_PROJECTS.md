# Active Projects Board

This file tracks in-flight initiatives. `handover/ai-direct/LATEST.md` remains the single current-state summary; this board stores deeper operational context.

## 1. Snapshot Metadata

- `updated_at_local`: 2026-03-09 02:46:58 +0000
- `updated_at_utc`: 2026-03-09 02:46:58 +0000
- `updated_by`: Codex (GPT-5)

## 2. In-Flight Work

### Project: V643-STAGE3-HOLDOUT-MATRIX-BUILD

- Status: `SPEC_AUDITED_READY`
- Hosts: `controller`, `windows1-w1`, `linux1-lx`
- Goal: build the two missing holdout Stage3 artifacts using the fastest safe host allocation:
  - `base_matrix_holdout_2025.parquet`
  - `base_matrix_holdout_2026_01.parquet`
- Last signals:
  - Gemini audited the execution spec and returned `PASS`
  - live capacity check at audit time:
    - `linux1-lx` had no active Stage2 / Stage3 / train process and about `24 GiB` available memory
    - `windows1-w1` had no active `python` compute process and about `86.7 / 95.8 GiB` free/total memory
  - Windows remains the preferred forge node because:
    - it owns the relevant `2025*` and `202601*` Stage2 corpus locally
    - prior runtime evidence showed it faster than Linux on the repaired path
  - externally audited default mode:
    - Windows forges `2025`
    - Windows then forges `2026-01`
    - Linux runs validation / audit / cloud-controller work in parallel
  - externally audited optimized mode:
    - Linux may forge `2026-01` only after a Linux-local copy of the `202601*.parquet` subset is created and re-asserted locally
- Active gates:
  - generate Windows-local manifests for `2025` and `202601`
  - keep holdout evaluation roots clean and shard-free
  - execute the actual forge runs
- Risks:
  - `2026-01` must be defined by explicit manifest, not `--years 2026` alone
  - evaluation tooling can misbehave if pointed at directories that still contain shard parquet files
  - Linux must not do remote-mounted Windows parquet forge work
- Spec source:
  - `handover/ai-direct/entries/20260309_025500_holdout_basematrix_dual_host_execution_spec.md`
  - `handover/ai-direct/entries/20260309_030257_gemini_holdout_dual_host_spec_audit.md`

### Project: V643-STAGE2-PATHO-EMPTY-FRAME-REMEDIATION

- Status: `PROOF_COMPLETE_PENDING_LINUX_CONNECTIVITY_DECISION`
- Hosts: `controller`, `linux1-lx`, `windows1-w1`
- Goal: fix the normal `v643` Stage2 crash triggered after proactive pathological-symbol drop and prove the repaired three-file set is consumable by Stage3 forge as one input set
- Last signals:
  - remediation commit:
    - `23fd229`
  - local patch status:
    - `tools/stage2_physics_compute.py` hardened for zero-row symbol frames
    - local Stage2 regression suite passed: `15 passed in 5.47s`
  - windows normal-path runtime proof:
    - `20231219_b07c2229.parquet` -> `252844` rows in `86.5s`
    - `20241128_b07c2229.parquet` -> `253227` rows in `128.1s`
    - `20250908_fbd5c8b.parquet` -> `254884` rows in `169.6s`
  - Stage3 forge proof:
    - isolated Windows forge passed with `rows=760955`, `physics_valid_rows=760955`, `epi_pos_rows=716`, `topo_energy_pos_rows=4404`, `signal_gate_rows=3897`
    - produced `base_rows=3074` from the three-file set
  - Linux controller connectivity:
    - `ssh linux1-lx` timed out during this validation window
- Active gates:
  - decide whether a Linux mirror rerun is still required now that Stage3 whole-set proof has passed on Windows
  - restore the canonical controller deploy remotes before the next worker rollout
- Risks:
  - Linux remains operationally unverified in the post-patch state because of SSH reachability, not because of a known code failure
  - the controller deploy path is currently incomplete locally because worker deploy remotes are missing

### Project: V643-STAGE3-TRAIN-BASEMATRIX-2023-2024

- Status: `BASELINE_TRAIN_COMPLETE`
- Hosts: `linux1-lx`, `windows1-w1`, `controller`
- Goal: generate the Linux-side training base matrix for `2023,2024` from the repaired Stage2 corpus without relying on empty `latest_feature_l2/host=linux1`
- Last signals:
  - Linux training base matrix completed at:
    - `/omega_pool/parquet_data/stage3_base_matrix_train_20260308_095850/base_matrix_train_2023_2024.parquet`
  - meta evidence:
    - `base_rows=736163`
    - `input_file_count=484`
    - `batch_count=155`
    - `status=ok`
  - downstream preflight confirmed:
    - year scope is strictly `2023,2024`
    - required training schema is complete
    - training gate diagnostics are non-degenerate
  - baseline Vertex train completed successfully:
    - custom job `5549661916156133376`
    - output prefix `gs://omega_v52_central/omega/staging/models/latest/stage3_train_2023_2024_20260309_005839`
    - `total_training_rows=736163`
- Risks:
  - current active cloud train path is still a single-job offload path, not true cloud-parallel optimization
  - `tools/stage3_full_supervisor.py` currently points to absent bucket `gs://omega_central/...`, while successful live staging still used `gs://omega_v52_central/...`
  - current backtest entrypoints only support year-level filtering, so `2026-01` holdout needs a later explicit file-list or wrapper
  - this artifact is only the training shard of the optimal allocation scheme; separate `2025` and `2026-01` holdout base matrices are still missing

### Project: V643-GC-SWARM-OPTUNA-REVIVAL

- Status: `PROPOSED_SPEC_READY`
- Hosts: `controller`, `GCP Vertex AI`, `linux1-lx`
- Goal: restore the original cloud value proposition by replacing single-job train offload with real cloud-parallel Optuna/XGBoost optimization over the completed `2023,2024` training base matrix
- Historical evidence locked:
  - constitution: cloud is reserved for XGBoost swarm optimization over compressed parquet, not raw ETL
  - `v60` / `v62` handover history explicitly treated swarm optimize as a separate stage
  - archived `submit_swarm_optuna.py` + `swarm_xgb.py` prove the old pattern was many independent jobs, each running its own in-memory study
- Compatibility decisions for v643:
  - raw L2 stays on edge; cloud consumes only a train-only base matrix artifact
  - canonical Stage3 gates remain frozen:
    - `signal_epi_threshold`
    - `singularity_threshold`
    - `srl_resid_sigma_mult`
    - `topo_energy_min`
  - the revived swarm may search XGBoost hyperparameters only unless the Owner explicitly opens a separate math-governance mission
  - optimization and champion retrain must stay strictly inside `2023,2024`
  - `2025 + 2026-01` remains holdout only and is not part of the optimization objective
- Required Stage3 artifact partition:
  - `base_matrix_train_2023_2024.parquet`
  - `base_matrix_holdout_2025.parquet`
  - `base_matrix_holdout_2026_01.parquet`
- Required implementation shape:
  - new active Optuna payload in `tools/`, not archive-only
  - many independent single-replica Vertex jobs, spot-preferred with explicit one-shot on-demand retry
  - temporal validation inside the train set; no random `xgb.cv` across mixed dates
  - leaderboard aggregation plus final deterministic retrain of the chosen params
- Gemini review deltas now merged into the spec:
  - worker-level `2023` train / `2024` validation hard assertion
  - one-time `dtrain` / `dval` construction outside the trial loop
  - aggregator verification of identical frozen canonical-gate fingerprints across workers
  - explicit complexity tie-breaker for champion selection when score deltas are negligible
  - per-trial alpha / excess-return proxy diagnostics in addition to AUC
- Immediate blockers:
  - bucket authority is inconsistent: active supervisor points at absent `gs://omega_central/...`, while the live successful path still used `gs://omega_v52_central/...`
  - no active `tools/run_optuna_sweep.py` / swarm orchestrator currently exists
  - current backtest entrypoints cannot directly express `2026-01`
  - the two holdout artifacts still need to be forged separately with clean date scoping, but the execution spec for that phase is now externally audited and ready
- Spec source:
  - `handover/ai-direct/entries/20260309_012152_gc_swarm_optuna_project_spec.md`
  - `handover/ai-direct/entries/20260309_014638_gemini_swarm_spec_audit.md`
  - `handover/ai-direct/entries/20260309_024658_three_matrix_partition_for_stage3.md`
  - `handover/ai-direct/entries/20260309_025500_holdout_basematrix_dual_host_execution_spec.md`
  - `handover/ai-direct/entries/20260309_030257_gemini_holdout_dual_host_spec_audit.md`

### Project: GCP-LEGACY-STORAGE-CLEANUP

- Status: `COMPLETED`
- Hosts: `controller`, `GCS`
- Goal: remove `v63` or earlier billable cloud artifacts from legacy buckets to reduce spend
- Last signals:
  - verified Vertex AI custom jobs in project `gen-lang-client-0250995579` were all in terminal states before deletion
  - removed old corpus from `gs://omega_v52_central`, including:
    - `omega/omega/v52/frames/**` (about `126.24 GiB`)
    - `omega/staging/base_matrix/v63/**`
    - `omega/staging/models/v63/**`
    - `omega/staging/backtest/v6/**`
    - old code bundles, payloads, `aiplatform-*.tar.gz`, and stale `.done` markers
  - post-delete verification:
    - `gs://omega_v52_central/**` reports `0 B`
    - `gs://omega_v52/**` reports `0 B`
- Notes:
  - current local Linux Stage3 base-matrix run was unaffected because cleanup touched only legacy cloud artifacts

### Project: V62-STAGE1-LINUX

- Status: `COMPLETED`
- Host: `linux1-lx`
- Goal: complete Stage1 Base_L1 for shards `0,1,2`
- Last signals:
  - Stage1 recovery run finished with `Result=success`
  - run block: `ASSIGNED=555`, `COMPLETED=10`, `SKIPPED=545`, `ERROR=0`, `FRAMING_COMPLETE=1`
  - repaired archive dates all backfilled to done markers
- Notes:
  - repaired archives replaced from Windows copies
  - old broken files retained as `*.7z.bad_20260224_*`

### Project: V62-STAGE2-WINDOWS

- Status: `IN_PROGRESS`
- Host: `windows1-w1`
- Goal: produce Feature_L2 from completed Stage1 Base_L1
- Last signals (2026-02-24 16:53 +0800):
  - process active: `stage2_physics_compute.py --workers 1`
  - progress: `WIN_STAGE2_DONE=113 / 191`
  - log path in use: `D:\work\Omega_vNext\audit\stage2_compute.log`
- Risks:
  - throughput is moderate with single-worker mode

### Project: V62-STAGE2-LINUX

- Status: `BLOCKED`
- Host: `linux1-lx`
- Goal: produce Feature_L2 for `host=linux1` (input count `552`)
- Last signals:
  - stage2 unit launch tested
  - blocker hit immediately: `ModuleNotFoundError: No module named 'numba'`
  - unit stopped to avoid no-op churn
- Required action:
  - install `numba` in `/home/zepher/work/Omega_vNext/.venv`
  - relaunch stage2 under `heavy-workload.slice`

### Project: HANDOVER-MAINTENANCE

- Status: `IN_PROGRESS`
- Host: `controller`
- Goal: keep handover as canonical operational gateway
- Current task:
  - sync latest stage recovery + stage2 gate status
  - push docs to GitHub and normalize worker git state

## 3. Completed Recently

- Linux Stage1 bad-archive recovery and full backfill completion.
- `20241204` and `20241212` user-priority archives recovered and reprocessed successfully.

## 4. Update Rules

- Update this board when project state changes materially.
- Keep exact verification timestamps and host evidence.
- Mirror high-level status in `handover/ai-direct/LATEST.md`.
