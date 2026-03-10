# V658 Negative-Tail Hazard Admission Probe

Status: Frozen external audit authority
Date: 2026-03-10
Scope: Post-V657 contingent upgrade

## Central Judgment

After V657, the narrowest truthful remaining blocker is no longer pre-ML signal semantics.

V657 showed that at least some OMEGA campaign-state signals do have downstream economic utility when they are treated as:

- one-sided
- sign-aware
- threshold / hazard objects

rather than as:

- unconditional cross-sectional rankers

The remaining blocker is the translation of that utility into a mathematically consistent learner / admission protocol without drifting back into the wrong objective.

## Short Verdict

V657 is a real pass, but it is not a license for broad ML reopening.

It earns admission only to a very narrow, local-only ML-admission probe built around:

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- semantics:
  - sign-aware hazard

It does not justify reopening:

- general ranking / regression
- Vertex
- holdout workflows

## Frozen Input Basis

Reuse the frozen V655B H1 campaign matrix:

- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet`

Do not rerun forge.

Do not rewrite signals.

Do not change threshold search space.

## Single Allowed Change Axis

Change only:

- the admission protocol

from:

- raw threshold trigger

to:

- trigger-conditioned hazard learner

Everything else remains frozen.

## Frozen Primary Contract

Primary signal:

- `x_{i,d} = dPsiAmpE_10d`

Primary side:

- `negative`

Primary horizon:

- `10d`

Primary admission threshold:

- negative-side `90th` percentile of absolute magnitude

Shadow control only:

- `FreshAmpStar_10d`
- `negative`

No search is allowed over:

- signal family
- side
- horizon
- admission threshold

## Frozen Formulas

Negative-side universe on date `d`:

- `N_d = { i : x_{i,d} < -eps }`

Admission quantile:

- `q^-_{d,90} = Q_0.90({ |x_{i,d}| : i in N_d })`

Admission mask:

- `G_{i,d} = 1{ i in N_d and |x_{i,d}| >= q^-_{d,90} }`

Primary binary label:

- `Y_{i,d} = 1{ barrier_10d(i,d) = -1 }`

Primary signed economic diagnostic:

- `R_{i,d} = -excess_ret_t1_to_10d(i,d)`

Frozen feature set candidate:

- `dPsiAmpE_10d`
- `FreshAmpStar_10d`
- `PsiAmpE_10d`
- `PsiAmpStar_10d`
- `OmegaAmpE_10d`
- `OmegaAmpStar_10d`
- `vol20d`
- `pulse_count`
- `pulse_concentration`

Learner target:

- estimate:
  - `p_hat_{i,d} ~= P(Y_{i,d}=1 | Z_{i,d}, G_{i,d}=1)`

Fixed loss:

- binary logistic loss only

## Model Comparison Contract

The learner is evaluated only inside the admitted set:

- `G = 1`

For each validation date `d` and selection fraction `alpha in {0.50, 0.25}`:

Model-selected subset:

- `S_model(d, alpha) = { i : G_{i,d}=1 and p_hat_{i,d} >= Q_{1-alpha,d}(p_hat) }`

Raw same-count baseline:

- `S_raw(d, alpha) = { i : G_{i,d}=1 and |x_{i,d}| >= Q_{1-alpha,d}(|x|) }`

Date-neutral signed return:

- `Rbar_model(alpha) = mean_d mean_{i in S_model(d, alpha)} R_{i,d}`
- `Rbar_raw(alpha) = mean_d mean_{i in S_raw(d, alpha)} R_{i,d}`

Date-neutral hazard success:

- `Hbar_model(alpha) = mean_d mean_{i in S_model(d, alpha)} Y_{i,d}`
- `Hbar_raw(alpha) = mean_d mean_{i in S_raw(d, alpha)} Y_{i,d}`

Constant-baseline classifier comparison:

- `logloss_model < logloss_constant`

## Runtime Shape

Wave 1 remains:

- local-only
- no Vertex / GCP
- no holdout
- no Optuna
- no forge rerun

Use two forward folds on `pure_date`:

- Fold A:
  - first `60%` dates train
  - next `20%` dates validate
- Fold B:
  - first `80%` dates train
  - final `20%` dates validate

## Fixed Learner Capacity

Use one fixed learner only:

- `binary:logistic`

Example fixed low-capacity parameters:

- `max_depth = 3`
- `eta = 0.05`
- `min_child_weight = 20`
- `subsample = 0.8`
- `colsample_bytree = 0.8`
- `n_estimators <= 200`

No hyperparameter search is allowed.

## V658 Success Criteria

On each forward validation fold:

1. `logloss_model < logloss_constant`
2. for at least one `alpha in {0.50, 0.25}`:
   - `Rbar_model(alpha) > Rbar_raw(alpha)`
   - `Hbar_model(alpha) > Hbar_raw(alpha)`

## V658 Kill Condition

Kill V658 and keep ML closed if:

- the admission probe is implemented cleanly
- forge and transition derivations remain frozen
- but the fixed learner cannot beat:
  - constant-baseline logloss
  - and raw same-count baseline economics

That outcome would mean:

- the signal may have direct trigger utility
- but learner sharpening is not yet justified
