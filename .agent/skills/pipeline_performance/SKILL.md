---
name: pipeline_performance
description: OMEGA 全流程提速执行框架（先 CPU/工程与 I/O，后 GPU PoC），保证数学不变、结果不降质、可恢复与可审计。
---

# Pipeline Performance Skill

用于 OMEGA `frame -> train -> backtest` 的系统化提速任务。  
目标是**不改数学核心**、**不降低结果质量**前提下提升吞吐与稳定性。

## 何时触发

当需求包含以下关键词时触发：
1. 提速、吞吐、耗时优化、I/O 优化
2. worker 参数、batch/chunk 调参
3. 假死、日志不刷新、断点续作稳定性
4. 先不上 GPU，先做 CPU/工程优化

## 不可违背约束

1. 不改动 Trinity 数学语义（TDA/SRL/Epiplexity）。
2. 不引入生产硬编码交易阈值。
3. train/backtest 必须 role-isolated，默认 fail-closed。
4. 所有优化必须有前后证据与可回滚路径。

## 复用流程（Phase-by-Phase）

### Phase 0: 基线冻结（先测量后优化）
1. 记录三阶段基线：`archives_per_hour`、`rows/s`、`files/s`、总耗时。
2. 固定输入样本与 split，避免比较污染。
3. 输出基线到 `audit/`，作为后续对照。

### Phase 1: I/O 前整体优化（先 CPU/工程）
按“less is more”优先做不会改变结果的改造：
1. 训练 worker 内对象复用（避免每文件重复初始化重对象）。
2. `imap_unordered` 的 `chunksize` 从 1 改为自适应（如 4/8）并保留内存守卫。
3. 物理主瓶颈循环（Python row loop）做 typed-array/Numba 重构，公式保持等价。
4. backtest 改按需列读取，减少读放大。
5. worker 侧统一限制 `OMP/MKL/OPENBLAS` 线程为 1，避免多进程抢核。

### Phase 2: I/O 优化（staging-first）
1. frame/train/backtest 全流程默认本地 staging。
2. frame 使用 `io-slots` 节流 + `extract-csv-only` + `copyfile`。
3. train/backtest 使用 chunk staging + copy workers，并在每 chunk 后清理。
4. 在目标机器做 worker 快测（短 benchmark）后再定全量默认值。

### Phase 3: 可恢复性与可观测性
1. status/state 必须原子写（含重试）并持续刷新。
2. 每阶段日志与 status 路径固定在 `audit/v40_runtime/windows/`。
3. 断点续作语义明确：
   - frame: `_audit_state.jsonl`
   - train: `checkpoint_rows_*.pkl + processed_files`
   - backtest: `backtest_state.json`
4. 出现 stale/异常时先降档再重试，不直接放弃流程。

### Phase 4: 质量守门（不降质）
1. 数据契约：frame 产物满足 train/backtest 必需列与正价约束。
2. split 预检：train/backtest overlap 必须为 0。
3. 先 smoke 再 fullrun，比较前后质量指标：
   - PnL
   - Topo_SNR / Orthogonality / Vector_Alignment
   - race winner 可解释性

### Phase 5: GPU Gate（第二阶段专项）
只在以下条件同时满足后进入 GPU PoC：
1. CPU 长时间高占用（如 >85%）且 I/O 已优化完成；
2. 当前 CPU 路径已稳定，日志与续作可靠；
3. 有独立 PoC 分支与数值一致性回归计划。

## 输出要求（每次优化任务）

1. 一份执行计划（phase 切分 + 验收标准）。
2. 一份优化结果文档（前后对比 + 参数决策 + 风险）。
3. 一份 handover（运行命令、日志路径、恢复规则）。
4. README/治理索引同步，避免知识漂移。

## 参考材料

优先读取：
1. `audit/v40_cpu_first_execution_plan_2026-02-09.md`
2. `audit/v40_frame_optimization.md`
3. `audit/v40_hardware_optimization.md`
4. `audit/v40_windows_fullrun_handover_2026-02-10.md`
5. `./references/v40_speedup_case.md`
