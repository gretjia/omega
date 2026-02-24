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
import gc
import re
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

from omega_core.kernel import apply_recursive_physics


DATE_HASH_PARQUET_RE = re.compile(r"^(?P<date>\d{8})_[0-9a-f]{7}\.parquet$")


def _dedupe_l1_files_by_date(l1_files):
    """
    Keep one Base_L1 parquet per trading date.

    If mixed-hash artifacts exist for the same date, keep the newest file by
    mtime and drop older duplicates to avoid double-processing in Stage2.
    """
    per_date = {}
    passthrough = []
    duplicates = []

    for raw in l1_files:
        p = Path(raw)
        m = DATE_HASH_PARQUET_RE.match(p.name)
        if m is None:
            passthrough.append(str(p))
            continue

        date_key = m.group("date")
        current = per_date.get(date_key)
        if current is None:
            per_date[date_key] = p
            continue

        if p.stat().st_mtime > current.stat().st_mtime:
            duplicates.append(str(current))
            per_date[date_key] = p
        else:
            duplicates.append(str(p))

    selected = [str(v) for _, v in sorted(per_date.items(), key=lambda kv: kv[0])]
    selected.extend(sorted(passthrough))
    return selected, sorted(duplicates)


def _iter_complete_symbol_frames_from_parquet(l1_file):
    """
    Iterate complete symbol blocks in file order with a single parquet pass.
    Assumes Stage1 output is sorted by symbol/date/time.
    """
    import pyarrow.parquet as pq

    parquet = pq.ParquetFile(l1_file)
    current_symbol = None
    current_parts = []

    for rg_idx in range(parquet.num_row_groups):
        rg_table = parquet.read_row_group(rg_idx)
        rg_df = pl.from_arrow(rg_table)
        if rg_df.height == 0:
            continue

        # Keep row order from Stage1 sort; split row-group into contiguous symbol segments.
        for part in rg_df.partition_by("symbol", maintain_order=True):
            symbol = part.get_column("symbol")[0]

            if current_symbol is None:
                current_symbol = symbol
                current_parts = [part]
                continue

            if symbol == current_symbol:
                current_parts.append(part)
                continue

            yield pl.concat(current_parts, how="vertical_relaxed")
            current_symbol = symbol
            current_parts = [part]

    if current_parts:
        yield pl.concat(current_parts, how="vertical_relaxed")


def _run_feature_physics_batch(batch_frames, writer, tmp_parquet):
    """
    Run Stage2 feature + physics on a symbol batch and append to parquet writer.
    Returns updated writer and rows written for this batch.
    """
    import pyarrow.parquet as pq

    rows_written = 0
    batch_df = None
    input_df = None
    arrow_table = None

    try:
        input_df = pl.concat(batch_frames, how="vertical_relaxed")
        batch_df = build_l2_features_from_l1(input_df.lazy(), GLOBAL_CFG)

        if batch_df is not None and batch_df.height > 0:
            batch_df = apply_recursive_physics(batch_df, GLOBAL_CFG)

        if batch_df is not None and batch_df.height > 0:
            rows_written = batch_df.height
            arrow_table = batch_df.to_arrow()
            if writer is None:
                writer = pq.ParquetWriter(tmp_parquet, arrow_table.schema, compression="snappy")
            writer.write_table(arrow_table)
    finally:
        del arrow_table
        del batch_df
        del input_df
        gc.collect()

    return writer, rows_written


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
        # Single parquet pass path: avoid N-times re-scan from repeated lf.filter(...).collect().
        schema_names = pl.scan_parquet(l1_file).collect_schema().names()
        has_symbol = "symbol" in schema_names

        batch_size = 50
        tmp_parquet = out_path.with_suffix(".parquet.tmp")
        writer = None
        total_rows = 0

        if has_symbol:
            symbol_frames = []

            for symbol_df in _iter_complete_symbol_frames_from_parquet(l1_file):
                symbol_frames.append(symbol_df)
                if len(symbol_frames) >= batch_size:
                    writer, rows_written = _run_feature_physics_batch(
                        symbol_frames, writer, tmp_parquet
                    )
                    total_rows += rows_written
                    symbol_frames = []
                    gc.collect()

            if symbol_frames:
                writer, rows_written = _run_feature_physics_batch(
                    symbol_frames, writer, tmp_parquet
                )
                total_rows += rows_written
                symbol_frames = []
                gc.collect()
        else:
            # Rare fallback: no symbol column, process file once.
            full_df = pl.read_parquet(l1_file)
            writer, rows_written = _run_feature_physics_batch([full_df], writer, tmp_parquet)
            total_rows += rows_written
            del full_df
            gc.collect()
        
        if writer is not None:
            writer.close()
            # Atomic write completion
            tmp_parquet.rename(out_path)
            done_path.touch()
            return_msg = f"[{file_path.name}] Completed: {total_rows} rows"
        else:
            return_msg = f"[{file_path.name}] Error: Empty physics frames generated"
            
        return return_msg
            
    except Exception as e:
        return f"[{file_path.name}] CRITICAL Error: {e}"
    finally:
        # OOM Guard: Force garbage collection on both success and exception paths
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
    l1_files, dropped_dupes = _dedupe_l1_files_by_date(l1_files)

    print(f"Found {len(l1_files)} Base_L1 chunks to process.")
    if dropped_dupes:
        print(
            f"[WARN] Dropped {len(dropped_dupes)} duplicate date chunks (mixed hash).",
            flush=True,
        )

    tasks = []
    for f in l1_files:
        tasks.append({'l1_file': f, 'out_dir': str(output_path)})

    if not tasks:
        print("Nothing to do. Exiting.")
        return

    if args.workers <= 1:
        # Stability path: avoid multiprocessing SemLock/spawn regressions in single-worker mode.
        print("[GUARDRAIL] workers<=1 detected, using single-process execution.", flush=True)
        for task in tasks:
            res = process_chunk(task)
            if res:
                print(res, flush=True)
    else:
        # Use spawn for safety across different OS
        ctx = get_context("spawn")
        with ctx.Pool(args.workers, maxtasksperchild=10) as p:
            for res in p.imap_unordered(process_chunk, tasks):
                if res:
                    print(res, flush=True)

    print("=== STAGE 2 PHYSICS COMPUTE COMPLETE ===")

if __name__ == "__main__":
    main()
