#coding:gbk
"""
OMEGA v13.0 (QMT/讯投投研端 内置Python可直接执行版本)
-----------------------------------------------------------------
目的：
1) 将你现有的 OMEGA kernel/config 的“研究态脚本”整理为 QMT 策略脚本骨架；
2) 适配投研端内置Python的生命周期：init / handlebar / after_init / stop；
3) 支持 tick/L2 数据驱动回测：你只需在投研端回测界面选择 period=tick 或 l2transaction/l2order（若版本支持），并下载好历史数据。

重要说明（请务必读）：
- 你上传的 kernel.py / config.py 含有“...”占位符（不是合法Python）。本文件已替换为可运行的“兼容实现 + 可插拔接口”。
- 由于缺失的核心算法细节无法从占位符还原，我把你的“参数与算法”插入口全部保留：
    (A) build_features_from_ticks(...)
    (B) score_state(...)
    (C) decide_orders(...)
  你可以把你的真实算法直接粘进这三个函数（或交给你的AI生成并替换）。
- 本脚本默认用 get_market_data_ex(period='tick') 拉取最近N笔tick窗口，避免一次性加载大量数据。
- 若你使用 Level-2 逐笔：请把 DATA_MODE 改成 'l2transaction' 或 'l2order'，并在字段映射 FIELD_MAP 中校正列索引。

-----------------------------------------------------------------
依赖：
- numpy（投研端内置Python通常自带）
- QMT内置函数：timetag_to_datetime / get_trade_detail_data / passorder / ContextInfo.get_market_data_ex
"""

import numpy as np
from collections import deque

# =========================
# 0) 配置（从你原 config.py 抽取并可在此扩展）
# =========================

# --- CAPITAL & RISK (示例默认值；请按你的真实配置/算法修订) ---
INITIAL_CASH = 1_000_000.0

# --- FEATURE WINDOW / AGGREGATION ---
TICK_WINDOW = 4000               # 每次从 end_time 往回取多少笔 tick（按你的机器性能调整）
AGG_WINDOW = 10                  # 你原模型提到 10 点窗口（示例）
BAR_VOL_RATIO = 0.005            # 每bar累计量阈值（示例）

# --- PHYSICS WEIGHTS (来自你原 config.py 的末段) ---
W_POTENTIAL_STRUCT = 80.0
W_POTENTIAL_SRL = 10.0

# --- STRATEGY GATES (来自你原 config.py 的末段) ---
Z_K_CEILING = 1.5
Z_P_FLOOR = 2.0
SCORE_ENTRY_GATE = 0.02

# --- EXECUTION (来自你原 config.py 的末段) ---
SIZE_BASE = 0.10
STOP_LOSS = 0.05
TAKE_PROFIT = 0.095

# --- 数据模式（三选一）---
# 'tick'：普通分笔；'l2transaction'：逐笔成交；'l2order'：逐笔委托
DATA_MODE = 'tick'
# DATA_MODE = 'l2transaction'
# DATA_MODE = 'l2order'

# --- Tick字段映射（不同版本/数据类型列顺序可能不同；用小样本print确认一次后改这里）---
FIELD_MAP = {
    'tick':         {'ts': 0, 'price': 1, 'volume': 2, 'amount': 3},
    'l2transaction':{'ts': 0, 'price': 1, 'volume': 2, 'amount': 3},  # 逐笔成交常见：time/price/volume/amount...
    'l2order':      {'ts': 0, 'price': 1, 'volume': 2},               # 逐笔委托常见：time/price/volume/...
}

def _idx(key: str) -> int:
    return FIELD_MAP[DATA_MODE][key]


# =========================
# 1) 状态结构（替代你原 OmegaState + Kernel 内部状态）
# =========================

class OmegaState(object):
    """
    统一状态载体：你的真实模型可以把更多字段挂在这里。
    """
    __slots__ = ('code', 'ts', 'price', 'z_k', 'z_p', 'kappa', 'srl_defect', 'energy_gap', 'vec_raw')
    def __init__(self, code, ts, price, z_k, z_p, kappa, defect, gap, vec_raw):
        self.code = code
        self.ts = ts
        self.price = price
        self.z_k = z_k
        self.z_p = z_p
        self.kappa = kappa
        self.srl_defect = defect
        self.energy_gap = gap
        self.vec_raw = vec_raw


class OmegaKernel(object):
    """
    你原 kernel.py 的“Lossless Aggregation”思想：这里实现一个可运行的版本：
    - 维护一个滚动特征队列（bar_feats）
    - 当达到阈值时输出聚合向量（mean/std/max concat）
    """
    def __init__(self, agg_window: int = AGG_WINDOW):
        self.agg_window = int(agg_window)
        self.bar_feats = []
        self.bar_vol = 0.0

    def push_tick_features(self, feat_vec: np.ndarray, vol: float) -> np.ndarray:
        """
        输入：单笔tick的特征向量 + 成交量
        输出：若聚合条件满足，则返回聚合向量；否则 None
        """
        if feat_vec is None:
            return None
        self.bar_feats.append(feat_vec.astype(np.float64, copy=False))
        self.bar_vol += float(vol if vol is not None else 0.0)

        # 这里给一个“窗口触发”条件：达到 agg_window 笔 tick 就聚合一次
        if len(self.bar_feats) >= self.agg_window:
            mat = np.vstack(self.bar_feats)
            f_mean = np.mean(mat, axis=0)
            f_std  = np.std(mat, axis=0)
            f_max  = np.max(mat, axis=0)
            final_vec = np.concatenate([f_mean, f_std, f_max])
            # reset
            self.bar_feats = []
            self.bar_vol = 0.0
            return final_vec
        return None


# =========================
# 2) 你的“参数与算法”插入口（交给你的AI填充/替换）
# =========================

def build_features_from_ticks(ticks_arr: np.ndarray) -> np.ndarray:
    """
    输入：ticks_arr = np.ndarray (N, M) 最近N笔 tick/逐笔
    输出：单笔tick的“基础特征向量” 或者 “一组”特征（这里默认取最后一笔生成特征）
    说明：
    - 你原模型的 vec_raw / z_k / z_p / kappa / defect 等在此产生或在后续函数计算。
    - 这里给出一个最小可跑的示例特征：log-return, vol, amount, micro-volatility（极简）
    """
    if ticks_arr is None or not isinstance(ticks_arr, np.ndarray) or ticks_arr.size == 0:
        return None

    ts_i = _idx('ts')
    px_i = _idx('price')
    vol_i = _idx('volume')
    amt_i = FIELD_MAP[DATA_MODE].get('amount', None)

    # 取最后两笔计算收益
    if ticks_arr.shape[0] < 2:
        p0 = float(ticks_arr[-1, px_i])
        ret = 0.0
    else:
        p0 = float(ticks_arr[-2, px_i])
        p1 = float(ticks_arr[-1, px_i])
        ret = np.log(max(p1, 1e-12) / max(p0, 1e-12))

    v1 = float(ticks_arr[-1, vol_i])
    a1 = float(ticks_arr[-1, amt_i]) if (amt_i is not None and amt_i < ticks_arr.shape[1]) else (float(ticks_arr[-1, px_i]) * v1)

    # 简单波动：最近20笔收益std
    n = min(20, ticks_arr.shape[0])
    if n >= 2:
        px = ticks_arr[-n:, px_i].astype(np.float64, copy=False)
        r = np.diff(np.log(np.maximum(px, 1e-12)))
        volat = float(np.std(r))
    else:
        volat = 0.0

    # 你可以把这里替换成你的 Hawkes/TDA/结构熵/缺陷指标等
    feat = np.array([ret, v1, a1, volat], dtype=np.float64)
    return feat


def score_state(code: str, ts: int, price: float, agg_vec: np.ndarray) -> OmegaState:
    """
    输入：聚合特征向量 agg_vec
    输出：OmegaState（含 z_k/z_p/kappa/defect 等）
    说明：
    - 这里给出一个“占位实现”，确保策略可运行；
    - 你的真实 z_k / z_p / kappa / defect / energy_gap 计算应在此替换。
    """
    if agg_vec is None:
        return None

    # 占位：把前几维映射为“动力/势能”指标
    # 你应替换为你的 Dual Manifold 定义
    z_k = float(np.clip(abs(agg_vec[0]) * 100, 0, 10))          # 动量强度（示例）
    z_p = float(np.clip(agg_vec[-1] * 10 + 2.0, -5, 10))        # “内压”（示例）

    # 占位：结构熵 / 缺陷
    kappa = float(np.clip(np.std(agg_vec) * 100, 0, 100))
    defect = float(np.clip(np.mean(np.abs(agg_vec)) * 10, 0, 100))

    gap = z_p - z_k
    return OmegaState(code=code, ts=ts, price=price, z_k=z_k, z_p=z_p, kappa=kappa, defect=defect, gap=gap, vec_raw=agg_vec)


def decide_orders(state: OmegaState, account_cash: float, position_shares: int) -> dict:
    """
    输入：
      - state：OmegaState
      - account_cash：可用资金
      - position_shares：当前持仓股数
    输出：
      - None 或 {"side": "BUY"/"SELL", "shares": int}
    说明：
      - 这里实现一个“最小可跑”的门控逻辑，体现你 config.py 的 gate；
      - 你应把你的真实“入场/出场/止损/止盈/仓位控制”替换在此处。
    """
    if state is None:
        return None

    # --- 入场门控（来自你原配置思想）---
    if position_shares == 0:
        if (state.z_k <= Z_K_CEILING) and (state.z_p >= Z_P_FLOOR):
            # 用能隙+结构作为“分数”
            score = (W_POTENTIAL_STRUCT * state.kappa + W_POTENTIAL_SRL * state.srl_defect) / 100000.0
            if score >= SCORE_ENTRY_GATE and account_cash > 1000:
                # 简单按现金比例买入（A股按100股一手）
                notional = account_cash * SIZE_BASE
                shares = int(notional / max(state.price, 1e-12) / 100) * 100
                if shares >= 100:
                    return {"side": "BUY", "shares": shares}

    # --- 出场规则（示例：止损/止盈占位）---
    # 你真实策略应基于成本价/结构失效等信号
    # 这里仅演示：当势能显著下降则卖出
    if position_shares > 0:
        if state.energy_gap < -0.5:
            return {"side": "SELL", "shares": position_shares}

    return None


# =========================
# 3) QMT 策略生命周期函数
# =========================

# 建议：用全局变量保存状态（知识库建议不要把复杂状态挂在 ContextInfo 上）
G = {
    "kernel": None,
    "last_tick_ts": {},   # code -> last processed ts
}

def init(C):
    """
    初始化：只执行一次
    """
    # 初始化聚合器
    G["kernel"] = OmegaKernel(agg_window=AGG_WINDOW)
    G["last_tick_ts"] = {}

    # 交易标的：主图品种（你也可以在此改为自建池）
    C.stock = C.stockcode + "." + C.market
    C.period = "tick"  # 回测界面也需选 tick；若你要逐笔成交/委托，需在回测界面选对应周期（若支持）
    C.accountid = "test"  # 回测账户一般用'test'

    # 可选：打印提示
    print("[OMEGA] init ok. stock=", C.stock, "mode=", DATA_MODE)


def after_init(C):
    """
    初始化后：可用于立即下单/订阅等
    """
    pass


def handlebar(C):
    """
    行情驱动：回测时按tick/逐笔触发，实盘时也可能按tick触发
    关键实现：
      - 取 end_time = 当前bar时间
      - 拉取最近 TICK_WINDOW 笔 tick
      - 仅处理“新tick”（避免重复计算）
      - 生成特征 -> 聚合 -> state -> 决策 -> passorder
    """
    code = C.stock

    # 1) 当前bar时间（timetag）
    # barpos 是当前K线位置；tick模式下barpos也会推进
    bar_ts = C.get_bar_timetag(C.barpos)
    end_time = timetag_to_datetime(bar_ts, "%Y%m%d%H%M%S")

    # 2) 拉取最近窗口 tick（回测时 subscribe=False 更快；实盘可用 subscribe=True）
    ticks = C.get_market_data_ex(
        fields=[], stock_code=[code],
        period=DATA_MODE,
        end_time=end_time,
        count=TICK_WINDOW,
        subscribe=False
    )

    if ticks is None or code not in ticks:
        return

    arr = ticks[code]
    if not isinstance(arr, np.ndarray) or arr.size == 0:
        return

    # 3) 去重：只处理最后一笔（或你可在此处理增量区间）
    ts_i = _idx('ts')
    px_i = _idx('price')
    vol_i = _idx('volume')

    last_ts = int(arr[-1, ts_i])
    if G["last_tick_ts"].get(code) == last_ts:
        return
    G["last_tick_ts"][code] = last_ts

    last_price = float(arr[-1, px_i])
    last_vol = float(arr[-1, vol_i])

    # 4) 生成单笔特征（你可替换为“增量多笔处理”）
    feat = build_features_from_ticks(arr)

    # 5) 聚合（lossless aggregation）
    agg_vec = G["kernel"].push_tick_features(feat, last_vol)
    if agg_vec is None:
        return

    # 6) 评分/状态
    state = score_state(code, last_ts, last_price, agg_vec)
    if state is None:
        return

    # 7) 查询账户/持仓（回测/实盘通用）
    acc = get_trade_detail_data(C.accountid, "stock", "account")
    pos = get_trade_detail_data(C.accountid, "stock", "position")

    cash = float(acc[0].m_dAvailable) if acc else 0.0
    shares = 0
    if pos:
        for p in pos:
            if p.m_strInstrumentID == code:
                shares = int(p.m_nVolume)
                break

    # 8) 决策
    od = decide_orders(state, cash, shares)
    if not od:
        return

    # 9) 下单（passorder 参数因版本而异；此处采用“最常见”的内置函数签名）
    # 你可让你的AI根据你终端的 passorder 签名微调参数
    side = od["side"]
    vol = int(od["shares"])

    if side == "BUY":
        # 市价/对手价策略：此处用限价=当前价（示例），你可替换为更真实的盘口/滑点模型
        passorder(23, 1101, C.accountid, code, 0, last_price, vol, "OMEGA_BUY", 1)
        print(f"[OMEGA] BUY {code} px={last_price} vol={vol} ts={last_ts}")
    else:
        passorder(24, 1101, C.accountid, code, 0, last_price, vol, "OMEGA_SELL", 1)
        print(f"[OMEGA] SELL {code} px={last_price} vol={vol} ts={last_ts}")


def stop(C):
    """
    停止前：不要在这里下单/撤单（交易连接已断开）
    """
    print("[OMEGA] stop. done.")
