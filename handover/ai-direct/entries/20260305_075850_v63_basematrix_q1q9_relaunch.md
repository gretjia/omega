# 2026-03-05 07:58 +0000 (V63 BaseMatrix Jan-Sep Relaunch)

## 背景
- 依据最新要求，Base Matrix 仅用于训练集。
- 本轮 V63 Stage3 约定仅使用 2025 全量文件中的 1-9 月数据（1-9 月训练区间）。

## 纠偏动作
- 发现当前输入清单生成逻辑错误：`name[:6] <= 202509` 误将 2023/2024 文件也带入。
- 已重建输入清单：`/home/zepher/work/Omega_vNext/audit/v63_2025_q1q9_input_list.txt`  
  - 行数：`141`
  - 过滤范围：`202501xx ~ 202509xx`
- 已将 forge 命令显式加上 `--years 2025`，避免 `forge_base_matrix.py` 默认 `--years 2023,2024` 导致的误过滤。

## 当前执行
- 命令已重启并落在 `linux1-lx`：
  - `.venv/bin/python3 tools/forge_base_matrix.py --input-file-list /home/zepher/work/Omega_vNext/audit/v63_2025_q1q9_input_list.txt --years 2025 --symbols-per-batch 200 --max-workers 2 --reserve-mem-gb 20 --worker-mem-gb 10 ...`
- 输出文件：
  - `audit/v63_2025_q1q9_basematrix.parquet`
  - `audit/v63_2025_q1q9_basematrix.meta.json`
  - `audit/v63_2025_q1q9_basematrix_shards/`
- 当前进度快照：
  - 进程：`.venv/bin/python3 tools/forge_base_matrix.py ...`（前端 2 进程）
  - 预计总 batch：`39`（与日志头部 `forge scheduling: total_batches=39` 一致）

## 预估
- 按历史运行（155 batches 耗时约 95639s）与当前单核/单 worker 执行策略推估，当前 39-batch 任务预计剩余约 `6~7小时`。

## 下一步
- 等待任务完成后，先校验输出完整性（meta + 行数）再进入 `train/backtest` 的下一阶段。
