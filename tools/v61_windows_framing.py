#!/usr/bin/env python3
"""
v61 Windows Framing Agent (SHARDED).
Processes raw 7z archives -> Parquet Frames.
Supports 2023-2026 data.
"""

import os
import sys
import hashlib
import subprocess
import argparse
from pathlib import Path
from multiprocessing import Pool

# Add project root to sys.path
sys.path.append(r"C:\Omega_vNext")

from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l2_frames

RAW_ROOT = Path(r"E:\data\level2")
OUTPUT_ROOT = Path(r"D:\Omega_frames\v61\host=windows1")
SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"

def get_shard(filename, total_shards):
    h = hashlib.md5(filename.encode()).hexdigest()
    return int(h, 16) % total_shards

def process_day(args):
    year, month, day_path, shard_info = args
    shard_index, total_shards = shard_info
    
    filename = day_path.name
    if get_shard(filename, total_shards) != shard_index:
        return None
        
    os.chdir(r"C:\Omega_vNext")
    cfg = load_l2_pipeline_config()
    date_str = day_path.stem
    try:
        hash_str = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=r"C:\Omega_vNext").decode().strip()
    except:
        hash_str = "unknown"

    out_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet"
    done_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet.done"
    
    if done_path.exists():
        return f"Skipped {date_str} (Done)"
        
    print(f"[{date_str}] Starting processing (Shard {shard_index}/{total_shards})...", flush=True)
    
    import uuid
    unique_id = uuid.uuid4().hex
    tmp_dir = Path(f"D:/tmp/framing/{date_str}_{unique_id}")
    
    try:
        if tmp_dir.exists():
            subprocess.run(["rmdir", "/s", "/q", str(tmp_dir)], shell=True, check=False)
        tmp_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return f"Setup Error {date_str}: {e}"
    
    try:
        cmd = [SEVEN_ZIP, "x", str(day_path), f"-o{tmp_dir}", "-y"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        
        csvs = list(tmp_dir.glob("**/*.csv"))
        if not csvs:
            return f"Error {date_str}: No CSVs found"
            
        frames = build_l2_frames([str(p) for p in csvs], cfg)
        
        if frames.height > 0:
            frames.write_parquet(out_path, compression="snappy")
            done_path.touch()
            return f"Completed {date_str}: {frames.height} rows"
        else:
            return f"Error {date_str}: Empty frames"
            
    except Exception as e:
        return f"CRITICAL Error {date_str}: {e}"
    finally:
        try:
            if tmp_dir.exists():
                subprocess.run(["rmdir", "/s", "/q", str(tmp_dir)], shell=True, check=False)
        except:
            pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2023,2024,2025,2026")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--shard", type=int, default=1, help="Shard index (0 to N-1)")
    ap.add_argument("--total-shards", type=int, default=2, help="Total number of shards")
    args = ap.parse_args()
    
    years = args.years.split(",")
    all_files = []
    
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    
    for year in years:
        year_path = RAW_ROOT / year
        if year_path.exists():
             for p in year_path.rglob("*.7z"):
                 all_files.append(p)
        
        for sub in RAW_ROOT.glob(f"{year}*"):
            if sub.is_dir() and sub.name != year:
                 for p in sub.rglob("*.7z"):
                     all_files.append(p)

    tasks = []
    skipped_by_shard = 0
    for f in all_files:
        if get_shard(f.name, args.total_shards) == args.shard:
            tasks.append(("unknown", "unknown", f, (args.shard, args.total_shards)))
        else:
            skipped_by_shard += 1

    print(f"Total files found: {len(all_files)}")
    print(f"Files assigned to this shard ({args.shard}/{args.total_shards}): {len(tasks)}")
    print(f"Files skipped by sharding: {skipped_by_shard}")

    if not tasks:
        print("Nothing to do for this shard. Exiting.")
        return

    with Pool(args.workers) as p:
        for res in p.imap_unordered(process_day, tasks):
            if res:
                print(res)

if __name__ == "__main__":
    main()
