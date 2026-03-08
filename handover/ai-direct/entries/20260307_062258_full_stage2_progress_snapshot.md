# Entry ID: FULL STAGE2 PROGRESS SNAPSHOT

## Context
Live run:
- run tag: `stage2_full_20260307_v643fix`
- code: `6b0afff`
- route: engineering-speed path + Stage2 ordering-contract fix + input gates

## Current progress snapshot
As of this entry:

### linux1-lx
- host output: `/omega_pool/parquet_data/stage2_full_20260307_v643fix/l2/host=linux1`
- split size: `371`
- completed `.done`: `19`
- failed `.fail`: `0`
- current batch: `20230206_fbd5c8b.parquet`
- observed mean per-file runtime: `220.39s` over `18` completed full-run samples
- remaining files: `352`
- ETA: about `21.55 hours`
- health: healthy; `__BATCH_OK__` continues; no fail markers

### windows1-w1
- host output: `D:\Omega_frames\stage2_full_20260307_v643fix\l2\host=windows1`
- split size: `372`
- completed `.done`: `44`
- failed `.fail`: `0`
- current batch: `20240925_fbd5c8b.parquet`
- observed mean per-file runtime: `88.14s` over `43` completed full-run samples
- remaining files: `328`
- ETA: about `8.03 hours`
- health: healthy; `__BATCH_OK__` continues; no fail markers

## Operational interpretation
- The run is stable on both nodes.
- `windows1` is materially faster and is expected to finish much earlier.
- `linux1` remains the long pole for cluster completion.
- Cross-host assist is still blocked by the deferred `n_ticks` dtype drift until that schema issue is normalized.

## Deferred schema note
- Current V64.3 canonical columns are valid on both nodes.
- Deferred closure remains:
  - `linux1`: `n_ticks = UInt32`
  - `windows1`: `n_ticks = UInt64`
- This does not block disjoint host-local running.
- It **does** block future cross-host assist / mixed-host merge until normalized.
