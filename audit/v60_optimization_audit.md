# v6.0 Optimization Audit: Architecture vs. Implementation Gap

**Date:** 2026-02-17
**Status:** OPEN FOR REVIEW
**Auditor Target:** External AI Consultant / Chief Architect

## 1. The Core Conflict

**Architectural Requirement (`audit/v6.md`):**
> "Executes `physics_auditor.py` swarms to constantly recalibrate `peace_threshold` and `ANCHOR_Y` across changing A-share market regimes."

**Current Implementation (`tools/v60_autopilot.py`):**
- Pipeline Stage 1: `monitor_frame` (Active)
- Pipeline Stage 2: `sync_gcs` (Pending)
- Pipeline Stage 3: `vertex_train` (XGBoost Default Params)
- Pipeline Stage 4: `vertex_backtest` (XGBoost Default Params)
- **MISSING:** Stage 5 Optimization (Hyperparameter Sweep / Physics Calibration)

**The Question:**
Why are we deploying a v6.0 pipeline that violates the "continuous calibration" mandate of the architecture?

## 2. Root Cause Analysis (Engineering Audit)

The decision to skip optimization in the initial v6.0 rollout is **intentional** but driven by a critical **tooling gap**, not architectural negligence.

### Evidence A: Incompatible Legacy Tooling
- **Script:** `tools/run_optuna_sweep.py`
- **Status:** **DEPRECATED / DANGEROUS**
- **Findings:**
  - Hardcodes `model_type="sgd_logistic"` (Line 103).
  - Uses `sklearn.partial_fit` API, incompatible with XGBoost.
  - Optimization objective is "linear separation," which would poison the non-linear XGBoost model with invalid hyperparameters.

### Evidence B: Immutable Trainer
- **Script:** `tools/run_vertex_xgb_train.py`
- **Status:** **NEEDS REFACTOR**
- **Findings:**
  - Hardcodes `L2PipelineConfig()` defaults.
  - Does **not** expose `peace_threshold`, `srl_resid_decay`, or `y_ema_alpha` as CLI arguments.
  - Vertex AI / Vizier cannot inject parameters into the current container.

## 3. Risk Assessment

| Risk Scenario | Probability | Impact | Decision |
| :--- | :--- | :--- | :--- |
| **Inject Legacy Optimization Now** | High | **Catastrophic.** Optimizing XGBoost with SGD logic will yield "garbage" params. | **REJECT** |
| **Wait for Perfect Tooling** | Medium | **High.** Delays first feedback loop on XGBoost memory/runtime behavior. | **REJECT** |
| **Run Baseline (Defaults) -> Optimize** | Low | **Low.** Establishes a performance baseline (`train_metrics.json`) to sizing the future swarm. | **ACCEPT** |

## 4. Execution Plan (The "Stage 5" Protocol)

We will proceed with the current `monitor_frame -> upload -> train` sequence to validate the **infrastructure** (Memory, I/O, Time). Parallel to this, we will prepare the optimization suite.

### Immediate Actions (During Upload Wait Time):
1.  **Refactor Trainer:** Modify `tools/run_vertex_xgb_train.py` to accept CLI overrides for:
    - `--peace_threshold`
    - `--srl_resid_decay`
    - `--y_ema_alpha`
2.  **Develop Swarm Driver:** Create `tools/submit_swarm_xgb.py` (New v6-native Optuna driver).
3.  **Deploy Stage 5:** Once the Baseline Backtest completes, immediately trigger the new Swarm Driver to recalibrate `peace_threshold` for the final production model.

## 5. Auditor Conclusion
The deviation from `audit/v6.md` is a **temporary engineering necessity**. The "Stage 5" approach correctly isolates infrastructure risk from model risk.

**Approved Next Step:** Continue Baseline Run. Begin development of `submit_swarm_xgb.py`.
