# Specification: OMEGA v5.0 Full Pipeline Implementation

## 1. 背景与目标 (Background & Goals)
在成功通过冒烟测试验证架构后，本项目进入全量生产阶段。
本 Track 旨在利用 v5.0 的“全息阻尼器”架构，处理全部历史 L2 数据，训练物理模型，并完成性能评估。

## 2. 核心要求 (Core Requirements)
- **数据吞吐**：处理 E: 盘 747 个 7z 归档文件。
- **并行加速**：充分利用 32 核硬件配置，在 Framing 和 Training 阶段启用多进程。
- **因果一致性**：确保全量生成的特征库无 Paradox 3 漏洞。
- **闭环验证**：生成标准的回测指标（Sharpe, MDD, PnL）。

## 3. 验收标准 (Acceptance Criteria)
- 所有 747 个文件成功转化为 v5 Parquet 帧。
- 训练产出 `artifacts/omega_v5_model.pkl`。
- 回测管道在指定验证集上完成运行并输出 `backtest_report.md`。
