# OMEGA Next-Gen Pipeline Architecture (v50+): Engineering Roadmap

**Date:** 2026-02-11
**Objective:** Transform the OMEGA v40 experimental scripts into a production-grade, versioned, and scalable Quantitative Research Platform (QRP).
**Target Audience:** Core Engineering Team

---

## Phase 1: Configuration as Code (The "Decoupling" Phase)
**Goal:** Eliminate the need to edit `.ps1` or `.py` source code to change run parameters. All logic is controlled via versioned YAML/JSON files.

### 1.1 Hierarchical Configuration System
*   **Technology:** Adopt **Hydra** (Python) for composable configurations.
*   **Structure:**
    ```text
    conf/
    ├── config.yaml             # Main entry point
    ├── hardware/
    │   ├── workstation_32core.yaml  # Your current machine profile
    │   └── server_128core.yaml
    ├── model/
    │   ├── v40_patch02.yaml    # Snapshot of the current winner
    │   └── v41_experimental.yaml
    └── env/
        ├── production.yaml     # Real paths (D:\Omega_stage)
        └── dev.yaml            # Test paths
    ```
*   **Benefit:** Switch between `v40` and `v41` logic just by changing a command-line flag: `--config-name=v41_experimental`.

### 1.2 Data Contracts & Schema Validation
*   **Action:** Define strict **Pydantic** models for all inputs and outputs.
*   **Feature:** Before a run starts, the system validates that `level2_config.json` matches the code's expected schema. No more `KeyError` 5 hours into a run.

---

## Phase 2: Modular Core Abstraction (The "Interface" Phase)
**Goal:** Allow `omega_v3_core` to be upgraded or replaced without breaking the outer Framing/Training loops.

### 2.1 The Core Interface (`IPhysicsKernel`)
*   **Action:** Define an abstract base class that all Math Cores must implement.
    ```python
    class IPhysicsKernel(ABC):
        @abstractmethod
        def apply_recursive_physics(self, df: PolarsDataFrame) -> PolarsDataFrame: ...
        @abstractmethod
        def get_version(self) -> str: ...
    ```
*   **Benefit:** You can test a new `omega_v4_core` side-by-side with `v3` by simply injecting a different class implementation.

### 2.2 Dynamic Class Loading
*   **Feature:** The pipeline loads the kernel based on the config string (e.g., `"kernels.v3.StandardKernel"`).
*   **Result:** Old versions of the code can coexist in the repo. You can reproduce a "v34 run" even years later.

### 2.3 Modular Data Loaders
*   **Separation:** Separate "Physical Storage" (7z/Parquet/S3) from "Logical Data" (Ticks/Snapshots).
*   **Feature:** A `SmartLoader` that automatically handles the "Source -> Staging -> Memory" lifecycle, respecting the hardware profile (e.g., auto-throttling based on Disk Queue depth).

---

## Phase 3: The Robust Execution Engine (The "Runner" Phase)
**Goal:** Replace the fragile PowerShell/Python hybrid scripts with a robust Python State Machine.

### 3.1 Unified State Manager (SQLite/JSONL)
*   **Current Issue:** `_audit_state.jsonl` is simple but brittle.
*   **Upgrade:** Use a persistent **SQLite** database to track the state of every single file (Framed? Trained? Error Count? Retry Count?).
*   **Feature:** "Smart Resume" — The runner queries the DB at startup. If a file failed 3 times, skip it. If it’s pending, queue it.

### 3.2 Hardware-Aware Task Scheduler
*   **Context:** You faced disk bottlenecks.
*   **Feature:** Implement a **Resource Semaphore**.
    *   *Config:* `resources: { io_slots: 4, cpu_slots: 26 }`
    *   *Logic:* A worker must acquire an `io_slot` before reading disk and release it immediately after. This prevents "Disk Thrashing" (Queue > 10) programmatically, ensuring smooth 100% CPU usage.

### 3.3 Checkpoint Manager 2.0
*   **Action:** Standardize checkpoint naming: `model_{version}_epoch_{epoch}_loss_{loss}.pkl`.
*   **Feature:** Automatic "Best K" retention (keep only top 3 checkpoints to save space).

---

## Phase 4: Automated Validation & Analytics (The "Quality" Phase)
**Goal:** Trust the green "Success" message implicitly.

### 4.1 Automated Regression Testing
*   **Action:** Create a "Mini-Universe" dataset (e.g., 1 week of data).
*   **CI Pipeline:** Before any full run, the system runs the *entire* pipeline on the Mini-Universe.
    *   *Check 1:* Does it crash?
    *   *Check 2:* Is PnL > 0? (Sanity check)
    *   *Check 3:* Is `Orthogonality` within spec?

### 4.2 Experiment Tracking (MLflow / TensorBoard)
*   **Action:** Integrate an experiment tracker.
*   **Benefit:** Instead of digging through `train.log`, you open a web dashboard to see a graph of `Loss` vs `Time`, and compare "v40" vs "v41" curves overlayed.

### 4.3 Backtest Scenario Framework
*   **Feature:** Define "Scenarios" in config.
    *   *Scenario A:* "High Volatility" (Filter 2024 data).
    *   *Scenario B:* "Bear Market" (Filter 2022 data).
*   **Result:** The Backtest engine runs all scenarios automatically and generates a comparative report table.

---

## Execution Plan & Deliverables

| Phase | Estimated Effort | Key Deliverable |
| :--- | :--- | :--- |
| **1. Config** | 1 Week | `hydra_config` setup, `configs/` folder structure. |
| **2. Modular** | 2 Weeks | `omega.core.api` package, Refactored `kernel.py`. |
| **3. Runner** | 2 Weeks | `pipeline_manager.py` (replacing `.ps1`), SQLite State DB. |
| **4. Validation** | 1 Week | `tests/integration/` suite, MLflow logging hooks. |

**Immediate Next Step:**
Initialize the **Phase 1** folder structure and port the current `v40` parameters into a `config.yaml` to prove the concept.
