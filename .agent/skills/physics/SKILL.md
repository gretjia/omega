---
name: physics
description: Guard rails for OMEGA's market microstructure physics model (SRL, Impact, Spoofing).
---

# Skill: physics

## When To Use

- Modifying the Square Root Law (SRL) implementation
- Changing adaptive Y recursion, spoofing penalty, or impact model
- Working on `_apply_recursive_physics()` in `kernel.py`
- Modifying Stage 2 physics compute (`tools/stage2_physics_compute.py`)

## The Physics Model

OMEGA models price impact as:

```
Impact = Y × σ × √(|Q|/D)     (Sato 2025, delta=0.5)
```

Where:

- **Y** = structural rigidity (adaptive, `y_min=0.1` to `y_max=5.0`)
- **σ** = volatility (floored at `sigma_floor`)
- **Q** = net order flow imbalance
- **D** = effective depth (adjusted for spoofing via `exp(-γ × cancel/trade)`)

## Critical Rules

1. **delta=0.5 is a physics constant**, not a hyperparameter. Never optimize it.
2. **Y update requires OFI signal**. If `abs(net_ofi) < min_ofi_for_y_update`, hold previous Y state. Do not update from noise.
3. **Spoofing correction is multiplicative**: `D_eff = D × exp(-γ × spoof_ratio)`. It narrows depth, it doesn't add to it.
4. **Peace threshold** (`peace_threshold=0.8799`): When epiplexity exceeds this, the market is in a "peace" regime — suppress physics signals.

## Lessons from Production

- **Numba JIT**: `calc_srl_recursion_loop` is JIT-compiled. If numba is missing, the fallback pure-Python loop works but is 50x slower. Verify with `python3 -c "import numba; print(numba.__version__)"`.
- **Stage 2 timeout**: Physics compute on large files can hit 5400s timeouts. The `fail_ledger` tracks these. Check before reprocessing.
- **Thread contention**: `POLARS_MAX_THREADS` must be set to prevent oversubscription when running multiple workers. Use `configs/node_paths.py` for node-specific settings.

## Canonical Files

- `omega_core/kernel.py` → `_apply_recursive_physics()` (main loop)
- `omega_core/omega_math_core.py` → `calc_srl_state()` (scalar kernel)
- `omega_core/omega_math_vectorized.py` → `calc_srl_recursion_loop()` (JIT batch)
- `config.py` → `L2SRLConfig`, `L2SignalConfig`
