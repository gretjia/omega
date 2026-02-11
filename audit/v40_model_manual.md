# OMEGA v4.0 Model Manual: The Physics of Alpha
**Version:** 4.0 (Race Patch 02)
**Date:** 2026-02-11
**Based on:** Training Checkpoint `32517695`

---

## Chapter 1: The Core Philosophy
**"Structure Predicts Movement"**

Unlike traditional technical analysis (which follows trends) or standard high-frequency trading (which chases speed), OMEGA v4.0 is built on **Statistical Physics**.

It views the market not as a random walk, but as a physical system subject to:
1.  **Energy Constraints**: Prices cannot move infinitely without fuel (Volume/OFI).
2.  **Impact Limits**: Price changes must obey the Square-Root Law (SRL). Deviations create "potential energy" that must be released (Mean Reversion).
3.  **Structural Complexity**: Information density (Epiplexity) distinguishes "Dead" markets from "Alive" ones.

**The Strategy:** OMEGA v4.0 does not predict the news. It predicts **Physical Restitution**—betting that when the market violates the laws of physics (e.g., moves too far with too little volume), it *must* snap back.

---

## Chapter 2: System Architecture (The Two-Layer Funnel)

The model operates as a sophisticated two-stage filter.

### Stage 1: The Gatekeeper (Kernel Level)
Before any prediction is made, data must pass a strict physical exam.

**Code Source:** `omega_v3_core/kernel.py` (Lines ~88-100)

```python
# [omega_v3_core/kernel.py]
# Patch A: Energy Gating Logic
sigma_gate_enabled = bool(getattr(epi_cfg, "sigma_gate_enabled", False))
sigma_gate = float(getattr(epi_cfg, "sigma_gate", 0.0))

# The Physical Check
is_energy_active = (not sigma_gate_enabled) or (sigma_eff >= sigma_gate)

if is_energy_active:
    epiplexity = calc_epiplexity(trace, epi_cfg)
else:
    # REJECTION: Force complexity to zero if energy is too low
    epiplexity = float(epi_cfg.fallback_value) 
```

*   **The Guard**: `Sigma Gate` & `Epiplexity`
*   **The Mechanism**:
    *   If **Volatility (Sigma) < 0.01** (Configured in `config.py`): The market is a "Zombie".
    *   **Action**: `is_energy_active` becomes False, `epiplexity` forced to 0.0.

### Stage 2: The Decision Brain (Linear Level)
Once data passes the gate, the Linear Model calculates a score.

**Code Source:** `parallel_trainer/run_parallel_v31.py` (Lines ~160)

```python
# [parallel_trainer/run_parallel_v31.py]
# The mathematical prediction using learned weights
# X_scaled = Scaler(Features)
# y_pred = Model.dot(X_scaled) + Intercept
probs = model.predict_proba(X_scaled)[:, 1]
```

---

## Chapter 3: The Decision Logic (Decoding the Weights)

### 3.1 The "Brakes": Mean Reversion Drivers

**Code Source:** `omega_v3_core/kernel.py` (Lines ~170-190 for Feature Calculation)

```python
# [omega_v3_core/kernel.py]
# Calculating the Physics Anchor (SRL Residual)
srl_residuals, ... = calc_srl_race(
    price_change=price_change,
    sigma=sigma_eff,
    net_ofi=net_ofi,
    ...
)
# If price_change > Theoretical_Impact, srl_resid becomes positive.
# Model Weight (-0.0300) * Positive Resid = Negative Score (Sell Signal).
```

| Feature | Weight | Role | Logic |
| :--- | :--- | :--- | :--- |
| **`net_ofi`** | **-0.0599** | **Contra-Flow** | "Everyone is panic buying (OFI > 0). Liquidity is exhausted. **Sell into them.**" |
| **`price_change`** | **-0.0381** | **Reversal** | "Price just jumped up. Short-term overextension. **Short it.**" |
| **`srl_resid_050`** | **-0.0300** | **Physics Anchor** | "Price moved further than the Square-Root Law allows. **Fade it.**" |

### 3.2 The "Accelerator": Topological Energy

**Code Source:** `omega_v3_core/omega_math_core.py` (via `kernel.py`)

```python
# [omega_v3_core/kernel.py]
# Topology Energy Calculation
topo_area, topo_energy = calc_holographic_topology(...)
# High Energy = Complex Phase Space Trajectory
```

| Feature | Weight | Role | Logic |
| :--- | :--- | :--- | :--- |
| **`topo_energy`** | **+0.0317** | **Signal Amplifier** | "The market is chaotic and high-energy. **Double the bet.**" |

---

## Chapter 4: Topology - The 3D Glasses

### 4.1 The Race Winner: Lane B (Classic)
**`topo_classic` (Price vs. Volume) | Weight: -0.0130**

**Code Source:** `config.py` (L2TopologyRaceConfig)

```python
# [config.py]
# Lane B Definition: Price vs Volume Manifold
("topo_classic", "trace", "vol_trace", "price_scale_floor", "vol_scale_floor"),
```

This feature measures the **Geometric Area** swept by Price and Volume.
*   **Scenario**: A "high volume spike".
    *   **2D View**: Price +1%, Volume 100k.
    *   **3D View (Topology)**: The trajectory on the Price-Volume manifold encloses a massive "Area".
*   **Decision**:
    *   If Price is up and Area is huge, it means the move "cost" too much energy.
    *   Model says: **"This rally is exhausted. The heavy truck cannot stop instantly, but it cannot accelerate further. Short."**

### 4.2 Quantitative Impact
In extreme events, Topology can be **more important than price**.
*   *Example*: A Flash Crash (Price -5, Energy High).
    *   **Price Signal**: $+0.19$ (Buy)
    *   **Topology Signal**: $+0.191$ (Buy Harder)
    *   **Combined**: A "Strong Buy" that is 2x stronger than using Price alone.

---

## Chapter 5: Case Studies (How it Thinks)

### Case A: The "Fake Rally" (Short Signal)
**Market State:**
*   Price jumps up 1% (`price_change` > 0).
*   Retail is chasing the high (`net_ofi` > 0).
*   Volume is huge (`topo_classic` area > 0).
*   Move exceeds SRL limit (`srl_resid` > 0).

**Model Calculation:**
$$ Score = (	ext{Positive Price} 	imes -0.038) + (	ext{Positive OFI} 	imes -0.059) + (	ext{Positive Area} 	imes -0.013) $$
$$ Score = 	ext{Negative} + 	ext{Negative} + 	ext{Negative} = \mathbf{	ext{Strong Negative}} $$

**Decision:** **SHORT**. The model identifies an overextended, expensive move driven by retail flow.

### Case B: The "Zombie" (No Signal)
**Market State:**
*   Price is flat (`price_change` $\approx$ 0).
*   Volume is zero.
*   Sigma is 0.005 (Low).

**Kernel Action:**
*   `sigma < sigma_gate` (0.01).
*   **Gate Closes.** `epiplexity` forced to 0.
*   **Decision:** **SLEEP**. No computation wasted. No spread paid.

---

## Chapter 6: Conclusion

OMEGA v4.0 is not a black box. It is a logical machine built on physical principles.
1.  **It ignores the noise** (Kernel Gating).
2.  **It fades the crowd** (Negative OFI/Price weights).
3.  **It respects the limits of physics** (SRL Anchoring).
4.  **It senses the energy** (Topological Amplification).

It does not try to be "smart" about every tick. It waits for the market to break a physical law, and then it steps in to capture the restitution.
