---
entry_id: 20260227_015810_stage2_dual_host_progress_update
task_id: TASK-STAGE2-PERF-OPTIMIZATION
timestamp_local: 2026-02-27 09:58:10 +0800
operator: Gemini CLI
role: agent
branch: perf/stage2-speedup-v62
tags: [stage2, progress, linux1-lx, windows1-w1, fallback-success]
related_files:
  - handover/ai-direct/LATEST.md
---

## 1. Context & Goal
The user requested a status check on the dual-node Stage 2 physics computation following the performance optimizations and bug fixes (OOM killer resolution on Linux, Polars `ParseIntError` and allocator failure mitigations on Windows).

## 2. Technical Decisions & Actions Taken
Connected to both `linux1-lx` and `windows1-w1` to check the progress of `.parquet.done` files against total `.parquet` files and reviewed the latest runner logs.

### A. Linux Node (`linux1-lx`) Progress
- **Status:** Healthy and processing at high speed.
- **Progress:** 417 / 552 files completed (up from 207 during the stall).
- **Performance:** Processing 3.2GB (~1.1M rows) files in approximately 118 - 122 seconds per file. No signs of OOM or memory stalls.

### B. Windows Node (`windows1-w1`) Progress
- **Status:** Healthy. The pathologically slow/crashing symbol fallback mechanism is actively working.
- **Progress:** 180 / 191 files completed (up from 179).
- **Details:** The node successfully chewed through the pathological file `20250725_b07c2229.parquet` (which previously caused allocator panics due to having only 2 distinct time values for 223k+ rows). It utilized the safe fallback mechanism, completing 271,571 rows in ~12,370 seconds (approx. 3.4 hours). It has now moved on to the next file `20250828_b07c2229.parquet`.

## 3. Current State & Next Steps
- **Result:** Both nodes are actively processing without crashing. The optimizations and crash guards applied in `perf/stage2-speedup-v62` are proving effective in production.
- **Next Action:** Continue monitoring until queues are fully depleted. Once complete, proceed to Stage 3 / feature validation.
