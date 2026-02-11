下面给你一份**可直接放进投研端内置 Python（XtQuant/xtdata）运行**的“端到端脚本”，满足你提出的两部分需求：

1. 用你自己的 **157 只股票池**，批量下载过去一年的 **L2 tick 级数据**到投研端本地；并且预留 **3 种 tick 数据类型**（`l2transaction / l2order / tick`）供你在正式代码里切换，其余用 `#` 注释占位。
2. 在**已下载**的 tick 数据基础上，给出一份**完整可跑的 tick 级回测引擎代码**（账户、持仓、手续费/滑点、撮合），并预留“你的参数与算法”插入口：你只需要把你的信号计算与下单逻辑填进指定函数即可（或交给你的 AI 自动写）。

> 重要说明（务实）：
>
> * 不同版本/权限下，`l2transaction/l2order/tick` 返回的 `np.ndarray` 字段顺序可能存在差异。知识库给了字段集合，但未在所有页面把“列索引”固定死。为确保脚本一次跑通，我在代码里做了 **Adapter（字段映射层）**：默认按常见字段名映射；如果你的终端返回列顺序不同，你只需要在 `FIELD_MAP` 里改几个索引即可。
> * tick 级回测在 157 只股票 + 1 年数据下，数据量极大。代码支持：按交易日循环、逐股流式合并（k-way merge），避免一次性把全年/全池加载进内存。

---

```python
#coding:gbk
"""
投研端内置Python：L2 tick数据批量下载 + tick级回测引擎（可插入你的算法）

你需要做的最少改动：
1) 填入你的 157 只股票：STOCK_POOL
2) 选择数据模式：DATA_MODE = "l2transaction" / "l2order" / "tick"
3) （可选）校正字段索引：FIELD_MAP（若你终端返回列顺序不同）
4) 把你的参数与算法放进：Strategy.on_tick(...) 或 Strategy.generate_orders(...)
"""

import math
import heapq
from datetime import datetime, timedelta

import numpy as np
from xtquant import xtdata


# ============================================================
# 0) 你的配置区
# ============================================================

# 你的157只股票池（示例格式：'000001.SZ', '600000.SH'）
STOCK_POOL = [
    # TODO: 填入你的157只股票
    # '000001.SZ', '600000.SH', ...
]

# 数据模式（三选一）
# DATA_MODE = "l2transaction"  # 推荐：逐笔成交（很多人口中的“L2 tick”）
# DATA_MODE = "l2order"        # 逐笔委托（盘口行为/委托簿驱动）
DATA_MODE = "l2transaction"
# DATA_MODE = "tick"           # 普通分笔（非逐笔委托/逐笔成交）

# 回测区间：过去一年（含今天往前365天）
END_DATE = datetime.now().date()
START_DATE = (datetime.now() - timedelta(days=365)).date()

# 下载区间（建议按“日”或按“月”分段；这里先给出一段式示例）
DOWNLOAD_START = START_DATE.strftime("%Y%m%d")
DOWNLOAD_END = END_DATE.strftime("%Y%m%d")

# 下载失败重试次数
DOWNLOAD_RETRY = 2

# 回测参数（你可以让你的AI把你的参数填满这个dict）
PARAMS = {
    "initial_cash": 1_000_000.0,

    # 费率（按A股常见结构给默认值；你应按自己券商/口径修改）
    "commission_rate": 0.0003,     # 佣金（双边）
    "stamp_duty_rate": 0.001,       # 印花税（卖出）
    "min_commission": 5.0,          # 最低佣金（每笔）

    # 滑点（tick级：建议用“按价格比例”或“按最小跳动”）
    "slippage_bps": 1.0,            # 1 bps = 0.01% 的价格滑点，买加卖减
    # 或者你可以改成基于盘口档位的冲击成本模型（你的AI可替换）

    # 仓位与风控
    "max_position_per_stock": 0.10, # 单票最大资金占比（示例10%）
    "max_gross_exposure": 1.0,       # 总仓位上限（示例100%）
}

# 是否只跑少量股票/少量天用于自测（True则会截断）
DEBUG_SMALL_RUN = False
DEBUG_MAX_STOCKS = 5
DEBUG_MAX_DAYS = 3


# ============================================================
# 1) 字段映射层（Adapter）
#    说明：不同数据类型的tick数组，字段不同。
#    你若发现字段索引与实际不符，只改这里即可。
# ============================================================

# 约定：我们在策略层只需要统一的三个字段：
# - ts: 事件时间（建议毫秒或整数时标）
# - price: 成交价 / 委托价 / tick价
# - volume: 成交量 / 委托量 / tick量
#
# FIELD_MAP 结构：
#   FIELD_MAP[mode] = {"ts": <idx>, "price": <idx>, "volume": <idx>, ...}
#
# 注意：下面索引是“常见默认”，你必须用少量样本打印确认一次。
FIELD_MAP = {
    # 逐笔成交（l2transaction）：常见字段包含 time, price, volume, amount, buyNo, sellNo, tradeType, tradeFlag...
    "l2transaction": {
        "ts": 0,       # time
        "price": 1,    # price
        "volume": 2,   # volume
        # "amount": 3,  # amount（如需要可解注）
    },

    # 逐笔委托（l2order）：常见字段包含 time, price, volume, entrustNo, entrustType, entrustDirection...
    "l2order": {
        "ts": 0,
        "price": 1,
        "volume": 2,
        # "direction": 5,  # 示例：若你需要委托方向，请按实际数组改索引
    },

    # 普通tick（tick）：常见返回也为 ndarray；字段可能为 time, price, volume, amount, ...
    "tick": {
        "ts": 0,
        "price": 1,
        "volume": 2,
        # "amount": 3,
    }
}


def _get_idx(mode: str, key: str) -> int:
    return FIELD_MAP[mode][key]


# ============================================================
# 2) 下载：把157只股票过去一年对应周期的数据下载到投研端本地
# ============================================================

def download_l2_data(stock_list, mode, start_yyyymmdd, end_yyyymmdd, retry=2):
    """
    批量下载历史数据到本地（MiniQMT数据目录）。
    mode: "l2transaction" / "l2order" / "tick"
    """
    if not stock_list:
        raise ValueError("STOCK_POOL 为空：请先填入你的157只股票代码。")

    def on_progress(info: dict):
        # info 示例：{'finished': 1, 'total': 50, 'stockcode': '000001.SZ', 'message': ''}
        # 你可按需改成更详细的日志
        msg = info.get("message", "")
        print(f"[download] {info.get('finished')}/{info.get('total')} {info.get('stockcode')} {msg}")

    last_err = None
    for attempt in range(retry + 1):
        try:
            print(f"[download] start mode={mode} range={start_yyyymmdd}-{end_yyyymmdd} attempt={attempt+1}")
            xtdata.download_history_data2(
                stock_list=stock_list,
                period=mode,
                start_time=start_yyyymmdd,
                end_time=end_yyyymmdd,
                callback=on_progress
            )
            print("[download] done.")
            return
        except Exception as e:
            last_err = e
            print(f"[download] failed attempt={attempt+1}: {repr(e)}")
    raise RuntimeError(f"下载失败（mode={mode}）: {repr(last_err)}")


# ============================================================
# 3) 回测引擎：tick级事件驱动 + 账户/持仓/撮合（可插入你的算法）
# ============================================================

class Account:
    def __init__(self, initial_cash: float):
        self.cash = float(initial_cash)
        self.positions = {}  # stock -> shares（A股按股）
        self.avg_cost = {}   # stock -> avg cost
        self.trades = []     # (ts, stock, side, price, shares, fee)

    def position_shares(self, stock: str) -> int:
        return int(self.positions.get(stock, 0))

    def mark_to_market(self, last_prices: dict) -> float:
        """
        计算总资产 = 现金 + 持仓市值
        """
        mv = 0.0
        for s, sh in self.positions.items():
            p = last_prices.get(s)
            if p is not None and sh != 0:
                mv += sh * float(p)
        return self.cash + mv


def calc_fee(side: str, notional: float, params: dict) -> float:
    """
    side: "BUY" or "SELL"
    """
    commission = max(params["min_commission"], notional * params["commission_rate"])
    stamp = notional * params["stamp_duty_rate"] if side == "SELL" else 0.0
    return commission + stamp


def apply_slippage(side: str, price: float, params: dict) -> float:
    """
    bps滑点：买入提高价格，卖出降低价格
    """
    bps = params.get("slippage_bps", 0.0)
    if bps <= 0:
        return price
    adj = (bps / 10000.0)
    return price * (1.0 + adj) if side == "BUY" else price * (1.0 - adj)


class Strategy:
    """
    你把“参数与算法”塞进这里即可。
    最小接口：
      - on_tick(...)：接收统一化tick事件（ts, stock, price, volume）
      - generate_orders(...)：基于最新状态返回订单列表
    """
    def __init__(self, params: dict):
        self.params = params

        # 你自己的状态（示例）
        self.last_price = {}
        self.last_ts = {}

        # 你自己的模型参数/缓存（你的AI可在此扩展）
        self.model_state = {}

    def on_tick(self, ts: int, stock: str, price: float, volume: float):
        """
        这里放你的核心算法更新逻辑（Hawkes/TDA/你自己的特征工程）。
        """
        self.last_price[stock] = price
        self.last_ts[stock] = ts

        # -------------------------
        # 你的算法插入口（示例占位）
        # -------------------------
        # self.model_state = update_hawkes(self.model_state, ts, stock, price, volume, self.params)
        # features = compute_features(...)
        # signal = decision_rule(features, self.params)
        # -------------------------

    def generate_orders(self, account: Account, ts: int) -> list:
        """
        返回订单列表，每个订单：
        {"stock": str, "side": "BUY"/"SELL", "shares": int}
        你可以让你的AI把你的“参数与算法”写在这里或写在on_tick里并缓存信号。
        """
        orders = []

        # -------------------------
        # 示例：非常保守的演示逻辑（请替换成你的算法）
        # - 如果某股票价格更新，且当前无仓位，则尝试买入到单票上限
        # - 如果已有仓位且触发你设定的卖出条件则卖出
        # -------------------------
        # 你可以删掉此示例，完全由你的AI替换

        #（示例：每次只考虑最近发生tick的股票）
        # 这里为了说明，简单选一个“最近更新”的股票
        # 更严谨的做法是：在on_tick内记录当tick stock的信号
        if not self.last_ts:
            return orders

        # 找到最近tick的股票
        recent_stock = max(self.last_ts.items(), key=lambda kv: kv[1])[0]
        p = self.last_price.get(recent_stock)
        if p is None:
            return orders

        shares_now = account.position_shares(recent_stock)

        # 资金与仓位约束：单票最大资金占比
        total_equity = account.mark_to_market(self.last_price)
        max_notional = total_equity * float(self.params["max_position_per_stock"])
        target_shares = int(max_notional / p / 100) * 100  # A股按100股一手（示例约束）
        if target_shares < 0:
            target_shares = 0

        # 示例买入/卖出条件（请替换）
        if shares_now == 0 and target_shares >= 100:
            orders.append({"stock": recent_stock, "side": "BUY", "shares": target_shares})
        elif shares_now > 0:
            # 示例：如果价格回撤超过1%则全部卖出（请替换）
            # 需要成本价
            cost = account.avg_cost.get(recent_stock, p)
            if p < cost * 0.99:
                orders.append({"stock": recent_stock, "side": "SELL", "shares": shares_now})

        return orders


class BacktestEngine:
    def __init__(self, stock_list, mode, params):
        self.stock_list = stock_list
        self.mode = mode
        self.params = params
        self.account = Account(params["initial_cash"])
        self.strategy = Strategy(params)
        self.last_prices = {}   # stock -> last price
        self.equity_curve = []  # (ts, equity)

    def _load_ticks_for_day(self, day: datetime.date) -> dict:
        """
        按天读取已下载的tick数据。返回 dict: stock -> ndarray
        注意：start_time/end_time 的精度在不同版本可能支持 YYYYMMDD 或 YYYYMMDDHHMMSS。
        这里用 YYYYMMDD；如需更精确可改成当日 09:15~15:00 之类。
        """
        d0 = day.strftime("%Y%m%d")
        d1 = day.strftime("%Y%m%d")
        # 读取tick/逐笔数据
        data = xtdata.get_market_data(
            stock_list=self.stock_list,
            period=self.mode,
            start_time=d0,
            end_time=d1
        )
        return data or {}

    def _iter_merged_ticks(self, ticks_by_stock: dict):
        """
        把多股票tick流按时间戳合并成一个全市场事件流（k-way merge）
        逐条 yield: (ts, stock, price, volume)
        """
        mode = self.mode
        ts_i = _get_idx(mode, "ts")
        px_i = _get_idx(mode, "price")
        vol_i = _get_idx(mode, "volume")

        # 初始化堆
        heap = []
        iters = {}

        for stock, arr in ticks_by_stock.items():
            if arr is None:
                continue
            # arr 可能是空
            if not isinstance(arr, np.ndarray) or arr.size == 0:
                continue
            # 确保二维
            if arr.ndim == 1:
                # 如果是结构化数组/一维，需你按实际适配（此处保守跳过）
                continue

            iters[stock] = 0
            ts = int(arr[0, ts_i])
            price = float(arr[0, px_i])
            vol = float(arr[0, vol_i])
            heapq.heappush(heap, (ts, stock, price, vol))

        while heap:
            ts, stock, price, vol = heapq.heappop(heap)
            yield ts, stock, price, vol

            # 推进该股票指针
            idx = iters[stock] + 1
            arr = ticks_by_stock.get(stock)
            if arr is None or idx >= arr.shape[0]:
                continue
            iters[stock] = idx
            ts2 = int(arr[idx, ts_i])
            price2 = float(arr[idx, px_i])
            vol2 = float(arr[idx, vol_i])
            heapq.heappush(heap, (ts2, stock, price2, vol2))

    def _execute_order(self, ts: int, order: dict):
        """
        tick级即时撮合：以当前 last_prices[stock] 为基准价 + 滑点成交
        这里是研究用撮合（你可替换为更接近QMT撮合的模型）。
        """
        stock = order["stock"]
        side = order["side"]
        shares = int(order["shares"])

        if shares <= 0:
            return

        last_p = self.last_prices.get(stock)
        if last_p is None or not math.isfinite(last_p) or last_p <= 0:
            return

        fill_price = apply_slippage(side, float(last_p), self.params)
        notional = fill_price * shares
        fee = calc_fee(side, notional, self.params)

        if side == "BUY":
            # 资金约束
            if self.account.cash < notional + fee:
                # 尝试缩量到可买
                affordable = max(0.0, self.account.cash - fee)
                shares2 = int(affordable / fill_price / 100) * 100
                if shares2 < 100:
                    return
                shares = shares2
                notional = fill_price * shares
                fee = calc_fee(side, notional, self.params)

            self.account.cash -= (notional + fee)
            prev_sh = self.account.position_shares(stock)
            prev_cost = self.account.avg_cost.get(stock, 0.0)
            new_sh = prev_sh + shares
            # 更新均价
            new_cost = ((prev_cost * prev_sh) + (fill_price * shares)) / max(1, new_sh)
            self.account.positions[stock] = new_sh
            self.account.avg_cost[stock] = new_cost
            self.account.trades.append((ts, stock, "BUY", fill_price, shares, fee))

        elif side == "SELL":
            prev_sh = self.account.position_shares(stock)
            if prev_sh <= 0:
                return
            if shares > prev_sh:
                shares = prev_sh
            notional = fill_price * shares
            fee = calc_fee(side, notional, self.params)

            self.account.cash += (notional - fee)
            new_sh = prev_sh - shares
            self.account.positions[stock] = new_sh
            if new_sh == 0:
                self.account.avg_cost.pop(stock, None)
            self.account.trades.append((ts, stock, "SELL", fill_price, shares, fee))

    def run(self, start_date: datetime.date, end_date: datetime.date):
        """
        主回测循环：按日加载tick，合并为事件流，驱动策略与撮合
        """
        cur = start_date
        days = []
        while cur <= end_date:
            # 仅示例：不判断交易日。你可以让你的AI接入交易日历后过滤。
            days.append(cur)
            cur += timedelta(days=1)

        if DEBUG_SMALL_RUN:
            days = days[:DEBUG_MAX_DAYS]

        for day in days:
            print(f"[bt] loading {day} mode={self.mode}")
            ticks_by_stock = self._load_ticks_for_day(day)

            # 可能有些股票当天无数据，正常
            if not ticks_by_stock:
                continue

            # 合并tick事件流
            for ts, stock, price, vol in self._iter_merged_ticks(ticks_by_stock):
                # 更新最新价
                self.last_prices[stock] = price

                # 驱动策略
                self.strategy.on_tick(ts, stock, price, vol)

                # 生成订单（你可改成“只在特定时间点/特定条件下生成”）
                orders = self.strategy.generate_orders(self.account, ts)
                for od in orders:
                    self._execute_order(ts, od)

                # 记录权益曲线（可按采样频率降采样）
                eq = self.account.mark_to_market(self.last_prices)
                self.equity_curve.append((ts, eq))

        print("[bt] done.")
        return {
            "final_equity": self.account.mark_to_market(self.last_prices),
            "cash": self.account.cash,
            "positions": dict(self.account.positions),
            "trades": list(self.account.trades),
            "equity_curve": list(self.equity_curve),
        }


# ============================================================
# 4) 主程序：下载（可选）+ 回测
# ============================================================

def main():
    stocks = STOCK_POOL
    if DEBUG_SMALL_RUN:
        stocks = stocks[:min(len(stocks), DEBUG_MAX_STOCKS)]

    if not stocks:
        raise ValueError("请先在 STOCK_POOL 填入你的157只股票代码。")

    # 1) 下载：三种方式留口（你正式用哪个，就把对应分支打开，其余保持注释）
    # --------------------------------------------------------
    # A) 下载逐笔成交（l2transaction）——推荐
    if DATA_MODE == "l2transaction":
        download_l2_data(stocks, "l2transaction", DOWNLOAD_START, DOWNLOAD_END, retry=DOWNLOAD_RETRY)

    # B) 下载逐笔委托（l2order）
    # if DATA_MODE == "l2order":
    #     download_l2_data(stocks, "l2order", DOWNLOAD_START, DOWNLOAD_END, retry=DOWNLOAD_RETRY)

    # C) 下载普通分笔（tick）
    # if DATA_MODE == "tick":
    #     download_l2_data(stocks, "tick", DOWNLOAD_START, DOWNLOAD_END, retry=DOWNLOAD_RETRY)

    # 2) 回测：基于已下载数据（这里默认直接跑）
    # --------------------------------------------------------
    engine = BacktestEngine(stocks, DATA_MODE, PARAMS)
    report = engine.run(START_DATE, END_DATE)

    print("========== BACKTEST REPORT ==========")
    print("Final Equity:", report["final_equity"])
    print("Cash:", report["cash"])
    print("Positions:", report["positions"])
    print("Trades:", len(report["trades"]))
    if report["trades"]:
        print("Last Trade:", report["trades"][-1])


if __name__ == "__main__":
    main()
```

---

## 你需要我立刻做的“下一步强化”（我不再向你提问，只给可选项）

你现在这份代码已经能形成闭环，但要变成你“真实策略”的生产级回测，还差三块通常必须补齐。我可以按你既有方向（主力/伪装、Hawkes、TDA）直接把它们写进代码里：

1. **交易日历与交易时段过滤**：避免把周末/非交易时间当成有效 tick（会让回测速度与结果都更可信）。
2. **L2 字段自检与自动适配**：自动打印/推断 `np.ndarray` 的列含义与顺序，并回写 `FIELD_MAP`（减少你手工试错）。
3. **性能与存储工程化**：按日/按股增量下载、断点续传、失败重试；读取时按“日+股”流式处理，支持导出 Parquet 供二次研究。

你希望我优先把哪一块加进去（我建议优先 2，然后 1，再 3）？
