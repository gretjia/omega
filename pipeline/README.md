# OMEGA Pipeline Engine

**Role:** Orchestration & Execution

This package manages the "How" of running OMEGA, while `omega_core` manages the "What".

## Architecture

*   **`config/`**: Configuration schemas (HardwareProfile, ModelConfig).
*   **`interfaces/`**: Abstract Base Classes defining the contract for any Math Core.
*   **`adapters/`**: Glue code. `OmegaCoreAdapter` allows the `omega_core` to function within this modern pipeline.
*   **`engine/`**: The heavy lifting (Framer, Trainer, Backtester logic).
    *   **`framer.py`**: A highly parallelized (ProcessPoolExecutor), map-reduce style ETL engine. It solves the "Slice Paradox" by grouping files by symbol before processing.

## Workflow
1.  `pipeline_runner.py` and `pipeline/engine/framer.py` are archived legacy (v50/v52) and blocked.
2.  Active framing path is v62 two-stage scripts under `tools/`:
    - `tools/stage1_linux_base_etl.py` / `tools/stage1_windows_base_etl.py`
    - `tools/stage2_physics_compute.py`
3.  Archived legacy sources are preserved at:
    - `archive/legacy_v50/pipeline_runner_v50.py`
    - `archive/legacy_v50/pipeline_engine_framer_v52.py`
