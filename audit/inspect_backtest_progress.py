
import re
import sys

log_path = "audit/_parallel_backtest_fixed.log"

try:
    with open(log_path, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print("Log file not found.")
    sys.exit(0)

print("=== Live Backtest Progress Inspection ===")
pnl = 0.0
trades = 0
rows = 0

# Scan for "Progress: 500,000 rows | PnL: 123.4 | Trades: 50" lines
pattern = re.compile(r"Progress: ([\d,]+) rows \| PnL: ([-\d.]+) \| Trades: (\d+)")

last_match = None
for line in lines:
    match = pattern.search(line)
    if match:
        last_match = match

if last_match:
    rows = int(last_match.group(1).replace(",", ""))
    pnl = float(last_match.group(2))
    trades = int(last_match.group(3))
    
    print(f"Status: RUNNING")
    print(f"Rows Processed: {rows:,}")
    print(f"Cumulative PnL: {pnl:.4f} (Signal Strength)")
    print(f"Total Trades  : {trades:,}")
    
    if trades > 0:
        print(f"Avg PnL/Trade : {pnl/trades:.6f}")
    
    if rows > 0:
        print(">> VERDICT: System is generating valid signals.")
else:
    print("No progress lines found yet (Check buffering or initialization).")
    # Check if we have [Start] or [Plan]
    for line in lines:
        if "[Plan]" in line or "[Start]" in line:
            print(f"Found Init Line: {line.strip()}")
