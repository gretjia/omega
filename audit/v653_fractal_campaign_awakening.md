# System Architect Absolute Override: The Fractal Campaign Awakening

Status: Frozen external architect override
Date: 2026-03-09
Scope: V64 canon + Path A exhaustion + Path B collapse + V650 kill + V652 superseded

## Override Status

This document supersedes the narrower V652 framing.

Hard rule:

- the mathematical formulas defined below are frozen
- they must not be changed
- implementation may adapt files, pipelines, `omega_core/*`, and even Stage2 recomputation if required by truth
- but the mathematical meaning must remain identical

## Central Claim

Verdict:

- `PARTIAL ONLY`

Interpretation:

- V64 still detects real compression and singularity structure
- but the correct downstream object is not a microscopic return predictor
- it is a **fractal campaign-state machine** built on a real daily temporal spine

## Canonical Diagnosis

Three failures are now canonical:

1. **Mechanical Zero-Mass Bug**
   - demeaning by `["date", "time_key"]` can create one-name or near-one-name groups
   - this mechanically manufactures zeros and must be treated as a code bug
2. **Broken Temporal Spine**
   - sparse signal matrices destroy true calendar semantics
   - rolling over sparse event rows is not equivalent to rolling over trading days
3. **Fractal Disconnect**
   - a 60-bar micro-physical detector cannot be translated honestly into next-step payoff logic
   - the correct object is campaign pressure integrated over true calendar time

## Frozen Mathematical Contract

### Layer 1: Pulse Compression on Symbol-Day

For symbol `i`, date `d`, and intraday event set `E_{i,d}`:

- `F_{i,d} = sum_{e in E_{i,d}} s_{i,d,e}`
- `A_{i,d} = sum_{e in E_{i,d}} |s_{i,d,e}|`

Iron rule:

- the daily spine must be continuous in real trading dates
- if no physical event exists on a valid trading date:
  - `F = 0`
  - `A = 0`

### Layer 2: Recursive Campaign State via IIR / EMA

For half-life `tau in {5, 10, 20}`:

- `S_{i,d}^{(tau)} = EMA_tau(F_{i,d})`
- `V_{i,d}^{(tau)} = EMA_tau(A_{i,d})`
- `Omega_{i,d}^{(tau)} = |S_{i,d}^{(tau)}| / (V_{i,d}^{(tau)} + eps)`
- `Psi_{i,d}^{(tau)} = S_{i,d}^{(tau)} * Omega_{i,d}^{(tau)}`

### Layer 3: Tradable Asymmetric Labels

Tradable excess return:

- `Y_ret_{i,d,H} = P_close(i,d+H) / P_open(i,d+1) - 1 - Rbar_date,H`

Hard demeaning rule:

- demeaning is only allowed by:
  - `pure_date`
- never by:
  - `["date", "time_key"]`

Triple-barrier first-passage hazard:

- entry price:
  - next-day open
- upper barrier:
  - `entry * (1 + 2 * sigma)`
- lower barrier:
  - `entry * (1 - 1 * sigma)`
- conservative precedence:
  - if stop-loss is touched first or ties the profit touch:
    - label `-1`
  - else if profit barrier is touched first:
    - label `1`
  - else:
    - label `0`

## Truth-First Engineering Rule

The formulas above are frozen.

Truth-first implementation freedom is allowed for:

- `omega_core/*`
- `tools/*`
- Stage2 recomputation
- artifact schemas
- daily-spine construction
- Numba path kernels

provided that:

- the formulas remain identical
- every formula-bearing diff is audited by `gemini -p` on `gemini 3.1 pro preview`

## Strategic Execution Order

The correct order is:

1. restore a real daily temporal spine
2. forge campaign-state features from micro pulses onto that spine
3. compute tradable multi-day labels and first-passage barriers
4. run a pure event study first
5. only if monotonicity is proven may ML return

No cloud / Vertex / XGBoost opening move is allowed before the event-study gate.
