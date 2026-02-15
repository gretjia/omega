# OMEGA v5.2 Final Implementation Plan (Parallel Framing + 3-Host Sync + Cloud)

**Date:** 2026-02-15  
**Version:** v5.2 (The Epistemic Release)  
**Context (Current Progress):** Linux 已设置好；`2.6TB` 原始 `.7z` 正在复制进 Linux 的 `8TB USB4` 硬盘中，预计约 `1.5h` 完成。

---

## 0. 先回答你的两个意见点（结论）

### 0.1 “主程序是否保存在 windows1-w1？”
- **从仓库内状态证据看：是的，至少在 2026-02-14 时主仓库曾以 Windows 为主机。** `audit/v52_implementation_status.md` 明确写了 “Codebase Stable … Verified via smoke tests … on the Windows host”，并点名 `C:\\Omega_vNext` 为当时的工作路径。
- **但从今天开始建议把“主程序/主仓库”的定义改成：`Git 远端 = Source of Truth`。** windows1-w1 仍可作为主开发机/主跑机，但不再是唯一真相来源；Mac/Linux 都是“同一 repo 的克隆”，靠 `git pull` 同步。

### 0.2 “framing 很耗时，Windows1 + Linux 分工同时跑”
- **同意**，并且可把 framing 分成两个互不冲突的 shard（按日期/月份/年份分区），两台机器同时跑，最后把 frames 合并（本地合并或云端合并）。
- 关键是：**必须同一份代码版本、同一份 L2 config、同一套输出命名与 manifest**，否则后面训练会出现“数据口径漂移”。

---

## 1. v5.2 不可妥协的 DoD / 设计公理（执行中不再争论）

1. **指标换轨（双轨度量）**
   - `Phys_Alignment`：物理基线，仅作对照（预期 ~0.5 附近浮动，不要拿它当失败理由）。
   - **DoD 指标：`Model_Alignment > 0.6`**（在结构区间/高 Epiplexity 上的认知对齐），并同时满足：
     - `Topo_SNR > 3.0`
     - `|Orthogonality| < 0.1`
2. **工程换轨（禁止 to_dicts 递归爆内存）**
   - 任何会把 `Polars DataFrame -> List[Dict]` 的路径一律禁止用于大规模数据。
   - v5.2 已在 `omega_core/kernel.py` 做了张量化/向量化，IIR（`adaptive_y`）只保留轻量标量递推。
3. **杠铃架构（最小运维债）**
   - 本地（Windows1 + Linux）负责：解压、清洗、framing 产出 Parquet（重 I/O + 重 CPU）。
   - 云端负责：并行训练/寻优（可选，但能显著缩短“找上帝参数”的时间）。
   - 交易端（如果有 QMT）：只跑极简推理，必要时把模型拆成 `weights.json`，避免 sklearn/依赖地雷。

---

## 2. 三台电脑职责划分（推荐）

> 你说“三台电脑”，这里按最常见组合写：`Mac(控制塔) + Windows1-w1(重跑机A) + Linux(重跑机B)`。  
> 如果你第三台不是 Mac（比如第二台 Windows/QMT），把下面的“控制塔”换成你实际那台。

### 2.1 Mac（Control Tower）
- 代码编辑与审计文档维护（`git` 主控）。
- 生成/提交：manifest、分片清单、运行参数表。
- 云端作业触发（如果上 GCP/Vertex/Optuna sweep）。

### 2.2 Windows1-w1（Framing Shard A）
- 跑 framing（处理 shard A 的 `.7z`）。
- 同步 shard A 的 frames 到统一存储（本地合并盘或 GCS）。
- 可选：本机做“第一轮小样本训练/审计”，快速验证 DoD 逻辑。

### 2.3 Linux（Framing Shard B）
- 跑 framing（处理 shard B 的 `.7z`）。
- 同步 shard B 的 frames 到统一存储（本地合并盘或 GCS）。
- 你正在复制的 `2.6TB .7z -> 8TB USB4`：建议把 USB4 盘作为 **RAW 档案盘**；解压 staging 尽量走内置 NVMe（更快、更不伤 USB4 盘）。

---

## 3. 文件与同步：什么进 Git、什么不上 Git、真相在哪

### 3.1 Code（必须进 Git）
- repo：`Omega_vNext` 的代码与 `audit/*.md` 文档。
- 原则：任何会影响 framing/training 口径的改动必须 `git commit` 后再跑全量（避免“跑到一半换逻辑”）。

### 3.2 Config（建议进 Git，但要做“模板化”）
- 建议新增三份机器配置（文件名只是建议）：
  - `configs/hardware/windows1.yaml`
  - `configs/hardware/linux.yaml`
  - `configs/hardware/mac.yaml`（如果 Mac 不跑 framing 可只放占位）
- **模板化策略：**
  - repo 中放“可公开的相对路径/挂载点约定”。
  - 各机器本地允许放一个不进 git 的覆盖文件（比如 `configs/hardware/local_override.yaml`），用于真实盘符/真实挂载点。

### 3.3 Data（绝对不要进 Git）
1. 原始 `.7z`（2.6TB）：**只做校验与 manifest**，不进 git。
2. staging 解压目录（临时 CSV）：永远只做临时目录，任务结束必须清空。
3. 产物 frames（Parquet）：不进 git；**进入统一数据湖（本地汇聚盘或 GCS）**。
4. 模型 artifacts（`.pkl`、`production_config.json`、审计报告）：不进 git；但应同步到云端与至少 1 份本地备份。

---

## 4. 统一目录语义（跨机器一致，靠“语义”而不是盘符）

为避免路径在三台机器上各自硬编码，所有脚本/运行时只认下面 5 个语义路径：

- `RAW_ROOT`：原始 `.7z` 所在根目录（只读）
- `STAGE_ROOT`：单个 `.7z` 解压的临时目录（可删）
- `FRAMES_ROOT`：framing 输出 Parquet（日级）
- `ARTIFACTS_ROOT`：训练输出 `.pkl` / checkpoints / configs
- `RUNTIME_LOG_ROOT`：运行日志与 manifest（JSONL/MD）

**建议约定：**
- `RAW_ROOT` 放在 USB4 盘（容量大、顺序读为主）。
- `STAGE_ROOT` 放在内置 NVMe（解压 + 多进程读写更快）。
- `FRAMES_ROOT` 放在 USB4 盘或内置大盘（以写为主）。

---

## 5. 核心：Parallel Framing（Windows + Linux 同时跑）的实施方案

### 5.1 先做“manifest”，再分片（避免重复劳动）

**目标：** 在控制塔（建议 Mac）生成一个“全量归档清单”，并把分片结果固定成文件，确保两台机器跑的是互斥集合。

产物（建议放在 `audit/runtime/v52/`，本 repo 里可追踪）：
- `audit/runtime/v52/archive_manifest_7z.txt`：所有 `.7z` 的排序列表（相对路径或绝对路径都可，但要一致）
- `audit/runtime/v52/shard_windows1.txt`
- `audit/runtime/v52/shard_linux.txt`

**分片规则（推荐 2 选 1）：**
1. **按年份/月份目录切分（最直观）**
   - Windows1：例如跑 `2016-2020`
   - Linux：例如跑 `2021-2025`
   - 优点：简单；缺点：年份间数据量可能不均衡。
2. **按日期奇偶或 hash mod 2（最均衡、最省脑）**
   - 取文件名里的 `YYYYMMDD`，`int(YYYYMMDD) % 2 == 0` 给 Linux，奇数给 Windows1（或反之）。
   - 优点：天然负载均衡；缺点：目录跳跃（但不影响程序）。

> 如果你两台机器性能差距很大：用 `hash mod 4` 做 4 片，强机器跑 3 片，弱机器跑 1 片。

### 5.2 两台机器的 framing 输出必须“互不覆盖”

**强制要求：每台机器写到自己的 FRAMES_ROOT 子目录：**
- Windows1：`FRAMES_ROOT/frames_w1/`
- Linux：`FRAMES_ROOT/frames_linux/`

这样即使误处理了同一天，也只是产生“重复文件”，不会互相覆盖；后续合并时再去重。

### 5.3 运行方式（两种，选一个就行）

#### 方案 A（最少改代码）：按目录分工
- 做法：把 shard 对应的 `.7z` 放到不同目录（移动或硬链接/软链接），然后分别把 `storage.source_root` 指向各自目录。
- 适用：你不想动任何代码，只想立刻开跑。

#### 方案 B（推荐，改动极小）：支持 “按清单处理”
- 做法：新增一个小入口脚本 `tools/frame_from_list.py`（或给 `pipeline_runner.py` 加 `--archive-list`）。
- 输入：`--archive-list shard_windows1.txt`
- 输出：照现有 `Framer._process_archive()` 逐个处理。
- 优点：不需要移动/链接 TB 级数据；最清晰、最稳定。

（如果你认可方案 B，我下一步可以直接在 repo 里把这个脚本补齐并自测。）

---

## 6. 数据同步规划（3 台机器 + 云）

### 6.1 代码同步（强制：Git）
- 远端（GitHub/自建）作为唯一真相。
- 每台机器只做：
  - `git pull` 更新代码
  - 仅控制塔（或你指定的一台）负责 `git push`
- framing/training 开跑前固定一个 `commit hash`，写入 `audit/runtime/v52/run_meta.json`（避免中途换逻辑）。

### 6.2 frames 同步（推荐把云当“统一汇聚点”）

**推荐结构（GCS 举例）：**
- `gs://<bucket>/omega/v52/frames/host=windows1/....parquet`
- `gs://<bucket>/omega/v52/frames/host=linux/....parquet`
- `gs://<bucket>/omega/v52/artifacts/...`

**同步节奏：**
- framing 每处理完 N 天（比如 20 天或 50GB），就增量同步一次到云端（防止本地单点故障）。
- 同步是“追加式”，不要做 destructive mirror（避免误删云端）。

> 你也可以反过来：先在本地合并盘汇总，再由一台机器统一上传云端。取决于你上行带宽与是否想让两台机器都装云 SDK。

### 6.3 模型 artifacts 同步（必须双备份）
- `ARTIFACTS_ROOT` 里最重要的：
  - `omega_v5_model_final.pkl` / `checkpoint_rows_*.pkl`
  - `production_config.json`
  - 每轮 `audit report md`
- 要求：至少同时存在 **云端 1 份 + 本地 1 份**（任意机器或外置盘）。

---

## 7. Training / Audit / Tuning（与 framing 并行推进）

### 7.1 不等全量 framing 完成就开始训练
- v5.2 的训练器是 `partial_fit` 思路，本质上支持“增量扩数据”。
- 当 frames 产出到一个可用规模（例如 30-60 个交易日）：
  - 立刻跑一轮训练，拿到 `Model_Alignment/Topo_SNR/Orthogonality` 的基线。
  - 先把“口径”跑通，避免 framing 全跑完才发现 DoD 指标逻辑/数据字段缺失。

### 7.2 参数寻优的最小闭环（本地 Optuna -> 可选云端并行）
- 优先寻优的参数（从 v52 文档共识提炼）：
  - `peace_threshold`
  - `srl.y_ema_alpha`
  - `epiplexity.sigma_gate_quantile` 或 `epiplexity.sigma_gate`
- Objective：`Maximize Model_Alignment`
- Constraints：`Topo_SNR >= 3.0` 且 `|Orthogonality| <= 0.1`
- 先本地跑 30-50 次 trial；若耗时太久再把 trial 并行丢云端。

---

## 8. 最终交付物（你应该在什么路径看到什么）

1. **frames（训练数据湖）**
   - 本地：`FRAMES_ROOT/frames_w1/*.parquet` + `FRAMES_ROOT/frames_linux/*.parquet`
   - 云端：`.../omega/v52/frames/host=.../*.parquet`
2. **artifacts（模型与配置）**
   - `.../omega/v52/artifacts/<run_id>/omega_v5_model_final.pkl`
   - `.../omega/v52/artifacts/<run_id>/production_config.json`
3. **审计报告**
   - `audit/runtime/v52/<run_id>/audit_report.md`
4. **运行元信息（可复现）**
   - `audit/runtime/v52/<run_id>/run_meta.json`：
     - `git_commit`
     - `l2_cfg_digest`（配置摘要）
     - `raw_manifest_digest`
     - `shard_rule`
     - `host_paths`（仅语义，不写隐私盘符也行）

---

## 9. 时间线建议（以“今天开始”估算）

1. **T+0 ~ T+2h**：数据拷贝完成后抽样 `7z t` 校验 + 生成 manifest + 分片文件。
2. **T+2h ~ T+48h**：Windows1 + Linux 并行 framing（持续产出 frames 并同步到统一存储）。
3. **T+6h 起**（不等全量）：拿到首批 frames 后开始训练与 DoD 审计闭环。
4. **T+24h 起**：开始 Optuna sweep（本地或云端）。
5. **T+48h 后**：冻结最佳 artifacts，准备（可选）QMT/实盘集成。

---

## 10. 下一步需要你确认的 3 个关键信息（我才能把“分片 + 同步”写到可直接执行）

1. “三台电脑”分别是什么系统与主要用途？（Mac/Windows/Linux？还是 2 台 Windows + 1 台 Linux？）
2. 原始 `.7z` 的目录结构是什么？（是否类似 `YYYY/YYYYMM/YYYYMMDD.7z`）
3. 云端你准备用什么作为数据湖？（GCS / S3 / 阿里 OSS / 先本地汇聚盘后再上传）

一旦你给出这 3 个答案，我可以把本计划里的 “分片规则 + 目录约定 + 同步命令/脚本” 固化成可直接运行的脚本集合（并把 `方案 B: --archive-list` 的 framing 入口补齐）。

