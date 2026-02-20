#!/usr/bin/env python3
"""
v61 Linux Framing Agent.
Processes raw 7z archives -> Parquet Frames.
Specialized for 2025-2026 data (Backtest Portion).
"""

import os
import sys
import glob
import subprocess
import argparse
from pathlib import Path
from multiprocessing import Pool

# Add project root to sys.path
sys.path.append("/home/zepher/work/Omega_vNext")

from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l2_frames

RAW_ROOT = Path("/omega_pool/raw_7z_archives")
OUTPUT_ROOT = Path("/omega_pool/parquet_data/v52/frames/host=linux1")
SEVEN_ZIP = "/usr/bin/7z"

def process_day(args):
    year, month, day_path = args
    cfg = load_l2_pipeline_config()
    
    # Define output
    date_str = day_path.stem # e.g. 20250102
    hash_str = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd="/home/zepher/work/Omega_vNext").decode().strip()
    out_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet"
    done_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet.done"
    
    if done_path.exists():
        return f"Skipped {date_str} (Done)"
        
    print(f"Processing {date_str}...", flush=True)
    
    # Temp extract dir
    tmp_dir = Path(f"/tmp/omega_framing/{date_str}")
    if tmp_dir.exists():
        import shutil
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract 7z
    # Assumes day_path is a .7z file? Or a dir?
    # User showed 2025/202501. Likely folders containing 7z or CSVs?
    # Let's assume day_path is a file for now, or adapt.
    # Actually, standard structure is Year/Month/Date.7z or Year/Month/Date.csv?
    # Let's assume we extract `day_path` to `tmp_dir`.
    
    try:
        cmd = [SEVEN_ZIP, "x", str(day_path), f"-o{tmp_dir}", "-y"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        
        # Find CSVs
        csvs = list(tmp_dir.glob("**/*.csv"))
        if not csvs:
            return f"No CSVs in {date_str}"
            
        # Run ETL
        # build_l2_frames takes path or list of paths
        frames = build_l2_frames([str(p) for p in csvs], cfg)
        
        if frames.height > 0:
            frames.write_parquet(out_path, compression="snappy")
            done_path.touch()
            return f"Completed {date_str}: {frames.height} rows"
        else:
            return f"Empty frames for {date_str}"
            
    except Exception as e:
        return f"Error {date_str}: {e}"
    finally:
        # Cleanup
        if tmp_dir.exists():
            import shutil
            shutil.rmtree(tmp_dir)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2025,2026")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    
    years = args.years.split(",")
    tasks = []
    
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    
    for year in years:
        year_path = RAW_ROOT / year
        if not year_path.exists(): 
            # Try 202601 style
            if len(year) == 4:
                 # Look for 2026*
                 candidates = list(RAW_ROOT.glob(f"{year}*"))
                 for c in candidates:
                     if c.is_dir():
                         # Recurse? No, structure is Year/Month/File?
                         # Let's just walk the tree looking for .7z
                         for p in c.rglob("*.7z"):
                             tasks.append((year, "unknown", p))
                         for p in c.rglob("*.rar"):
                             tasks.append((year, "unknown", p))
            continue
            
        # Walk year path
        for p in year_path.rglob("*.7z"):
             tasks.append((year, "unknown", p))
        for p in year_path.rglob("*.rar"):
             tasks.append((year, "unknown", p))

    print(f"Found {len(tasks)} day archives to process.")
    
    with Pool(args.workers) as p:
        for res in p.imap_unordered(process_day, tasks):
            print(res)

if __name__ == "__main__":
    main()
