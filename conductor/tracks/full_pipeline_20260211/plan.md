# Implementation Plan - OMEGA v5.0 Full Pipeline

## Phase 1: 全量 Framing 生产 (Full-Scale Framing)
利用 `pipeline_runner.py` 进行大规模并行数据转换。

- [x] **Task: 启动并行 Framing 任务**
    - [x] 确认 `configs/hardware/active_profile.yaml` 中的 `framing_workers` 设置 (Set to 48).
    - [x] 执行 `python pipeline_runner.py --stage frame`。
    - [x] 使用 `tools/monitor_training.ps1` 监控 D: 盘写入速度和 CPU 负载。
    - *Note 1: Fixed `framer.py` to support multi-symbol processing (found 16k files/day).*
    - *Note 2: Fixed `framer.py` to filter non-Quote files (Schema Mismatch fix).*
    - *Note 3: Fixed `framer.py` to strictly sort slices by time (Volume Clock fix).*
    - *Note 4: Maximized workers to 48 (based on 96GB RAM) for IO saturation.*
- [ ] **Task: 生产数据集完整性校验**
    - [x] 验证部分输出 (Smoke Test `20230103.parquet` verified: 164k rows, 5337 symbols, monotonic buckets).
    - [ ] 验证全量输出目录中 Parquet 文件数量是否对齐（应为 747）。
    - [ ] 抽样检查特征值的分布（epiplexity > 0.5 的占比）。
- [ ] **Task: Conductor - User Manual Verification 'Phase 1: Full-Scale Framing' (Protocol in workflow.md)**

## Phase 2: 物理驱动模型训练 (Physics-Driven Training)
基于 v5 特征库训练 SGD 增量模型。

- [ ] **Task: 执行 v5 训练流水线**
    - [ ] 运行 `python parallel_trainer/run_parallel_v31.py --stage-dir D:/Omega_train_stage`。
    - *Note: `omega_core/trainer.py` patched to support multi-symbol Parquet labels and skip redundant physics.*
    - [ ] 验证特征权重（Weights）是否符合物理直觉（如 Epiplexity 贡献为正）。
- [ ] **Task: 模型 Artifact 固化**
    - [ ] 验证 `artifacts/omega_v5_model.pkl` 的生成。
- [ ] **Task: Conductor - User Manual Verification 'Phase 2: Physics-Driven Training' (Protocol in workflow.md)**

## Phase 3: 闭环回测验证 (Closed-Loop Backtest)
在历史数据上验证 Alpha 强度。

- [ ] **Task: 执行并行回测**
    - [ ] 运行 `python parallel_trainer/run_parallel_backtest_v31.py`。
- [ ] **Task: 产出回测审计报告**
    - [ ] 分析 PnL 曲线与 Epiplexity 制度的关联性。
- [ ] **Task: Conductor - User Manual Verification 'Phase 3: Closed-Loop Backtest' (Protocol in workflow.md)**
