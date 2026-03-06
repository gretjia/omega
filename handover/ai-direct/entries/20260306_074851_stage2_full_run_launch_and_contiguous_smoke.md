# Entry ID: 20260306_074851_stage2_full_run_launch_and_contiguous_smoke

## Summary

- Synchronized `omega-vm`, `mac`, `linux1-lx`, and `windows1-w1` to commit `52c3b62`.
- Verified both workers now hold the same full Stage 1 corpus locally: `743` files total (`552` from original Linux shard + `191` from original Windows shard).
- Re-ran smoke at the **real Stage 2 production entrypoint** (`tools/stage2_targeted_resume.py`), not just `stage2_physics_compute.py`.
- Added a **strict contiguous-day smoke** to cover the previously observed failure mode where isolated-day smoke passed but downstream later failed because a step implicitly depended on preceding days / warm-up context.
- Launched the full Stage 2 run with a simple contiguous-half split that preserves date continuity inside each worker's assignment and keeps later manual takeover easy.

## Why the split changed

The first instinct was an odd/even or interleaved split. That was rejected after re-checking two constraints:

1. The Owner explicitly allowed a simple average split if runtime evidence was ambiguous.
2. There is historical risk that some success criteria only show up when a step sees a contiguous temporal block rather than isolated days.

The chosen split is therefore:

- `linux1-lx`: first contiguous half, `371` files
- `windows1-w1`: second contiguous half, `372` files

This is intentionally conservative. It avoids inventing automatic steal-over logic mid-run. If one machine finishes much earlier, the remaining half can be manually reassigned from the other machine's unfinished tail.

## Sync and readiness facts

- Local/controller commit: `52c3b62`
- `mac`: synced to `52c3b62`
- `linux1-lx`: synced to `52c3b62`
- `windows1-w1`: synced to `52c3b62`
- Both workers have:
  - `host=linux1`: `552` Stage 1 parquet files
  - `host=windows1`: `191` Stage 1 parquet files

## Smoke validation performed

### 1. Existing end-to-end smoke

Linux previously passed the repo-alignment smoke covering:

- Stage 2
- Stage 3
- base matrix
- training
- backtest

This validated the code path after the Bourbaki Closure alignment and the subsequent entrypoint/backtest fixes.

### 2. Production-wrapper smoke

Because the full run uses `tools/stage2_targeted_resume.py`, not only `tools/stage2_physics_compute.py`, a wrapper-level smoke was required.

### 3. Contiguous-day smoke

A strict contiguous 5-day block was built from real Stage 1 files:

- `20230103_fbd5c8b.parquet`
- `20230104_fbd5c8b.parquet`
- `20230105_fbd5c8b.parquet`
- `20230106_b07c2229.parquet`
- `20230109_b07c2229.parquet`

For those files, the smoke pipeline passed:

- `Stage 2` via `tools/stage2_targeted_resume.py`
- `Stage 3` via `tools/forge_base_matrix.py`
- local training via `tools/run_vertex_xgb_train.py`
- local backtest via `tools/run_local_backtest.py`

Schema gates passed:

- L2 required columns present:
  - `singularity_vector`
  - `topo_micro`
  - `topo_classic`
  - `topo_trend`
  - `epiplexity`
  - `srl_resid`
  - `topo_area`
  - `topo_energy`
  - `is_energy_active`
  - `spoof_ratio`
- Base matrix required columns present:
  - `singularity_vector`
  - `epiplexity`
  - `srl_resid`
  - `sigma_eff`
  - `topo_area`
  - `topo_energy`
  - `is_energy_active`
  - `spoof_ratio`
  - `t1_fwd_return`

### 4. Windows Stage 2 probe

Windows passed a direct `tools/stage2_targeted_resume.py --max-files 1` probe on:

- `20240717_b07c2229.parquet`

Probe result:

- `__BATCH_OK__`
- completed in `96.0s`
- confirmed the Windows Numba/fallback overrides are effective in the current code state

## Full Stage 2 launch

### Linux

- Runner: `tools/stage2_targeted_resume.py`
- Placement: `heavy-workload.slice`
- Input dir: `/omega_pool/parquet_data/stage2_full_20260306/input_linux1`
- Output dir: `/omega_pool/parquet_data/stage2_full_20260306/l2/host=linux1`
- Log: `audit/runtime/stage2_full_20260306/linux_stage2.log`
- Split:
  - first file: `20230103_fbd5c8b.parquet`
  - last file: `20240716_fbd5c8b.parquet`
  - count: `371`

Observed early runtime:

- first file `20230103_fbd5c8b.parquet`
- input size `2379.25MB`
- completed in `420.6s`
- `__BATCH_OK__` confirmed

### Windows

- Runner: `tools/stage2_targeted_resume.py`
- Input dir: `D:\\Omega_frames\\stage2_full_20260306\\input_windows1`
- Output dir: `D:\\Omega_frames\\stage2_full_20260306\\l2\\host=windows1`
- Log: `audit/runtime/stage2_full_20260306/windows_stage2.log`
- Environment overrides:
  - `OMEGA_STAGE2_FORCE_SCAN_FALLBACK=0`
  - `OMEGA_DISABLE_NUMBA=0`
  - `OMEGA_STAGE2_ISOLATE_SYMBOL_BATCH=0`
- Split:
  - first file: `20240717_b07c2229.parquet`
  - last file: `20260130_fbd5c8b.parquet`
  - count: `372`

At full-run start, the first file had already been completed by the successful Windows probe, so the live run began with `PENDING_TOTAL=371`.

## Operational rules for the next agent

1. Monitor only the run-specific logs:
   - `audit/runtime/stage2_full_20260306/linux_stage2.log`
   - `audit/runtime/stage2_full_20260306/windows_stage2.log`
2. Do not mix these outputs into `latest_feature_l2` mid-run.
3. Do not start Stage 3 until:
   - Linux half is done
   - Windows half is done
   - Windows L2 has been copied/shadowed back to Linux
4. If one worker finishes much earlier, the Owner approved a manual reassignment of the unfinished tail from the other machine.
5. Do not add automatic work stealing or repartition logic while this run is active.
