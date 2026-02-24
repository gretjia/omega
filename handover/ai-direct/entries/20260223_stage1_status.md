> [Superseded 2026-02-24 04:16 +0800] This snapshot incorrectly classified windows as hard-down.
> Use: handover/ai-direct/entries/20260224_041600_omega_vm_windows_connectivity_rca_fix.md

# Handover: Stage 1 Status Check

**Date:** 2026-02-24 (Current Time: 08:25+0800)
**Task:** v62 Stage 1 Base Lake ETL Monitoring

## 1. Linux Node (linux1-lx) - 100.64.97.113
*   **Status:** 🟢 **ACTIVE**
*   **Process:** `tools/stage1_linux_base_etl.py --years 2023,2024,2025,2026 --total-shards 4 --shard 0,1,2`
*   **Progress:**
    *   Completed Files: **491** Parquets (up from 422).
    *   Current Activity: Processing March 2025 data (latest completion: `20250311` at 08:17).
    *   Health: Stable, bypassing ZFS via `/home/zepher/framing_cache`.
*   **Action:** None required; allow to continue.

## 2. Windows Node (windows1-w1) - 100.123.90.25
*   **Status:** 🟡 **IDLE / STALLED**
*   **Connectivity:** 🟢 REACHABLE (Stability probe passed).
*   **Diagnosis:** The node is online, but no `stage1` process is running and no output files have been generated in `D:\Omega_frames\v62_base_l1\host=windows1`. Previous logs are missing or path is incorrect.
*   **Action Required:**
    *   **RESTART REQUIRED:** Manually launch Stage 1 Shard 3 on Windows.
    *   Command: `python tools\stage1_windows_base_etl.py --years 2023,2024,2025,2026 --total-shards 4 --shard 3 --workers 1`
    *   Monitor for initial `.parquet.done` file to confirm start.

## 3. Summary of Data Coverage
*   **Linux (Shards 0, 1, 2):** Actively progressing through 2025. ~75% of total workload.
*   **Windows (Shard 3):** 0% progress. Coverage for Shard 3 is missing.
