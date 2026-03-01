# OMEGA v5.2 "Epistemic" Upgrade & Implementation Plan

**Version:** 5.2 (The Epistemic Release)
**Target Architecture:** Hybrid (Local Linux "Alchemy" Station + Google Vertex AI "Brain" + Windows QMT "Edge")
**Date:** 2026-02-14
**Status:** Ready for Execution

---

## 1. Executive Summary

This plan outlines the upgrade from v5.1 to **v5.2**. The core objective is to transition from a "Physics-Only" paradigm to a **"Physics-Guided Epistemic"** paradigm.
*   **Math Upgrade:** Switch from `Vector Alignment` (Physics) to `Model Alignment` (Intelligence) as the DoD metric.
*   **Code Upgrade:** Replace memory-heavy `to_dicts()` loops with vectorized NumPy arrays in `kernel.py` to eliminate MemoryErrors.
*   **Infra Upgrade:** Establish a "Barbell" architecture using a local high-performance Linux station for heavy ETL and Google Vertex AI for massive parallel training/tuning.

---

## 2. Phase 1: Local Code Refactoring (The "Epistemic" Patch)
**Goal:** Fix the memory leak and align the math.

*   **Step 1.1: Vectorize Kernel (`omega_core/kernel.py`)**
    *   **Action:** Rewrite `_apply_recursive_physics` to use `numpy` arrays for column-based processing instead of row-based dict iteration.
    *   **Result:** Memory usage drops from ~50GB to ~500MB per file. Speed increases 100x.
*   **Step 1.2: Dual-Track Auditor (`omega_core/physics_auditor.py`)**
    *   **Action:** Implement `Phys_Alignment` (Baseline) and `Model_Alignment` (Target).
    *   **Result:** DoD pass criteria shifts to `Model_Alignment > 0.6`.
*   **Step 1.3: Epistemic Trainer (`omega_core/trainer_v52.py`)**
    *   **Action:** Inject `epi_x_srl_resid` interaction terms.
    *   **Action:** Enforce `Model_Alignment` monitoring during training.

---

## 3. Phase 2: Local Linux "Alchemy" Station Setup
**Goal:** Prepare the local machine (AMD AI Max 395 #1) to crunch 20TB of data.

### 3.1 OS & Environment
*   **Distribution:** **Ubuntu 24.04 LTS (Noble Numbat)** or **Debian 12 (Bookworm)**.
    *   *Why?* Most stable kernels for high-memory workloads and native ZFS support.
*   **Filesystem:** **ZFS (with LZ4 compression)**.
    *   *Why?* The CSV/Parquet data is highly compressible. ZFS LZ4 provides transparent compression, saving ~30-50% disk space and increasing effective I/O throughput.
    *   *Setup:* `sudo zpool create -f -O compression=lz4 omega_pool /dev/nvme0n1`
*   **Python Environment:**
    *   **Version:** Python 3.11 (Sweet spot for performance/compatibility).
    *   **Manager:** `uv` (An extremely fast Rust-based Python package manager, replaces pip/poetry).
    *   **Core Libs:** `polars` (Rust-based DF), `numpy`, `py7zr`, `google-cloud-storage`.

### 3.2 The ETL "Forge" Script
*   **Task:** Develop `etl_forge.py`.
*   **Logic:** 
    1.  Stream-read `.7z` archives using `py7zr`.
    2.  Parse CSV chunks into `Polars` DataFrames.
    3.  Compute OMEGA v5.2 Features (Kernel) immediately in memory.
    4.  Write to `Zstandard` compressed Parquet.
    5.  Upload to GCS Bucket (`gs://omega-data-lake`).
    6.  **Delete** local temp files immediately.

---

## 4. Phase 3: Cloud Infrastructure (Google Vertex AI)
**Goal:** Establish the "Cloud Brain" for massive search.

### 4.1 Data Lake (GCS)
*   **Bucket:** `gs://omega-data-lake`
*   **Structure:**
    *   `/raw`: (Empty - we don't store raw data here)
    *   `/features`: Parquet files partitioned by Date/Symbol.
    *   `/artifacts`: Trained models (`.pkl`) and configs.

### 4.2 Compute (Vertex AI)
*   **Mechanism:** `CustomJob` via `aiplatform` SDK.
*   **Machine Type:** `c2-standard-60` (Compute Optimized, 60 vCPUs) for Training.
*   **Tuning:** `Optuna` running on a standard node, spawning ephemeral Training Jobs.

---

## 5. Phase 4: Execution & Tuning
**Goal:** Find the "God Parameters".

*   **Step 4.1: The Upload:** Run `etl_forge.py` on the Linux station. Watch the 20TB raw data transform into a clean ~500GB Parquet Lake on GCS.
*   **Step 4.2: The Sweep:** Run `submit_vertex_sweep.py` (Optuna) from your Mac/Control Tower.
    *   **Objective:** Maximize `Model_Alignment`.
    *   **Constraints:** `Topo_SNR > 3.0`.
    *   **Parameters:** `y_ema_alpha`, `peace_threshold`, `sigma_gate`.
*   **Step 4.3: The Selection:** Download the best `omega_v5_model_final.pkl` and `production_config.json` to the Windows machine.

---

## 6. Phase 5: Edge Deployment (Windows QMT)
**Goal:** Microsecond execution.

*   **Step 6.1: The Decoupling:** Run `extract_weights.py` to strip the `SGDClassifier` into a pure JSON/Numpy weight file (`weights.json`).
*   **Step 6.2: The QMT Strategy:**
    *   **Init:** Load `weights.json` into memory. Pre-allocate `deque` buffers.
    *   **On_Tick:** 
        1.  Update `trace` buffer.
        2.  Compute `srl_resid`, `epiplexity` (Vectorized, N=1000).
        3.  Compute Interaction Term: `Epi * Resid`.
        4.  Dot Product: `w · x + b`.
        5.  Sigmoid: `1 / (1 + exp(-x))`.
    *   **Trade:** If `Prob > 0.65` -> `passorder`.

---

## 7. Timeline & Checklist

| Phase | Task | Estimated Time |
| :--- | :--- | :--- |
| **P1** | Code Refactoring (Kernel/Auditor) | 2 Hours |
| **P2** | Linux Station Setup (OS/ZFS/Env) | 4 Hours |
| **P3** | ETL Script Dev & Dry Run | 2 Hours |
| **P4** | **Data Migration (The Heavy Lift)** | **24-48 Hours** (Background) |
| **P5** | Cloud Tuning (Vertex + Optuna) | 4 Hours |
| **P6** | QMT Deployment & Paper Trading | 1 Day |

---

## 8. Appendix: Local Linux Setup Details

**Recommended Hardware Config (AMD AI Max 395):**
*   **RAM:** 128GB (Crucial for Polars chunking).
*   **Storage:** 2TB+ NVMe SSD (Gen4/5).
*   **Network:** 2.5GbE/10GbE (if available) for GCS upload.

**Installation Commands (Ubuntu/Debian):**
```bash
# 1. System Updates & ZFS
sudo apt update && sudo apt upgrade -y
sudo apt install -y zfsutils-linux build-essential curl git htop nvtop

# 2. Python (via uv)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
uv python install 3.11
uv venv omega_env
source omega_env/bin/activate

# 3. Core Libraries
uv pip install polars numpy py7zr google-cloud-storage google-cloud-aiplatform optuna tqdm scikit-learn

# 4. GCloud CLI (for auth)
sudo apt-get install apt-transport-https ca-certificates gnupg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt-get update && sudo apt-get install google-cloud-cli
gcloud auth application-default login
```
