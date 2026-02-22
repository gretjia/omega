# Handover: Stage 1 Base Lake Dual-Node Deadlock

Date: 2026-02-22 17:23:04 +0800
Author: Gemini (Architect)
Context: V62 Two-Stage Pipeline Deployment (Stage 1)

## [UPDATE] ROOT CAUSE DIAGNOSIS

1. **Windows Silent Crash:** Windows Event Viewer confirms `python.exe` suffered a hard OS-level crash (Exception Code `0xc0000005` - Memory Access Violation / Segfault) originating inside `_polars_runtime.pyd`. This occurred *after* 7z successfully extracted CSVs into `d:\tmp\framing\`. Polars is natively crashing on Windows when trying to ingest these massive CSVs.
2. **Linux ZFS Deadlock:** The Linux node is entirely unresponsive to SSH commands (`exit code 255`). The heavy ZFS + 4TB NVMe write queue has completely locked the OS kernel. This requires a hard physical reboot.

## 1. Linux Node Status (192.168.3.113)

* **Assigned Load:** Shards 0, 1, 2 (75% of raw data).
* **Current State:** 🚨 **CRITICAL ZFS/NVMe I/O DEADLOCK** (Unresponsive to SSH)
* **Symptoms:** 3 overlapping `stage1_` processes trapped in **`D` state (Uninterruptible Sleep)**.
* **Next Agent Action Required:**
    1. Wait for User to hard reboot (`sudo reboot -f`).
    2. Rewrite `stage1_linux_base_etl.py` to use a true `tmpfs` RAM disk for extracting chunks, and limit to max 2 workers to prevent ZFS queue explosion.

## 2. Windows Node Status (192.168.3.112)

* **Assigned Load:** Shard 3 (25% of raw data).
* **Current State:** ❌ **POLARS ACCESS VIOLATION (0xc0000005)**
* **Symptoms:** `d:\tmp\framing` contains extracted CSVs, but no Parquets generated. Windows Event Log shows `_polars_runtime.pyd` segfaults.
* **Next Agent Action Required:**
    1. Polars memory mapping (`streaming=True` or `low_memory=True`) is likely triggering a segfault on Windows 314 architecture.
    2. We must modify `stage1_windows_base_etl.py` to disable Polars multi-threading (`POLARS_MAX_THREADS=1`) or chunk the CSV reads explicitly, or downgrade tracking version of Polars on Windows.
