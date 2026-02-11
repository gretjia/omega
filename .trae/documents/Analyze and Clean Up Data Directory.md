# Data Folder Cleanup Plan

Based on the analysis of the `./data` directory (approx. 100GB), here is the breakdown and cleanup strategy.

## Data Inventory & Analysis

| Directory | Size | Type | Usage | Status |
| :--- | :--- | :--- | :--- | :--- |
| `history_ticks` | **35.0 GB** | Raw Data | Primary source of tick data (CSV). | **Keep** (Source of Truth) |
| `binary_ticks` | **30.4 GB** | Binary Cache | Optimized `.npy` files for high-speed backtesting. | **Keep** (Performance Critical) |
| `rq` | **14.9 GB** | External Data | RiceQuant data bundle and ticks. | **Keep** (External Source) |
| `history_ticks_full`| **6.8 GB** | Raw Data | Detailed daily tick files (mostly 2025). | **Keep** (High Fidelity Data) |
| `golden_setups_full`| **3.8 GB** | Training Data | "Golden Sample" datasets for model training. | **Cleanable** (Reproducible) |
| `golden_setups_full_v2`| **3.1 GB** | Training Data | Version 2 of golden samples. | **Cleanable** (Reproducible) |
| `mockrq` | **1.1 GB** | Sim Data | QMT-to-RQ conversion simulation. | **Cleanable** (Redundant) |
| `cache_v2` | **0.9 GB** | Cache | Feature engineering cache. | **Cleanable** (Reproducible) |
| `daily_bars` | **0.2 GB** | Market Data | Daily K-line data. | **Keep** (Small & Useful) |
| `test.csv` / `test.npy`| **~4 MB** | Temp Files | Temporary test artifacts. | **Delete** |

## Proposed Actions

I recommend removing the following **reproducible or temporary** data to free up approximately **9 GB** of space.

1.  **Delete Training Artifacts**:
    *   `d:\OMEGA\data\golden_setups_full`
    *   `d:\OMEGA\data\golden_setups_full_v2`
    *   *Reason*: These are generated from ticks and can be recreated by `omega_data_refinery.py` when needed.

2.  **Delete Simulation Data**:
    *   `d:\OMEGA\data\mockrq`
    *   *Reason*: Intermediate data for QMT/RQ compatibility testing.

3.  **Delete Calculation Cache**:
    *   `d:\OMEGA\data\cache_v2`
    *   *Reason*: Feature cache that will auto-regenerate during the next training session.

4.  **Delete Temporary Files**:
    *   `d:\OMEGA\data\test.csv`
    *   `d:\OMEGA\data\binary_ticks\test.npy`
    *   `d:\OMEGA\data\tiny.csv`
    *   `d:\OMEGA\data\tiny_train.csv`

**Total Space to Recover: ~9 GB**

> **Note on `binary_ticks` (30GB)**: This consumes the most space but is essential for the system's performance. Deleting it would require a time-consuming "rebaking" process (`bake_ticks.py`) before the next backtest. I recommend keeping it unless you are critically low on disk space.

## Execution Steps

1.  Execute delete commands for the folders and files listed above.
