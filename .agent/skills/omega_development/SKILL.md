---
name: omega_development
description: OMEGA 量化引擎开发规范 - 遵循 Constitution、防止幻觉、保护数学内核
---

# OMEGA Development Skill

## 核心原则

**OMEGA 是一个基于 Constitution 第一性原理的量化交易系统。所有修改必须基于证据，遵循动态参数原则。**

---

## 第一章：禁止行为 (NEVER DO)

### 1.1 禁止硬编码交易参数 (Constitution Article II)

根据 `OMEGA_CONSTITUTION.md` Article II:

> **"There are NO static parameters."**
> Hardcoding `threshold = 0.5` or `window = 20` is a VIOLATION.

**所有交易阈值必须是动态函数**：
```python
# ❌ PROHIBITED: Static hardcoding (限制模型智能)
STOP_LOSS = -0.03
TAKE_PROFIT = 0.15
trigger_floor = 1.2

# ✅ REQUIRED: Dynamic/Recursive thresholds
threshold = quantile(rolling_history, 0.95)
epsilon_tda = adaptive_to_local_density(point_cloud)
exit_signal = entropy_gated_control_law(H_T, S_T)
```

**违反后果**：硬编码 STOP_LOSS/TAKE_PROFIT 会限制模型学习最优退出策略的能力。

### 1.2 禁止猜测数据格式

**历史教训 (保留参考)**：
- "JSON Blindness"：猜测 L2 价格是数组，实际是字符串 `"[21.5, 21.6]"`
- "Volume Starvation"：猜测字段名是 `delta_vol`，实际是 `_delta_vol`

**正确做法**：
```python
# ALWAYS check actual data before processing
sample = data.iloc[0] if hasattr(data, 'iloc') else data[0]
print(f"DEBUG: type={type(sample)}, columns={getattr(data, 'columns', 'N/A')}")
```

### 1.3 禁止假设训练/推理一致性

**历史教训 (保留参考)**：
- "K=0 Bug"：训练用 Z-score，推理用原始值
- "Shape Mismatch"：训练用 (N, 120, 5)，推理用 (N, 11, 5)

**正确做法**：
1. `feature_factory.py` 和 `omega_v3_core/kernel.py` 必须共享相同的特征计算逻辑
2. 任何特征修改必须同时更新训练端与 `omega_v3_core/kernel.py`
3. 使用 `assert` 验证输入维度

---

## 第二章：必须行为 (ALWAYS DO)

### 2.1 边界检查

**历史教训**：`np.log(0)` 导致 `-inf` 造成训练崩溃

**必须添加的防护**：
```python
# MANDATORY: Price floor
prices = np.maximum(prices, 1e-9)

# MANDATORY: Return clamp
returns = np.clip(returns, -0.1, 0.1)

# MANDATORY: Shape guard
if tensor.shape[0] != EXPECTED_BARS:
    continue  # Skip, don't crash
```

### 2.2 现金流正确性

**历史教训**："Infinite Money Glitch" - 买入后忘记扣除 `cash`

**必须检查的逻辑**：
```python
# CORRECT: Cash deduction
if signal_buy:
    positions = cash / price
    cash = 0.0  # <-- CRITICAL: Must deduct

# CORRECT: Position closing
if signal_sell:
    cash = positions * price
    positions = 0.0
```

### 2.3 调试输出

**任何新功能必须包含调试点**：
```python
if DEBUG:
    print(f"[{stock}] bars={len(bars)}, signal={signal}")
```

---

## 第三章：内核修改协议

### 3.1 受保护文件列表

| 文件 | 保护等级 | 修改要求 |
| :--- | :--- | :--- |
| `omega_v3_core/kernel.py` | 🔴 CRITICAL | 需要数学证明 + 回测验证 |
| `omega_v3_core/omega_math_core.py` | 🔴 CRITICAL | 需要数学证明 |
| `feature_factory.py` | 🟡 HIGH | 需要同步 omega_v3_core/kernel.py |
| `config.py` | 🟡 HIGH | 需要回测验证 |

### 3.2 修改前确认协议

**当 AI 准备修改核心文件时，必须先暂停并向用户展示**：

```markdown
⚠️ **内核修改确认**

**📁 文件**: `omega_v3_core/kernel.py`

**🔄 修改项**:
| 项目 | 修改前 | 修改后 | 影响范围 |
| :--- | :--- | :--- | :--- |
| [具体修改] | [原值] | [新值] | [影响] |

**📊 证据来源**: [具体文件/日志/审计报告]

**请确认是否继续修改？** (是/否)
```

### 3.3 变更记录要求

任何被批准的核心修改必须同时更新：
1. `audit/` 目录下创建变更记录
2. 更新 `handover_log.md`

---

## 第四章：验证流程

### 4.1 单股快速验证

```bash
python omega_standaloner.py --stock 000032 --debug
```

**通过标准**：
- 有交易产生 (Trades > 0)
- 无 NaN/Inf 输出
- 信号值在合理范围

### 4.2 数据验证

```bash
# 检查 L2 训练进度
# macOS/Linux
wc -l data/level2_frames_win2023/_audit_state.jsonl

# Windows
type data\level2_frames_win2023\_audit_state.jsonl | find /c /v ""
```

---

## 第五章：常见 Bug 模式 (调试参考)

### 5.1 零交易 (Zero Trades)

**症状**：回测完成，但 `Trades = 0`

**检查清单**：
1. 触发条件是否过于严格？
2. `Surprise` 是否锁定在高值？
3. `Kappa (K)` 是否计算正确？（检查是否在 Z-score 上计算）

### 5.2 无限金钱 (Infinite ROI)

**症状**：ROI 异常高 (> 1000%)

**检查清单**：
1. 买入后 `cash` 是否扣除？
2. 是否允许买入已涨停股票？
3. 仓位计算是否溢出？

### 5.3 训练崩溃 (Training Crash)

**症状**：训练中途退出

**检查清单**：
1. 是否有 `np.log(0)` 或 `np.log(-x)`？
2. 是否有 `x / 0`？
3. 输入 tensor shape 是否一致？

---

## 第六章：证据驱动开发

### 6.1 所有声明必须有证据

**错误示例**：
> "我认为这个参数应该改成 0.2。"

**正确示例**：
> "根据 `audit/xxx.md` 的回测结果，动态 quantile 方法比静态阈值 Win Rate 提升 15%。"

### 6.2 证据来源优先级

1. **代码输出** (最高优先级)
2. **日志文件**
3. **审计文档 (audit/)**
4. **Constitution 原则**

---

## 第七章：工程闭环与可恢复任务（并入 omega_engineering）

### 7.1 物理优先补充
1. 金融信号是方向性对象，避免仅用无方向标量替代趋势方向判定。
2. 熵过滤是硬门禁：高熵区间优先降权/静默，不可强行放大信号。

### 7.2 长任务可恢复
1. 超过 10 分钟的训练/回测/批处理任务，必须有 checkpoint。
2. checkpoint 语义记录“下一步位置”，恢复从该位置继续。
3. checkpoint 与产物写盘必须原子化（临时文件 + replace）。
4. 若使用 streaming/partial_fit，checkpoint 要包含缓冲区与 scaler 状态。

### 7.3 不可变基线
1. 训练或校准结果不得运行时回写 `config.py`。
2. 训练快照写入 artifacts，推理/回测从 artifacts 加载冻结状态。

### 7.4 开发执行顺序
1. Plan: 先定义完成标准（输出、行为、不变性、验证方式）。
2. Execute: 先小改动，避免把实验性逻辑直接写入主干。
3. Audit: 每次实现后检查边界、恢复语义、日志与产物。
4. Fix: 审计问题同轮修正并更新文档/交接。

---

## 附录：关键文件路径

| 用途 | 路径 |
| :--- | :--- |
| 宪法 | `OMEGA_CONSTITUTION.md` |
| 数学推导 | `audit/Bible.md` |
| 核心引擎 | `omega_v3_core/kernel.py` |
| 数学核心 | `omega_v3_core/omega_math_core.py` |
| 训练数据 | `data/history_ticks_full/` |
| L2 数据 | `data/level2/` |
| 审计文档 | `audit/` |

---

*End of OMEGA Development Skill*
