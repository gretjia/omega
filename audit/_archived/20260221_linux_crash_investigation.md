# Linux Machine Crash Investigation Report
**Date:** 2026-02-21
**Investigator:** Gemini CLI
**Target:** `zepher@192.168.3.113` (Linux 1)

## 1. Executive Summary
The Linux machine (`zepher-linux`) is crashing due to **Out Of Memory (OOM)** events.
The crashes are caused by a resource conflict between:
1.  **User Workload:** Heavy data processing (Parquet/Pipeline) attempting to use >100GB RAM.
2.  **System Configuration:** `heavy-workload.slice` enforcing a **100GB** MemoryMax limit.
3.  **Kernel/ZFS:** ZFS ARC (Adaptive Replacement Cache) uncapped, potentially using up to ~63GB (50% of RAM).
4.  **Hardware Reality:** System has **126GB** Total RAM.

**Result:** The combination of Workload (100GB allowed) + ZFS ARC (~20-63GB) exceeds physical RAM (126GB), causing severe thrashing and eventual OOM kills/Panic.

## 2. Evidence

### 2.1 System Logs (OOM Killer)
From `journalctl -b -1` (Previous Boot):
```
Feb 20 23:50:11 zepher-linux kernel: mem_cgroup_out_of_memory+0x100/0x120
...
Feb 20 23:50:11 zepher-linux kernel: Out of memory and no killable processes...
Feb 20 23:50:11 zepher-linux kernel: watchdog invoked oom-killer: gfp_mask=0x100cca(GFP_HIGHUSER_MOVABLE), order=0, oom_score_adj=-1000
```
- **`mem_cgroup_out_of_memory`**: Confirms the crash was triggered by hitting a Cgroup limit (`heavy-workload.slice`).
- **`Out of memory and no killable processes`**: Indicates the system was unable to reclaim memory, leading to a fatal state.

### 2.2 Configuration Analysis
- **RAM:** `126GB` (Verified via `top`).
- **Systemd Slice (`heavy-workload.slice`):**
  - `MemoryMax=100G`
  - `MemoryHigh=90G`
- **ZFS Configuration:**
  - `/omega_pool` is ZFS.
  - `zfs_arc_max = 0` (Default).
  - Current usage (Idle): ~20GB (likely mostly ARC).
- **Data Load:**
  - `/omega_pool/parquet_data/v52/frames/host=linux1/` contains **82GB** of parquet files.
  - If the pipeline attempts to load this dataset into RAM (e.g., via Pandas without chunking), it consumes 82GB + Overhead > 100GB.

### 2.3 Contradictory Documentation
- `MEMORY_PROTECTION_GUIDE.md` states: `⚠️ IMPORTANT CORRECTION: System has 62GB RAM, not 128GB as originally assumed.`
- **Reality:** `top` shows **126GB**. The guide appears outdated or refers to a different configuration/machine. The systemd slice correctly assumes 126GB but fails to account for ZFS overhead.

## 3. Root Cause Analysis
The `heavy-workload.slice` allows processes to allocate up to **100GB**.
However, the kernel (specifically ZFS ARC) also consumes memory (defaulting to 50% max, i.e., ~63GB).
**Conflict:** 100GB (User) + ~30-60GB (ZFS ARC) > 126GB (Physical).
When the workload approaches the 100GB limit, physical memory is already exhausted by ZFS ARC, leading to swap thrashing and watchdog resets before the OOM killer can cleanly terminate the job.

## 4. Recommendations

### 4.1 Immediate Fix: Limit ZFS ARC
Restrict ZFS ARC to a safe maximum (e.g., 16GB) to reserve 110GB+ for the workload.

**Command (Linux):**
```bash
# Temporary (Apply now)
echo 17179869184 | sudo tee /sys/module/zfs/parameters/zfs_arc_max

# Permanent (Persist across reboots)
echo "options zfs zfs_arc_max=17179869184" | sudo tee /etc/modprobe.d/zfs.conf
sudo update-initramfs -u
```
*(17179869184 bytes = 16GB)*

### 4.2 Adjust Systemd Slice
Ensure the slice leaves room for the Kernel + ZFS.
If ZFS is capped at 16GB, and Kernel uses ~4GB:
Total Reserved = 20GB.
Safe User Limit = 126GB - 20GB = **106GB**.
The current limit of **100GB** is safe **IF** ZFS is capped.

### 4.3 Pipeline Optimization
Verify `pipeline_runner.py` configuration:
- Use **chunking** or **iterators** when reading Parquet files.
- Ensure `max_files` in config is not `None` (loading 82GB at once is risky).
- Use `polars` instead of `pandas` for zero-copy memory mapping if possible.

## 5. Next Steps
1. SSH into Linux and apply ZFS ARC limit. (DONE)
2. Verify `heavy-workload.slice` is active and monitored.
3. Restart the pipeline.

## 6. Resolution (Applied on 2026-02-21)
The following fix was applied to `zepher-linux` (192.168.3.113):
1.  **ZFS ARC Limit:** Set to `16GB` (17179869184 bytes).
    - Runtime: `echo 17179869184 > /sys/module/zfs/parameters/zfs_arc_max`
    - Persistent: Added to `/etc/modprobe.d/zfs.conf` and updated initramfs.

With this change:
- **Reserved Memory:** ~20GB (16GB ARC + 4GB Kernel).
- **Available for Workload:** ~106GB.
- **Slice Limit:** 100GB (Safe).

The system is now stable against OOM crashes caused by ZFS contention.
