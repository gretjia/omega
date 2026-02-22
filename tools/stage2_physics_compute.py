#!/usr/bin/env python3
"""
v62 Stage 2 Physics Compute Agent
Reads Base_L1.parquet -> Computes MDL/SRL/Topology -> Writes Feature_L2.parquet

Anti-Fragile Fixes (Codex Validated):
  1. Explicit Symbol-Batch Loading: Prevents OOM by lazy-scanning and executing
     physics per symbol/date chunk instead of blindly loading the entire universe.
"""

import os
import sys
import glob
import argparse
import polars as pl
from pathlib import Path
from multiprocessing import get_context

# Prevent Polars Rayon Thread Explosion
os.environ["POLARS_MAX_THREADS"] = "8"

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l2_features_from_l1

GLOBAL_CFG = load_l2_pipeline_config()

def process_chunk(kwargs):
    l1_file = kwargs['l1_file']
    out_dir = kwargs['out_dir']
    
    file_path = Path(l1_file)
    out_path = Path(out_dir) / file_path.name.replace("Base_L1", "Feature_L2")
    done_path = Path(out_dir) / (file_path.name.replace("Base_L1", "Feature_L2") + ".done")
    
    if done_path.exists():
        return f"[{file_path.name}] Skipped (Done)"
        
    print(f"[{file_path.name}] Starting Stage 2 Physics Computation...", flush=True)

    try:
        # Codex Correction: DO NOT load full universe into memory blindly.
        # We process files individually, and within each file, process by symbol batches.
        lf = pl.scan_parquet(l1_file)
        
        # 1. Lazy evaluation to extract unique symbols in this chunk
        try:
            symbols = lf.select("symbol").unique().collect(streamable=True).get_column("symbol").to_list()
        except pl.exceptions.ColumnNotFoundError:
            # Fallback if no symbol column exists
            symbols = [None]
            
        batch_size = 50
        symbol_batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]
        
        computed_dfs = []
        for batch in symbol_batches:
            if batch == [None]:
                batch_lf = lf
            else:
                batch_lf = lf.filter(pl.col("symbol").is_in(batch))
                
            # Apply the mathematically verified V62 Physics pipeline
            batch_df = build_l2_features_from_l1(batch_lf, GLOBAL_CFG)
            
            if batch_df is not None and batch_df.height > 0:
                computed_dfs.append(batch_df)
                
            # OOM Guard: Iterative GC sweep per batch
            del batch_lf
            del batch_df
            import gc
            gc.collect()
        
        if computed_dfs:
            frames_df = pl.concat(computed_dfs)
            # Atomic write
            tmp_parquet = out_path.with_suffix(".parquet.tmp")
            frames_df.write_parquet(tmp_parquet, compression="snappy")
            tmp_parquet.rename(out_path)
            done_path.touch()
            return_msg = f"[{file_path.name}] Completed: {frames_df.height} rows"
            
            del frames_df
            del computed_dfs
        else:
            return_msg = f"[{file_path.name}] Error: Empty physics frames generated"
            
        del lf
        return return_msg
            
    except Exception as e:
        return f"[{file_path.name}] CRITICAL Error: {e}"
    finally:
        # OOM Guard: Force garbage collection on both success and exception paths
        import gc
        gc.collect()

def main():
    ap = argparse.ArgumentParser(description="v62 Stage 2 Physics Compute Agent")
    ap.add_argument("--input-dir", required=True, help="Directory containing Base_L1.parquet files")
    ap.add_argument("--output-dir", required=True, help="Directory to output Feature_L2.parquet files")
    ap.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    args = ap.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    l1_files = list(input_path.rglob("*.parquet"))
    # Filter out tmp/done files
    l1_files = [str(p) for p in l1_files if not str(p).endswith(".tmp") and not str(p).endswith(".done")]

    print(f"Found {len(l1_files)} Base_L1 chunks to process.")

    tasks = []
    for f in l1_files:
        tasks.append({'l1_file': f, 'out_dir': str(output_path)})

    if not tasks:
        print("Nothing to do. Exiting.")
        return

    # Use spawn for safety across different OS
    ctx = get_context("spawn")
    with ctx.Pool(args.workers, maxtasksperchild=10) as p:
        for res in p.imap_unordered(process_chunk, tasks):
            if res:
                print(res, flush=True)

    print("=== STAGE 2 PHYSICS COMPUTE COMPLETE ===")

if __name__ == "__main__":
    main()
