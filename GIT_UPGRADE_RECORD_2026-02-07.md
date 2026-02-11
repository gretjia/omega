# OMEGA Git 升级留存记录（本地私有模式）

记录日期：2026-02-07
记录目的：为后续 AI / 开发者提供这次 Git 升级的审计留痕与复盘依据。

---

## 1. 升级背景

项目处于 v31 开发阶段，要求：
1. 高保密（不接 GitHub）
2. 双机协作（Mac + Windows，经局域网共享）
3. 获得可逆/可分叉/可追溯能力

---

## 2. 本次实施内容

### 2.1 初始化本地仓库

在项目根目录初始化 Git：
- 工作仓库：`.git/`
- 主分支：`main`

### 2.2 仓库跨平台配置

已写入（仓库级）配置：
1. `core.filemode=false`
2. `core.autocrlf=false`
3. `core.ignorecase=true`

目的：减少 Mac/Windows 文件系统差异导致的噪音变更。

### 2.3 建立本地私有远端（替代 GitHub）

在项目内建立裸仓库：
- `.local_remote/Omega_vNext.git`

并配置：
- `origin -> .local_remote/Omega_vNext.git`

已推送 `main`，形成局域网可同步的私有中心仓。

### 2.4 增加版本控制护栏文件

新增：
1. `.gitignore`
2. `.gitattributes`

关键策略：
1. 排除大目录与运行产物（`data/`, `artifacts/`, `archive/`, `tools/MinGit/`, 多类 audit 产物）
2. 文本默认 LF，Windows 脚本保持 CRLF
3. 排除 `.local_remote/`，避免把裸仓库本体再纳入版本库

### 2.5 基线提交

已创建提交：
1. `2df6cf5 chore: initialize local private git baseline for omega v31`
2. `9bd4ff5 chore: ignore local private bare remote directory`

---

## 3. 当前结果快照

### 3.1 远端状态

```bash
git remote -v
origin .local_remote/Omega_vNext.git (fetch)
origin .local_remote/Omega_vNext.git (push)
```

### 3.2 分支状态

```bash
git branch --show-current
main
```

### 3.3 历史状态

```bash
git log --oneline --decorate --max-count=5
9bd4ff5 (HEAD -> main, origin/main) chore: ignore local private bare remote directory
2df6cf5 chore: initialize local private git baseline for omega v31
```

---

## 4. 设计决策与取舍

1. 选择本地裸仓库而非 GitHub：满足保密要求。
2. 选择“工作仓 + 裸仓”模式：保留 GitHub 类开发体验（branch/push/pull/merge）。
3. 选择排除数据与产物：防止仓库膨胀和历史污染。
4. 保留审计文档类 `*.md`：保留研究上下文和可解释性。

---

## 5. 风险与后续建议

### 5.1 已识别风险

1. 共享盘稳定性：网络抖动可能影响 push/pull。
2. 双机并发修改同一 working tree：会导致冲突和锁文件问题。
3. 行尾差异：历史文档有 CRLF/LF 混合，虽可控但会产生提示。

### 5.2 建议执行规范

1. Windows 从裸仓库重新 clone 本地工作副本，不直接与 Mac 共用同一工作目录。
2. 每次开工先 `pull --ff-only`，收工后 `push`。
3. 里程碑打 tag，重要版本导出 `git bundle` 离线备份。
4. 优先使用 `revert` 回滚，不改写共享分支历史。

---

## 6. 关联文档

1. Windows 侧操作手册：`GIT_LOCAL_WORKFLOW_WINDOWS_AI.md`
2. 项目总览入口：`README.md`（新增 Git 本地协作章节）

---

## 7. 复现命令（摘要）

```bash
# 初始化
git init
git branch -M main

# 配置
git config core.filemode false
git config core.autocrlf false
git config core.ignorecase true

# 首次提交
git add .
git commit -m "chore: initialize local private git baseline for omega v31"

# 本地私有远端
mkdir -p .local_remote
git init --bare .local_remote/Omega_vNext.git
git remote add origin .local_remote/Omega_vNext.git
git push -u origin main
```

