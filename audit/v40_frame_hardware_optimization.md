# v40 Frame Stage: Hardware Optimization Analysis

**Date:** 2026-02-10  
**Based on:** Live Runtime Logs (PID 30780) & System Metrics  
**Status:** Active (51% Complete, 367/723 Archives processed in current run)

## 1. Executive Summary

**Conclusion:** The framing task is currently **CPU COMPUTATION BOUND**, not I/O bound.  
**Bottleneck:** 94% of the processing time is spent on CPU tasks (Python Kernel Logic + Decompression). Only ~6% is waiting on Disk I/O.  
**Speed:** ~48.1 archives/hour with 12 workers.

## 2. Quantitative Bottleneck Analysis

Data derived from `frame_status.json` timing totals (normalized):

| Metric | Total Seconds (All Workers) | Share of Time | Interpretation |
| :--- | :--- | :--- | :--- |
| **Kernel Logic (`kernel_sec`)** | **230,964 s** | **74.1%** | **PRIMARY BOTTLENECK.** Parsing CSVs, cleaning data, ensuring data integrity in Python. |
| **Extraction (`extract_sec`)** | **61,750 s** | **19.8%** | **SECONDARY BOTTLENECK.** 7-Zip decompression of large archives. |
| **Disk Write (`write_sec`)** | 15,598 s | 5.0% | Writing Parquet files. Very efficient. |
| **I/O Wait (`io_wait_sec`)** | 3,212 s | 1.0% | Time spent waiting for disk. Negligible. |
| **Copy/Overhead** | ~804 s | 0.1% | Staging overhead. Negligible. |

**Key Insight:** The system waits for the CPU 15x more often than it waits for the Disk.

## 3. Resource Usage Observations

*   **CPU:** The 12 worker processes are heavily utilizing CPU cycles (approx. 39,000 CPU-seconds consumed per worker over ~7.5 hours). This aligns with the "Kernel + Extract" dominance.
*   **Memory:** Working Set is ~350MB per worker. Total for 12 workers is ~4.2GB. This is low and likely not a constraint.
*   **Storage:** The low `io_wait_sec` confirms that the current NVMe/SSD setup is handling the throughput easily. The `io_slots=4` setting is effectively keeping the drives fed without saturating them.

## 4. Optimization Recommendations

### A. Immediate Software/Config Tuning
1.  **Increase Worker Count:** If your CPU usage is not yet hitting 100% on all cores, you can safely increase `FrameWorkers` from `12` to `16` or `20`. The low memory footprint (~4GB total) and low I/O wait suggest there is headroom *if* physical cores are available.
2.  **Profile `kernel.py`:** Since 74% of time is in the kernel, optimizing the CSV parsing logic (e.g., using Polars `scan_csv` more aggressively or optimizing regex/string cleaning) would yield the highest ROI.

### B. Hardware Investment Strategy (If upgrading)
The task is **embarrassingly parallel** (file-level independence). Scaling is nearly linear with core count until disk saturation.

*   **Priority 1: CPU Core Count (Best Investment)**
    *   **Recommendation:** AMD Threadripper (7000 series) or EPYC / Intel Xeon w/ high core counts.
    *   **Why:** Moving from 12 cores to 24 cores would nearly double the speed (e.g., ~96 archives/hour), as I/O has plenty of headroom.
*   **Priority 2: CPU IPC (Frequency)**
    *   **Recommendation:** Processors with high boost clocks.
    *   **Why:** Faster cores reduce `kernel_sec` (Python execution time).
*   **Priority 3: Memory Speed**
    *   **Recommendation:** Low latency DDR5.
    *   **Why:** Helps with the constant allocation/deallocation during CSV parsing.
*   **Do NOT Upgrade:** Storage / NVMe.
    *   **Why:** You are currently using <10% of likely I/O capacity. Faster drives will sit idle.

## 5. Summary Advice
**Do not buy faster SSDs.** Buy a CPU with **more cores**.
If your current CPU is not maxed out (check Task Manager for overall utilization), **increase `FrameWorkers` in `start_v40_pipeline_win.ps1` immediately** to utilize existing hardware better.
