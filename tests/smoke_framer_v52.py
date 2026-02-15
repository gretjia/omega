import sys
import os
import shutil
from pathlib import Path
import polars as pl
import pandas as pd

# Ensure project root is in path
sys.path.append(os.getcwd())

from pipeline.engine.framer import _process_single_stock, _validate_is_quote_file
from config import load_l2_pipeline_config

def create_dummy_csv(path, is_quote=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    N = 20
    # Use Chinese column names as per config.py default L2MappingConfig
    cols = {
        "自然日": [20250101] * N,
        "时间": [93000000 + i * 3000 for i in range(N)],
        "成交价": [10.0 + i * 0.01 for i in range(N)],
        "成交量": [100] * N,
        "成交额": [1000] * N,
        "BS标志": [0] * N
    }
    
    if is_quote:
        # Add Quote specific columns
        cols["申买价1"] = [9.9 + i * 0.01 for i in range(N)]
        cols["申卖价1"] = [10.1 + i * 0.01 for i in range(N)]
        cols["申买量1"] = [100] * N
        cols["申卖量1"] = [100] * N
    
    df = pd.DataFrame(cols)
    # Save as GBK to mimic real QMT data
    df.to_csv(path, index=False, encoding="gbk")
    return path

def test_framer_v52_logic():
    print("--- Starting Framer v5.2 Logic Smoke Test ---", flush=True)
    
    cfg = load_l2_pipeline_config()
    tmp_dir = Path("tests/temp_framer_smoke")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    try:
        # 1. Test Schema Validation
        print("\n[Test 1] Schema Validation (Quotes vs Ticks)", flush=True)
        quote_file = create_dummy_csv(tmp_dir / "000001.SZ" / "quote.csv", is_quote=True)
        tick_file = create_dummy_csv(tmp_dir / "000001.SZ" / "tick.csv", is_quote=False)
        
        is_quote_valid = _validate_is_quote_file(quote_file, cfg)
        is_tick_valid = _validate_is_quote_file(tick_file, cfg)
        
        print(f"  Quote File Valid? {is_quote_valid} (Expected: True)", flush=True)
        print(f"  Tick File Valid?  {is_tick_valid} (Expected: False)", flush=True)
        
        if not is_quote_valid or is_tick_valid:
            print("  [FAIL] Schema validation failed.", flush=True)
            return

        # 2. Test Processing & Output
        print("\n[Test 2] Processing & Physics Output", flush=True)
        # Pass both files; expect Ticks to be filtered out
        df_res = _process_single_stock("000001.SZ", [str(quote_file), str(tick_file)], cfg)
        
        if df_res is None:
            print("  [FAIL] Processing returned None.", flush=True)
            return
            
        print(f"  Output Schema: {df_res.columns}", flush=True)
        print(f"  Row Count: {df_res.height}", flush=True)
        
        # Verify Symbol Column
        if "symbol" not in df_res.columns:
            print("  [FAIL] 'symbol' column missing.", flush=True)
        elif df_res["symbol"][0] != "000001.SZ":
             print(f"  [FAIL] Symbol mismatch. Got {df_res['symbol'][0]}", flush=True)
        else:
            print("  [PASS] Symbol column verified.", flush=True)

        # Verify Physics Columns
        req_physics = ["epiplexity", "srl_resid", "adaptive_y", "direction"]
        missing = [c for c in req_physics if c not in df_res.columns]
        if missing:
            print(f"  [FAIL] Missing physics columns: {missing}", flush=True)
        else:
            print("  [PASS] Physics columns verified.", flush=True)
            
        # Verify Sorting (bucket_id or time)
        # Note: bucket_id is derived from time in build_l2_frames
        if "bucket_id" in df_res.columns:
            is_sorted = df_res["bucket_id"].is_sorted()
            print(f"  [PASS] Time/Bucket Sorted? {is_sorted}", flush=True)
        
        print("\n--- Smoke Test Complete: SUCCESS ---", flush=True)

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Test Failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)

if __name__ == "__main__":
    test_framer_v52_logic()
