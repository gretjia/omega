# Omega 文件体系审计与去版本号迁移方案（2026-02-13）

## 执行状态（2026-02-13）

- Phase 1 已执行完成：第 4 节所列 20 个“v5 本轮未使用文件”已迁入  
  `archive/legacy/2026-02-13/v5_runtime_unused/`
- 路径映射索引已生成：`audit/v5_runtime/windows/ARCHIVE_INDEX.md`
- README 入口已更新到当前可用全链路 detached 脚本与归档方案入口。
- 执行后快照（同日复核）:
  - 仓库可见文件总数（`rg --files`）: `269`
  - 含版本号命名痕迹文件（`rg --files | rg '(^|/|_|-)v[0-9]+'`）: `117`
  - `audit/v5_runtime/windows` 活跃文件数: `18`
  - `archive/legacy/2026-02-13/v5_runtime_unused` 已归档文件数: `20`

## 1. 审计基线（当前现状）

- 仓库可见文件总数（`rg --files`）: `286`
- 含版本号命名痕迹文件（路径或文件名包含 `v\d+`）: `132`
- 本次 v5 运行目录文件数: `37`
- 本次 v5 运行核心产物（保留）: `17`
- 本次 v5 运行未使用候选（可归档）: `20`

结论:
- 版本号命名已渗透到运行脚本、审计文档、历史工具，存在升级引用扰动风险。
- 可按“先冻结活跃路径，再归档未用文件，再重命名活跃入口”的顺序执行，风险可控。

## 2. 命名治理目标（未来规则）

### 2.1 核心规则

1. 活跃文件名不包含版本号（禁止 `v\d+`）。
2. 版本信息不放在文件名，改放到:
   - 运行元数据（`run_id`, `schema_rev`, `model_rev`）
   - 文档 front-matter
   - archive 路径层级
3. 活跃路径固定，历史版本只进 `archive/legacy/...`。

### 2.2 目标目录语义

- 活跃运行产物: `audit/runtime/windows/...`
- 活跃规格文档: `audit/spec/...`
- 历史文档与旧流水线: `archive/legacy/<YYYYMMDD>/...`

## 3. 活跃路径重命名映射（建议）

### 3.1 训练/回测入口

- `parallel_trainer/run_parallel_v31.py` -> `parallel_trainer/train_parallel.py`
- `parallel_trainer/run_parallel_backtest_v31.py` -> `parallel_trainer/backtest_parallel.py`

### 3.2 运行目录

- `audit/v5_runtime/windows/...` -> `audit/runtime/windows/...`
- `audit/v5_runtime/windows/run_full_noresume_detached.ps1` -> `audit/runtime/windows/run_full_detached.ps1`

### 3.3 规格与说明

- `audit/v5.md` -> `audit/spec/physics.md`
- `audit/v5_auditor_intent.md` -> `audit/spec/auditor_intent.md`
- `audit/v5_explain.md` -> `audit/spec/explain.md`
- `v5_auditor_report.py` -> `auditor_report.py`

说明:
- 先复制/重命名生成新入口，再保留旧路径 shim（1 个迁移周期）避免任务中断。

## 4. 本次 v5 未使用文件归档清单（20 个）

以下文件未参与本次 `full_noresume` 主流水线，可归档到 `archive/legacy/2026-02-13/v5_runtime_unused/...`:

1. `audit/v5_runtime/windows/backtest/backtest_state_full_allow_v2.json`
2. `audit/v5_runtime/windows/backtest/backtest_state_probe_5d.json`
3. `audit/v5_runtime/windows/backtest/backtest_state_probe_5d_allow.json`
4. `audit/v5_runtime/windows/backtest/backtest_state_probe_5d_allow_v2.json`
5. `audit/v5_runtime/windows/backtest/backtest_status_full_allow_v2.json`
6. `audit/v5_runtime/windows/backtest/backtest_status_probe_5d.json`
7. `audit/v5_runtime/windows/backtest/backtest_status_probe_5d_allow.json`
8. `audit/v5_runtime/windows/backtest/backtest_status_probe_5d_allow_v2.json`
9. `audit/v5_runtime/windows/backtest/run_backtest_detached.ps1`
10. `audit/v5_runtime/windows/launch_full_noresume.bat`
11. `audit/v5_runtime/windows/manifests/backtest_files_probe_5d.txt`
12. `audit/v5_runtime/windows/manifests/train_files_probe_5d.txt`
13. `audit/v5_runtime/windows/pipeline/sp_test.txt`
14. `audit/v5_runtime/windows/pipeline/start_test.txt`
15. `audit/v5_runtime/windows/train/run_train_detached.ps1`
16. `audit/v5_runtime/windows/train/train.err.log`
17. `audit/v5_runtime/windows/train/train_status_foreground.json`
18. `audit/v5_runtime/windows/train/train_status_probe12.json`
19. `audit/v5_runtime/windows/train/train_status_probe_5d.json`
20. `audit/v5_runtime/windows/train/train_status_stability12.json`

## 5. 仓库级归档建议（非本轮立即执行）

建议迁入 `archive/legacy/2026-02-13/`:

- `jobs/windows_v40/**`
- `tools/*v40*.py`
- `tools/inspect_v3_artifact.py`
- `pipeline/adapters/v3_adapter.py`
- 历史审计文档:
  - `audit/v3*`
  - `audit/v31*`
  - `audit/v34*`
  - `audit/v40*`
  - `audit/v6*`
  - `audit/v1001.md`
  - `audit/_v31_*`

说明:
- `audit/v5_*` 仍有当前运行链证据价值，先不归档。

## 6. 分阶段执行计划

### Phase 0: 冻结活跃集合（只读）

产出:
- `audit/runtime/active_file_allowlist.txt`
- `audit/runtime/migration_manifest.json`

动作:
1. 固化本轮主链路文件清单（训练、回测、manifest、脚本、checkpoint snapshot）。
2. 对 active 文件计算哈希，作为回滚基线。

### Phase 1: 归档未使用 v5 文件（低风险）

动作:
1. 按第 4 节清单 move 到 `archive/legacy/2026-02-13/v5_runtime_unused/`。
2. 在原目录生成 `ARCHIVE_INDEX.md`（记录原路径 -> 新路径）。

验收:
- `audit/runtime/windows/` 中只剩 active 路径与本轮证据。

### Phase 2: 创建去版本号新入口（双轨）

动作:
1. 新增无版本入口文件（train/backtest/runtime 脚本）。
2. 旧版本入口改为 shim（内部转调新入口并打印 deprecation 提示）。
3. 更新 README 和自动化任务引用到新入口。

验收:
- 新旧入口均可跑通同一流水线；结果一致。

### Phase 3: 全仓引用替换 + 禁止新版本号命名

动作:
1. 批量替换路径引用（README/docs/jobs/tools）。
2. 加入命名门禁脚本（CI/本地 pre-commit）:
   - 活跃目录出现 `v\d+` 文件名直接失败。

验收:
- 活跃目录零版本号命名。
- 历史文件全部在 `archive/legacy/...`。

## 7. 风险点与控制

1. Windows 计划任务仍指向旧脚本  
控制: 先做 shim，任务分批切换，不直接删旧文件。

2. 文档引用断链  
控制: 先全局替换引用，再迁移文件。

3. 外部 agent 使用硬编码路径  
控制: 提供 `migration_manifest.json` 和 `ARCHIVE_INDEX.md`，保留一周期兼容层。

4. 回滚困难  
控制: 每阶段完成后打 tag，并保存哈希快照。

## 8. 建议执行顺序（最小中断）

1. 先执行 Phase 1（仅归档 v5 未使用 20 文件）。  
2. 再执行 Phase 2（建立无版本新入口 + shim）。  
3. 最后执行 Phase 3（全仓路径替换与门禁）。  

该顺序可确保你当前 `full_noresume` 主流水线不受影响。
