# OMEGA v5.1 最终深度审计（Full Autopilot / No-Resume）
**审计日期**: 2026-02-14  
**审计范围**: windows1 上 v51 全流程（frame 补齐 -> 全量训练 -> 全量回测）  
**审计目标**: 按 `audit/v51.md` 的升级理念，对 v51 代码升级后的真实运行结果做最终对照，为下一轮修补提供可执行入口。

## 1. 最终结论（先结论）

**C1. 本轮 v51 训练与回测均已完成，且为 no-resume 路径。**  
- 训练状态 `completed`，`files_selected=456`，`total_rows=15,880,921`。  
- 回测状态 `completed`，`total_tasks=263`，`files_processed_in_run=263`，`files_remaining=0`。

**C2. 回测最终 DoD 仍失败，唯一阻断项仍是 Vector Alignment。**  
- `Topo SNR=9.4581`（通过，阈值 > 3.0）  
- `Orthogonality=-0.0404`（通过，阈值 abs < 0.1）  
- `Vector Alignment=0.5077`（未通过，阈值 > 0.6）  
- `FINAL AUDIT STATUS=FAILED`

**C3. 本轮已使用 v51 训练产物进行回测，不再是旧 v5 policy。**  
回测 policy 为 `C:\Omega_vNext\artifacts\checkpoint_rows_15880921.pkl`，来源于本轮 v51 训练最终 checkpoint。

**C4. 回测存在 2 个文件级内存错误，但未中断总流程。**  
`20251105.parquet`、`20251022.parquet` 在 `_prepare_frames -> apply_recursive_physics` 路径发生 `MemoryError`；流程在 `allow-audit-failed` 模式下继续完成。

**C5. 本轮清理已完成并显著恢复磁盘空间，未破坏回测完成态。**  
已删除本轮无意义大文件（超大打包 zip、旧 stage/cache 目录），C 盘 `Free` 从约 `73,995,882,496` 提升至 `1,712,677,445,632` 字节；清理后回测状态仍为 `completed`。

**C6. `Vector Alignment` 与上午结果接近是“指标口径”导致，不等同于训练无效。**  
当前 backtest 的 `Vector Alignment` 计算使用物理层 `direction` 与 `future return` 的一致率，而不是模型 `predict_proba` 的方向一致率，因此对训练参数变化天然不敏感。

## 2. 运行事实与关键指标

### 2.1 训练（full_autopilot/train）
- workers: `6`
- manifest files: `456`（`2023-01` 到 `2024-12`）
- total_rows: `15,880,921`
- elapsed: `3,276.49s`（约 `54.6 min`）
- latest checkpoint: `artifacts/checkpoint_rows_15880921.pkl`
- status: `completed`

### 2.2 回测（full_autopilot/backtest）
- workers: `8`
- manifest files: `263`（`2025-01-02` 到 `2026-01-30`）
- total_tasks: `263`
- files_processed_in_run: `263`
- processed_files_total: `261`
- error_count: `2`
- total_rows: `11,557,977`
- total_trades: `2,344,617`
- total_pnl: `212.748283629935`
- elapsed: `14,254.98s`（约 `3.96 h`）
- final_audit_status: `FAILED`

### 2.3 DoD 指标
| 指标 | 本轮结果 | 阈值 | 结论 |
|---|---:|---:|---|
| Topo SNR | 9.4581 | > 3.0 | 通过 |
| Orthogonality | -0.0404 | abs < 0.1 | 通过 |
| Vector Alignment | 0.5077 | > 0.6 | 未通过 |

### 2.4 上午回测 vs 刚结束回测（口径核验）
| 项目 | 上午（reframed 2025 子集） | 刚结束（full_autopilot） | 说明 |
|---|---:|---:|---|
| 回测时间 | `2026-02-14 03:24:28` | `2026-02-14 16:18:06` | 两次是不同任务 |
| policy | `checkpoint_rows_55039250.pkl` | `checkpoint_rows_15880921.pkl` | 后者来自本轮新训练 |
| total_tasks | 222 | 263 | 样本覆盖不同 |
| processed_files_total | 222 | 261 | full_autopilot 有 2 个文件 MemoryError |
| total_rows | 9,776,693 | 11,557,977 | 本轮样本更大 |
| total_trades | 450,320 | 2,344,617 | 交易数显著增加 |
| total_pnl | 75.8662 | 212.7483 | 收益显著提高 |
| avg_align | 0.5072 | 0.5077 | 接近，差异仅 +0.0005 |

结论：
- `v51_deep_audit` 采用的是刚结束的 full_autopilot 回测结果，而非上午子集回测。
- `avg_align` 接近不是“没用新模型”，而是该指标口径本身主要受物理方向定义影响。

## 3. 关键异常与影响评估

### 3.1 文件级内存错误（2个）
- `20251105.parquet` -> `MemoryError`
- `20251022.parquet` -> `MemoryError`

影响评估：
- 总任务未中断，流程完成。
- `processed_files_total=261` vs `total_tasks=263`，与 `error_count=2` 一致。
- 指标存在轻微样本缺口风险，下一轮应先补跑这 2 个文件并验证指标稳定性。

### 3.2 状态文件写入告警（磁盘不足）
- 回测日志出现一次 `status_json write failed: [Errno 28] No space left on device`。
- 后续通过清理空间已恢复，最终状态文件与回测结果已落盘。

### 3.3 流程控制脚本问题（已绕过）
- 自动生成审计文档脚本 `generate_v51_deep_audit.py` 存在编码/字符串错误导致 finalizer 报错。
- 本文档为手工基于最终产物重建，作为 authoritative final audit。

### 3.4 Alignment 指标口径风险（解释本次疑问）
- 在 `run_parallel_backtest_v31.py` 中，指标来自 `evaluate_frames(df, policy_cfg)`，位置：`parallel_trainer/run_parallel_backtest_v31.py:176`。
- `evaluate_frames` 内部的 `_vector_alignment` 使用 `direction` 与 `fwd_return`，位置：`omega_core/trainer_v51.py:253`。
- 其中 `direction` 取自物理层（`kernel`），不是模型预测概率，因此训练对该指标影响弱于对 `PnL/Trades` 的影响。
- 本轮 `PnL/Trades/Rows` 已明显变化，说明训练影响体现在交易决策链；但 DoD 当前定义下的 `Vector Alignment` 仍未过线。

## 4. v51.md 递归对齐审计（Recursive Alignment）

| 升级项 | v51 要求 | 证据 | 结论 |
|---|---|---|---|
| P0 对称门控 + 阻尼方向 | 由单边门控改为双边触发；方向采用 damper 语义 | `omega_core/kernel.py:205`, `omega_core/kernel.py:211` | 已落地 |
| P1 交互特征层 | 注入 `epi_x_*` 非线性交互，提升线性 SGD 感知 | `omega_core/trainer_v51.py:54`, `omega_core/trainer_v51.py:91` | 已落地 |
| C6 末端状态固化 | 训练末段必须强制 final checkpoint | `omega_core/trainer_v51.py:215`, `omega_core/trainer_v51.py:218` | 已落地 |
| P4 ETL 早盘防爆 | 抬高早盘外推下限，防 opening projection 爆炸 | `omega_core/omega_etl.py:237` | 已落地 |
| A1 Damper 对齐审计 | 审计方向对齐应使用 `-sign(srl_resid)` | `omega_core/physics_auditor.py:200` | 已落地 |
| DoD 验收 | `vector_alignment_min=0.6` | `config.py:686` + 本轮回测结果 0.5077 | 未达标 |

## 5. 清理台账（本轮无意义产物）

### 5.1 已删除项
- `C:\Omega_vNext\artifacts\upload_packages\Omega_vNext_clean_20260214_120409.zip`（约 563,125,864,525 bytes）
- `C:\Omega_vNext\artifacts\upload_packages\Omega_vNext_clean_20260214_120558.zip`（约 553,513,540,702 bytes）
- `C:\Omega_level2_stage`（约 440.77 GB）
- `C:\Temp\omega_train_cache`（约 36.03 GB）

### 5.2 清理后状态
- 以上路径均 `Exists=False`。
- C 盘可用空间恢复至约 `1.71 TB`（`1,712,677,445,632` bytes）。
- 当前无 `python.exe` 在跑，回测最终状态保持 `completed`。

## 6. 面向下一轮修补的最小闭环计划

1. **先补跑 2 个 MemoryError 文件并复核 DoD**  
   对 `20251105.parquet` 与 `20251022.parquet` 做单文件回测或小批回测，确认 `Vector Alignment` 对缺失样本的敏感度。

2. **优先解决 `_prepare_frames` 内存峰值**  
   当前瓶颈来自 `frames.to_dicts()` / 行级累积路径。建议改为分块处理或纯列式表达，避免大文件峰值内存炸裂。

3. **继续围绕 Alignment 做定向修补（保持 SNR/Orth 不退化）**  
   当前仅差 `0.0923`（`0.6000 - 0.5077`）。建议以方向一致性为主目标做小步扫描，禁止通过放宽阈值“过审”。

4. **新增“模型驱动 Alignment”并与物理 Alignment 双轨报告**  
   保留现有物理口径（`direction` vs `fwd_return`）用于物理一致性，同时增加一列模型口径（例如 `sign(predict_proba-0.5)` vs `fwd_return`），避免把训练收益误判为“无变化”。

5. **保留磁盘护栏，禁止再次生成超大 upload zip**  
   将 `upload_packages` 产物改为按需生成或引入 TTL 清理，避免再次触发状态写盘失败。

## 7. 证据索引（最终）

- v51 审计要求：`audit/v51.md`
- 训练状态：`audit/v51_runtime/windows/full_autopilot/train/train_status.json`
- 训练日志：`audit/v51_runtime/windows/full_autopilot/train/train.stdout.log`
- 回测状态：`audit/v51_runtime/windows/full_autopilot/backtest/backtest_status.json`
- 回测日志：`audit/v51_runtime/windows/full_autopilot/backtest/backtest.stdout.log`
- 回测状态快照：`audit/v51_runtime/windows/full_autopilot/backtest/backtest_state.json`
- 训练 manifest：`audit/v51_runtime/windows/full_autopilot/manifests/train_files.txt`
- 回测 manifest：`audit/v51_runtime/windows/full_autopilot/manifests/backtest_files.txt`
- Autopilot 主日志：`audit/v51_runtime/windows/full_autopilot/autopilot.log`
- Watchdog 日志：`audit/v51_runtime/windows/full_autopilot/watchdog.log`

## 8. 与 v51.md 互证的法医级原始证据（Forensic Pack）

### 8.1 升级要求 -> 代码落地（逐条互证）
| `audit/v51.md` 原始要求 | 当前代码原始证据 | 结论 |
|---|---|---|
| `audit/v51.md:21` P0：对称门控 + `-sign(srl_resid)` 方向 | `omega_core/kernel.py:205`（`srl_resid.abs()` 双边触发）；`omega_core/kernel.py:211`（`direction=-sign(srl_resid)`） | 已落地 |
| `audit/v51.md:22` P1：非线性交互项 | `omega_core/trainer_v51.py:54`~`omega_core/trainer_v51.py:56`（feature schema）；`omega_core/trainer_v51.py:91`~`omega_core/trainer_v51.py:93`（`epi_x_*` 实际注入） | 已落地 |
| `audit/v51.md:23` C6：末端 checkpoint 强制落盘 | `omega_core/trainer_v51.py:215`~`omega_core/trainer_v51.py:218`（unconditional final checkpoint） | 已落地 |
| `audit/v51.md:24` P4：早盘外推防爆 | `omega_core/omega_etl.py:237`（`time_fraction.lower_bound=0.05`） | 已落地 |
| `audit/v51.md:24` A1：Damper 对齐审计 | `omega_core/physics_auditor.py:186`（A1 注释）；`omega_core/physics_auditor.py:200`~`omega_core/physics_auditor.py:204`（`dir_sign=-sign(srl_resid)` 与 `future_ret` 对齐率） | 已落地 |

### 8.2 训练 -> 回测证据链（同一轮产物，不是旧 policy）
| 证据点 | 原始字段/日志 | 结果 |
|---|---|---|
| 训练完成态 | `audit/v51_runtime/windows/full_autopilot/train/train_status.json:22`=`completed`；`:13`=`total_rows 15880921`；`:25`=`files_selected 456` | 训练完成且样本规模固定 |
| C6 最终 checkpoint 落盘 | `audit/v51_runtime/windows/full_autopilot/train/train.stdout.log:109`（`checkpoint_rows_15880921.pkl`）；`:110`（`Training Complete`） | 末端行数已固化 |
| 回测 policy 指向本轮训练产物 | `audit/v51_runtime/windows/full_autopilot/backtest/backtest_status.json:7`=`checkpoint_rows_15880921.pkl`；与训练 `latest_checkpoint`（`train_status.json:15`）一致 | 回测确为本轮新模型 |
| 回测完成态 | `audit/v51_runtime/windows/full_autopilot/backtest/backtest_status.json:4`=`completed`；`:16`=`total_tasks 263`；`:36`=`FAILED`；`:39`=`avg_align 0.507709` | 流程完成，DoD 仅卡 Alignment |
| 与上午子集回测区分 | `audit/v51_runtime/windows/backtest_patch_2025_reframed/backtest_status.json:3`=`2026-02-14 03:24:28`；`:7`=`checkpoint_rows_55039250.pkl`；`:39`=`0.507161` | 上午与本轮为不同任务，不可混淆 |

### 8.3 数据覆盖口径（可复算）
- 训练 manifest：`audit/v51_runtime/windows/full_autopilot/manifests/train_files.txt` 共 `456` 文件（`20230103` 到 `20241231`），与 `train_status.json:25` 一致。
- 回测 manifest：`audit/v51_runtime/windows/full_autopilot/manifests/backtest_files.txt` 共 `263` 文件（`20250102` 到 `20260130`），与 `backtest_status.json:16` 一致。
- 由回测 manifest 统计（可复算）：
  - `2025-12` 共 `23` 个 archive；
  - `2026-01` 共 `20` 个 archive；
  - 全 `2025` 共 `243` 个 archive，`2025 + 2026-01` 合计 `263`。
- 回测有效审计样本数：`audit/v51_runtime/windows/full_autopilot/backtest/backtest_state.json:275`=`n_valid 261`，与 `backtest_status.json:18`=`processed_files_total 261` 对齐（另有 2 文件错误）。

### 8.4 异常原始日志（阻断项与风险项）
- `audit/v51_runtime/windows/full_autopilot/backtest/backtest.stdout.log:33`：`status_json write failed: [Errno 28] No space left on device`。
- `audit/v51_runtime/windows/full_autopilot/backtest/backtest.stdout.log:36`~`:51`：`20251105.parquet` 在 `frames.to_dicts()` 路径 `MemoryError`。
- `audit/v51_runtime/windows/full_autopilot/backtest/backtest.stdout.log:53`~`:63`：`20251022.parquet` 在结果累积路径 `MemoryError`。
- `audit/v51_runtime/windows/full_autopilot/backtest/backtest_status.json:19`=`error_count 2`，与上述两条日志一致。

### 8.5 审计取证哈希（SHA256）
```
41dd8330d27f37e685ec4a511d6b20014f2c7b5697dceecac8d69917f1eb97b8  audit/v51_runtime/windows/full_autopilot/train/train_status.json
a42aeec1efe638d203e840cf8f6f89507eba6cf62a41b585d44b15099c50de54  audit/v51_runtime/windows/full_autopilot/backtest/backtest_status.json
c1d3759e40907dfb4721088af4d63a9a11698cd8aad4c9c81c489f094940fa22  audit/v51_runtime/windows/full_autopilot/backtest/backtest_state.json
d833465c739286fcb47b8e0e885b89886c64ff6c2e82238845ea95c98569b268  audit/v51_runtime/windows/full_autopilot/backtest/backtest.stdout.log
47e0971db3d7b23b0d69e1cde7be078408e69c77aa434f7c2c80cd6eba0a4809  audit/v51_runtime/windows/full_autopilot/autopilot.log
d3c446ba3ca61de506a5d1d51445ba7054f93d639197f9931b986e2b68fe7dfa  audit/v51_runtime/windows/full_autopilot/manifests/train_files.txt
a7c8a1715707cd37fb1231f2413862e1ed89aaabfccdcb3ec8f6c8af65b0ad69  audit/v51_runtime/windows/full_autopilot/manifests/backtest_files.txt
22cdafe7460099f9d0d718e30b8590ed3c0a4c70ef29b1ccf2296d53fc26a76c  audit/v51_runtime/windows/backtest_patch_2025_reframed/backtest_status.json
```

### 8.6 给审计师下一轮规划的证据化入口
1. **先做缺失样本补跑**：依据 `8.4` 两个 `MemoryError` 文件定点补跑，验证 `avg_align` 对补样是否敏感。  
2. **并行推进指标口径修补**：当前 `Vector Alignment` 来自 `direction` vs `fwd_return`（`parallel_trainer/run_parallel_backtest_v31.py:176` + `omega_core/trainer_v51.py:253`），建议新增“模型方向一致率”并与现口径双轨报表。  
3. **保持验收阈值不动**：`config.py:686` 仍为 `vector_alignment_min=0.6`，禁止通过阈值下调规避问题。  

---
**Final Verdict**: v5.1 升级项（P0/P1/C6/P4/A1）均已工程落地，且本轮已完成“v51 训练产物驱动的全量回测”；系统当前唯一验收阻断仍是 `Vector Alignment < 0.6`，下一轮必须聚焦“内存稳定性 + 方向语义收敛”。
