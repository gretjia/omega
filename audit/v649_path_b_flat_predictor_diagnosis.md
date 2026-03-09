# V649 Path B Flat-Predictor Diagnosis

Status: Frozen diagnostic audit
Date: 2026-03-09
Scope: V648 blocked local smoke -> V649 local-only diagnosis

## Short Verdict

V649 confirms that the first Path B contract did not fail because continuous-label regression is impossible.

It failed because:

1. the frozen raw `t1_excess_return` target is extremely zero-dominated on the `2023 -> 2024` split,
2. the V648 regression search/regularization regime could collapse into a true no-split constant predictor,
3. simple variance recovery alone is still not enough to satisfy the structural-tail contract.

So the next justified axis is:

- stay inside Path B,
- stay local-only,
- target variance-recovery / degeneracy-avoidance,
- do not reopen GCP or holdouts yet.

## Canonical Frozen Constraints

The following remained frozen throughout V649:

- `omega_core/*`
- `canonical_v64_1` Stage3 gates
- frozen train matrix authority
- `2025` outer holdout isolation
- `2026-01` final canary isolation
- no GCP
- no promotion

## Primary Evidence

Mission records:

- `handover/ai-direct/entries/20260309_124249_v648_local_contract_and_smoke_blocked.md`
- `handover/ai-direct/entries/20260309_124940_v649_path_b_flat_predictor_diagnosis_spec_draft.md`
- `handover/ai-direct/entries/20260309_125400_v649_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_125420_v649_path_b_flat_predictor_diagnosis_mission_open.md`
- `handover/ai-direct/entries/20260309_125538_v649_flat_predictor_diagnosis_complete.md`

Runtime authorities:

- `audit/runtime/v648_local_smoke_20260309_123500/workers/w00/study_summary.json`
- `audit/runtime/v648_local_smoke_20260309_123500/workers/w00/trials.jsonl`
- `audit/runtime/v649_flat_diag_20260309_130000/path_b_probe_summary.json`
- `audit/runtime/v649_flat_diag_20260309_130000/path_b_probe_low_reg_summary.json`

Code context:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`

## Data Diagnosis

Frozen train matrix:

- `gs://omega_v52_central/omega/staging/base_matrix/latest/stage3_train_2023_2024_20260309_005839/base_matrix_train_2023_2024.parquet`

After the frozen canonical physics mask and frozen `t1_excess_return` construction:

- train rows:
  - `379331`
- validation rows:
  - `356832`

Train target shape:

- `std = 0.007425225216097302`
- `abs_mean = 0.0013424157598614236`
- `abs_median = 0.0`
- zero fraction:
  - `0.9126383026960623`

Validation target shape:

- `std = 0.008916774877572281`
- `abs_mean = 0.0017130631526304995`
- `abs_median = 0.0`
- zero fraction:
  - `0.9085788270110304`

Interpretation:

- the regression target is dominated by exact zeros,
- the median absolute magnitude is zero on both splits,
- so mean-collapse is a real default basin.

## Probe A: Replay The V648 Trial-0 Shape

Observed:

- `train_pred_std = 0.0`
- `val_pred_std = 0.0`
- rounded unique predictions:
  - `1`
- non-zero feature importance count:
  - `0`
- `val_spearman_ic = 0.0`
- `val_auc_sign = 0.5`
- `val_rmse = 0.00891676244840829`

Interpretation:

- this is an exact constant predictor,
- not a weak but non-degenerate model,
- so the V648 smoke collapse was a real no-split degeneration.

## Probe B: Low-Regularization Contrast

Observed:

- `train_pred_std = 0.0038556894931464714`
- `val_pred_std = 0.0026945871260126695`
- train rounded unique predictions:
  - `378712`
- val rounded unique predictions:
  - `356326`
- non-zero feature importance count:
  - `16`
- `val_spearman_ic = 0.008458359767276777`
- `val_auc_sign = 0.49061062250083853`
- `val_alpha_top_decile = 1.2134796680614228e-05`
- `val_alpha_top_quintile = 3.123546710946954e-05`

Interpretation:

- Path B is not mathematically forced to remain constant,
- but variance recovery alone still fails structural integrity:
  - `sign-AUC < 0.5`
  - `alpha_top_decile < alpha_top_quintile`

## Ranked Root-Cause View

1. Zero-dominated raw target invites constant-baseline collapse.
2. The current V648 regression search/regularization regime permits exact no-split basins.
3. Recovering prediction variance does not, by itself, recover structural-tail validity.

## What V649 Does And Does Not Prove

V649 proves:

- the V648 blocked local smoke was real model degeneracy,
- Path B is still a live branch,
- the next mission should not be cloud expansion.

V649 does not prove:

- that Path B is promotion-ready,
- that holdout evaluation should resume,
- that a new loss function or target transform is already justified.

## Recommended Next Mission Shape

Recommended next bounded axis:

- Path B only
- local-only
- no holdouts
- no GCP
- no Path A reopening

Recommended problem statement:

- `Path B variance-recovery / degeneracy-avoidance under the frozen raw excess-return label`

Recommended explicit gates:

- `pred_std > 0`
- non-zero feature-importance count
- more than one rounded prediction value

Only after those gates are met should the repo consider another structural ranking check.
