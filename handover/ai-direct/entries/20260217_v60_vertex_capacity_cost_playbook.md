# Handover: v60 Vertex Capacity + Cost Playbook
**Date:** 2026-02-17  
**Run Hash:** `aa8abb7`  
**Status:** ACTIVE

## 1) Why This Was Added
Cloud ETA was drifting because requested machine types and real regional capacity/quotas were mismatched.  
Goal: maximize usable compute per dollar without waiting in infinite `PENDING`.

## 2) Verified Capacity Facts (us-west1, this project)
Using `gcloud beta quotas info`:
- `custom_model_training_n2_cpus`: **20**
- `custom_model_training_c2_cpus`: **20**
- `custom_model_training_cpus` (total): **42**

Operational observation:
- `n2-highmem-16` jobs start reliably (with short queue).
- `n1-highmem-*` and tested `c2-standard-16` showed repeated long pending in this environment.

## 3) Enforced Execution Policy
### Machine policy
- Base matrix: `n2-highmem-16`
- Swarm optimize: `n2-highmem-16`
- Train: `n2-standard-16`
- Backtest: `n2-standard-8`

### Submission policy
- Always use `--force-gcloud-fallback`.
- Always use `--sync-timeout-sec=<N>` to prevent indefinite waits.
- Spot only with explicit one-shot on-demand retry.

### Dataset split safety
- Train remains `2023,2024`.
- Backtest is locked with date-prefix guard: `2025,202601` (means full 2025 + 2026 Jan).

## 4) Code Changes Applied
- `tools/submit_vertex_sweep.py`
  - Added `--sync-timeout-sec`.
  - On timeout: cancel custom job and fail fast.
  - Added flush logging for real-time state visibility.
- `tools/v60_autopilot.py`
  - Defaults moved to quota-safe N2 machine types.
  - Added per-stage sync timeout args.
  - Added optional spot with on-demand fallback (base/opt/train/backtest).
  - Added backtest prefix guard pass-through (`--test-year-months`).
  - Added recursive-audit checks for train/test split overlap.
- `tools/run_cloud_backtest.py`
  - Added `--test-ym` prefix filter.
  - File selection changed from head-only to uniform sampling.
  - If initial selection has no valid processed frames, expand scan until first valid frame.
- `tools/ai_incident_watchdog.py`
  - `upload_progress_stalled` now triggers only in upload-related stages.

## 5) Current Runtime
- `autopilot`: `v60_autopilot_aa8abb7` running.
- Current stage: `build_base_matrix` on Vertex (`n2-highmem-16`).
- `watchdog`: `v60_ai_watchdog_aa8abb7` active with auto-resume + codex debug.

## 6) Next-Agent Checklist
1. Check `/Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json`.
2. Confirm current Vertex job state for `omega-v60-run_vertex_base_matrix-*`.
3. If stage timeout occurs, inspect logs and retry with smaller/faster-available machine type.
4. Do not change v6 math logic or physics gates.
