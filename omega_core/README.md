# OMEGA Core (v5.0)

**Code Name:** Holographic Damper
**Role:** Mathematical Kernel

This directory contains the pure mathematical and logic implementation of OMEGA v5.0. It is agnostic to the execution environment (pipeline/runner).

## Key Components

*   **`omega_math_core.py`**: The Physics Engine.
    *   **Universal SRL**: `calc_srl_state` enforces $\delta=0.5$ (Sato 2025).
    *   **Compression Gain**: `calc_epiplexity` uses linear model R-squared (Finzi 2026).
*   **`omega_etl.py`**: The Data Factory.
    *   **Causal Projection**: Implements time-weighted volume extrapolation to fix Paradox 3.
    *   **Multi-Slice Support**: Recursively loads list of files and sorts by time to ensure causal integrity.
*   **`kernel.py`**: The Decision Logic.
    *   **Holographic Damper**: Gating $Y$ updates based on Epiplexity.
*   **`trainer.py`**: The Learning Machine.
    *   SGD-based incremental learning with Epiplexity weighting.
    *   **Multi-Symbol Support**: Smartly handles mixed-symbol parquet files by using `.over("symbol")` for label generation and skipping redundant physics.

## Usage
Do not import from here directly if possible. Use the `pipeline/adapters` interface.
