# V657 H1 Sign-Aware Threshold Gate Passed

Status: Frozen runtime checkpoint
Date: 2026-03-10 08:35 UTC
Mission: V657 Sign-Aware Threshold Hazard Audit

## What ran

- deployed commit:
  - `03db78e`
- remote synced to:
  - `deploy_v657_03db78e@03db78e`
- reused frozen runtime basis:
  - `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet`
- bounded V657 runtime root:
  - `audit/runtime/v657_sign_aware_threshold_h1_2023_20260310_082459`

## Local verification before runtime

- `16 passed in 0.46s`
- `python3 -m py_compile` passed
- direct Gemini code-delta audit:
  - `handover/ai-direct/entries/20260310_082310_v657_code_delta_gemini_pass.md`
  - verdict:
    - `PASS`

## Runtime verdict

The one-sided sign-aware threshold gate passed.

Strongest clean passing pair:

- `dPsiAmpE_10d`
- `negative` side
- signed mean excess return:
  - `90.0 -> 0.003238607335437723`
  - `95.0 -> 0.004486573885058402`
  - `97.5 -> 0.0079780357263173`
- sign-aware hazard win rate:
  - `90.0 -> 0.6266216077815256`
  - `95.0 -> 0.6455278951688243`
  - `97.5 -> 0.650444762209468`
- tightening summary:
  - `tightening_improves_both = true`

Second passing pair:

- `FreshAmpStar_10d`
- `negative` side
- signed mean excess return:
  - `90.0 -> -0.006762673991573722`
  - `95.0 -> -0.0013526812097862273`
  - `97.5 -> 0.009178225074400428`
- sign-aware hazard win rate:
  - `90.0 -> 0.5486666666666666`
  - `95.0 -> 0.5733333333333333`
  - `97.5 -> 0.5933333333333333`
- tightening summary:
  - `tightening_improves_both = true`

## Evidence

- `audit/v657_h1_sign_aware_threshold_pass_evidence.md`
- `audit/runtime/v657_sign_aware_threshold_h1_2023_20260310_082459/threshold_audit.json`
- `audit/runtime/v657_sign_aware_threshold_h1_2023_20260310_082459/threshold_audit.out`

## Consequence

- V657 no longer blocks at the evaluator stage
- this mission does not itself launch ML
- the next truthful step, if opened, is an ML-admission mission under the new one-sided sign-aware semantics
