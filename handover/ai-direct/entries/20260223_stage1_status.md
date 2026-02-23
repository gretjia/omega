> [Superseded 2026-02-24 04:16 +0800] This snapshot incorrectly classified windows as hard-down.
> Use: handover/ai-direct/entries/20260224_041600_omega_vm_windows_connectivity_rca_fix.md

# Handover: Stage 1 Status Check

**Date:** 2026-02-23 (Current Time: 04:00+ UTC/Local Approx)
**Task:** v62 Stage 1 Base Lake ETL Monitoring

## 1. Linux Node (linux1-lx) - 100.64.97.113
*   **Status:** 🟢 **ACTIVE**
*   **Process:** `tools/stage1_linux_base_etl.py --years 2023,2024,2025,2026 --total-shards 4 --shard 0,1,2`
*   **Progress:**
    *   Completed Files: **422** Parquets.
    *   Current Activity: Processing early 2025 data (latest completion: `20250106` at 03:58).
    *   Health: Stable, bypassing ZFS via `/home/zepher/framing_cache`.
*   **Action:** None required; allow to continue.

## 2. Windows Node (windows1-w1) - 100.123.90.25
*   **Status:** 🔴 **CRITICAL / DOWN**
*   **Connectivity:** Connection timed out (SSH), 100% packet loss (Ping).
*   **Diagnosis:** Likely an OS-level deadlock or hard crash similar to previous "Memory Access Violation" events. This node was assigned Shard 3.
*   **Action Required:**
    *   Manual physical reboot of the Windows machine.
    *   Check Event Viewer for `0xc0000005` errors after reboot.
    *   Resume Stage 1 using `tools/stage1_windows_base_etl.py`.

## 3. Summary of Data Coverage
*   **Linux (Shards 0, 1, 2):** Actively progressing through 2025.
*   **Windows (Shard 3):** Stalled; data coverage for this shard is incomplete.
