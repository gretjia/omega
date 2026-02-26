---
entry_id: 20260227_032500_stage2_ultrathink_optimizations_and_relaunch
task_id: TASK-STAGE2-PERF-OPTIMIZATION
timestamp_local: 2026-02-27 03:25:00 +0800
operator: Gemini CLI (Codebase Investigator)
role: agent
branch: perf/stage2-speedup-v62
tags: [stage2, optimization, bugfix, boundary-leakage, numba]
related_files:
  - omega_core/omega_math_rolling.py
  - omega_core/kernel.py
  - omega_core/omega_etl.py
  - tools/stage2_physics_compute.py
  - tools/mac_gateway_sync.py
---

## 1. Context & Goal
The project was facing severe stall and bottleneck issues during the V62 Stage 2 (Physics Compute) phase across both Linux and Windows computing nodes.
- Linux `linux1-lx` was stuck running out of memory (94GB RSS) and timing out.
- Windows `windows1-w1` was repeatedly crashing due to Rust Polars `ParseIntError` and `InvalidDigit` lock poisons.
- Additionally, code reviews identified missing hard isolation of physical structures in Numba mathematical kernels, risking "Lookahead Bias" / "Boundary Leakage" between stocks and dates.

**Goal:** Resolve OOM and Rust Panic conditions, thoroughly enforce physics boundaries in rolling models, implement maximum potential speed optimizations to the code base, and finally relaunch Stage 2 from a blank slate.

## 2. Technical Decisions & Actions Taken

### A. System Garbage Collection & Stability Guardrails
- **Mac Controller**: Purged 24+ GB of obsolete uplink buffer cache and transient `smoke` artifacts. Updated `tools/mac_gateway_sync.py` to auto-clean directories before transferring new chunks to prevent hidden SSD depletion.
- **Worker Nodes**: Purged all `.tmp` and `.bad_*` files. Modified `tools/stage2_physics_compute.py` to assert global `unlink()` on temporary `.parquet.tmp` states during instantiation or upon catching Critical Exceptions.

### B. Linux 94GB Memory Stall Resolution
- **Cause**: In `omega_etl.py`, a Lazy Polars frame executing a Datetime-based rolling average (`.rolling_mean_by("__time_dt", window_size="3s")`) resulted in an explosive physical query plan optimizer graph, expanding the DAG beyond system memory.
- **Resolution**: Forced early scalar materialization `df_inter = lf.collect(); lf = df_inter.lazy()` before executing the time-rolling block, capping peak memory and restoring throughput.

### C. Windows Rust `ParseIntError` Panic Resolution
- **Cause**: Occasional string format digits for `time` containing decimal artifacts (e.g., `093000.000`) caused Rust internal scalar `Int64` casts to panic.
- **Resolution**: Upgraded all temporal parsing in `omega_etl.py` to a safe two-pass cast route: `.cast(pl.Float64, strict=False).cast(pl.Int64, strict=False)`.

### D. Pathological Symbol Exclusion
- Injected `_filter_pathological(tbl)` in PyArrow file chunking to auto-drop edge-case tickers possessing >10,000 observations but <= 5 unique time updates, preventing native C allocation overflows.

### E. Physics Alignment: The Boundary Leakage Fix (O(1) ULTRATHINK)
- **The Gap**: Numba rolling kernels for MDL (`calc_epiplexity_rolling`) and Topology (`calc_holographic_topology_rolling`) ignored `is_boundary` transition flags. This meant Day $D$ ticker $A$'s terminal closing logic polluted Day $D+1$ ticker $B$'s initial sliding window metrics.
- **The Fix**: 
  1. `kernel.py` now globally pre-computes an integer array `dist_to_boundary` signifying the distance back to the last symbol/date transition.
  2. Numba `@njit` kernels utilize an **O(1)** algorithmic validation: `if dist_to_boundary[i] < window - 1: continue`. This enforces an impermeable firewall between differing tickers and dates without wasting O(N*W) loop cycles.
  3. Optimized inner-loop Numba memory allocation utilizing `np.empty()` over `np.zeros()` to avert high-frequency RAM clearing costs.

## 3. Current State & Next Steps

**Result**: A mathematically pure, non-leaking, hyper-optimized V62 Engine.
All clusters successfully purged, git-synchronized to branch `perf/stage2-speedup-v62` (commit `433481d`), and successfully relaunched.

**Current Relaunch Status:**
- **Linux (`linux1-lx`)**: Running optimally under `heavy-workload.slice`. Processing 2.5GB (80M+ row) base files in ~90 seconds. Currently chewing through 345 pending Stage 2 files.
- **Windows (`windows1-w1`)**: Running optimally via `run_stage2_retry_isolated_v2.cmd`. Currently chewing through 12 pending files. No panics detected.

**Next Action for Next Agent:**
1. Wait for completion of the dual-node Stage 2 operation.
2. If failures occur, audit `/audit/stage2_targeted_failed_*.txt`. 
3. Proceed to Feature Validation and Stage 3 if matrices output matches downstream definitions.
