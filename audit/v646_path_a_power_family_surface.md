# V646 Path A Power-Family Surface

Status: Frozen for external audit
Owner: Codex Commander
Date: 2026-03-09

## 1. Purpose

This document summarizes the full bounded `Path A` monotone power-family scan that was taken under V646.

It exists so an external auditor can read one file and see:

- what slices were actually run
- which slices remained local-only
- which slices were promoted to fresh retrain / fresh holdout
- what tradeoff surface was observed
- why the current family is now considered sufficiently explored

## 2. Canonical Boundaries

All slices in this document kept the following fixed:

- `omega_core/*` unchanged
- `canonical_v64_1` Stage3 gates unchanged
- `learner_mode=binary_logistic_sign`
- label:
  - `t1_excess_return > 0`
- temporal split:
  - `2023 -> 2024`
- objective:
  - `alpha_top_quintile`
- AUC guardrail:
  - `min_val_auc=0.501`

The only thing changed across slices was the Path A training-weight shape.

## 3. Slice Ladder

### Slice 0: Frozen V645 Path A Baseline

- weight shape:
  - `abs(t1_excess_return)`
- local best:
  - `6.299795037680448e-05`
- winning local `val_auc`:
  - `0.5885732459839437`
- promoted:
  - `yes`
- fresh `2025` holdout:
  - `auc=0.5392160785083961`
  - `alpha_top_quintile=0.00011493529740600989`
- fresh `2026-01` holdout:
  - `auc=0.5444775661061128`
  - `alpha_top_quintile=-9.652552940517018e-05`
- authority:
  - `handover/ai-direct/entries/20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass.md`

### Slice 1: First V646 Slice

- weight shape:
  - `sqrt(abs(t1_excess_return))`
- local best:
  - `0.00010345929832144143`
- winning local `val_auc`:
  - `0.5227522534018058`
- promoted:
  - `yes`
- fresh `2025` holdout:
  - `auc=0.4824941845966547`
  - `alpha_top_quintile=4.034581066262975e-05`
- fresh `2026-01` holdout:
  - `auc=0.48036047756825606`
  - `alpha_top_quintile=7.837793103528386e-05`
- authority:
  - `handover/ai-direct/entries/20260309_094727_v646_path_a_sqrt_refinement_mixed_holdout_verdict.md`

### Slice 2: Second V646 Slice

- weight shape:
  - `abs(t1_excess_return) ** 0.75`
- local best:
  - `8.786963269826855e-05`
- winning local `val_auc`:
  - `0.5533170029579313`
- promoted:
  - `no`
- authority:
  - `handover/ai-direct/entries/20260309_100300_v646_path_a_pow075_second_slice_local_only.md`

### Slice 3: Third V646 Slice

- weight shape:
  - `abs(t1_excess_return) ** 0.875`
- local best:
  - `8.216041648343417e-05`
- winning local `val_auc`:
  - `0.5351796685110878`
- promoted:
  - `no`
- authority:
  - `handover/ai-direct/entries/20260309_100830_v646_path_a_pow0875_third_slice_local_only.md`

### Slice 4: Fourth V646 Slice

- weight shape:
  - `abs(t1_excess_return) ** 0.625`
- local best:
  - `8.109984294116173e-05`
- winning local `val_auc`:
  - `0.5497136622521415`
- promoted:
  - `no`
- authority:
  - `handover/ai-direct/entries/20260309_100901_v646_path_a_pow0625_fourth_slice_local_only.md`

## 4. Rank Order

By local objective:

1. Slice 1:
   - `sqrt`
   - `0.00010345929832144143`
2. Slice 2:
   - `pow_0.75`
   - `8.786963269826855e-05`
3. Slice 3:
   - `pow_0.875`
   - `8.216041648343417e-05`
4. Slice 4:
   - `pow_0.625`
   - `8.109984294116173e-05`
5. Slice 0:
   - `abs`
   - `6.299795037680448e-05`

## 5. Structural Findings

### Finding 1

The power-family scan did produce local gains relative to the original `abs` baseline.

Every tested tempered transform beat Slice 0 on the local `2023 -> 2024` objective.

### Finding 2

The first promoted V646 slice (`sqrt`) remains the local winner.

No later midpoint or quarter-step interpolation beat it locally.

### Finding 3

The non-sqrt tempered slices all converged back to the original V645 local winning parameter region:

- winning trial:
  - `trial_number=7`
- parameter shape:
  - `max_depth=5`
  - `learning_rate=0.023200867504756827`
  - `subsample=0.8170784332632994`
  - `colsample_bytree=0.6563696899899051`
  - `min_child_weight=9.824166788294436`
  - `gamma=0.3727532183988541`
  - `reg_lambda=8.862326508576253`
  - `reg_alpha=0.7264803074826727`
  - `num_boost_round=119`

The promoted `sqrt` slice won from a different region:

- winning trial:
  - `trial_number=6`

So the current evidence does not suggest a smooth monotone interpolation that gradually improves both local objective and holdout behavior.

### Finding 4

The two promoted slices split the holdout tradeoff:

- Slice 0 (`abs`) is stronger on `2025 alpha_top_quintile`
- Slice 1 (`sqrt`) fixes the sign of `2026-01 alpha_top_quintile`

No intermediate local-only slice beat Slice 1 locally, so no additional holdout spend was justified inside this same power family.

## 6. Closing Verdict

The bounded `Path A` monotone power-family scan is now complete enough for external audit.

Why it is considered complete:

- endpoints were observed:
  - `abs`
  - `sqrt`
- midpoint was observed:
  - `0.75`
- quarter-points were observed:
  - `0.875`
  - `0.625`
- all later local-only slices were compared against the frozen first promoted V646 slice
- none beat the first promoted slice locally
- therefore none earned retrain / holdout promotion

## 7. Auditor Shortcut

If an auditor wants the shortest reliable read order for this family:

1. `audit/v644_mediocristan_label_bottleneck.md`
2. `handover/ai-direct/entries/20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass.md`
3. `handover/ai-direct/entries/20260309_094727_v646_path_a_sqrt_refinement_mixed_holdout_verdict.md`
4. `handover/ai-direct/entries/20260309_100300_v646_path_a_pow075_second_slice_local_only.md`
5. `handover/ai-direct/entries/20260309_100830_v646_path_a_pow0875_third_slice_local_only.md`
6. `handover/ai-direct/entries/20260309_100901_v646_path_a_pow0625_fourth_slice_local_only.md`
7. this file
