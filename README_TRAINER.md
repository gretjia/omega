# OMEGA Trainer v1

> Last updated: 2026-02-08 (legacy v1 note, v40 pipeline pointer)

> Status: This document is for legacy v1 trainer context.  
> For v40 production flow, use `jobs/windows_v40/start_v40_pipeline_win.ps1` and read `jobs/windows_v40/README.md`.

本目录包含 OMEGA 的第一版训练器（`trainer.py`）及其所需的最小配套模块。

## 数据集（你当前两套数据）

1. `./data/history_ticks_full`
   - 24,015 个切片 CSV，来自 4000+ A 股
   - 特征：高波动 + 多为跨日连续片段
2. `./data/history_ticks`
   - 156 只精选高波动股票，2025 全年 Level-1 Tick

> 这些数据特征与你的 `training_data_analysis.md` 一致：切片库具有显著高波动与跨日延续，Tick 密度约每文件 7,657 条、平均间隔约 3 秒。用于训练中短线趋势与极端行情非常合适。

## 训练器设计目标

- **不把“阈值”写死在代码里**：所有可调项都在 `config.py`（包括训练器相关参数）。
- **递归闭环（Recursive）**：
  1) 先做一次“校准扫描”(Pass-0)：估计 `S_bps` / `H_bps` 的分布分位数；
  2) 用分位数更新 `DecisionConfig`（这会影响 `epsilon_adaptive`）；
  3) 再在新阈值下重算完整特征并训练模型。

## 训练输出（Artifacts）

训练完成后会输出 `./artifacts/omega_policy.pkl`，其中包含：
- kernel_config（校准后的阈值）
- trainer_config
- feature_names
- sklearn scaler / model
- calibration 字典（分位数阈值）

## 快速运行

1) 修改 `trainer.py::example_trainer_config()` 中的两个 `root_dir` 路径，指向你的真实数据目录  
2) 执行：

```bash
python trainer.py
```

它会：
- 先校准阈值
- 训练 `SGDClassifier(log_loss)`
- 在 val/test split 上输出 Topo_SNR_avg / SRL_Resid_Kurtosis / Epi_Entropy_Corr / Vector_Alignment_avg（数学指标）

## 你大概率需要马上做的定制

1) **切分策略**：v1 默认 file-level split（适合 slices 数据）。  
   如果要在 `history_ticks` 上做更严格的时间切分，建议基于 bar 的 timestamp 做 walk-forward。

2) **标签定义**：当前使用未来 `label_horizon_bars` 的 log-return 符号。  
   你可以改为：
   - 未来收益减 SRL 成本后的符号（净收益标签）
   - 多类别（强上/弱上/震荡/弱下/强下）
   - 回归（预测未来归一化收益/冲击效率等）

3) **特征族扩展**：v1 特征集中在 (S,H)+TDA+SRL+OFI。  
   你可以追加盘口形状特征、价差、成交额、涨跌停状态等，但建议仍保持“所有旋钮放 config”。
