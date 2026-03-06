# Entry ID: 20260306_134038_v643_backtest_stall_triage

## Summary

- Mission context: `V64.3 Bourbaki Completion` isolated smoke on `linux1-lx`
- Smoke workspace: `/home/zepher/work/Omega_vNext_v643_smoke`
- Result:
  - `Stage 2`: PASS
  - `Stage 3 / forge`: PASS
  - `base_matrix merge`: PASS
  - `training`: PASS
  - `local backtest`: BLOCKED by runtime stall

## What changed before the stall diagnosis

- The smoke workspace was updated to the current single-entry config path:
  - `config.py`
  - `tools/forge_base_matrix.py`
  - `tools/run_vertex_xgb_train.py`
  - `tools/run_local_backtest.py`
  - `omega_core/omega_etl_ashare.py`
- Legacy top-level config entry files were removed from the remote smoke tree:
  - `ashare_config.py`
  - `config_v6.py`

## Completed smoke evidence

### Stage 2

- Logs:
  - `audit/runtime/smoke_v64_contig_stage2.log`
  - `audit/runtime/smoke_v64_contig_dates_stage2.log`
- Both runs completed with:
  - `DONE_NOW=5`
  - `FAILED_TOTAL=0`
  - `RUN_FAILED=0`

### Stage 3 / forge

- Existing shard forge output under:
  - `.tmp/smoke_v64_v643/base_matrix_shards`
- Merge-only closure command succeeded:
  - output parquet: `.tmp/smoke_v64_v643/base_matrix.parquet`
  - output meta: `.tmp/smoke_v64_v643/base_matrix.parquet.meta.json`
- Merge result:
  - `merged_rows = 7434`
  - `merged_files = 109`

### Training

- Command path:
  - `tools/run_vertex_xgb_train.py`
- Output files:
  - `.tmp/smoke_v64_v643/model/omega_xgb_final.pkl`
  - `.tmp/smoke_v64_v643/model/train_metrics.json`
- Training metrics summary:
  - `status = completed`
  - `base_rows = 7434`
  - `mask_rows = 7434`
  - `total_training_rows = 7434`
  - `seconds = 10.98`

## Backtest stall diagnosis

### Invocation

- Script:
  - `tools/run_local_backtest.py`
- Args:
  - `--model-path .tmp/smoke_v64_v643/model/omega_xgb_final.pkl`
  - `--frames-dir .tmp/smoke_v64_v643/l2`
  - `--years 2023`
  - `--output .tmp/smoke_v64_v643/model/local_backtest.json`
  - `--workers 2`
  - `--symbols-per-batch 50`

### Input scale

- L2 input files: `5`
- Approx total L2 size: `184 MB`
- Per-file rows:
  - `20230320_fbd5c8b.parquet`: `210123`
  - `20230321_fbd5c8b.parquet`: `247266`
  - `20230322_fbd5c8b.parquet`: `226390`
  - `20230323_fbd5c8b.parquet`: `240851`
  - `20230324_fbd5c8b.parquet`: `230617`
- Unique symbols discovered by backtest:
  - `5409`
- Batch count:
  - `109`

### Runtime evidence of stall

- Backtest log never advanced past:
  - `[*] Scanning 5 files for symbols...`
  - `[*] Found 5409 unique symbols.`
  - `[*] Created 109 batches for 5409 symbols.`
  - `[*] Starting Backtest on 2 workers...`
- No `local_backtest.json` was produced.
- Process inspection showed:
  - one parent Python process
  - two worker Python processes
  - all parked in `futex_do_wait`
- A 15-second delta sample on `/proc/<pid>/io` and `/proc/<pid>/status` showed:
  - `drchar = 0`
  - `dread_bytes = 0`
  - `dwchar = 0`
  - `dvctx = 0`
  - `dnvctx = 0`
- Interpretation:
  - the backtest path is not merely slow
  - it entered a no-progress runtime stall
  - this matches the known risk profile of the old Python `multiprocessing by symbol` design

## Stop state

- Owner approved stopping the stalled backtest.
- Final verification after stop:
  - no active `tools/run_local_backtest.py` process remained on `linux1-lx`
- Smoke status after stop:
  - `Stage 2`: preserved as PASS evidence
  - `forge/base_matrix`: preserved as PASS evidence
  - `training`: preserved as PASS evidence
  - `backtest`: unresolved blocker

## Next mission

- New active scope: `V64.3 Backtest Stall Remediation and Smoke Completion`
- Required discipline:
  - do not relaunch full `Stage 2`
  - do not rerun shard forge unless the backtest fix proves the current `base_matrix` contract is invalid
  - reuse the existing smoke artifacts
  - replace or remediate the stalled backtest implementation path
