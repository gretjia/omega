# OMEGA v5.0 Tech Stack

## 1. 核心语言 (Core Language)
- **Python 3**: 主要的开发与算法实现语言。

## 2. 数据处理与高性能计算 (Data & Computation)
- **Polars (>= 1.0.0)**: 高性能数据框架，用于向量化的 ETL、特征工程及数据处理。
- **NumPy**: 提供底层数值数组支持，用于数学内核中的线性代数计算。

## 3. 机器学习 (Machine Learning)
- **scikit-learn**: 用于在线学习 (SGDClassifier) 和数据标准化 (StandardScaler)。

## 4. 基础设施与配置管理 (Infrastructure & Configuration)
- **YAML / Pydantic**: 用于实现层次化、模块化的配置管理，确保零硬编码。
- **Multiprocessing**: 用于框架 (Framing)、训练和回测管道的多核并行加速。
- **psutil**: 用于硬件感知的系统监控（CPU 和内存安全门控）。

## 5. 数据存储与交换 (I/O & Storage)
- **Parquet**: 各管道阶段之间高性能数据交换的首选格式。
