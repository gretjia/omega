---
name: math_core
description: Guard rails for modifying OMEGA mathematical kernels (SRL, TDA, Epiplexity).
---

# Skill: math_core

## When To Use

- Modifying `omega_core/omega_math_core.py` or `omega_core/omega_math_vectorized.py`
- Adding/changing physics formulas, compression gain, topology calculations
- Changing `config.py` parameters that affect mathematical output

## Invariants (NEVER violate these)

1. **Delta = 0.5 is universal** (Sato 2025). The SRL exponent is hardcoded to 0.5. Do NOT make it configurable or "race" across exponents. The race was cancelled in v5.0.
2. **Epiplexity gain ≥ 0** (MDL discipline). `calc_compression_gain()` must never return negative values. If model cost exceeds data cost, return 0.
3. **Zero-variance → zero signal**. Constant traces must produce 0.0 gain, not NaN/inf.
4. **Topology sign reversal**. `calc_topology_area(x, y)` reversed == `-calc_topology_area(x_rev, y_rev)`. Green's theorem is antisymmetric.
5. **All scalars must be finite**. Every math function must handle NaN/inf inputs gracefully via safe floors.

## Safe Floors (Denominator Trap Prevention)

| Floor | Config Path | Purpose |
|---|---|---|
| `sigma_floor` | `L2SRLConfig.sigma_floor` | Prevents sqrt(Q/D) / 0 |
| `depth_floor` | `L2SRLConfig.depth_floor` | Prevents division by zero depth |
| `price_scale_floor` | `L2TopologyRaceConfig` | Prevents topology normalization explosion |
| `min_trace_len` | `L2EpiplexityConfig` | Prevents OLS on < 3 data points |

## Verification Gate

Before merging ANY math change:

```bash
python3 -m pytest tests/test_omega_math_core.py -v  # Must be 28/28 pass, <1s
```

## Canonical Files

- `omega_core/omega_math_core.py` — scalar kernels (source of truth)
- `omega_core/omega_math_vectorized.py` — batch kernels (must match scalar behavior)
- `omega_core/omega_math_rolling.py` — rolling window variants
- `tests/test_omega_math_core.py` — invariant tests
