# Filename: omega_qmt_daily_sync.py
# Purpose: Fast Full-Market Daily Bar Synchronizer (QMT/XtQuant)
# Target: d:\OMEGA\data\daily_bars

import os
import time
import argparse
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
DEFAULT_DAILY_DIR = r"d:\OMEGA\data\daily_bars"
QMT_PORT = 58610
SECTOR_NAME = "沪深A股"

def get_full_code(code: str) -> str:
    if '.' in code: return code
    # Basic suffix logic for A-share
    if code.startswith('6'): return f"{code}.SH"
    if code.startswith('0') or code.startswith('3'): return f"{code}.SZ"
    if code.startswith('4') or code.startswith('8'): return f"{code}.BJ"
    return f"{code}.SZ"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="20100101", help="YYYYMMDD")
    parser.add_argument("--end", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()
    
    if not os.path.exists(DEFAULT_DAILY_DIR):
        os.makedirs(DEFAULT_DAILY_DIR)
        
    try:
        from xtquant import xtdata
        xtdata.enable_hello = False
    except ImportError:
        print("❌ xtquant not found. Run on QMT machine.")
        return

    print(f"🔌 Connecting to QMT (Port {QMT_PORT})...")
    try:
        xtdata.connect(port=QMT_PORT)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    print(f"📋 Fetching universe: {SECTOR_NAME}...")
    codes = xtdata.get_stock_list_in_sector(SECTOR_NAME)
    print(f"✅ Found {len(codes)} stocks.")

    success = 0
    failed = 0
    
    # Using download_history_data for 1d bars is EXTREMELY fast
    for i, code in enumerate(sorted(codes)):
        short_code = code.split('.')[0]
        csv_path = os.path.join(DEFAULT_DAILY_DIR, f"{short_code}.csv")
        
        print(f"[{i+1}/{len(codes)}] {code} ... ", end="", flush=True)
        try:
            # Download
            xtdata.download_history_data(code, period='1d', start_time=args.start, end_time=args.end, incrementally=True)
            # Retrieve
            data = xtdata.get_market_data_ex(stock_list=[code], period='1d', start_time=args.start, end_time=args.end)
            if code in data and not data[code].empty:
                df = data[code].reset_index(drop=True)
                # Standard OMEGA Mapping
                df = df.rename(columns={'time': 'datetime'}) # Daily bars usually use 'time' as YYYYMMDD in some APIs, 
                                                            # but in xtquant get_market_data_ex it is often ms timestamp.
                                                            # We'll normalize to readable YYYYMMDD if possible or keep as is.
                df.to_csv(csv_path, index=False)
                print(f"✓ {len(df)} bars")
                success += 1
            else:
                print("⚠ No data")
                failed += 1
        except Exception as e:
            print(f"❌ {e}")
            failed += 1
        
        # Throttling to keep terminal responsive
        if i % 50 == 0: time.sleep(0.1)

    print(f"\n✨ Daily Sync Complete. Suceeded: {success} | Failed: {failed}")
    print(f"📁 Data in: {DEFAULT_DAILY_DIR}")

if __name__ == "__main__":
    main()
