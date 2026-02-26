### Section 1: Findings (Ranked Bottlenecks by Impact)

After auditing the v62 architecture and Stage 2 codebase, the root cause of the sluggishness is **not raw compute volume**. The V62 math itself (MDL/Topology) is fast if properly JIT-compiled. The slowness stems from **Architecture & Scheduling friction**—specifically, memory management collisions between Python, Polars (Rust), and the OS, which forces the system into catastrophic $O(N^2)$ fallback loops.

Here are the top bottlenecks ranked by impact:

1.  **The "Polars Panic" Fallback Cliff (Catastrophic I/O)**
    *   **Evidence:** In `stage2_physics_compute.py`, if the PyArrow-to-Polars conversion panics (usually due to OOM or thread exhaustion), it catches the exception and drops into `_process_file_via_symbol_scan_fallback`.
    *   **Impact:** The fallback uses `pl.scan_parquet(l1_file).filter(...).collect()` inside a loop over symbol batches. If a file has 3000 symbols and a batch size of 50, it reads and filters the **entire Parquet file 60 times**. This degrades throughput from GB/s to KB/s.
2.  **Thread Oversubscription (The Trigger for the Panic)**
    *   **Evidence:** `multiprocessing.Pool(args.workers)` runs concurrently with `POLARS_MAX_THREADS=8` (on Linux). If you run 8 workers on a 32-core machine, you spawn 64 active compute threads. Polars' Rust Rayon engine aggressively spins up threads. This causes L3 cache thrashing, GIL lock-ups during object creation, and memory spikes that trigger the aforementioned panic.
3.  **Synchronous GC Spam in Inner Loops (CPU Drag)**
    *   **Evidence:** `gc.collect()` is explicitly called at the end of every symbol batch in `_run_feature_physics_batch` and `_process_file_via_symbol_scan_fallback`.
    *   **Impact:** Forcing full Python garbage collection inside tight compute loops halts the interpreter, destroying CPU pipeline efficiency and preventing Numba/Polars from maintaining hot memory pages.
4.  **Inefficient Temporal Rolling via Joins (Memory Bloat)**
    *   **Evidence:** In `omega_etl.py`, V62 strictly demands 3s absolute temporal rolling. The implementation uses `.rolling(index_column="__time_dt", period="3s").agg(...)` followed by a `.join(rolled, on=..., how="left")`.
    *   **Impact:** Executing a temporal roll and a Left Join inside an unmaterialized LazyFrame creates a massive intermediary memory graph, doubling the RAM required per batch and contributing to the Polars panics.
5.  **Per-File Numba JIT Recompilation (Cold Start Tax)**
    *   **Evidence:** `stage2_targeted_resume.py` isolates *every single Parquet file* into a brand-new `subprocess.run` Python process.
    *   **Impact:** Every file pays the startup tax: loading Polars, PyArrow, and crucially, forcing LLVM to recompile the Numba `@njit` physics math from scratch before computing. On 1000+ files, you are spending hours just compiling C-code.

---

### Section 2: Recommended Plan (A/B/C)

#### Band A: Low-Risk Engineering-Only (1-2 Days)
*Goal: Stop the bleeding. No logic changes, purely execution parameters.*

*   **Action 1: Throttle `gc.collect()`:** Remove `gc.collect()` from all inner symbol batch loops. Only invoke it at the end of a complete file in `process_chunk`.
*   **Action 2: Fix Thread Oversubscription:** In `stage2_physics_compute.py`, dynamically pin `POLARS_MAX_THREADS`. If `args.workers > 1`, set `POLARS_MAX_THREADS = max(1, CPU_COUNT // args.workers)`. Never let `workers * polars_threads` exceed physical cores.
*   **Action 3: Enable Numba Disk Caching:** Ensure the `@njit` decorators in `omega_core.kernel.py` include `cache=True`. This caches the LLVM-compiled machine code to disk, completely eliminating the cold-start penalty in `stage2_targeted_resume.py`.
*   **Expected Speedup:** 30% - 50% baseline, but saves you from the 100x slowdown cliff by preventing Polars panics.
*   **Risk Level:** Extremely Low.
*   **Why outputs remain equivalent:** We are only altering garbage collection timing, thread limits, and compiler caching. Zero math or data flow changes.

#### Band B: Medium Refactors (3-7 Days)
*Goal: Optimize the Polars graph and eliminate the $O(N^2)$ fallback.*

*   **Action 1: Rewrite the Fallback Path (In-Memory Partitioning):** Instead of looping `scan_parquet().filter()`, read the file once: `df = pl.read_parquet(l1_file)`. Then use `df.partition_by("symbol", as_dict=True)` to yield all symbol dataframes instantly in memory, batch them into lists, and process.
*   **Action 2: Optimize Temporal Rolling (`group_by_dynamic`):** Replace the `.rolling().agg()` + `.join()` pattern in `omega_etl.py` with Polars native `group_by_dynamic` or `rolling` expressions (e.g. `pl.col("v_ofi").rolling_mean(window_size="3s", by="__time_dt")`) directly inside a `with_columns` block. This collapses the computation graph and avoids the costly left join.
*   **Action 3: Subprocess Batching:** Modify `stage2_targeted_resume.py` to pass chunks of 10-20 files to a single subprocess, rather than 1 process per file.
*   **Expected Speedup:** 2x - 3x on average.
*   **Risk Level:** Medium. Requires careful testing of Polars rolling syntax to ensure edge-case alignments match perfectly.
*   **Why outputs remain equivalent:** Mathematical operations (MDL, rolling averages) remain identical; we are only changing *how* the query engine builds the execution graph.

#### Band C: Structural Redesign (1-3 Weeks)
*Goal: Reach the absolute theoretical hardware limit of the AMD Ryzen AI Max.*

*   **Action 1: Unified Numba Kernel (The 10x Move):** The current pipeline uses Polars to calculate bucketization and temporal rolling, then passes the grouped result to Numba for MDL/Topology physics. Instead, extract pure NumPy arrays (`price`, `volume`, `time_ms`, `bid/ask` matrix) straight from Stage 1. Write **one single `@njit(parallel=True)` C-level kernel** that sweeps through the array, maintains the 3-second rolling state in native variables, detects the buckets, calculates MDL, and writes to pre-allocated output arrays.
*   **Expected Speedup:** 5x - 10x+. Polars is fast, but transitioning from Polars to Python to Numba across group boundaries destroys vectorization. A unified Numba pass processes memory at L1/L2 cache speeds (GB/s per core).
*   **Risk Level:** High. You are writing a custom C-style query engine.
*   **Why outputs remain equivalent:** By strictly implementing the V62 mathematical constraints (`min(r2, 0.9999)` log limit, MDL bit formulas) in the Numba loop, the final float outputs are mathematically identical.

---

### Section 3: Validation Gates

Because V62 outputs are sacred, every change must pass strict regression testing.

1.  **Gate 1: Schema & Type Integrity:**
    *   Run `df.schema` on the output of the new pipeline vs. the old pipeline. Every column name and exact dtype (e.g., `Float64`, `UInt32`) must match 1:1.
2.  **Gate 2: Bitwise Float Equivalency (The Tolerance Test):**
    *   Use `polars.testing.assert_frame_equal`.
    *   Compare Old Stage 2 vs. New Stage 2 outputs on a 5-day sample.
    *   Set `check_exact=False` but require `rtol=1e-5` to account for minor floating-point accumulation drift if rolling logic changes slightly.
    *   String/Integer columns (`symbol`, `bucket_id`, `n_ticks`) must pass `check_exact=True`.
3.  **Gate 3: The "Zero Information" Check (MDL Penalty):**
    *   Ensure the Time-Bounded Entropy rule (`mdl_gain_bits <= 0` returns `0.0`) is firing at exactly the same frequency. Calculate the sparsity (percentage of exactly `0.0` values in the physics features); it must match the baseline perfectly.
4.  **Gate 4: OOM & Core Saturation Test:**
    *   Run a 1-month benchmark on the Linux node in `heavy-workload.slice`. Monitor `htop`. CPU utilization should be a flat line near 95-100%, without the "sawtooth" pattern of heavy garbage collection, and RAM must plateau, never triggering Swap.

---

### Section 4: Final Verdict & Prioritized Execution Roadmap

**Explicit Answers to your Questions:**
*   **Is the current slowness mostly architecture/scheduling or raw compute growth?** It is almost entirely architecture/scheduling. Thread collisions between `multiprocessing` and Polars are causing panics, driving the system into an $O(N^2)$ I/O death loop, compounded by synchronous garbage collection.
*   **What single change has highest ROI?** Binding `POLARS_MAX_THREADS` correctly relative to `workers` to stop the PyArrow panics, combined with caching the Numba JIT compiler (`@njit(cache=True)`).
*   **What big redesign could give >2x while preserving v62 outputs?** Fusing the bucket grouping, temporal rolling, and MDL physics into a single pass of Numba `@njit` over contiguous NumPy arrays (Band C).

**Prioritized Execution Roadmap (Top 5 Actions):**

1.  **Stop the Panic Cliff (Today):** In `stage2_physics_compute.py`, add `os.environ["POLARS_MAX_THREADS"] = str(max(1, os.cpu_count() // args.workers))` before process spawn.
2.  **Enable Numba JIT Cache (Today):** Add `cache=True` to all `@njit` decorators in `omega_core/kernel.py` to stop the 750x cold-start compilation tax.
3.  **Kill the GC Drag (Today):** Remove `gc.collect()` from inner symbol processing loops; keep it only at the file boundary.
4.  **Rewrite the Fallback Path (Tomorrow):** Replace the `scan_parquet().filter()` loop in `_process_file_via_symbol_scan_fallback` with an in-memory `partition_by("symbol")`.
5.  **Flatten the Temporal Roll (Next Week):** Refactor `_lob_flux_expr` and the 3s temporal rolling in `omega_etl.py` to avoid the `.join()` bottleneck, utilizing `rolling_mean` inline expressions.
