# Entry ID: 20260306_080057_stage2_pause_for_audit_findings

## Summary

The Owner requested an immediate pause of the dual-node full `Stage 2` run after an auditor reported new issues.

The stop has been executed on both workers without fail-ledger expansion.

## Final state at pause

### linux1-lx

- runner state: stopped
- service: `stage2_full_20260306_linux1.service` is inactive
- output root: `/omega_pool/parquet_data/stage2_full_20260306/l2/host=linux1`
- `.done` count at pause: `2`
- fail ledger count at pause: `0`
- last cleanly completed files:
  - `20230103_fbd5c8b.parquet`
  - `20230104_fbd5c8b.parquet`

### windows1-w1

- runner state: stopped
- output root: `D:\\Omega_frames\\stage2_full_20260306\\l2\\host=windows1`
- `.done` count at pause: `10`
- fail ledger count at pause: `0`
- log confirms clean completion through:
  - `20240730_fbd5c8b.parquet`
- next batch had already started:
  - `20240731_fbd5c8b.parquet`

## What must not happen next

1. Do not resume either worker until the new audit findings are triaged.
2. Do not delete the run-specific outputs, manifests, logs, or ledgers under `stage2_full_20260306`.
3. Do not promote these paused outputs into `latest_feature_l2`.

## Resume anchor points

- Linux log:
  - `/home/zepher/work/Omega_vNext/audit/runtime/stage2_full_20260306/linux_stage2.log`
- Windows log:
  - `D:\\work\\Omega_vNext\\audit\\runtime\\stage2_full_20260306\\windows_stage2.log`
- Linux manifest split:
  - `20230103_fbd5c8b.parquet -> 20240716_fbd5c8b.parquet`
- Windows manifest split:
  - `20240717_b07c2229.parquet -> 20260130_fbd5c8b.parquet`

## Next action

Triage the newly surfaced audit findings first. Only after that should the Commander decide whether to:

- resume from current run roots
- regenerate a subset
- or discard this paused run and relaunch from scratch
