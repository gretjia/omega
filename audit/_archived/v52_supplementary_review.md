# OMEGA v5.2 补充审计意见书（Supplementary Review）

**Date:** 2026-02-15
**Reviewer:** Antigravity AI (独立交叉审计)
**Scope:** 针对 `v52_final_implementation_plan.md` 与 `v52_final_implementation_audit.md` 两份文档的补充意见

> [!NOTE]
> 本文件旨在补充两份原始文档中**未覆盖或覆盖不足**的维度，而非否定其核心架构方向。原始文档在"物理-智能解耦"与"杠铃架构"层面的判断极具洞察力；以下意见聚焦于从**代码工程、数据完整性、安全合规、数学一致性与实战运维**五个维度进行查缺补漏。

---

## 一、代码工程层面的补充意见

### 1.1 `kernel.py` 的 SRL Markov Loop 仍是 Python 级串行

实际 `omega_core/kernel.py`（非 `v52_code.md` 中的旧版本）已将 Epiplexity 和 Topology 提取到批量向量化调用（`calc_epiplexity_vectorized`、`calc_holographic_topology_vectorized`），循环体内仅保留 SRL 标量递推：

```python
# kernel.py L143-171 (实际代码)
for i in range(n_rows):
    resid, imp_y, eff_d, spoof = calc_srl_state(   # <-- 每行一次函数调用
        price_change=price_change[i], sigma=sigma_eff[i],
        net_ofi=net_ofi[i], depth=depth_eff[i],
        current_y=current_y, cfg=srl,
        cancel_vol=cancel_vol[i], trade_vol=trade_vol[i],
    )
    # ... adaptive_y EMA + anchor + clip ...
```

**问题**：`calc_srl_state()` 内部包含 `math.exp()`、`math.sqrt()`、多次 `max()`/`float()` 转换。当 `n_rows > 500,000`（全天 L2 快照的常见量级），Python 解释器开销（函数分派、栈帧创建）累积成为瓶颈——即便循环体本身是"轻量标量运算"。

**建议**：

- **短期**：将 `calc_srl_state()` 与循环体合并后，用 `numba.njit(cache=True)` 编译为一个纯标量函数。因为循环体内全部是 `float64` 标量运算，Numba 的类型推断可无痛完成，预计可获得 50-100x 加速。
- **中期**：将整个递推重写为 Rust 扩展（通过 `pyo3`/`maturin`，与 Polars 的 Rust 底层同源），彻底消灭 Python 解释器开销。
- **注意**：`v52_good_engineering_practice.md` 提到"不需要 Numba 或 C++"，该结论在 smoke test（10 天、~35k rows/day）上成立，但在全量 framing（数千天 x 数十万行/天）上不成立。

### 1.2 错误处理的静默吞噬（Silent Failure）

训练器 `OmegaTrainerV3.train()` 中（`trainer_v51.py` L198-199）：

```python
except Exception as exc:
    print(f"Error {f.name}: {exc}")    # <-- 静默跳过，无计数、无中断条件
```

**风险**：如果大量文件因数据质量问题（编码错误、schema 不匹配、Parquet 损坏）静默失败，训练将在"幸存者偏差"的数据子集上完成，且操作员无任何感知。

**建议**：

- 新增 `error_count` 计数器；当 `error_count / total_files > 5%` 时，**自动中断训练并输出诊断报告**。
- 将所有异常写入 `audit/runtime/v52/training_errors.jsonl`（含 traceback + 文件名 + 时间戳），而非仅打印到 stdout。
- 在 `run_meta.json` 中记录 `files_success`、`files_error`、`error_rate`。

### 1.3 `get_latest_model()` 的裸 `except` 反模式

`trainer_v51.py` L376-379：

```python
try:
    with open(paths[-1], "rb") as f: return pickle.load(f)
except:                # <-- 捕获一切异常，包括 KeyboardInterrupt
    return None
```

**风险**：磁盘损坏导致 pickle 反序列化失败时，调用方会静默收到 `None`，后续 `Model_Alignment` 计算直接回退到 `Phys_Alignment`，且无任何告警。

**建议**：将 `except:` 改为 `except (OSError, pickle.UnpicklingError, EOFError) as e:`，并记录日志。

### 1.4 缺少 `__main__` 入口与 CLI 规范

`trainer_v51.py` 和 `physics_auditor.py` 没有 `if __name__ == "__main__"` 入口。所有操作需要手动在 Python REPL 或外部脚本中驱动。

**建议**：为核心模块添加标准 CLI 入口（`argparse` 或 `click`），使其可直接通过 `python -m omega_core.trainer_v51 --config configs/hardware/linux.yaml` 调用。这对三机协作至关重要。

### 1.5 `v52_code.md` 与实际代码不一致（文档债务）

`audit/v52_code.md` 中记录的 `kernel.py` 仍然是旧版代码（Epiplexity/Topology 在 for-loop 内逐行计算，调用 `calc_epiplexity` 标量版本），而实际 `omega_core/kernel.py` 已升级为向量化版本（使用 `calc_epiplexity_vectorized`、`calc_holographic_topology_vectorized`，且从 `omega_math_vectorized` 导入而非 `omega_math_core`）。

**风险**：后续 AI Agent 或审计人员阅读 `v52_code.md` 时，会对系统当前状态产生错误认知，可能导致重复工作或错误决策。

**建议**：

- 使用实际源码文件（`omega_core/kernel.py`、`trainer_v51.py`、`physics_auditor.py`）作为唯一真相来源。
- 将 `v52_code.md` 标记为 `[DEPRECATED]` 或重新生成以反映当前代码。

---

## 二、数据完整性层面的补充意见

### 2.1 Parallel Framing 的幂等性（Idempotency）未保证

`v52_final_implementation_plan.md` S5.2 要求两台机器写到不同子目录以避免覆盖，但**未定义幂等性协议**：

- 如果 Windows1 在处理 `20230115.7z` 时崩溃并重启，它会重新处理还是跳过？
- 重新处理产生的 Parquet 与第一次的是否 bit-identical？

**建议**：

- 为每个 archive 的 framing 产物添加 **完成标志文件**（`YYYYMMDD.done`），重启后检查该标志决定是否跳过。
- 产物文件名中包含 `git_commit_short`（如 `20230115_a7f3b2c.parquet`），使得不同代码版本产出的帧永远不会混淆。

### 2.2 Parquet Schema 漂移检测缺失

两台机器若运行的代码版本存在微小差异（例如一方有 `topo_trend` 列而另一方没有），合并后的 frames 在训练时将触发 `missing features` 静默跳过。

**建议**：

- 在 `run_meta.json` 中记录 `schema_fingerprint`（所有列名 + dtype 的 SHA256）。
- 合并前执行 strict schema assertion；不一致时拒绝合并并报错。

### 2.3 原始数据校验覆盖不足

Plan 提到"抽样 `7z t` 校验"，但未定义：

- 校验覆盖率要求（是 100% 还是抽样 10%？）
- 校验失败的处理流程（丢弃？隔离？重传？）

**建议**：

- **100% 校验**：对所有 `.7z` 执行 `7z t`，将结果写入 `archive_integrity_manifest.jsonl`。
- 校验失败的 archive 移入 `quarantine/` 目录，pipeline 自动跳过并记录。
- 时间成本估算：2.6TB `.7z` 的 integrity test 在 USB4 顺序读约需 45-90 分钟，完全可接受。

---

## 三、安全与合规层面的补充意见

### 3.1 `pickle` 的安全隐患

整个系统高度依赖 `pickle.dump/load` 存储模型。`pickle` 在反序列化时可执行任意代码。

**风险场景**：如果攻击者篡改云端 GCS 上的 `.pkl` 文件，QMT 加载时可能执行恶意代码。

**建议**：

- **短期**：对 `.pkl` 文件计算 SHA256 签名并存储在 `artifacts/checksums.json` 中；加载前验证。
- **中期**（`v52_final_implementation_audit.md` 中的 `weights.json` 方案已在正确方向）：QMT 端**只接受 JSON 格式的权重**，彻底杜绝反序列化攻击面。
- 训练端可保留 pickle + 签名机制。

### 3.2 `.env` 文件管理

项目根目录存在 `.env` 文件（425 bytes）。

**已确认**：`.env` 已被 `.gitignore` 正确排除（`.gitignore` 第 7 行：`.env`）。

**补充建议**：

- 即使不进 Git，仍需确保 `.env` 在三台机器间的同步方式安全（不要通过明文 IM 或邮件传输）。建议使用 `scp` 或加密渠道。
- GCP 认证优先使用 **Service Account JSON + 环境变量指向路径**（`GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json`），而非直接在 `.env` 中存储 API Key 明文。

### 3.3 三机通信的认证缺失

Plan 描述了三机协作，但未提及机器间的认证与授权：

- Git push/pull 使用什么认证？（SSH Key？Token？）
- GCS 上传使用什么 Service Account？权限范围？

**建议**：在 `audit/runtime/v52/` 中新增 `security_posture.md`，记录每台机器的认证方式、密钥轮换策略和最小权限原则的落实情况。

---

## 四、数学一致性层面的补充意见

### 4.1 `Model_Alignment` 的统计显著性未量化

当前 `Model_Alignment` 的阈值为 `> 0.6`，但缺少：

- **置信区间**：0.6 在多少样本量下才有统计显著性？如果只有 50 个高 Epiplexity 样本，0.6 可能完全是噪声。
- **基线比较**：还应报告 `Random_Alignment`（随机打标签的对齐率）作为第三轨对照。

**建议**：

- 在 `evaluate_frames()` 中增加 **Bootstrap 置信区间** 或 **Binomial test p-value**。
- DoD 应为：`Model_Alignment > 0.6 AND p_value < 0.05`。
- 当 `min_samples < 200` 时，自动标记为 `INSUFFICIENT_SAMPLES`，不做 pass/fail 判定。

### 4.2 `Topo_SNR` 的 Shuffle Test 假设可能被违反

`topo_snr_from_traces()`（`omega_math_core.py` L237-263）使用逐元素 shuffle test 计算拓扑 SNR。其核心逻辑为 `rng.permutation(arr.size)` 对每条 trace 的元素做随机排列，隐含假设：

- trace 内元素的时序结构是被检验的信号，shuffle 破坏时序后作为 null baseline。

但实际 L2 数据中，相邻 volume bar 的 traces 高度自相关（主力动量延续跨 bar）。逐元素 shuffle 在强自相关序列上会**高估** SNR（因为 shuffle 打破了自相关结构，baseline 被低估）。

**建议**：

- 增加 **Block Shuffle** 测试（以 20 bars 为块进行随机排列），作为更保守的 SNR 基线。
- 在审计报告中同时报告 `Topo_SNR_iid` 和 `Topo_SNR_block`。

### 4.3 `adaptive_y` 的长期漂移缺乏监控

IIR 滤波器 `y = (1-alpha)*y + alpha*x` 在 `anchor_weight = 0.01`（`config.py` L599）的弱锚定下，长期运行可能跟随市场 regime shift 漂移到极端值。虽然有 `clip(y, clip_lo, clip_hi)` 保护，但 clip 范围 `[0.4, 1.5]`（`config.py` L600-601）是固定的，不随市场自适应。

**建议**：

- 在审计报告中增加 `adaptive_y` 的**时间序列轨迹图**与**分布直方图**，检测是否出现 clip 饱和（贴边运行）。
- 如果 `clip_saturation_rate > 20%`，自动告警并建议扩大 clip 范围或增大 `anchor_weight`。

---

## 五、运维与实战部署层面的补充意见

### 5.1 缺少"紧急回滚"协议

Plan 定义了完整的前向流程（framing -> training -> tuning -> deploy），但未定义：

- 如果 v5.2 模型在实盘亏损超过阈值，如何快速回滚到上一个已验证的模型？
- `weights.json` 是否做版本化存储？（如 `weights_v52_run003.json`）

**建议**：

- 在 GCS 上启用 **Object Versioning**，确保任何 `weights.json` 的覆盖都保留历史版本。
- 在 QMT 端定义 `EMERGENCY_FLAT_ALL` 逻辑：当日亏损 > X% 时，自动平仓并切换为空仓模式，等待人工介入。

### 5.2 三机的时钟同步未提及

Parallel framing 的 manifest 和 log 中会记录时间戳。如果三台机器的系统时钟不同步：

- 事后审计时可能无法准确重建"谁在什么时间处理了什么"。
- 特别是 Windows 机器的时钟漂移问题（NTP 默认同步间隔是 7 天）。

**建议**：三台机器均配置 NTP 自动同步（建议间隔 <= 1 小时），或在 `run_meta.json` 中使用 UTC 时间戳。

### 5.3 磁盘空间监控缺失

`v52_implementation_status.md` 和过往 handover 记录中多次提及 `Errno 28: No space left on device`。

**建议**：

- framing 脚本启动时检查 `STAGE_ROOT` 和 `FRAMES_ROOT` 所在分区的可用空间；若 < 50GB，拒绝启动并报告。
- 运行中每处理 100 个 archive 检查一次磁盘空间；低于阈值时自动暂停并发出告警。
- 这应作为 `v5.2 DoD` 的硬性工程指标：**pipeline 不能因磁盘空间耗尽而静默崩溃**。

### 5.4 Optuna Sweep 的资源预算未量化

Plan S7.2 提到"先本地跑 30-50 次 trial"，但未估算：

- 单次 trial 的耗时（基于 smoke test 外推）
- 单次 trial 的 peak 内存
- 50 trial 的总体 wall clock

**建议**：

- 在第一轮训练闭环后，从 smoke test 数据估算 `time_per_trial` 和 `mem_per_trial`。
- 写入 `audit/runtime/v52/resource_budget.md`，据此决定是否需要云端并行。
- 对于本地 Optuna：使用 `optuna.create_study(storage="sqlite:///optuna_v52.db")`，确保 trial 结果持久化，中断后可恢复。

### 5.5 监控与可观测性（Observability）几乎为零

当前系统缺少以下实时可观测能力：

- **framing 进度**：已处理 / 总量的百分比
- **训练进度**：loss curve、alignment 随 epoch 变化
- **资源利用**：CPU、内存、磁盘 I/O 的时间序列

**建议**：

- **最简方案**：framing/training 主循环中每 N 个 batch 向 `audit/runtime/v52/progress.jsonl` 追加一行 JSON（timestamp, step, metric, host）。
- Mac 控制塔可通过 `tail -f` 或简单的 Python 脚本实时展示三机进度。
- 这比引入 MLflow/W&B 更符合"零运维债"原则。

---

## 六、两份原始文档的风格/结构性补充

### 6.1 `v52_final_implementation_audit.md`：定位模糊

这份文档标题为"audit"，内容实际上是一份**架构愿景与 Vibe Prompt 手册**，而非传统意义上的审计报告。它包括：

- 对用户背景的渲染（美股期权收益等）
- 3 个完整的 Prompt 模板
- 哲学箴言

**建议**：将这份文件重命名为 `v52_architect_blueprint.md` 或 `v52_solo_quant_playbook.md`，使其定位更清晰。保留 `_audit.md` 后缀给严格的技术审计文档（如本文件的内容形态）。

### 6.2 `v52_final_implementation_plan.md`：缺少"失败模式分析"

Plan 描述了理想路径，但缺少 **Failure Mode Analysis**：

| 失败模式 | 概率 | 影响 | 缓解措施 |
|:---|:---|:---|:---|
| USB4 盘 I/O 性能不足导致 framing 极慢 | 中 | 高 | 将 `STAGE_ROOT` 移至 NVMe（Plan 已提及） |
| GCS 上传带宽瓶颈（上行 < 10Mbps） | 高 | 中 | 先本地汇聚，批量上传；或租用云端 VM 做中转 |
| 两台机器的 `.7z` 副本不一致 | 低 | 致命 | 全量 SHA256 manifest 对比 |
| SGD 模型在增量数据下灾难性遗忘 | 中 | 高 | 定期在全量数据上 re-fit 并与增量模型对比 |
| QMT 封闭 Python 环境中 `numpy` 版本过旧 | 高 | 中 | 优先测试 QMT 环境的 numpy 版本兼容性 |

---

## 七、总结：Top 5 优先执行建议

按紧急度排序：

1. **[P0] 数据完整性**：在 framing 开跑前完成**100% `.7z` integrity test** + schema fingerprint 协议
2. **[P0] 错误处理**：将训练器/framing 的 `except` 改为有计数、有日志、有中断条件的版本
3. **[P1] 幂等性**：实现 `.done` 标志文件 + `git_commit` 嵌入产物文件名
4. **[P1] 可观测性**：在主循环中添加 `progress.jsonl` 追加式日志
5. **[P2] 数学护栏**：为 `Model_Alignment` 添加 Bootstrap CI / p-value 统计显著性检验

> [!IMPORTANT]
> 以上 P0 项应在**第一轮 framing 启动前**完成。它们的实现成本极低（各约 30 分钟代码量），但能从根本上避免"跑了 48 小时才发现数据/训练结果不可用"的灾难性时间浪费。

---

## 审计追溯 (Audit Trail)

| 项 | 详情 |
|:---|:---|
| 审计日期 | 2026-02-15 |
| 审计范围 | `v52_final_implementation_plan.md`、`v52_final_implementation_audit.md` |
| 交叉验证 | 所有代码引用已与实际源文件逐行比对 |
| 实际代码文件 | `omega_core/kernel.py` (258L)、`omega_core/trainer_v51.py` (417L)、`omega_core/omega_math_core.py` (263L)、`config.py` (839L) |
| 关联文档 | `v52_code.md`（与实际代码不一致，见 S1.5）、`v52_implementation_status.md`、`v52_good_engineering_practice.md`、`.gitignore` |
| 自审修正 | S1.1 代码引用从 `v52_code.md` 旧版修正为实际 `kernel.py`；S3.2 确认 `.env` 已在 `.gitignore` 中；新增 S1.5 文档债务告警 |
