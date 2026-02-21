# OMEGA Handover Log

> 此文件由 AI 在每次 handover 时更新。最新条目在最上方。
> 新 AI 读取最近 1-2 条即可快速接手。

---

## [2026-02-21 09:00] Session Handover — v6.1 Anti-Fragile Framing (FAILED)

### Completed This Session

- Applied **8 anti-fragile patches** to `kernel.py`, `trainer.py`, `omega_etl.py`, `v61_run_local_backtest.py`
- Patches from `tools/v61_fix_final.md`: overnight phase reset, infinity shield, maxtasksperchild
- Patches from `tools/v61_fix_final_2.md`: LOB flux `.over()` isolation, singularity immunity, safe column extract, I/O panic prevention
- Fixed ETL `scan_l2_quotes` concat for mixed CSV schemas (`diagonal_relaxed`)
- Attempted tmpfs RAM disk acceleration (35GB at `/omega_pool/temp_framing/`)
- Lowered ZFS ARC from 16GB to 8GB

### Current State

- **数据状态**: ❌ 0 个新 parquet 帧产出。5次部署尝试全部因内存爆炸失败
- **代码状态**: 所有 8 个补丁已提交 (`ce2df71`)，已推送至两节点
- **阻塞项**: Polars ETL 每个 Worker 峰值 20-30GB，123GB Linux 无法安全运行 ≥2 workers

### Next AI Should

1. **读取详细 postmortem**: `handover/ai-direct/entries/20260221_090000_v61_antifragile_framing_postmortem.md`
2. **重构 ETL 内存管理** — `build_l2_frames()` 需要流式/分块处理，不能全量 `.collect()`
3. **修复 CSV schema 处理** — 跳过缺少 L2 深度列的 CSV，而非 `diagonal_relaxed` 填 null
4. **考虑单 Worker 模式** — 1 worker 虽慢但保证在 123GB 内完成
5. **注意 ZFS ARC 已降为 8GB** — 恢复命令: `echo 17179869184 | sudo tee /sys/module/zfs/parameters/zfs_arc_max`
6. **tmpfs 35GB 仍挂载在 Linux** — 决定保留或卸载: `sudo umount /omega_pool/temp_framing/`

### Files Modified

- `omega_core/kernel.py` — 2 patches (overnight reset + infinity shield)
- `omega_core/trainer.py` — 2 patches (safe extract + singularity immunity)
- `omega_core/omega_etl.py` — 2 patches (LOB flux isolation + diagonal_relaxed)
- `tools/v61_run_local_backtest.py` — 2 patches (maxtasksperchild + sequential scan)
- `tools/v61_linux_framing.py` — maxtasksperchild=5
- `tools/v61_windows_framing.py` — maxtasksperchild=1
- `tools/v61_fix_final.md` — [NEW] patch directives
- `tools/v61_fix_final_2.md` — [NEW] patch directives
- `handover/ai-direct/entries/20260221_090000_v61_antifragile_framing_postmortem.md` — [NEW] detailed postmortem

### Warnings

- ⚠️ `diagonal_relaxed` concat 产生的帧里 L2 深度列全为 null — 这是垃圾数据
- ⚠️ earlyoom 会静默杀死 Worker 子进程而主进程继续空转
- ⚠️ ZFS ARC 已被手动降为 8GB，重启后会恢复默认值
- ⚠️ tmpfs 35GB 仍挂载，重启后消失

---

## [2026-02-08 02:30] Session Handover - v40 Windows Runtime Handover + Resume Hardening

### Completed This Session

- 为 v40 新增 Windows 统一运行入口：`jobs/windows_v40/start_v40_pipeline_win.ps1`（`frame/train/backtest/all`）
- 为 `frame/train/backtest` 新增状态快照与断点续作支撑（`status_json` / `state_file` / checkpoint 追踪）
- 增加跨平台监控脚本：`tools/v40_runtime_status.py`（Mac 侧读取 Windows 运行状态）
- 新建交接手册：`audit/v40_windows_handover_runtime_2026-02-08.md`
- 根 README 已登记新手册索引，便于后续 AI 快速定位

### Current State

- 运行目录已统一到：`audit/v40_runtime/windows/{frame,train,backtest,manifests}`
- 断点续作机制已就位：frame(`_audit_state.jsonl`) / train(`checkpoint_rows_*.pkl`) / backtest(`backtest_state.json`)
- 当前尚未在该目录产生新一轮正式运行状态文件（`status=missing` 属于未启动状态）

### Next AI Should

1. 在 Windows 启动第一轮 v40 实跑：`powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 -Stage all`
2. Mac 侧持续监控：`python3 tools/v40_runtime_status.py --json`
3. 若状态超过 10 分钟不更新，先降 workers 再重试单阶段定位（优先保留续作状态）

### Files Modified

- `parallel_trainer/run_parallel_v31.py` - 训练状态输出、内存守卫、checkpoint 粒度与进度增强
- `parallel_trainer/run_parallel_backtest_v31.py` - 回测状态输出、state 续作、周期保存与异常计数
- `tools/run_l2_audit_driver.py` - frame 状态输出、可配置内存阈值、跨平台 7z 解析
- `tools/v40_runtime_status.py` - [新建] 跨机运行状态汇总/预警脚本
- `jobs/windows_v40/start_v40_pipeline_win.ps1` - [新建] Windows v40 统一执行脚本
- `jobs/windows_v40/README.md` - 运行/恢复/监控说明补充
- `audit/v40_windows_handover_runtime_2026-02-08.md` - [新建] Windows AI 专用 handover 手册
- `README.md` - 新增 v40 Windows Runtime Handover 文档索引

### Validation Gates

- README sync: PASS (`python3 tools/check_readme_sync.py`)

### Warnings

- 仓库中存在大量历史未提交改动与审计文件，切勿在 handover 过程中误清理
- Windows 共享盘可能导致阶段日志短时停更，需结合 `status_json` 与日志尾部共同判读

---

## [2026-02-05 14:00] Session Handover - Trainer + Auto-Focus Upgrade

### Completed This Session

- 升级 `omega_v3_core/trainer.py`：接入 Reduce、标签中性区、结构采样、稳健变换
- 新增 `omega_v3_core/physics_auditor.py`：Auto-Focus 扫描 + 连续 Y 校准
- 新增 `load_l2_pipeline_config()`，运行期自动加载 `model_audit/production_config.json`
- 更新 README：根目录 / `omega_v3_core` / `data`
- 更新递归审计报告：`audit/v3_patch_artitecture_audit_response.md`
- 更新 handover：`audit/20260205_handover.md`

### Current State

- 代码升级完成，训练/回测未执行（交由其它 AI coder）
- 本机 macOS 缺 `polars`，未做 import sanity check

### Next AI Should

1. 在有 `polars` 的环境做最小 import/sanity check
2. 重新生成 `level2_frames_*`（包含 trade/cancel 字段）
3. 按审计要求执行训练/回测（由其它 AI coder 接手）

### Files Modified

- `omega_v3_core/kernel.py`
- `omega_v3_core/omega_math_core.py`
- `omega_v3_core/omega_etl.py`
- `omega_v3_core/trainer.py`
- `omega_v3_core/physics_auditor.py`
- `omega_v3_core/README.md`
- `config.py`
- `run_l2_audit.py`
- `README.md`
- `data/README.md`
- `audit/v3_patch_artitecture_audit_response.md`
- `audit/20260205_handover.md`
- `.agent/skills/ai_handover/handover_log.md`

### Warnings

- 本机缺 `polars`，尚未做 import 级验证
- 训练/回测交由其它 AI coder，当前不执行

---

## [2026-02-05 12:00] Session Handover - v3 Patch Upgrade + Recursive Audit

### Completed This Session

- 升级 `omega_v3_core/` 对齐 `audit/v3_patch_artitecture_audit.md`（Map-Reduce 内核 + Peace Protocol + Spoofing 过滤 + 全息拓扑归一化）
- 更新 ETL：新增 `lob_flux`，聚合 `trade_vol` / `cancel_vol`
- 更新数学内核：`calc_physics_state` + 标准化全息拓扑（Signed Area + Energy）
- 更新配置：新增 Y 递归边界、peace/spoofing/energy gate 相关阈值
- 生成递归审计报告：`audit/v3_patch_artitecture_audit_response.md`

### Current State

- v3 核心升级已完成，训练/回测未执行（交由其它 AI coder）
- 本机 macOS 缺 `polars`，暂未做 import sanity check

### Next AI Should

1. 在有 `polars` 的环境做最小 import/sanity check
2. 按审计要求执行训练/回测（由其它 AI coder 接手）

### Files Modified

- `omega_v3_core/kernel.py`
- `omega_v3_core/omega_math_core.py`
- `omega_v3_core/omega_etl.py`
- `omega_v3_core/README.md`
- `config.py`
- `audit/v3_patch_artitecture_audit_response.md`
- `.agent/skills/ai_handover/handover_log.md`

### Warnings

- 本机缺 `polars`，尚未做 import 级验证
- 训练/回测交由其它 AI coder，当前不执行

---

## [2026-02-05 00:00] Session Handover - v3 Full Run + Core Path Correction

### Completed This Session

- 更新交接文档：`audit/20260205_handover.md`
- 同步最新状态：v3 全量训练 + 2025 样本外回测已完成
- 明确核心代码位置：v3 核心代码在 `omega_v3_core/`，根目录代码仅作旧版/L1参考

### Key Changes

- v3 结果文件确认：
  - 回测分析：`audit/v3_full_bactest_results_analysis.md`（注意拼写：bactest）
  - 训练分析：`audit/v3_training_analysis.md`
- 交接文件中新增“最新进展”与关键指标摘要（仅记录，不做升级）

### Current State

- v3 全量训练完成（2023+2024 合并 ~50M frames）
- v3 2025 样本外回测完成
- 审计师正在对 v3 结果做审计
- **不执行任何升级/改动**，仅同步状态

### Next AI Should

1. 等待审计师结论（不要提前升级）
2. 如需改动，优先在 `omega_v3_core/` 进行

### Files Modified

- `audit/20260205_handover.md` - [更新：新增 v3 全量结果与核心路径修正]
- `.agent/skills/ai_handover/handover_log.md` - [新增本次条目]

### Warnings

- v3 回测文件名为 `v3_full_bactest_results_analysis.md`，注意拼写
- 当前阶段不允许任何升级操作，等待审计结论

---

## [2026-02-03 08:27] Session Handover - SKILL Cleanup

### Completed This Session

- **审计并清理所有 SKILL 文件**，移除过时版本引用和硬编码参数
- 更新 `omega_development/SKILL.md` - 移除 v10.6, v25.01 硬编码参数引用，保留调试经验
- 更新 `evolution_knowledge/SKILL.md` - 移除 LOCKED 概念，引用 Constitution 动态原则
- 更新 `evidence_based_reasoning/SKILL.md` - 移除 v2200/v2202 引用，更新示例
- 更新 `math_consistency/SKILL.md` - 移除 versions/vXXXX 路径
- 更新 `omega_data/SKILL.md` - 修正路径为 Omega_vNext，添加 L2 数据说明
- 更新 `ai_handover/SKILL.md` - 移除 versions/v2500 引用

### Key Changes

- **Constitution 优先**: STOP_LOSS/TAKE_PROFIT 硬编码现在被明确标记为 PROHIBITED
- **动态参数原则**: 所有交易阈值必须是分布的动态函数，不允许静态值
- **移除僵尸代码章节**: 不再引用不存在的 versions/vXXXX 目录结构

### Current State

- **SKILL 库**: 已清理，与 Constitution 一致
- **数据状态**: 不变 (5000万帧待合并)
- **阻塞项**: 无

### Next AI Should

1. **合并 Parquet 数据** - 将两个 L2 目录合并或配置多目录读取
2. **启动 Maxwell TCN 训练** - 使用 ~5000万帧数据
3. **实现动态阈值机制** - 按 Constitution Article II 要求

### Files Modified

- `.agent/skills/omega_development/SKILL.md` - [重写]
- `.agent/skills/evolution_knowledge/SKILL.md` - [重写]
- `.agent/skills/evidence_based_reasoning/SKILL.md` - [重写]
- `.agent/skills/math_consistency/SKILL.md` - [重写]
- `.agent/skills/omega_data/SKILL.md` - [重写]
- `.agent/skills/ai_handover/SKILL.md` - [更新]

### Warnings

- 代码中可能仍有硬编码参数残留，需在实现时逐步替换为动态计算

---

## [2026-02-03 08:00] Session Handover

### Completed This Session

- 阅读项目全部核心文档 (Constitution, README, Bible.md, 6个Skills)
- 创建 `ai_handover` SKILL.md - AI 专用交接协议
- 创建 `/handover` workflow - 交接流程定义
- 确认双机并行训练已完成 (Win2023 + Mac2024)

### Current State

- **数据状态**:
  - `level2_frames_win2023/`: 2679万帧 (2023年, 已完成)
  - `level2_frames_mac2024/`: 2280万帧 (2024年, 已完成)
  - 总计 ~5000万帧待合并
- **代码状态**: 稳定，无待修改项
- **阻塞项**: 无

### Next AI Should

1. **合并 Parquet 数据** - 将两个目录的数据合并或配置多目录读取
2. **启动 Maxwell TCN 训练** - 使用 ~5000万帧数据
3. **实现年份分层采样** - 避免 2023/2024 分布偏移

### Files Modified

- `.agent/skills/ai_handover/SKILL.md` - [新建] AI 交接协议
- `.agent/workflows/handover.md` - [新建] 交接 workflow
- 本文件 - [新建] handover 日志

### Warnings

- `audit/level2_v3_audit_report.md` 可能被双端覆盖，需检查
- 2024年 Topo_SNR (0.14) 低于 2023年 (0.17)，训练时注意信号衰减

---

## [Initial Entry] Project Setup

项目初始状态记录。详见 `.agent/skills/ai_handover/SKILL.md` Section 4。
