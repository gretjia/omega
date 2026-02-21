#!/usr/bin/env python3
"""
v61 Linux Framing Agent (SHARDED, Anti-Fragile Edition).
Processes raw 7z archives -> Parquet Frames.

Anti-Fragile Fixes (2026-02-21):
  1. POLARS_MAX_THREADS=8 to prevent thread explosion (4 workers × 32 threads = 128 → capped)
  2. Global config load (was: per-file YAML parse)
  3. Git hash computed once in main() (was: subprocess per file)
  4. Workers default=2 (was: 4, caused swap thrash on 123GB system)
  5. shutil.rmtree for reliable cleanup (was: subprocess rm -rf)
"""

import os
import sys
import hashlib
import subprocess
import argparse
import shutil
import uuid
from pathlib import Path
from multiprocessing import get_context

# 【CRITICAL DEFENSE】Cap Polars internal Rayon threads per worker.
# Without this: 4 workers × 32 CPU cores = 128 threads fighting for RAM.
# With this:    2 workers × 8 threads  = 16 threads = optimal for 32-core Ryzen.
os.environ["POLARS_MAX_THREADS"] = "8"

# Add project root to sys.path
sys.path.append("/home/zepher/work/Omega_vNext")

from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l2_frames

RAW_ROOT = Path("/omega_pool/raw_7z_archives")
OUTPUT_ROOT = Path("/omega_pool/parquet_data/v52/frames/host=linux1")
SEVEN_ZIP = "/usr/bin/7z"

# 【FIX 2】Global config — load once, not per-file
GLOBAL_CFG = load_l2_pipeline_config()

def get_shard(filename, total_shards):
    h = hashlib.md5(filename.encode()).hexdigest()
    return int(h, 16) % total_shards

def process_day(args):
    """Process a single trading day: 7z extract → CSV scan → Polars ETL → Parquet."""
    day_path, hash_str, shard_index, total_shards = args

    date_str = day_path.stem
    out_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet"
    done_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet.done"

    if done_path.exists():
        return f"[{date_str}] Skipped (Done)"

    print(f"[{date_str}] Starting processing (Shard {shard_index}/{total_shards})...", flush=True)

    unique_id = uuid.uuid4().hex
    tmp_dir = Path(f"/omega_pool/temp_framing/{date_str}_{unique_id}")

    # Ensure clean start — kill any orphaned debris
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 7z extraction
        cmd = [SEVEN_ZIP, "x", str(day_path), f"-o{tmp_dir}", "-y"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        csvs = list(tmp_dir.glob("**/*.csv"))
        if not csvs:
            return f"[{date_str}] Error: No CSVs found in 7z"

        # ETL with global config (no re-parse)
        frames = build_l2_frames([str(p) for p in csvs], GLOBAL_CFG)

        if frames.height > 0:
            # Atomic write: write to .tmp then rename
            tmp_parquet = out_path.with_suffix(".parquet.tmp")
            frames.write_parquet(tmp_parquet, compression="snappy")
            tmp_parquet.rename(out_path)
            done_path.touch()
            return f"[{date_str}] Completed: {frames.height} rows"
        else:
            return f"[{date_str}] Error: Empty frames generated"

    except Exception as e:
        return f"[{date_str}] CRITICAL Error: {e}"
    finally:
        # ALWAYS clean up 7.6GB of extracted CSVs, even on error
        shutil.rmtree(tmp_dir, ignore_errors=True)

def main():
    ap = argparse.ArgumentParser(description="v61 Linux Framing Agent (Anti-Fragile)")
    ap.add_argument("--years", default="2023,2024,2025,2026")
    ap.add_argument("--workers", type=int, default=2,
                    help="Number of parallel workers. Default=2 to prevent swap thrash.")
    ap.add_argument("--shard", type=int, default=0, help="Shard index (0 to N-1)")
    ap.add_argument("--total-shards", type=int, default=2, help="Total number of shards")
    args = ap.parse_args()

    years = args.years.split(",")
    all_files = []

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # 【FIX 1】Compute git hash ONCE in main, pass to workers
    try:
        hash_str = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd="/home/zepher/work/Omega_vNext"
        ).decode().strip()
    except Exception:
        hash_str = "unknown"

    print(f"Git hash: {hash_str}")
    print(f"Shard: {args.shard}/{args.total_shards}, Workers: {args.workers}")
    print(f"POLARS_MAX_THREADS: {os.environ.get('POLARS_MAX_THREADS', 'unset')}")

    for year in years:
        year_path = RAW_ROOT / year
        if year_path.exists():
            all_files.extend(list(year_path.rglob("*.7z")))
            all_files.extend(list(year_path.rglob("*.rar")))

        # Check for YearMonth style folders (e.g. 202601)
        for sub in RAW_ROOT.glob(f"{year}*"):
            if sub.is_dir() and sub.name != year:
                all_files.extend(list(sub.rglob("*.7z")))

    # Filter by shard BEFORE spawning Pool
    tasks = []
    skipped_by_shard = 0
    for f in all_files:
        if get_shard(f.name, args.total_shards) == args.shard:
            tasks.append((f, hash_str, args.shard, args.total_shards))
        else:
            skipped_by_shard += 1

    print(f"Total files found: {len(all_files)}")
    print(f"Files assigned to this shard ({args.shard}/{args.total_shards}): {len(tasks)}")
    print(f"Files skipped by sharding: {skipped_by_shard}")

    if not tasks:
        print("Nothing to do for this shard. Exiting.")
        return

    # Linux + Polars can deadlock under fork; force spawn context for worker safety.
    # maxtasksperchild=5 balances memory release and process cold-start overhead.
    ctx = get_context("spawn")
    with ctx.Pool(args.workers, maxtasksperchild=5) as p:
        for res in p.imap_unordered(process_day, tasks):
            if res:
                print(res, flush=True)

    print("=== FRAMING COMPLETE ===")

if __name__ == "__main__":
    main()
