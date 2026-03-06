# OMEGA Core (v5.0)

Global index and cross-module navigation: [`../README.md`](../README.md).

**Code Name:** Holographic Damper
**Role:** Mathematical Kernel

This directory contains the pure mathematical and logic implementation of OMEGA v5.0. It is agnostic to the execution environment (pipeline/runner).

## Key Components

*   **`omega_math_core.py`**: The Physics Engine.
    *   **Universal SRL**: `calc_srl_state` enforces $\delta=0.5$ (Sato 2025).
    *   **Legacy Linear-Probe Compression**: `calc_linear_probe_compression_gain` remains as a historical scalar helper and is not the canonical runtime `epiplexity`.
    *   **Canonical Runtime Compression**: the live Stage 2 path uses `omega_math_rolling.calc_srl_compression_gain_rolling`, defined by the relative SRL compression score between `price_change` and `srl_residuals` under a prequential MDL interpretation with `Delta k = 0`.
*   **`omega_etl.py`**: The Data Factory.
    *   **Causal Projection**: Implements time-weighted volume extrapolation to fix Paradox 3.
    *   **Multi-Slice Support**: Recursively loads list of files and sorts by time to ensure causal integrity.
*   **`kernel.py`**: The Decision Logic.
    *   **Holographic Damper**: Updates $Y$ only in the Brownian baseline regime (`Q_topo < brownian_q_threshold`), while the final signal gate is driven by canonical `epiplexity` plus geometry/spoof filters.
    *   **Single Compression Semantics**: `bits_srl` is forbidden, `srl_resid` is never rewritten by `has_singularity`, and `dominant_probe` is a compatibility placeholder fixed at `1`.
*   **`trainer.py`**: The Learning Machine.
    *   SGD-based incremental learning with Epiplexity weighting.
    *   **Multi-Symbol Support**: Smartly handles mixed-symbol parquet files by using `.over("symbol")` for label generation and skipping redundant physics.

## Usage
Do not import from here directly if possible. Use the `pipeline/adapters` interface.
