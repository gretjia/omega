# System Architect Absolute Override: The Campaign-State Revelation

Status: Frozen external architect override
Date: 2026-03-09
Scope: Frozen V64 math canon + Path A exhaustion + Path B collapse + V650 zero-mass kill

## Override Status

This document supersedes the narrower V651 horizon-only framing as the new top-level authority for the next upgrade wave.

Hard rule:

- the mathematical formulas defined below are **frozen**
- they must not be changed
- engineering glue may adapt the implementation only to connect these formulas into the current codebase without altering their meaning

## Central Claim

Verdict:

- `PARTIAL ONLY`

Interpretation:

- the V64 physics core successfully detects real trajectory compression and `Epiplexity`
- but the current downstream translation layer has not yet proven that it converts that compression into stable campaign-level intelligence
- the next blocker is not merely target horizon length in isolation
- it is the need to elevate OMEGA from a microscopic return label to a **campaign-state machine**

## Absolute Diagnosis

Two failures are now treated as canonical:

1. **The Mechanical Zero-Mass Bug**
   - the old excess-return demeaning key used:
     - `["date", "time_key"]`
   - in very small time slices this can produce groups containing one or very few symbols
   - subtracting a group mean from itself mechanically manufactures zeros
   - this is treated as a code-level bug, not as market truth
2. **The Fractal / Campaign-State Disconnect**
   - V64 detects compressed market energy using local topological and singularity structure
   - large campaign-style capital accumulation cannot be expected to fully release in the next microscopic step
   - the label must therefore move from short-step payoff to multi-day / multi-week campaign release

## Frozen Mathematical Upgrade

### Layer 1: Intraday -> Symbol-Day collapse

Daily net force:

`F_{i,d} = sum_b SingularityVector_{i,d,b}`

Daily absolute action:

`A_{i,d} = sum_b |SingularityVector_{i,d,b}|`

Daily consistency:

`C_{i,d} = |F_{i,d}| / (A_{i,d} + eps)`

### Layer 2: Symbol-Day -> Multi-Week Campaign collapse

For campaign horizon `H`:

Campaign coherence:

`Omega_{i,d}^{(H)} = |sum_{k=0}^{H-1} F_{i,d-k}| / (sum_{k=0}^{H-1} A_{i,d-k} + eps)`

Campaign momentum:

`M_{i,d}^{(H)} = Omega_{i,d}^{(H)} * sum_{k=0}^{H-1} F_{i,d-k}`

### Layer 3: Asymmetric campaign labels

True excess return:

`Y_ret_{i,d,H} = (P_{i,d+H} / P_{i,d} - 1) - Rbar_{d,H}`

Hard demeaning rule:

- demeaning is only allowed at pure-date horizon:
  - `pure_date`
- never by `["date", "time_key"]`

Triple-barrier hazard:

- future `H`-day path first touches `+2 sigma`:
  - label `1`
- future `H`-day path first touches `-1 sigma`:
  - label `-1`
- otherwise:
  - label `0`

## Engineering Translation Rule

The formulas above are frozen.

However, engineering corrections are allowed for:

- field plumbing
- grouping key normalization
- variable naming mistakes in pseudocode
- artifact schemas
- runtime orchestration

provided that:

- the mathematical meaning of the formulas does not change
- any necessary edits inside `omega_core/*` are treated as implementation-level translation only
- every formula-bearing `omega_core/*` change is audited against this document

## Strategic Execution Order

The architect override explicitly forbids immediate cloud ML escalation.

The required order is:

1. build a campaign-state matrix locally
2. verify the zero-mass collapse disappears under the corrected demeaning and campaign horizons
3. run a pure event study first
4. only after clear monotonicity is proven may ML move back into scope

## Operational Consequence

The next mission must not start as:

- Vertex swarm
- XGBoost sweep
- holdout-heavy ML iteration

It must start as:

- campaign-state forge
- distribution audit
- classical event study

with ML deferred behind an explicit gate.
