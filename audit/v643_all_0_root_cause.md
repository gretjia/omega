# V64.3 All-Zero Recursive Audit - Root Cause Conclusion

Date: 2026-03-07  
Author: Codex  
Mission: `V64 All-Zero Root-Cause Recursive Audit`  
Status: root cause identified

## 1. Root cause statement

`The all-zero phenomenon is caused by an ETL -> kernel interface defect: build_l2_features_from_l1() emits Stage 2 frames in a symbol-interleaved order, while apply_recursive_physics() assumes symbol/date-contiguous row order for its boundary-aware rolling state.`

Because the emitted rows are interleaved:

- `dist_to_boundary` is repeatedly reset by adjacent symbol changes
- rolling windows for topology and compression never warm up correctly
- `topo_area`, `topo_energy`, `epiplexity`, `is_signal`, and `singularity_vector` collapse to zero

## 2. Defect class

### Primary class

`integration defect`

The canonical math formulas are not, by themselves, the first failed object here. The failure is in the contract between:

- Stage 2 feature aggregation output ordering
- and kernel rolling-state assumptions

### Secondary class

`validation defect`

The smoke framework historically accepted zero-signal slices and therefore failed to surface the integration defect early.

## 3. Why this is sufficient to explain the failure

The critical causal chain is:

1. the kernel rolling logic depends on contiguous same-symbol trajectories
2. `build_l2_features_from_l1()` outputs rows in a highly interleaved `(symbol, bucket_id)` order
3. `apply_recursive_physics()` computes `is_boundary` and `dist_to_boundary` from adjacent row transitions in that interleaved order
4. rolling topology and rolling compression therefore never see the intended same-symbol window history
5. the canonical downstream signal chain remains zero

This single interface failure explains why:

- the baseline route is all-zero
- the speed route is also all-zero
- later gates are not the first point of collapse
- topology and compression both disappear together

## 4. Core proof

### 4.1 Kernel requires contiguous same-symbol segments

In [kernel.py](/home/zephryj/projects/omega/omega_core/kernel.py), the rolling chain builds boundaries from adjacent row transitions:

- `is_boundary` is derived from row-to-row changes in `symbol` or `date`
- `dist_to_boundary` is then used to gate rolling warm-up

Relevant code region:

- [kernel.py:129](/home/zephryj/projects/omega/omega_core/kernel.py:129)

This is a row-order-sensitive contract.

### 4.2 Stage2 streaming path explicitly assumes sorted Stage1 input

In [stage2_physics_compute.py](/home/zephryj/projects/omega/tools/stage2_physics_compute.py), the iterator states:

> `Assumes Stage1 output is sorted by symbol/date/time.`

Relevant code region:

- [stage2_physics_compute.py:442](/home/zephryj/projects/omega/tools/stage2_physics_compute.py:442)

### 4.3 Stage1 input is indeed symbol-contiguous

Direct checks on raw Stage1 files show long same-symbol runs:

- `20250725_b07c2229.parquet`
  - sampled `200000` rows
  - `transitions = 8`
  - `max_consecutive_same_symbol = 67582`
- `20230320_fbd5c8b.parquet`
  - sampled `200000` rows
  - `transitions = 19`
  - `max_consecutive_same_symbol = 36266`

Therefore the raw Stage1 files do satisfy the expected upstream symbol ordering at the point they are read.

### 4.4 The defect appears inside Stage 2 feature aggregation, before kernel rolling

A minimal read-only reproduction was executed on `linux1-lx`:

- input:
  - the first `3` complete symbol blocks from `20250725_b07c2229.parquet`
- upstream condition:
  - input symbols were contiguous:
    - `000001.SZ`
    - `000002.SZ`
    - `000004.SZ`

Then `build_l2_features_from_l1()` was run directly on that already symbol-contiguous input.

Observed output:

- `output_rows = 116`
- `output_unique_symbols = 3`
- `output_transitions = 77`
- `output_max_consecutive_same_symbol = 5`

First output symbols were already interleaved, e.g.:

- `000004.SZ`
- `000004.SZ`
- `000001.SZ`
- `000002.SZ`
- `000001.SZ`
- `000004.SZ`
- ...

This is the decisive evidence:

`The same-symbol continuity is broken inside build_l2_features_from_l1() before the kernel rolling physics is applied.`

### 4.5 Once the interleaved Stage 2 order reaches the kernel, rolling state collapses

Observed L2 full-day outputs show:

- `max_consecutive_same_symbol <= 5`
- `epiplexity = 0`
- `topo_area = 0`
- `topo_energy = 0`
- `is_signal = 0`
- `singularity_vector = 0`

This is consistent with a boundary-aware rolling chain that never accumulates the intended same-symbol window history.

## 5. Why alternative explanations are weaker

### Alternative: the engineering speed patch introduced the defect

Rejected because:

- the pre-speed baseline smoke is already all-zero
- therefore the phenomenon predates the speed patch

### Alternative: the topology fast path alone is broken

Rejected as primary cause because:

- the same all-zero behavior already existed in the baseline route
- the decisive break occurs earlier, at the ordering contract that feeds the kernel

### Alternative: the slices are simply uninformative

Rejected as primary cause because:

- even where reference same-symbol geometry is non-zero
- the stored topology chain is still zero
- this points to construction/integration failure, not only slice weakness

## 6. Final conclusion

### Root cause

`build_l2_features_from_l1()` emits Stage 2 frames in a symbol-interleaved order, while apply_recursive_physics() requires symbol/date-contiguous ordering to compute boundary-aware rolling topology and compression.`

### Practical interpretation

The algorithm is not being evaluated on the intended trajectories.

Instead:

- ETL creates bucketed rows
- those rows are emitted in an order incompatible with the kernel's rolling assumptions
- the kernel silently interprets that order as real trajectory boundaries
- the canonical signal chain collapses to zero

### Severity

`critical defect`

Because if the canonical Stage 2 math is fed with the wrong row-order contract, the entire signal engine can appear inert even when meaningful same-symbol rolling structure exists in the underlying data.
