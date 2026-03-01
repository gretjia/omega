# OMEGA v5.2 (v52) Before Full Run Notes / Checklist

**Date:** 2026-02-15  
**Run ID / Tag:** `v52-run-20260215-frame02`  
**Pinned Commit:** `4f9c78631428d5fd76b6e95e5f4bf01e3571ab3b` (git short: `4f9c786`)

> 注：`v52-run-20260215-frame01` 在 Linux 上出现 “第二个 archive 卡死” 的现象（与 `fork` + Polars runtime 线程相关）。
> `frame02` 通过将 framing 的 `ProcessPoolExecutor` 改为 **spawn + 全 run 复用同一个 pool** 修复该问题，并已重新完成 smoke gate 后开跑全量。

本文件用于记录 **v52 全量开跑前** 必须锁定的口径、分工、产物路径、smoke gate、以及多机并行 framing/training/backtest 的执行与质量保障策略。目标是在 **提速** 的同时 **不降低数据处理质量**，并尽量避免“跑到一半发现口径不一致导致重做”。

---

## 0. 不可妥协原则（v52 运行纪律）

1. **全链路必须 pin 到同一个 git tag/commit。**
   - Worker 端跑 framing 的工作区必须是：`git checkout v52-run-20260215-frame02`
   - **运行中禁止 `git pull` / 修改代码**（避免产物混入不同逻辑版本）。
2. **Data 不进 Git。**
   - raw `.7z`、frames `.parquet`、model artifacts 一律不提交。
   - 只提交：代码、配置（硬件 profile）、manifest/shard 清单、audit 文档。
3. **先 smoke test，再全量。**
   - framing smoke + compat gate +（至少一台机器）train/backtest smoke 跑通，确认字段/口径/链路可用后，才允许并行全量 framing。

---

## 1. 代码与依赖（Source of Truth）

### 1.1 Git Controller/Worker 架构

- **Mac 是控制塔（authority）**：负责生成/提交 shards、tag、audit 文档。
- **Windows1 / Linux 是执行节点（read-only workers）**：只 `fetch/checkout`，不 push。
- Worker 获取代码不需要 VPN、不需要传 raw data：
  - `origin = git://192.168.3.93/Omega_vNext.git`
  - 只用于 LAN 内可信环境（`git://` 无鉴权）。

### 1.2 本次全量 framing 的 pin 点

- Tag: `v52-run-20260215-frame02`
- Commit: `4f9c78631428d5fd76b6e95e5f4bf01e3571ab3b`

**重要：** framing 输出文件名包含 git short（例如 `20230104_4f9c786.parquet`）。后续所有质量检查/进度统计都应 **只统计 `*_4f9c786*`**，避免把旧 smoke hash 的 `.done` 混进去。

---

## 2. Shards / Manifest（并行 framing 的核心保障）

本次采用 shard 清单驱动的 framing，确保两台机器处理的 `.7z` **互斥且覆盖全集**，避免重复劳动与覆盖写。

仓库内文件（已提交）：

- `audit/runtime/v52/archive_manifest_7z.txt`：全量 `.7z` 清单（总计 751）
- `audit/runtime/v52/shard_windows1.txt`：Windows1 shard（358）
- `audit/runtime/v52/shard_linux.txt`：Linux shard（393）

规则说明：

- shard 文件行内为 `.7z` 相对路径（相对 `storage.source_root`），跨 OS 可读（允许 `/`）。
- 两 shard **不重叠**、合并后覆盖全 manifest。

---

## 3. 两台机器 framing 配置（必须写清楚产物路径）

### 3.1 Windows1（PowerShell 优先）

- 硬件配置文件：`configs/hardware/windows1.yaml`
- RAW root：`E:/data/level2`
- STAGE root：`D:/Omega_frames/v52/stage_windows1`
- FRAMES 输出：`D:/Omega_frames/v52/frames/host=windows1`
- framing workers：`28`

产物：

- frames：`D:\Omega_frames\v52\frames\host=windows1\YYYYMMDD_4f9c786.parquet`
- 进度标记：同目录下 `YYYYMMDD_4f9c786.parquet.done`、`*.meta.json`
- 运行日志：`D:\work\Omega_vNext\audit\_pipeline_frame.log`
- PID 文件：`D:\work\Omega_vNext\artifacts\runtime\v52\frame_windows1.pid`

### 3.2 Linux1

- 硬件配置文件：`configs/hardware/linux.yaml`
- RAW root：`/omega_pool/raw_7z_archives`
- STAGE root：`/home/zepher/Omega_frames/v52/stage_linux`（本机 NVMe `/home`）
- FRAMES 输出：`/omega_pool/parquet_data/v52/frames/host=linux1`
- framing workers：`28`

产物：

- frames：`/omega_pool/parquet_data/v52/frames/host=linux1/YYYYMMDD_4f9c786.parquet`
- 进度标记：同目录下 `YYYYMMDD_4f9c786.parquet.done`、`*.meta.json`
- 运行日志：`/home/zepher/work/Omega_vNext/audit/_pipeline_frame.log`
- PID 文件：`/home/zepher/work/Omega_vNext/artifacts/runtime/v52/frame_linux1.pid`

---

## 4. Smoke Test Gate（全量开跑前必须通过）

### 4.1 framing smoke（两机都要过）

- smoke archive 列表：`audit/runtime/v52/smoke_archive_list.txt`
  - 当前 smoke 使用：`2023/202301/20230103.7z`

通过标准（v52 framing）：

- Windows1 与 Linux 对同一 `.7z` 的 framing 输出行数一致（本次 smoke 行数约 `179,600`，两机一致）。
- `tools/check_frame_train_backtest_compat.py` 在 smoke 产物上通过：
  - required columns / schema OK
  - `OmegaTrainerV3._prepare_frames` 可跑通
  - `close > 0` 等关键 sanity OK

### 4.2 全链路 smoke（至少 1 台机器）

在 Windows1 完成（用于验证：frames -> training -> backtest 的链路可用）：

- 训练：`parallel_trainer/run_parallel_v31.py`（基于 file-list）
- 回测：`parallel_trainer/run_parallel_backtest_v31.py --allow-audit-failed`
  - 小样本 DoD 指标不通过是预期的（样本太小），但链路必须可用、字段必须齐全。

---

## 5. 正式 framing（两机并行执行方式）

### 5.1 Worker 端 git 锁定

Windows1 / Linux 都必须：

1. `git fetch --tags`
2. `git checkout v52-run-20260215-frame02`
3. 确认 `git rev-parse HEAD` == `4f9c786...`

### 5.2 正式 framing 命令

Linux（示例）：

```bash
cd /home/zepher/work/Omega_vNext
python3 pipeline_runner.py \
  --stage frame \
  --config configs/hardware/linux.yaml \
  --archive-list audit/runtime/v52/shard_linux.txt
```

Windows1（建议 PowerShell，且使用绝对路径避免 Start-Process 工作目录问题）：

```powershell
cd D:\work\Omega_vNext
C:\Python314\python.exe -u D:\work\Omega_vNext\pipeline_runner.py `
  --stage frame `
  --config D:\work\Omega_vNext\configs\hardware\windows1.yaml `
  --archive-list D:\work\Omega_vNext\audit\runtime\v52\shard_windows1.txt
```

**如果是通过 SSH 远程启动（无人在 Windows 前台开终端）：建议用 Task Scheduler 启动**，避免 OpenSSH 会话关闭后清理子进程导致 framing 被杀。

Task Scheduler（PowerShell）示例：

```powershell
$task = "Omega_v52_frame02"
$action = New-ScheduledTaskAction `
  -Execute "C:\Python314\python.exe" `
  -Argument "-u D:\work\Omega_vNext\pipeline_runner.py --stage frame --config D:\work\Omega_vNext\configs\hardware\windows1.yaml --archive-list D:\work\Omega_vNext\audit\runtime\v52\shard_windows1.txt" `
  -WorkingDirectory "D:\work\Omega_vNext"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 7)
Register-ScheduledTask -TaskName $task -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
Start-ScheduledTask -TaskName $task

# 查看状态
Get-ScheduledTask -TaskName $task | Select TaskName,State
Get-ScheduledTaskInfo -TaskName $task | Select LastRunTime,LastTaskResult
```

---

## 6. 监控与进度统计（必须可审计、可复跑）

### 6.1 进度以 `.done` 为准

- Windows1：
  - `D:\Omega_frames\v52\frames\host=windows1\*_4f9c786.parquet.done`
- Linux1：
  - `/omega_pool/parquet_data/v52/frames/host=linux1/*_4f9c786.parquet.done`

**注意：** 只统计 `*_4f9c786*`，避免把 smoke 产物的 `.done` 混入。

### 6.2 若 framing 异常退出（避免重做/避免脏 staging）

1. 先看 `audit/_pipeline_frame.log` 最后一条 `[Job]` / `[Done]` 对应的 archive。
2. **清理该 archive 的 staging 目录**（避免复用半解压残留导致口径污染）。
3. 确认 output 目录里没有同名 `YYYYMMDD_4f9c786.parquet`（或先移走），再重跑。

---

## 7. framing 后的合并与下游（training/backtest 的并行策略）

### 7.1 framing 合并（逻辑层面）

- 两台机器输出在不同 `host=...` 子目录，不会互相覆盖。
- 训练/回测只需要一个“files list/manifest”：
  - 以 `*_4f9c786.parquet` 为准，收集两端路径列表，排序去重后生成 `train_files.txt` / `backtest_files.txt`。

### 7.2 training 是否可两机拆分？

**不建议把 training 拆成两台机器并行训练再合并模型。**

理由（质量优先）：

- 当前训练产物是单个 policy/checkpoint（含 scaler + model + feature cols + cfg），跨机器合并不可控，容易产生不可复现的口径差异。

提速建议（不降质）：

- framing 进行中即可开始 training（用已产出的前 N 天 frames 做早期基线训练），等 framing 完整后再做一次全量训练。

### 7.3 backtest 是否可两机拆分？

**可以拆分，但需要 shard file-list + 合并结果。**（backtest 本身更难，需要更严格的审计）

策略：

1. 固定同一个 `checkpoint_rows_*.pkl`（同一份 policy）。
2. 将 backtest 的 files list 按日期或 hash 分成两份（Windows/Linux 各跑一份）。
3. 两台机器分别输出 `backtest_status.json` / `backtest_state.json` / summary（或我们补一个 merge 工具）。
4. 合并方式：按 rows/trades 进行加权汇总（或以 per-file 结果再聚合）。

---

## 8. 当前开跑状态（用于对齐“是否真的在跑”）

判定标准：

- `audit/_pipeline_frame.log` 的 `LastWriteTime` 持续更新
- `.done` 文件数量持续增长
- PID 文件对应进程仍存在

如果风扇没声音，最常见原因是：

- 当前阶段 I/O/解压或串行扫描占主导，CPU 不会持续满载；
- 或者进程已退出（此时 `log mtime` 不再更新，`.done` 不增长）。

---

## 9. 2026-02-16 补跑与完成态结论（最新）

### 9.1 本次补跑目标与结果

- 目标：修复 quarantine 损坏 `.7z` 导致的 framing 缺口（2025-12-26 / 2025-12-29 / 2025-12-31）。
- 处理：
  - Windows1 以同日非 quarantine 原包覆盖 `quarantine/` 中损坏包并 `7z t` 复检通过。
  - Linux1 同步修复包到 `/omega_pool/raw_7z_archives/2025/202512/quarantine/` 并 `7z t` 通过。
  - 两机按 `--archive-list` 做最小补跑，不重跑全量。
- 结果：
  - Windows1：`Processed 1/1 archives`，`*_4f9c786.parquet.done = 359`
  - Linux1：`Processed 2/2 archives`，`*_4f9c786.parquet.done = 392`
  - 对照 shard 期望：Windows `358 -> 0 missing`，Linux `392 -> 0 missing`

### 9.2 当前运行态（不是 smoke）

- 两机当前执行的是 **正式 framing 的缺口补跑**（`Smoke: False`）。
- 相关任务/进程均已结束：
  - Windows 计划任务状态 `Ready`
  - Linux 无 `pipeline_runner.py --stage frame` 活跃进程

### 9.3 现阶段是否可进入下一阶段

- 结论：**可以**。以 `4f9c786` 为口径的 framing shard 已齐全，可进入训练基线与云端同步准备。
- 建议顺序（降低重做风险）：
  1. 先做一次“frames 清单快照”与去重校验（两 host 合并 file-list，固定 run_meta）。
  2. 用 30-60 交易日先跑一轮训练基线（本地或 Vertex smoke）验证 DoD 口径。
  3. 再开启全量训练；backtest 放到训练后、使用同一 checkpoint 做分片并行。
