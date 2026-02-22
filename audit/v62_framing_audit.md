# OMEGA V62 Framing Architecture & Audit Report

**Date:** 2026-02-22
**Author:** Antigravity (V62 Upgrade Phase)

## 1. Architectural Overview

The V62 Framing stage ("The Heavy I/O Task") is responsible for ingesting historical Level-2 Tick Data (residing as highly compressed `.7z` / `.rar` archives), decompressing it, computing complex physics features (Ito calculus, topological energy, SRL matrices) via `omega_core.omega_etl`, and writing the output as clean `.parquet` frames.

Because this stage requires intense CPU crunching and causes massive I/O, the workload is **sharded** across heterogeneous nodes (Linux & Windows) instead of choking the main Mac Orchestrator.

### Node Assignments

- **Windows Node (`jiazi@192.168.3.112`)**: Handles Shard 1. Processes from `E:\data\level2` and outputs to `D:\Omega_frames\v61\host=windows1`.
- **Linux Node (`zepher@192.168.3.113`, 32-core Ryzen)**: Handles Shard 0. Processes from `/omega_pool/raw_7z_archives` and outputs to `/omega_pool/parquet_data/v52/frames/host=linux1`.

### 1.1 The Mandatory Framing Data Contract (Downstream Requirements)

The fundamental purpose of the Framing stage is NOT just to decompress CSVs. Its strict architectural mandate is to fulfill the invariant requirements of the three downstream V62 cores. If Framing fails to produce these exact mathematical guarantees, the entire pipeline collapses:

1. **For the Mathematical Core (`omega_math_core.py`)**:
   - **Mandate**: Must compute non-linear physics embeddings per ticker per day.
   - **Required Output Columns**:
     - `epiplexity` (Time-Bounded MDL Compression Gain S_T).
     - `srl_resid_050` (Physics violation using strict Delta=0.5).
     - `sigma_eff` and Topo metrics (`topo_energy`, `topo_area`).

2. **For the ML / Swarm Optimizer Core (`v60_swarm_xgb.py`)**:
   - **Mandate**: Must provide a clean Boolean Alpha target to orthogonalize performance against macro-market drift.
   - **Required Output Columns**: `t1_fwd_return` (The raw T+1 future return must be pre-calculated by the framing/ETL engine so the swarm can derive `t1_excess_return`).
   - **Constraint**: Must NEVER contain `NaN` or `Infinity` in the core physics features, as this instantly panics the XGBoost Optuna trials.

3. **For the Edge Backtester Core (`v61_run_local_backtest.py`)**:
   - **Mandate**: Must preserve strict chronological ordering (T+1 causality) and provide spatial ticker metadata.
   - **Required Structural Columns**: `date`, `time`, `symbol`.
   - **OOM Prevention Mandate**: The framing output MUST be partitioned via efficient Parquet groups. (The backtester defensively drops heavy list-traces like `ofi_list`, but the framer must ensure the scalar features are pre-computed so the backtester doesn't have to load raw ticks).

---

## 2. Hard-Learned Optimizations (The Anti-Fragile Fixes)

During the V61 to V62 transition, the system suffered from massive deadlocks (especially on the Linux node). The following engine modifications were permanently implemented:

### A. Polars Thread Throttling (Preventing Context Thrash)

By default, the Polars Rust backend (Rayon) spawns threads equal to the number of logical cores. If 4 Python multiprocessing workers spawn on a 32-core machine, it generates 128 competing threads, causing deadly RAM/CPU context swapping.

- **Fix:** Hardcoded `os.environ["POLARS_MAX_THREADS"] = "4"` (Linux) and `"8"` (Windows) to strictly cap thread explosions.

### B. ZFS Write Amplification Bypass (Linux Zepher Fix)

The Linux node previously deadlocked completely (0 files output, 171GB of Kernel error logs) because extracting millions of tiny CSVs from 7z directly onto a ZFS filesystem saturated the Transaction Group (TXG) queues, freezing the NVMe.

- **Fix:** Bypassed ZFS completely. The script was repointed to leverage a monolithic 4TB SSD (mounted at `/home`) as a dumb scratchpad. Temporary caches are isolated to `/home/zepher/framing_cache`.

### C. Bulletproof Caching Cleanup (OOM Guardians)

A crashed worker leaving behind 10GB of uncompressed CSVs rapidly fills primary disks (causing 100% full `/` partitions).

- **Fix:** Implemented three-tier cleanup:
  1. `finally` block `shutil.rmtree` per file loop.
  2. Native `atexit.register(nuke_cache)` hook.
  3. `signal.signal(signal.SIGINT/SIGTERM, nuke_cache)` intercepts.

---

## 3. Core Source Files

### Linux Framing Script (`tools/v61_linux_framing.py`)

This script resides on the Linux node and is built for sheer horizontal scale across 32 cores, while safely guarding the filesystem.

```python
#!/usr/bin/env python3
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

# 【ZFS BYPASS & CPU OPTIMIZATION】
# Extracting to the massive 4TB NVMe (/home) bypasses ZFS write amplification and RAM limits.
os.environ["POLARS_TEMP_DIR"] = "/home/zepher/framing_cache"
os.environ["TMPDIR"] = "/home/zepher/framing_cache"
os.environ["POLARS_MAX_THREADS"] = "4"

# Add project root to sys.path
sys.path.append("/home/zepher/work/Omega_vNext")

from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l2_frames

RAW_ROOT = Path("/omega_pool/raw_7z_archives")
OUTPUT_ROOT = Path("/omega_pool/parquet_data/v52/frames/host=linux1")
SEVEN_ZIP = "/usr/bin/7z"
GLOBAL_CFG = load_l2_pipeline_config()

def get_shard(filename, total_shards):
    h = hashlib.md5(filename.encode()).hexdigest()
    return int(h, 16) % total_shards

def process_day(args):
    day_path, hash_str, shard_index, total_shards = args
    date_str = day_path.stem
    out_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet"
    done_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet.done"

    if done_path.exists():
        return f"[{date_str}] Skipped (Done)"

    unique_id = uuid.uuid4().hex
    tmp_dir = Path(f"/home/zepher/framing_cache/omega_framing_{date_str}_{unique_id}")

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        cmd = [SEVEN_ZIP, "x", str(day_path), f"-o{tmp_dir}", "-y"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        csvs = list(tmp_dir.glob("**/*.csv"))

        frames = build_l2_frames([str(p) for p in csvs], GLOBAL_CFG)
        if frames.height > 0:
            tmp_parquet = out_path.with_suffix(".parquet.tmp")
            frames.write_parquet(tmp_parquet, compression="snappy")
            tmp_parquet.rename(out_path)
            done_path.touch()
            return f"[{date_str}] Completed"
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2023,2024,2025,2026")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--total-shards", type=int, default=2)
    args = ap.parse_args()

    # Bulletproof cleanup
    CACHE_DIR = "/home/zepher/framing_cache"
    def nuke_cache(*args_sig):
        shutil.rmtree(CACHE_DIR, ignore_errors=True)
    atexit.register(nuke_cache)
    signal.signal(signal.SIGINT, nuke_cache)
    signal.signal(signal.SIGTERM, nuke_cache)

    hash_str = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd="/home/zepher/work/Omega_vNext").decode().strip()
    # ... task mapping and multiprocessing ...
    
    ctx = get_context("spawn")
    with ctx.Pool(args.workers, maxtasksperchild=5) as p:
        for res in p.imap_unordered(process_day, tasks):
            print(res)

if __name__ == "__main__":
    main()
```

### Windows Framing Script (`tools/v61_windows_framing.py`)

Run under PowerShell on Windows 11, specifically tuned for the local environment where Windows lacks aggressive OOM management but handles multi-threading IO reasonably via NTFS.

```python
#!/usr/bin/env python3
import os
import sys
import hashlib
import subprocess
import argparse
import shutil
import uuid
from pathlib import Path
from multiprocessing import Pool

# Cap Polars internal threads
os.environ["POLARS_MAX_THREADS"] = "8"

sys.path.append(r"C:\Omega_vNext")
from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l2_frames

RAW_ROOT = Path(r"E:\data\level2")
OUTPUT_ROOT = Path(r"D:\Omega_frames\v61\host=windows1")
SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"
GLOBAL_CFG = load_l2_pipeline_config()

# ... (similar function logic to Linux, strictly adapted for Windows D:\tmp caching and multiprocessing)
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)  # Limited to 2 to prevent NTFS/Swap lock
    ap.add_argument("--shard", type=int, default=1)
    # ...
```

## 4. Mathematical Core (`omega_core/omega_math_core.py`)

The mathematical engine was structurally upgraded in V61/V62 to implement Time-Bounded Minimum Description Length (MDL) Gain for Epiplexity, and a strict Delta=0.5 universality constant for the Square Root Law (SRL).

```python
def calc_compression_gain(trace: Sequence[float], cfg: L2EpiplexityConfig) -> float:
    # V62 Upgrade: Time-Bounded Minimum Description Length (MDL) Gain
    # delta_k = 2 for linear probe (slope, intercept)
    delta_k = 2.0
    if n < 3:
        return 0.0
        
    mdl_gain_bits = -(n / 2.0) * np.log(1.0 - R_squared) - (delta_k / 2.0) * np.log(n)
    
    if mdl_gain_bits <= 0:
        return 0.0
        
    return float(mdl_gain_bits)

def calc_srl_state(price_change, sigma, net_ofi, depth, current_y, cfg, cancel_vol=0.0, trade_vol=0.0):
    # Sato 2025: "delta is exactly 0.5"
    raw_impact_unit = safe_sigma * math.sqrt(q_over_d) 
    theory_impact = sign * float(current_y) * raw_impact_unit
    
    # Residual: How much did Price violate Physics?
    srl_resid = float(price_change) - float(theory_impact)
```

## 5. Training / Swarm Optimizer (`tools/v60_swarm_xgb.py`)

The Swarm Optimizer introduces critical guards against Target/Dataset Collapse. It orthogonalizes the return target (Excess Return against the chronological cross-section) to eliminate look-ahead bias and macro-market drift.

```python
class EpistemicSwarmV6:
    def __init__(self, base_matrix_path: str, feature_cols: list[str]):
        import polars as pl
        self.df = pl.read_parquet(base_matrix_path)

        # v6.1: Orthogonalize Target (Excess Return) to remove Look-Ahead Bias
        self.df = self.df.with_columns([
            (pl.col("t1_fwd_return") - pl.col("t1_fwd_return").mean().over(["date", "time"]))
            .alias("t1_excess_return")
        ])
        
        # Original absolute target -> New V6.1 Alpha Target
        self.y_excess = (self.df.get_column("t1_excess_return").to_numpy() > 0).astype(int)

    def objective(self, trial, min_samples, nfold, ...):
        # V62 Fix: Strict hard-caps on ranges to strictly prevent dataset collapse
        peace_threshold = trial.suggest_float("peace_threshold", 0.05, 0.20)
        srl_mult = trial.suggest_float("srl_resid_sigma_mult", 0.5, 2.0)
        topo_energy_mult = trial.suggest_float("topo_energy_sigma_mult", 1.0, 3.0)
```

## 6. Local Inference & Backtesting Core (`tools/v61_run_local_backtest.py`)

To prevent OOM during validation on Mac/Linux nodes (128GB RAM), the backtester iterates over the massive 126GB Parquet dataset using **Spatial Ticker Sharding** instead of temporal chunking, ensuring T+1 causal integrity is perfectly maintained.

```python
def _process_backtest_batch(task: dict) -> dict:
    # ACTION 3: Single-file scan to prevent Arrow Rust panics from schema drift
    # across months of parquet files. Sequential is safer than bulk scan.
    try:
        tables = []
        for f_path in input_files:
            try:
                df_one = pl.scan_parquet(f_path).filter(pl.col("symbol").is_in(symbols)).collect()
                if df_one.height > 0:
                    tables.append(df_one)
            except Exception:
                continue

        df = pl.concat(tables, how="diagonal_relaxed")
        
        # V62 Defensive Engineering: Drop heavy trace lists before sorting/preparing
        # to prevent OOM spikes as warned in handover/DEBUG_LESSONS.md
        heavy_cols = ["ofi_list", "ofi_trace", "vol_list", "vol_trace", "time_trace", "trace"]
        drop_cols = [c for c in heavy_cols if c in df.columns]
        if drop_cols:
            df = df.drop(drop_cols)

        # Evaluate and aggregate metrics using trainer.py
        batch_metrics = evaluate_frames(...)
```

---

## 7. Operational Conclusion

The V61/V62 upgrade fundamentally decouples Data Ingestion (Anti-Fragile Framing), Mathematical Verification (Time-Bounded Epiplexity / Orthogonal Targets), and Inference (Spatial Sharded Backtests).
The current configuration acts as the **maximum stable threshold** on local hardware.

Any further scale-out beyond the current isolated edge nodes will orchestrate across Google Cloud Batch and Vertex AI natively utilizing the `.parquet` Lakehouse architecture detailed above.
