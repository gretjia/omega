# OMEGA Distributed Training Guide

> Last updated: 2026-02-08 (legacy distributed note, v40 unified pipeline pointer)

> Status: This guide documents historical split-machine flow (`windows_2023` + `mac_2024`).
> For current v40 execution, prefer unified pipeline:
> `jobs/windows_v40/start_v40_pipeline_win.ps1`
> and `jobs/windows_v40/README.md`.

## Overview
This guide describes how to run the distributed training workload on two air-gapped machines:
1. **Windows PC** (AMD Ryzen, 128G RAM) -> Processes **2023** Data.
2. **Mac Studio** (M4 Max, 32G RAM) -> Processes **2024** Data.

## 1. Windows PC Setup (2023 Workload)
**Location**: `d:\Omega_vNext`

1. Open Terminal/PowerShell.
2. Navigate to `jobs/windows_2023/`.
3. Run `start_train_win.bat`.
   - **Safety**: Script automatically kills idle python processes before starting.
   - **Memory**: Monitors RAM usage; auto-pauses if > 85% used.
   - **Output**: Results saved to `d:\Omega_vNext\data\level2_frames_win2023`.

## 2. Mac Studio Setup (2024 Workload)
**Preparation**:
1. Copy the entire `Omega_vNext` folder from Windows to Mac via external SSD.
2. Ensure Python 3.10+ and dependencies (`polars`, `numpy`, `psutil`) are installed on Mac.

**Execution**:
1. Open Terminal.
2. Navigate to `Omega_vNext/jobs/mac_2024/`.
3. Run `chmod +x start_train_mac.sh`.
4. Run `./start_train_mac.sh`.
   - **Config**: Optimized for 32G Unified Memory (Workers=6).
   - **Output**: Results saved to `Omega_vNext/data/level2_frames_mac2024`.

## 3. Merge Results (Post-Training)
Once both machines finish:
1. Copy the folder `data/level2_frames_mac2024` from Mac back to Windows `d:\Omega_vNext\data\`.
2. You should now have:
   - `data/level2_frames_win2023` (from Windows)
   - `data/level2_frames_mac2024` (from Mac)
3. The Audit/Training pipeline can now read both directories (via glob patterns) for the final model training.
