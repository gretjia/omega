================================================================================
OMEGA RQSDK 独立开发体系使用手册
版本：v24.00 (Maxwell Adapter)
日期：2026-01-30
================================================================================

1. 项目概述 (Overview)
--------------------------------------------------------------------------------
本项目 (`./rq`) 是 OMEGA 量化系统的独立底层设施，旨在封装 Ricequant SDK (RQSDK) 的核心组件
(RQData, RQAlpha, RQFactor, RQOptimizer)，并提供适配 OMEGA v24.00 "Maxwell" 物理引擎
的专属接口。

核心设计哲学：
- 独立性：作为独立 Package 运行，不依赖 OMEGA 业务逻辑。
- 接口化：通过 `interface.py` 提供统一原语。
- 物理适配：原生支持 v24 的 "Frozen Statistics" (绝对标尺) 和 "Shift-Add Conv" (矢量卷积)。

2. 目录结构与文件说明 (Directory Structure)
--------------------------------------------------------------------------------
d:\OMEGA\rq\
│
├── config.yaml                 [核心配置] 定义运行模式(仿真/实盘)、数据路径、物理常数
├── interface.py                [统一接口] 外部调用的唯一入口 (import rq.interface as OmegaRQ)
├── README.txt                  [本文档]   详细使用说明
│
├── data\                       [数据层 - RQData]
│   ├── adapter.py              核心适配器，负责：
│   │                           1. 自动切换本地 H5/CSV (simulation) 与远程 API (production)
│   │                           2. 提供 get_maxwell_tensor() 生成 v24 标准化张量
│   ├── frozen_stats.py         管理 v24 的全局均值/标准差 (Absolute Ruler)
│   ├── frozen_stats.json       存储训练好的全局统计量 (需手动更新)
│   └── bundle\                 本地数据仓 (包含 H5 Ticks, CSVs 等)
│
├── factor\                     [因子层 - RQFactor]
│   └── maxwell_operators.py    定义 v24 物理算子：
│                               1. shift_add_conv1d (NumPy 极速卷积)
│                               2. kinetic_energy (动能)
│                               3. structural_entropy (结构熵)
│
├── alpha\                      [策略层 - RQAlpha]
│   └── runner.py               封装 rqalpha.run_func，提供简化的回测启动接口
│
└── optimizer\                  [优化层 - RQOptimizer]
    └── __init__.py             (预留) 组合优化与资金分配接口

3. 使用逻辑与流程 (Usage Workflow)
--------------------------------------------------------------------------------

[场景 A：获取训练数据]
目标：获取某只股票过去 120 个 Tick 的标准化张量，用于神经网络训练。
逻辑：
1. 调用 `OmegaRQ.init()` 加载配置。
2. 调用 `OmegaRQ.data.get_maxwell_tensor(code)`。
3. Adapter 会自动：
   - 读取本地 H5/CSV (节省流量)。
   - 计算 LogReturn, LogVolume 等原始特征。
   - 读取 `frozen_stats.json` 进行 Z-Score 归一化。
   - 返回 [120, 5] 的 NumPy 数组。

[场景 B：运行策略回测]
目标：测试一个基于 v24 信号的策略。
逻辑：
1. 定义策略的 `init(context)` 和 `handle_tick(context, tick)` 函数。
2. 调用 `OmegaRQ.alpha.run_backtest(...)`。
3. Runner 会自动：
   - 配置 RQAlpha 环境。
   - 挂载本地 Bundle 数据。
   - 启动回测并返回结果对象。

[场景 C：计算物理因子]
目标：手动验证卷积算子的正确性。
逻辑：
1. 获取 Tensor 数据。
2. 调用 `OmegaRQ.factor.shift_add_conv1d(tensor, weights, ...)`。
3. 得到卷积输出，无需启动 PyTorch。

4. 版本说明 (Version Notes)
--------------------------------------------------------------------------------
当前版本：v24.00 (Maxwell Adapter)

特性支持：
- [x] Maxwell 物理引擎适配 (Shift-Add Conv, Kinetic Energy)
- [x] Frozen Statistics (绝对标尺归一化)
- [x] 本地数据优先 (Simulation Mode)
- [x] 流量配额保护 (Quota Management)

待办事项 (TODO)：
- [ ] 集成 RQOptimizer 进行组合权重优化
- [ ] 完善 frozen_stats.json 的自动训练更新脚本

5. 快速上手代码 (Quick Start)
--------------------------------------------------------------------------------
import sys
sys.path.append("d:/OMEGA")  # 确保根目录在路径中
import rq.interface as OmegaRQ

# 1. 初始化
OmegaRQ.init()

# 2. 获取数据 (v24 Tensor)
# 自动处理 H5 读取和 Frozen Stats 归一化
tensor = OmegaRQ.data.get_maxwell_tensor("000032.XSHE", lookback=120)
print(f"Tensor Shape: {tensor.shape}")

# 3. 运行简单回测
def init(context):
    context.s1 = "000032.XSHE"
    subscribe(context.s1)

def handle_tick(context, tick):
    print(f"Tick: {tick.order_book_id} {tick.last}")

OmegaRQ.alpha.run_backtest(init, handle_tick, "2025-01-01", "2025-01-05")

================================================================================
