# Entry ID: CROSS-HOST N_TICKS DTYPE DRIFT

## Summary
A non-core but operationally important schema drift was observed during the live `stage2_full_20260307_v643fix` run:

- `linux1` emits `n_ticks: UInt32`
- `windows1` emits `n_ticks: UInt64`

## Why it matters
This does **not** block current V64.3 canonical math validation, because `n_ticks` is not part of the canonical compression / topology / SRL signal chain.

It **does** matter for future cross-host assist or merged downstream consumption:

- as long as `linux1` and `windows1` keep writing disjoint host-specific outputs, the run can continue safely
- before any future `windows -> linux` tail assist, mixed-host merge, or promotion into a unified downstream dataset, `n_ticks` dtype must be normalized

## Operational rule
Treat this as a `cross-host assist gate`:

- current split run: allowed to continue
- future cross-host assist: blocked until `n_ticks` dtype is unified

## Status
Deferred for later closure. Record retained in handover so the next mission does not ignore it.
