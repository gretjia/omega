# Filename: omega_v1506_target_sync.py
# Purpose: Targeted Tick Extraction with Multi-Day Buffer (v15.06)
# Strategy: Scan Daily -> Identify ALL Setups -> Download [T-1, T] Ticks -> Ensure 3000+ Ticks

import os
import pandas as pd
import numpy as np
import glob
from datetime import datetime, timedelta
import time

# --- CONFIG ---
DAILY_DIR = r"d:\OMEGA\data\daily_bars"
TICK_DIR = r"D:\OMEGA\data\history_ticks_full"
QMT_PORT = 58610

def require_xtquant():
    try:
        from xtquant import xtdata
        xtdata.enable_hello = False
        return xtdata
    except: return None

def get_full_code(code: str) -> str:
    if '.' in code: return code
    if code.startswith('6'): return f"{code}.SH"
    return f"{code}.SZ"

def parse_ms_to_date(ms):
    return datetime.fromtimestamp(ms/1000).strftime("%Y%m%d")

def main():
    if not os.path.exists(TICK_DIR): os.makedirs(TICK_DIR)
    
    xtdata = require_xtquant()
    if not xtdata: return
    
    print(f"🔌 Connecting to QMT...")
    try: xtdata.connect(port=QMT_PORT)
    except: return

    files = glob.glob(os.path.join(DAILY_DIR, "*.csv"))
    print(f"🔍 Scanning {len(files)} daily bar files for ALL v15.06 setups...")
    
    targets = [] # List of (full_code, target_date_str, prev_date_str)
    
    for f in files:
        try:
            code = os.path.basename(f).split('.')[0]
            df = pd.read_csv(f)
            if len(df) < 15: continue
            
            # v15.06 Indicators: Future 10D > 20% | Past 5D < 5%
            closes = df['close'].values
            times = df['datetime'].values 
            
            for i in range(5, len(closes) - 10):
                past_ret = abs(closes[i]/closes[i-5] - 1.0)
                fut_ret = closes[i+10]/closes[i] - 1.0
                
                if fut_ret > 0.20 and past_ret < 0.05:
                    target_date = parse_ms_to_date(times[i])
                    # Get previous trading day from the local daily data
                    prev_date = parse_ms_to_date(times[i-1])
                    targets.append((get_full_code(code), target_date, prev_date))
                    # Removed 'break' to capture Multiple Setups per stock
        except: continue

    print(f"🎯 Identified {len(targets)} Golden Targets. Starting Targeted Tick Sync (with T-1 Buffer)...")
    
    success = 0
    for i, (full_code, date_str, prev_date_str) in enumerate(targets):
        short_code = full_code.split('.')[0]
        # Filename includes date to support multi-setup per stock
        csv_path = os.path.join(TICK_DIR, f"{short_code}_{date_str}.csv")
        
        # Skip if already downloaded
        if os.path.exists(csv_path):
            success += 1
            continue

        print(f"[{i+1}/{len(targets)}] {full_code} @ {date_str} (Buffering {prev_date_str}) ... ", end="", flush=True)
        
        try:
            # Download T-1 and T to guarantee 3000 ticks
            xtdata.download_history_data(full_code, period='tick', start_time=prev_date_str, end_time=date_str)
            data = xtdata.get_market_data_ex(stock_list=[full_code], period='tick', start_time=prev_date_str, end_time=date_str)
            
            if full_code in data and not data[full_code].empty:
                df_tick = data[full_code].reset_index(drop=True)
                
                # Extract ask1/bid1 scalar
                if 'askPrice' in df_tick.columns:
                    df_tick['ask1'] = df_tick['askPrice'].apply(lambda x: x[0] if isinstance(x, (list, np.ndarray)) and len(x) > 0 else x)
                if 'bidPrice' in df_tick.columns:
                    df_tick['bid1'] = df_tick['bid1'] = df_tick['bidPrice'].apply(lambda x: x[0] if isinstance(x, (list, np.ndarray)) and len(x) > 0 else x)
                
                df_tick = df_tick.rename(columns={'lastPrice': 'price', 'volume': 'vol'})
                cols = [c for c in ['time', 'price', 'vol', 'ask1', 'bid1'] if c in df_tick.columns]
                
                # Final Check: Do we have enough ticks?
                if len(df_tick) < 3000:
                    print(f"⚠ Low density ({len(df_tick)} ticks)")
                else:
                    print(f"✓ {len(df_tick)} ticks")
                
                df_tick[cols].to_csv(csv_path, index=False)
                success += 1
            else:
                print("⚠ No ticks")
        except Exception as e:
            print(f"❌ {e}")
            
        if i % 5 == 0: time.sleep(0.05)

    print(f"\n✨ Targeted Sync Complete. Harvested {success} multi-setup Golden Tick files.")

if __name__ == "__main__":
    main()
