# v40 Frame Benchmark Runbook (CPU-First)

日期：2026-02-09  
目标：在不改数学核心与结果质量前提下，为 frame 选择最优并发参数。

## 1) 运行 worker 扫描

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\benchmark_v40_frame_win.ps1 `
  -Limit 800 `
  -Workers "12,16,20,22" `
  -FrameSevenZipThreads 1
```

输出文件：
- `audit/v40_runtime/windows/frame_bench/benchmark_summary.json`
- `audit/v40_runtime/windows/frame_bench/benchmark_summary.csv`
- `audit/v40_runtime/windows/frame_bench/w*.log`

## 2) 选型规则

优先选择：
1. `archives_per_hour` 最大
2. 运行稳定（无异常退出，`success=true`）
3. 在并发回测/共享盘压力下吞吐波动最小

若前两名差距 < 5%，优先较低 worker（更稳）。

## 3) 用最佳参数跑 frame 全量

假设最佳为 `FrameWorkers=20`：

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage frame `
  -FrameWorkers 20 `
  -FrameSevenZipThreads 1 `
  -FrameOutputDir data/level2_frames_v40_win `
  -FrameStageDir C:/Omega_level2_stage
```

## 4) 衔接 train/backtest（固定分割）

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1
```

固定策略：
- Train: `2023,2024`
- Backtest: `2025` + `202601`

## 5) 结果核对

必查状态文件：
- `audit/v40_runtime/windows/frame/frame_status.json`
- `audit/v40_runtime/windows/train/train_status.json`
- `audit/v40_runtime/windows/backtest/backtest_status.json`

通过标准：
- frame 完成且无异常中断
- split preflight 通过，manifest overlap = 0
- train/backtest 正常完成并写入终态

