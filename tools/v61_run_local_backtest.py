#!/usr/bin/env python3
"""
v61 Local Edge Backtest Engine (The Boomerang Topology).

Design Principles (Data Gravity Enforced):
1. Runs EXCLUSIVELY on Local Edge Nodes (Linux/Windows AMD 128GB).
2. NEVER uploads 126GB raw frames to cloud. Downloads only the small model (.pkl).
3. Uses Spatial Ticker Sharding (Multiprocessing by Symbol) to strictly prevent OOM.
4. Preserves absolute T+1 causality by loading FULL time history per symbol batch.
5. Replicates exact V6.1 Cloud math: Rolling Mean, T+1 Targets, Excess Return.
"""

from __future__ import annotations

import argparse
import gc
import json
import multiprocessing as mp
import os
import pickle
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import polars as pl

# Try importing XGBoost (Required for Inference)
try:
    import xgboost as xgb
except ImportError:
    xgb = None

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from config import load_l2_pipeline_config, L2PipelineConfig
from config_v6 import FEATURE_COLS
from omega_core.trainer import OmegaTrainerV3, evaluate_frames


def _scan_local_frames(input_pattern: str) -> List[str]:
    """Scan local directory for parquet files."""
    import glob
    files = sorted(glob.glob(input_pattern, recursive=True))
    if not files:
        raise FileNotFoundError(f"No files found matching: {input_pattern}")
    return files


def _extract_all_symbols(file_paths: List[str]) -> List[str]:
    """
    Rapidly scan all parquet headers to find unique symbols.
    Uses polars scan for speed.
    """
    print(f"[*] Scanning {len(file_paths)} files for symbols...", flush=True)
    # Scan in chunks to avoid blowing up memory with metadata
    all_symbols = set()
    
    # Simple strategy: scan all, select symbol, unique.
    # For 126GB spread across many files, lazy scan + collect(unique) is efficient.
    try:
        lf = pl.scan_parquet(file_paths)
        if "symbol" not in lf.collect_schema().names():
             print("[!] Warning: 'symbol' column not found in schema. Assuming single-asset or error.")
             return []
        
        symbols = lf.select("symbol").unique().collect().get_column("symbol").to_list()
        all_symbols.update(s for s in symbols if s)
        
    except Exception as e:
        print(f"[!] Symbol scan failed: {e}. Falling back to file iteration.")
        # Fallback
        for f in file_paths:
            try:
                df = pl.read_parquet(f, columns=["symbol"])
                all_symbols.update(df["symbol"].unique().to_list())
            except Exception:
                continue
                
    sorted_syms = sorted(list(all_symbols))
    print(f"[*] Found {len(sorted_syms)} unique symbols.", flush=True)
    return sorted_syms


def _process_backtest_batch(task: dict) -> dict:
    """
    Worker function: Process a batch of symbols for backtest inference.
    """
    batch_id = task["batch_id"]
    symbols = task["symbols"]
    input_files = task["input_files"]
    model_path = task["model_path"]
    cfg_dump = task["cfg_dump"]
    
    # Load Config & Model inside worker to ensure isolation
    cfg = pickle.loads(cfg_dump)
    trainer = OmegaTrainerV3(cfg)
    
    with open(model_path, "rb") as f:
        payload = pickle.load(f)
        model = payload.get("model")
        scaler = payload.get("scaler")
        feature_cols = payload.get("feature_cols")

    # Load Data for Batch Symbols ONLY
    # ACTION 3: Single-file scan to prevent Arrow Rust panics from schema drift
    # across months of parquet files. Sequential is safer than bulk scan.
    try:
        tables = []
        for f_path in input_files:
            try:
                df_one = pl.scan_parquet(f_path).filter(pl.col("symbol").is_in(symbols)).collect()
                if df_one.height > 0:
                    tables.append(df_one)
            except Exception:
                continue

        if not tables:
            return {"batch_id": batch_id, "rows": 0, "metrics": {}}

        df = pl.concat(tables, how="diagonal_relaxed")
        
        # V62 Defensive Engineering: Drop heavy trace lists before sorting/preparing
        # to prevent OOM spikes as warned in handover/DEBUG_LESSONS.md
        heavy_cols = ["ofi_list", "ofi_trace", "vol_list", "vol_trace", "time_trace", "trace"]
        drop_cols = [c for c in heavy_cols if c in df.columns]
        if drop_cols:
            df = df.drop(drop_cols)

        # V6.1: Run _prepare_frames (includes T+1 logic and Physics features if not present)
        # Note: If reusing precomputed physics, this is fast.
        # If not, it runs recursive physics.
        # Ensure we don't accidentally re-run smoothing if it was done in ETL.
        # (ETL does smoothing. Trainer prepares targets).
        
        df = trainer._prepare_frames(df, cfg)
        
        if df.height == 0:
             return {"batch_id": batch_id, "rows": 0, "metrics": {}}

        # Calculate Excess Return for Evaluation Context (Optional, but good for alignment)
        # Trainer _prepare_frames calculates 't1_fwd_return' (absolute).
        # We can calc excess here if needed for metrics, but Model_Alignment uses direction.
        
        # Evaluate
        # We use the shared evaluate_frames logic from trainer.py
        batch_metrics = evaluate_frames(
            df, cfg, model=model, scaler=scaler, feature_cols=feature_cols
        )
        
        # Return partial sums for weighted aggregation?
        # evaluate_frames returns: n_frames, Topo_SNR, Orthogonality, Phys_Alignment, Model_Alignment
        # To aggregate globally, we need weighted averages.
        # Topo_SNR is global-ish, but can be averaged.
        # Alignments are means.
        
        # We return the counts and sum-products for accurate global aggregation
        # or simply return the raw metrics and average them (less accurate but simpler).
        # Better: Return raw correct/count for alignment.
        
        # Let's extract key components for aggregation
        n = batch_metrics["n_frames"]
        res = {
            "batch_id": batch_id,
            "rows": n,
            "weighted_metrics": {k: v * n for k, v in batch_metrics.items() if k != "DoD_pass"},
            "raw_metrics": batch_metrics
        }
        
        del df
        gc.collect()
        return res

    except Exception as e:
        print(f"[!] Batch {batch_id} failed: {e}")
        import traceback
        traceback.print_exc()
        return {"batch_id": batch_id, "rows": 0, "error": str(e)}


def main() -> int:
    ap = argparse.ArgumentParser(description="v61 Local Edge Backtest (Boomerang Topology)")
    ap.add_argument("--model-path", required=True, help="Path to downloaded .pkl model")
    ap.add_argument("--frames-dir", required=True, help="Local directory containing raw frames (126GB)")
    ap.add_argument("--output", default="backtest_metrics.json", help="Path to save result")
    ap.add_argument("--workers", type=int, default=8, help="Number of parallel workers")
    ap.add_argument("--symbols-per-batch", type=int, default=50, help="Symbols per memory batch")
    args = ap.parse_args()

    start_time = time.time()
    
    # 1. Validation
    if not os.path.exists(args.model_path):
        raise FileNotFoundError(f"Model not found at {args.model_path}")
    
    # 2. Config Loading
    cfg = load_l2_pipeline_config()
    cfg_dump = pickle.dumps(cfg)
    
    # 3. Discovery
    input_files = _scan_local_frames(os.path.join(args.frames_dir, "**/*.parquet"))
    all_symbols = _extract_all_symbols(input_files)
    
    if not all_symbols:
        print("[!] No symbols found. Exiting.")
        return 1

    # 4. Batching
    batches = [
        all_symbols[i : i + args.symbols_per_batch]
        for i in range(0, len(all_symbols), args.symbols_per_batch)
    ]
    print(f"[*] Created {len(batches)} batches for {len(all_symbols)} symbols.")

    tasks = []
    for idx, syms in enumerate(batches):
        tasks.append({
            "batch_id": idx,
            "symbols": syms,
            "input_files": input_files,
            "model_path": args.model_path,
            "cfg_dump": cfg_dump
        })

    # 5. Execution (Multiprocessing)
    print(f"[*] Starting Backtest on {args.workers} workers...", flush=True)
    
    global_stats = {
        "n_frames": 0.0,
        "Topo_SNR": 0.0,
        "Orthogonality": 0.0,
        "Phys_Alignment": 0.0,
        "Model_Alignment": 0.0,
        "Vector_Alignment": 0.0
    }
    
    processed_batches = 0
    
    # ACTION 4: Anti-Fragile Memory Release — force worker death after each batch
    # Rust/C++ jemalloc inside Polars does NOT reliably return freed pages to OS.
    # maxtasksperchild=1 forces process restart → OS Ring-0 reclaims all memory.
    with mp.Pool(args.workers, maxtasksperchild=1) as pool:
        for res in pool.imap_unordered(_process_backtest_batch, tasks):
            if "error" in res:
                print(f"    [!] Batch {res['batch_id']} error: {res['error']}")
                continue
                
            n = res["rows"]
            if n > 0:
                global_stats["n_frames"] += n
                for k, v in res["weighted_metrics"].items():
                    # V61 Fix: Prevent metric pollution. 
                    # Do not sum "n_frames" from weighted_metrics (which is n*n), as we handled it above.
                    if k in global_stats and k != "n_frames":
                        # Handle NaNs in partials? evaluate_frames returns NaNs if undefined.
                        # Assuming 0 contribution if NaN for sum
                        if np.isfinite(v):
                            global_stats[k] += v
            
            processed_batches += 1
            if processed_batches % 10 == 0:
                print(f"    Progress: {processed_batches}/{len(batches)} batches...", flush=True)

    # 6. Aggregation
    total_n = global_stats["n_frames"]
    if total_n > 0:
        for k in global_stats:
            if k != "n_frames":
                global_stats[k] /= total_n
    
    global_stats["seconds"] = round(time.time() - start_time, 2)
    global_stats["status"] = "completed"
    
    # 7. Output
    print("=== V61 Edge Backtest Results ===")
    print(json.dumps(global_stats, indent=2))
    
    with open(args.output, "w") as f:
        json.dump(global_stats, f, indent=2)
        
    print(f"[*] Results saved to {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
