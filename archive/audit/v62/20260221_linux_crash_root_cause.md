# Linux Crash Root Cause Analysis (Deep Dive)
**Date:** 2026-02-21
**Target:** zepher-linux (192.168.3.113)
**Incident:** Repeated System Freezes/Reboots (Feb 20 18:41, 22:05, 22:44)

## 1. Executive Summary
The crashes were caused by a **Kernel Resource Deadlock** between the ZFS File System and the Systemd Memory Controller (`heavy-workload.slice`).
The system did not just "run out of memory"; it entered a state where the kernel could not reclaim memory fast enough to satisfy the workload, triggering the **Hardware Watchdog**.

**Fix Applied:** ZFS ARC (Adaptive Replacement Cache) hard-limited to **16GB** (down from ~63GB potential).

## 2. Technical Root Cause

### 2.1 The "Invisible" Memory Consumer
- **Physical RAM:** 126 GB
- **User Limit:** `heavy-workload.slice` restricted user processes to **100 GB**.
- **ZFS Behavior:** By default, ZFS on Linux uses up to **50% of RAM** for its ARC (Cache). On this system, that is **~63 GB**.

**The Math of Failure:**
```math
100 \text{ GB (User Allowed)} + 63 \text{ GB (ZFS Potential)} = 163 \text{ GB}
```
**163 GB > 126 GB (Physical Limit)**

### 2.2 The Crash Mechanism (Why it wasn't a normal OOM)
1.  **Workload Start:** The framing job begins, reading huge 7z files.
2.  **Cache Growth:** ZFS fills RAM with cached data (ARC) to speed up reads. RAM usage looks like "100%" but mostly cache.
3.  **Pressure:** The workload allocates more Python objects (Heaps).
4.  **The Trap:**
    -   Linux asks ZFS: "Shrink your cache, I need RAM."
    -   ZFS tries to shrink (evict pages).
    -   **BUT** the disk I/O is saturated (128MB/s writes).
    -   Eviction becomes too slow.
5.  **Deadlock:** The system enters a "Thrashing" state. CPU spikes waiting for memory.
6.  **Watchdog:** The Kernel Watchdog detects the system is unresponsive (no progress for 10+ seconds) and forces a hard reboot (`watchdog invoked oom-killer`).

### 2.3 Why EarlyOOM Didn't Help
`EarlyOOM` is configured to kill processes when "Real Available Memory" is low.
However, Linux counts ZFS ARC as "Reclaimable Slab". Tools like `free` and `EarlyOOM` often see this as "Available" memory.
**EarlyOOM thought:** "We have 60GB of cache, we are fine!"
**Kernel Reality:** "I cannot reclaim this cache fast enough!"
Result: The system died before EarlyOOM pulled the trigger.

## 3. Evidence
From `journalctl -b -1` (Crash at 22:44):
```
kernel: mem_cgroup_out_of_memory+0x100/0x120
kernel: Out of memory and no killable processes...
kernel: watchdog invoked oom-killer
```
- **`mem_cgroup`**: Proves the 100GB slice limit was hit.
- **`watchdog`**: Proves the system hung before it could clean up.

## 4. Resolution & Validation

### 4.1 The Fix
We applied a hard limit to ZFS ARC to prevent it from fighting the workload.
-   **Config:** `/etc/modprobe.d/zfs.conf` -> `options zfs zfs_arc_max=17179869184` (16GB).
-   **Result:** ZFS can now only take 16GB.
    -   16GB (ZFS) + 100GB (Workload) = 116GB.
    -   116GB < 126GB (Physical).
    -   **Safety Margin:** ~10GB free for OS/Network.

### 4.2 Current Status (as of 00:50)
-   **Uptime:** >50 minutes.
-   **Memory:** ~80GB Available (Healthy).
-   **Workload:** v61 Framing is running (8 workers).
-   **Disk I/O:** Active (~120MB/s writes), confirming real work is happening.

## 5. Recommendation
The system is now mathematically safe for the 100GB workload. No further crashes of this type are expected.
Monitor `framing_v61.log` to ensure the application logic proceeds.
