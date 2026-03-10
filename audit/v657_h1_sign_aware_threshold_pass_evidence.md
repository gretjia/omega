# V657 H1 Sign-Aware Threshold Pass Evidence

Status: Frozen evidence packet
Date: 2026-03-10
Mission: V657 Sign-Aware Threshold Hazard Audit

## Runtime basis

- reused existing campaign matrix:
  - `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet`
- no forge rerun
- no signal-family rewrite
- no ML / Vertex / holdout use

## Runtime root

- `audit/runtime/v657_sign_aware_threshold_h1_2023_20260310_082459`

## Output artifacts

- `audit/runtime/v657_sign_aware_threshold_h1_2023_20260310_082459/threshold_audit.json`
- `audit/runtime/v657_sign_aware_threshold_h1_2023_20260310_082459/threshold_audit.out`

## Frozen input facts reused from V655B

- `rows=271447`
- `symbols=5448`
- `raw_candidates=136439`
- `kept_pulses=30449`
- widened excess-return zero fractions:
  - `excess_ret_t1_to_5d_zero_fraction = 0.0`
  - `excess_ret_t1_to_10d_zero_fraction = 0.0`
  - `excess_ret_t1_to_20d_zero_fraction = 0.0`

## Evaluator change axis only

The V657 runtime changed only evaluator semantics:

- sign-aware
- one-sided
- threshold ladder:
  - `90.0`
  - `95.0`
  - `97.5`
- reused V656 transition families only:
  - `dPsiAmpE_10d`
  - `dPsiAmpE_20d`
  - `dPsiAmpStar_10d`
  - `dPsiAmpStar_20d`
  - `FreshAmpE_10d`
  - `FreshAmpE_20d`
  - `FreshAmpStar_10d`
  - `FreshAmpStar_20d`

## Passing signal-side pairs

### Pair 1

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- signed mean excess return by threshold:
  - `90.0 -> 0.003238607335437723`
  - `95.0 -> 0.004486573885058402`
  - `97.5 -> 0.0079780357263173`
- sign-aware hazard win rate by threshold:
  - `90.0 -> 0.6266216077815256`
  - `95.0 -> 0.6455278951688243`
  - `97.5 -> 0.650444762209468`
- scored rows by threshold:
  - `90.0 -> 1654`
  - `95.0 -> 851`
  - `97.5 -> 453`
- scored dates:
  - `51`
- tightening summary:
  - `signed_mean_excess_non_decreasing = true`
  - `hazard_win_rate_non_decreasing = true`
  - `n_rows_non_increasing = true`
  - `tightening_improves_both = true`
  - `strongest_threshold_positive = true`

### Pair 2

- signal:
  - `FreshAmpStar_10d`
- side:
  - `negative`
- signed mean excess return by threshold:
  - `90.0 -> -0.006762673991573722`
  - `95.0 -> -0.0013526812097862273`
  - `97.5 -> 0.009178225074400428`
- sign-aware hazard win rate by threshold:
  - `90.0 -> 0.5486666666666666`
  - `95.0 -> 0.5733333333333333`
  - `97.5 -> 0.5933333333333333`
- scored rows by threshold:
  - `90.0 -> 106`
  - `95.0 -> 72`
  - `97.5 -> 54`
- scored dates:
  - `50`
- tightening summary:
  - `signed_mean_excess_non_decreasing = true`
  - `hazard_win_rate_non_decreasing = true`
  - `n_rows_non_increasing = true`
  - `tightening_improves_both = true`
  - `strongest_threshold_positive = true`

## Supporting non-pass but positive-tail cases

- `FreshAmpE_20d` negative:
  - signed mean excess stays positive across all thresholds:
    - `0.013907049109323246`
    - `0.015008362814388337`
    - `0.01836270588441161`
  - sign-aware hazard remains positive:
    - `0.7233333333333333`
    - `0.696`
    - `0.7133333333333333`
  - but `hazard_win_rate_non_decreasing = false`

- `dPsiAmpE_20d` negative:
  - signed mean excess stays positive across all thresholds:
    - `0.0006706816077242892`
    - `0.01496141416534702`
    - `0.017406389964555413`
  - sign-aware hazard remains positive:
    - `0.6636408859161306`
    - `0.6764023413043865`
    - `0.6722399604752546`
  - but `hazard_win_rate_non_decreasing = false`

## Gate verdict

V657 success condition was:

- at least one signal / side / horizon pair shows:
  - positive signed excess return
  - positive sign-aware hazard edge
- and that pair improves as thresholds tighten

This condition is satisfied.

## Operational consequence

- V657 sign-aware one-sided threshold gate is earned
- this mission did not reopen ML by itself
- no ML / Vertex / holdout run was launched inside V657
