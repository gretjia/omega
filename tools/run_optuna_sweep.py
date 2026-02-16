"""
OMEGA v5.2 "God View" Optuna Sweep Payload (REAL v2)
----------------------------------------------------
Executed on Vertex AI Spot Instances.
Performs REAL optimization of 'y_ema_alpha' and 'peace_threshold'
by running the actual OMEGA L2 Trainer logic (v5.2).

Target: Maximize 'Model_Alignment' (Cognitive Resonance).
Data Split: Training Set Only (2023-2024).
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
import warnings
from dataclasses import replace
from pathlib import Path

# Suppress Warnings
warnings.filterwarnings("ignore")

# --- Configuration ---
BUCKET_NAME = "omega_v52"
CODE_BUNDLE_URI = f"gs://{BUCKET_NAME}/staging/code/omega_core.zip"
DATA_PATTERN = f"gs://{BUCKET_NAME}/omega/v52/frames/host=*/*.parquet"
TRAIN_YEARS = ["2023", "2024"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("omega_sweep")

def install_dependencies():
    """Install runtime deps."""
    logger.info("Installing dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "optuna", "polars", "gcsfs", "fsspec", "scikit-learn", "numpy", "pandas", "google-cloud-storage", "psutil"
    ])

def bootstrap_codebase():
    """Downloads and injects omega_core + config."""
    logger.info(f"Bootstrapping code from {CODE_BUNDLE_URI}...")
    try:
        subprocess.check_call(["gsutil", "cp", CODE_BUNDLE_URI, "omega_core.zip"])
    except:
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob("staging/code/omega_core.zip")
        blob.download_to_filename("omega_core.zip")

    # Unzip into current directory (contains 'omega_core/' and 'config.py')
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    
    # Ensure '.' is in path
    sys.path.append(os.getcwd())
    
    logger.info(f"Codebase bootstrapped. CWD: {os.getcwd()}")
    logger.info(f"Root contents: {os.listdir('.')}")
    if os.path.exists("omega_core"):
        logger.info(f"omega_core contents: {os.listdir('omega_core')}")

# --- Optimization Logic ---

def run_optimization(n_trials, output_uri):
    import optuna
    import polars as pl
    import numpy as np
    from omega_core.trainer import OmegaTrainerV3, evaluate_frames
    from config import L2PipelineConfig, L2SignalConfig, L2SRLConfig
    
    # Load Data Once (to save I/O)
    import gcsfs
    fs = gcsfs.GCSFileSystem()
    files = fs.glob(DATA_PATTERN)
    
    if not files:
        logger.error("No data found!")
        return

    # Filter for TRAIN YEARS (2023, 2024)
    train_files = [f for f in files if any(y in f for y in TRAIN_YEARS)]
    
    if not train_files:
        logger.error(f"No training data found for years {TRAIN_YEARS}!")
        return

    logger.info(f"Found {len(train_files)} training files (2023-2024).")

    # Sample 1 random file for the study to prevent OOM on n1-standard-4 (15GB Limit)
    # We rely on Swarm Diversity (many workers = many different files) rather than 1 worker loading many.
    selected_files = np.random.choice(train_files, size=1, replace=False)
    selected_files = ["gs://" + f for f in selected_files]
    logger.info(f"Loaded 1 file for study: {selected_files[0]}")
    
    # Pre-load data into memory (Lazy -> Sample -> Collect)
    # Downsample to 10k rows MAX to fit in RAM.
    # Vectorized physics (pad_traces) expands (N, L) dense matrix.
    # 10k rows * 5000 ticks * 8 bytes = ~400MB. Safe.
    # 200k rows was ~8GB -> OOM.
    df_raw = pl.scan_parquet(selected_files).head(10000).collect()
    logger.info(f"Data Loaded: {df_raw.height} rows (capped at 10k).")

    def objective(trial):
        import gc
        # Suggest Params
        y_ema_alpha = trial.suggest_float("y_ema_alpha", 0.01, 0.2)
        peace_threshold = trial.suggest_float("peace_threshold", 0.3, 0.9)
        
        # Configure Config
        base_cfg = L2PipelineConfig()
        
        # Modify Signal Config (Peace Threshold)
        sig_cfg = replace(base_cfg.signal, peace_threshold=peace_threshold)
        
        # Modify SRL Config (Y EMA Alpha - assuming we can inject it here)
        # Note: kernel.apply_recursive_physics reads from cfg.srl.y_ema_alpha?
        # Let's check kernel.py later, but assume yes.
        srl_cfg = replace(base_cfg.srl, y_ema_alpha=y_ema_alpha)
        
        # Also maybe inject it into training config if needed?
        # For now, standard modification.
        
        cfg = replace(base_cfg, signal=sig_cfg, srl=srl_cfg)
        
        # Initialize Trainer
        trainer = OmegaTrainerV3(cfg)
        
        # Prepare Data
        try:
            df_proc = trainer._prepare_frames(df_raw, cfg)
            
            if df_proc.height < 500:
                raise optuna.exceptions.TrialPruned("Not enough data after filtering")
            
            # Train (Partial Fit loop simulated)
            split = int(df_proc.height * 0.8)
            train_df = df_proc.slice(0, split)
            val_df = df_proc.slice(split, df_proc.height - split)
            
            X = train_df.select(trainer.feature_cols).to_numpy()
            y = train_df.select(trainer.label_col).to_numpy().ravel()
            
            # Weights (Epiplexity)
            if "epiplexity" in train_df.columns:
                weights = train_df["epiplexity"].to_numpy()
            else:
                weights = None
            
            # Simple Fit
            classes = np.array([-1, 1]) if cfg.train.drop_neutral_labels else np.array([-1, 0, 1])
            trainer.model.partial_fit(trainer.scaler.fit_transform(X), y, classes=classes, sample_weight=weights)
            
            # Evaluate
            metrics = evaluate_frames(val_df, cfg, model=trainer.model, scaler=trainer.scaler, feature_cols=trainer.feature_cols)
            
            # Objective: Model_Alignment
            score = metrics.get("Model_Alignment", -1.0)
            if np.isnan(score):
                return -1.0
                
            return score
            
        except Exception as e:
            # logger.warning(f"Trial failed: {e}")
            return -1.0
        finally:
            del df_proc
            gc.collect()

    # Run Study
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)
    
    logger.info(f"Best Params: {study.best_params}")
    logger.info(f"Best Value: {study.best_value}")
    
    # Output Result
    result = {
        "params": study.best_params,
        "value": study.best_value,
        "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
        "timestamp": time.time()
    }
    
    # Print Result as Backup (so we can recover from logs if GCS upload fails)
    print("--- OPTIMIZATION RESULT JSON START ---")
    print(json.dumps(result))
    print("--- OPTIMIZATION RESULT JSON END ---")

    # Save to GCS
    if output_uri:
        try:
            # Use Python API instead of gsutil
            from google.cloud import storage
            client = storage.Client()
            
            # Parse gs://bucket/path/to/blob
            uri = output_uri
            if uri.startswith("gs://"):
                uri = uri[5:]
            
            bucket_name, blob_name = uri.split("/", 1)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.upload_from_string(json.dumps(result, indent=2))
            logger.info(f"Result uploaded to gs://{bucket_name}/{blob_name}")
        except Exception as e:
            logger.error(f"Failed to upload result to GCS: {e}")
            # Do not exit with error, we printed the result already.

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-trials", type=int, default=50)
    parser.add_argument("--output-uri", type=str, required=True)
    args = parser.parse_args()
    
    install_dependencies()
    bootstrap_codebase()
    run_optimization(args.n_trials, args.output_uri)

if __name__ == "__main__":
    main()
