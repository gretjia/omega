# v62 Stage 1 Windows Base Lake ETL Agent
# Extracts 7z archives -> Parses CSVs -> Writes Base_L1.parquet
# (Strictly NO physics math to prevent 72-hour IO/CPU deadlock)
#
# Anti-Fragile Fixes:
#   1. POLARS_MAX_THREADS=8 to prevent thread explosion
import sys
import hashlib
import subprocess
import argparse
import shutil
import uuid
from pathlib import Path
from multiprocessing import Pool

# 【CRITICAL DEFENSE】Cap Polars internal Rayon threads per worker.
os.environ["POLARS_MAX_THREADS"] = "8"

# Add project root to sys.path
sys.path.append(r"C:\Omega_vNext")

from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l1_base_ticks

RAW_ROOT = Path(r"E:\data\level2")
OUTPUT_ROOT = Path(r"D:\Omega_frames\v62_base_l1\host=windows1")
SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"

# 【FIX 2】Global config — load once, not per-file
GLOBAL_CFG = load_l2_pipeline_config()

def get_shard(filename, total_shards):
    h = hashlib.md5(filename.encode()).hexdigest()
    return int(h, 16) % total_shards

def process_day(args):
    """Process a single trading day: 7z extract -> CSV scan -> Polars ETL -> Parquet."""
    day_path, hash_str, shard_index, total_shards = args

    os.chdir(r"C:\Omega_vNext")
    date_str = day_path.stem
    out_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet"
    done_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet.done"

    if done_path.exists():
        return f"[{date_str}] Skipped (Done)"

    print(f"[{date_str}] Starting processing (Shard {shard_index}/{total_shards})...", flush=True)

    unique_id = uuid.uuid4().hex
    tmp_dir = Path(f"D:/tmp/framing/{date_str}_{unique_id}")

    # Ensure clean start
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 7z extraction
        cmd = [SEVEN_ZIP, "x", str(day_path), f"-o{tmp_dir}", "-y"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        csvs = list(tmp_dir.glob("**/*.csv"))
        if not csvs:
            return f"[{date_str}] Error: No CSVs found"

        # ETL with global config (no re-parse) - Pure Base L1 Generation
        frames = build_l1_base_ticks([str(p) for p in csvs], GLOBAL_CFG)

        if frames.height > 0:
            # Atomic write: write to .tmp then rename
            tmp_parquet = out_path.with_suffix(".parquet.tmp")
            frames.write_parquet(tmp_parquet, compression="snappy")
            tmp_parquet.rename(out_path)
            done_path.touch()
            return f"[{date_str}] Completed: {frames.height} rows"
        else:
            return f"[{date_str}] Error: Empty frames"

    except Exception as e:
        return f"[{date_str}] CRITICAL Error: {e}"
    finally:
        # ALWAYS clean up extracted CSVs, even on error
        shutil.rmtree(tmp_dir, ignore_errors=True)

def main():
    ap = argparse.ArgumentParser(description="v61 Windows Framing Agent (Anti-Fragile)")
    ap.add_argument("--years", default="2023,2024,2025,2026")
    ap.add_argument("--workers", type=int, default=2,
                    help="Number of parallel workers. Default=2 to prevent swap thrash.")
    ap.add_argument("--shard", type=int, default=1, help="Shard index (0 to N-1)")
    ap.add_argument("--total-shards", type=int, default=2, help="Total number of shards")
    args = ap.parse_args()

    years = args.years.split(",")
    all_files = []

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # 【FIX 1】Compute git hash ONCE in main, pass to workers
    try:
        hash_str = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=r"C:\Omega_vNext"
        ).decode().strip()
    except Exception:
        hash_str = "unknown"

    print(f"Git hash: {hash_str}")
    print(f"Shard: {args.shard}/{args.total_shards}, Workers: {args.workers}")
    print(f"POLARS_MAX_THREADS: {os.environ.get('POLARS_MAX_THREADS', 'unset')}")

    for year in years:
        year_path = RAW_ROOT / year
        if year_path.exists():
            for p in year_path.rglob("*.7z"):
                all_files.append(p)

        for sub in RAW_ROOT.glob(f"{year}*"):
            if sub.is_dir() and sub.name != year:
                for p in sub.rglob("*.7z"):
                    all_files.append(p)

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

    # maxtasksperchild=1: Force worker death after each 7z+ETL cycle.
    # Polars/Rust jemalloc hoards memory and won't release to OS.
    with Pool(args.workers, maxtasksperchild=1) as p:
        for res in p.imap_unordered(process_day, tasks):
            if res:
                print(res, flush=True)

    print("=== FRAMING COMPLETE ===")

if __name__ == "__main__":
    main()
