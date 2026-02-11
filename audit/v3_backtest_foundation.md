# OMEGA v3 (Level-2) 回测基础设施调研报告

## 1. 概述
OMEGA v3 系统基于 Level-2 行情数据，采用基于“成交量时钟”（Volume-Clock）的采样方式，结合确定性物理模型与机器学习策略。目前回测逻辑已集成在 `omega_v3_core` 模块中。

## 2. 核心组件说明

### 2.1 信号生成引擎 ([kernel.py](file:///d:/Omega_vNext/omega_v3_core/kernel.py))
- **功能**：实现确定性信号生成逻辑。
- **核心逻辑**：基于 `epiplexity`（复杂性）、`srl_resid`（平方根定律残差）和 `topo_area`（拓扑符号面积）等特征，结合 `config.py` 中的阈值产生买卖信号。
- **输出**：提供 `run_l2_kernel` 接口，返回处理后的数据帧（Frames）及触发的信号（Signals）。

### 2.2 数据处理流水线 ([omega_etl.py](file:///d:/Omega_vNext/omega_v3_core/omega_etl.py))
- **功能**：基于 Polars 的高性能向量化 ETL。
- **核心逻辑**：
    - 清洗原始 L2 数据（处理 GB18030 编码、异常值）。
    - 计算中间特征：Microprice、OFI（订单流不平衡）、Depth（深度）。
    - 按成交量（Volume）进行分桶，生成成交量时钟数据帧。
- **数据源**：主要读取 `level2_frames_*` 目录下的 Parquet 文件。

### 2.3 评估与审计 ([trainer.py](file:///d:/Omega_vNext/omega_v3_core/trainer.py))
- **功能**：提供模型训练及确定性模型的审计（Audit）功能。
- **核心指标**：
    - **Topo_SNR**：拓扑信号信噪比，衡量信号的统计显著性。
    - **Vector_Alignment**：矢量对齐度，衡量预测方向与未来价格走势的一致性。
    - **DoD_pass**：是否通过“定义完成”（Definition of Done）的标准。
- **接口**：`run_l2_audit` 可对指定路径的数据进行批量回测评估。

## 3. 机器学习模型集成
目前已训练完成的模型文件为 `artifacts/omega_v3_policy.pkl`。

- **模型类型**：`SGDClassifier`（逻辑回归，L2 正则化）。
- **包含组件**：
    - 训练好的 `model`。
    - 特征缩放器 `scaler` (`StandardScaler`)。
    - 特征列表 `feature_cols`（包括 `sigma_eff`, `net_ofi`, `depth_eff` 等 8 个特征）。
    - 训练时的配置 `cfg`。

## 4. 下一步回测计划
为了支持 2025 年样本外数据的全量回测，计划开发 `run_v3_backtest.py` 驱动脚本，实现以下流程：
1. **加载模型**：读取 `omega_v3_policy.pkl`。
2. **数据处理**：调用 `omega_etl.py` 加载 2025 年 L2 数据。
3. **策略执行**：使用 `SGDClassifier` 对每一帧进行预测，结合 `decision_margin` 生成交易指令。
4. **性能评估**：统计 PnL、胜率、回撤及 `trainer.py` 中定义的审计指标。

## 5. 结论
系统已具备完整的回测框架。当前的重点是利用已有的 ETL 和评估逻辑，将 ML 模型无缝集成到自动化回测流程中。
