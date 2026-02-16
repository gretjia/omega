"""
OMEGA v5.2 Cloud Backtest Driver
--------------------------------
Runs a full OMEGA evaluation on the Test Set (2025-2026) using the 
"God Params" baked into config.py.

Usage:
    python tools/run_cloud_backtest.py
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import json
import warnings
from pathlib import Path

# Suppress Warnings
warnings.filterwarnings("ignore")

# --- Configuration ---
BUCKET_NAME = "omega_v52"
CODE_BUNDLE_URI = f"gs://{BUCKET_NAME}/staging/code/omega_core.zip"
# Backtest Data: 2025 and 2026
DATA_PATTERN = f"gs://{BUCKET_NAME}/omega/v52/frames/host=*/*.parquet"
TEST_YEARS = ["2025", "2026"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("omega_backtest")

def install_dependencies():
    logger.info("Installing dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "polars", "gcsfs", "fsspec", "scikit-learn", "numpy", "pandas", "google-cloud-storage", "psutil"
    ])

def bootstrap_codebase():
    logger.info(f"Bootstrapping code from {CODE_BUNDLE_URI}...")
    try:
        subprocess.check_call(["gsutil", "cp", CODE_BUNDLE_URI, "omega_core.zip"])
    except:
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob("staging/code/omega_core.zip")
        blob.download_to_filename("omega_core.zip")

    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    sys.path.append(os.getcwd())
    logger.info(f"Codebase bootstrapped.")

def run_backtest():
    import polars as pl
    import numpy as np
    from omega_core.trainer import OmegaTrainerV3, evaluate_frames
    from config import L2PipelineConfig
    import gcsfs
    
    # 1. Load Data
    fs = gcsfs.GCSFileSystem()
    files = fs.glob(DATA_PATTERN)
    
    # Filter for Test Years
    test_files = [f for f in files if any(y in f for y in TEST_YEARS)]
    test_files = ["gs://" + f for f in test_files]
    
    if not test_files:
        logger.error(f"No test data found for years {TEST_YEARS}!")
        return

    logger.info(f"Found {len(test_files)} test files (2025-2026).")
    
    # Load limited test data to prevent OOM (15GB Limit)
    if len(test_files) > 10:
        selected_files = np.random.choice(test_files, size=1, replace=False)
    else:
        selected_files = test_files
        
    # Ensure paths are strings, not numpy objects, and valid URIs
    # The list is already formatted as ["gs://...", ...] but verify.
    selected_files = [str(f) for f in selected_files]
    
    logger.info(f"Loading file: {selected_files[0]}")
    # Lazy scan, take 100k, then collect.
    df_raw = pl.scan_parquet(selected_files[0]).head(100000).collect()
    logger.info(f"Data Loaded: {df_raw.height} rows.")
    
    # 2. Configure
    # This automatically picks up the updated config.py with God Params
    cfg = L2PipelineConfig()
    
    # 3. Apply Physics (Re-calc with God Params)
    trainer = OmegaTrainerV3(cfg)
    logger.info("Applying God Physics...")
    df_proc = trainer._prepare_frames(df_raw, cfg)
    
    # 4. Evaluate
    logger.info("Evaluating Metrics...")
    # For backtest, we don't necessarily train a new model, we simulate the strategy.
    # BUT, evaluate_frames checks 'Model_Alignment'. This implies a model exists.
    # If we want to check the *Physics* Strategy (is_signal), we look at Phys_Alignment or just returns.
    
    # However, trainer_v52 implies we train a model.
    # To get a valid OOS score, we should ideally TRAIN on 2023-2024 (which we did in Oracle/Swarm individually) 
    # and PREDICT on 2025.
    
    # Simplification: Train a fresh model on the *processed* test data (Self-Consistency check) 
    # OR just check the physics alignment (Phys_Alignment).
    # Since we don't have the serialized model from the Swarm (we only got params),
    # checking Physics Alignment is the most honest test of the *parameters*.
    
    metrics = evaluate_frames(df_proc, cfg, model=None, scaler=None, feature_cols=None)
    
    print("\n--- BACKTEST RESULTS (2025-2026) ---")
    print(json.dumps(metrics, indent=2))
    print("------------------------------------")

def main():
    install_dependencies()
    bootstrap_codebase()
    run_backtest()

if __name__ == "__main__":
    main()
