---
name: evolution_knowledge
description: OMEGA 版本演化与审计知识库 - 利用历史审计结果和版本记录，防止在参数和逻辑上"原地踏步"
---

# Evolution Knowledge (Audit & Version Forensics)

## 核心目标
利用 `audit/` 目录下的丰富历史记录，使 Agent 具备"记忆"能力。防止 Agent 提出已经被证明无效的修改建议，或违反已经达成的核心共识。

## 1. 决策溯源协议 (FORENSICS PROTOCOL)

在提出任何重大的逻辑修改或参数调整前，必须：

### 1.1 检索历史提案
使用 `grep` 或 `search` 搜索 `audit/` 目录下相关的提案：
```bash
# 搜索参数修改历史
grep -r "dynamic_threshold" ./audit/
```

### 1.2 查阅演化日志
优先阅读 `audit/omega_evolution_master_log.md` (如果存在) 或最近的版本审计报告（如 `audit/vXXXX_audit.md`）。

## 2. 知识优先级 (Knowledge Priority)

1.  **Constitution 原则**：`OMEGA_CONSTITUTION.md` Article II 禁止硬编码阈值，所有交易参数必须是动态函数。
2.  **FAILED 路径**：在历史审计文档中记录为"预期不符"或"回测失败"的路径，必须避免。
3.  **SUCCESS 经验**：已验证的**动态计算方法**和边界处理逻辑，应作为新功能的基石。

## 3. 证据引用规范

当 Agent 做出决策时，应引用版本历史作为证据：
- ✅ "根据 `audit/vXXXX_audit.md` 的结论，动态 quantile 方法比静态阈值更稳健。"
- ❌ "我认为应该把 trigger_floor 硬编码为 1.2。" (违反 Constitution Article II)

## 4. 维护义务
每当完成一次重要的版本补丁或参数实验，必须在 `audit/` 下创建一个简短的 `.md` 报告，记录：
- 修改内容
- 验证结果（Win Rate, Trades 等）
- 最终结论（保留/废弃）
