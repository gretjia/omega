# OMEGA v5.1 Core Math Manual
**Version:** 5.1 (Sato-Finzi Hybrid)  
**Date:** 2026-02-14  
**Status:** Production (Windows/Mac Hybrid)

This manual documents the exact mathematical logic, algorithms, and data structures used in the OMEGA v5.1 Trading Engine. It is generated from a forensic analysis of the `omega_core` codebase (`kernel.py`, `omega_math_core.py`, `trainer_v51.py`, `physics_auditor.py`).

---

## 1. Core Math Concepts

OMEGA v5.1 is based on the **"Holographic Damper"** hypothesis, which synthesizes two theoretical frameworks:
1.  **Universal Square Root Law (SRL):** Market impact is a fixed physical law with $\delta=0.5$. Violations of this law create a restorative force (Residual).
2.  **Epiplexity (Compression Gain):** Markets oscillate between "Noise" (High Entropy) and "Structure" (Low Entropy). Physics is only valid during structured regimes.

### 1.1. Epiplexity (Structural Information)
*Source: `omega_math_core.py` (Finzi et al., 2026)*

Epiplexity measures the **Compression Gain** ($G$) of the price signal. It quantifies how much better a linear predictor is compared to a null (mean) predictor.

$$
G = 1 - \frac{	ext{Var}(R)}{	ext{Var}(X)}
$$

Where:
*   $X$: The price trace (time series sequence).
*   $	ext{Var}(X)$: Total Variance (Entropy of the Null Model).
*   $R$: Residuals from a linear fit ($y = mx + c$) to the trace.
*   $	ext{Var}(R)$: Unexplained Variance (Entropy of the Linear Model).

**Interpretation:**
*   $G \approx 0$: Pure Noise (Random Walk). The linear model explains nothing.
*   $G \approx 1$: Perfect Structure (Line). The linear model explains everything.
*   **v5.1 Logic:** Physics is only applied when $G > 	ext{Threshold}$ (e.g., 0.5).

### 1.2. Universal Square Root Law (SRL)
*Source: `omega_math_core.py` (Sato & Kanazawa, 2025)*

Price change ($\Delta P$) is modeled as a function of Order Flow Imbalance (OFI) and Liquidity (Depth), scaled by Volatility ($\sigma$).

$$
	ext{Impact}_{	ext{theoretical}} = Y \cdot \sigma \cdot 	ext{sgn}(	ext{OFI}) \cdot \sqrt{\frac{|	ext{OFI}|}{D_{	ext{eff}}}}
$$

Where:
*   $Y$: The "Yield" coefficient (Structural Rigidity/Elasticity). Adaptive state.
*   $\sigma$: Volatility (Standard Deviation of price).
*   $D_{	ext{eff}}$: Effective Depth (Book Depth penalized for Spoofing).
*   $\sqrt{\dots}$: The fixed universal exponent ($\delta = 0.5$).

### 1.3. The Residual (The Force)
The deviation between actual price move and theoretical impact constitutes the **SRL Residual**.

$$
	ext{Resid}_{	ext{SRL}} = \Delta P_{	ext{actual}} - 	ext{Impact}_{	ext{theoretical}}
$$

*   **Positive Residual (+):** Price moved *more* than flow justified (Overshoot/Overbought).
*   **Negative Residual (-):** Price moved *less* than flow justified (Undershoot/Oversold).
*   **Damper Force:** The restorative force is opposite to the residual: $\vec{F} = -	ext{sgn}(	ext{Resid})$.

---

## 2. Logic Flow (The Pipeline)

Data flows through three distinct stages: **Kernel (Physics)** -> **Trainer (Learning)** -> **Strategy (Execution)**.

### Phase 1: The Kernel (`omega_core/kernel.py`)
*Deterministic Physics Engine*

1.  **Ingest:** Read raw L2 frames (Parquet).
2.  **Gate:** Check `is_energy_active` ($\sigma \ge \sigma_{	ext{gate}}$).
3.  **Compute:**
    *   Calculate **Epiplexity** on the `trace` (recent ticks).
    *   Calculate **Holographic Topology** (Green's Theorem area on Price-OFI manifold).
    *   Calculate **SRL State** (Residual, Implied Y).
4.  **Update State (Adaptive Y):**
    *   *If* Epiplexity is high AND OFI is significant: Update $Y_t$ towards $Y_{	ext{implied}}$.
    *   *Else:* Decay $Y_t$ towards anchor.
5.  **Signal Generation (v5.1 Logic):**
    *   **Trigger:** High Epiplexity + Symmetric Residual > Limit + High Topo Energy.
    *   **Direction:** `-sign(srl_resid)` (Reversion).

### Phase 2: The Trainer (`omega_core/trainer_v51.py`)
*Probabilistic Interaction Layer*

1.  **Feature Engineering:**
    *   Load Kernel outputs (Epiplexity, Residual, Topo).
    *   **v5.1 P1 Fix:** Inject **Interaction Terms** ($X_{new} = 	ext{Epi} 	imes 	ext{Resid}$).
    *   *Why?* Linear models (SGD) cannot learn "IF Epi High THEN Trade Resid". Interaction terms linearize this logic.
2.  **Labeling:**
    *   Calculate Forward Return ($R_{fwd}$) over horizon $H$.
    *   Label = $	ext{sgn}(R_{fwd})$ *if* $|R_{fwd}| > k \cdot \sigma$.
3.  **Learning:**
    *   Model: `SGDClassifier(loss='log_loss')`.
    *   Weighting: Samples weighted by **Epiplexity** (Learn more from structured data).
4.  **Persist:** Save `checkpoint_rows_N.pkl`.

---

## 3. Algorithms & Data Structures

### 3.1. Key Algorithms

#### `calc_srl_state`
```python
# Pseudo-code
def calc_srl_state(dPrice, sigma, ofi, depth, Y):
    # 1. Spoofing Penalty
    depth_eff = depth * exp(-gamma * (cancel_vol / trade_vol))
    
    # 2. Theoretical Impact (Delta = 0.5)
    impact_unit = sigma * sqrt(abs(ofi) / depth_eff)
    impact_theo = sign(ofi) * Y * impact_unit
    
    # 3. Residual
    resid = dPrice - impact_theo
    
    # 4. Inverse Problem (Implied Y)
    # Only solve if signal > noise
    if impact_unit > epsilon:
        Y_implied = abs(dPrice) / impact_unit
    else:
        Y_implied = Y_current
        
    return resid, Y_implied
```

#### `apply_recursive_physics` (The Loop)
*Note: This is the current bottleneck (`to_dicts`).*
```python
current_Y = initial_Y
for row in dataframe:
    # 1. Compute Physics
    epi = calc_epiplexity(row.trace)
    resid, implied_Y = calc_srl_state(row, current_Y)
    
    # 2. Update State (Recursion)
    if epi > threshold and abs(ofi) > min_ofi:
        current_Y = (1 - alpha) * current_Y + alpha * implied_Y
    
    # 3. Store Result
    row.adaptive_y = current_Y
    results.append(row)
```

### 3.2. Data Structures (Polars Schema)

| Column | Type | Description | Source |
| :--- | :--- | :--- | :--- |
| `trace` | `List[f64]` | Recent price history (tick buffer) | Framer |
| `epiplexity` | `f64` | Compression Gain [0, 1] | Kernel |
| `srl_resid` | `f64` | Deviation from SRL Physics | Kernel |
| `adaptive_y` | `f64` | Current elasticity state | Kernel (Recursive) |
| `topo_area` | `f64` | Signed area of Price-OFI loop | Kernel |
| `is_signal` | `bool` | Hard physics gate trigger | Kernel |
| `direction` | `f64` | `-1`, `0`, `1`. Physics suggestion. | Kernel |
| `epi_x_srl_resid` | `f64` | Interaction Term (v5.1) | Trainer |

---

## 4. Metrics & Validation

### 4.1. Definition of Done (DoD) Metrics
*Source: `physics_auditor.py`*

1.  **Topo SNR (Signal-to-Noise Ratio):**
    *   Measures strength of Epiplexity signal vs. random shuffles.
    *   Formula: $(\mu_{real} - \mu_{shuffled}) / \sigma_{shuffled}$
    *   **Target:** $> 3.0$

2.  **Orthogonality:**
    *   Measures independence of Structure (Epiplexity) and Force (Residual).
    *   Formula: $	ext{Corr}(	ext{Epiplexity}, |	ext{Resid}|)$
    *   **Target:** $|ho| < 0.1$ (Ideally 0.0)

3.  **Vector Alignment:**
    *   Measures predictive power of the **Damper Hypothesis**.
    *   Formula: Accuracy of $	ext{sgn}(	ext{Direction}) == 	ext{sgn}(	ext{FutureReturn})$
    *   **Scope:** Only measured where Structure (Epi) is high (Top 20%).
    *   **Target:** $> 0.6$ (60% Directional Accuracy)

### 4.2. Audit Procedure
1.  **Continuous Calibration:** `physics_auditor.py` scans random files to learn `ANCHOR_Y` and `SIGMA_GATE`.
2.  **Deep Audit:** Processes full dataset to compute global DoD metrics.
3.  **Result:** Generates `audit/v51_deep_audit.md`.

---

## 5. Edge Cases & Safety

1.  **Morning Spike Protection:**
    *   In `omega_etl.py`, `time_fraction` is clamped to `[0.05, 1.0]` to prevent opening auction volatility from projecting 100x volume for the day.
2.  **Zero Volatility:**
    *   If `sigma < 1e-9`, `srl_resid` defaults to 0.0 and `epiplexity` to 0.0.
3.  **Missing Columns:**
    *   If `trade_vol` is missing, Spoofing Penalty is disabled (warns user).
4.  **Memory Exhaustion:**
    *   The recursive loop (`to_dicts`) explodes RAM on files > 50MB.
    *   *Mitigation:* Split files or use `check_memory_safe` (sleep if RAM > 85%).

---

## 6. Versioning

**v5.1 (Current)** differs from v5.0 by:
1.  **Symmetric Gating:** `srl_resid.abs() > Limit` (was `srl_resid < -Limit`).
2.  **Damper Direction:** Explicitly `-sign(srl_resid)` (was `sign(topo)`).
3.  **Interaction Terms:** `epi_x_*` features added to Trainer.
4.  **Final Flush:** Trainer forces a checkpoint at the very last batch.

---

## 7. Performance

*   **Complexity:** $O(N)$ per day.
*   **Bottleneck:** `omega_core/kernel.py: _apply_recursive_physics` -> `frames.to_dicts()`.
    *   *Cost:* Deserializing millions of Polars rows to Python objects.
    *   *Impact:* High RAM usage, low CPU utilization (GIL bound).
*   **Parallelism:**
    *   **Training:** Multi-process (File-level parallelism).
    *   **Backtesting:** Multi-process (File-level parallelism).
