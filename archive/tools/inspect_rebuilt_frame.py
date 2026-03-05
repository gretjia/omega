import polars as pl
import sys
from pathlib import Path

def inspect_frame(file_path):
    print(f"Inspecting file: {file_path}")
    try:
        df = pl.read_parquet(file_path)
        print("\n--- Schema ---")
        print(df.schema)
        
        print("\n--- Columns ---")
        print(df.columns)
        
        required_cols = ["trade_vol", "cancel_vol"]
        missing = [c for c in required_cols if c not in df.columns]
        
        if missing:
            print(f"\n[FAIL] Missing required columns: {missing}")
        else:
            print(f"\n[PASS] All required columns found: {required_cols}")
            
        print("\n--- Head (5 rows) ---")
        print(df.head(5))
        
        print("\n--- Statistics ---")
        print(df.select([
            pl.col("trade_vol").sum().alias("total_trade_vol"),
            pl.col("cancel_vol").sum().alias("total_cancel_vol"),
            pl.col("trade_vol").max().alias("max_trade_vol"),
            pl.col("cancel_vol").max().alias("max_cancel_vol"),
        ]))
        
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to a file found in LS output if not provided
        default_file = "data/level2_frames_2023/20230103_000001.SZ.parquet"
        print(f"No file provided, defaulting to {default_file}")
        inspect_frame(default_file)
    else:
        inspect_frame(sys.argv[1])
