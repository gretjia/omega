---
name: data_integrity_guard
description: OMEGA 数据契约与质量守卫 - 确保数据源 Schema 的准确性，防止因格式猜测导致的 Bug
---

# Data Integrity Guard (Data Schema Protocol)

## 核心目标
防止因猜测数据格式（如 `JSON Blindness`, `Volume Starvation`）而引入的量化逻辑错误。确保输入到 `omega_v3_core/kernel.py` 或 `feature_factory.py` 的数据完全符合预期。

## 1. 强制性数据校验协议 (ALWAYS DO)

在处理任何来自外部（RQData, QMT, H5, CSV）的数据前，必须执行以下步骤：

### 1.1 结构探测 (Structure Probing)
如果是第一次接触该数据源或字段，必须先打印样本：
```python
# DO NOT GUESS. PROBE.
sample = data.iloc[0] if hasattr(data, 'iloc') else data[0]
print(f"DEBUG SCHEMA: {type(data)} | Columns: {getattr(data, 'columns', 'N/A')}")
print(f"DEBUG SAMPLE: {sample}")
```

### 1.2 字段一致性检查
必须验证关键字段的存在性和命名规范。
- ❌ `vol` (猜测)
- ✅ `_delta_vol` (验证后的实际字段名)

## 2. 常见数据陷阱清单 (Pitfalls)

| 数据源 | 陷阱 | 验证方法 |
| :--- | :--- | :--- |
| **QMT L2** | 价格可能是字符串形式的数组 `"[21.5, 21.6]"` | `isinstance(val, str)` then `eval()` or `json.loads()` |
| **RQData** | 字段名可能带有后缀或特定前缀 | `df.columns.tolist()` |
| **H5/Numpy** | 维度可能缺失或多余 (N, 1) vs (N,) | `assert arr.ndim == 2` |
| **CSV** | 日期格式不统一 (2023-01-01 vs 20230101) | `pd.to_datetime()` 显式转换 |

## 3. Schema 守卫函数模式

建议在数据加载层实现如下守卫逻辑：

```python
def validate_tick_schema(df):
    required = ['datetime', 'last', 'volume', '_delta_vol']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"CRITICAL: Missing field {col}. Available: {df.columns}")
    
    # 验证类型
    if not np.issubdtype(df['last'].dtype, np.number):
        raise TypeError(f"CRITICAL: 'last' price is not numeric. Type: {df['last'].dtype}")
```

## 4. 证据记录
当发现新的数据格式特性时，必须更新本技能文档的 **Pitfalls** 章节。
