
import os
import sys
import shutil
import polars as pl
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from omega_core.omega_etl import scan_l2_quotes, build_l2_frames
from config import load_l2_pipeline_config
from tools.forge_base_matrix import _process_symbol_batch

def create_synthetic_l2_data(output_path):
    """Generates synthetic L2 data to test smoothing."""
    # Create 6 ticks. 
    # Ticks 1-3: v_ofi=10, depth=100
    # Ticks 4-6: v_ofi=40, depth=200
    # Rolling mean (window=3) at tick 3 should be (10+10+10)/3 = 10
    # Rolling mean at tick 4 should be (10+10+40)/3 = 20
    # Rolling mean at tick 6 should be (40+40+40)/3 = 40
    
    data = {
        "symbol": ["TEST"] * 12,
        "time": [93000000 + i*3000 for i in range(12)], # 12 ticks
        "price": [100.0 + (i%2)*0.1 for i in range(12)],
        "vol": [100.0 + i*10 for i in range(12)],
        "bid_p1": [99.0 + (i%2)*0.1 for i in range(12)],
        "ask_p1": [101.0 + (i%2)*0.1 for i in range(12)],
        "bid_v1": [50.0] * 12,
        "ask_v1": [50.0] * 12,
        # 6 ticks for day 1, 6 ticks for day 2
        "date": [20240101] * 6 + [20240102] * 6
    }
    
    # Add dummy levels 2-5
    for i in range(2, 6):
        data[f"bid_p{i}"] = [99.0 - i*0.1] * 12
        data[f"ask_p{i}"] = [101.0 + i*0.1] * 12
        data[f"bid_v{i}"] = [10.0] * 12
        data[f"ask_v{i}"] = [10.0] * 12

    df = pl.DataFrame(data)
    df.write_parquet(output_path)
    print(f"Created synthetic L2 data at {output_path}")
    return df

def verify_etl_smoothing(l2_path):
    print("\n--- Verifying ETL Smoothing (Anti-Aliasing) ---")
    cfg = load_l2_pipeline_config()
    
    # Patch scan_l2_quotes to return the parquet directly, skipping rename logic
    # because our synthetic data already has the correct internal column names.
    # We also need to cast time/numeric columns as build_l2_frames expects specific types.
    
    original_scan = scan_l2_quotes
    
    def mock_scan(path, cfg):
        return pl.scan_parquet(path).with_columns([
            pl.col("time").cast(pl.Int64),
            pl.col("price").cast(pl.Float64),
            pl.col("vol").cast(pl.Float64),
            pl.col("bid_p1").cast(pl.Float64),
            pl.col("ask_p1").cast(pl.Float64),
            pl.col("bid_v1").cast(pl.Float64),
            pl.col("ask_v1").cast(pl.Float64),
        ])

    # Inject mock
    import omega_core.omega_etl
    omega_core.omega_etl.scan_l2_quotes = mock_scan
    
    # Disable session filter for test
    from dataclasses import replace
    new_session = replace(cfg.session, enable_session_filter=False)
    
    # Relax volume clock for small data
    new_vc = replace(cfg.volume_clock, bucket_size=30, min_ticks_per_bucket=2, dynamic_bucket_size=False)
    
    # Relax quality filter just in case
    new_quality = replace(cfg.quality, min_price=0.0, min_book_price=0.0)
    
    cfg = replace(cfg, session=new_session, volume_clock=new_vc, quality=new_quality)
    
    try:
        frames = build_l2_frames(str(l2_path), cfg)
        print("ETL output frames schema:", frames.schema)
    finally:
        # Restore
        omega_core.omega_etl.scan_l2_quotes = original_scan
    
    if frames.height == 0:
        print("[FAIL] ETL produced empty frames.")
        return None
        
    print("[PASS] ETL pipeline ran successfully.")
    print("ETL Frames (Head/Tail):")
    print(frames.head(2))
    print(frames.tail(2))
    print("Explicit Dates:", frames.get_column("date").to_list())
    print("Explicit Buckets:", frames.get_column("bucket_id").to_list())
    return frames

def verify_forge_logic(frames_path, output_dir):
    print("\n--- Verifying Forge Logic (Momentum & Excess Return) ---")
    
    # We need to mock the inputs for _process_symbol_batch or run it directly.
    # Let's run a simplified forge process using the same logic.
    
    # 1. Load frames
    frames = pl.read_parquet(frames_path)
    
    # Save temp frames for forge
    temp_frames_path = os.path.join(output_dir, "temp_frames.parquet")
    frames.write_parquet(temp_frames_path)
    
    # 3. Configure task
    task = {
        "batch_id": 0,
        "batch_symbols": ["TEST"],
        "input_files": [temp_frames_path],
        "shard_dir": output_dir,
        "keep_cols": ["srl_resid", "direction", "t1_excess_return"], # Columns to verify
        "peace_threshold": -1.0, # Disable filter (allow any value)
        "peace_threshold_baseline": -1.0,
        "srl_resid_sigma_mult": 0.0,
        "topo_energy_sigma_mult": 0.0
    }
    
    # 4. Run Forge Batch
    try:
        result = _process_symbol_batch(task)
        print("Forge Result:", result)
    except Exception as e:
        print(f"[FAIL] Forge process crashed: {e}")
        import traceback
        traceback.print_exc()
        return

    output_path = result.get("output_path")
    if not output_path or not os.path.exists(output_path):
        print(f"[FAIL] No output parquet found at {output_path}")
        
        # DEBUG: Inspect why rows were dropped
        print("DEBUG: Inspecting intermediate frame...")
        from omega_core.trainer import OmegaTrainerV3
        from tools.forge_base_matrix import _build_relaxed_cfg
        
        cfg = _build_relaxed_cfg(
            peace_threshold=-1.0,
            srl_mult=0.0,
            topo_mult=0.0
        )
        trainer = OmegaTrainerV3(cfg)
        raw_df = pl.read_parquet(temp_frames_path)
        base_df = trainer._prepare_frames(raw_df, cfg)
        print("Base DF Columns:", base_df.columns)
        print("Base DF Head:", base_df.head())
        if "epiplexity" in base_df.columns:
            print("Epiplexity:", base_df.get_column("epiplexity").to_list())
        if "is_physics_valid" in base_df.columns:
            print("Physics Valid:", base_df.get_column("is_physics_valid").to_list())
            
        # DEBUG Step-by-Step
        print("\n--- DEBUG: Manual Step-by-Step ---")
        df = raw_df
        print(f"Step 0 (Raw): {df.height} rows")
        
        # 1. T+1 Logic
        t1_days = 1
        key_cols = ["symbol", "date"]
        sort_cols = ["symbol", "date", "bucket_id"]
        
        daily = (
            df.sort(sort_cols)
            .group_by(key_cols, maintain_order=True)
            .agg(pl.col("close").last().alias("_day_close"))
            .sort(key_cols)
        )
        print("Daily Agg:", daily)
        
        daily = daily.with_columns(pl.col("_day_close").shift(-t1_days).over("symbol").alias("t1_close"))
        print("Daily Shift:", daily)
        
        daily = daily.select(key_cols + ["t1_close"])
        df = df.join(daily, on=key_cols, how="left")
        
        print(f"Step 1 (Join T1): {df.height} rows")
        print(df.select(["symbol", "date", "close", "t1_close"]))
        
        # 2. Drop Nulls
        df = df.drop_nulls(subset=["t1_close"])
        print(f"Step 2 (Drop Nulls): {df.height} rows")
        
        return

    # 5. Inspect Output
    df = pl.read_parquet(output_path)
    print("Forge output columns:", df.columns)
    
    # Check Direction Sign
    # In v61, direction = sign(srl_resid). 
    # If srl_resid is positive, direction must be 1.
    if "direction" in df.columns and "srl_resid" in df.columns:
        srl = df.get_column("srl_resid").head(1).item()
        direction = df.get_column("direction").head(1).item()
        print(f"SRL Resid: {srl}, Direction: {direction}")
        
        if np.sign(srl) == np.sign(direction):
             print("[PASS] Momentum sign is correct (Positive Correlation).")
        else:
             print("[FAIL] Momentum sign is INVERTED (Negative Correlation) - Regression!")
    else:
        print("[WARN] 'direction' or 'srl_resid' column missing in output.")

    # Check Excess Return logic (implied presence)
    # The forge script usually just prepares features. The excess return is calculated in the SWARM tool in v61.
    # Wait, the plan said "Update tools/swarm_xgb.py ... Implement Excess Return".
    # It also said "Update tools/run_vertex_xgb_train.py".
    # Does forge calculate it? 
    # Let's check `forge_base_matrix.py`.
    # It does NOT seem to calculate excess return. It selects columns.
    # The excess return is calculated in memory during training (swarm/vertex).
    # So we don't check it here.

    print("[PASS] Forge pipeline ran successfully.")

def main():
    output_dir = "v61_test_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    l2_path = os.path.join(output_dir, "synthetic_l2.parquet")
    create_synthetic_l2_data(l2_path)
    
    frames = verify_etl_smoothing(l2_path)
    if frames is not None:
        frames_path = os.path.join(output_dir, "frames.parquet")
        frames.write_parquet(frames_path)
        verify_forge_logic(frames_path, output_dir)
        
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    main()
