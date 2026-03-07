# V64.3 All-Zero Audit Submission

Date: 2026-03-07  
Author: Codex  
Status: Submitted for independent audit review

## 1. Purpose

This document packages the current evidence around the `all-zero` phenomenon observed during V64.3 smoke and discovery work.

The goal is to answer one narrow question:

`Did the engineering speed patch introduce the all-zero condition, or did that condition already exist in the pre-speed baseline?`

This audit does **not** attempt to reopen the approved V64.3 canonical runtime math core. It is an evidence package for independent review.

## 2. Canonical review anchor

The math-core release standard remains:

- `audit/v64_audit_evolution.md`
- `audit/v643.md`
- `audit/v643_auditor_pass.md`

Working rule for this audit:

- if the all-zero condition already existed in the pre-speed baseline, it cannot be treated as evidence that the engineering speed patch introduced a new canonical math regression

## 3. Evidence sources

Repo-local evidence:

- `audit/v64_audit_evolution.md`
- `audit/v643.md`
- `audit/v643_auditor_pass.md`

Remote smoke / probe evidence on `linux1-lx`:

- baseline smoke workspace:
  - `/home/zepher/work/Omega_vNext_v643_smoke`
- speed smoke workspace:
  - `/home/zepher/work/Omega_vNext_v643_speed_smoke`
- training-comparison smoke workspace:
  - `/home/zepher/work/Omega_vNext_v643_traincmp_smoke`
- discovery probe workspace:
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke`

Key artifacts in the discovery probe workspace:

- `audit/runtime/v643_probe/monthly_probe_manifest.json`
- `audit/runtime/v643_probe/probe_rankings.json`
- `audit/runtime/v643_probe/fullprobe_candidates.json`
- `audit/runtime/v643_probe/fullprobe.log`
- `audit/runtime/v643_probe/fullprobe2_candidates.json`
- `audit/runtime/v643_probe/fullprobe2.log`
- `audit/runtime/v643_probe/fullprobe2_rankings.json`
- `audit/runtime/v643_probe/gate_chain_diagnosis.json`

## 4. Baseline smoke evidence: the pre-speed route is already all-zero

The pre-speed baseline smoke workspace was checked directly:

- workspace:
  - `/home/zepher/work/Omega_vNext_v643_smoke`
- code anchor:
  - `a0e65e6`

The baseline `L2` files for the historical successful smoke window:

- `20230320_fbd5c8b.parquet`
- `20230321_fbd5c8b.parquet`
- `20230322_fbd5c8b.parquet`
- `20230323_fbd5c8b.parquet`
- `20230324_fbd5c8b.parquet`

Observed result for all five baseline files:

- `epiplexity max = 0.0`
- `epiplexity sum = 0.0`
- `is_signal sum = 0`
- `singularity_vector abs sum = 0.0`
- `topo_area_nonzero_rows = 0`
- `topo_energy_pos_rows = 0`

This is the most important baseline fact:

- the old pre-speed engineering route is already zero-signal on its own smoke evidence

## 5. Discovery probe evidence: repeated search also found only zero-output slices

### 5.1 Monthly tiny-symbol probes

Method:

- one representative day per month
- tiny liquid-symbol slice
- Stage 2 probe only

Result:

- `37` monthly probes completed
- every one remained zero under strict V64.3 semantics

### 5.2 Full-day full-market probes: `fbd5c8b`

Files:

- `20250901_fbd5c8b.parquet`
- `20251013_fbd5c8b.parquet`
- `20251105_fbd5c8b.parquet`
- `20251202_fbd5c8b.parquet`
- `20260105_fbd5c8b.parquet`

Result for all five:

- `epiplexity max = 0.0`
- `epiplexity sum = 0.0`
- `is_signal sum = 0`
- `singularity_vector abs sum = 0.0`

### 5.3 Full-day full-market probes: `b07c2229`

These files were chosen from real historical debug / assist / pathological records, not from random date guessing.

Files:

- `20240717_b07c2229.parquet`
- `20250704_b07c2229.parquet`
- `20250725_b07c2229.parquet`
- `20250828_b07c2229.parquet`
- `20251022_b07c2229.parquet`

Result for all five:

- `epiplexity max = 0.0`
- `epiplexity sum = 0.0`
- `is_signal sum = 0`
- `singularity_vector abs sum = 0.0`

Net result of discovery work:

- `37` monthly tiny probes: all zero
- `10` full-day full-market probes: all zero

## 6. Gate-chain diagnosis: later gates are not the first point of collapse

The gate-chain diagnosis over all `10` full-day probe outputs is recorded in:

- `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/gate_chain_diagnosis.json`

Totals across `2,631,868` rows:

- `physics_valid_rows = 2,631,868`
- `energy_active_rows = 2,631,868`
- `sigma_gate_rows = 1,442,120`
- `spoof_ok_rows = 847,836`
- `epi_pos_rows = 0`
- `epi_gate_rows = 0`
- `topo_area_rows = 0`
- `topo_energy_rows = 0`
- `full_signal_gate_rows = 0`

Interpretation:

- the collapse is not first caused by the later `sigma` or `spoof` gates
- the chain is already zero earlier:
  - `epiplexity` never becomes positive
  - topology outputs never become positive

## 7. Ordering evidence: full-day smoke outputs are highly symbol-interleaved

Two sampled full-day probe outputs were checked for row-order structure.

### `20250725_b07c2229.parquet`

- `rows = 271,571`
- `unique_symbols = 7,011`
- `transitions = 265,170`
- `max_consecutive_same_symbol = 5`

### `20250901_fbd5c8b.parquet`

- `rows = 259,501`
- `unique_symbols = 7,130`
- `transitions = 253,487`
- `max_consecutive_same_symbol = 4`

This matters because the rolling physics and topology kernels use boundary-aware state. Highly interleaved rows mean the effective same-symbol run length in file order is extremely short.

However, this evidence still does **not** prove the speed patch introduced the problem, because the pre-speed baseline smoke is also all-zero and also symbol-interleaved.

## 8. Reference-window evidence: real geometry can be non-zero even when stored topology is zero

A direct reference computation was run on a real eligible symbol from `20250725_b07c2229.parquet`.

Example symbol:

- `002097.SZ`
- `n_rows = 177`

Reference first `60`-window geometry from raw `close` and cumulative `net_ofi`:

- `reference_area_window0 = -1.5816135493197145`
- `reference_energy_window0 = 58.69980789238198`

Stored outputs for the same symbol:

- `stored_topo_area_max = 0.0`
- `stored_topo_energy_max = 0.0`
- `stored_epiplexity_max = 0.0`

Additional spot check:

- among the first `20` eligible symbols with at least `60` rows in `20250725_b07c2229.parquet`
- `20/20` had non-zero reference geometry in the sampled first window
- but stored topology outputs were still zero

This establishes a real discrepancy between:

- reference geometry computed on raw same-symbol windows
- stored Stage 2 topology outputs in the probe artifacts

But because the baseline smoke is also zero, this discrepancy cannot yet be attributed uniquely to the engineering speed patch.

## 9. Boundaries of what this evidence proves

This evidence **does prove**:

- the all-zero condition predates the engineering speed patch
- the baseline smoke workspace already exhibits zero `epiplexity`, zero `is_signal`, zero `singularity_vector`, zero `topology`
- repeated discovery probes on the speed-patch branch did not find an informative non-zero slice
- the later `sigma` and `spoof` gates are not the first place where rows are eliminated

This evidence does **not yet prove**:

- the exact root cause of the all-zero condition
- whether the dominant cause is:
  - a long-standing input ordering contract problem
  - an overly strict smoke slice under current semantics
  - a topology / rolling integration defect that already existed before the speed patch
  - or a combination of the above

## 10. Current operational conclusion

Until the all-zero root cause is found:

- the old pre-speed engineering route must be preserved
- the engineering-speed route must also be preserved
- neither route should be retired or blessed as final
- the all-zero condition must not be assigned as a unique fault of the speed patch

## 11. Questions for the independent auditor

Please answer these questions directly against the evidence above:

1. Does this evidence package support the conclusion that the all-zero condition already existed in the pre-speed baseline smoke?
2. Is it technically correct to preserve both the old route and the engineering-speed route until the root cause is found?
3. Given the evidence, what is the most likely next narrow diagnosis scope?
4. Do you see any logical error in separating:
   - engineering speed-patch evaluation
   - long-standing zero-signal diagnosis

## 12. Requested auditor decision

The requested decision is not a final release verdict.

The requested decision is narrower:

- whether this audit package is sufficient to establish that the all-zero condition predates the engineering speed patch
- and therefore whether both routes must remain preserved pending root-cause analysis
