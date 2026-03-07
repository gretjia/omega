# V64.3 All-Zero Recursive Audit - Round 1 Candidate Decomposition

Date: 2026-03-07  
Author: Codex  
Mission: `V64 All-Zero Root-Cause Recursive Audit`  
Status: complete

## 1. Round objective

Round 1 ranks candidate root causes for the all-zero phenomenon.

The governing question is:

`What shared mechanism can explain why both the baseline route and the speed route produce all-zero outputs?`

## 2. Candidate classes

### Candidate A: ETL -> kernel ordering / boundary contract defect

Hypothesis:

- the frames entering `apply_recursive_physics()` are not emitted in the symbol-contiguous order required by the rolling boundary logic
- `dist_to_boundary` therefore resets too frequently
- rolling topology and rolling compression never warm up

Supporting evidence:

- `kernel.py` computes boundaries from adjacent row transitions in `symbol/date`
- Stage 2 outputs are highly symbol-interleaved, with `max_consecutive_same_symbol <= 5` in sampled full-day outputs
- the baseline route is also highly interleaved and also all-zero

Weakness at this round:

- we had not yet localized the defect to a specific upstream stage

Preliminary ranking:

- `highest`

Defect class:

- `integration`

### Candidate B: topology fast-path regression

Hypothesis:

- the topology fast-path implementation in `omega_math_rolling.py` collapses to zero on real data

Supporting evidence:

- reference geometry on sampled eligible windows is non-zero
- stored topology values are zero

Weakness at this round:

- the baseline route is also zero
- so this cannot yet explain why the old route already exhibited the same phenomenon

Preliminary ranking:

- `medium`

Defect class:

- `algorithm` or `integration`

### Candidate C: epiplexity is naturally zero on these slices

Hypothesis:

- the chosen slices simply do not produce positive `Var(ΔP) / Var(R)` compression

Supporting evidence:

- sampled reference epiplexity windows can indeed be zero

Weakness at this round:

- this cannot explain why topology is also systematically zero
- it does not explain the shared baseline/speed-route topology collapse

Preliminary ranking:

- `low`

Defect class:

- `validation` or `slice-selection`

### Candidate D: smoke-validation framework never required informative slices

Hypothesis:

- the historical smoke framework was good for pipeline contract validation, but never guaranteed signal-bearing slices

Supporting evidence:

- the previously “successful” baseline smoke was already zero-signal
- backtest metrics were zero because there were no informative rows

Weakness at this round:

- this explains why the problem was not detected
- it does not by itself explain why topology and epiplexity remain zero on repeated full-day probes

Preliminary ranking:

- `medium`

Defect class:

- `validation`

## 3. Candidate ranking

### Rank 1

`Candidate A: ETL -> kernel ordering / boundary contract defect`

Reason:

- it is the strongest shared explanation for both routes
- it explains why rolling-state features die before later gates
- it is consistent with the symbol-interleaved outputs already observed

### Rank 2

`Candidate D: smoke-validation framework defect`

Reason:

- it explains why the baseline route was historically accepted despite zero-signal outputs
- it is likely real, but it looks secondary rather than primary

### Rank 3

`Candidate B: topology fast-path regression`

Reason:

- it remains plausible locally
- but the existence of the same phenomenon in the pre-speed baseline makes it less likely as the principal shared cause

### Rank 4

`Candidate C: natural slice-level zero compression`

Reason:

- possible for epiplexity in isolation
- insufficient as a full explanation for zero topology plus zero signal everywhere

## 4. Round 1 verdict

### Verdict

`PASS`

### Meaning

Round 1 narrows the investigation to one dominant candidate:

`The most likely primary cause is an ordering / boundary contract defect at the ETL -> kernel interface.`

## 5. Next-round question

Round 2 should ask a much narrower question:

`Can we directly show that Stage 2 emits or constructs frames in an order that violates the symbol-contiguous assumption required by apply_recursive_physics()?`
