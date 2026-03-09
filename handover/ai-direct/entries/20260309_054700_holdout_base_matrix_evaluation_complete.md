---
entry_id: 20260309_054700_holdout_base_matrix_evaluation_complete
task_id: TASK-V643-HOLDOUT-BASEMATRIX-EVAL
timestamp_local: 2026-03-09 05:47:00 +0000
timestamp_utc: 2026-03-09 05:47:00 +0000
operator: Codex
role: commander
branch: main
git_head: a1dda60
hosts_touched: [controller, windows1-w1, linux1-lx]
status: completed
---

# Holdout Base-Matrix Evaluation: Complete

## 1. Objective

- Evaluate the completed swarm champion retrain artifact on the two isolated downstream Stage3 artifacts:
  - `base_matrix_holdout_2025.parquet`
  - `base_matrix_holdout_2026_01.parquet`
- Reuse active train/Optuna semantics:
  - same feature columns
  - same `t1_excess_return` label construction
  - same singularity masking
- Preserve dataset isolation:
  - no holdout data enters optimization or retraining

## 2. Code Added

- New active tool:
  - `tools/evaluate_xgb_on_base_matrix.py`
- New regression file:
  - `tests/test_vertex_holdout_eval.py`

Local validation:

- `python3 -m py_compile tools/evaluate_xgb_on_base_matrix.py tests/test_vertex_holdout_eval.py`
- `uv run --python /usr/bin/python3.11 --with pytest --with polars --with xgboost --with optuna --with scikit-learn pytest -q tests/test_vertex_holdout_eval.py tests/test_vertex_optuna_split.py tests/test_vertex_swarm_aggregate.py`
- result:
  - `9 passed in 2.02s`

## 3. Deployment And Runtime Recovery

The canonical controller deploy path was partially broken at mission start.

Recovered controller remotes:

- `linux`
  - `linux1-lx:/home/zepher/work/Omega_vNext`
- `windows`
  - `ext::ssh windows1-w1 %S D:/work/Omega_vNext/.git`

Important live lesson:

- `tools/deploy.py` still cannot push the repaired Windows remote because it does not pass:
  - `-c protocol.ext.allow=always`
- Linux worker sync succeeded through the recovered remote.
- Windows worker sync had to be completed with a manual controller-side push:
  - `git -c protocol.ext.allow=always push windows HEAD:main --force`

Champion artifacts handed to workers:

- model:
  - `gs://omega_v52_central/omega/staging/swarm_optuna/pilot_20260309_045700/champion_retrain/omega_xgb_final.pkl`
- retrain metrics:
  - `gs://omega_v52_central/omega/staging/swarm_optuna/pilot_20260309_045700/champion_retrain/train_metrics.json`

Artifact handoff method:

- a temporary controller-side HTTP server on the Tailscale address
- rationale:
  - small artifacts only
  - avoids copying large holdout parquet files between hosts
  - avoids flaky direct stdin binary streaming to Windows in this shell stack

## 4. 2025 Outer Holdout

Execution host:

- `windows1-w1`

Runtime:

- `C:\Python314\python.exe`
- `xgboost 3.1.3`

Inputs:

- base matrix:
  - `D:\Omega_frames\stage3_holdout_2025_eval_20260309_031430\base_matrix_holdout_2025.parquet`
- output:
  - `D:\work\Omega_vNext\audit\runtime\holdout_eval_2025_20260309_054300\results\holdout_metrics.json`

Scope proof:

- `rows=385674`
- `date_min=20250102`
- `date_max=20251230`
- `year_count=1`
- `expected_date_prefix=2025`

Class balance:

- `positive_rows=13761`
- `negative_rows=371913`

Metrics:

- `auc=0.8235655072013123`
- `alpha_top_decile=-0.00011772199576048959`
- `alpha_top_quintile=-3.151894696127132e-05`
- `seconds=0.47`

Gate validation:

- canonical fingerprint:
  - `stage3_param_contract=canonical_v64_1`
  - `signal_epi_threshold=0.5`
  - `singularity_threshold=0.1`
  - `srl_resid_sigma_mult=2.0`
  - `topo_energy_min=2.0`
- retrain overrides matched the evaluator arguments exactly

## 5. 2026-01 Final Canary

Execution host:

- `linux1-lx`

Runtime:

- `/home/zepher/work/Omega_vNext/.venv/bin/python`
- `xgboost 1.7.6`

Important compatibility note:

- the serialized champion pickle loaded successfully under `xgboost 1.7.6`
- it emitted the expected old-pickle compatibility warning, but the evaluation completed successfully

Inputs:

- base matrix:
  - `/omega_pool/parquet_data/stage3_holdout_2026_01_eval_20260309_031248/base_matrix_holdout_2026_01.parquet`
- output:
  - `/home/zepher/work/Omega_vNext/audit/runtime/holdout_eval_2026_01_20260309_054300/results/holdout_metrics.json`

Scope proof:

- `rows=26167`
- `date_min=20260105`
- `date_max=20260129`
- `year_count=1`
- `expected_date_prefix=202601`

Class balance:

- `positive_rows=883`
- `negative_rows=25284`

Metrics:

- `auc=0.8097376879061562`
- `alpha_top_decile=-0.0008295253060950895`
- `alpha_top_quintile=-0.0002874404451020619`
- `seconds=1.97`

Gate validation:

- canonical fingerprint:
  - `stage3_param_contract=canonical_v64_1`
  - `signal_epi_threshold=0.5`
  - `singularity_threshold=0.1`
  - `srl_resid_sigma_mult=2.0`
  - `topo_energy_min=2.0`
- retrain overrides matched the evaluator arguments exactly

## 6. Verdict

- The downstream holdout evaluation phase is complete.
- The same champion retrain artifact was evaluated on both isolated holdout artifacts.
- Both runs passed exact scope and canonical-gate checks.
- Both runs achieved strong classification AUC on future data.

But the decisive finding is:

- `2025` top-quantile alpha proxy is negative.
- `2026-01` top-quantile alpha proxy is also negative.

Therefore:

- the current champion is **not yet validated as a positive future alpha ranker**
- the next logical mission is **not** more holdout evaluation
- the next logical mission is to revise the cloud optimization objective / champion selection rule so that future sweeps do not optimize AUC while leaving future alpha negative
- this result is now frozen as an audit baseline:
  - later missions may add new evidence
  - they may not overwrite these recorded output paths or reinterpret them away
