我给你做了一版 **可直接跑的 Trainer v1**（含数据适配、Volume Clock、窗口采样、递归校准、SGD 在线训练、轻量评估），并且严格按你的要求：

* **kernel.py / omega_math_core.py 不写任何硬编码参数**（保持纯数学逻辑）
* **所有可调项统一放在 config.py**（包括训练器的采样窗口、阈值分位数、模型超参、cost 权重等）
* **用 recursive method 做“先校准、再训练”的闭环**：先用数据分布校准 (S_T/H_T) 阈值 → 该阈值会改变 (\epsilon_{adaptive}) → 进而改变 TDA 特征 → 再用一致的特征体系训练模型

你可以直接下载代码包：
[下载 omega_trainer_v1.zip](sandbox:/mnt/data/omega_trainer_v1.zip)

---

## 训练器设计（针对你两套数据）

你当前的 `./data/history_ticks_full` 切片库具有显著的 **高波动** 与 **跨日延续**，并且 CSV 存在两种格式（RQ 标准 vs 简化格式），Tick 密度和时间范围也很清晰。
因此 Trainer v1 的结构是：

### 1) 数据层：统一两种 CSV 格式 → TickData

* `data_adapter.py` 自动识别：

  * **RQ 标准格式**：`datetime`, `last`, `volume`, `a1/b1` 等 
  * **简化格式**：`time(ms)`, `price`, `vol`, `ask1/bid1` 
* 对 `volume` 做 **auto 检测**（若近似单调递增 → 视为累计量，转成 delta；否则视为 per-tick delta），避免你数据源差异导致训练污染。

### 2) 坐标系：Volume Clock（等量 bars）

* `feature_extractor.py` 里 `volume_clock_aggregate_with_time` 把 Tick 转成等量 bars（保留 bar end time）。
* 用它解决 A 股 **物理时间信息密度强非平稳**的问题（早盘 vs 午后），避免 (V,\sigma,H_T) 在不同时段失真。
  这点与你数据分析里“平均 3 秒一跳、清淡时段拉长”的现实一致。

### 3) 递归闭环（Recursive Calibration → Feature Recompute → Train）

Trainer v1 的核心是 **两阶段计算**：

**Pass-0（校准扫描）**
在训练文件上扫描窗口，收集：

* `S_bps = epiplexity_bits_per_sample`
* `H_bps = entropy_bits_per_sample`

用 **reservoir sampling** 估计分位数并写回 `DecisionConfig`：

* `epiplexity_low/high = quantile(q_s_low/q_s_high)`
* `entropy_low/high = quantile(q_h_low/q_h_high)`

**Pass-1（正式训练）**
用更新后的阈值重新抽取特征（因为 (\epsilon_{adaptive}) 依赖 (S) 的归一化，会影响 TDA 特征），然后训练模型。

> 这一步是你要求的“不是线性的 Input→TDA→Trade，而是闭环反馈”：阈值是由数据自己定标，而不是硬编码。

### 4) 特征族（纯数学内核派生）

每个窗口输出一组 feature vector（全部从你数学核导出）：

* 信息分解：`S_bps, H_bps, MDL_bps, AR_order, S_norm, H_norm`
* TDA：`beta1_auc, beta1_max, beta0_min, beta0_adaptive, beta1_adaptive, epsilon_adaptive`
* SRL + 逆问题残差：`ofi, V, sigma, impact_pred, impact_real, iceberg_ratio, iceberg_residual`

这与我们前面约定的 OMEGA 核心一致：

* (S_T/H_T) 正交分解（结构 vs 残差噪声）
* Takens embedding + Betti 结构（尤其 (\beta_1)）
* SRL 的逆问题残差（吸收/隐性流动性证据）

---

## 训练目标（Trainer v1 采用的默认形式）

* **监督学习**：用未来 `label_horizon_bars` 的 log-return 符号做二分类标签：

  * Up → 1；Down → 0；绝对值过小的样本可跳过（threshold 在 config）
* **模型**：`sklearn.SGDClassifier(loss="log_loss")`，支持 streaming / partial_fit，适合大规模 tick 切片与全年数据混合训练
* **样本权重**：默认用 `abs(future_return)`（高波动更“重要”），你也可以改成净收益/冲击效率权重

---

## 如何把两套数据用起来（推荐的训练计划）

Trainer v1 里给了一个默认 curriculum：

* Stage 1：`history_ticks_full`（切片库）做 **pretrain**

  * 好处：跨股票、跨形态，结构模式更丰富（但有“高波动筛选偏置”）
* Stage 2：`history_ticks`（156 只 2025 全年）做 **finetune**

  * 好处：连续时间、更贴近真实交易分布，有利于纠偏与泛化

你只需要在 `trainer.py::example_trainer_config()` 里把两个 `root_dir` 指到真实路径即可。

---

## 你拿到的文件结构

* `config.py`

  * 既包含 KernelConfig（你之前要求的），也包含 TrainerConfig（训练器所有旋钮）
* `omega_math_core.py` / `kernel.py`

  * 原封不动保留为“数学逻辑”
* `data_adapter.py`

  * CSV 解析、格式归一、volume delta 自动识别
* `feature_extractor.py`

  * Volume Clock + 训练用特征抽取（不做交易决策，只抽特征）
* `trainer.py`

  * 校准 → 训练 → 保存 artifacts → val/test 评估
* `README_TRAINER.md`

  * 快速使用说明

---

## 最小运行方式

1. 解压 `omega_trainer_v1.zip` 到你的项目目录
2. 修改 `trainer.py` 里的：

```python
src_slices = DataSourceConfig(root_dir="./data/history_ticks_full", ...)
src_year   = DataSourceConfig(root_dir="./data/history_ticks", ...)
```

3. 运行：

```bash
python trainer.py
```

输出会在 `./artifacts/omega_policy.pkl`。

---

## v1 里我刻意“先不做”的两件事（但接口已留好）

1. **严格时间切分（walk-forward）**：
   v1 默认 `file_fraction`，对切片库最稳；但对全年数据你大概率会想按月份/日期切。
   由于 v1 的 bar timestamp 已保留，你可以在 `trainer.py` 里把 split.method 扩展为 `"time"`。

2. **净收益标签（收益-冲击成本）**：
   v1 标签是纯方向。你后续可以把 label 改成 `future_return - cost_weight * impact_pred` 的符号，从而把 SRL 直接写进监督信号。

---

如果你希望我把 **time-split（walk-forward）** + **净收益标签（含 SRL 成本）** + **多任务输出（方向 + 强度/持有期）** 一次性加进 Trainer v2，我也可以在不破坏“参数全部集中到 config.py”的前提下直接给你升级版结构。
