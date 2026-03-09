---
entry_id: 20260309_094727_v646_path_a_sqrt_refinement_mixed_holdout_verdict
task_id: TASK-V646-PATH-A-REFINEMENT-SLICE-1
timestamp_local: 2026-03-09 09:47:27 +0000
timestamp_utc: 2026-03-09 09:47:27 +0000
operator: Codex
role: commander
branch: main
git_head: 421b749
hosts_touched: [controller, windows1-w1, linux1-lx]
status: completed
---

# V646 Path A Sqrt Refinement: Mixed Holdout Verdict

## 1. Objective

- Execute the first bounded `Path A` refinement slice under the active V646 mission
- Keep `omega_core/*` and frozen `canonical_v64_1` Stage3 gates unchanged
- Stay local-first until a refined `Path A` candidate earns promotion
- Compare the refined slice against the frozen V645 `Path A` reference, not against the older AUC-first baseline

## 2. AgentOS Convergence Used

All three V646 packets converged before execution:

- Plan Agent:
  - introduce exactly one new tempered `Path A` weight mode
  - choose:
    - `sqrt_abs_excess_return`
  - keep everything else fixed for the first slice:
    - `learner_mode=binary_logistic_sign`
    - `objective_metric=alpha_top_quintile`
    - `min_val_auc=0.501`
    - local-only `10` trial micro-sweep
- Math Auditor:
  - `PASS WITH FIXES`
  - monotone transforms of `abs(t1_excess_return)` are allowed inside `Path A`
  - no row-membership, label, temporal-split, or gate mutation allowed
- Runtime Auditor:
  - `PASS`
  - local-only first slice
  - fresh runtime roots only
  - no fresh retrain / holdout unless the refined local candidate beats the frozen V645 local `Path A` reference

## 3. Code Wave Applied

Files changed:

- `tools/run_optuna_sweep.py`
- `tests/test_vertex_optuna_split.py`
- `tools/run_vertex_xgb_train.py`
- `tests/test_vertex_train_weight_mode.py`

What changed:

- added a new tempered `Path A` weight mode:
  - `sqrt_abs_excess_return`
- sweep payload now supports:
  - `physics_abs_singularity`
  - `abs_excess_return`
  - `sqrt_abs_excess_return`
- retrain payload now supports the same three weight modes
- promotion parity is now explicit:
  - the same weight mode used to win locally can be carried into full retrain

Local validation:

- `uv run --python /usr/bin/python3.11 --with pytest --with polars --with xgboost --with optuna --with numpy pytest -q tests/test_vertex_optuna_split.py tests/test_vertex_swarm_aggregate.py tests/test_vertex_train_weight_mode.py`
- result:
  - `16 passed in 0.98s`

## 4. Local First-Slice Result

Runtime root:

- `audit/runtime/v646_path_a_refine_local_20260309_093827`

Shape:

- local only
- `1` worker
- `10` trials
- `train_year=2023`
- `val_year=2024`
- `objective_metric=alpha_top_quintile`
- `min_val_auc=0.501`
- `learner_mode=binary_logistic_sign`
- `weight_mode=sqrt_abs_excess_return`

Summary:

- `n_trials=10`
- `n_completed=10`
- `n_auc_guardrail_passed=6`
- `best_value=0.00010345929832144143`
- old V645 local `Path A` reference:
  - `6.299795037680448e-05`
- improvement factor:
  - `1.6422645134108143`

Winning trial:

- `trial_number=6`
- `val_auc=0.5227522534018058`
- `alpha_top_decile=0.00010345929832144143`
- `alpha_top_quintile=0.00010345929832144143`
- params:
  - `max_depth=6`
  - `learning_rate=0.15826541904647565`
  - `subsample=0.6353970008207678`
  - `colsample_bytree=0.6783931449676581`
  - `min_child_weight=1.4975001780159187`
  - `gamma=1.6266516538163218`
  - `reg_lambda=0.03586816498627549`
  - `reg_alpha=0.002273762810253686`
  - `num_boost_round=340`

## 5. Fresh Retrain Promoted From The Winning Slice

Runtime root:

- `audit/runtime/v646_path_a_retrain_20260309_094045`

Output root:

- `audit/runtime/v646_path_a_retrain_20260309_094045/model`

Retrain summary:

- `status=completed`
- `base_rows=736163`
- `mask_rows=736163`
- `total_training_rows=736163`
- `seconds=10.25`
- `stage3_param_contract=canonical_v64_1`
- `weight_mode=sqrt_abs_excess_return`

Artifacts:

- model:
  - `audit/runtime/v646_path_a_retrain_20260309_094045/model/omega_xgb_final.pkl`
- metrics:
  - `audit/runtime/v646_path_a_retrain_20260309_094045/model/train_metrics.json`

## 6. Fresh 2025 Holdout

Execution host:

- `windows1-w1`

Runtime:

- `C:\Python314\python.exe`
- `xgboost 3.1.3`

Output:

- `D:\work\Omega_vNext\audit\runtime\holdout_eval_v646_2025_20260309_094500\results\holdout_metrics.json`

Scope proof:

- `rows=385674`
- `date_min=20250102`
- `date_max=20251230`
- `expected_date_prefix=2025`

Metrics:

- `auc=0.4824941845966547`
- `alpha_top_decile=5.8729942639996136e-05`
- `alpha_top_quintile=4.034581066262975e-05`
- `seconds=0.37`

## 7. Fresh 2026-01 Holdout

Execution host:

- `linux1-lx`

Runtime:

- `/home/zepher/work/Omega_vNext/.venv/bin/python`
- `xgboost 1.7.6`

Output:

- `/home/zepher/work/Omega_vNext/audit/runtime/holdout_eval_v646_2026_01_20260309_094500/results/holdout_metrics.json`

Scope proof:

- `rows=26167`
- `date_min=20260105`
- `date_max=20260129`
- `expected_date_prefix=202601`

Metrics:

- `auc=0.48036047756825606`
- `alpha_top_decile=2.8311302723807468e-05`
- `alpha_top_quintile=7.837793103528386e-05`
- `seconds=1.69`

## 8. Direct Compare Against The Frozen V645 Path A Reference

Frozen V645 reference:

- `handover/ai-direct/entries/20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass.md`

`2025` changed from:

- `auc=0.5392160785083961`
- `alpha_top_decile=8.733709672524669e-05`
- `alpha_top_quintile=0.00011493529740600989`

to:

- `auc=0.4824941845966547`
- `alpha_top_decile=5.8729942639996136e-05`
- `alpha_top_quintile=4.034581066262975e-05`

delta:

- `auc=-0.05672189391174143`
- `alpha_top_decile=-2.8607154085250553e-05`
- `alpha_top_quintile=-7.458948674338014e-05`

`2026-01` changed from:

- `auc=0.5444775661061128`
- `alpha_top_decile=9.280953096675273e-05`
- `alpha_top_quintile=-9.652552940517018e-05`

to:

- `auc=0.48036047756825606`
- `alpha_top_decile=2.8311302723807468e-05`
- `alpha_top_quintile=7.837793103528386e-05`

delta:

- `auc=-0.06411708853785669`
- `alpha_top_decile=-6.449822824294526e-05`
- `alpha_top_quintile=0.00017490346044045404`

## 9. Verdict

This first V646 refinement slice is a **mixed holdout result**, not a clean promotion.

What improved:

- the refined local slice clearly beat the frozen V645 local `Path A` reference
- fresh `2026-01` `alpha_top_quintile` flipped from negative to positive
- both fresh holdouts stayed economically positive on at least one tail metric:
  - `2025`: decile and quintile both positive
  - `2026-01`: decile and quintile both positive

What regressed:

- both fresh holdout `AUC` values fell below `0.5`
- `2025` alpha weakened materially relative to the frozen V645 `Path A` branch
- `2026-01` decile alpha also weakened materially relative to the frozen V645 `Path A` branch

Meaning:

- tempering the `Path A` weight shape helped the local `2023 -> 2024` objective
- and it fixed the specific V645 `2026-01` quintile-sign defect
- but it over-traded against the broader V645 fresh-holdout profile

Operational decision:

- keep V646 open
- freeze this first-slice result as new audit evidence
- do **not** widen back into GC
- do **not** replace the V645 `Path A` fresh holdout branch as the leading promoted candidate yet
- next step remains local-first:
  - AgentOS should choose the second bounded `Path A` refinement slice
  - aim to preserve the V646 `2026-01` quintile fix without giving up as much `2025` strength or AUC stability

## 10. Runtime Lessons

- Windows SSH remained intermittently unstable during this run
- the most reliable Windows execution path was:
  - encode the PowerShell script locally
  - send it through `powershell -EncodedCommand`
  - reuse the controller-side temporary HTTP server for model handoff
- cross-runtime XGBoost version skew still emits old-pickle warnings:
  - Windows: `3.1.3`
  - Linux: `1.7.6`
  - evaluation still completed successfully on both hosts
