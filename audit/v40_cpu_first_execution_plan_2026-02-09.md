# OMEGA v40 CPU-First 执行方案（不改数学核心，不降结果质量）

日期：2026-02-09  
适用版本：v40 / Patch-02 对齐代码基线  
适用环境：Windows 主机（AMD AI Max 395, 128GB unified memory）+ Mac 监控

---

## 1. 目标与边界

### 1.1 目标
- 聚焦 `frame` 阶段提速（首要瓶颈），并同步保证 `train/backtest` 可无缝衔接。
- 在**不改变数学核心与结果质量**前提下提升吞吐与稳定性。
- 方案默认不引入 GPU，采用 CPU + I/O + 并行调优。

### 1.2 明确边界（本方案不做）
- 不改动核心数学定义与交易逻辑语义（Trinity / SRL / Epiplexity / Topology 的公式与判定语义不变）。
- 不引入 GPU 框架迁移（cuML / PyTorch 重写）作为当前阶段任务。
- 不放宽 Train/Backtest 数据隔离与 fail-closed 机制。

---

## 2. 约束对齐（Constitution + SKILL + v40 patch_02）

### 2.1 Constitution 强约束
- `OMEGA_CONSTITUTION.md` Article I/II：保持数学三位一体、递归与体积时钟原则。
- Article V：`config.py` 为基线，运行态参数来自 artifact/snapshot，不回写污染基线。
- Dataset Role Isolation：Train/Backtest 清单必须构造式隔离、默认 overlap hard fail。

### 2.2 SKILL 强约束
- `ops`：全流程 staging-first、可恢复执行、状态 JSON 持续写盘、关键链路禁止无界 `collect()`。
- `engineering`：优先向量化、禁止链路关键路径做无界全量 collect。
- `hardcode_guard`：生产路径禁止新增业务硬编码阈值；仅允许数值稳定常数（需显式命名）。
- `v3_mainline_guard`：仅在 `omega_v3_core/*` 与现行 pipeline 主干演进，不向根 shim 增加业务逻辑。
- `math_consistency`：训练与推理特征路径一致性必须可验证。

### 2.3 v40 patch_02 对齐点（必须保持）
- 保持 Patch-02 的 meta-priors 机制：`PLANCK_SIGMA_GATE`、`ANCHOR_Y` 来自数据分布，不手工硬编码回退。
- 保持 `energy gate + anchor recursion` 生效语义不变。
- 保持并行 frame/train/backtest 的 fail-closed 与可恢复协议。

---

## 3. 当前瓶颈（基于真实代码路径）

### 3.1 frame 主瓶颈
- `tools/run_l2_audit_driver.py`
  - 每个归档执行：解压 -> kernel -> 小文件 parquet 输出，I/O 与进程调度开销高。
  - worker 内部解压命令当前未对 7z 线程进行显式约束，存在“多进程 * 多线程”抢核风险。
  - 默认每个 symbol/date 生成小 parquet，文件系统元数据开销大。

### 3.2 训练/回测衔接风险点
- frame 尾部 report 不能阻塞 train/backtest 链路（当前已默认 `--skip-report`，必须保持）。
- 任何 frame 产出都必须通过兼容性预检 + split preflight 才能进入 train/backtest。

---

## 4. 执行总策略（CPU-First，分阶段）

## Phase 0：基线测量（只观测，不改代码）

目标：拿到可比较的基线吞吐，避免“感觉优化”。

执行：
1. 固定同一批归档样本（建议 500~1000 个 archive）跑 frame。
2. 记录：
   - archives/hour
   - parquet files/hour
   - CPU 利用率、内存峰值、stage 盘占用峰值
   - 单归档耗时分布（P50/P95）
3. 将结果写入：
   - `audit/v40_runtime/windows/frame/frame.log`
   - `audit/v40_runtime/windows/frame/frame_status.json`
   - 新增审计记录（按日期）

验收门：
- 基线数据完整且可复现（同命令二次运行偏差可解释）。

---

## Phase 1：参数级优化（不改数学，不改核心公式）

目标：在不改代码语义下先吃掉最大收益。

执行项：
1. Worker 扫描（frame）
   - 对 `FrameWorkers` 做分档压测：`12 / 16 / 20 / 22`。
   - 选择 `archives/hour` 最高且系统稳定（内存<88%，无长时间掉速）的档位。
2. 强化 staging 策略
   - 保持 `--copy-to-local` + `C:/Omega_level2_stage`。
   - 保持 cleanup 默认开启，避免 stage 堆积反噬 I/O。
3. 保持 frame 链路默认 `--skip-report`
   - report 改为独立异步任务，不阻塞 train/backtest 启动。

建议执行命令（Windows）：
```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\start_v40_pipeline_win.ps1 `
  -Stage frame `
  -FrameWorkers 20 `
  -FrameOutputDir data/level2_frames_v40_win `
  -FrameStageDir C:/Omega_level2_stage
```

验收门：
- 相比 Phase 0，frame 吞吐提升 >= 20%，且无 crash / 无卡死 / 状态持续更新。

---

## Phase 2：工程级优化（小改代码，数学语义不变）

目标：继续提升 frame 吞吐，保持结果等价。

执行项（按顺序）：
1. 增加 frame 细粒度耗时日志（解压/内核/写盘）
   - 在 `run_l2_audit_driver.py` 对每 archive 写 `extract_sec/kernel_sec/write_sec`。
   - 目的：定位瓶颈占比并指导后续优化，不改计算结果。
2. 7z 线程约束参数化（建议默认 1）
   - 新增 CLI（如 `--seven-zip-threads`），传入 7z 参数（例如 `-mmt=1`）。
   - 目的：避免多 worker 场景线程过订阅。
3. 解压白名单
   - 只解压 kernel 真正消费的行情 CSV（减少无效 I/O）。
4. 输出文件策略优化（可选）
   - 从“极小 parquet 粒度”升级为“按归档/批次分块输出”，减少文件系统元数据压力。
   - 前提：不改变下游 schema 与 train/backtest 读取契约。

验收门：
- 相比 Phase 1，再提升 >= 15% 或显著降低长尾耗时（P95）。
- 通过 frame->train/backtest 兼容性预检。

---

## Phase 3：衔接验证（train/backtest smoke）

目标：证明优化后 frame 产物可无缝进入训练与回测。

执行：
1. 运行兼容性检查：
   - `tools/check_frame_train_backtest_compat.py`
2. 运行 split preflight：
   - `tools/preflight_dataset_split_v40.py`
3. 运行 fixed split smoke（必须遵守官方分割）：
   - Train: 2023,2024
   - Backtest: 2025 + 202601

命令（Windows，官方固定入口）：
```powershell
cd D:\Omega_vNext
powershell -ExecutionPolicy Bypass -File jobs\windows_v40\run_v40_train_backtest_fixed_split_win.ps1
```

验收门：
- overlap_count == 0
- train/backtest 均可完成并写入终态 status（completed/failed 明确）
- 关键审计指标无异常劣化（同策略口径比较）

---

## Phase 4：质量与一致性审计（recursive audit）

目标：确认“提速不变质”。

必做检查：
1. 数学一致性
   - 不修改 `omega_v3_core/omega_math_core.py` 的核心公式语义。
   - 不改变 `omega_v3_core/kernel.py` 中 Patch-02 物理门控与锚定更新规则。
2. 数据契约一致性
   - frame 输出字段与 train/backtest 消费字段完全兼容。
3. 结果质量一致性
   - 对同一固定样本比较优化前后：样本数、标签分布、关键指标（PnL、Topo_SNR、Orthogonality、Vector_Alignment）偏差在可接受范围。
4. 可恢复性一致性
   - 中断后 resume 能正确接续（frame `_audit_state.jsonl`、train checkpoint、backtest state）。

输出文档：
- `audit/v40_frame_optimization_recursive_audit_<date>.md`

---

## 5. 变更白名单 / 黑名单

### 5.1 允许改动（本方案）
- `tools/run_l2_audit_driver.py`（观测、调度、I/O、日志、解压参数）
- `jobs/windows_v40/start_v40_pipeline_win.ps1`（默认参数/执行编排）
- `jobs/windows_v40/README.md` 与 handover 文档（运行说明）

### 5.2 禁止改动（本方案）
- 不修改数学公式语义：
  - `omega_v3_core/omega_math_core.py` 核心计算定义
  - `omega_v3_core/kernel.py` 中 Patch-02 关键门控/锚定语义
- 不新增生产硬编码业务阈值。
- 不取消数据集角色隔离与 overlap hard-fail。

---

## 6. 风险与回滚

### 6.1 主要风险
- worker 拉高后出现 I/O 抖动导致吞吐反降。
- 7z 线程/进程叠加造成抢核。
- 输出粒度变更若处理不当，影响 train/backtest 读取契约。

### 6.2 回滚策略
- 逐 phase 落地，每 phase 独立提交。
- 若某 phase 不达标，回滚到上个稳定提交，不跨 phase 连续叠改。
- 保留基线命令与 runtime 日志用于 A/B 复盘。

---

## 7. 交付物与里程碑

### 7.1 交付物
- 参数调优记录 + 基线对比表
- 优化后 pipeline 脚本与说明文档
- recursive audit 报告
- 可直接给 Windows AI coder 的运行命令清单

### 7.2 里程碑
1. M1（Phase 1 完成）：frame 吞吐稳定提升 >=20%
2. M2（Phase 2 完成）：在 M1 基础上继续提速或显著缩短 P95
3. M3（Phase 3/4 完成）：train/backtest 衔接通过 + 质量不降 + 可恢复性通过

---

## 8. 单行执行原则（供多 AI 协作）

> 先测量，后优化；先参数，后代码；先保持数学不变，再谈更大重构。  
> 任何提速改动必须同时满足：Constitution 合规、SKILL 合规、Patch-02 合规、结果质量不降。

