# OMEGA v5.2 Final Implementation Plan: The "Solo-Quant Barbell"

**Status:** Active
**Date:** 2026-02-16
**Context:** Local machines (Windows/Linux) are currently executing "Data Alchemy" - brute-forcing raw .7z ticks into Vectorized Parquet Frames.

---

## 1. Current Status: Data Alchemy (Local Heavy Lifting)
*   **Objective:** Transform raw, noisy market data into clean, structure-rich feature frames.
*   **Mechanism:** Utilizing local high-memory workstations (AMD AI Max) to run `omega_core` physics kernels.
*   **Output:** `Zstandard` compressed Parquet files.

---

## 2. The Plan Forward (Execution Sequence)

### Step 2: Cloud Synchronization (The Mac Gateway Strategy)
**Constraint:** Windows/Linux machines are on local LAN only (no VPN/Cloud SDK). Mac is the only uplink.
**Constraint:** Mac disk space is limited (~147GB). Total frames > 113GB.
**Solution:** Implementing a "Batch & Burn" sync mechanism.

*   **Action:**
    1.  Mac fetches a small batch (e.g., 20GB) of completed frames from Windows (`D:/Omega_frames/...`) and Linux (`/omega_pool/...`) via SCP/Rsync.
    2.  Mac uploads the batch to Google Cloud Storage (`gs://omega_v52/`).
    3.  Mac verifies upload success.
    4.  Mac deletes local batch to free space.
    5.  Repeat until sync is complete.
*   **Tool:** `tools/mac_gateway_sync.py` (Default bucket: `gs://omega_v52`).
*   **Target GCS Path:** `gs://omega_v52/omega/v52/frames/host=<hostname>/`

### Step 3: The "God View" Tuning (Vertex AI + Optuna)
*   **Project ID:** `gen-lang-client-0250995579`
*   **Region:** `us-west1`
*   **Action:** Launch the **"Cloud Hyperparameter Bomber"**.
    *   Spin up ephemeral Cloud Batch VMs using `tools/submit_vertex_sweep.py`.
    *   Run **Optuna** to aggressively search the parameter space.
*   **Target Parameters:**
    *   `y_ema_alpha` (Memory decay rate).
    *   `peace_threshold` (Cognitive gate).
*   **Objective Function:** Maximize **`Model_Alignment`** (The OMEGA Cognitive Alignment metric).
*   **Constraint:** `Topo_SNR >= 3.0`.
*   **Goal:** Mathematically lock in the optimal physical constants for v5.2.

### Step 4: Final Training & Weights Extraction
*   **Action:** Train the final `SGDClassifier` using the optimal parameters found in Step 3.
*   **Tool:** `trainer_v52.py` (Cloud execution).
*   **Outputs:**
    1.  `model_v52_final.pkl`: The Python object (for archival/research).
    2.  `weights.json`: The "Disassembled" coefficients (intercept, coef_, scale_, mean_) for the QMT production environment.
*   **Tool:** `tools/extract_weights_json.py` (To be created) - Extracts raw math from the sklearn object.

### Step 5: Full Backtest & Report Generation
*   **Action:** Run a comprehensive local backtest on the AMD machine using the optimized `weights.json` logic (simulating the QMT engine).
*   **Metrics to Harvest:**
    *   **Physics:** `Topo_SNR`, `Orthogonality`, `Epiplexity` distribution.
    *   **Performance:** `Sharpe Ratio`, `Max Drawdown`, `PnL`.
    *   **Cognition:** `Model_Alignment` score.
*   **Final Deliverable:** Compile these into `audit/v52_deep_analysis_report.md` for the final audit review.

---

## 3. Immediate Infrastructure Actions

We have created the following tools to enable the plan:

1.  **`tools/mac_gateway_sync.py`**: [PENDING] A robust script to buffer-sync frames from LAN machines to GCS (Batch & Burn).
2.  **`tools/submit_vertex_sweep.py`**: [COMPLETE] The script to submit `trainer_v52.py` to Vertex AI with Optuna.
3.  **`tools/extract_weights_json.py`**: [COMPLETE] The tool to convert the final `.pkl` into the QMT-compatible JSON format.
