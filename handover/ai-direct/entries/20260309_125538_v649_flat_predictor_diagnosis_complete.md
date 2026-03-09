---
entry_id: 20260309_125538_v649_flat_predictor_diagnosis_complete
task_id: TASK-V649-PATH-B-FLAT-PREDICTOR-DIAGNOSIS
timestamp_local: 2026-03-09 12:55:38 +0000
timestamp_utc: 2026-03-09 12:55:38 +0000
operator: Codex
role: commander
branch: main
git_head: 8c08f84
status: completed
---

# V649 Diagnosis Complete: Path B Flat-Predictor Collapse

## 1. Scope Executed

V649 stayed fully inside its local-only diagnostic boundary:

- no GCP
- no holdouts
- no promotion
- no `omega_core/*` or Stage3 gate changes

## 2. External And AgentOS Gates

- spec draft:
  - `handover/ai-direct/entries/20260309_124940_v649_path_b_flat_predictor_diagnosis_spec_draft.md`
- Gemini audit:
  - `handover/ai-direct/entries/20260309_125400_v649_spec_draft_gemini_pass.md`
  - verdict:
    - `PASS`
- AgentOS packets:
  - Plan:
    - minimum decisive wave = local data diagnosis + one deterministic probe
  - Math:
    - `PASS WITH FIXES`
  - Runtime:
    - `PASS`

## 3. Data Diagnosis

Frozen train matrix used:

- `gs://omega_v52_central/omega/staging/base_matrix/latest/stage3_train_2023_2024_20260309_005839/base_matrix_train_2023_2024.parquet`

After the frozen canonical physics mask and the frozen `t1_excess_return` construction:

- train rows:
  - `379331`
- val rows:
  - `356832`

### Train target shape

- `mean = 5.7621222091808395e-21`
- `std = 0.007425225216097302`
- `abs_mean = 0.0013424157598614236`
- `abs_median = 0.0`
- zero rows:
  - `346192`
- zero fraction:
  - `0.9126383026960623`
- non-zero fraction:
  - `0.08736169730393772`

### Validation target shape

- `mean = 1.3067596805851654e-20`
- `std = 0.008916774877572281`
- `abs_mean = 0.0017130631526304995`
- `abs_median = 0.0`
- zero rows:
  - `324210`
- zero fraction:
  - `0.9085788270110304`
- non-zero fraction:
  - `0.0914211729889696`

### Constant baseline

- validation mean predictor:
  - `1.244533029128729e-20`
- validation constant-baseline RMSE:
  - `0.008916762383203613`

Interpretation:

- the Path B raw target is extremely zero-dominated on the frozen split
- the median absolute target is literally zero in both train and validation

## 4. Deterministic Probe A: Replay The V648 Trial-0 Shape

Runtime root:

- `audit/runtime/v649_flat_diag_20260309_130000/path_b_probe_summary.json`

Probe config:

- `reg:squarederror`
- replayed from the first V648 smoke trial parameter shape
- no sample weights

Observed result:

- train prediction std:
  - `0.0`
- val prediction std:
  - `0.0`
- train rounded unique predictions:
  - `1`
- val rounded unique predictions:
  - `1`
- train Spearman:
  - `0.0`
- val Spearman:
  - `0.0`
- val sign-AUC:
  - `0.5`
- val RMSE:
  - `0.00891676244840829`
- val decile alpha:
  - `1.244533029128729e-20`
- val quintile alpha:
  - `1.244533029128729e-20`
- non-zero feature importance count:
  - `0`

Interpretation:

- this probe is not merely weak
- it is an exact constant predictor
- it is effectively identical to the constant-baseline regime
- the collapsed V648 smoke was therefore real model degeneracy, not just Optuna bookkeeping

## 5. Deterministic Probe B: Low-Regularization Contrast

Runtime root:

- `audit/runtime/v649_flat_diag_20260309_130000/path_b_probe_low_reg_summary.json`

Probe config:

- `reg:squarederror`
- `max_depth=8`
- `eta=0.1`
- `subsample=1.0`
- `colsample_bytree=1.0`
- `min_child_weight=0.0`
- `gamma=0.0`
- `lambda=0.0`
- `alpha=0.0`
- `num_boost_round=400`
- no sample weights

Observed result:

- train prediction std:
  - `0.0038556894931464714`
- val prediction std:
  - `0.0026945871260126695`
- train rounded unique predictions:
  - `378712`
- val rounded unique predictions:
  - `356326`
- train Spearman:
  - `0.26077593548915856`
- val Spearman:
  - `0.008458359767276777`
- val sign-AUC:
  - `0.49061062250083853`
- val RMSE:
  - `0.009304255819060935`
- val decile alpha:
  - `1.2134796680614228e-05`
- val quintile alpha:
  - `3.123546710946954e-05`
- non-zero feature importance count:
  - `16`

Interpretation:

- Path B is **not** mathematically forced to stay constant
- once regularization and split barriers are relaxed, the model recovers prediction variance and uses all features
- but the recovered model is still not structurally valid:
  - validation Spearman is only weakly positive
  - sign-AUC is still below `0.5`
  - `alpha_top_decile < alpha_top_quintile`

## 6. Final Diagnosis

The dominant failure mode is now much clearer:

1. The raw Path B target on the frozen split is heavily zero-dominated.
2. Under the current V648 search regime, Optuna can settle into exact no-split / constant-predictor basins.
3. That means the V648 collapse was not purely “Path B impossible.”
4. But it also means the current Path B contract is not yet good enough:
   - permissive trees recover variance
   - yet they still fail the structural tail shape

So the true diagnosis is:

- **target sparsity is a real pressure**
- **and the current regression search/regularization regime is too collapse-prone**
- **but even variance recovery alone does not yet yield a promotable model**

## 7. Recommended Next Bounded Axis

Do **not** reopen GCP yet.

Do **not** touch `2025` or `2026-01`.

Recommended next mission axis:

- keep Path B
- keep raw `t1_excess_return`
- keep no sample weights
- keep local-first
- target the **variance-recovery / degeneracy-avoidance axis** only

Concretely, the next mission should test:

- a regression search space that cannot silently collapse into no-split models
- explicit non-degeneracy diagnostics / gates such as:
  - `pred_std > 0`
  - non-zero feature-importance count
  - more than one unique rounded prediction

What this diagnosis does **not** justify yet:

- holdout reruns
- GCP swarm
- promotion
- reopening Path A

## 8. One-Sentence Verdict

V649 proves that V648 failed because the current Path B regime is trapped between:

- a zero-dominated target that invites mean-collapse
- and a search space that can degenerate into constant models

while simple variance recovery alone is still insufficient to satisfy the structural-tail contract.
