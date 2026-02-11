---
name: math_core
description: OMEGA v3 math kernel skill for SRL residuals, epiplexity, topology proxies, and topo-SNR calculations.
---

# Skill: Math Core (The Trinity)

## Description
Use the deterministic kernels in `omega_v3_core/omega_math_core.py` for active v3 work.

## Capabilities

### 1. Epiplexity and topology signal quality
- `calc_epiplexity(trace, cfg)` for time-bounded structure proxy.
- `topo_snr_from_traces(traces, cfg, epi_cfg)` for topology signal-to-noise check.

### 2. SRL physics and residual analysis
- `calc_srl_residual(net_ofi, price_change, depth, sigma, cfg)` for vectorized residuals.
- `calc_physics_state(price_change, sigma, net_ofi, depth, current_y, cfg)` for per-sample inverse SRL diagnostics.

### 3. Directional topology proxies
- `calc_signed_area(trace, ofi_list)` for direction proxy in phase space.
- `calc_holographic_topology(trace, ofi_list)` for `(signed_area, energy)` pair.

## Required config types
- `L2SRLConfig`
- `L2EpiplexityConfig`
- `L2TopoSNRConfig`

All are defined in `config.py`.

## Verification protocol
- [ ] Inputs are converted to numeric arrays and shape-checked.
- [ ] SRL is applied in volume-clock-consistent context.
- [ ] Floors (`depth_floor`, `sigma_floor`, `std_floor`) are respected.
- [ ] No ad-hoc hardcoded thresholds bypass config.
