# Omega_vNext -> Vertex AI 导入资料包（提交版）

更新时间：2026-02-14  
目标：让 Vertex AI 在不了解历史上下文的情况下，快速理解 OMEGA_vNext 的系统结构、核心代码、依赖、运行状态与约束，并输出可执行的导入/提质方案。

---

## 1. 项目定位与目标

OMEGA_vNext 是一个面向中国 A 股 Level-2 数据的量化研究与训练系统，核心是“物理先验 + 机器学习”混合流水线：

1. 从 Level-2 Tick/盘口数据构建帧（Frame）。
2. 在帧上执行递归物理核（SRL / Epiplexity / Topology）。
3. 通过增量学习（SGD + StandardScaler）完成训练。
4. 在 OOS 数据上执行并行回测与审计 gate。

当前真实约束：

1. 全量原始数据约 2.6TB，本地为主，不能依赖全量上云。
2. Deep Think API 白名单未获批，最终审计仍需手动网页提交。
3. 需要把“升级质量”从人工经验转为可重复、可评估、可门禁的工程流程。

---

## 2. 仓库结构（基于可访问快照）

> 说明：当前可访问仓库快照以 `.pyc` 为主（非明文 `.py`），以下结构与接口来自字节码反射与配置提取。

目录（核心）：

```text
omega_core/                # 物理核、ETL、训练、审计核心
omega_v3_core/             # 历史/兼容核心
parallel_trainer/          # 并行训练/回测驱动
pipeline/                  # Framer + 配置加载 + 适配器接口
tools/                     # 运行监控、契约校验、数据清单、审计辅助
tests/                     # 核心 smoke/数学/兼容性测试
config.cpython-39.pyc      # 中央配置 dataclass
```

模块数量（`.pyc`）：

1. `omega_core`: 7
2. `omega_v3_core`: 6
3. `parallel_trainer`: 7
4. `pipeline`: 5
5. `tools`: 29
6. `tests`: 4

---

## 3. 核心代码映射（供 Vertex 建模）

### 3.1 中央配置：`config`

关键点：

1. 使用 dataclass 统一管理核参数、训练/回测、数据分割、审计阈值。
2. 同时包含 legacy 训练配置与 L2 v5/v5.1 流水线配置。
3. 默认分割策略（从配置反射）：`train_years=[2023,2024]`, `test_years=[2025]`, `test_year_months=[202601]`。

配置片段（提取自 `audit/_l2_pipeline_config_defaults.json`）：

```json
{
  "io": {
    "input_root": "./data/level2",
    "output_root": "./data/level2_frames",
    "input_format": "csv",
    "csv_encoding": "gb18030"
  },
  "validation": {
    "topo_snr_min": 3.0,
    "orthogonality_max_abs": 0.1,
    "vector_alignment_min": 0.6,
    "forward_return_horizon_buckets": 3
  },
  "train": {
    "drop_neutral_labels": true,
    "decision_margin": 0.05,
    "topology_race_features": ["topo_micro", "topo_classic", "topo_trend"]
  }
}
```

### 3.2 数学与物理核：`omega_core`

#### `omega_core/omega_math_core`

核心函数（反射）：

1. `calc_epiplexity`
2. `calc_compression_gain`
3. `calc_srl_state`
4. `calc_srl_race`
5. `calc_topology_area`
6. `calc_holographic_topology`
7. `topo_snr_from_traces`

关键说明字符串（来自字节码常量）：

1. `Universal SRL (Delta=0.5)`
2. `Epiplexity as Compression Gain`
3. `Holographic Topology`

#### `omega_core/omega_etl`

核心函数（反射）：

1. `scan_l2_quotes`
2. `_apply_session_filter`
3. `_apply_quality_filter`
4. `_microprice_expr`
5. `_ofi_expr`
6. `build_l2_frames`

含义：对 L2 CSV/Parquet 进行会话过滤、质量过滤、微价格/OFI/深度等特征构造，输出帧级特征表。

#### `omega_core/kernel`

核心函数/类：

1. `_apply_recursive_physics`
2. `apply_recursive_physics`
3. `run_l2_kernel`
4. `OmegaKernel.run`

### 3.3 训练与回测

#### `omega_core/trainer` 与 `omega_core/trainer_v51`

`OmegaTrainerV3` 方法（反射）：

1. `__init__`
2. `_prepare_frames`
3. `train`
4. `save`

v5.1 额外函数：

1. `_safe_corr`
2. `_vector_alignment`
3. `_collect_traces`
4. `run_l2_audit`
5. `write_audit_report`

#### `parallel_trainer/run_parallel_v31`

`ParallelTrainerV31` 方法：

1. `load_latest_checkpoint`
2. `save_checkpoint`
3. `_iter_manifest_task_chunks`
4. `train`

CLI 标志（提取）：

```text
--workers
--batch-rows
--checkpoint-rows
--file-list
--max-files
--memory-threshold
--status-json
--stage-local / --no-stage-local
--stage-dir
--stage-chunk-files
--stage-copy-workers
--no-cleanup-stage
--no-resume
```

#### `parallel_trainer/run_parallel_backtest_v31`

`ParallelBacktester` 方法：

1. `_load_state`
2. `_save_state`
3. `_iter_file_list_chunks`
4. `run`

CLI 标志（提取）：

```text
--policy
--workers
--data-dir
--file-list
--state-file
--status-json
--memory-threshold
--stage-local / --no-stage-local
--ret-clip-abs
--fail-on-audit-failed / --allow-audit-failed
```

### 3.4 Framing 引擎

`pipeline/engine/framer`：

1. `Framer.run`
2. `_scan_archives`
3. `_resolve_7z_exe`
4. `_process_archive`

运行特征（字符串提取）：

1. 多进程处理 `.7z` 档案。
2. 支持 `SEVEN_ZIP_EXE` 与 Windows 默认 7-Zip 路径。
3. 有 smoke 限制模式。

### 3.5 质量门禁与运维工具（`tools/`）

关键工具：

1. `preflight_dataset_split_v40`: 分割前置校验（年份/月份、交集、空集、命名规则）。
2. `build_dataset_manifest_v40`: 严格生成 train/backtest manifest。
3. `check_frame_train_backtest_compat`: 抽样验证 frame 与 train/backtest 消费兼容。
4. `verify_v40_data_contract`: 汇总运行状态与清单，验证数据契约闭环。
5. `v40_runtime_status`: 跨机监控 frame/train/backtest 状态与日志尾。
6. `run_l2_audit_driver`: .7z 批处理+抽取+frame+报告。

---

## 4. Dependencies（依赖）

### 4.1 主要运行时依赖（从导入图 + 本地环境反射）

核心三方库：

1. `numpy` 1.26.4
2. `polars` 1.36.1
3. `scikit-learn` 1.6.1
4. `psutil` 7.2.1
5. `pandas` 2.3.3
6. `PyYAML` 6.0.3
7. `scipy` 1.13.1
8. `sympy` 1.14.0（非核心训练路径，但在环境中）

外部生态/平台耦合：

1. `xtquant`（QMT 接入相关）
2. `qmt`/`qmt.exceptions`（工具链中存在导入）

### 4.2 工程特征

1. 主要计算模式是 CPU 向量化 + 多进程，非 GPU 深度学习训练。
2. I/O 负载重：7z 解压、stage 拷贝、Parquet 读写占主导。
3. `SGDClassifier + partial_fit` 单线程聚合逻辑是训练瓶颈之一。

---

## 5. 数据契约与输入输出

### 5.1 输入数据

1. 根目录：`./data/level2`（可配置）。
2. 格式：`.7z` 压缩档/CSV。
3. 编码：`gb18030`。
4. 列映射：中文列名（如 `万得代码`、`交易所代码`、`成交价`、`成交量`、`申买价*`、`申卖价*`）。

### 5.2 中间产物

1. Frame Parquet（`./data/level2_frames*`）。
2. manifest（train/backtest 列表）。
3. status JSON（frame/train/backtest 各阶段）。
4. checkpoint (`checkpoint_rows_*.pkl`)。

### 5.3 关键状态字段（来自脚本字符串与监控工具）

Frame 常见字段：

1. `archives_completed_in_run`
2. `archives_remaining_in_run`
3. `parquet_files_written_in_run`

Train 常见字段：

1. `files_done_in_run`
2. `files_remaining`
3. `total_rows`
4. `latest_checkpoint`

Backtest 常见字段：

1. `files_processed_in_run`
2. `total_rows`
3. `total_trades`
4. `total_pnl`
5. `error_count`

---

## 6. 测试与质量控制基线

现有测试（`tests/`）：

1. `test_math_core`: 压缩增益、SRL 普适性、反作弊惩罚等数学单测。
2. `test_causal_projection`: 动态分桶/因果投影相关测试。
3. `test_framer_output`: 跑 framing smoke 并验证 parquet 列。
4. `test_smoke_log`: 检查 pipeline smoke 日志产出。

运维质量门禁（推荐固定纳入 CI gate）：

1. `preflight_dataset_split_v40`
2. `build_dataset_manifest_v40`
3. `check_frame_train_backtest_compat`
4. `verify_v40_data_contract`

---

## 7. 可提交给 Vertex AI 的材料清单（优先级）

目标：不上传 2.6TB 全量原始数据，仍让模型理解系统全貌并做方案设计。

### P0（必须提交）

1. 项目结构与模块映射：本文件 `audit/vertex_ai.md`。
2. 配置默认快照：
   - `audit/_l2_pipeline_config_defaults.json`
   - `audit/_legacy_config_defaults.json`
   - `audit/_hardware_profile_default.json`
3. 代码接口快照：
   - `audit/_class_method_map.json`
   - `audit/_pyc_introspection_summary.json`
4. 运行工具链清单：
   - `tools/*.pyc`（至少以上 6 个 gate/监控脚本）

### P1（强烈建议）

1. 最近一次 `frame/train/backtest` 的 status JSON（真实运行产物，含耗时/吞吐/错误）。
2. 最近一次 audit 报告（Markdown/JSON）。
3. 训练 checkpoint 元信息（不必上传完整模型权重，可先上传摘要）。
4. 10~30 个代表性 parquet schema/样本（每个 1k~5k 行）。

### P2（可选）

1. 历史版本变更记录与失败案例。
2. Deep Think 网页审计反馈摘要（去敏后）。
3. 本地硬件资源曲线（CPU/RAM/磁盘/IOPS）。

---

## 8. 建议提交的“代码片段”示例（可直接给 Vertex）

> 注：以下来自字节码反射，不是完整源代码；用于说明接口和职责边界。

### 8.1 训练并行入口

```python
class ParallelTrainerV31:
    def load_latest_checkpoint(self): ...
    def save_checkpoint(self): ...
    def _iter_manifest_task_chunks(self): ...
    def train(self): ...
```

### 8.2 回测并行入口

```python
class ParallelBacktester:
    def _load_state(self): ...
    def _save_state(self): ...
    def _iter_file_list_chunks(self): ...
    def run(self): ...
```

### 8.3 数学核 API

```python
def calc_epiplexity(...): ...
def calc_srl_state(...): ...
def calc_topology_area(...): ...
def topo_snr_from_traces(...): ...
```

### 8.4 质量门禁命令（示意）

```bash
python tools/preflight_dataset_split_v40.py --input-dir <frames_dir> --status-json <split_status.json>
python tools/build_dataset_manifest_v40.py --role train --input-dir <frames_dir> --out-file <train_files.txt>
python tools/check_frame_train_backtest_compat.py --input-dir <frames_dir> --status-json <frame_compat_status.json>
python tools/verify_v40_data_contract.py --runtime-root <audit/v40_runtime/windows>
```

---

## 9. 结果 Snapshot 模板（建议实际运行后替换为真实值）

### 9.1 train_status.json（模板）

```json
{
  "stage": "train",
  "status": "completed",
  "files_done_in_run": 456,
  "files_remaining": 0,
  "total_rows": 55800000,
  "latest_checkpoint": "checkpoint_rows_55800000.pkl"
}
```

### 9.2 backtest_status.json（模板）

```json
{
  "stage": "backtest",
  "status": "failed",
  "files_processed_in_run": 456,
  "total_rows": 30100000,
  "total_trades": 1650000,
  "error_count": 0,
  "reason": "final audit status is FAILED and fail_on_audit_failed=true"
}
```

### 9.3 frame_status.json（模板）

```json
{
  "stage": "frame",
  "status": "running",
  "workers": 22,
  "archives_completed_in_run": 318,
  "archives_remaining_in_run": 433,
  "parquet_files_written_in_run": 698
}
```

---

## 10. 给 Vertex AI 的任务指令（可直接粘贴）

```text
你是本项目的“导入与质量提升架构师”。
请基于提交材料完成以下输出：
1) 梳理 OMEGA_vNext 的真实瓶颈（按严重级别排序：正确性风险、工程风险、性能风险）。
2) 给出不依赖 Deep Think API 的质量提升方案：
   - 本地 + Vertex 的职责边界
   - 审计流水线自动化
   - 回归评测与门禁阈值
3) 给出数据不上云/部分上云策略：
   - 最小上传集
   - 冷热分层
   - 成本与收益
4) 给出 30/60/90 天执行计划与验收指标。
5) 给出可直接落地的脚本清单与目录结构建议。

约束：
- 全量原始数据 2.6TB 暂不全量上云。
- 最终 Deep Think 审计当前仍需网页手动提交。
- 方案必须保持当前 train/backtest 物理逻辑不被破坏。
```

---

## 11. 对 Vertex 的额外说明（务必附上）

1. 当前仓库快照以 `.pyc` 为主，建议在安全边界内补充核心 `.py` 明文源码以提升审查深度。
2. 可先只提供“接口 + 配置 + 状态 + 小样本 parquet”，不上传原始全量数据。
3. 所有结论需返回“可证据化依据”，并映射到具体脚本/配置键。

---

## 12. 本地附加文件（已生成）

1. `audit/_pyc_introspection_summary.json`
2. `audit/_l2_pipeline_config_defaults.json`
3. `audit/_legacy_config_defaults.json`
4. `audit/_hardware_profile_default.json`
5. `audit/_class_method_map.json`

这些文件建议和本 Markdown 一起提交给 Vertex AI，作为第一轮“项目理解输入包”。
