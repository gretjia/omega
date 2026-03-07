# 2026-03-07 03:23:37 UTC | V64.3 Stage2 Ordering Fix + Speed Route Smoke PASS

## Summary

The `all-zero` critical defect has been broken on the engineered-speed route without changing the approved V64.3 canonical runtime math core.

This run used the speed-route codebase plus the Stage2 ordering-contract remediation and input-contract fail-fast gates. The run proved that the canonical chain is no longer degenerate:

- `topo_area` is non-zero
- `topo_energy` is non-zero
- `epiplexity` is non-zero
- `singularity_vector` is non-zero
- `is_signal` is non-zero
- `direction` is populated and consumable downstream

## Root cause recap

The root cause was not Stage1.

- Stage1 raw parquet remained symbol-contiguous.
- The defect was the ETL -> kernel interface contract inside Stage2.
- `build_l2_features_from_l1()` emitted symbol-interleaved frames.
- `apply_recursive_physics()` computed rolling topology / compression on boundary logic that assumed symbol/date continuity.
- Rolling windows were therefore reset incorrectly, collapsing the canonical chain to zero.

The remediation repaired ordering inside the Stage2 -> kernel handoff and added fail-fast input-contract gates on the main operational path.

## Smoke workspace

- workspace: `/home/zepher/work/Omega_vNext_v643_stage2fix_speed_smoke`
- run root: `/home/zepher/work/Omega_vNext_v643_stage2fix_speed_smoke/.tmp/smoke_v64_v643_stage2fix_speed`

Preserved historical evidence workspaces:

- `/home/zepher/work/Omega_vNext_v643_smoke`
- `/home/zepher/work/Omega_vNext_v643_speed_smoke`
- `/home/zepher/work/Omega_vNext_v643_traincmp_smoke`
- `/home/zepher/work/Omega_vNext_v643_probe_smoke`

## Input window

The validating contiguous 5-day hot week was:

- `20250723_fbd5c8b.parquet`
- `20250724_b07c2229.parquet`
- `20250725_b07c2229.parquet`
- `20250728_b07c2229.parquet`
- `20250729_b07c2229.parquet`

## Stage 2 proof

Stage2 completed successfully on all 5 files.

- `success=5`
- `failed=0`
- `STAGE2_SECONDS=1879.12`

Aggregate proof over the 5 L2 files:

- `rows = 1,366,691`
- `epi_pos_rows = 2,006`
- `topo_area_nonzero_rows = 11,247`
- `topo_energy_pos_rows = 11,276`
- `sv_nonzero_rows = 10,822`
- `signal_rows = 466`
- `direction_nonnull_rows = 1,366,691`
- `epi_max = 35.13918333942269`
- `topo_energy_max = 64.36587101405199`
- `sv_abs_max = 2222.1659387380196`

Known probe symbol validation on `20250725_b07c2229 / 002097.SZ`:

- `rows = 177`
- `topo_area_max_abs = 14.930243421263738`
- `topo_energy_max = 39.53119115288678`
- `epiplexity_max = 4.1506694353795215`
- `signal_rows = 2`

## Downstream chain

### Forge

- input contract: PASS
- `base_rows = 8549`
- `symbols_total = 7245`
- `seconds = 184.79`
- `FORGE_SECONDS = 186.89`

### Training

- input contract: PASS
- local smoke contract used lightweight comparison hyperparameters only:
  - `xgb_max_depth = 3`
  - `num_boost_round = 2`
- `base_rows = 8549`
- `mask_rows = 8549`
- `total_training_rows = 8549`
- `seconds = 11.6`
- `TRAIN_SECONDS = 14.90`
- output model: `model/omega_xgb_final.pkl`

### Backtest

- input contract: PASS
- engine: `file_stream`
- `n_frames = 1055429.0`
- `seconds = 4.7`
- `BACKTEST_SECONDS = 6.80`
- output artifact: `model/local_backtest.json`

Backtest metrics:

- `Topo_SNR = 0.0`
- `Orthogonality = 0.00012346729376811198`
- `Phys_Alignment = 0.0`
- `Model_Alignment = 0.0`
- `Vector_Alignment = 0.0`

Important interpretation:

- this is no longer the previous `all-zero chain` failure mode
- the canonical chain is active upstream and remains consumable downstream
- remaining zero-valued alignment metrics are now a later-layer signal-quality question, not the original Stage2 ordering collapse

## Lessons locked

1. A smoke is invalid if it only proves that code runs; it must prove that the canonical chain is non-degenerate.
2. Fail-fast input gates are useful, but their granularity must match the batching model.
3. Implicit CLI defaults can invalidate smoke conclusions; `forge_base_matrix.py` defaulted to `--years=2023,2024`, so explicit year scoping is mandatory for hot-week validation outside the 2023 baseline.
4. The correct rollback strategy is to preserve both the pre-speed route and the speed route until root cause is known.
5. The Stage2 ordering defect was an integration defect with mathematical consequences.

## Status

This smoke should be treated as the first run that passes both:

- mathematical meaning: canonical V64.3 signal chain activated
- engineering meaning: Stage2 -> forge -> training -> backtest all consume non-degenerate inputs successfully

Next gate: record to fixed memory, then `git commit` and `push` the local remediation tree.
