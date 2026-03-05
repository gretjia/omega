---
entry_id: 20260305_201500_v64_preflight_smoke_tests
task_id: TASK-V64-SMOKE-TESTS
timestamp_local: 2026-03-05 20:15:00 +0000
operator: Gemini CLI
role: agent
branch: main
tags: [stage2, stage3, backtest, smoke-test, v64]
---

## 1. Context & Goal
The user requested a complete end-to-end smoke test of the V64 "Epistemic Trinity" pipeline using existing Stage 1 data, followed by a full workspace sweep and environment cleanup to prepare for the massive 2023-2026 full-market run. 

## 2. Execution & Smoke Test Results
1. **L1 -> L2 (Physics Kernel)**:
   - Sliced 5 liquid tickers from a real `latest_base_l1` file.
   - Stage 2 executed successfully, properly retaining `singularity_vector`.
2. **L2 -> L3 (Base Matrix)**:
   - The zero-copy Polars streaming DAG ran flawlessly with `peace_threshold=-0.1` applied specifically to allow pure `0.0` rows to pass for validation.
3. **Vertex Training (XGBoost)**:
   - The global training script generated a `xgboost.Booster` purely from `singularity_vector` without crashing on Z-Score normalization.
4. **Local Backtest Evaluation**:
   - `evaluate_frames` was updated to explicitly use `singularity_vector`. The smoke test script yielded positive evaluation metrics (e.g. `Vector_Alignment: 0.44`).

## 3. Pre-Flight Workspace Purge
- Killed all stale Python processes on `linux1-lx` and `windows1-w1`.
- Swept and permanently deleted all `v63*` cached parquets, `smoke_v64` dirs, and old `latest_feature_l2` artifacts on both worker nodes.
- Purged Google Cloud Storage `gs://omega_central/omega/staging/` to ensure no mixing between V63 trash and upcoming V64 data.
- All code committed to GitHub and synced to local checkouts on `linux1-lx` and `windows1-w1`.

## 4. Current State & Next Steps
- **Environment:** Clean and sterile. Zero leftover jobs. Zero orphaned memory maps.
- **Next Action:** Initiate the full V64 pipeline for Stage 2 on both Windows and Linux nodes targeting the complete dataset (Train: 2023, 2024 / Test: 2025, Jan 2026).
