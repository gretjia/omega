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
1.  User runs `python pipeline_runner.py`.
2.  `ConfigLoader` reads `configs/hardware/active_profile.yaml`.
3.  `Framer` (or Trainer) is instantiated with the Hardware Profile.
4.  The Engine calls `adapter.process_frame()` to delegate math to `omega_core`.
