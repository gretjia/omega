# v34 Epiplexity 专项分支执行手册

Date: 2026-02-07  
Branch: `codex/epiplexity-v34-race`

## 1. 分支目标

在不改动主干训练哲学的前提下，先做非全量并行实验，比较三种 Epiplexity 路径在同一训练赛场上的有效性：

1. `epiplexity_zlib`（原有 zlib 抛物线映射）
2. `epiplexity_lz76`（LZ76 线性复杂度）
3. `epiplexity_perm`（Permutation Entropy 线性复杂度）

先得出方法优先级，再决定是否全量训练。

## 2. 已完成代码改造

1. `config.py`
- `L2EpiplexityConfig` 新增 `perm_order`
- `L2TrainConfig` 新增：
  - `epiplexity_feature_mode` (`baseline`/`race`)
  - `epiplexity_race_features`

2. `omega_v3_core/omega_math_core.py`
- 保留原 `calc_epiplexity`（zlib 抛物线）
- 新增：
  - `calc_epiplexity_lz76`
  - `calc_epiplexity_permutation`

3. `omega_v3_core/kernel.py`
- 单次 Reduce 同时输出：
  - `epiplexity`（兼容字段）
  - `epiplexity_zlib`
  - `epiplexity_lz76`
  - `epiplexity_perm`
- 信号门控仍使用既有 `epiplexity`，不改主干判定逻辑。

4. `omega_v3_core/trainer.py`
- 特征列改为配置驱动：
  - `baseline`: 使用单特征 `epiplexity`
  - `race`: 使用三特征 `epiplexity_zlib/lz76/perm`

5. `parallel_trainer/run_parallel_v31.py`
- 特征列改为动态读取 `OmegaTrainerV3(cfg).feature_cols`，去除硬编码。

6. 新增 `parallel_trainer/run_parallel_epi_race.py`
- 专用于 v34 赛马实验，支持：
  - 并行训练
  - 断点续训
  - 内存水位保护
  - 共享盘文件分块本地暂存（可自动清理）
  - 指定数据目录（`--data-dir`，可多次传入）
  - 非全量训练参数（`max-files`, `sample-frac`）
  - 自动输出结果 `audit/v34_epi_race_report.json`

## 3. Mac Studio 32GB 推荐参数

> 场景：Windows 机器仍在跑 backtest，共享盘 IO 紧张；Mac 本地盘有限。

推荐策略：

1. 开启本地分块暂存：`--stage-local`
2. 小块搬运+处理后立刻清理：`--stage-chunk-files 16~24`
3. 控制并行度：`--workers 6~8`
4. 内存闸门：`--memory-threshold 80~82`
5. 先非全量：`--max-files` + `--sample-frac`

## 4. 首轮非全量实验命令

```bash
/Volumes/desktop-41jidl2/Omega_vNext/.venv/bin/python \
  /Volumes/desktop-41jidl2/Omega_vNext/parallel_trainer/run_parallel_epi_race.py \
  --workers 8 \
  --batch-rows 120000 \
  --checkpoint-rows 400000 \
  --sample-frac 0.15 \
  --max-files 600 \
  --out-dir /Volumes/desktop-41jidl2/Omega_vNext/artifacts/epi_race \
  --checkpoint-prefix epi_race_ckpt_rows_ \
  --stage-local \
  --stage-dir /tmp/omega_epi_stage \
  --stage-chunk-files 24 \
  --memory-threshold 82 \
  --report-path /Volumes/desktop-41jidl2/Omega_vNext/audit/v34_epi_race_report.json \
  --data-dir /Volumes/desktop-41jidl2/Omega_vNext/data/level2_frames_win2023 \
  --data-dir /Volumes/desktop-41jidl2/Omega_vNext/data/level2_frames_mac2024
```

## 5. 断点续训

默认自动续训。脚本会读取：

- `artifacts/epi_race/epi_race_ckpt_rows_*.pkl` 最新检查点
- `processed_files` 集合

如需强制从头跑：

```bash
... run_parallel_epi_race.py --no-resume
```

## 6. 本地暂存与清理策略

1. 每个 chunk 从共享盘拷贝到 `/tmp/omega_epi_stage/chunk_xxxxxx`
2. 该 chunk 完成后立即 `rmtree` 清理（默认开启）
3. 如需保留临时文件排障，可加 `--no-cleanup-stage`

这保证“随用随清理”，避免占满本地盘。

## 7. 胜出判据（第一阶段）

读取 `audit/v34_epi_race_report.json`：

1. 比较 `epiplexity_zlib/lz76/perm` 的 `abs_weight`
2. 绝对值最高者为首轮优选方法
3. 若差异很小（例如 <10%），再做第二轮（不同 `max-files` 分层）复核

建议两轮复核后再进入全量训练。

若报告中出现 `status: "no_fitted_batches"`，说明当前样本在过滤/标签条件下未形成有效训练批次，应增加样本量或放宽实验采样约束后重跑。

## 8. 已知环境前置条件

当前 Mac 解释器环境需具备：

1. `polars`
2. `numpy`
3. `scikit-learn`
4. `psutil`

若缺失 `scikit-learn`，训练无法启动（脚本导入阶段会报错）。
