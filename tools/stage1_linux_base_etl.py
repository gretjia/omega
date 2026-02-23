# v62 Stage 1 Linux Base Lake ETL Agent
# Extracts 7z archives -> Parses CSVs -> Writes Base_L1.parquet
# (Strictly NO physics math to prevent 72-hour IO/CPU deadlock)
#
# Anti-Fragile Fixes (Codex Validated):
#   1. Robust NVMe Fallback: Writes temp cache to /home/zepher/framing_cache (4TB NVMe) instead of finite /dev/shm.
import os
import sys
import hashlib
import subprocess
import argparse
import shutil
import uuid
import signal
import atexit
from pathlib import Path
from multiprocessing import get_context

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 【ZFS BYPASS & CPU OPTIMIZATION】
# Extracting to the massive 4TB NVMe (/home) bypasses ZFS write amplification and RAM limits.
os.environ["POLARS_TEMP_DIR"] = "/home/zepher/framing_cache"
os.environ["TMPDIR"] = "/home/zepher/framing_cache"
os.environ["POLARS_MAX_THREADS"] = "4"

# Add project root to sys.path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l1_base_ticks
from tools.stage1_incremental_writer import write_l1_incremental_parquet
from tools.stage1_resume_utils import (
    clear_stale_done_marker,
    ensure_done_for_existing_parquet,
    find_existing_done_for_date,
)

RAW_ROOT = Path("/omega_pool/raw_7z_archives")
OUTPUT_ROOT = Path("/omega_pool/parquet_data/v62_base_l1/host=linux1")
SEVEN_ZIP = "/usr/bin/7z"

# 【FIX 2】Global config — load once, not per-file
GLOBAL_CFG = load_l2_pipeline_config()

ALLOW_USER_SLICE_ENV = "OMEGA_STAGE1_ALLOW_USER_SLICE"
TARGET_OOM_SCORE_ADJ = 300


def _read_self_cgroup_path():
    """Return cgroup v2 path for current process, best-effort."""
    cgroup_file = Path("/proc/self/cgroup")
    if not cgroup_file.exists():
        return ""
    try:
        for line in cgroup_file.read_text(encoding="utf-8").splitlines():
            # cgroup v2 format: 0::/some/path
            parts = line.split(":", 2)
            if len(parts) == 3 and parts[2]:
                return parts[2]
    except Exception:
        return ""
    return ""


def _ensure_heavy_workload_slice():
    """
    Hard guardrail:
    Refuse to run stage1 outside heavy-workload.slice unless explicitly bypassed.
    """
    if sys.platform != "linux":
        return

    if os.environ.get(ALLOW_USER_SLICE_ENV, "").strip().lower() in {"1", "true", "yes"}:
        print(
            f"[WARN] {ALLOW_USER_SLICE_ENV}=1 set, bypassing heavy-workload.slice guardrail.",
            flush=True,
        )
        return

    cgroup_path = _read_self_cgroup_path()
    in_heavy_slice = (
        "/heavy-workload.slice/" in cgroup_path or cgroup_path.endswith("/heavy-workload.slice")
    )
    if in_heavy_slice:
        return

    print(
        "[FATAL] stage1 is not running in heavy-workload.slice.\n"
        f"Detected cgroup path: {cgroup_path or '<unknown>'}\n"
        "Refusing to continue to avoid user.slice OOM storms.\n"
        "Launch with: bash tools/launch_linux_stage1_heavy_slice.sh -- <stage1 args>\n"
        f"(Emergency override only: export {ALLOW_USER_SLICE_ENV}=1)",
        file=sys.stderr,
        flush=True,
    )
    raise SystemExit(101)


def _raise_oom_score_adj(target=TARGET_OOM_SCORE_ADJ):
    """
    Make stage1 easier to kill under pressure, so desktop/session services survive.
    """
    if sys.platform != "linux":
        return

    oom_adj_file = Path("/proc/self/oom_score_adj")
    if not oom_adj_file.exists():
        return

    try:
        current = int(oom_adj_file.read_text(encoding="utf-8").strip())
    except Exception:
        return

    if current >= target:
        return

    try:
        oom_adj_file.write_text(str(target), encoding="utf-8")
        print(f"[GUARDRAIL] oom_score_adj raised from {current} to {target}.", flush=True)
    except Exception as exc:
        print(
            f"[WARN] Could not raise oom_score_adj from {current} to {target}: {exc}",
            flush=True,
        )


def _pool_initializer():
    _ensure_heavy_workload_slice()
    _raise_oom_score_adj()

def get_shard(filename, total_shards):
    h = hashlib.md5(filename.encode()).hexdigest()
    return int(h, 16) % total_shards

def process_day(args):
    """Process a single trading day: 7z extract → CSV scan → Polars ETL → Parquet."""
    day_path, hash_str, shard_index, total_shards, symbol_batch_size = args

    date_str = day_path.stem
    out_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet"
    done_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet.done"

    if done_path.exists() and out_path.exists():
        return f"[{date_str}] Skipped (Done)"

    if clear_stale_done_marker(out_path, done_path):
        print(
            f"[{date_str}] WARN: removed stale done marker {done_path.name}",
            flush=True,
        )

    if ensure_done_for_existing_parquet(out_path, done_path):
        return f"[{date_str}] Skipped (Recovered Done Marker)"

    existing_done = find_existing_done_for_date(OUTPUT_ROOT, date_str)
    if existing_done is not None:
        return f"[{date_str}] Skipped (Done: {existing_done.name})"

    print(f"[{date_str}] Starting processing (Shard {shard_index}/{total_shards})...", flush=True)

    unique_id = uuid.uuid4().hex
    # Extract directly to the 4TB NVMe disk mounted at /home to bypass ZFS IO deadlocks
    tmp_dir = Path(f"/home/zepher/framing_cache/omega_framing_{date_str}_{unique_id}")

    # Ensure clean start — kill any orphaned debris
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 7z extraction
        cmd = [SEVEN_ZIP, "x", str(day_path), f"-o{tmp_dir}", "-y"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        csvs = [str(p) for p in tmp_dir.glob("**/*.csv")]
        if not csvs:
            return f"[{date_str}] Error: No CSVs found in 7z"

        # Incremental per-symbol/par-batch writing to avoid full-day materialization blowups.
        tmp_parquet = out_path.with_suffix(".parquet.tmp")
        if tmp_parquet.exists():
            tmp_parquet.unlink(missing_ok=True)
        written_rows = write_l1_incremental_parquet(
            csv_paths=csvs,
            cfg=GLOBAL_CFG,
            tmp_parquet_path=tmp_parquet,
            symbol_batch_size=symbol_batch_size,
            build_fn=build_l1_base_ticks,
        )

        if written_rows > 0:
            # Atomic write: write to .tmp then rename
            tmp_parquet.rename(out_path)
            done_path.touch()
            return f"[{date_str}] Completed: {written_rows} rows"
        else:
            return f"[{date_str}] Error: Empty frames generated"

    except Exception as e:
        return f"[{date_str}] CRITICAL Error: {e}"
    finally:
        # ALWAYS clean up 7.6GB of extracted CSVs, even on error
        shutil.rmtree(tmp_dir, ignore_errors=True)

def main():
    ap = argparse.ArgumentParser(description="v62 Linux Framing Agent (Anti-Fragile)")
    ap.add_argument("--years", default="2023,2024,2025,2026")
    ap.add_argument("--workers", type=int, default=6,
                    help="Number of workers. workers<=1 runs single-process mode (no multiprocessing pool).")
    ap.add_argument("--shard", type=str, default="0", help="Comma-separated shard indices (e.g., '0,1,2' out of N-1)")
    ap.add_argument("--total-shards", type=int, default=4, help="Total number of shards")
    ap.add_argument(
        "--symbol-batch-size",
        type=int,
        default=64,
        help="Symbols processed per incremental write batch in Stage1.",
    )
    args = ap.parse_args()

    _ensure_heavy_workload_slice()
    _raise_oom_score_adj()

    years = args.years.split(",")
    active_shards = [int(s) for s in args.shard.split(",")]
    all_files = []

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # 【FIX 1】Compute git hash ONCE in main, pass to workers
    try:
        hash_str = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(PROJECT_ROOT),
        ).decode().strip()
    except Exception:
        hash_str = "unknown"

    print(f"Git hash: {hash_str}")
    print(f"Active Shards: {active_shards}/{args.total_shards}, Workers: {args.workers}")
    print(f"POLARS_MAX_THREADS: {os.environ.get('POLARS_MAX_THREADS', 'unset')}")
    print(f"symbol_batch_size: {args.symbol_batch_size}")

    # 【FIX 5】Bulletproof cleanup: Ensure the global framing cache on the 4TB drive is swept if the main process dies
    CACHE_DIR = "/home/zepher/framing_cache"
    def nuke_cache(*args_sig):
        print("\n[WATCHDOG] Sweeping framing_cache to prevent 4TB disk explosion...", flush=True)
        shutil.rmtree(CACHE_DIR, ignore_errors=True)
    
    atexit.register(nuke_cache)
    signal.signal(signal.SIGINT, nuke_cache)
    signal.signal(signal.SIGTERM, nuke_cache)

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
        shard_idx = get_shard(f.name, args.total_shards)
        if shard_idx in active_shards:
            tasks.append((f, hash_str, shard_idx, args.total_shards, args.symbol_batch_size))
        else:
            skipped_by_shard += 1

    print(f"Total files found: {len(all_files)}")
    print(f"Files assigned to this shard ({args.shard}/{args.total_shards}): {len(tasks)}")
    print(f"Files skipped by sharding: {skipped_by_shard}")

    if not tasks:
        print("Nothing to do for this shard. Exiting.")
        return

    if args.workers <= 1:
        # Stability path: avoid multiprocessing SemLock/spawn regressions when single-worker.
        print("[GUARDRAIL] workers<=1 detected, using single-process execution.", flush=True)
        for task in tasks:
            res = process_day(task)
            if res:
                print(res, flush=True)
    else:
        # Linux + Polars can deadlock under fork; force spawn context for worker safety.
        # maxtasksperchild=5 balances memory release and process cold-start overhead.
        ctx = get_context("spawn")
        with ctx.Pool(args.workers, maxtasksperchild=5, initializer=_pool_initializer) as p:
            for res in p.imap_unordered(process_day, tasks):
                if res:
                    print(res, flush=True)

    print("=== FRAMING COMPLETE ===")

if __name__ == "__main__":
    main()
