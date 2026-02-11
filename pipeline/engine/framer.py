import os
import glob
import time
import shutil
import subprocess
import concurrent.futures
from typing import List
from pathlib import Path
import polars as pl

from pipeline.config.hardware import HardwareProfile
from pipeline.interfaces.math_core import IMathCore
from omega_core.omega_etl import build_l2_frames
from omega_core.kernel import apply_recursive_physics
from config import load_l2_pipeline_config

def _process_single_stock(file_paths: List[str], cfg) -> pl.DataFrame:
    """
    Worker task to process a single stock (all slices).
    Runs ETL -> Physics -> Metadata.
    """
    try:
        # Filter for Quotes files (Snapshot Level 2)
        quote_paths = []
        # Required column: Bid Price 1 (e.g., "申买价1")
        required_col = f"{cfg.mapping.bid_price_prefix}1"
        
        for f in file_paths:
            try:
                # Check schema (first few bytes)
                # Note: Assuming config encoding is correct (e.g. gb18030)
                schema = pl.read_csv(f, n_rows=0, encoding=cfg.io.csv_encoding).columns
                if required_col in schema:
                    quote_paths.append(f)
            except Exception:
                continue
        
        if not quote_paths:
            # No valid L2 Quote file found in this group.
            return None

        # 1. ETL (Framing)
        # build_l2_frames now accepts a list of paths (via scan_l2_quotes recursion)
        df = build_l2_frames(quote_paths, cfg)
        if df.height == 0:
            return None
            
        # ENSURE TIME ORDER for Physics!
        # group_by() does not guarantee order of groups.
        df = df.sort("bucket_id")

        # 2. Core Processing (Math) - Per Asset Physics
        df = apply_recursive_physics(df, cfg)
        
        # 3. Enrich with Symbol
        # Take symbol from first file
        first_path = file_paths[0]
        symbol = Path(first_path).parent.name
        
        # If symbol looks like a date (e.g. nested date folders), try grandparent
        if symbol.isdigit() and len(symbol) == 8:
             symbol = Path(first_path).parent.parent.name
             
        df = df.with_columns(pl.lit(symbol).alias("symbol"))
        
        return df
    except Exception as e:
        # Minimal error reporting to avoid spamming the main process
        print(f"[Error] {file_paths[0] if file_paths else '?'}: {e}")
        import traceback
        traceback.print_exc()
        return None

class Framer:
    def __init__(self, hardware: HardwareProfile, core: IMathCore, logger=None):
        self.hw = hardware
        self.core = core
        self.logger = logger or print
        self.seven_zip = self._resolve_7z_exe()

    def run(self, year_filter: str = None, limit: int = 0):
        """
        Main entry point for the Framing Stage.
        """
        self.logger(f"--- [Framer] Starting (Multi-Process V5) ---")
        self.logger(f"Source: {self.hw.storage.source_root}")
        self.logger(f"Stage : {self.hw.storage.stage_root}")
        self.logger(f"Output: {self.hw.storage.output_root}")
        self.logger(f"Workers: {self.hw.compute.framing_workers}")
        
        # Ensure directories
        os.makedirs(self.hw.storage.stage_root, exist_ok=True)
        os.makedirs(self.hw.storage.output_root, exist_ok=True)

        # 1. Discovery
        archives = self._scan_archives(year_filter)
        self.logger(f"Found {len(archives)} archives.")
        
        if limit > 0:
            archives = archives[:limit]
            self.logger(f"Limiting to {limit} archives for smoke test.")

        # 2. Execution
        results = []
        for archive in archives:
            try:
                res = self._process_archive(archive)
                if res:
                    results.append(res)
            except Exception as e:
                self.logger(f"[Error] Failed to process {archive}: {e}")
                import traceback
                self.logger(traceback.format_exc())

        self.logger(f"--- [Framer] Complete. Processed {len(results)} archives. ---")

    def _scan_archives(self, year_filter: str) -> List[str]:
        if not os.path.exists(self.hw.storage.source_root):
            self.logger(f"[Warn] Source root does not exist: {self.hw.storage.source_root}")
            return []
            
        pattern = "**/*.7z"
        if year_filter:
            pattern = f"**/*{year_filter}*/**/*.7z"
            
        return sorted(list(glob.glob(os.path.join(self.hw.storage.source_root, pattern), recursive=True)))

    def _resolve_7z_exe(self) -> str:
        env = os.environ.get("SEVEN_ZIP_EXE")
        if env and os.path.exists(env):
            return env
        
        candidates = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return "7z" # Fallback to path

    def _process_archive(self, archive_path: str) -> str:
        filename = os.path.basename(archive_path)
        date_str = filename.split(".")[0]
        output_path = os.path.join(self.hw.storage.output_root, f"{date_str}.parquet")
        
        # Check if already processed
        if os.path.exists(output_path):
            self.logger(f"[Skip] {filename} already exists at {output_path}")
            return filename

        self.logger(f"[Job] Processing {filename}...")
        start_time = time.time()
        
        # 1. Staging (Extraction)
        temp_stage = os.path.join(self.hw.storage.stage_root, date_str)
        os.makedirs(temp_stage, exist_ok=True)
        
        try:
            cmd = [self.seven_zip, "x", archive_path, f"-o{temp_stage}", "-y"]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Find ALL CSV files
            csv_files = glob.glob(os.path.join(temp_stage, "**/*.csv"), recursive=True)
            if not csv_files:
                 # Try Parquet if CSV not found
                 csv_files = glob.glob(os.path.join(temp_stage, "**/*.parquet"), recursive=True)
                 
            if not csv_files:
                self.logger(f"[Warn] No data files found in {archive_path}")
                return None
            
            self.logger(f"       Found {len(csv_files)} files. Grouping by symbol...")

            # Group by Symbol
            symbol_map = {}
            for f in csv_files:
                p = Path(f)
                symbol = p.parent.name
                if symbol.isdigit() and len(symbol) == 8:
                     symbol = p.parent.parent.name
                if symbol not in symbol_map:
                    symbol_map[symbol] = []
                symbol_map[symbol].append(str(p))

            self.logger(f"       Processing {len(symbol_map)} symbols...")

            # 2. Parallel Processing (Map-Reduce)
            l2_cfg = load_l2_pipeline_config()
            
            processed_dfs = []
            workers = int(self.hw.compute.framing_workers)
            
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
                # Submit all tasks (list of files per symbol)
                futures = {executor.submit(_process_single_stock, files, l2_cfg): sym for sym, files in symbol_map.items()}
                
                # Collect results
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    if res is not None:
                        processed_dfs.append(res)
            
            if not processed_dfs:
                self.logger(f"[Warn] All files failed processing for {date_str}")
                return None

            # 3. Concatenation
            self.logger(f"       Concatenating {len(processed_dfs)} frames...")
            full_df = pl.concat(processed_dfs)
            
            # 4. Output
            full_df.write_parquet(output_path)
            duration = time.time() - start_time
            self.logger(f"[Done] {filename} -> {output_path} ({full_df.height} rows, {duration:.1f}s)")
            
        finally:
            # Cleanup stage
            if os.path.exists(temp_stage):
                try:
                    shutil.rmtree(temp_stage)
                except Exception as e:
                    self.logger(f"[Warn] Failed to cleanup stage {temp_stage}: {e}")
                
        return filename