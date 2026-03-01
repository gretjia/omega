#!/usr/bin/env python3
"""
V63 Ticker-Aligned Sharding (Transpose ETL)
Converts daily high-frequency shards into symbol-aligned continuous parquets.
This breaks the ZFS/NFS curse by changing high-entropy blind-reads into contiguous sequential reads.
"""

import argparse
import logging
import os
import shutil
from pathlib import Path
import polars as pl
from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def _process_chunk(chunk_files: list[str], output_dir: Path, tmp_dir: Path, chunk_id: int):
    """Reads a chunk of daily files, partitions them by symbol, and appends to symbol files."""
    if not chunk_files:
        return
    
    # Load the whole chunk (e.g., 10 days of data for all symbols)
    df = pl.scan_parquet(chunk_files).collect()
    
    # Partition by symbol
    symbols = df.get_column("symbol").unique().to_list()
    for sym in symbols:
        sym_df = df.filter(pl.col("symbol") == sym)
        sym_file = output_dir / f"{sym}.parquet"
        tmp_file = tmp_dir / f"{sym}_chunk{chunk_id}.parquet"
        
        # Write temporary chunk for this symbol
        sym_df.write_parquet(tmp_file, compression="snappy")

def _merge_symbol(sym: str, tmp_dir: Path, output_dir: Path):
    """Merges all temporary chunks for a single symbol into the final contiguous file."""
    chunk_files = list(tmp_dir.glob(f"{sym}_chunk*.parquet"))
    if not chunk_files:
        return
    
    # Read all chunks, sort by time, and write the final file
    final_df = pl.scan_parquet([str(f) for f in chunk_files]).sort(["date", "time_end"]).collect()
    
    final_path = output_dir / f"{sym}.parquet"
    final_df.write_parquet(final_path, compression="snappy")
    
    # Cleanup chunks
    for f in chunk_files:
        f.unlink()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-pattern", required=True, help="Glob pattern for daily parquet files")
    parser.add_argument("--output-dir", required=True, help="Directory to save symbol-aligned parquets")
    parser.add_argument("--chunk-size", type=int, default=10, help="Number of daily files to load into memory at once")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers for chunking and merging")
    args = parser.parse_args()

    import glob
    input_files = sorted(glob.glob(args.input_pattern, recursive=True))
    if not input_files:
        logging.error(f"No files found matching {args.input_pattern}")
        return

    out_dir = Path(args.output_dir)
    tmp_dir = out_dir / "_tmp_chunks"
    
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    logging.info(f"Found {len(input_files)} daily files. Starting Ticker-Aligned Sharding...")

    # Phase 1: Chunked Scatter (Read Daily -> Write Symbol Chunks)
    chunks = [input_files[i:i + args.chunk_size] for i in range(0, len(input_files), args.chunk_size)]
    
    logging.info(f"Phase 1: Scattering into {len(chunks)} chunks using {args.workers} workers...")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = []
        for i, chunk in enumerate(chunks):
            futures.append(pool.submit(_process_chunk, chunk, out_dir, tmp_dir, i))
        for f in futures:
            f.result() # Wait and raise exceptions
            
    # Phase 2: Gather (Merge Symbol Chunks -> Final Symbol File)
    # Find all unique symbols generated in the tmp dir
    all_chunks = list(tmp_dir.glob("*.parquet"))
    symbols = set(f.name.split("_chunk")[0] for f in all_chunks)
    
    logging.info(f"Phase 2: Gathering and merging {len(symbols)} symbols...")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = []
        for sym in symbols:
            futures.append(pool.submit(_merge_symbol, sym, tmp_dir, out_dir))
        for f in futures:
            f.result()
            
    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)
    logging.info("Ticker-Aligned Sharding Complete.")

if __name__ == "__main__":
    main()
