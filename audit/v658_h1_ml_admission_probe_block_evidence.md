# V658 H1 ML Admission Probe Block Evidence

Status: Frozen evidence packet
Date: 2026-03-10
Mission: V658 Negative-Tail Hazard Admission Probe

## Scope

This file records only the concrete V658 H1 runtime evidence needed to justify the current no-go result for the narrow ML-admission probe.

It does not introduce a new mission direction.

## Runtime Artifacts

Evidence:

- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet`
- `audit/runtime/v658_ml_admission_probe_h1_2023_20260310_094420/admission_probe.json`
- `audit/runtime/v658_ml_admission_probe_h1_2023_20260310_094420/probe.out`

## Frozen Runtime Basis

V658 did not rerun forge.

It reused the frozen V655B H1 campaign matrix and the frozen V656 transition derivations:

- `rows=271447`
- `symbols=5448`
- `raw_candidates=136439`
- `kept_pulses=30449`
- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

## Fixed Admission Contract Tested

V658 kept the contract frozen to:

- primary signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- horizon:
  - `10d`
- admission threshold:
  - negative-side `90th` percentile of absolute magnitude
- learner:
  - fixed low-capacity `binary:logistic`
- shadow control retained as read-only feature:
  - `FreshAmpStar_10d`

Admitted-set coverage:

- `n_rows_input=265999`
- `n_rows_negative_side=16117`
- `n_rows_admitted=1654`
- `n_dates_negative_side=51`
- `n_dates_admitted=51`

## Fold Results

### Fold A

- train dates:
  - `20230104 -> 20230313`
- validation dates:
  - `20230315 -> 20230328`
- `n_train_rows=658`
- `n_val_rows=400`
- `train_positive_rate=0.6580547112462006`
- `val_positive_rate=0.59`
- `logloss_model=0.6873002195762993`
- `logloss_constant=0.6868685069000361`
- `fold_pass=false`

Alpha summaries:

- `alpha=0.50`
  - model:
    - `date_neutral_signed_return=-0.008009175692313426`
    - `date_neutral_hazard_win_rate=0.6420248447204969`
  - raw same-count:
    - `date_neutral_signed_return=-0.013088503925875555`
    - `date_neutral_hazard_win_rate=0.6318434970826273`
  - `model_beats_raw_on_both=true`
- `alpha=0.25`
  - model:
    - `date_neutral_signed_return=-0.00236658535784952`
    - `date_neutral_hazard_win_rate=0.6317599067599067`
  - raw same-count:
    - `date_neutral_signed_return=-0.011079643487730278`
    - `date_neutral_hazard_win_rate=0.6987762237762236`
  - `model_beats_raw_on_both=false`

### Fold B

- train dates:
  - `20230104 -> 20230328`
- validation dates:
  - `20230329 -> 20230417`
- `n_train_rows=1058`
- `n_val_rows=596`
- `train_positive_rate=0.6323251417769377`
- `val_positive_rate=0.6778523489932886`
- `logloss_model=0.6552068498403909`
- `logloss_constant=0.6330215280784024`
- `fold_pass=false`

Alpha summaries:

- `alpha=0.50`
  - model:
    - `date_neutral_signed_return=0.01723276068951436`
    - `date_neutral_hazard_win_rate=0.6771290650600995`
  - raw same-count:
    - `date_neutral_signed_return=0.01677128029570749`
    - `date_neutral_hazard_win_rate=0.6536534984810847`
  - `model_beats_raw_on_both=true`
- `alpha=0.25`
  - model:
    - `date_neutral_signed_return=0.024610954870540755`
    - `date_neutral_hazard_win_rate=0.6845154845154844`
  - raw same-count:
    - `date_neutral_signed_return=0.02318666294373417`
    - `date_neutral_hazard_win_rate=0.6167832167832167`
  - `model_beats_raw_on_both=true`

## Exact No-Go Facts

Under the frozen V658 mission gate:

1. The admitted set was built only from the fixed V657 contract.
2. The learner stayed inside the admitted set only.
3. Both forward folds emitted model-vs-raw same-count economics.
4. Fold A did not beat the constant-baseline logloss.
5. Fold B did not beat the constant-baseline logloss.
6. Therefore neither fold satisfied the full V658 pass condition.
7. Therefore `mission_pass=false`.
8. Therefore broader ML reopening remains blocked.
