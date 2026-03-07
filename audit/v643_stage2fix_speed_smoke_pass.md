# V64.3 Stage2 Ordering-Contract Remediation Smoke PASS

## Verdict

`PASS` for the smoke objective.

This run validates that the Stage2 ordering-contract remediation removes the historical `all-zero` collapse without changing the approved V64.3 canonical runtime math core.

## Scope of this verdict

This is not a new mathematical re-definition.

It is a runtime/integration verdict on the following claim:

- after repairing the Stage2 -> kernel ordering contract and adding fail-fast input-contract gates, the canonical signal chain becomes non-degenerate and remains consumable across `Stage2 -> forge -> training -> backtest`

## Canonical math unchanged

The following remained fixed:

- prequential MDL compression path (`Delta k = 0`)
- no `has_singularity -> srl_resid = 0` overwrite
- no `bits_srl` second compression branch
- topology gate semantics and signal gate semantics remain the V64.3 approved ones

## Validating smoke basis

Workspace:

- `/home/zepher/work/Omega_vNext_v643_stage2fix_speed_smoke`

Contiguous 5-day window:

- `20250723_fbd5c8b.parquet`
- `20250724_b07c2229.parquet`
- `20250725_b07c2229.parquet`
- `20250728_b07c2229.parquet`
- `20250729_b07c2229.parquet`

## Stage2 proof

Stage2 completed with:

- `success=5`
- `failed=0`
- `STAGE2_SECONDS=1879.12`

Aggregate non-degeneracy proof:

- `rows = 1,366,691`
- `epi_pos_rows = 2,006`
- `topo_area_nonzero_rows = 11,247`
- `topo_energy_pos_rows = 11,276`
- `sv_nonzero_rows = 10,822`
- `signal_rows = 466`
- `direction_nonnull_rows = 1,366,691`

These values are sufficient to reject the prior `all-zero` failure mode.

Probe symbol evidence (`20250725_b07c2229 / 002097.SZ`):

- `topo_area_max_abs = 14.930243421263738`
- `topo_energy_max = 39.53119115288678`
- `epiplexity_max = 4.1506694353795215`
- `signal_rows = 2`

## Downstream proof

### Forge
- input contract: PASS
- `base_rows = 8549`
- `symbols_total = 7245`
- `FORGE_SECONDS = 186.89`

### Training
- input contract: PASS
- `base_rows = 8549`
- `mask_rows = 8549`
- `total_training_rows = 8549`
- `TRAIN_SECONDS = 14.90`

### Backtest
- input contract: PASS
- `n_frames = 1055429.0`
- `BACKTEST_SECONDS = 6.80`
- `Orthogonality = 0.00012346729376811198`

## Engineering reflections

1. The root cause was an integration defect, not a Stage1 defect.
2. A gate is only useful if it is placed at the correct granularity. The initial batch-level `window_len` gate created false file failures and had to be relaxed to diagnostic mode.
3. A smoke harness must set explicit years when validating non-baseline hot weeks; default year filters can silently empty the run.
4. A smoke can no longer be accepted if it only proves process completion. It must prove non-degenerate canonical signal activation.

## Release relevance

This smoke is sufficient to justify committing the local remediation tree to `main`, provided the fixed-memory handover and lessons ledgers are updated in the same commit.
