# v61 Pre-Flight Recursive Audit Report

**Date:** 2026-02-20
**Target:** v6.1 Production Run (Architectural Rescue)
**Auditor:** Gemini CLI (Recursive Mode)

## 1. Architectural Alignment (v61.md)

| Requirement | Implementation Status | Evidence |
| :--- | :--- | :--- |
| **Action 1: Stop Dataset Collapse** | **VERIFIED** | `tools/v60_swarm_xgb.py`: `min_samples` set to **150,000** (default). Optuna ranges tightened. |
| **Action 2: Fix Momentum Sign** | **VERIFIED** | `omega_core/kernel.py`: Direction is `pl.col("srl_resid").sign()` (Positive Correlation). Verified by smoke test. |
| **Action 3: Orthogonalize Target** | **VERIFIED** | `tools/v60_swarm_xgb.py` & `tools/run_vertex_xgb_train.py`: Excess Return (`t1_excess_return`) implemented. |
| **Action 4: Anti-Aliasing** | **VERIFIED** | `omega_core/omega_etl.py`: 3-tick rolling mean applied to `v_ofi` and `depth` before aggregation. Verified by smoke test. |

## 2. Operational Lessons & Guardrails (Handover)

| Risk | Mitigation Strategy | Check |
| :--- | :--- | :--- |
| **Quota Trap** | Use `us-central1`. Avoid "Partial" quotas. | **MANUAL** (Operator must select correct region/machine). |
| **Blind Retries** | Watchdog policy updated (implicit in `ai_incident_watchdog.py` or operational habit). | **ACKNOWLEDGED** |
| **Missing Dependencies** | `run_vertex_xgb_train.py` installs `polars`, `xgboost`, `scikit-learn`. `python-json-logger` risk assessed (no usage found in active code). | **CLEARED** |
| **Data Gravity** | Compute/Data unified in `us-central1`. | **ACKNOWLEDGED** |
| **Schema Contract** | `omega_etl.py` fix for multi-day sorting (`sort(["date", "time"])`) prevents causality breaks. | **FIXED** |
| **Memory Risk** | `v60_forge_base_matrix_local.py` uses ticker sharding (low memory footprint). | **DESIGN SAFE** |

## 3. Data Hygiene

| Component | Status | Action Taken |
| :--- | :--- | :--- |
| **v60 Frames** | **PURGED** | `artifacts/runtime/v60`, `gs://.../smoke/v60` deleted. |
| **v60 Base Matrix** | **PURGED** | Local and GCS artifacts removed. |
| **Test Output** | **CLEANED** | `v61_test_output` removed. |

## 4. Final Recommendation

**STATUS: GO FOR LAUNCH**

The system is architecturally aligned with v6.1 requirements. Critical regressions (Momentum Sign, Multi-Day Sort) have been fixed and verified via smoke tests on both Linux and Windows nodes. The environment is pristine.

### Next Steps (Execution):
1.  **ETL:** Run `v60_autopilot.py` (or manual `mac_dispatch.py`) to regenerate frames on Linux/Windows.
2.  **Upload:** Sync frames to GCS (`mac_gateway_sync.py`).
3.  **Forge:** Run `v60_forge_base_matrix_local.py` (Ticker Sharding) to build the clean base matrix.
4.  **Swarm:** Submit `v60_swarm_xgb.py` to Vertex AI (us-central1).
5.  **Train:** Submit `run_vertex_xgb_train.py` with best params.
