---
description: AI 交接班协议 - 记录当前进度并为下一个 AI 准备上下文
---

# Handover Workflow

当用户说 "handover"、"交接"、"换班" 或类似指令时，执行以下步骤：

## Step 1: 执行交接前校验（必须先通过）

```bash
python3 tools/check_readme_sync.py
```

要求：
1. 输出必须是 `README sync check passed.`
2. 若失败，先修复 README 索引漂移，再继续 handover

## Step 2: 读取当前状态

```bash
# 读取现有 handover 日志
cat .agent/skills/ai_handover/handover_log.md
```

## Step 3: 记录本次会话进度

在 `.agent/skills/ai_handover/handover_log.md` **顶部** 追加以下格式的条目：

```markdown
---

## [YYYY-MM-DD HH:MM] Session Handover

### Completed This Session
- [具体完成的任务1]
- [具体完成的任务2]

### Current State
- 数据状态: [描述]
- 代码状态: [描述]
- 阻塞项: [无/具体描述]

### Next AI Should
1. [下一步任务1]
2. [下一步任务2]

### Files Modified
- `path/to/file1.py` - [修改说明]
- `path/to/file2.md` - [修改说明]

### Validation Gates
- README sync: PASS (`python3 tools/check_readme_sync.py`)

### Warnings
- [任何需要注意的问题]
```

## Step 4: 通知用户

告知用户 handover 已记录，下一个 AI 可以从哪里接手。

---

# 新 AI 接手流程

当新 AI 开始会话时：

1. **首先阅读**: `.agent/skills/ai_handover/SKILL.md`
2. **其次阅读**: `.agent/skills/ai_handover/handover_log.md` (查看最近条目)
3. **了解项目**: 按需阅读其他 skill 文件

// turbo-all
