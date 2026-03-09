---
entry_id: 20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass
task_id: TASK-V645-GC-ASYMMETRIC-LABEL-PIVOT-PATH-A
timestamp_local: 2026-03-09 08:43:15 +0000
timestamp_utc: 2026-03-09 08:43:15 +0000
operator: Codex
role: commander
branch: main
git_head: fdedba9
hosts_touched: [controller, windows1-w1, linux1-lx]
status: completed
---

# V645 Path A Retrain And Fresh Holdout: Partial Pass

## 1. Objective

- Take the winning local Path A trial from:
  - `handover/ai-direct/entries/20260309_080141_v645_path_a_local_micro_sweep_positive.md`
- Retrain a fresh model on full `2023,2024`
- Evaluate that fresh artifact on new isolated holdout roots:
  - `2025`
  - `2026-01`
- Preserve the frozen baseline verdict from:
  - `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`

## 2. Code Wave Applied

Files changed:

- `tools/run_vertex_xgb_train.py`
- `tests/test_vertex_train_weight_mode.py`

What changed:

- training payload now supports:
  - `weight_mode=physics_abs_singularity`
  - `weight_mode=abs_excess_return`
- local retrain can run without forcing `--code-bundle-uri`
- dependency bootstrap now first checks whether required modules already exist
- training metrics now record:
  - `weight_mode`

Local validation:

- `python3 -m py_compile tools/run_vertex_xgb_train.py tests/test_vertex_train_weight_mode.py`
- `uv run --python /usr/bin/python3.11 --with pytest --with numpy pytest -q tests/test_vertex_train_weight_mode.py`
- result:
  - `2 passed in 0.41s`

## 3. Fresh Path A Retrain

Runtime root:

- `audit/runtime/v645_path_a_retrain_20260309_081034`

Output root:

- `audit/runtime/v645_path_a_retrain_20260309_081034/model`

Winning params promoted into retrain:

- `max_depth=5`
- `learning_rate=0.023200867504756827`
- `subsample=0.8170784332632994`
- `colsample_bytree=0.6563696899899051`
- `min_child_weight=9.824166788294436`
- `gamma=0.3727532183988541`
- `reg_lambda=8.862326508576253`
- `reg_alpha=0.7264803074826727`
- `num_boost_round=119`
- `weight_mode=abs_excess_return`

Retrain summary:

- `status=completed`
- `base_rows=736163`
- `mask_rows=736163`
- `total_training_rows=736163`
- `seconds=4.13`
- `stage3_param_contract=canonical_v64_1`

Artifacts:

- model:
  - `audit/runtime/v645_path_a_retrain_20260309_081034/model/omega_xgb_final.pkl`
- metrics:
  - `audit/runtime/v645_path_a_retrain_20260309_081034/model/train_metrics.json`

## 4. Fresh 2025 Holdout

Execution host:

- `windows1-w1`

Runtime:

- `C:\Python314\python.exe`
- `xgboost 3.1.3`

Output:

- `D:\work\Omega_vNext\audit\runtime\holdout_eval_path_a_2025_20260309_084300\results\holdout_metrics.json`

Scope proof:

- `rows=385674`
- `date_min=20250102`
- `date_max=20251230`
- `expected_date_prefix=2025`

Metrics:

- `auc=0.5392160785083961`
- `alpha_top_decile=8.733709672524669e-05`
- `alpha_top_quintile=0.00011493529740600989`
- `seconds=0.35`

## 5. Fresh 2026-01 Holdout

Execution host:

- `linux1-lx`

Runtime:

- `/home/zepher/work/Omega_vNext/.venv/bin/python`
- `xgboost 1.7.6`

Output:

- `/home/zepher/work/Omega_vNext/audit/runtime/holdout_eval_path_a_2026_01_20260309_082500/results/holdout_metrics.json`

Scope proof:

- `rows=26167`
- `date_min=20260105`
- `date_max=20260129`
- `expected_date_prefix=202601`

Metrics:

- `auc=0.5444775661061128`
- `alpha_top_decile=9.280953096675273e-05`
- `alpha_top_quintile=-9.652552940517018e-05`
- `seconds=2.07`

## 6. Comparison Against Frozen Baseline

Frozen baseline:

- `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`

`2025` changed from:

- `auc=0.8235655072013123`
- `alpha_top_decile=-0.00011772199576048959`
- `alpha_top_quintile=-3.151894696127132e-05`

to:

- `auc=0.5392160785083961`
- `alpha_top_decile=8.733709672524669e-05`
- `alpha_top_quintile=0.00011493529740600989`

`2026-01` changed from:

- `auc=0.8097376879061562`
- `alpha_top_decile=-0.0008295253060950895`
- `alpha_top_quintile=-0.0002874404451020619`

to:

- `auc=0.5444775661061128`
- `alpha_top_decile=9.280953096675273e-05`
- `alpha_top_quintile=-9.652552940517018e-05`

## 7. Verdict

This run materially changes the diagnosis.

What improved:

- the Path A retrain flipped `2025` holdout tail alpha positive at both:
  - decile
  - quintile
- the same retrain also flipped `2026-01` decile alpha positive
- `2026-01` quintile alpha remained negative, but improved materially relative to the frozen baseline

What regressed:

- holdout `AUC` collapsed from the old `~0.81-0.82` range to the new `~0.54` range

Meaning:

- the learner-interface pivot is doing real economic work
- but it is over-correcting away from the old high-AUC classifier regime
- this is therefore **not** a production-ready champion yet

Operational decision:

- do **not** widen back into larger GC spend yet
- keep working locally / dual-host first
- the next mission boundary is now narrower:
  - refine Path A further
  - or compare against Path B regression
- but do not overwrite either:
  - the frozen old holdout baseline
  - or these fresh Path A holdout outputs
