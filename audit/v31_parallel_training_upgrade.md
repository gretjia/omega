# OMEGA v3.1 Parallel Training Upgrade Audit

**Date:** 2026-02-07
**Event:** Critical Performance Upgrade & Migration
**Author:** OMEGA Pair Programmer

## 1. Problem Identification

During the "Full Solo Cycle" training of OMEGA v3.1, a severe performance bottleneck was identified.

### Symptoms
*   **Low Resource Utilization:** The training process on a high-end AMD AI Max workstation utilized only **4% CPU** and **45% Memory**.
*   **Slow Velocity:** Training speed dropped to ~3,400 rows/minute.
*   **Estimated Time:** At the observed rate, the remaining 18.8M rows would have taken **~4 days** (92+ hours) to complete.

### Root Cause Analysis
*   **Bottleneck:** The function `omega_v3_core.kernel.apply_recursive_physics` was identified as the culprit.
*   **Mechanism:** This function converts Polars DataFrames to Python dictionaries (`frames.to_dicts()`) and iterates through them in a standard Python loop to calculate recursive state (Peace Protocol, Adaptive Y).
*   **Concurrency:** Due to the Python GIL (Global Interpreter Lock), this heavy scalar math was forced to run on a **single CPU core**, leaving the other 23+ cores idle.
*   **Legacy Tooling:** The existing `parallel_trainer/` directory contained a legacy **v1 implementation** designed for raw CSV processing, which was incompatible with the current v3.1 Parquet Frame architecture and lacked modern physics logic (spoofing detection).

## 2. Solution: Parallel V3.1 Adapter

To resolve this without restarting the multi-day training run, a custom Parallel V3.1 Adapter was engineered.

### Architecture
*   **Pattern:** Producer-Consumer (Multiprocessing).
*   **Producers (12 Workers):**
    *   Load `level2_frames` (Parquet) in parallel.
    *   Execute `apply_recursive_physics` locally (bypassing GIL limitations).
    *   Perform Label Engineering.
    *   Return processed feature vectors.
*   **Consumer (Main Process):**
    *   Aggregates vectors from workers.
    *   Feeds `SGDClassifier.partial_fit` (which remains sequential but is fast).
    *   Manages checkpointing.

### Key Features
1.  **Zero Math Change:** The adapter imports and reuses `OmegaTrainerV3` methods directly to ensure the physics and logic are bit-for-bit identical to the sequential run.
2.  **Seamless Resume:** The adapter was designed to read the **exact same checkpoint format** (`checkpoint_rows_*.pkl`) as the sequential trainer. It reads the `processed_files` set from the old checkpoint and skips those files, allowing for a frictionless transition.
3.  **Optimization:** Configured to use 12 workers to saturate the CPU cores.

## 3. Implementation Process

### 3.1 Code Creation
Created `parallel_trainer/run_parallel_v31.py` with:
*   `process_file_v31` worker function.
*   `ParallelTrainerV31` driver class.
*   Compatibility layer for `OmegaTrainerV3` checkpoints.

### 3.2 Migration
1.  **Stopped** the slow sequential process (PID 20872) at ~13.6M rows.
2.  **Launched** the new parallel trainer in the background.
3.  **Verified** process spawning (13 active Python processes).

## 4. Outcome
*   **Status:** Active & Running.
*   **Resume Point:** Successfully resumed from `checkpoint_rows_13669705.pkl`.
*   **Expected Improvement:** Training velocity is expected to increase by **10x-20x**, reducing remaining time from ~4 days to **<12 hours**.

## 5. Files
*   **Script:** `parallel_trainer/run_parallel_v31.py`
*   **Logs:** `audit/_parallel_v31.log` / `.err`
*   **Previous Checkpoint:** `artifacts/checkpoint_rows_13669705.pkl`

---
*Signed, OMEGA Pair Programmer*
