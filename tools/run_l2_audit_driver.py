"""
run_l2_audit_driver.py

Orchestrates the Level-2 (v3) Audit by:
1. Batch-extracting .7z archives to a temporary stage directory.
2. Running the v3 Kernel (Polars) on extracted CSVs.
3. Saving intermediate frame results (Parquet).
4. Aggregating metrics for the Audit Report.

Features:
- Resumable (skips processed archives).
- Disk-space aware (extracts one batch, processes, then deletes).
- Config-driven (uses config.L2PipelineConfig).
"""

import sys
import os
from pathlib import Path
import subprocess
import json
import time
import argparse
import polars as pl
import multiprocessing as mp
import shutil
import random
from typing import Dict, Iterator, List, Optional, Tuple

import psutil

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config import L2PipelineConfig
from omega_core.kernel import run_l2_kernel
from omega_core.trainer import evaluate_frames, evaluate_dod, write_audit_report
from tools.level2_batch_extract import _find_7z_exe

# Use a dynamic stage root that supports per-process isolation
if os.name == 'nt':
    # Prefer D: to avoid filling the system disk; fallback to C: when D: is unavailable.
    DEFAULT_STAGE_ROOT = Path("D:/Omega_level2_stage") if Path("D:/").exists() else Path("C:/Omega_level2_stage")
else:
    # On Mac/Linux, use a local temp directory in user home to ensure write access and space
    DEFAULT_STAGE_ROOT = Path(os.path.expanduser("~/omega_level2_stage"))
OUTPUT_ROOT = Path("./data/level2_frames")


def resolve_7z_exe(user_path: str = "") -> str:
    """
    Cross-platform 7z resolver.
    """
    if user_path:
        p = Path(user_path)
        if p.exists():
            return str(p)
        raise FileNotFoundError(f"7z executable not found: {user_path}")

    env = os.environ.get("SEVEN_ZIP_EXE", "")
    if env:
        p = Path(env)
        if p.exists():
            return str(p)

    if os.name == "nt":
        return str(_find_7z_exe(None))

    for cmd in ("7zz", "7z", "7za"):
        found = shutil.which(cmd)
        if found:
            return found

    raise FileNotFoundError("7z executable not found. Install 7zz/7z or pass --seven-zip.")


def check_memory_safe(threshold=85.0, sleep_sec=10):
    """
    Blocks execution if memory usage exceeds threshold.
    """
    while True:
        mem = psutil.virtual_memory()
        if mem.percent < threshold:
            break
        print(f"[Driver] High Memory Warning: {mem.percent}% used. Pausing for {sleep_sec}s...")
        time.sleep(sleep_sec)


def write_status_json(path: str, payload: dict):
    if not path:
        return
    def sanitize(v):
        if isinstance(v, dict):
            return {k: sanitize(x) for k, x in v.items()}
        if isinstance(v, list):
            return [sanitize(x) for x in v]
        if isinstance(v, float):
            if not (float("-inf") < v < float("inf")):
                return None
            return v
        return v
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(sanitize(payload), f, ensure_ascii=False, indent=2)
    tmp.replace(p)


def _sample_paths(paths: List[Path], keep: int, seed: int) -> List[Path]:
    if keep <= 0 or len(paths) <= keep:
        return list(paths)
    rng = random.Random(int(seed))
    return sorted(rng.sample(paths, keep))


def _iter_csv_files(root: Path) -> Iterator[Path]:
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith(".csv"):
                yield Path(dirpath) / name


def _collect_report_frames_safe(
    parquet_files: List[Path],
    *,
    rows_per_file: int,
    memory_threshold: float,
) -> pl.DataFrame:
    """
    Collect a bounded dataframe for report generation.
    If rows_per_file > 0, each file contributes at most that many rows.
    """
    if not parquet_files:
        return pl.DataFrame()

    if rows_per_file > 0:
        chunks = []
        for p in parquet_files:
            check_memory_safe(threshold=float(memory_threshold))
            df = pl.scan_parquet(str(p)).head(int(rows_per_file)).collect()
            if df.height > 0:
                chunks.append(df)
        if not chunks:
            return pl.DataFrame()
        return pl.concat(chunks, how="vertical")

    # Full-mode path (explicit)
    check_memory_safe(threshold=float(memory_threshold))
    return pl.scan_parquet([str(p) for p in parquet_files]).collect()

def load_processed_archives(state_file: Path) -> set:
    if not state_file.exists():
        return set()
    processed = set()
    with open(state_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec["status"] == "done":
                    processed.add(rec["archive_path"])
            except:
                pass
    return processed

def mark_archive_done(archive_path: str, metrics: dict, state_file: Path):
    rec = {
        "ts": time.time(),
        "archive_path": str(archive_path),
        "status": "done",
        "metrics": metrics
    }
    # Simple file lock for concurrency safety or just atomic append (usually safe for small lines on OS)
    # For robustness in MP, we should use a lock, but Python's append is atomic enough for logs.
    try:
        with open(state_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception as e:
        print(f"Warning: Failed to write state: {e}")

def process_single_archive(
    archive_path: Path,
    cfg: L2PipelineConfig,
    worker_id: int,
    output_dir: str,
    copy_to_local: bool,
    seven_zip_exe: str,
    seven_zip_threads: int,
    stage_root: Path,
    cleanup_stage: bool,
    io_semaphore: Optional[mp.Semaphore],
    extract_csv_only: bool,
) -> Dict[str, float]:
    """
    Worker function: Extract -> Process -> Cleanup for one archive.
    Returns per-archive execution stats.
    """
    # 1. Setup isolated stage dir
    stage_dir = stage_root / f"worker_{worker_id}"
    seven_zip = seven_zip_exe
    
    if stage_dir.exists():
        shutil.rmtree(stage_dir, ignore_errors=True)
    stage_dir.mkdir(parents=True, exist_ok=True)
    
    target_archive = archive_path
    stats: Dict[str, float] = {
        "n_files": 0.0,
        "copy_sec": 0.0,
        "extract_sec": 0.0,
        "kernel_sec": 0.0,
        "write_sec": 0.0,
        "io_wait_sec": 0.0,
        "csv_total": 0.0,
        "csv_quote": 0.0,
    }

    try:
        io_acquired = False
        if io_semaphore is not None:
            wait_started_at = time.time()
            io_semaphore.acquire()
            io_acquired = True
            stats["io_wait_sec"] += max(0.0, time.time() - wait_started_at)

        try:
            # Optional: Copy to local first (for network drives).
            if copy_to_local:
                copy_started_at = time.time()
                local_archive = stage_dir / archive_path.name
                try:
                    # Keep staging cheap: metadata preservation is unnecessary for temp files.
                    shutil.copyfile(archive_path, local_archive)
                    target_archive = local_archive
                except Exception as e:
                    # Keep pipeline moving: fallback to original archive path.
                    print(f"[Worker-{worker_id}] Copy failed for {archive_path.name}: {e}. Fallback to source.")
                    target_archive = archive_path
                finally:
                    stats["copy_sec"] += max(0.0, time.time() - copy_started_at)

            # 2. Extract
            extract_started_at = time.time()
            seven_zip_threads = max(1, int(seven_zip_threads))
            cmd = [
                seven_zip,
                "x",
                str(target_archive),
                f"-o{stage_dir}",
                "-y",
                f"-mmt={seven_zip_threads}",
                "-bso0",
                "-bsp0",
            ]
            if extract_csv_only:
                cmd.extend(["-ir!*.csv", "-ir!*.CSV"])
            ret = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            stats["extract_sec"] += max(0.0, time.time() - extract_started_at)
            if ret.returncode != 0:
                print(f"[Worker-{worker_id}] Extraction failed for {target_archive.name}: {ret.stderr.decode()}")
                return stats
        finally:
            if io_acquired:
                io_semaphore.release()

        # 3. Process
        processed_count = 0
        for p in _iter_csv_files(stage_dir):
            stats["csv_total"] += 1.0
            if "行情" not in p.name and "Quote" not in p.name:
                continue
            stats["csv_quote"] += 1.0
                
            try:
                kernel_started_at = time.time()
                frames, signals = run_l2_kernel(str(p), cfg)
                stats["kernel_sec"] += max(0.0, time.time() - kernel_started_at)
                
                if frames.height > 0:
                    symbol = p.parent.name
                    date_str = p.parent.parent.name 
                    if not date_str.isdigit() and "date" in frames.columns:
                         date_str = str(frames["date"][0])
                    
                    out_name = f"{date_str}_{symbol}.parquet"
                    out_path = Path(output_dir) / out_name
                    # Atomic Write: Write to .tmp first, then rename.
                    # This guarantees that if a .parquet file exists, it is complete.
                    write_started_at = time.time()
                    tmp_path = out_path.with_suffix(".tmp")
                    frames.write_parquet(tmp_path)
                    tmp_path.replace(out_path)
                    stats["write_sec"] += max(0.0, time.time() - write_started_at)
                    processed_count += 1
                    
            except Exception:
                # Keep worker robust on one-file failures inside archive.
                pass
        stats["n_files"] = float(processed_count)
        return stats
    finally:
        if cleanup_stage:
            shutil.rmtree(stage_dir, ignore_errors=True)

def worker_entry(
    task_queue: mp.Queue,
    result_queue: mp.Queue,
    cfg: L2PipelineConfig,
    worker_id: int,
    output_dir: str,
    copy_to_local: bool,
    seven_zip_exe: str,
    seven_zip_threads: int,
    stage_root: str,
    cleanup_stage: bool,
    io_semaphore: Optional[mp.Semaphore],
    extract_csv_only: bool,
):
    """
    Consumer loop.
    """
    while True:
        task = task_queue.get()
        if task is None:
            break
        
        archive_path = Path(task)
        try:
            n = process_single_archive(
                archive_path,
                cfg,
                worker_id,
                output_dir,
                copy_to_local,
                seven_zip_exe,
                seven_zip_threads,
                Path(stage_root),
                cleanup_stage,
                io_semaphore,
                extract_csv_only,
            )
            result_queue.put((str(archive_path), n))
        except Exception as e:
            print(f"[Worker-{worker_id}] Fatal error on {archive_path}: {e}")
            result_queue.put((str(archive_path), {"n_files": 0.0, "worker_error": 1.0}))

def main():
    mp.freeze_support() # Windows support
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=1, help="Max archives to process")
    ap.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    ap.add_argument("--report", default="./audit/level2_v3_audit_report.md")
    ap.add_argument("--year", type=str, default="", help="Filter by year (e.g. 2023)")
    ap.add_argument("--output-dir", default=str(OUTPUT_ROOT), help="Output directory for parquets")
    copy_group = ap.add_mutually_exclusive_group()
    copy_group.add_argument("--copy-to-local", dest="copy_to_local", action="store_true", help="Copy archive to local stage before extracting (network opt)")
    copy_group.add_argument("--no-copy-to-local", dest="copy_to_local", action="store_false", help="Disable local archive copy and read from source directly")
    ap.add_argument("--skip-report", action="store_true", help="Skip generating aggregate report (avoids OOM on large datasets)")
    ap.add_argument("--seven-zip", type=str, default="", help="Optional explicit path to 7z/7zz executable")
    ap.add_argument("--seven-zip-threads", type=int, default=1, help="Threads used by 7z per worker process")
    ap.add_argument("--memory-threshold", type=float, default=88.0, help="Pause when memory usage exceeds this percentage")
    ap.add_argument("--status-json", type=str, default="", help="Optional JSON status output path")
    ap.add_argument("--stage-dir", type=str, default=str(DEFAULT_STAGE_ROOT), help="Local staging root (Windows: C: recommended)")
    ap.add_argument("--io-slots", type=int, default=0, help="Max concurrent frame IO workers (copy+extract). <=0 means auto")
    extract_group = ap.add_mutually_exclusive_group()
    extract_group.add_argument("--extract-csv-only", dest="extract_csv_only", action="store_true", help="Ask 7z to extract csv entries only")
    extract_group.add_argument("--extract-all", dest="extract_csv_only", action="store_false", help="Extract all archive entries")
    ap.add_argument("--no-cleanup-stage", action="store_true", help="Keep staged worker dirs for debugging")
    ap.add_argument("--report-full", action="store_true", help="Use full wildcard collect() for report (memory-heavy; avoid on large datasets)")
    ap.add_argument("--report-sample-files", type=int, default=200, help="Max parquet files used for report when not in --report-full mode")
    ap.add_argument("--report-rows-per-file", type=int, default=2000, help="Rows sampled per parquet for report when not in --report-full mode")
    ap.add_argument("--report-sample-seed", type=int, default=20260208, help="Sampling seed for bounded report mode")
    ap.add_argument("--report-fail-fatal", action="store_true", help="If set, report failure marks frame stage failed")
    ap.set_defaults(copy_to_local=True)
    ap.set_defaults(extract_csv_only=True)
    args = ap.parse_args()

    cfg = L2PipelineConfig()
    seven_zip_exe = resolve_7z_exe(args.seven_zip)
    seven_zip_threads = max(1, int(args.seven_zip_threads))
    io_slots = int(args.io_slots)
    if io_slots <= 0:
        io_slots = max(1, min(8, max(1, int(args.workers) // 2)))
    stage_root = Path(args.stage_dir)
    stage_root.mkdir(parents=True, exist_ok=True)
    cleanup_stage = not bool(args.no_cleanup_stage)
    
    # Derive state file from output dir name to support multi-machine independence
    output_dir_path = Path(args.output_dir)
    # e.g. data/level2_frames_win2023 -> data/level2_frames/_audit_state_win2023.jsonl
    # or just put it INSIDE the output dir.
    # Let's put it inside the output dir for full encapsulation.
    state_file = output_dir_path / "_audit_state.jsonl"
    
    # Ensure output dir exists
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Collect Archives
    root = Path(cfg.io.input_root)
    all_archives = sorted(list(root.rglob("*.7z")))
    
    # Apply year filter if specified
    if args.year:
        all_archives = [a for a in all_archives if args.year in str(a)]
    
    processed = load_processed_archives(state_file)
    
    todo = [a for a in all_archives if str(a) not in processed]
    
    # Apply limit
    if args.limit > 0:
        todo = todo[:args.limit]
        
    print(
        f"[Driver] Found {len(all_archives)} archives (year={args.year}), {len(processed)} done. "
        f"Processing {len(todo)} with {args.workers} workers. CopyToLocal={args.copy_to_local} "
        f"StageDir={stage_root} CleanupStage={cleanup_stage} SevenZipThreads={seven_zip_threads} "
        f"IOSlots={io_slots} ExtractCsvOnly={bool(args.extract_csv_only)}"
    )
    print(f"[Driver] State file: {state_file}")
    write_status_json(
        args.status_json,
        {
            "stage": "frame",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "running",
            "archives_total": len(all_archives),
            "archives_done_historical": len(processed),
            "archives_run_now": len(todo),
            "workers": args.workers,
            "output_dir": str(output_dir_path),
            "state_file": str(state_file),
            "copy_to_local": bool(args.copy_to_local),
            "seven_zip_threads": seven_zip_threads,
            "io_slots": io_slots,
            "extract_csv_only": bool(args.extract_csv_only),
            "stage_dir": str(stage_root),
            "cleanup_stage": cleanup_stage,
        },
    )
    
    if not todo:
        print("[Driver] Nothing to do.")
        write_status_json(
            args.status_json,
            {
                "stage": "frame",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "completed",
                "archives_total": len(all_archives),
                "archives_done_historical": len(processed),
                "archives_run_now": 0,
                "workers": args.workers,
                "output_dir": str(output_dir_path),
                "state_file": str(state_file),
                "copy_to_local": bool(args.copy_to_local),
                "seven_zip_threads": seven_zip_threads,
                "io_slots": io_slots,
                "extract_csv_only": bool(args.extract_csv_only),
                "stage_dir": str(stage_root),
                "cleanup_stage": cleanup_stage,
                "report_skipped": True,
            },
        )
        return

    # Update global OUTPUT_ROOT based on arg (dirty hack for multiprocessing pickling? No, MP uses fork/spawn)
    # Actually, we need to pass output dir to workers or update the global before forking.
    # On Windows (spawn), globals might reset. We should pass output_dir to worker.
    # Let's update the global here, but we also need to pass it or ensure it's set in worker.
    # A cleaner way is to pass it in worker_entry -> process_single_archive.
    
    # 2. Start Workers
    task_queue = mp.Queue()
    result_queue = mp.Queue()
    io_semaphore = mp.Semaphore(io_slots)
    
    workers = []
    for i in range(args.workers):
        p = mp.Process(
            target=worker_entry,
            args=(
                task_queue,
                result_queue,
                cfg,
                i,
                args.output_dir,
                args.copy_to_local,
                seven_zip_exe,
                seven_zip_threads,
                str(stage_root),
                cleanup_stage,
                io_semaphore,
                bool(args.extract_csv_only),
            ),
        )
        p.start()
        workers.append(p)
        
    # 3. Feed Tasks
    for a in todo:
        check_memory_safe(threshold=float(args.memory_threshold))
        task_queue.put(str(a))
        
    # 4. Collect Results
    run_started_at = time.time()
    completed = 0
    total_files_output = 0
    timing_totals = {
        "copy_sec": 0.0,
        "extract_sec": 0.0,
        "kernel_sec": 0.0,
        "write_sec": 0.0,
        "io_wait_sec": 0.0,
        "csv_total": 0.0,
        "csv_quote": 0.0,
        "worker_error": 0.0,
    }
    while completed < len(todo):
        archive_path, stats_payload = result_queue.get()
        if isinstance(stats_payload, dict):
            n_files = int(stats_payload.get("n_files", 0.0))
            for key in timing_totals.keys():
                timing_totals[key] += float(stats_payload.get(key, 0.0))
        else:
            # Backward-compatible fallback
            n_files = int(stats_payload)
        # Fix: Only mark done if successfully processed at least one file.
        # This prevents marking archives as "done" when extraction failed (n_files=0).
        if n_files > 0:
            mark_archive_done(
                archive_path,
                {
                    "n_files": n_files,
                    "timing": {
                        "copy_sec": float(stats_payload.get("copy_sec", 0.0)) if isinstance(stats_payload, dict) else 0.0,
                        "extract_sec": float(stats_payload.get("extract_sec", 0.0)) if isinstance(stats_payload, dict) else 0.0,
                        "kernel_sec": float(stats_payload.get("kernel_sec", 0.0)) if isinstance(stats_payload, dict) else 0.0,
                        "write_sec": float(stats_payload.get("write_sec", 0.0)) if isinstance(stats_payload, dict) else 0.0,
                        "io_wait_sec": float(stats_payload.get("io_wait_sec", 0.0)) if isinstance(stats_payload, dict) else 0.0,
                    },
                    "csv": {
                        "total": int(stats_payload.get("csv_total", 0.0)) if isinstance(stats_payload, dict) else 0,
                        "quote": int(stats_payload.get("csv_quote", 0.0)) if isinstance(stats_payload, dict) else 0,
                    },
                },
                state_file,
            )
            total_files_output += int(n_files)
        else:
            print(f"[Driver] Warning: Archive {Path(archive_path).name} yielded 0 files. NOT marking as done.")
            
        completed += 1
        elapsed = max(0.0, time.time() - run_started_at)
        archives_per_hour = (completed * 3600.0 / elapsed) if elapsed > 0 else 0.0
        print(
            f"[Driver] ({completed}/{len(todo)}) Finished {Path(archive_path).name}: {n_files} files | "
            f"speed={archives_per_hour:.1f} archives/hour",
            flush=True,
        )
        write_status_json(
            args.status_json,
            {
                "stage": "frame",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "running",
                "archives_total": len(all_archives),
                "archives_done_historical": len(processed),
                "archives_run_now": len(todo),
                "archives_completed_in_run": completed,
                "archives_remaining_in_run": max(len(todo) - completed, 0),
                "parquet_files_written_in_run": total_files_output,
                "timing_totals": {
                    "copy_sec": timing_totals["copy_sec"],
                    "extract_sec": timing_totals["extract_sec"],
                    "kernel_sec": timing_totals["kernel_sec"],
                    "write_sec": timing_totals["write_sec"],
                    "io_wait_sec": timing_totals["io_wait_sec"],
                },
                "csv_counts": {
                    "csv_total": int(timing_totals["csv_total"]),
                    "csv_quote": int(timing_totals["csv_quote"]),
                },
                "worker_error_count": int(timing_totals["worker_error"]),
                "archives_per_hour": archives_per_hour,
                "workers": args.workers,
                "output_dir": str(output_dir_path),
                "state_file": str(state_file),
                "copy_to_local": bool(args.copy_to_local),
                "seven_zip_threads": seven_zip_threads,
                "io_slots": io_slots,
                "extract_csv_only": bool(args.extract_csv_only),
                "stage_dir": str(stage_root),
                "cleanup_stage": cleanup_stage,
            },
        )
        
    # 5. Stop Workers
    for _ in workers:
        task_queue.put(None)
    for p in workers:
        p.join()
    run_elapsed = max(0.0, time.time() - run_started_at)
    final_archives_per_hour = (completed * 3600.0 / run_elapsed) if run_elapsed > 0 else 0.0
        
    # 6. Generate Aggregate Report
    if args.skip_report:
        print("[Driver] Skipping Aggregate Report generation (--skip-report enabled).")
        write_status_json(
            args.status_json,
            {
                "stage": "frame",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "completed",
                "report_skipped": True,
                "archives_total": len(all_archives),
                "archives_done_historical": len(processed),
                "archives_run_now": len(todo),
                "archives_completed_in_run": completed,
                "parquet_files_written_in_run": total_files_output,
                "timing_totals": {
                    "copy_sec": timing_totals["copy_sec"],
                    "extract_sec": timing_totals["extract_sec"],
                    "kernel_sec": timing_totals["kernel_sec"],
                    "write_sec": timing_totals["write_sec"],
                    "io_wait_sec": timing_totals["io_wait_sec"],
                },
                "run_elapsed_sec": run_elapsed,
                "archives_per_hour": final_archives_per_hour,
                "workers": args.workers,
                "output_dir": str(output_dir_path),
                "state_file": str(state_file),
                "copy_to_local": bool(args.copy_to_local),
                "seven_zip_threads": seven_zip_threads,
                "io_slots": io_slots,
                "extract_csv_only": bool(args.extract_csv_only),
                "stage_dir": str(stage_root),
                "cleanup_stage": cleanup_stage,
            },
        )
        return

    print("[Driver] Generating Aggregate Report...")
    try:
        pq_files = list(output_dir_path.rglob("*.parquet"))
        if not pq_files:
            print("[Driver] No parquet files found for report.")
            write_status_json(
                args.status_json,
                {
                    "stage": "frame",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "completed",
                    "report_skipped": True,
                    "report_empty_input": True,
                    "archives_total": len(all_archives),
                    "archives_done_historical": len(processed),
                    "archives_run_now": len(todo),
                    "archives_completed_in_run": completed,
                    "parquet_files_written_in_run": total_files_output,
                    "timing_totals": {
                        "copy_sec": timing_totals["copy_sec"],
                        "extract_sec": timing_totals["extract_sec"],
                        "kernel_sec": timing_totals["kernel_sec"],
                        "write_sec": timing_totals["write_sec"],
                        "io_wait_sec": timing_totals["io_wait_sec"],
                    },
                    "run_elapsed_sec": run_elapsed,
                    "archives_per_hour": final_archives_per_hour,
                    "workers": args.workers,
                    "output_dir": str(output_dir_path),
                    "state_file": str(state_file),
                    "copy_to_local": bool(args.copy_to_local),
                    "seven_zip_threads": seven_zip_threads,
                    "io_slots": io_slots,
                    "extract_csv_only": bool(args.extract_csv_only),
                    "stage_dir": str(stage_root),
                    "cleanup_stage": cleanup_stage,
                },
            )
            return

        report_mode = "full" if args.report_full else "sampled"
        if args.report_full:
            report_files = pq_files
            rows_per_file = 0
        else:
            report_files = _sample_paths(
                pq_files,
                max(1, int(args.report_sample_files)),
                int(args.report_sample_seed),
            )
            rows_per_file = max(1, int(args.report_rows_per_file))

        print(
            f"[Driver] Report mode={report_mode}, files={len(report_files)}/{len(pq_files)}, "
            f"rows_per_file={'full' if rows_per_file <= 0 else rows_per_file}"
        )
        frames = _collect_report_frames_safe(
            report_files,
            rows_per_file=rows_per_file,
            memory_threshold=float(args.memory_threshold),
        )
        if frames.height == 0:
            raise RuntimeError("report frame sample is empty")
        
        metrics = evaluate_frames(frames, cfg)
        metrics["DoD_pass"] = float(1.0 if evaluate_dod(metrics, cfg) else 0.0)
        
        write_audit_report(metrics, cfg, args.report)
        print(f"[Driver] Report written to {args.report}")
        print(metrics)
        write_status_json(
            args.status_json,
            {
                "stage": "frame",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "completed",
                "report_skipped": False,
                "report_mode": report_mode,
                "report_files_total": len(pq_files),
                "report_files_used": len(report_files),
                "report_rows_per_file": rows_per_file,
                "archives_total": len(all_archives),
                "archives_done_historical": len(processed),
                "archives_run_now": len(todo),
                "archives_completed_in_run": completed,
                "parquet_files_written_in_run": total_files_output,
                "timing_totals": {
                    "copy_sec": timing_totals["copy_sec"],
                    "extract_sec": timing_totals["extract_sec"],
                    "kernel_sec": timing_totals["kernel_sec"],
                    "write_sec": timing_totals["write_sec"],
                    "io_wait_sec": timing_totals["io_wait_sec"],
                },
                "run_elapsed_sec": run_elapsed,
                "archives_per_hour": final_archives_per_hour,
                "workers": args.workers,
                "output_dir": str(output_dir_path),
                "state_file": str(state_file),
                "metrics": metrics,
                "copy_to_local": bool(args.copy_to_local),
                "seven_zip_threads": seven_zip_threads,
                "io_slots": io_slots,
                "extract_csv_only": bool(args.extract_csv_only),
                "stage_dir": str(stage_root),
                "cleanup_stage": cleanup_stage,
            },
        )
        
    except Exception as e:
        print(f"[Driver] Report generation failed: {e}")
        if args.report_fail_fatal:
            final_status = "failed"
            report_failed_fatal = True
        else:
            final_status = "completed"
            report_failed_fatal = False
        write_status_json(
            args.status_json,
            {
                "stage": "frame",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": final_status,
                "error": str(e),
                "report_failed": True,
                "report_failed_fatal": report_failed_fatal,
                "archives_total": len(all_archives),
                "archives_done_historical": len(processed),
                "archives_run_now": len(todo),
                "archives_completed_in_run": completed,
                "parquet_files_written_in_run": total_files_output,
                "timing_totals": {
                    "copy_sec": timing_totals["copy_sec"],
                    "extract_sec": timing_totals["extract_sec"],
                    "kernel_sec": timing_totals["kernel_sec"],
                    "write_sec": timing_totals["write_sec"],
                    "io_wait_sec": timing_totals["io_wait_sec"],
                },
                "run_elapsed_sec": run_elapsed,
                "archives_per_hour": final_archives_per_hour,
                "workers": args.workers,
                "output_dir": str(output_dir_path),
                "state_file": str(state_file),
                "copy_to_local": bool(args.copy_to_local),
                "seven_zip_threads": seven_zip_threads,
                "io_slots": io_slots,
                "extract_csv_only": bool(args.extract_csv_only),
                "stage_dir": str(stage_root),
                "cleanup_stage": cleanup_stage,
            },
        )

if __name__ == "__main__":
    main()
