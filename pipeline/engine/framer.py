import os
import glob
import time
import shutil
import subprocess
import concurrent.futures
from typing import List, Dict, Tuple
from pathlib import Path
import polars as pl
import json
import hashlib
from pipeline.config.hardware import HardwareProfile
from pipeline.interfaces.math_core import IMathCore
from omega_core.omega_etl import build_l2_frames
from omega_core.kernel import apply_recursive_physics
from config import load_l2_pipeline_config

def _validate_is_quote_file(file_path: str, cfg) -> bool:
    """
    Validates if a file is a Quote (Snapshot) file and not a Tick file.
    Checks for the existence of Bid Price 1 column.
    """
    required_col = f"{cfg.mapping.bid_price_prefix}1"
    try:
        with open(file_path, 'rb') as f:
            # Read first 4KB to cover header even with weird encoding
            chunk = f.read(4096)
            header = chunk.decode(cfg.io.csv_encoding, errors='ignore').split('\n')[0]
            return required_col in header
    except Exception:
        return False

def _process_single_stock(symbol: str, file_paths: List[str], cfg) -> pl.DataFrame:
    """
    Worker task to process a single stock (all slices).
    Runs ETL -> Physics -> Metadata.
    """
    try:
        # 1. Schema Validation (Filter Ticks)
        quote_paths = [f for f in file_paths if _validate_is_quote_file(f, cfg)]
        
        if not quote_paths:
            # print(f"  [Skip] {symbol}: No valid quote files found.", flush=True)
            return None

        # 2. ETL (Framing)
        # build_l2_frames handles loading CSVs and mapping columns
        df = build_l2_frames(quote_paths, cfg)
        if df.height == 0:
            return None
            
        # 3. Causal Sorting (CRITICAL for v5.2 Physics)
        # Physics state (adaptive_y) depends on strict time ordering.
        # Merging slices often disrupts order.
        df = df.sort("bucket_id")

        # 4. Core Processing (Math) - Per Asset Physics
        # This applies SRL, Epiplexity, and Adaptive Y
        df = apply_recursive_physics(df, cfg)
        
        # 5. Enrich with Symbol
        df = df.with_columns(pl.lit(str(symbol)).cast(pl.Utf8).alias("symbol"))
        
        return df
    except Exception as e:
        print(f"  [Error] {symbol}: {e}", flush=True)
        return None

def _process_stock_chunk(chunk: List[Tuple[str, List[str]]], cfg) -> List[pl.DataFrame]:
    """
    Processes a batch of symbols to reduce IPC overhead.
    """
    results = []
    for sym, file_paths in chunk:
        res = _process_single_stock(sym, file_paths, cfg)
        if res is not None:
            results.append(res)
    return results

class Framer:
    def __init__(self, hardware: HardwareProfile, core: IMathCore, logger=None):
        self.hw = hardware
        self.core = core
        self.logger = logger or print
        self.seven_zip = self._resolve_7z_exe()

    def _get_git_hash(self) -> str:
        try:
            return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
        except Exception:
            return "nohash"
    def run(self, year_filter: str = None, limit: int = 0):
        """
        Main entry point for the Framing Stage.
        """
        self._log(f"--- [Framer v5.2] Starting ---")
        self._log(f"Source: {self.hw.storage.source_root}")
        self._log(f"Stage : {self.hw.storage.stage_root}")
        self._log(f"Output: {self.hw.storage.output_root}")
        self._log(f"Workers: {self.hw.compute.framing_workers}")
        
        os.makedirs(self.hw.storage.stage_root, exist_ok=True)
        os.makedirs(self.hw.storage.output_root, exist_ok=True)

        # 1. Discovery
        archives = self._scan_archives(year_filter)
        self._log(f"Found {len(archives)} archives.")
        
        if limit > 0:
            archives = archives[:limit]
            self._log(f"Limiting to {limit} archives for smoke test.")

        # 2. Execution
        success_count = 0
        for i, archive in enumerate(archives):
            try:
                res = self._process_archive(archive)
                status = "success" if res else "failed"
                if res:
                    success_count += 1
                    
                # Progress Logging
                prog = {
                    "archive": os.path.basename(archive),
                    "status": status,
                    "index": i + 1,
                    "total": len(archives),
                    "timestamp": time.time()
                }
                with open("framer_progress.jsonl", "a") as pf:
                    json.dump(prog, pf)
                    pf.write("\n")
                    
            except Exception as e:
                self._log(f"[Error] Failed to process {archive}: {e}")
                import traceback
                traceback.print_exc()

        self._log(f"--- [Framer v5.2] Complete. Processed {success_count} archives. ---")

    def run_archives(self, archives: List[str], limit: int = 0):
        """
        Run framing on an explicit list of archive paths.

        This is the worker-safe mode for distributed framing: the controller
        generates `shard_*.txt` lists (relative paths), workers resolve and
        process them without moving raw data across machines.
        """
        self._log(f"--- [Framer v5.2] Starting (Explicit Archive List) ---")
        self._log(f"Source: {self.hw.storage.source_root}")
        self._log(f"Stage : {self.hw.storage.stage_root}")
        self._log(f"Output: {self.hw.storage.output_root}")
        self._log(f"Workers: {self.hw.compute.framing_workers}")

        os.makedirs(self.hw.storage.stage_root, exist_ok=True)
        os.makedirs(self.hw.storage.output_root, exist_ok=True)

        if not archives:
            self._log("[Warn] No archives provided.")
            return

        if limit > 0:
            archives = list(archives)[:limit]
            self._log(f"Limiting to {limit} archives for smoke test.")

        success_count = 0
        for archive in archives:
            if not os.path.exists(archive):
                self._log(f"[Skip] File not found: {archive}")
                continue
            try:
                res = self._process_archive(archive)
                if res:
                    success_count += 1
            except Exception as e:
                self._log(f"[Error] Failed to process {archive}: {e}")
                import traceback
                traceback.print_exc()

        self._log(f"--- [Framer v5.2] Complete. Processed {success_count}/{len(archives)} archives. ---")

    def _log(self, msg: str):
        if self.logger == print:
            print(msg, flush=True)
        else:
            self.logger(msg)

    def _scan_archives(self, year_filter: str) -> List[str]:
        if not os.path.exists(self.hw.storage.source_root):
            self._log(f"[Warn] Source root does not exist: {self.hw.storage.source_root}")
            return []
            
        # If no year filter, default scan
        if not year_filter:
            pattern = "**/*.7z"
        else:
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
        
        # Idempotency: Git Hash & Done File
        git_hash = self._get_git_hash()
        out_name = f"{date_str}_{git_hash}.parquet"
        output_path = os.path.join(self.hw.storage.output_root, out_name)
        done_path = output_path + ".done"
        meta_path = output_path + ".meta.json"
        
        if os.path.exists(done_path) and os.path.exists(output_path):
            self._log(f"[Skip] {out_name} already done.")
            return filename

        self._log(f"[Job] Processing {filename}...")
        start_time = time.time()
        
        # 1. Staging (Extraction)
        temp_stage = os.path.join(self.hw.storage.stage_root, date_str)
        
        # Pre-Cleanup
        if os.path.exists(temp_stage):
            try:
                shutil.rmtree(temp_stage)
            except Exception: pass
        os.makedirs(temp_stage, exist_ok=True)
        
        try:
            # Extract
            cmd = [self.seven_zip, "x", archive_path, f"-o{temp_stage}", "-y", "-mmt=on"]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Find Files
            all_files = glob.glob(os.path.join(temp_stage, "**/*.csv"), recursive=True)
            if not all_files:
                 all_files = glob.glob(os.path.join(temp_stage, "**/*.parquet"), recursive=True)
                 
            if not all_files:
                self._log(f"[Warn] No data files found in {archive_path}")
                return None
            
            # Group by Symbol
            symbol_map = {}
            for f in all_files:
                p = Path(f)
                # Heuristic: Symbol is usually the parent folder name
                # Structure: YYYYMMDD/Symbol/Symbol_YYYYMMDD_slice.csv
                symbol = p.parent.name
                if symbol.isdigit() and len(symbol) == 8: # If parent is date, go up one
                     symbol = p.parent.parent.name
                
                if symbol not in symbol_map:
                    symbol_map[symbol] = []
                symbol_map[symbol].append(str(p))

            self._log(f"       Found {len(all_files)} files. Grouped into {len(symbol_map)} symbols.")

            # 2. Parallel Processing (Map-Reduce)
            l2_cfg = load_l2_pipeline_config()
            
            processed_dfs = []
            workers = int(self.hw.compute.framing_workers)

            symbol_items = list(symbol_map.items())
            chunk_size = max(1, len(symbol_items) // (workers * 2))
            chunks = [symbol_items[i:i + chunk_size] for i in range(0, len(symbol_items), chunk_size)]
            
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(_process_stock_chunk, chunk, l2_cfg) for chunk in chunks]
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        res_list = future.result()
                        if res_list:
                            processed_dfs.extend(res_list)
                    except Exception as e:
                        print(f"Worker Error: {e}", flush=True)
            
            if not processed_dfs:
                self._log(f"[Warn] No valid dataframes generated for {date_str} (Check logs for schema rejections)")
                return None

            # 3. Concatenation & Output
            self._log(f"       Concatenating {len(processed_dfs)} asset frames...")
            full_df = pl.concat(processed_dfs)
            
            # Final Schema Check
            if "symbol" not in full_df.columns:
                self._log("[Error] 'symbol' column missing in output!")
                return None

            full_df.write_parquet(output_path)
            
            # Metadata & Done Marker
            meta = {
                "source": filename,
                "rows": full_df.height,
                "columns": list(full_df.columns),
                "schema_fingerprint": str(full_df.schema),
                "git_hash": git_hash,
                "timestamp": time.time()
            }
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2)
                
            Path(done_path).touch()
            
            duration = time.time() - start_time
            self._log(f"[Done] {filename} -> {output_path} ({full_df.height} rows, {duration:.1f}s)")
            
        except subprocess.CalledProcessError as e:
             self._log(f"[Error] 7-Zip failed: {e}")
             return None
        finally:
            # Cleanup
            if os.path.exists(temp_stage):
                try:
                    shutil.rmtree(temp_stage)
                except Exception as e:
                    self._log(f"[Warn] Failed to cleanup stage {temp_stage}: {e}")
                
        return filename
