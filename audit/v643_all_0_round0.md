# V64.3 All-Zero Recursive Audit - Round 0

Date: 2026-03-07  
Author: Codex  
Mission: `V64 All-Zero Root-Cause Recursive Audit`  
Status: complete

## 1. Round objective

Round 0 asks only one question:

`Is the all-zero phenomenon a new engineering speed-patch regression, or did it already exist in the pre-speed baseline?`

This round does not identify final root cause. It only validates the evidence package and draws the first hard boundary between fact and inference.

## 2. Materials reviewed

- [v643_all_0_audit.md](/home/zephryj/projects/omega/audit/v643_all_0_audit.md)
- [v64_audit_evolution.md](/home/zephryj/projects/omega/audit/v64_audit_evolution.md)
- baseline smoke workspace:
  - `linux1-lx:/home/zepher/work/Omega_vNext_v643_smoke`
- speed smoke workspace:
  - `linux1-lx:/home/zepher/work/Omega_vNext_v643_speed_smoke`
- comparison smoke workspace:
  - `linux1-lx:/home/zepher/work/Omega_vNext_v643_traincmp_smoke`
- discovery probe workspace:
  - `linux1-lx:/home/zepher/work/Omega_vNext_v643_probe_smoke`

## 3. What is proven

### 3.1 The pre-speed baseline smoke is already all-zero

This is directly established from the historical successful baseline smoke workspace:

- workspace:
  - `linux1-lx:/home/zepher/work/Omega_vNext_v643_smoke`
- sampled files:
  - `20230320_fbd5c8b.parquet`
  - `20230321_fbd5c8b.parquet`
  - `20230322_fbd5c8b.parquet`
  - `20230323_fbd5c8b.parquet`
  - `20230324_fbd5c8b.parquet`

All five baseline Stage 2 outputs show:

- `epiplexity max = 0.0`
- `epiplexity sum = 0.0`
- `is_signal sum = 0`
- `singularity_vector abs sum = 0.0`
- `topo_area_nonzero_rows = 0`
- `topo_energy_pos_rows = 0`

### 3.2 The speed route discovery probes are also all-zero

This is directly established from:

- `37` monthly tiny-symbol probes
- `5` full-day `fbd5c8b` probes
- `5` full-day `b07c2229` probes

All of them remained all-zero under strict V64.3 semantics.

### 3.3 Later gates are not the first point of collapse

The gate-chain diagnosis shows:

- `physics_valid_rows` and `energy_active_rows` stay non-zero at full scale
- `sigma_gate_rows` and `spoof_ok_rows` are non-zero
- but:
  - `epi_pos_rows = 0`
  - `topo_area_rows = 0`
  - `topo_energy_rows = 0`
  - `full_signal_gate_rows = 0`

This proves the chain is collapsing before the final signal gate.

## 4. What is only inferred

The following are not yet proven in Round 0:

- the exact root cause
- whether the primary fault is:
  - an algorithm defect
  - an integration defect
  - a validation defect
  - or a combination of these

## 5. Round 0 verdict

### Verdict

`PASS`

### Meaning

The evidence package is sufficient to establish a critical boundary fact:

`The all-zero phenomenon predates the engineering speed patch.`

Therefore:

- it is not technically correct to treat all-zero as speed-patch-specific evidence
- both routes must remain preserved until root cause is identified

## 6. Consequence for the recursive audit

Round 1 should no longer ask:

- `Did the speed patch break the math core?`

It should instead ask:

- `What shared mechanism can explain why both the baseline route and the speed route produce all-zero outputs?`

## 7. Next-round question

Round 1 will decompose candidate causes and rank them:

1. ETL -> kernel ordering / boundary contract defect
2. topology / rolling integration defect
3. slice informativeness defect
4. validation-framework defect
5. stricter combination of the above
