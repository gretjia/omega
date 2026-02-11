# OMEGA Constitution: The Mathematical Trinity

> **Supreme Directive**: This document is the Single Source of Truth for all OMEGA Agents (Trae, Antigravity, Gemini, Codex). All code, strategies, and decisions MUST derive from these First Principles. Engineering heuristics (like "T+1") are *constraints*, not *principles*.

## Article I: The Trinity (First Principles)

The Market is a complex system defined by three orthogonal dimensions.

### 1. Geometry (Topological Data Analysis - TDA)
*   **Principle**: The market has "Shape" and "Structure", not just "Trend".
*   **Definition**: We use **Persistent Homology** (Vietoris-Rips filtration) on **Takens' Embedded** Point Clouds to detect topological features (Loops/Holes).
*   **Invariant**: A "Loop" ($H_1$) represents a cycle of energy accumulation (Accumulation) or release (Distribution).
*   **Correction**: TDA is naturally undirected. We MUST use **Signed Area** (Levy Area) or **SRL Residuals** to assign direction (Buy/Sell) to the structure.

### 2. Physics (Square-Root Law - SRL)
*   **Principle**: The "Gravity" of the market is invariant.
*   **Law (Sato 2025)**: The impact exponent $\delta$ is **strictly 0.5**.
    *   **Equation**: $\Delta P \sim \text{Sign}(OFI) \cdot Y \cdot \sqrt{\frac{Q}{D}}$
    *   **Universal Constant**: $\delta = 0.5$ is NOT a parameter to be learned. It is a physical constant.
    *   **Prohibition**: "Race" logic (testing 0.33 vs 0.5 vs 0.66) is pseudoscience and strictly prohibited.
*   **State Variable ($Y$)**: The **Liquidity Coefficient** ($Y$) is the ONLY free degree of freedom. It represents the "Structural Rigidity" of the market.
    *   **The Holographic Damper**: $Y$ is dynamic and scales with Epiplexity. High $\mathcal{E}$ $\rightarrow$ High Rigidity ($Y$ stable). Low $\mathcal{E}$ $\rightarrow$ Fluidity ($Y$ volatile).

### 3. Information (Epiplexity & MDL)
*   **Principle**: Information is "Compression Gain", not just "Complexity".
*   **Definition (Finzi 2026)**:
    *   **Epiplexity ($\mathcal{E}$)**: Structural Information. Measured as **Compression Gain**: $1 - \frac{Var(Residuals_{linear})}{Var(Data_{naive})}$.
        *   Replaces outdated **LZ76** (which confused high-entropy noise with high-complexity structure).
    *   **Entropy ($H$)**: The remaining incompressible noise.
*   **Rule**: We trade ONLY when Compression Gain > 0 (Structure Emerging).
*   **Factorization Order**: Time must be strictly ordered (Volume Clock) to reveal causality. Random sampling destroys Epiplexity.

## Article II: The Methodology (Recursive & Adaptive)

### 1. Recursion
*   **Rule**: There are NO static parameters.
*   **Violation**: Hardcoding `threshold = 0.5` or `window = 20`.
*   **Compliance**: Thresholds are dynamic functions of distribution (e.g., `quantile(0.95)` of rolling history). $\epsilon$ for TDA is adaptive to local density.

### 2. The Volume Clock
*   **Rule**: Physical Time (Wall Clock) is an illusion in finance.
*   **Compliance**: All math MUST operate in **Volume Time** (Volume Bars).
*   **Reason**: SRL is linear in Volume Time; non-linear in Physical Time.

### 3. Boundary Conditions
*   **Rule**: Physics breaks at boundaries (Limit Up/Down).
*   **Compliance**: SRL is undefined at $P \approx Limit$. The Agent must detect `Regime.BOUNDARY` and suspend "Normal Physics" in favor of "Boundary Constraints".

## Article III: The Agent (The Orchestrator)

### 1. Role
*   The Agent is the **Pilot**; the Code is the **Engine**.
*   The Agent DOES NOT just "write code". The Agent **Plans**, **Implements**, and **Verifies**.

### 2. Verification Protocol
*   **Prohibited**: "It runs without error."
*   **Required**: "It adheres to Article I." (e.g., "Does this function conserve mass/volume?" "Is the dimension consistent?")

## Article IV: Settlement & Constraints

### 1. Settlement (T+1)
*   **Status**: A **Constraint**, NOT a Principle.
*   **Logic**: We do not "believe" in T+1; we "obey" it because the Settlement System enforces it.
*   **Implementation**: Strategies must calculate `SettlableVolume`. If `SettlableVolume < TradeVolume`, the trade is **Physically Impossible** (not just "illegal").

### 2. Execution
*   **Status**: Friction.
*   **Logic**: Execution cost is Entropy. Minimizing impact minimizes Entropy.

## Article V: Configuration & Reproducibility

### 1. Immutable Configuration
*   **Principle**: `config.py` is the **Baseline**, Artifacts are **Snapshots**.
*   **Rule**: Training MUST NOT write back to `config.py`.
*   **Reason**: Writing back pollutes the baseline and prevents reproducibility. Each training run yields a unique "Frozen State" (Thresholds + Weights).

### 2. Artifact-Driven Inference
*   **Principle**: Inference (Backtest/Live) relies on the **Frozen Snapshot**, not the Baseline.
*   **Compliance**:
    *   **Training**: Saves `artifacts/omega_policy.pkl`.
    *   **Backtest**: Loads `artifacts/omega_policy.pkl` (using `artifact_loader`).
    *   **Prohibited**: Running backtest using `KernelConfig()` from `config.py` (which lacks trained thresholds).

### 3. Dataset Role Isolation (Train/Val/Test/Backtest)
*   **Principle**: Evaluation is invalid if data roles overlap.
*   **Rule**: Train/Val/Test/Backtest must be **mutually disjoint by construction** (time/group boundaries), not by convention.
*   **Compliance**:
    *   Build role-specific manifests (for example `train_files.txt`, `backtest_files.txt`).
    *   Enforce overlap checks in pipeline runtime; any overlap is a hard failure.
    *   Persist split evidence (filters, distributions, overlap count) in status artifacts.
*   **Prohibited**:
    *   Reusing train manifest as backtest manifest.
    *   Building train/backtest file lists from a single wildcard without role filters.
*   **Override policy**: Any temporary overlap override must be explicit, auditable, and never default-on.

---
*Signed,*
*The OMEGA Architect*
*February 2026*
