---
name: qmtsdk
description: 使用 QMT/xtquant 数据服务的工作流与代码范式。需要下载/读取日线、分钟、tick、L2逐笔数据或排查 QMT 连接问题时调用。
---

# QMTSDK Skill

## 前置条件
- QMT 投研端/MiniQMT 必须已启动并已登录，否则会出现“无法连接xtquant服务”
- 外部 Python 运行时需要能导入 `xtquant`（通常使用 QMT 自带 Python，或设置 PYTHONPATH 指向其 site-packages）
- L2（`l2transaction`/`l2order`）需要账号具备相应权限

参考：[qmt_external_python_setup.md](docs/qmt_external_python_setup.md)

## 数据下载与同步（已并入 data_download）

推荐日常同步脚本：

```bash
python tools/omega_qmt_daily_sync.py --start YYYYMMDD --end YYYYMMDD
```

连接/权限排错脚本：
- `python tools/check_qmt_status.py`
- `python tools/diag_qmt_download.py`
- `python tools/test_qmt_datac.py`

说明：
- 以上脚本用于 QMT 环境自检与同步，不应直接替代主干训练/审计流程。
- 下载结果应统一落在项目相对路径（`./data/*`）并纳入审计记录。

## 推荐入口（类似 rqdatac）
项目内提供了轻量封装：`qmt.QmtDataClient` 与 `qmt.api` 单例。

```python
from qmt import api

api.init(port=58610, enable_hello=False, auto_connect=True)
print("data_dir:", api.data.data_dir)
```

## 常用数据接口映射

### 1) 获取股票池
```python
from qmt import api

api.init()
stocks = api.data.get_stock_list_in_sector("沪深A股")
```

### 2) 预下载到本地（MiniQMT 数据目录）
单标的：
```python
from qmt import api

api.init()
api.data.download_history_data("000001.SZ", period="1d", start_time="20240101", end_time="20250101", incrementally=True)
```

批量（适合 tick/L2，支持进度回调）：
```python
from qmt import api

api.init()

def on_progress(info: dict):
    print(info)

api.data.download_history_data2(
    stock_list=["000001.SZ", "600000.SH"],
    period="l2transaction",
    start_time="20250101",
    end_time="20250131",
    callback=on_progress,
)
```

### 3) 读取历史行情（DataFrame）
日线/分钟（推荐走 `get_price`/`get_market_data_ex`）：
```python
from qmt import api

api.init()
df = api.data.get_price("000001.SZ", start_date="20250101", end_date="20250131", frequency="1d")
print(df.head())
```

多标的：
```python
from qmt import api

api.init()
data = api.data.get_price(["000001.SZ", "600000.SH"], start_date="20250101", end_date="20250131", frequency="1d")
print(data.keys())
print(data["000001.SZ"].head())
```

### 4) 读取 tick / L2逐笔
```python
from qmt import api

api.init()
ticks = api.data.get_ticks("000001.SZ", start_dt="20250102", end_dt="20250103", kind="tick")
trades = api.data.get_ticks("000001.SZ", start_dt="20250102", end_dt="20250103", kind="l2transaction")
orders = api.data.get_ticks("000001.SZ", start_dt="20250102", end_dt="20250103", kind="l2order")
```

### 5) 快照（全市场）
```python
from qmt import api

api.init()
snap = api.data.get_full_tick(["000001.SZ", "600000.SH"])
```

### 6) 订阅实时回调
```python
from qmt import api

api.init()

def on_tick(data):
    print(data)

api.data.subscribe_quote("000001.SZ", period="tick", callback=on_tick)
```

## 排错清单（高频）
- 导入失败：检查解释器是否为 QMT 自带 Python，或是否已配置 PYTHONPATH
- 连接失败：检查 QMT 是否已登录、MiniQMT 是否已启动、端口是否正确（常见 58610/58613）
- L2 为空：检查账号权限；先用 1-2 只股票 + 1 个交易日验证
- 需要自检脚本：运行 [test_qmt_datac.py](tools/test_qmt_datac.py)
