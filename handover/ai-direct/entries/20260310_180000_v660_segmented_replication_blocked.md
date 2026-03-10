# V660 Regime-Segmented Replication Audit Blocked

Status: Frozen runtime checkpoint
Date: 2026-03-10 18:00 UTC
Mission: V660 Regime-Segmented Replication Audit

## What finished

- deployed commit:
  - `9713641`
- remote synced to:
  - `deploy_v660_9713641@9713641`
- reused frozen runtime basis:
  - `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/campaign_matrix.parquet`
- bounded V660 runtime root:
  - `audit/runtime/v660_segmented_replication_20260310_175918`

## Runtime verdict

The regime-segmented replication audit did **not** pass.

Segment summary:

- `n_segments_total=4`
- `n_segments_eligible=3`
- `n_segments_passing=0`
- `n_segments_failing=3`
- `eligible_segments = [202305, 202306, 202307]`
- `mission_pass=false`

Notable segment outcomes:

- `202305`
  - signed returns:
    - `90.0 -> -0.000534251843241415`
    - `95.0 -> 0.006377284336937434`
    - `97.5 -> -0.0001670535903299541`
  - hazard ladder also failed
- `202306`
  - signed returns:
    - `90.0 -> 0.0029632474540068217`
    - `95.0 -> -0.009684701261401318`
    - `97.5 -> 0.00157729553662997`
- `202307`
  - signed returns:
    - `90.0 -> 0.01365616318253993`
    - `95.0 -> 0.008115122205567217`
    - `97.5 -> 0.018560557712998704`
  - hazard ladder passed
  - strongest-threshold positivity and within-side outperformance passed
  - but signed-return tightening still failed

Ineligible segment:

- `202308`
  - `n_dates_input=6`
  - below the frozen segment minimum

## Consequence

- V660 did not show that the V659 failure was cleanly regime-mixed in the strong sense required by the frozen gate
- no eligible month segment fully passed the unchanged V659 ladder
- broader ML / Vertex / holdout reopening remains blocked

## Evidence

- `audit/v660_segmented_replication_block_evidence.md`
- `audit/runtime/v660_segmented_replication_20260310_175918/segmented_audit.json`
- `audit/runtime/v660_segmented_replication_20260310_175918/segmented_audit.out`
