# v34 Epiplexity Race Debug Postmortem (2026-02-08)

## Scope
- Task: 非全量赛马训练（zlib / lz76 / perm）并输出可决策结果。
- Context: 项目位于共享盘 `/Volumes/desktop-41jidl2`，Windows 主机同时执行 backtest，存在高 I/O 争用。
- Host: Mac Studio M4 Max, 32GB.

## Incident Summary
训练任务多次出现“进程存活但无进度”：
1. 日志长期不刷新（仅 `START round1`）
2. CPU/内存占用低
3. 无 checkpoint 产出
4. `ps` 显示 `UN` 或 `SN`，主进程存活但无有效推进

## Observable Evidence
- 日志卡住样例：`audit/v34_epi_race_round1.log`
- 早期重启但无进展：`audit/v34_epi_race_round1b.log`
- 有效两轮日志：
  - `audit/v34_epi_race_round1_final.log`
  - `audit/v34_epi_race_round2_final.log`
- 两轮结果：
  - `audit/v34_epi_race_round1_final_report.json`
  - `audit/v34_epi_race_round2_final_report.json`
- 运行清单：`audit/v34_epi_manifest_round1.txt`

## Root Cause Analysis

### Root Cause A: 共享盘目录遍历阻塞
- 症状：进程卡在启动前期，无 worker 进展。
- 采样证据：`sample` 调用栈在 `__opendir2/open` 与 `stat`。
- 原因：共享盘目录级枚举在高争用时阻塞（metadata path）。

### Root Cause B: Polars 路径扩展触发额外 `stat`
- 即使进入 worker，`pl.scan_parquet(...).collect()` 会触发路径扩展流程。
- 采样证据显示路径在 `scan_sources::expand_paths_with_hive_update -> Path::is_dir -> stat`。
- 这会再次放大共享盘 metadata 开销，导致 worker 挂起。

### Root Cause C: API mismatch
- `LazyFrame.sample` 不可用（当前环境），导致 worker 报错后无有效 batch。
- 修复前错误信息：`'LazyFrame' object has no attribute 'sample'`。

## Fixes Applied

### Fix 1: File-list execution mode
- 新增 `--file-list`（显式文件清单）绕过目录扫描。
- 逻辑：直接读取文件路径列表，不做共享盘目录枚举。

### Fix 2: Remove blocking pre-check
- 移除 `Path.exists()` 目录预检查（会触发 `stat`）。
- 改为“直接尝试，异常再记录”。

### Fix 3: Stronger heartbeat logging
- 在计划阶段增加 `flush=True` 的心跳日志。
- 避免“进程活着但看不到任何输出”的盲区。

### Fix 4: Eager sampling fix
- 改为先 `collect/read` 后 `df.sample(...)`。
- 避免 `LazyFrame.sample` 不存在导致 worker 失败。

### Fix 5: File-handle parquet read
- 改为：
```python
with open(read_path, "rb") as fh:
    df = pl.read_parquet(fh)
```
- 目的：减少由路径对象触发的额外路径扩展/metadata 调用。

### Fix 6: Robust empty-fit reporting
- 若无有效 batch，不再抛异常；输出 `status=no_fitted_batches` 的报告 JSON。
- 便于自动化流程继续并提示“样本不足/过滤过强”。

## Execution Strategy That Worked
1. 本地执行代码与环境（避免运行时依赖共享盘代码路径）。
2. 共享盘仅用于读取明确文件路径（manifest）。
3. 先跑探针（2 文件）验证链路，再放大到 120 / 280 文件。
4. 两轮实验后再作算法结论，避免单轮偶然性。

## Final Experiment Outcomes
- Round 1: `293` rows, winner=`epiplexity_lz76`
- Round 2: `3262` rows, winner=`epiplexity_lz76`（稳定复现）
- 结论摘要：`audit/v34_epi_race_summary_2026-02-08.md`

## Reusable Runbook (for future AI agents)
1. 若共享盘场景日志不刷新，先判定是否 I/O 阻塞而非训练逻辑错误。
2. 先执行 `sample <pid> 1 1`，确认是否在 `opendir/stat`。
3. 立即切换到 `--file-list` 模式，不再扫目录。
4. 优先使用“探针 -> 小规模 -> 扩容”三段式。
5. 任何轮次都要保证：
   - 有 checkpoint
   - 有 report JSON
   - 有单独 log
6. 若 `total_rows` 过低，自动执行第二轮扩样复核。

## Files Changed During Recovery
- `parallel_trainer/run_parallel_epi_race.py` (核心修复)
- `audit/v34_epi_race_round1_final.log`
- `audit/v34_epi_race_round2_final.log`
- `audit/v34_epi_race_round1_final_report.json`
- `audit/v34_epi_race_round2_final_report.json`
- `audit/v34_epi_race_summary_2026-02-08.md`

