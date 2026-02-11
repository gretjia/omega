下面按“产品使用说明书”的颗粒度，把**讯投投研端（内置 Python）做回测**的完整流程、关键对象/函数、以及你要交给另一个 AI 自动写代码时应明确的“调用契约”整理出来；最后回答你关于**外部 Python + xtquant**是否能达到同等质量回测。

---

## 1) 总体架构：投研端内置 Python 回测是怎么跑起来的

### 1.1 生命周期与驱动模型

投研端内置 Python 策略是由系统以固定生命周期调用的，不是你手动 main() 启动：

* `init(ContextInfo)`：策略启动时仅调用一次，用于参数初始化、订阅等。文档明确说明：`ContextInfo` 是运行环境对象，不建议给它挂太多自定义属性（会随 bar 切换回滚到上一根 bar 的结束状态），推荐用自建全局变量存状态。([dict.thinktrader.net][1])
* `after_init(ContextInfo)`：初始化后可做“只执行一次”的动作（例如立刻委托）。([dict.thinktrader.net][1])
* `handlebar(ContextInfo)`：行情事件函数。历史回测时按时间顺序逐根 K 线触发；盘中实时行情时还会被 tick 驱动触发。([dict.thinktrader.net][1])
* `stop(ContextInfo)`：停止前调用。注意 stop 时交易连接已断开，不能在 stop 里下单/撤单。([dict.thinktrader.net][1])

辅助判定：

* `ContextInfo.is_last_bar()`：是否到右侧最新 K 线。([dict.thinktrader.net][1])
* `ContextInfo.is_new_bar()`：盘中某根 K 线的第一个 tick 到来时为 True。([dict.thinktrader.net][1])

---

## 2) 回测前置：数据准备是“能不能回测”的第一道门

### 2.1 先把本地历史行情补齐（强制要求）

知识库对回测模型的要求非常明确：

1. 首次下载历史行情：客户端左上角 **“操作 → 数据管理 → 补充行情”**，选择周期（如日线）、板块（如沪深 A 股板块）、时间范围（全部）下载到本地。([dict.thinktrader.net][2])
2. 设置每日定时更新：客户端右下角 **“行情 → 批量下载”** 勾选 **“定时下载”**，让它每天自动补增量数据到本地。([dict.thinktrader.net][2])

### 2.2 回测读本地数据：`get_market_data_ex(subscribe=False)`

回测遍历固定历史数据，**不需要订阅实时行情**，应使用 `get_market_data_ex` 并指定 `subscribe=False` 从本地行情文件读取，速度更快且不受订阅数量限制（但前提是你已下载对应历史数据）。([dict.thinktrader.net][2])

---

## 3) 投研端回测的“标准操作流程”（UI + 代码）

### 3.1 UI 操作（你需要告诉 AI：回测是在投研端界面里触发的）

知识库在回测示例处指向“界面操作-策略回测”，并给出可直接复制运行的示例策略。你可以把它抽象成以下流程：

1. 打开投研端策略编辑器，新建/打开一个 Python 策略脚本
2. 第一行写 `#coding:gbk`（文档明确要求脚本编码统一 GBK）([dict.thinktrader.net][2])
3. 填写 `init/handlebar`
4. 在“策略回测”界面设置：标的（主图品种或股票列表/板块）、周期（如 1d/5m）、回测区间、资金（可用默认或脚本里自设）
5. 点击回测运行，查看净值曲线、交易明细等

> 回测示例代码中，标的是 `C.stockcode + '.' + C.market`（主图品种），并设置 `C.period`、`C.accountid` 等。([dict.thinktrader.net][2])

---

## 4) 核心 API 说明（按“说明书”口径给到你的 AI）

下面是你交给另一个 AI 生成策略代码时，必须让它“按契约调用”的关键接口。

### 4.1 行情获取：`ContextInfo.get_market_data_ex(...)`

**原型（内置 Python）**：([dict.thinktrader.net][3])
`ContextInfo.get_market_data_ex(fields=[], stock_code=[], period='follow', start_time='', end_time='', count=-1, dividend_type='follow', fill_data=True, subscribe=True)`

* 回测推荐：`subscribe=False`（读本地历史）([dict.thinktrader.net][2])
* 常用字段（K 线）：`open/high/low/close/volume/amount` 等；tick 周期字段集合不同。([dict.thinktrader.net][3])
* 注意事项：不建议在 `init` 中运行；在 `init` 中运行时仅能取到本地数据。([dict.thinktrader.net][3])

**回测示例中典型用法**（关键点：用当前 bar 的 timetag 作为 `end_time`，并取足够长 `count` 做指标窗口）：([dict.thinktrader.net][2])

* `bar_date = timetag_to_datetime(C.get_bar_timetag(C.barpos), '%Y%m%d%H%M%S')`
* `C.get_market_data_ex(['close'], [C.stock], end_time=bar_date, period=C.period, count=窗口长度, subscribe=False)`

### 4.2 回测下单与撮合：`passorder(...)` 与撮合规则

知识库给出两层信息：

**(1) 撮合规则（回测引擎怎么成交）**：

* 指定价格在当前 K 线高低点区间内按指定价撮合；超过高低点则按当前 K 线收盘价撮合。
* 委托数量大于可用数量时，按可用数量撮合。([dict.thinktrader.net][2])

**(2) 下单函数 `passorder` 的行为与 quickTrade**：

* 默认是“逐 K 线生效”：信号在最后一根 K 线走完后生成，在下一根 K 线第一个 tick 来时触发下单；
* `quickTrade=1`：当处于非历史 bar（`is_last_bar()==True`）时调用即触发下单；
* `quickTrade=2`：不判断 bar 状态，历史 bar 调用也会触发下单（谨慎）。([dict.thinktrader.net][4])

并且文档给出 after_init 立刻下单示例（含投资备注 msg）：([dict.thinktrader.net][1])

> 你在让 AI 写策略时，应要求它：
>
> * 回测模式一般不用 quickTrade=2；
> * 在 `handlebar` 里先用 `is_last_bar()` 过滤“历史 bar 不发实盘信号”的逻辑（完整示例里也这么做）。([dict.thinktrader.net][5])

### 4.3 回测资金/持仓/委托查询：`get_trade_detail_data(...)`

回测示例用它取资金与持仓：

* `get_trade_detail_data('test', 'stock', 'account')` 取可用资金
* `get_trade_detail_data('test', 'stock', 'position')` 取持仓列表，再组装成字典。([dict.thinktrader.net][2])

交易函数页也明确 `get_trade_detail_data` 属于交易查询函数体系（并且 `passorder` 的 `strategyName` 可用于区分不同策略产生的委托/成交集合）。([dict.thinktrader.net][6])

---

## 5) 一份“可交给 AI 的最小策略骨架规范”（强约束版本）

你可以直接把以下规范（不是代码）交给你的 AI，让它按此生成回测代码：

1. 文件头必须 `#coding:gbk` ([dict.thinktrader.net][2])
2. 必须实现 `init(C)` 与 `handlebar(C)`；可选实现 `after_init(C)` / `stop(C)` ([dict.thinktrader.net][1])
3. `init(C)` 只做参数与标的设定：

   * `C.stock = C.stockcode + '.' + C.market`（单标的）或用板块函数拿列表（如示例用板块“上证50”）([dict.thinktrader.net][2])
   * 设定指标窗口、回测账号字符串 `C.accountid='test'` 等
4. `handlebar(C)` 每根 bar：

   * 用 `timetag_to_datetime(C.get_bar_timetag(C.barpos), fmt)` 得到当前 bar 时间 ([dict.thinktrader.net][2])
   * 用 `C.get_market_data_ex(..., end_time=bar_date, count=窗口, subscribe=False)` 取历史窗口行情 ([dict.thinktrader.net][2])
   * 用 `get_trade_detail_data(accountid, 'stock', 'account'/'position')` 得到可用资金与持仓 ([dict.thinktrader.net][2])
   * 生成交易信号后调用 `passorder(...)` 下单，并遵守 quickTrade 语义 ([dict.thinktrader.net][4])
5. 状态保存：不要依赖在 `ContextInfo` 上持久挂载复杂状态；用全局对象/全局变量保存（知识库明确警告）。([dict.thinktrader.net][1])

---

## 6) 你问的关键问题：外部 Python + xtquant，能否做到同等质量回测？

### 6.1 能做到“同数据质量”，但未必“同回测引擎质量”

* **数据层面**：外部 Python 通过 `xtquant/xtdata` 可以获取行情数据、并可连接投研端数据服务（示例里提到 `xtdata.reconnect(port=58613)`，并展示 `xtdata.get_market_data_ex` / `xtdata.subscribe_quote` 的用法）。([dict.thinktrader.net][7])
  这意味着：你可以在外部 Python 中获得与投研端一致的数据源（取决于你的权限与下载情况）。

* **回测引擎层面**：投研端内置回测已经内置了撮合规则与资金/持仓记账逻辑（撮合规则在知识库有明确描述）。([dict.thinktrader.net][2])
  外部 Python 若要达到“同等质量”，你需要自己实现（或选择框架实现）：

  * 撮合/滑点/手续费/最小成交单位等规则，并尽量复现投研端撮合描述；([dict.thinktrader.net][2])
  * 资金与持仓的日内/逐 bar 记账；
  * 复权/分红送转处理策略（`get_market_data_ex` 有 `dividend_type` 等参数，但外部框架如何一致处理需要你统一口径）。([dict.thinktrader.net][3])

结论：

* **“同质量数据”**：可以（xtquant/xtdata 能做到）。([dict.thinktrader.net][7])
* **“同质量回测结果（与投研端一致）”**：只有在你把撮合与记账规则严格对齐时才可以；否则很容易出现净值、成交价、换手等差异。([dict.thinktrader.net][2])

### 6.2 一个实务建议（避免你在工程上走弯路）

* 如果你的目标是：**尽可能与投研端回测一致、并快速迭代策略逻辑**
  → 优先用**投研端内置 Python 回测**，让系统提供撮合与报表。([dict.thinktrader.net][2])

* 如果你的目标是：**在外部 Python 做更复杂的研究/大规模组合回测/自定义撮合**
  → 用 xtquant 拿数据，然后用你自己的回测框架（或自研）实现撮合与账本；并把“投研端撮合规则”写成单元测试对齐。([dict.thinktrader.net][2])

---

## 7) 你接下来如果要我继续“补齐到可直接生成代码”的程度

我可以在你确认“回测对象类型”后，把“策略生成契约”进一步细化到字段级（例如：多标的组合、板块轮动、日频/分钟频、是否需要 Level2 字段、是否需要订单流/资金流向等特色数据，因为 `get_market_data_ex` 也支持取这些数据）。([dict.thinktrader.net][3])

你只需要回答一句：你要让 AI 写的回测属于哪一类？

1. 单标的（主图股票）逐日/逐分钟
2. 板块成分股多标的（例如上证50/沪深300）
3. 自建股票池（你自选股/自定义篮子）
4. 期货/期权/可转债（数据结构与撮合细节会不同）

[1]: https://dict.thinktrader.net/innerApi/system_function.html "系统函数 | 迅投知识库"
[2]: https://dict.thinktrader.net/innerApi/start_now.html "快速开始 | 迅投知识库"
[3]: https://dict.thinktrader.net/innerApi/data_function.html "行情函数 | 迅投知识库"
[4]: https://dict.thinktrader.net/innerApi/trading_function.html?utm_source=chatgpt.com "交易函数"
[5]: https://dict.thinktrader.net/innerApi/code_examples.html?utm_source=chatgpt.com "完整示例"
[6]: https://dict.thinktrader.net/innerApi/trading_function.html "交易函数 | 迅投知识库"
[7]: https://dict.thinktrader.net/videos/touyan/ty_native_python.html "原生Python_策略回测_投研端 | 迅投知识库"
