# OMEGA 本地私有 Git 协作手册（Windows AI 专用）

更新时间：2026-02-07
适用项目：`Omega_vNext (v31 开发阶段)`
适用场景：不使用 GitHub，仅通过局域网共享文件夹在 Mac + Windows 双机协作

---

## 1. 目标与边界

本手册的目标是让 Windows 侧 AI 在**不接入公网仓库**的前提下，获得与 GitHub 类似的开发便利：

1. 可逆（回滚、还原、追责）
2. 可分叉（分支并行）
3. 可同步（双机协作）
4. 可审计（提交历史稳定）

边界：
1. 不上传 GitHub
2. 不把大数据/训练产物纳入版本库
3. 不让两台机器同时写同一个 working tree

---

## 2. 当前仓库事实（请先确认）

项目根目录：
`/Volumes/desktop-41jidl2/Omega_vNext`

当前 Git 状态（已初始化）：
1. 主分支：`main`
2. 本地私有远端：`origin -> .local_remote/Omega_vNext.git`
3. 最近提交：
   - `9bd4ff5 chore: ignore local private bare remote directory`
   - `2df6cf5 chore: initialize local private git baseline for omega v31`

跨平台关键配置（仓库级）：
1. `core.filemode=false`
2. `core.autocrlf=false`
3. `core.ignorecase=true`

仓库中的关键文件：
1. `.gitignore`（已排除 `data/`, `artifacts/`, `archive/`, `.local_remote/` 等）
2. `.gitattributes`（统一文本行尾策略，`.bat/.ps1` 保持 CRLF）

---

## 3. Windows 侧第一次接入（标准流程）

### 3.1 安装 Git

在 Windows 安装 Git for Windows（确保 `git` 命令可用）。

### 3.2 不要直接复用 Mac 的 working tree

必须从裸仓库克隆**Windows 本地工作副本**，避免跨系统同时写同一工作目录。

示例（PowerShell）：

```powershell
# 共享盘示例路径（按你的实际挂载盘符替换）
$REMOTE = "Z:\Omega_vNext\.local_remote\Omega_vNext.git"
$WORK = "D:\Omega_vNext_win"

git clone $REMOTE $WORK
cd $WORK
```

### 3.3 设置本地配置（仅此仓库）

```powershell
git config core.filemode false
git config core.autocrlf false
git config core.ignorecase true
```

> 说明：`core.autocrlf=false` 与仓库 `.gitattributes` 配合，避免跨平台行尾漂移导致噪音 diff。

---

## 4. 双机协作规则（最重要）

### 4.1 基本节奏

每次开始工作前：

```powershell
git switch main
git pull --ff-only
```

每次结束工作后：

```powershell
git add -A
git commit -m "feat/fix/docs: ..."
git push
```

### 4.2 严禁事项

1. Mac 与 Windows 同时修改同一 working tree
2. 在未 `pull` 最新 `main` 的情况下长时间开发后直接强推
3. 把 `data/`, `artifacts/` 之类大目录强行纳入版本库

---

## 5. 分支策略（推荐）

建议统一前缀：
1. `exp/*`：探索实验（可失败）
2. `fix/*`：缺陷修复
3. `refactor/*`：重构（不改行为）
4. `docs/*`：文档治理
5. `chore/*`：工程维护

示例：

```powershell
git switch -c exp/v31-topology-gate
git push -u origin exp/v31-topology-gate
```

合并策略（本地）：

```powershell
git switch main
git pull --ff-only
git merge --no-ff exp/v31-topology-gate
git push
```

---

## 6. 回滚与可逆操作

### 6.1 回退一个已提交变更（保留历史）

```powershell
git revert <commit_sha>
git push
```

### 6.2 查看变更图谱

```powershell
git log --graph --oneline --decorate --all
```

### 6.3 关键里程碑打标签

```powershell
git tag checkpoint/v31-20260207
git push origin checkpoint/v31-20260207
```

> 不建议用 `reset --hard` 回写共享分支历史。

---

## 7. 离线备份（强保密场景）

定期导出 bundle（单文件可冷备）：

```powershell
$DATE = Get-Date -Format "yyyyMMdd"
git bundle create "D:\backup\Omega_vNext_$DATE.bundle" --all
```

恢复示例：

```powershell
git clone "D:\backup\Omega_vNext_20260207.bundle" Omega_vNext_restore
```

---

## 8. 日常命令清单（Windows AI 快速参考）

```powershell
# 当前状态
git status
git branch -vv
git remote -v

# 同步主分支
git switch main
git pull --ff-only

# 开新分支
git switch -c fix/some-issue

# 提交
git add -A
git commit -m "fix: ..."
git push -u origin fix/some-issue

# 合并回 main
git switch main
git pull --ff-only
git merge --no-ff fix/some-issue
git push
```

---

## 9. 常见故障与处理

### 9.1 `index.lock` 残留

场景：命令中断后出现 `Unable to create .git/index.lock`

处理：
1. 确认无 Git 进程占用
2. 删除锁文件后重试

```powershell
Remove-Item .git\index.lock -Force
```

### 9.2 行尾（CRLF/LF）噪音

检查：
1. 仓库内存在 `.gitattributes`
2. `core.autocrlf=false`

若仍有噪音，先保证仅改业务文件，再最小提交。

### 9.3 push 被拒绝（非快进）

```powershell
git pull --rebase
git push
```

如有冲突：先手工解决，再 `git add` + `git rebase --continue`。

---

## 10. 与 OMEGA 开发规范对齐（关键）

1. 主干开发默认在 `omega_v3_core/*`
2. 根目录 `kernel.py/omega_math_core.py/trainer.py` 视为兼容 shim，不写新业务逻辑
3. 不把训练运行态文件与审计大产物纳入 Git 历史
4. 规则变更优先改 `.agent/principles.yaml`，再执行：

```bash
python3 tools/sync_agent_rules.py
python3 tools/sync_agent_rules.py --check
```

---

## 11. 最小执行 Checklist（Windows AI 开工前）

1. `git switch main`
2. `git pull --ff-only`
3. 新建分支 `git switch -c <type>/<topic>`
4. 完成功能后 `git add -A && git commit`
5. `git push -u origin <branch>`

---

## 12. 双向同步 SOP（Windows 改完 -> Mac；Mac 改完 -> Windows）

下面是严格的“接力棒”流程。核心原则只有两条：
1. 谁先改完，谁先 `commit + push`
2. 接力方先 `pull --ff-only`，再开始改

### 12.1 Windows 完成修改后，Mac 如何接力

Windows 侧（先提交并推送）：

```powershell
git status
git add -A
git commit -m "type(scope): summary"
git push
```

Mac 侧（接力前先同步）：

```bash
cd /Volumes/desktop-41jidl2/Omega_vNext
git switch main
git pull --ff-only
git log --oneline -n 5
```

若 Windows 推的是分支（非 `main`），Mac 侧接力方式：

```bash
cd /Volumes/desktop-41jidl2/Omega_vNext
git fetch origin
git switch <branch>
git pull --ff-only
```

### 12.2 Mac 完成修改后，Windows 如何接力

Mac 侧（先提交并推送）：

```bash
cd /Volumes/desktop-41jidl2/Omega_vNext
git status
git add -A
git commit -m "type(scope): summary"
git push
```

Windows 侧（接力前先同步）：

```powershell
git switch main
git pull --ff-only
git log --oneline -n 5
```

若 Mac 推的是分支（非 `main`），Windows 侧接力方式：

```powershell
git fetch origin
git switch <branch>
git pull --ff-only
```

### 12.3 冲突与并发保护

1. 任何一方 `push` 失败（non-fast-forward），先 `pull --rebase`，解决冲突后再推
2. 同一时段只允许一个主机在同一分支持续开发，另一方只读/同步
3. 交接时写一句简短 handoff 说明（改了什么、下一步做什么），避免 AI 误判上下文
4. 合并前确保主干最新并解决冲突

---

如果这份文档与现场仓库状态不一致，以以下来源为准：
1. `git remote -v`
2. `git log --oneline --decorate --max-count=20`
3. `.gitignore` / `.gitattributes`
