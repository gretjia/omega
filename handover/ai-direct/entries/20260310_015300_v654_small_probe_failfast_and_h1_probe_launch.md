---
entry_id: 20260310_015300_v654_small_probe_failfast_and_h1_probe_launch
task_id: V654-IDENTITY-PRESERVING-PULSE-COMPRESSION
timestamp_local: 2026-03-10 01:53:00 +0000
timestamp_utc: 2026-03-10 01:53:00 +0000
operator: Codex
role: commander
branch: main
git_head: 2ccc9a2
status: in_progress
---

# V654 Small Probe Fail-Fast, H1 Probe Launched

## 1. Small Jan Probe

Runtime root:

- `audit/runtime/v654_probe_linux_20260310_014600`

Observed forge facts:

- `matched L1 files=10`
- `matched L2 files=16`
- `phase 2/4 done rows=85711 total_events=3635714 raw_candidates=529 kept_pulses=238`

Observed problem:

- after horizon trimming under `5/10/20d`, the forged frame became empty
- output meta reported:
  - `rows=0`

Interpretation:

- this was not treated as a valid event-study sample
- it exposed a runtime guard gap:
  - a too-short date window could silently produce an empty campaign matrix

## 2. Fail-Fast Repair

Repair landed on `main`:

- `2ccc9a2` `fix(v654): fail fast on empty horizon-trimmed forge`

Local verification after the repair:

- `python3 -m py_compile` passed
- `uv run --with pytest --with polars --with numpy pytest tests/test_campaign_state_contract.py tests/test_campaign_event_study.py -q`
  - `16 passed in 0.50s`

## 3. H1 Probe Launch

Current runtime root:

- `audit/runtime/v654_probe_linux_h1_2023_20260310_015200`

Launch shape:

- node:
  - `linux1-lx`
- inputs:
  - `/omega_pool/parquet_data/latest_base_l1/host=linux1/20230[1-5]*.parquet`
  - `/omega_pool/parquet_data/stage2_full_20260307_v643fix/l2/host=linux1/20230[1-5]*.parquet`

Latest observed live state:

- active python PID:
  - `3710033`
- latest log lines:
  - `matched L1 files=72 L2 files=98 horizons=[5, 10, 20] pulse_mode=sign_nms pulse_min_gap=30`
  - `phase 1/4 collecting daily spine from L1`

## 4. Current State

- V654 remains active
- ML remains closed
- the small Jan probe is frozen as insufficient-width runtime evidence
- the H1 probe is now the live execution authority for the first real V654 event-study attempt
