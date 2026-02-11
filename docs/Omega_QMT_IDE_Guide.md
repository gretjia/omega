OMEGA v13.00: VS Code + XtQuant Backtest Development Guide
Overview
This guide enables you to develop and debug QMT backtests in VS Code instead of copy-pasting into the QMT terminal. The key is using the xtquant library which connects to a running MiniQMT instance.

Architecture
┌─────────────────┐    TCP/IPC    ┌──────────────────┐
│   VS Code       │◄────────────► │   MiniQMT        │
│   (Your Code)   │               │   (Data Server)  │
│   xtquant lib   │               │   Running in BG  │
└─────────────────┘               └──────────────────┘
Key Insight: xtquant connects to MiniQMT which handles data requests. The data and behavior are identical to the built-in Python - you're just running externally.

Setup Requirements
1. MiniQMT Must Be Running
Launch the QMT terminal (迅投极速交易终端)
It runs a data service on a local port (default: auto-detected)
Keep it running while you develop
2. Python Environment
# Create conda environment
conda create -n omega python=3.9
conda activate omega
pip install numpy pandas xgboost
# xtquant is bundled with QMT - add to path
# Located at: D:\迅投极速交易终端睿智融科版\bin.x64\Lib\site-packages\
3. Add xtquant to Python Path
import sys
sys.path.append(r"D:\迅投极速交易终端睿智融科版\bin.x64\Lib\site-packages")
from xtquant import xtdata
Core APIs
xtdata - Market Data Module
Connection
from xtquant import xtdata
# Auto-connect to running MiniQMT (usually works automatically)
# Or specify port explicitly:
xtdata.reconnect(port=58613)
Download Historical Data
# Download tick data for stocks
xtdata.download_history_data2(
    stock_list=["000032.SZ", "600118.SH"],
    period="tick",              # "1d", "1m", "5m", "tick", "l2transaction"
    start_time="20240101",
    end_time="20250120",
    callback=lambda info: print(f"Progress: {info}")
)
Get Market Data
# Get historical K-line data
data = xtdata.get_market_data_ex(
    field_list=['open', 'high', 'low', 'close', 'volume'],
    stock_list=["000032.SZ"],
    period="1d",
    start_time="20240101",
    end_time="20250120"
)
# Returns: dict[stock_code] -> DataFrame
# Get tick data
tick_data = xtdata.get_market_data_ex(
    field_list=[],  # Empty = all fields
    stock_list=["000032.SZ"],
    period="tick",
    start_time="20250120093000",
    end_time="20250120150000"
)
Subscribe Real-time Data
def on_data(datas):
    for code, records in datas.items():
        print(f"{code}: {records[-1]}")
# Subscribe to tick updates
seq = xtdata.subscribe_quote("000032.SZ", period="tick", callback=on_data)
# Keep running to receive callbacks
import time
while True:
    time.sleep(1)
Key Period Types
Period	Description
1d	Daily bars
1m, 5m, 15m, 30m, 60m	Minute bars
tick
Level 1 tick data
l2transaction	Level 2 transaction-by-transaction
l2order	Level 2 order-by-order
Custom Backtester Pattern
Since QMT's built-in backtest engine doesn't work well externally, you need to build your own:

"""
VS Code Custom Backtester for OMEGA v13.00
"""
import sys
sys.path.append(r"D:\迅投极速交易终端睿智融科版\bin.x64\Lib\site-packages")
from xtquant import xtdata
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
# ============================================================
# 1. CONFIGURATION
# ============================================================
STOCK_POOL = ["000032.SZ", "600118.SH"]  # Your 156 stocks
INITIAL_CAPITAL = 10_000_000.0
START_DATE = "20240101"
END_DATE = "20250120"
COMMISSION_RATE = 0.0003
STAMP_DUTY = 0.001  # Sell only
# ============================================================
# 2. DATA LOADING
# ============================================================
def load_tick_data(stocks, start, end):
    """Load tick data from MiniQMT"""
    print("Downloading data...")
    xtdata.download_history_data2(
        stock_list=stocks,
        period="tick",
        start_time=start,
        end_time=end
    )
    
    print("Loading data...")
    data = {}
    for stock in stocks:
        df = xtdata.get_market_data_ex(
            field_list=['time', 'lastPrice', 'volume', 'amount'],
            stock_list=[stock],
            period="tick",
            start_time=start,
            end_time=end
        )
        if stock in df and len(df[stock]) > 0:
            data[stock] = df[stock]
    return data
# ============================================================
# 3. ACCOUNT SIMULATION
# ============================================================
class SimAccount:
    def __init__(self, capital):
        self.cash = capital
        self.positions = {}  # stock -> shares
        self.avg_cost = {}   # stock -> cost
        self.trades = []
        self.equity_curve = []
    
    def buy(self, stock, price, shares, ts):
        cost = shares * price * (1 + COMMISSION_RATE)
        if cost > self.cash:
            shares = int(self.cash / price / (1 + COMMISSION_RATE) / 100) * 100
            cost = shares * price * (1 + COMMISSION_RATE)
        if shares < 100:
            return False
        
        self.cash -= cost
        prev = self.positions.get(stock, 0)
        prev_cost = self.avg_cost.get(stock, 0)
        new_shares = prev + shares
        self.avg_cost[stock] = (prev_cost * prev + price * shares) / new_shares
        self.positions[stock] = new_shares
        self.trades.append((ts, stock, "BUY", price, shares))
        return True
    
    def sell(self, stock, price, shares, ts):
        held = self.positions.get(stock, 0)
        if held <= 0:
            return False
        shares = min(shares, held)
        proceeds = shares * price * (1 - COMMISSION_RATE - STAMP_DUTY)
        self.cash += proceeds
        self.positions[stock] -= shares
        if self.positions[stock] == 0:
            del self.positions[stock]
            del self.avg_cost[stock]
        self.trades.append((ts, stock, "SELL", price, shares))
        return True
    
    def mark_to_market(self, prices, ts):
        equity = self.cash
        for stock, shares in self.positions.items():
            if stock in prices:
                equity += shares * prices[stock]
        self.equity_curve.append((ts, equity))
        return equity
# ============================================================
# 4. YOUR STRATEGY (OMEGA v13.00 Kernel)
# ============================================================
from collections import deque
class OmegaKernel:
    """Your v13.00 Dual Manifold physics kernel"""
    def __init__(self):
        self.prev_price = 0
        self.vec_k = np.zeros(2)
        self.vec_p = np.zeros(4)
        # ... (copy your full kernel here)
    
    def update(self, price, vol, ts):
        # Your physics calculations
        # Return (z_k, z_p, signal)
        pass
# ============================================================
# 5. BACKTEST LOOP
# ============================================================
def run_backtest():
    # Load data
    data = load_tick_data(STOCK_POOL, START_DATE, END_DATE)
    
    # Initialize
    account = SimAccount(INITIAL_CAPITAL)
    kernels = {s: OmegaKernel() for s in STOCK_POOL}
    
    # Merge all ticks by timestamp
    all_ticks = []
    for stock, df in data.items():
        for _, row in df.iterrows():
            all_ticks.append((row['time'], stock, row['lastPrice'], row['volume']))
    all_ticks.sort(key=lambda x: x[0])
    
    print(f"Processing {len(all_ticks)} ticks...")
    
    # Event loop
    for ts, stock, price, vol in all_ticks:
        kernel = kernels[stock]
        signal = kernel.update(price, vol, ts)
        
        # Trading logic
        if signal == "BUY":
            account.buy(stock, price, 1000, ts)
        elif signal == "SELL":
            pos = account.positions.get(stock, 0)
            if pos > 0:
                account.sell(stock, price, pos, ts)
        
        # Record equity periodically
        if len(all_ticks) % 10000 == 0:
            prices = {s: data[s]['lastPrice'].iloc[-1] for s in data}
            account.mark_to_market(prices, ts)
    
    # Final results
    print(f"\n=== BACKTEST RESULTS ===")
    print(f"Total trades: {len(account.trades)}")
    print(f"Final cash: {account.cash:,.2f}")
    print(f"Positions: {account.positions}")
    
    return account
if __name__ == "__main__":
    run_backtest()
Debugging Tips
1. Check MiniQMT Connection
from xtquant import xtdata
import time
# Test connection
try:
    stocks = xtdata.get_stock_list_in_sector("沪深A股")
    print(f"Connected! Found {len(stocks)} stocks")
except Exception as e:
    print(f"Connection failed: {e}")
    print("Make sure QMT terminal is running!")
2. VS Code Launch Configuration
Create .vscode/launch.json:

{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "OMEGA Backtest",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run_l2_audit.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder};D:\\迅投极速交易终端睿智融科版\\bin.x64\\Lib\\site-packages"
            }
        }
    ]
}
3. Common Issues
Issue	Solution
ModuleNotFoundError: xtquant	Add QMT site-packages to PYTHONPATH
Connection refused	Start QMT terminal first
No data returned	Download data first with download_history_data2
NumPy version mismatch	Use isolated conda env, not QMT's Python
Next Steps
Use `run_l2_audit.py` as the VS Code-ready v3 entry point for deterministic L2 audit
This will use your OMEGA v13.00 kernel with the custom SimAccount
You can set breakpoints, debug, and iterate quickly
Want me to proceed with creating the VS Code backtest script?
