---
entry_id: 20260309_100901_v646_path_a_pow0625_fourth_slice_local_only
task_id: TASK-V646-PATH-A-REFINEMENT-SLICE-4
timestamp_local: 2026-03-09 10:09:01 +0000
timestamp_utc: 2026-03-09 10:09:01 +0000
operator: Codex
role: commander
branch: main
git_head: 011fd93
hosts_touched: [controller]
status: completed
---

# V646 Path A Fourth Slice: `pow_0p625_abs_excess_return` Local Only

## 1. Objective

- Complete the quarter-step monotone power-family scan under V646
- Record this slice separately from slices 1 through 3
- Stay local-only unless the slice beats the frozen first-slice local gate

## 2. Slice Identity

Weight mode:

- `pow_0p625_abs_excess_return`

Exact transform:

- `abs(t1_excess_return) ** 0.625`

Runtime root:

- `audit/runtime/v646_path_a_refine4_local_20260309_100700`

Shape:

- local only
- `1` worker
- `10` trials
- `train_year=2023`
- `val_year=2024`
- `objective_metric=alpha_top_quintile`
- `min_val_auc=0.501`
- `learner_mode=binary_logistic_sign`

## 3. Result

Summary:

- `n_trials=10`
- `n_completed=10`
- `n_auc_guardrail_passed=5`
- `best_value=8.109984294116173e-05`
- `seconds=20.0`

Winning trial:

- `trial_number=7`
- `val_auc=0.5497136622521415`
- `alpha_top_decile=0.00017377787307968167`
- `alpha_top_quintile=8.109984294116173e-05`

Winning params:

- `max_depth=5`
- `learning_rate=0.023200867504756827`
- `subsample=0.8170784332632994`
- `colsample_bytree=0.6563696899899051`
- `min_child_weight=9.824166788294436`
- `gamma=0.3727532183988541`
- `reg_lambda=8.862326508576253`
- `reg_alpha=0.7264803074826727`
- `num_boost_round=119`

## 4. Compare Against Frozen References

Versus frozen V645 local Path A:

- old:
  - `6.299795037680448e-05`
- new:
  - `8.109984294116173e-05`
- delta:
  - `+1.8101892564357248e-05`

Versus frozen V646 first slice:

- first-slice local best:
  - `0.00010345929832144143`
- this fourth slice:
  - `8.109984294116173e-05`
- delta:
  - `-2.23594553802897e-05`

## 5. Verdict

This fourth slice is valid standalone evidence, but it does **not** earn promotion.

Why:

- it beats the old V645 local Path A reference
- but it remains below the frozen first V646 slice

Operational consequence:

- no retrain
- no fresh holdout rerun
- the monotone power-family quarter-step scan is now complete
