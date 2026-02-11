# v40 Frame Optimization (Windows AI 直接执行版)

目标：用**极限快测**决定 `FrameWorkers`，再进入全量 frame。  
约束：不改数学核心，不改结果定义，只做并行参数优化。

## Best-Practice Basis（代码+网络调研结论）

### A. 现网证据（v40 bench 实测）
- `w12`：`55.28 arh/h`（`audit/v40_runtime/windows/frame_bench/w12_status.json`）
- `w22`：`51.41 arh/h`（`audit/v40_runtime/windows/frame_bench/w22_status.json`）
- 同样 24 archive 工作量下，`w22` 的 `copy/extract` 累计耗时明显更高，符合 I/O 争用特征。

### B. 外部 best practice（官方文档）
- Python `shutil.copyfile()`：会使用平台级 fast-copy syscall，适合 staging 临时拷贝。
- Python `os.walk()` 自 3.5 起基于 `os.scandir()`，目录遍历更高效。
- 7-Zip `-mmt`：每个 worker 内部线程需谨慎设置，避免与多进程 oversubscription。
- 7-Zip `-i` include：可限制解压范围（此处默认仅解 `*.csv`），减少无效 I/O。
- Polars `thread_pool_size`：并行环境要避免“进程并发 + 每进程高线程”叠加导致资源竞争。

### C. 已落地到代码的优化（不改变数学结果）
- frame driver 新增 `--io-slots`（copy+extract 并发闸门）；
- 默认 `--extract-csv-only`（减少解压无关文件）；
- staging 拷贝改为 `copyfile`（不保留元数据，降低开销）；
- manifest/preflight/compat/train/backtest 路径扫描升级为递归，兼容分层输出目录。

---

## 0) 如果当前还在跑长测（例如 747 档）

先在 Windows 终端停止当前 benchmark：
- `Ctrl + C`

说明：
- 之前的 `-Limit 800` 会在当前数据量下跑到 `747`，不适合“快速定参”。

---

## 1) 极限快测（推荐，先做这个）

只比较极值 `12 vs 22`，避免在基准测试上浪费时间。

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\benchmark_v40_frame_win.ps1 `
  -Limit 24 `
  -Workers "12,22" `
  -IoSlots 4 `
  -FrameSevenZipThreads 1
```

快速决策规则：
1. 若 `22` 比 `12` 提升 **>= 5%**，选 `22`
2. 若提升 **< 5%**，选 `12`（稳定且资源占用更低）

说明：
- 这个测试通常能在较短时间内给出足够可靠的结论。
- `Limit 24` 保证队列深度大于 22，`12/22` 的差异可以被观察到。

---

## 2) 健康检查（可选，1-2 分钟）

用途：确认脚本能跑通，不用于决定最优 worker。

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\benchmark_v40_frame_win.ps1 `
  -Limit 4 `
  -Workers "12,16,20,22" `
  -IoSlots 4 `
  -FrameSevenZipThreads 1
```

---

## 3) 第一轮有效对比（用于细化 worker，可选）

关键原则：`Limit` 必须大于最大 worker（22），否则对比无效。  
建议使用 `Limit 32`（短时可完成，且有并发深度）：

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\benchmark_v40_frame_win.ps1 `
  -Limit 32 `
  -Workers "12,16,20,22" `
  -IoSlots 4 `
  -FrameSevenZipThreads 1
```

---

## 4) 第二轮确认（只跑前两名，可选）

把第一轮 `archives_per_hour` 最高的两档替换到下面命令，例如 `20,22`：

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\benchmark_v40_frame_win.ps1 `
  -Limit 64 `
  -Workers "20,22" `
  -IoSlots 4 `
  -FrameSevenZipThreads 1
```

---

## 5) 选型规则（最终）

按顺序判定：
1. `archives_per_hour` 最大
2. `success=true`
3. 若前两名差距 < 5%，选较小 worker（稳定优先）

---

## 5) 全量 frame 执行

假设最终选择 `FrameWorkers=12`（快测常见结果）：

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage frame `
  -FrameWorkers 12 `
  -FrameIoSlots 4 `
  -FrameSevenZipThreads 1 `
  -FrameOutputDir data/level2_frames_v40_win `
  -FrameStageDir C:/Omega_level2_stage
```

---

## 7) 结果记录（固定写入位置）

### 5.1 benchmark 原始输出（自动生成）
- `audit/v40_runtime/windows/frame_bench/benchmark_summary.json`
- `audit/v40_runtime/windows/frame_bench/benchmark_summary.csv`
- `audit/v40_runtime/windows/frame_bench/w*.log`
- `audit/v40_runtime/windows/frame_bench/w*_status.json`（含 `timing_totals.io_wait_sec`，用于判断 I/O 争用）

### 5.2 决策结论（必须写）
- **固定文件**：`audit/v40_frame_optimization_result_latest.md`

执行下面命令自动写入结论文件（Windows PowerShell）：

```powershell
cd D:\Omega_vNext
$csv = "audit/v40_runtime/windows/frame_bench/benchmark_summary.csv"
$out = "audit/v40_frame_optimization_result_latest.md"
$rows = Import-Csv $csv | Sort-Object {[double]$_.archives_per_hour} -Descending
$top = $rows | Select-Object -First 1
$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$content = @()
$content += "# v40 Frame Optimization Result (Latest)"
$content += ""
$content += "- Timestamp: $ts"
$content += "- Selected FrameWorkers: $($top.worker_count)"
$content += "- FrameSevenZipThreads: 1"
$content += "- Top archives_per_hour: $($top.archives_per_hour)"
$content += "- Top elapsed_sec: $($top.elapsed_sec)"
$content += "- Source CSV: $csv"
$content += ""
$content += "## Ranked Results"
$content += ""
$content += "| worker_count | success | archives_per_hour | elapsed_sec | archives_done | parquet_files |"
$content += "|---:|:---:|---:|---:|---:|---:|"
foreach ($r in $rows) {
  $content += "| $($r.worker_count) | $($r.success) | $($r.archives_per_hour) | $($r.elapsed_sec) | $($r.archives_done) | $($r.parquet_files) |"
}
$content -join "`r`n" | Set-Content -Path $out -Encoding UTF8
Write-Host "Written: $out"
```

---

## 8) 后续衔接（固定分割）

frame 完成后执行：

```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1
```

固定分割：
- Train: `2023,2024`
- Backtest: `2025` + `202601`

---

## 9) 必查状态文件

- `audit/v40_runtime/windows/frame/frame_status.json`
- `audit/v40_runtime/windows/train/train_status.json`
- `audit/v40_runtime/windows/backtest/backtest_status.json`
