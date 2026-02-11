---
name: math_consistency
description: OMEGA 数学逻辑一致性校验 - 确保训练与推理逻辑 100% 对齐
---

# Math Consistency (Feature-Kernel Sync)

## 核心目标
消除量化系统中典型的"离线/在线不一致"Bug。确保模型训练时使用的特征计算逻辑与实盘/回测推理时的逻辑完全一致。

## 1. 强制同步协议 (SYNC PROTOCOL)

### 1.1 双向更新原则
任何对特征计算逻辑（公式、归一化方式、滑动窗口大小）的修改，必须**同时**在以下文件中实施：
1.  训练端特征提取代码
2.  `omega_v3_core/kernel.py` (推理端主干；若维护 v1，则为 `legacy_model/v1/kernel.py`)

### 1.2 逻辑提取比对
在修改完成后，必须人工或通过脚本比对两端的核心函数（如 `calculate_zscore`, `get_alpha_signal`）。

## 2. 常见不一致风险点 (Risk Points)

| 风险项 | 表现形式 | 防护措施 |
| :--- | :--- | :--- |
| **归一化差异** | 训练用 Z-score，推理用原始值 | 统一使用共享的数学函数 |
| **Look-ahead Bias** | 训练时使用了未来数据，推理时无法获取 | 严格检查滑动窗口索引 |
| **精度丢失** | Float32 (TensorFlow/Torch) vs Float64 (Numpy) | 强制显式类型转换 |
| **数据填充** | `NaN` 填充策略不一致 (0 vs Forward Fill) | 统一封装填充函数 |

## 3. 验证方法 (Verification)

### 3.1 单元测试对齐 (Cross-Verification)
建议创建验证脚本：
1.  构造一组模拟数据 `X_test`
2.  调用训练端特征提取得到 `Y_train`
3.  调用 `omega_v3_core/kernel.py` 特征提取得到 `Y_infer`
4.  执行 `assert np.allclose(Y_train, Y_infer, atol=1e-7)`

## 4. 变更记录
修改内核逻辑后，必须在 `audit/` 文档中注明："已验证训练端与推理端的同步性"。
