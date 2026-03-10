# V660 Regime-Segmented Replication Mission Open

Status: Active mission
Date: 2026-03-10 17:53 UTC
Mission: V660 Regime-Segmented Replication Audit

## What changed

V660 opens after V659 blocked on the fixed-contract replication ladder.

The single allowed change axis is:

- evaluation-sample partition inside the already-forged V659 replication block

Everything else remains frozen.

## Frozen Contract

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- thresholds:
  - `90 / 95 / 97.5`

## Frozen Runtime Basis

- `audit/runtime/v659_replication_linux_20230508_20230927_20260310_114408/campaign_matrix.parquet`

## Next Runtime Step

- deploy from a clean worktree
- run `tools/run_campaign_segmented_replication_audit.py` on the frozen V659 campaign matrix
- record a pass / block verdict from the frozen V660 rules only
