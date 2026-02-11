# OMEGA v3.1 Training Prep — Data Qualification (2026-02-05)

## Scope
- Read: `audit/20260205_handover.md`, `audit/v3_training_preparation_plan.md`
- Checked datasets:
  - Frames 2023: `d:\Omega_vNext\data\level2_frames_win2023`
  - Frames 2024: `d:\Omega_vNext\data\level2_frames_mac2024`
  - Raw archives: `d:\Omega_vNext\data\level2\2023\**\*.7z`, `d:\Omega_vNext\data\level2\2024\**\*.7z`

## Executive Result
- **v3.0 training with current frames: PASS (basic qualification).**
- **v3.1 training with current frames: FAIL (missing required fields).**

## Key Findings
1. **Path clarification**
   - User-mentioned `d:\data\level2_frames_win2023` not found; actual path is `d:\Omega_vNext\data\level2_frames_win2023`.

2. **Raw archive coverage is consistent**
   - 2023: **242** `.7z` archives (20230103–20231229)
   - 2024: **242** `.7z` archives (20240102–20241231)
   - Coverage suggests same vendor & full trading-day set.

3. **Frames file coverage**
   - 2023 frames: **1,231,592** parquet files; filename dates 20230103–20231229
   - 2024 frames: **1,275,770** parquet files; filename dates 20240102–20241231

4. **Schema parity (2023 vs 2024)**
   - Both years share **exact same 22 columns** (Polars-generated parquet):
     `bucket_id, open, close, sigma, net_ofi, depth, trace, ofi_list, time_start, time_end, date, n_ticks, maintain_order, bar_duration_ms, price_change, sigma_eff, depth_eff, srl_resid, epiplexity, topo_area, is_signal, direction`

5. **v3.1 required fields are missing in BOTH years**
   - Missing: `trade_vol`, `cancel_vol`, `spoof_ratio`, `lob_flux`
   - Therefore, **current frames are not v3.1‑ready**.

6. **Sample stats (80 files per year; ~1.5k rows each)**
   - No nulls in key numeric columns; `bar_duration_ms` and `n_ticks` positive.
   - `is_signal` is sparse (~1–3% True), `direction` distributed among -1/0/+1.
   - `topo_area / price_change / srl_resid` show heavy tails (expected for L2).
   - `epiplexity` includes negative values → implies normalized/centered metric; verify any non‑negative assumption in training.

## Implications
- The reported 2024 vs 2023 differences in `trade_vol/cancel_vol/spoof_ratio` **cannot be verified** inside current frames because these columns **do not exist** in the produced parquet outputs.
- If v3.1 features are required, frames must be **re‑generated** or those fields **recomputed** during training.

## Recommendation (Choose One)
1. **Full scan report** over all parquet files (missing rate, distribution, anomalies).
2. **Rebuild frames** for 2023/2024 with v3.1 fields (`trade_vol/cancel_vol/spoof_ratio/lob_flux`).
3. **Raw data spot‑check** by unpacking a small sample of `.7z` to verify vendor consistency.
