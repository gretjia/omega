# Data Lifecycle & Disk Hygiene Guard

**Skill Description:** Defines the architectural rules for temporary data cleanup, artifact retention, and log rotation to prevent multi-node disk exhaustion.

## 1. 原则 (Core Philosophy)
* **中间态用完即毁 (Ephemeral Intermediates)**: 运行过程中的分片 (Shards)、临时合并缓冲文件等，必须在最终产物（如 `base_matrix.parquet`）成功生成并校验通过后，由生成该分片的脚本**自动删除**。
* **最终产物人工/显式收割 (Artifact Retention)**: 阶段性的最终巨型文件（如 Base Matrix、Model、Backtest Results），严禁由底层工作脚本自行清理。必须在确认已上传云端或项目完全结束后，由操作者或统筹脚本进行显式清理。
* **日志防爆机制 (Log Rotation)**: 严禁将高频输出（如每一行的进度打印）无限制地 `nohup > log 2>&1` 长期挂载，更不能让其污染系统的 `/var/log/syslog`。

## 2. 垃圾产生溯源 (Origins of V62 Leftovers)
以下为本次 V62 运行中产生的主要“系统垃圾”及其溯源：

* **`windows1-w1` (Windows 节点)**:
  * `audit\stage3_full_unified\windows1_base_matrix_full_shards`: 重达几 GB 的中间碎文件。由 `forge_base_matrix.py` 生成。
  * `audit\stage3_full_unified\windows1_base_matrix_full.parquet`: 9.35GB 最终产物。由 `forge_base_matrix.py` 生成。
  * `upload_gcs_win.py` 等：手动临时创建的 GCP 诊断脚本。
* **`mac-back` (Mac 节点)**:
  * `~/Downloads/windows1_base_matrix_full.parquet`: 9.35GB 巨型搬运包。由主控机通过 SCP 指令临时下发，用于利用 Mac 软路由上传 GCP。
  * `/tmp/mac_gsutil*.log`: 庞大的重试日志，由 `gsutil` 失败重试引起。
* **`linux1-lx` (Linux 节点)**:
  * `audit/stage3_full/` 及相关 `shards`: 约 600MB 的废弃分片。由早期在 Linux 上崩溃的 `forge_base_matrix.py` 遗留。
  * `/var/log/syslog`: 系统日志。由于底层 ZFS 内存泄漏导致的系统反复重启、OOM Killer 和网络进程断连，使得内核向 syslog 疯狂抛出报错，曾导致启动盘占满。
* **`omega-vm` (云端主控节点)**:
  * `audit/stage3_full_unified_local/`: SCP 跨国传输出错遗留的残缺 `.parquet` 文件。
  * `/tmp/scp_*.log`, `/tmp/vertex_*.log`: 各种手动调试打流生成的后台输出日志。

## 3. 顶层自动清理设计 (Top-Level Auto-Cleanup Design)

为了避免未来的执行脚本再次把各台机器的硬盘撑爆，制定如下代码级规范：

### A. 脚本级自动收尸 (Script-Level Auto GC)
在类似 `forge_base_matrix.py` 这种涉及海量硬盘 I/O 的脚本中，应引入 `try...finally` 或依赖校验的自动清理：
```python
def merge_and_cleanup(shard_dir: Path, out_file: Path):
    success = False
    try:
        # 执行合并逻辑
        _merge(shard_dir, out_file)
        success = True
    finally:
        if success and out_file.exists():
            # 只有在最终产物安全落地后，才静默删掉那几千个碎文件
            shutil.rmtree(shard_dir, ignore_errors=True)
```
*注：如果在合并前崩溃，`shard_dir` 将被保留，以便于下一次带着 `--resume` 快速断点续传。这兼顾了调试安全性与磁盘卫生。*

### B. 防止 Syslog/启动盘被打爆 (Log Spillage Prevention)
当运行大量子进程（如 8-32 个 Workers）时，如果子进程向 `sys.stdout` 或 `sys.stderr` 疯狂打日志（比如每一条数据的进度），系统默认可能会将其兜底到 `syslog` 或者使本地日志文件瞬间膨胀至 GB 级。
* **对策 1 (Python 侧)**: 在 `tools/` 的主干脚本中，必须配置 `logging.handlers.RotatingFileHandler`。将日志大小严格卡死（如 `maxBytes=50*1024*1024`, `backupCount=3`）。
* **对策 2 (Linux 系统侧)**: 在 `linux1-lx` 上，确保 `/etc/logrotate.d/rsyslog` 具有 `size 100M` 触发强制轮转的兜底配置，防止单一报错风暴吃光 `/` 根目录。

### C. 跨端临时搬运清理确认 (Inter-node Transport Sweep)
像这次借道 Mac 上传 9GB 文件的情况属于“战术动作”。针对这种非固定流水线的巨型文件转移：
* 应当采用临时目录（如 `/tmp/`，重启即焚），或者在传输完成的回调指令中硬编码 `rm -f <payload>` 进行阅后即焚。
* 若涉及永久目录，则必须在 `stage3` 等结束时，由 Supervisor 弹出一个 **"Project Teardown"** 人工确认步骤，让主控机去清扫旁路机器上的残留。