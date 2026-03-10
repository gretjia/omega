# V658 H1 ML Admission Probe Blocked

Status: Frozen runtime checkpoint
Date: 2026-03-10 09:59 UTC
Mission: V658 Negative-Tail Hazard Admission Probe

## What finished

- deployed commit:
  - `6603e72`
- remote synced to:
  - `deploy_v658_6603e72_a@6603e72`
- reused frozen runtime basis:
  - `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet`
- bounded V658 runtime root:
  - `audit/runtime/v658_ml_admission_probe_h1_2023_20260310_094420`

## Local verification before runtime

- `20 passed in 1.46s`
- `python3 -m py_compile` passed
- direct Gemini code-delta audit:
  - `handover/ai-direct/entries/20260310_093716_v658_code_delta_gemini_pass.md`
  - verdict:
    - `PASS`

## Runtime verdict

The narrow negative-tail hazard admission probe did **not** pass.

Coverage:

- `n_rows_input=265999`
- `n_rows_negative_side=16117`
- `n_rows_admitted=1654`
- `n_dates_admitted=51`

Fold A:

- `logloss_model=0.6873002195762993`
- `logloss_constant=0.6868685069000361`
- `fold_pass=false`
- `alpha=0.50`
  - model beats raw on both economics:
    - `true`
- `alpha=0.25`
  - model beats raw on both economics:
    - `false`

Fold B:

- `logloss_model=0.6552068498403909`
- `logloss_constant=0.6330215280784024`
- `fold_pass=false`
- `alpha=0.50`
  - model beats raw on both economics:
    - `true`
- `alpha=0.25`
  - model beats raw on both economics:
    - `true`

Mission result:

- `mission_pass=false`

## Consequence

- V658 did not satisfy the frozen admission condition
- the admitted-set learner showed some same-count economic improvement
- but it failed the constant-baseline logloss gate on both forward folds
- broader ML / Vertex / holdout reopening remains blocked

## Evidence

- `audit/v658_h1_ml_admission_probe_block_evidence.md`
- `audit/runtime/v658_ml_admission_probe_h1_2023_20260310_094420/admission_probe.json`
- `audit/runtime/v658_ml_admission_probe_h1_2023_20260310_094420/probe.out`
