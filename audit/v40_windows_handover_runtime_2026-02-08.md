# v40 Windows AI Handover Runtime Manual (Stage/Resume/Logging)

更新时间：2026-02-09  
适用主干：`omega_v3_core/*`（v40 升级阶段）  
适用硬件：Windows 主机 `AMD AI Max 395 + 128GB unified memory`

---

## 1. 目标

本手册用于让 Windows 侧 AI coder 在掉线/重连/换班情况下，稳定执行 v40 的：

1. `frame`（L2 原始压缩包 -> Parquet frame）
2. `train`（并行训练 + checkpoint）
3. `backtest`（并行回测 + 物理审计）

并保证：

1. 日志可追踪
2. 状态可观察
3. 可断点续作
4. 对 Mac 侧可远程监控
5. 训练/回测数据集严格分割（默认防重叠）

---

## 2. 唯一入口（Windows）

统一使用：

- `jobs/windows_v40/start_v40_pipeline_win.ps1`
- `jobs/windows_v40/run_v40_train_backtest_win.ps1`（一键全量 train+backtest）
- `jobs/windows_v40/run_v40_smoke_win.ps1`（一键真实数据 smoke）

不要分散执行旧脚本，避免日志和状态文件路径漂移。

---

## 3. 运行目录与日志总表（必须统一）

运行根目录（共享盘）：

- `audit/v40_runtime/windows/`

分阶段：

1. frame
- `audit/v40_runtime/windows/frame/frame.log`
- `audit/v40_runtime/windows/frame/frame_status.json`
- `audit/v40_runtime/windows/frame/frame_compat.log`
- `audit/v40_runtime/windows/frame/frame_compat_status.json`

2. train
- `audit/v40_runtime/windows/train/train.log`
- `audit/v40_runtime/windows/train/train_status.json`

3. backtest
- `audit/v40_runtime/windows/backtest/backtest.log`
- `audit/v40_runtime/windows/backtest/backtest_status.json`
- `audit/v40_runtime/windows/backtest/backtest_state.json`

4. manifests
- `audit/v40_runtime/windows/manifests/train_files.txt`
- `audit/v40_runtime/windows/manifests/backtest_files.txt`
- `audit/v40_runtime/windows/manifests/train_manifest_status.json`
- `audit/v40_runtime/windows/manifests/backtest_manifest_status.json`
- `audit/v40_runtime/windows/manifests/split_preflight_status.json`
- `audit/v40_runtime/windows/manifests/split_preflight.log`

5. frame stage 内部断点文件（由 frame 输出目录承载）
- `data/level2_frames_v40_win/_audit_state.jsonl`

---

## 4. Windows 侧标准命令

工作目录：

```powershell
cd D:\Omega_vNext
```

### 4.1 一键 smoke（真实 frame -> train -> backtest）

用途：
1. 在不污染正式 `artifacts/` 的情况下，验证当前代码链路可运行。
2. smoke 会把产物写到本地 `C:/Omega_v40_smoke/run_时间戳/`。

推荐命令：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_smoke_win.ps1 `
  -CondaExe "C:\Users\YOUR_USER\miniforge3\Scripts\conda.exe" `
  -CondaEnv OMEGA
```

常用可选参数：
1. `-FrameYear 2026`（限定年份）
2. `-FrameLimit 1`（默认 1）
3. `-SmokeFiles 3`（默认 3）

---

### 4.2 一键全量 train+backtest（hassle free，推荐下一步）

用途：
1. 基于 `data/level2_frames_v40_win` 直接串行执行 train -> backtest。
2. 自动复用 `start_v40_pipeline_win.ps1` 的兼容性预检、状态日志、断点续作机制。
3. 前提：`frame` 已完成且 `data/level2_frames_v40_win` 可用。

推荐命令（默认 128GB 参数）：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_win.ps1
```

固定运行命令（官方边界，推荐）：

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1
```

该命令固定为：
1. train: `2023,2024`
2. backtest: `2025` + `202601`

数据集分割默认来自 `config.py` `SplitConfig`：
1. train: `train_years=(2023, 2024)`
2. backtest: `test_years=(2025,) + test_year_months=(202601,)`
3. train/backtest manifest 默认强制不重叠（检测到重叠直接失败）
4. train/backtest 前会执行 split preflight（失败即停止，不进入训练）

显式覆盖示例（推荐在关键跑批前写清楚）：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_win.ps1 `
  -TrainYears "2023,2024" `
  -BacktestYears "2025" `
  -BacktestYearMonths "202601"
```

如需强制全新重跑（不续作）：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_win.ps1 -NoResume
```

如遇并发占用较高，建议降档：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_win.ps1 `
  -TrainWorkers 14 `
  -BacktestWorkers 12 `
  -MemoryThreshold 85
```

如尚未完成 frame，请直接执行全流程：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage all
```

---

全流程：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage all
```

说明（默认行为）：

1. frame 默认会启用 `--skip-report`，避免超大数据下在 frame 收尾阶段阻塞后续 train/backtest。
2. train/backtest 前会自动执行 frame 兼容性预检（采样 + `_prepare_frames` smoke）。
3. 如确实需要 frame 报告同轮生成，显式开启：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage frame `
  -FrameGenerateReport `
  -FrameReportPath audit\level2_v3_audit_report.md
```

仅 frame：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage frame
```

仅 train：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage train
```

仅 backtest：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage backtest
```

强制从头（不续作）：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage all -NoResume
```

---

## 5. 内存管理策略（128GB）

默认并行参数（已写入脚本）：

1. `FrameWorkers=22`
2. `TrainWorkers=26`
3. `BacktestWorkers=20`
4. `TrainBatchRows=1000000`
5. `TrainCheckpointRows=2000000`
6. `TrainStageChunkFiles=48`
7. `BacktestStageChunkFiles=48`
8. `MemoryThreshold=88`

当 Windows 主机同时有其它任务（例如 backtest/磁盘 IO 重负载）时，建议降档：

1. 轻度拥塞：`FrameWorkers=18, TrainWorkers=20, BacktestWorkers=16, MemoryThreshold=85`
2. 重度拥塞：`FrameWorkers=14, TrainWorkers=14, BacktestWorkers=10, MemoryThreshold=82`

示例（轻度拥塞）：

```powershell
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage all `
  -FrameWorkers 18 `
  -TrainWorkers 20 `
  -BacktestWorkers 16 `
  -MemoryThreshold 85
```

---

## 6. 掉线后的恢复规则

Windows 意外掉线后，恢复步骤固定如下：

1. 进入项目根目录
2. 先检查日志末尾是否存在异常终止
3. 重新执行同一 `-Stage` 命令（默认即续作）

续作依据：

1. frame：`_audit_state.jsonl`（已完成 archive 会被跳过）
2. train：`artifacts/checkpoint_rows_*.pkl` + `processed_files`
3. backtest：`backtest_state.json`（已处理文件会跳过）

注意：

1. 不要手工删除状态文件，除非明确要全新重跑
2. 如需全新重跑，显式加 `-NoResume`

---

## 7. Mac 侧实时监控（通过共享目录）

在 Mac 上查看三阶段状态汇总：

```bash
python3 /Volumes/desktop-41jidl2/Omega_vNext/tools/v40_runtime_status.py
```

机器可读 JSON：

```bash
python3 /Volumes/desktop-41jidl2/Omega_vNext/tools/v40_runtime_status.py --json
```

如果要看最近日志尾部：

```bash
tail -n 40 /Volumes/desktop-41jidl2/Omega_vNext/audit/v40_runtime/windows/frame/frame.log
tail -n 40 /Volumes/desktop-41jidl2/Omega_vNext/audit/v40_runtime/windows/train/train.log
tail -n 40 /Volumes/desktop-41jidl2/Omega_vNext/audit/v40_runtime/windows/backtest/backtest.log
```

---

## 8. 异常早停与排障触发条件

以下任一条件成立时，应立即排障而不是盲跑：

1. `*_status.json` 超过 10 分钟无更新时间（stale）
2. train 有 `files_done_in_run > 0` 但长期无 `latest_checkpoint`
3. backtest 的 `error_count` 持续增长
4. 日志出现连续 extraction/prediction 异常
5. `split_preflight_status.json` 状态为 `failed`

首选排障动作：

1. 降低 workers
2. 降低 `MemoryThreshold`
3. 只跑单阶段（先定位 frame/train/backtest 中的故障点）
4. 检查 `frame_compat_status.json` 是否失败（列兼容或 smoke 问题）

---

## 9. 交接班最小清单（Windows AI -> Mac AI / 下一个 AI）

交接时必须提供：

1. 当前阶段（frame/train/backtest）
2. 最后更新时间戳（来自 status json）
3. 本轮已完成文件数/剩余文件数
4. 当前 checkpoint 或 state 文件路径
5. 最近一次异常摘要（若有）

推荐附带：

1. `tools/v40_runtime_status.py --json` 输出片段
2. 对应阶段日志最后 30-50 行

---

## 10. 与工程规范的绑定关系

本运行手册遵循以下约束：

1. 不新增生产硬编码阈值（仅允许可配置参数）
2. 内存保护与断点续作优先
3. 日志与状态输出路径固定且可审计
4. v3 主干逻辑保持在 `omega_v3_core/*`，并行脚本仅做执行层增强
5. train/backtest 数据分割由配置+manifest构建统一控制，不允许默认混用
