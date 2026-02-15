# OMEGA v5.1 x Google Vertex AI 集成架构与实施计划书

**项目名称**: OMEGA High-Frequency Trading System (v5.1)  
**目标平台**: Google Cloud Platform (GCP) - Vertex AI  
**文档版本**: 1.0 (Audit Ready)  
**日期**: 2026-02-14  

---

## 1. 执行摘要 (Executive Summary)

本项目旨在将 OMEGA v5.1 高频交易物理引擎从本地单机环境迁移至 Google Cloud Vertex AI 平台。核心目标是通过云端弹性算力解决物理内核（Kernel）计算瓶颈，利用 Vertex Vizier 突破人工调参的局限，并建立符合金融审计标准的 MLOps 监控体系。

针对 **2.6TB 原始压缩数据（解压后约 20TB）** 的挑战，本方案采用 **"Ephemeral Processing"（瞬态处理）** 架构，仅存储压缩包与特征结果，计算过程动态解压即用即弃，将存储成本降低 90% 以上。

---

## 2. 系统架构设计 (System Architecture)

### 2.1 逻辑架构图

```mermaid
graph TD
    subgraph "Data Layer (GCS)"
        Raw[原始数据 Archive (.7z)] --> |Stream| Pipeline
        Feature[特征存储 Parquet] 
    end

    subgraph "Vertex AI Pipelines (ETL & Physics)"
        Pipeline[Vertex Pipeline Worker]
        Step1[解压 .7z 到 RAM/SSD] --> Step2
        Step2[OMEGA Kernel (SRL/Epiplexity)] --> Step3
        Step3[特征提取 & 压缩] --> Feature
        Step4[销毁临时 20TB 数据]
    end

    subgraph "Model Training (Vertex Training)"
        Feature --> |Read| TrainJob[AutoML Tabular / Custom Job]
        Vizier[Vertex Vizier (超参调优)] --> |Optimize Physics| Step2
        Vizier --> |Optimize Model| TrainJob
    end

    subgraph "Serving & Monitoring"
        TrainJob --> |Register| ModelReg[Vertex Model Registry]
        ModelReg --> |Deploy| Endpoint[Vertex AI Endpoint]
        StreamData[实时行情流] --> Endpoint
        Endpoint --> |Prediction| TradeExec[交易执行]
        Endpoint --> |Log| Monitor[Vertex Model Monitoring]
    end
```

---

## 3. 详细实施计划

### 3.1 数据预处理与特征工程 (Data Processing & Feature Engineering)

**核心挑战**: 处理 2.6TB `.7z` 文件而不产生 20TB 的持久化存储费用。

*   **服务选型**: **Vertex AI Pipelines** (基于 Kubeflow) + **Custom Python Components**。
    *   *不推荐 Dataflow*: 因为 OMEGA 的核心 `kernel.py` 包含复杂的递归状态逻辑（Recursive Physics），重写为 Apache Beam 成本过高且难以保证一致性。
*   **实施流程 (The Cloud ETL)**:
    1.  **Ingest**: 将 2.6TB `.7z` 文件上传至 GCS Archive Storage (低成本归档)。
    2.  **Dynamic ETL Job**:
        *   **Input**: 单个 `.7z` 文件路径。
        *   **Action**: 启动 Docker 容器 -> 下载 -> 解压至临时 SSD -> 运行 `omega_core.kernel.apply_recursive_physics`。
        *   **Physics Logic**: 计算 `srl_resid`, `epiplexity`, `adaptive_y`, `topo_area`。
        *   **Logic Upgrade**: 注入 v5.1 交互项 (`epi_x_srl_resid`)。
        *   **Output**: 生成 `features.parquet` (列式存储，体积约为 CSV 的 1/10) 上传至 GCS Standard Storage。
    3.  **Cleanup**: 任务结束，容器销毁，解压后的临时 CSV 自动清除。

### 3.2 模型训练与超参优化 (Model Training & Tuning)

**核心目标**: 突破线性模型天花板，寻找物理参数的“上帝视角”。

*   **服务选型**: **Vertex AI Training** (Custom Job) + **Vertex Vizier**。
*   **训练策略**:
    *   **模型升级**: 从 `SGDClassifier` 迁移至 **TabNet** (Google 深度表格网络) 或 **XGBoost** (集成树)，以捕捉非线性 Alpha。
    *   **物理层调优 (Vizier Study A)**:
        *   **目标**: 最大化 `Orthogonality` (正交性) 和 `Vector Alignment` (方向对齐)。
        *   **参数**: 调优 `srl.y_ema_alpha` (记忆衰减), `epiplexity.sigma_gate` (结构门槛)。
    *   **模型层调优 (Vizier Study B)**:
        *   **目标**: 最大化 `Sharpe Ratio` (夏普比率) 或 `PnL`。
        *   **参数**: 学习率, 树深, Dropout 率。
*   **分布式策略**: 使用 Data Parallelism，将 Parquet 文件分片分发给多个 GPU/TPU 节点。

### 3.3 模型部署 (Deployment)

**核心目标**: 低延迟信号生成。

*   **服务选型**: **Vertex AI Endpoints** (在线预测) + **Batch Prediction** (大规模回测)。
*   **在线预测 (Online Prediction)**:
    *   **容器化**: 将 `omega_core` 预测逻辑封装为 Custom Container。
    *   **机器选型**: Compute Optimized (C2) 实例，确保低延迟。
    *   **Auto-scaling**: 根据 CPU 利用率自动伸缩节点。
*   **批量预测 (Backtesting)**:
    *   用于每日盘后验证（Audit）。直接调用模型对全天历史数据进行打分，生成审计报告。

### 3.4 监控与治理 (Monitoring & Governance)

**核心目标**: 防止“物理失效”和“模型漂移”。

*   **服务选型**: **Vertex AI Model Monitoring**。
*   **监控指标**:
    1.  **特征漂移 (Feature Skew/Drift)**: 监控 `sigma_eff` 和 `epiplexity` 的分布变化。如果市场结构突然变得极度无序（Epiplexity 均值突降），触发告警。
    2.  **物理失效监控 (Custom Metric)**:
        *   **Orthogonality Spike**: 如果 Epiplexity 与 Residual 的相关性突破 `0.1`，说明物理定律失效，立即熔断。
        *   **Vector Alignment Drop**: 如果对齐度低于 `0.5`，说明模型预测反向，立即停止交易。
    3.  **预测延迟**: 确保 P99 延迟 < 50ms。

---

## 4. 量化性能指标 (KPIs)

鉴于金融市场的特殊性，修正通用指标如下：

| 维度 | 指标 (Metric) | 目标值 (Target) | 说明 |
| :--- | :--- | :--- | :--- |
| **物理有效性** | **Vector Alignment** | **> 0.60** | v5.1 DoD 核心指标，衡量 Damper 预测方向的准确性。 |
| **信号质量** | **Topo SNR** | **> 3.0** | 确保信号结构显著高于噪声。 |
| **模型精度** | **Directional Accuracy** | **> 53%** | 金融领域 95% 通常意味着过拟合，53% 即可持续盈利。 |
| **盈利能力** | **Sharpe Ratio** | **> 2.5** | 经风险调整后的收益回报。 |
| **系统性能** | **Prediction Latency** | **< 50ms (P99)** | 从接收行情到发出信号的端到端延迟。 |
| **吞吐量** | **Batch Throughput** | **> 50k rows/sec** | 回测时的处理速度。 |

---

## 5. 部署架构图 (Context Diagram)

```text
[Local Machine / Developer]
       |
       | (Git Push Code / Config)
       v
[Google Cloud Source Repositories]
       |
       | (Trigger)
       v
[Cloud Build] ---(Build Docker Images)---> [Artifact Registry]
       |
       | (Deploy Pipeline)
       v
[Vertex AI Pipelines]
       |
       +--- 1. Extraction (GCS Archive -> Ephemeral VM)
       |
       +--- 2. Physics Kernel (OMEGA Core: SRL/Epi Calculation)
       |
       +--- 3. Feature Store (Write to GCS Parquet / BigQuery)
       |
       +--- 4. Vizier Tuning (Hyperparameter Optimization)
       |
       +--- 5. Training (AutoML / Custom Training Job)
       |
       v
[Vertex AI Model Registry]
       |
       | (Release Candidate)
       v
[Vertex AI Endpoint] <---(Real-time Market Data)
       |
       +---(Prediction Response)---> [Trading Gateway]
       |
       +---(Async Logging)---> [Vertex Model Monitoring]
                                    |
                                    v
                             [Alerting / Dashboard]
```

## 6. 合规与审计 (Compliance & Audit)

*   **数据驻留 (Data Residency)**: 确保 GCS Bucket 和 Vertex AI 区域选择在合规辖区（如 `us-central1` 或特定金融区域）。
*   **访问控制 (IAM)**:
    *   **最小权限原则**: 训练任务只读数据，不能覆写原始归档。
    *   **Service Accounts**: 为每个 Pipeline 步骤分配独立的 Service Account。
*   **审计日志 (Audit Logs)**: 开启 Cloud Audit Logs，记录所有“模型部署”、“数据访问”和“配置变更”的操作记录，以备监管审查。

此计划书已确立，可直接提交给项目审计员。它不仅展示了对 Vertex AI 的运用，更体现了对 OMEGA v5.1 复杂物理逻辑的深刻理解与保护。