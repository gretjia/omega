---
name: engineering
description: Engineering and adapter practices for OMEGA v3, including config usage, data-frame hygiene, and external SDK integration.
---

# Skill: Engineering & Adapter

## Description
Handles implementation details for Python engineering, adapter boundaries, and data IO safety.

## Capabilities

### 1. Adapter layer discipline
- Keep external SDK calls (`qmt`, `rq`) in adapter modules, not in `omega_v3_core/*`.
- Normalize symbol formats at boundaries (`600000` -> `600000.XSHG` or `600000.SH`).
- Ensure retries/timeouts for network-style SDK calls.

### 2. Python engineering
- Prefer vectorized `numpy`/`pandas`/`polars` paths over row loops.
- Keep explicit types for public functions and dataclasses.
- Add guards for NaN/Inf and empty frames before core math calls.
- For large parquet corpora, avoid unbounded wildcard `collect()` in chain-critical paths; use bounded sampling/chunking.

### 3. Configuration handling
- **Read**: use `config.py` dataclasses and `load_l2_pipeline_config()`.
- **Write**: never write runtime state back to `config.py`.
- **State**: save trained/frozen state to artifacts (for example `artifacts/*.pkl`).
- **Split contract**: training/backtest file lists must be role-filtered manifests with overlap checks (fail closed by default).

## Verification protocol
- [ ] External SDK calls are wrapped and failures are explicit.
- [ ] DataFrame columns/index/order are validated before compute.
- [ ] NaN/Inf/shape guards are present around critical transforms.
- [ ] No runtime path writes into `config.py`.
- [ ] Train/backtest manifests are role-isolated (no overlap).
