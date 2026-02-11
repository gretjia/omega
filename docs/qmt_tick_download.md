下面按“产品使用说明书”的粒度，把 **在讯投投研端（MiniQMT/投研端内置 Python）下载并落地 Level-2 tick/逐笔数据** 的流程与可直接交给 AI 写代码的调用细节整理出来，并给出你提到的 **157 只股票批量下载** 的内置 Python 样例。

---

## 0. 先确认：你要的“Level-2 tick”到底是哪一种

在讯投体系里常见有两类“tick 级”数据：

1. **tick（分笔）**：更偏“成交逐笔/分笔线”语义（接口周期名就是 `tick`）。在 `get_market_data()` 中明确支持 `period='tick'`，返回的是每只股票对应的 `np.ndarray`。([dict.thinktrader.net][1])

2. **Level-2 逐笔**：

* `l2order`：逐笔委托
* `l2transaction`：逐笔成交（很多人说“Level-2 tick”实际想要这个）([dict.thinktrader.net][1])

你后面说“基于 level 2 tick 级别的数据”，从研究主力行为/微观结构的常见需求看，**更大概率是 `l2transaction`（逐笔成交）+ 可能还要 `l2order`（逐笔委托）**。

---

## 1) 权限与历史范围/下载约束（决定你能下多长）

在“迅投知识库 → 数据字典 → 快速开始”的权限对比里，明确写了 **投研版权限** 的历史下载范围可到：

* `tick`：最长 **1 年**
* 另有分钟/5分钟到 **3 年** 等（以及“行情数量 300 个限制”一类限制项）([dict.thinktrader.net][2])

你股票池 **157 只**，从“投研版权限行情数量 300 个限制”的表述看，**157 在可支持范围内**（前提是你当前确实是投研权限或已开通相应 Level-2 权限）。([dict.thinktrader.net][2])

---

## 2) 投研端下载 tick/逐笔数据到“本地”的两种路径

### 路径 A：纯界面（GUI）方式（适合先验证权限与速度）

一般做法是通过投研端的数据管理/行情下载（不同版本菜单名略有差异，核心是“下载/补充历史行情”）：

* 选择股票范围：自选股/自定义板块/导入列表
* 选择周期：`tick` 或 Level-2（`l2transaction`/`l2order` 等）
* 选择日期区间
* 执行下载

**关键点**：在 xtdata 的运行逻辑说明里，行情数据请求本质由 **MiniQmt** 处理，数据下载后会落到本地数据文件目录（后续 Python 可直接读“本地数据”）。([dict.thinktrader.net][1])

> 这条路径的价值：你可以先用 1–2 只股票、1–2 个交易日验证“你是否真的有 l2 权限、能否成功落地、落地后 Python 是否能读取”。

---

### 路径 B：内置 Python 批量下载（你要的“157 只股票一键拉取”）

在 XtQuant 的行情模块里，有两组“下载历史行情数据”接口：

* 单只：`download_history_data(stock_code, period, ...)`
* 批量：`download_history_data2(stock_list, period, ..., callback=None, ...)`（同步执行，支持回调进度）([dict.thinktrader.net][1])

这正是你要的“投研端内部 Python 批量下载 157 只股票 tick/逐笔到本地”。

---

## 3) 157 只股票批量下载：可直接用的内置 Python 模板

> 说明：以下代码在“投研端内置 Python / 连接到投研端的 Python 环境”中使用，核心模块是 `from xtquant import xtdata`。xtdata 与 MiniQmt 建立连接，由 MiniQmt 执行下载与落盘。([dict.thinktrader.net][1])

### 3.1 批量下载 Level-2 逐笔成交（推荐：l2transaction）

```python
from xtquant import xtdata

# 你的股票池：157只，格式示例 '000001.SZ' / '600000.SH'
stocks = [
    # ... 填入 157 只代码 ...
]

def on_progress(info: dict):
    # info: {'finished': 1, 'total': 50, 'stockcode': '000001.SZ', 'message': ''}
    print(info)

# 下载逐笔成交：l2transaction
# start_time/end_time 通常用 'YYYYMMDD'（或按你终端支持的时间粒度）
xtdata.download_history_data2(
    stock_list=stocks,
    period="l2transaction",
    start_time="20250101",
    end_time="20250131",
    callback=on_progress
)
```

字段层面，`l2transaction` 在文档附录给出了典型字段（time/price/volume/amount 等，以及 buyNo/sellNo、tradeType、tradeFlag 等）。([dict.thinktrader.net][1])

---

### 3.2 批量下载 Level-2 逐笔委托（如你要做更细的盘口行为建模）

```python
from xtquant import xtdata

stocks = [
    # ... 157只 ...
]

def on_progress(info: dict):
    print(info)

xtdata.download_history_data2(
    stock_list=stocks,
    period="l2order",
    start_time="20250101",
    end_time="20250131",
    callback=on_progress
)
```

`l2order` 字段在附录也有（time/price/volume/entrustNo/entrustType/entrustDirection 等）。([dict.thinktrader.net][1])

---

### 3.3 如果你要的是“普通 tick 分笔”（非 l2 逐笔）

```python
from xtquant import xtdata

stocks = [
    # ... 157只 ...
]

def on_progress(info: dict):
    print(info)

xtdata.download_history_data2(
    stock_list=stocks,
    period="tick",
    start_time="20250101",
    end_time="20250131",
    callback=on_progress
)
```

文档对 `get_market_data()` 明确说明：当 `period='tick'` 时，返回结构是 `{stock: np.ndarray}`（每只股票一个 ndarray，按时间戳递增）。([dict.thinktrader.net][1])

---

## 4) “下载到本地”之后：本地数据目录与如何读取（给 AI 写回测很关键）

下载完成后，你通常不需要再“另存为”，因为数据已经落在 MiniQmt 的本地数据目录。xtdata 提供了**直接从本地数据文件读取**的接口：

* `get_local_data(..., data_dir=...)`：从本地数据文件读取行情数据
* `data_dir` 默认会通过连接向 MiniQmt 获取（即通常不需要你手动填写路径），也可以通过 `xtdata.data_dir` 修改默认值。([dict.thinktrader.net][1])

示例（读取本地已下载数据）：

```python
from xtquant import xtdata

stocks = ['000001.SZ', '600000.SH']

# 示例：读本地 1m K线
bars = xtdata.get_local_data(
    field_list=['open','high','low','close','volume','amount'],
    stock_list=stocks,
    period='1m',
    start_time='20250101',
    end_time='20250131'
)

# tick/逐笔类（tick/l2transaction/l2order）读取时，返回结构通常是 dict: stock -> ndarray（风格与tick一致）
ticks = xtdata.get_market_data(
    stock_list=stocks,
    period='tick',
    start_time='20250101',
    end_time='20250131'
)
```

其中 `get_market_data()` 备注里也强调：**取 lv2 数据需要终端有 lv2 数据权限**。([dict.thinktrader.net][1])

---

## 5) 如果你确实需要“导出到你指定的磁盘目录（CSV/Parquet/Feather）”

讯投的“下载到本地”本质是落到 MiniQmt 数据目录，供终端/xtdata 快速读取。
如果你还要把这批逐笔数据再导出到你自己的目录（例如 `D:\ticks\...`），通用做法是：

1. `download_history_data2()` 先确保本地齐全 ([dict.thinktrader.net][1])
2. `get_market_data()` / `get_local_data()` 拉出来 ([dict.thinktrader.net][1])
3. 用 pandas/numpy 写文件（CSV/Parquet/Feather）

由于逐笔数据返回的是 `np.ndarray`（并非天然带列名 DataFrame），导出前你需要按你选择的数据类型（tick/l2order/l2transaction）映射字段。字段清单在附录里已经给出（尤其是 l2order/l2transaction）。([dict.thinktrader.net][1])

---

## 6) 你问的“有没有内部 Python 代码让投研端下载 157 只股票 tick 数据进入本地？”

结论：**有**，标准做法就是上面的：

* `xtdata.download_history_data2(stock_list, period, start_time, end_time, callback=...)` ([dict.thinktrader.net][1])

并且它是同步执行、可回调进度，正适合“股票池批量预下载 → 再跑回测”。

---

如果你愿意，我可以把你“157 只股票池”的代码生成也一并标准化：

* 支持从（1）自选股导出文本、（2）CSV、（3）QMT自定义板块，自动解析成 `['000001.SZ', ...]`
* 并给出一个“分日下载 + 失败重试 + 断点续传（incrementally）”的工程化模板（更适合 tick/逐笔的大数据量下载）。

[1]: https://dict.thinktrader.net/nativeApi/xtdata.html "XtQuant.XtData 行情模块 | 迅投知识库"
[2]: https://dict.thinktrader.net/dictionary/ "快速开始 | 迅投知识库"
