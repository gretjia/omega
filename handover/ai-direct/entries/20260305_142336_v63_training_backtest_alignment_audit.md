---
entry_id: 20260305_142336_v63_training_backtest_alignment_audit
task_id: TASK-V63-GEMINI-EVIDENCE
timestamp_local: 2026-03-05 14:23:37 +0000
timestamp_utc: 2026-03-05 14:23:37 +0000
operator: Codex
role: auditor
branch: main
git_head: 43f03cf
hosts_touched: [omega-vm, linux1-lx, windows1-w1]
status: completed
---

## 1. Objective

- 聚合并固定化今天所有与 v63 相关工作证据。
- 将训练/回测结果与手册要求的 v63 指令对齐关系进行归档。
- 让审计端可按固定路径直接读取原始证据，不依赖会话过程记忆。

## 2. Scope

- 已收集：`handover/ai-direct` 的当日更新文件、`audit/v63*` 证据文件、远端训练/回测产物。
- 已更新：`handover/ai-direct/LATEST.md` 的状态段落（本轮 backtest 产物已完成），`handover/ai-direct/README.md` 的证据入口说明，仓库根 `README.md` 的快速入口。
- 未修改：训练/回测模型代码与核心参数（仅作审计归档和状态同步）。

## 3. Actions Taken

1. 识别并复核本轮关键交接与验收文件。
2. 读取并确认以下原始证据文件（含字段值）：
   - `handover/ai-direct/LATEST.md`
   - `handover/ai-direct/entries/20260305_075850_v63_basematrix_q1q9_relaunch.md`
   - `handover/ai-direct/entries/20260305_094450_v63_vertex_train_submit_retry.md`
   - `handover/ai-direct/entries/20260305_094830_v63_vertex_train_success.md`
   - `audit/v63.md`
   - `audit/v63_recursive_audit_report.txt`
   - `audit/v63_recursive_audit_raw_diff.txt`
   - `/home/zepher/work/Omega_vNext/audit/v63_2025_q1q9_basematrix.meta.json`
   - `/home/zepher/work/Omega_vNext/artifacts/v63_q1q9_train_metrics.json`
   - `/home/zepher/work/Omega_vNext/audit/v63_backtest_q4_status.json`
   - `/home/zepher/work/Omega_vNext/audit/v63_backtest_q4_result.json`
   - `/home/zepher/work/Omega_vNext/audit/v63_backtest_q4_status_verify.json`
   - `/home/zepher/work/Omega_vNext/audit/v63_backtest_q4_2025_all_manifest.txt`
   - `/home/zepher/work/Omega_vNext/audit/v63_backtest_q4_2025_manifest.txt`
3. 用 `gemini -y` 进行一次结构化对齐输出，结论为：流程有闭环但不满足放行质量门禁（训练样本过窄、回测交易率异常高）。
4. 将上述结论与原始数字写入 handover 新条目，更新可读入口。

## 4. Evidence

### 训练阶段

- `v63_2025_q1q9_basematrix.meta.json`：
  - `years=["2025"]`、`input_file_count=141`
  - `base_rows=561281`，`merged_rows=561281`
  - `batch_count=39`，`seconds=28455.72`
- `v63_q1q9_train_metrics.json`：
  - `status=completed`
  - `job_id=306719677785047040`
  - `mask_rows=603`
  - `total_training_rows=586`
  - `seconds=0.24`

### 回测阶段

- `v63_backtest_q4_status.json`：
  - `status=completed`
  - `phase=done_no_tasks`
  - `processed_files_total=1`
  - `total_rows=9940792`
  - `total_trades=9618642`
  - `total_pnl=2590.1997923344275`
- `v63_backtest_q4_result.json`：
  - `summary.files=1`
  - `summary.processed=1`
  - `summary.errors=0`
  - `total_pnl=2590.1997923344275`
  - `total_rows=9940792`
  - `total_trades=9618642`
- `v63_backtest_q4_2025_all_manifest.txt`：
  - 仅 `v63_backtest_q4_2025_all.parquet`（单文件 manifest）
- `v63_backtest_q4_2025_manifest.txt`：
  - 39 文件，覆盖 20251013~20251230

### 指令对齐与异常

- `parallel_trainer/run_parallel_backtest.py` 与 `parallel_trainer/run_parallel_backtest_v31.py` 同存（v31 为历史命名）。
- `audit/v63.md` 与 `handover/ai-direct/entries/.../20260305_094830_v63_vertex_train_success.md` 记录本轮已启动的对齐路径。

## 5. Risks / Open Issues

1. 训练有效样本严重坍缩（56.1w -> 586），高风险：模型实际训练数据不足。
2. 回测交易率过高（`9618642/9940792`≈96.7%），说明信号触发行为偏激，可能偏离生产合规边界。
3. 回测 manifest 形态上存在 `processed_files_total=1` 与 39 分片 manifest 共存的可审计不一致，需确认是否按分片流严格执行。
4. 核心 v63 指令（topology close/fastmath 禁用/warm-up mask/路由顺序）虽有文档与入口声明，但产物中未见可机读到位的逐步核函数审计字段。

## 6. Changes Made

- 新增交接文件：`handover/ai-direct/entries/20260305_142336_v63_training_backtest_alignment_audit.md`
- 更新文件：`handover/ai-direct/LATEST.md`
- 更新文件：`handover/ai-direct/README.md`
- 更新文件：`README.md`

## 7. Next Actions (Exact)

1. 由主审核链路补齐 v63 kernel/路径的可机读审计产物（topology 闭合、warm-up mask、out_epi fallback 具体算子阶段日志），并在回测前冻结证据版本。
2. 复核/修复训练数据塌缩问题，重新拉起训练任务后再做一次 Q4 回测；对比 `total_training_rows` 与 trade/row 触发率是否回归。
3. 明确 `run_parallel_backtest.py` 与分片 manifest 的强制路径策略，避免 `v31` 命名脚本进入主执行路径。

## 8. LATEST.md Delta

- `handover/ai-direct/LATEST.md`：
  - 更新 `Latest Related Entries` 中新增本条 entry 引用
  - 将 `Stage3-BASEMATRIX` 的 `Local Backtest Evaluation` 从 `PENDING` 调整为 `DONE (quality_gate_in_review)`
  - 将 `Immediate Next Actions` 增补：先完成 v63 门禁/审计再放行

