# Track: Full Pipeline Optimization

## 1. Context & Objective
The OMEGA v5.0 pipeline was hitting a "Small File" I/O bottleneck on NTFS SSDs during the framing stage (21k files/day). The goal was to reach sub-90s/day framing speed while maintaining "Zero Crash" (no 死机) stability on the Ryzen AI Max+ Pro hardware.

## 2. Technical Strategy
- **RAM Disk Staging:** Use ImDisk to create a dynamic NTFS volume for 7z extraction, bypassing SSD metadata journaling.
- **Ryzen Core Balancing:** Optimized worker count to 1.25x physical cores (40 workers) to maximize L3 cache hits.
- **IPC Reduction:** Implemented symbol chunking to reduce the overhead of managing 7,000+ tasks per day.

## 3. Resource Matrix

| Stage | Path | Worker Strategy | Goal |
| :--- | :--- | :--- | :--- |
| **Framing** | `R:/Omega_stage` | 40 Workers (1.25x) | <90s/day |
| **Training** | `D:/Omega_train_tmp` | 30 Workers (0.95x) | Max RAM for Models |
| **Backtest** | `R:/Omega_backtest` | 28 Workers (0.85x) | High-speed Tracing |

## 4. Stability Constraints
- **RAM Ceiling:** 2025 archives (~45GB extracted) require a 60GB RAM disk.
- **Pre-flight Cleanup:** `framer.py` must wipe `stage_root` before and after (on success) to prevent disk overflow.
- **Graceful Fallback:** Stage-aware runner switches to SSD if RAM is needed for training tensors.
