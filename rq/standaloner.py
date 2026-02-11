# Filename: rq/standaloner.py
# ROLE: The One-Click Verification Tool

import sys
import os
import argparse

# Import local interface
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rq.interface import OmegaRQ

def main():
    parser = argparse.ArgumentParser(description="OMEGA RQ Standalone Runner")
    parser.add_argument("code", help="Stock Code (e.g., 000032.XSHE)")
    parser.add_argument("--start", default="2025-01-01", help="Start Date")
    parser.add_argument("--end", default="2025-01-10", help="End Date")
    
    args = parser.parse_args()
    
    print(f">>> OMEGA v24 MAXWELL STANDALONE: {args.code} <<<")
    OmegaRQ.init()
    
    # Run default strategy
    res = OmegaRQ.alpha.run_backtest(
        start_date=args.start,
        end_date=args.end,
        codes=[args.code] # Need to handle subscription in init
    )
    
    # We need to ensure the default strategy subscribes to args.code
    # The default strategy in rq/alpha/runner.py -> strategy.py subscribes to a fixed list?
    # We should probably modify strategy.py to read from context.config or similar.
    # For now, let's assume strategy.py has a hardcoded list or we modify it dynamically.
    # Actually, let's inject a wrapper here.
    
    def init(context):
        from rq.alpha.strategy import init as base_init
        base_init(context)
        # Override subscription
        from rqalpha.api import subscribe
        subscribe(args.code)
        
    def handle_tick(context, tick):
        from rq.alpha.strategy import handle_tick as base_tick
        base_tick(context, tick)
        
    res = OmegaRQ.alpha.run_backtest(init, handle_tick, args.start, args.end)
    
    if res and 'sys_analyser' in res:
        s = res['sys_analyser']['summary']
        print("\n=== REPORT ===")
        print(f"Return: {s['total_returns']:.2%}")
        print(f"Sharpe: {s['sharpe']:.2f}")
        print(f"Trades: {s['total_trade_count']}")
    else:
        print("No trades or error.")

if __name__ == "__main__":
    main()
