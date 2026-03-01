我已经把三份关键材料与你当前代码骨架一起看完，并把它们合并成一个**可落地的 Level-2 升级方案**（偏架构与工程实现路线，而不是“写几段公式就完事”）。你现在的条件（2023–2025 全量 L2、磁盘不足、需要边解压边训练）决定了：**核心难点不是“算什么特征”，而是“如何把 L2 变成可重复、可扩展、可审计、不会泄漏的训练样本流”**。  

下面按「目标 → 数据层 → Kernel/数学层 → 训练层 → 工程落地 → 递归审计」给出完整升级计划。

---

## 0) 你当前版本的关键瓶颈（必须先承认，否则 L2 会被浪费）

从上一版 evidence report 的事实看，你 Stage1/Stage2 的“训练失败/无效”，主要不是数学不对，而是**样本流形态不成立**：

* **val/test 样本数极低**（甚至出现只产出 1 个样本的情况），导致任何指标都不可信；根因通常是 volume-bar 阈值、窗口长度、切片方式与数据密度不匹配。
* 数据里存在**盘前/集合竞价/异常时间戳、0 价/0 量段**等污染，会把 SRL/MDL/TDA 的输入退化成“非交易物理”。
* 你现在的 Kernel（L1）TDA 基本只在 price embedding 上工作；“方向性”更多靠 OFI 的符号或 residual 的启发式，**可解释但信息不够**。

L2 升级的第一目标不是“更复杂”，而是：**让 Stage1 的 epistemic metrics 在多年份、多 regime 下稳定成立**，并且让“矢量方向”不再靠猜。

---

## 1) Level-2 升级的总目标（Definition of Done 不是 PnL）

你审计师给的 Level-2 更新建议，本质是在要求你把 Omega 的输入从

> “price/vol 的低维时间序列”
> 升级为
> “order book 作为可观测物理系统的状态轨迹（state trajectory）”
> 并且用 L2 的 **深度、价差、微价格、跨档 OFI** 来重写 SRL 与方向性。

我建议把 DoD（阶段性交付）明确分三层：

### DoD-A：数据物理层（不成立就别谈训练）

* 训练样本在**连续竞价时段**内构建（auction 独立建集或 mask）。
* 每个样本窗口内至少有 `N_points >= 256`（你做 TDA/复杂度分解，点数太少等于伪科学）。
* train/val/test 切分**无重叠泄漏**：同一 `(symbol, trading_date)` 不跨 split。

### DoD-B：数学一致性（纯 epistemic）

* **Topo_SNR** 在结构样本上显著 > 3（你之前审计师也强调“结构必须能在 shuffle 后消失”的显著性检验思路）。
* **SRL residual** 在“平时”接近白噪声，在“战时”出现肥尾/记忆性（可用 kurtosis / Hurst 等）。
* **Epiplexity 与 Entropy 解耦**（相关性接近 0）。

### DoD-C：方向性与可迁移性（但仍不看钱）

* “结构触发”后，**方向判别**（吸筹 vs 派发）在跨年份 OOS 里稳定（而不是只在 2025 有效）。
* 同时做两种泛化：

  1. 时间外推（2023–2024 训，2025 测）
  2. 横截面外推（留出一批未见过股票做 test）

---

## 2) 数据层升级：把“全量 L2”变成“可训练的流”（这是最关键的工程）

你现在的 L2 数据结构（按日压缩包、内部 CSV、GB18030 编码、包含行情/逐笔成交/逐笔委托）已经在 evidence report 中实锤过。
你磁盘不足，README 里给了“边解压边训练”的做法。
但我必须直说：**直接拿 7z 流式 CSV 去做“随机采样训练”会非常痛苦**，因为训练需要反复访问同一天/同一股票/同一窗口，7z 的重复解压会把吞吐打穿。

所以我建议你把数据层拆成两条管线（强烈建议这样做）：

### 2.1 管线 1：一次性“炼油”（Refinery / Baking）→ 生成可随机访问的中间层

目标：只解压一次，把原始 L2 转成**轻量、中间粒度、可随机访问**的数据格式。

**中间层建议（按优先级）：**

1. **Bar 级（Volume Bars / Notional Bars）**：你审计师一直强调从 Time Bars 转 Volume Bars 的物理必要性；L2 更应该这样做。
2. 每个 bar 只保留你训练所需的 state：

   * `mid` / `microprice`
   * `spread`
   * `depth_{k}`（top-K 深度，或加权深度）
   * `OBI`（order book imbalance）
   * `OFI`（multi-level weighted）
   * `trade_notional`, `bar_duration`（用来衡量信息密度）
   * 以及你 Omega 原本的 info decomposition / residual 入口所需变量

**存储格式建议：**

* 不要继续“海量小文件 per-slice CSV”。会把 inode/目录性能打爆。
* 推荐两种稳健方案：

  1. **按 trading_date 分区的 Parquet（ZSTD 压缩）**：易读、可列裁剪、生态成熟。
  2. **单机最强随机访问：LMDB/SQLite + 压缩 blob**（每个 key = (date,symbol)，value = numpy bytes）。

> 你最终要的是：训练阶段能够 O(毫秒) 级取到某个 `(symbol, day)` 的 bar 序列，而不是每次都去解压一遍 7z。

### 2.2 管线 2：事件驱动切片（Golden Setups v2）

你之前的思路是：用日线先筛 silent→burst，再下载 tick。现在你已有全量 L2，所以可以改成：

* 日线（或日级聚合）只负责**粗筛候选日**（把全市场压到 1–5% 的候选）。
* 候选日再用 L2 bar 级信号做**精筛与切片**，输出 Stage1 的“稀有结构样本集”。

这样做的直接好处：

* 你不需要把 2023–2025 全市场所有股票都 bake 成中间层；只 bake 候选日，磁盘压力立刻下降一个数量级。
* Stage1 样本质量显著提升，而且可以做类别均衡（吸筹/派发/噪声对照）。

---

## 3) Level-2 Kernel/数学层适配：从 L1 的“近似物理”升级为“可观测物理系统”

审计师的 level2_update.md 给出的核心方向是：

1. 用 L2 的 order book 深度和微价格
2. 计算 multi-level OFI（而不是用 L1 的粗糙 proxy）
3. 用 “OFI / Depth → 价格响应” 来重构 SRL 与 residual
4. 让方向性从“猜”变成“由 order flow 矢量决定”

我建议把 Kernel 升级拆成 3 个可递增的版本（每一步都能跑通训练）：

---

### 3.1 KernelL2-v1：Quotes-only（最快上线）

只用 `行情.csv`（order book snapshot），不引入逐笔成交/委托。

**新增观测量：**

* `mid = (ask1+bid1)/2`
* `microprice`（利用 bid1/ask1 的量加权，审计师明确建议）
* `spread = ask1 - bid1`
* `depth_K = Σ_{k<=K}(bid_sz_k + ask_sz_k)`（可加权）
* `OBI_K = (Σ bid_sz - Σ ask_sz)/(Σ bid_sz + Σ ask_sz)`
* `OFI_K`：先用 quotes 的 Δqueue 版本（Cont-style OFI），跨档加权求和（审计师明确建议 multi-level）

**SRL（v1）**：

* 形式：`Δmid_pred = κ * OFI / depth`
* residual：`r = Δmid_real - Δmid_pred`
* 你原本的 “iceberg_ratio / residual_kurtosis / Hurst” 逻辑可以直接迁移，但更可信。

**TDA（v1）**：
不要再只做 price embedding。直接做状态点云：
`X_t = [z(mid), z(cum_OFI), z(spread), z(OBI), z(depth)]`
再做 Takens embedding（可选），然后做 Betti 曲线/Betti1 峰值/面积。
并立刻补上 **Topo_SNR 的 shuffle 显著性检验**（你审计师在 L1 阶段就强调过这类思想，而你旧版并未真正固化为 pipeline DoD）。

---

### 3.2 KernelL2-v2：Quotes + Trades（方向性与 SRL 质变）

引入 `逐笔成交.csv` 的买卖方向（如果字段可靠），替代 BVC 近似。

**方向矢量：**

* `signed_volume`（buy=+，sell=-）
* `trade_flow = Σ signed_volume`（可做 volume bars 的天然累计量）
* `aggressor_imbalance`（更强的方向判别）

**OFI 与 SRL：**

* OFI 继续用 order book 变化（这是“供给曲线变化”）
* trade_flow 是“实际冲击输入”
  两者组合可以做更强的物理诊断：
* `Δmid_real` 与 `OFI/depth` 的拟合残差（冰山/暗池注入）
* `trade_flow` 与 `OFI` 的背离（“看起来在买，但 book 没动” vs “book 动了但成交没跟”）

**Vector Alignment（你旧版 kernel 里已有雏形）**：
结构触发（TDA）后，用 trade_flow 或 OFI 的方向与 price momentum 做余弦相似度门控：

* `cos_sim(OFI_vector, momentum_vector) > τ`
  否则把结构视作“下跌中继 / 假环 / 纯噪声”。

---

### 3.3 KernelL2-v3：加入逐笔委托（可选，但对“派发/吸筹”会更像显微镜）

逐笔委托能让你看到撤单波、补单、队列变化（但代价是工程复杂度与吞吐）。

我建议把它作为 **Stage1.5**：在你已经用 v1/v2 跑出稳定 DoD-B 指标后再加，否则很容易陷入“数据工程无限深坑”。

---

## 4) 训练与评估升级：从“预测回报”回到“数学能力训练”

你的审计目标非常明确：先训练 intelligence（识别非随机结构），再训练 survival（PnL）。这与 level2_update.md 的精神一致：它强调先改数据与物理量，再谈策略映射。

我给你一个**可执行的训练分层方案**：

### 4.1 Stage0：只做数据/物理审计（不训练任何模型）

输出一个 `level2_dataset_report.md`，至少包含：

* session 覆盖（盘前/盘中/盘后占比）
* 0 价/异常价占比
* 每个 (symbol,day) 的 bar 数分布（确保 windows 能生成）
* spread、depth、OFI 的分位统计（检验是否合理）
* train/val/test 分组切分后的“重叠率=0”的证明（hash 校验）

> 你上一版 val/test 样本几乎为空的情况，在 Stage0 就应该被发现并阻断。

### 4.2 Stage1：Epistemic Pretrain（只优化认知指标）

训练目标不是收益，而是让模型/参数选择最大化：

* `Topo_SNR`（结构显著性）
* `SRL residual` 的“平时白噪声、战时肥尾/记忆”对比度
* `Corr(Epiplexity, Entropy)` → 0
* `Vector Alignment` → 高

这里你可以有两种路线：

**路线 A（更符合你现在代码形态）：不训练神经网络，训练“参数/阈值/映射”**

* 你 OmegaKernel 里有大量可调项（volume clock 阈值、TDA epsilon、SRL κ、过滤窗口等）。
* Stage1 就做“结构显著性最大化”的参数搜索（贝叶斯/网格/递归）。
* 优点：工程轻、解释强、审计友好。

**路线 B（升级到表示学习，但仍不看钱）：自监督任务**
用 L2 状态序列做：

* 真假辨别（real vs shuffled）
* masked modeling（遮住 OFI/depth 预测下一段 microprice 响应）
* 对比学习（结构窗口 vs 噪声窗口拉开 embedding）

如果你暂时不想引入 DL 复杂度，先走路线 A，把数据与 Kernel 物理打稳，再考虑 B。

### 4.3 Stage2：方向性训练（吸筹 vs 派发），仍不直接优化 PnL

当 Stage1 的 DoD-B 稳定后，再加一个“方向头”：

* label 不用未来收益（容易被 regime 噪声污染），可以用**后验短窗的订单流净方向/价格响应**定义弱标签（例如事件后若干 bar 内 OFI 与 price response 的一致性）。
* 或做半监督：用聚类 + 人工少量审计标签（更符合科学实在论：先定义现象，再定义经济意义）。

---

## 5) 工程落地：你代码库需要怎样升级（文件级别路线图）

结合你当前代码结构（config/data_adapter/feature_extractor/kernel/omega_math_core/trainer），我建议你做**最小破坏式升级**：保留 L1 路径，新增 L2 路径，接口统一到 “BarSequence”。

### 5.1 新增/改造的核心抽象

#### (1) `BarSequence`（统一输入）

一个窗口最终喂给 kernel 的，不再是 raw ticks，而是：

```text
ts_ms: int64[...]
mid: float32[...]
microprice: float32[...]
spread: float32[...]
depth: float32[...]
obi: float32[...]
ofi: float32[...]
trade_flow(optional): float32[...]
bar_duration_ms: int32[...]
```

#### (2) `Level2Refinery`

负责：

* 读取 7z 内部 CSV（GB18030）
* 清洗 session / 去除 0 价段
* 构建 volume/notional bars
* 计算上述 bar 特征
* 输出到中间存储（Parquet/LMDB）

#### (3) `OmegaKernelL2`

输入 `BarSequence`，输出 `KernelOutput`（沿用你旧的结构），但内部改为：

* L2 OFI
* L2 depth
* microprice 驱动的 SRL/residual
* 状态点云 TDA + Topo_SNR

### 5.2 你现有文件的改动清单（建议按提交分阶段）

**提交 1：数据层（不改训练）**

* `data_adapter.py`：新增 `Level2ArchiveReader` / `Level2DayLoader`（支持从 7z 流式读，或从中间层读）。
* `inspect_artifact.py`：新增 `inspect_level2_day()` 输出 Stage0 报告。
* 新增：`level2_refinery.py`（bake 工具 + manifest 生成）。

**提交 2：KernelL2（可单元测试）**

* `omega_math_core.py`：新增

  * `microprice()`
  * `ofi_multilevel()`
  * `effective_depth()`
  * `topo_snr_shuffle_test()`（关键：把显著性检验固化为函数）
* `kernel.py`：新增 `omega_kernel_step_l2(bar_seq, cfg)` 与 `OmegaKernelL2`。

**提交 3：训练适配**

* `feature_extractor.py`：支持从 `BarSequence` 走 feature pipeline（或直接让 kernel 输出作为特征）。
* `trainer.py`：

  * 新增 Stage0/Stage1 的日志字段（Topo_SNR、residual_kurtosis、corr 等），减少/移除早期 PnL 字段。
  * split 逻辑改为按 `(symbol, time_block)` 分组，彻底杜绝重叠泄漏。

**提交 4：性能与缓存**

* 在 refinery 里做：

  * day-level LRU cache（同一天多次访问不重复解压）
  * 并行处理 symbol（多进程）
* 训练时：优先从中间层读；若中间层缺失再 fallback 到 7z 流式构建（lazy bake）。

---

## 6) 关于“边解压边训练”：我给你的更优方案（比 README 更适合随机采样训练）

你 README 的方案本质是“训练时临时解压”。
它适合**顺序扫描式训练**，不适合**随机采样、反复 epoch**。

我建议改成“半在线炼油”：

### 方案：Lazy Bake + Cache（推荐）

* 训练集有一个 `manifest`（列出需要的 `(date, symbol, start_bar, end_bar)`）。
* dataloader 请求样本时：

  1. 先查中间层（parquet/lmdb）是否已有该 `(date,symbol)` 的 bar 序列；
  2. 若无，则触发一次性 bake：只解压该日该 symbol 所需文件，生成 bar 序列写入中间层；
  3. 后续 epoch 直接命中中间层，不再解压。

这会把“边解压边训练”的时间成本，从 **每个 epoch 都付一次**，变成 **首次访问付一次**，训练吞吐会稳定很多。

---

## 7) 递归审计（Recursive Audit）：这个升级计划可能失败的点与防线

最后我用“反对者视角”挑 8 个高风险点，每个给出防线：

1. **时间对齐错误（quotes vs trades）**

   * 风险：用到了未来的 book snapshot 解释当前 trade，形成隐性 lookahead。
   * 防线：事件驱动合并时，trade 使用“上一条可得快照”作为 book 状态；写单元测试校验时间单调。

2. **OFI 公式实现错误（跨档价格变化处理）**

   * 风险：OFI 方向反了，整个 SRL 变成“反物理”。
   * 防线：用人工构造的 3 条 toy book 序列做金标准测试（bid 上移、队列增减、ask 下移三类）。

3. **limit-up/limit-down 与一字板导致深度失真**

   * 风险：depth 爆炸或单边为 0，分母接近 0 导致 SRL 发散。
   * 防线：显式 `is_boundary` mask，边界态单独建集或只用于 regime 分类不用于 SRL 拟合。

4. **集合竞价/盘前 0 价段污染**

   * 防线：严格 session filter（9:30–11:30, 13:00–15:00），auction 独立处理。

5. **Volume-bar 阈值选错 → 样本点数不足**

   * 防线：阈值用动态规则（过去 N 日 ADV 的分数），并在 Stage0 报告里强制检查 `bars_per_day` 分布；低于阈值直接拒绝训练（这是数据质量门，而不是策略硬约束）。

6. **重叠切片导致 train/test 泄漏**

   * 防线：split 先按 `symbol + week/month block` 分组，再在组内取窗口；并做 hash 校验证明 0 重叠。

7. **“结构显著性”被厚尾噪声伪造**（Topo_SNR 假阳性）

   * 防线：shuffle 不仅做完全随机，也做 block shuffle / circular shift；显著性必须在多种 null 下稳健。

8. **工程吞吐跟不上（全量 L2 太大）**

   * 防线：候选日粗筛 + Lazy Bake；不要试图把全市场三年全量都 materialize 成中间层。

---

## 你下一步最该做的 3 件事（最小闭环）

1. **Stage0 报告**：先把 L2 的数据健康与 bar 密度跑出来（不训练）。
2. **KernelL2-v1（quotes-only）**：先把 microprice/depth/OFI/SRL residual + Topo_SNR 跑通并可视化。
3. **Golden Setups v2 生成**：从 2023–2025 中抽出“结构窗口 + 噪声窗口”的平衡数据集，保证 val/test 有足够样本量。

---

如果你同意这个升级路线，下一步我可以直接按“提交 1→4”的顺序，把你现有的 `data_adapter.py / kernel.py / omega_math_core.py / trainer.py` 逐文件给出**具体的代码改造草案（包含接口签名、数据结构、关键函数的实现骨架、以及必要的单元测试模板）**，确保你可以边改边验证，而不是一次性重构到不可控。
