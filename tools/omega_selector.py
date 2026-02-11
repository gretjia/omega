# filename: tools/omega_selector.py
# -----------------------------------------------------
# OMEGA v10: ELITE STOCK SELECTOR (For XTQuant)
# -----------------------------------------------------
# Run this script INSIDE XTQuant (Windows) to generate 
# the 'omega_training_list.csv' file in the project root.
# -----------------------------------------------------

from xtquant import xtdata
import pandas as pd
import os

def get_omega_universe():
    print(">>> OMEGA SCOUT v10: Scanning for Alpha Manifolds...")
    
    # 1. Get Universe (All A-Shares)
    try:
        all_stocks = xtdata.get_stock_list_in_sector('沪深A股')
        print(f"Total Universe: {len(all_stocks)} stocks")
    except Exception as e:
        print(f"Error fetching stock list: {e}")
        return

    # 2. Snapshot Data (Fastest way to obtain Current Price & Volume)
    # Note: Ensure XTQuant has downloaded full tick data or is connected to live feed
    snapshots = xtdata.get_full_tick(all_stocks)
    
    candidates = []
    for code, data in snapshots.items():
        try:
            # Filter Safety (Penny stocks & ST)
            if data['lastPrice'] < 5: continue 
            if 'ST' in data.get('stock_name', ''): continue
            
            # Volatility Proxy: (High - Low) / Last
            # We want High Energy Potential, not dead stocks
            if data['lastPrice'] > 0:
                vol_score = (data['high'] - data['low']) / data['lastPrice']
            else:
                vol_score = 0
            
            candidates.append({
                'code': code,
                'amount': data['amount'], # Turnover Amount (Liquidity)
                'vol': vol_score
            })
        except:
            continue
        
    df = pd.DataFrame(candidates)
    
    if df.empty:
        print("CRITICAL: No snapshot data found. Is XTQuant connected?")
        return

    # 3. Filter for Institutional Liquidity (Top 500)
    # We only want Main Players, not random retail noise
    df_liquid = df.sort_values('amount', ascending=False).head(500)
    
    # 4. Filter for Alpha Energy (Top 88)
    # From the liquid ones, pick the most "Elastic/Volatile" ones
    df_elite = df_liquid.sort_values('vol', ascending=False).head(88)
    
    print(f"Selection Complete. Elite Vanguard: {len(df_elite)} stocks.")
    
    # 5. Save List to Root (Relative to where this script is run)
    # Assuming script is in tools/, saving to ../omega_training_list.csv
    # But QMT often runs in its own path. We will print the path.
    
    # Try to save in current working directory
    out_file = 'omega_training_list.csv'
    df_elite['code'].to_csv(out_file, index=False, header=False)
    
    print(f"SAVED: {os.path.abspath(out_file)}")
    print("-------------------------------------------------------")
    print("ACTION REQUIRED: ")
    print(f"1. Use this file to batch download 1-year Historical L2 Ticks.")
    print(f"2. Save the downloaded CSVs to 'data/l2_ticks/'")
    print("-------------------------------------------------------")

if __name__ == '__main__':
    get_omega_universe()
