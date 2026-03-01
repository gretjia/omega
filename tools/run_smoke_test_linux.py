#!/usr/bin/env python3
"""
V62 Smoke Test: End-to-End Local Train & Backtest
1. Select 5 days of V62 L2 parquet for training.
2. Select next 5 days of V62 L2 parquet for backtest.
3. Train XGBoost model locally.
4. Backtest using evaluate_frames.
5. Cleanup.
"""

import os
import sys
import glob
import shutil
import pickle
from pathlib import Path
import time
import polars as pl
import xgboost as xgb
from sklearn.preprocessing import StandardScaler

# Ensure correct path
sys.path.append("/home/zepher/work/Omega_vNext")
from config import load_l2_pipeline_config
from omega_core.trainer import OmegaTrainerV3, evaluate_frames

def main():
    base_dir = "/omega_pool/parquet_data/latest_feature_l2/host=linux1"
    tmp_train_dir = "/omega_pool/smoke_test_train"
    tmp_test_dir = "/omega_pool/smoke_test_test"
    model_path = "/omega_pool/smoke_test_model.pkl"

    done_files = sorted(glob.glob(f"{base_dir}/*.parquet.done"))
    if len(done_files) < 10:
        print(f"[!] Not enough files for smoke test. Found {len(done_files)}, need 10.")
        sys.exit(1)

    parquet_files = [f.replace(".done", "") for f in done_files]
    train_files = [f for f in parquet_files[:5] if os.path.exists(f)]
    test_files = [f for f in parquet_files[5:10] if os.path.exists(f)]

    if len(train_files) < 5 or len(test_files) < 5:
        print("[!] Missing actual parquet files despite .done markers.")
        sys.exit(1)

    print(f"[*] Smoke Test Train Files: {len(train_files)}")
    print(f"[*] Smoke Test Test Files: {len(test_files)}")

    os.makedirs(tmp_train_dir, exist_ok=True)
    os.makedirs(tmp_test_dir, exist_ok=True)

    try:
        cfg = load_l2_pipeline_config()
        trainer = OmegaTrainerV3(cfg)
        feature_cols = list(trainer.feature_cols)

        print("[*] Stage 3: Training XGBoost Model on Train files...")
        start = time.time()
        
        dfs = []
        for f in train_files:
            df = pl.scan_parquet(f).head(500000).collect()
            dfs.append(df)
        
        train_df = pl.concat(dfs, how="diagonal_relaxed")
        train_df = trainer._prepare_frames(train_df, cfg)
        
        # Prepare X and y
        X_train = train_df.select(feature_cols).to_numpy()
        y_train = train_df.select("direction_label").to_numpy().ravel()
        
        # XGBoost requires labels to be 0, 1
        # If labels are -1, 1, convert to 0, 1
        import numpy as np
        y_train = np.where(y_train == -1, 0, y_train)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)

        print(f"[*] Fitting XGBoost on {X_train_scaled.shape}...")
        model = xgb.XGBClassifier(
            n_estimators=20,
            max_depth=6,
            learning_rate=0.1,
            n_jobs=16,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)

        with open(model_path, "wb") as f:
            pickle.dump({
                "model": model,
                "scaler": scaler,
                "feature_cols": feature_cols
            }, f)
        
        del train_df
        dfs.clear()
        
        print(f"[*] Training Complete in {time.time()-start:.2f}s")
        print("[*] Stage 3: Backtesting on Test files...")
        start = time.time()
        
        test_dfs = []
        for f in test_files:
            test_df = pl.scan_parquet(f).head(500000).collect()
            test_dfs.append(test_df)
        
        test_df = pl.concat(test_dfs, how="diagonal_relaxed")
        test_df = trainer._prepare_frames(test_df, cfg)
        
        metrics = evaluate_frames(test_df, cfg, model=model, scaler=scaler, feature_cols=feature_cols)
        
        print(f"[*] Backtest Complete in {time.time()-start:.2f}s")
        print("=== Smoke Test Backtest Metrics ===")
        for k, v in metrics.items():
            print(f"  {k}: {v}")

        print("[+] Smoke test passed successfully.")
        
    finally:
        print("[*] Cleaning up temporary files...")
        if os.path.exists(tmp_train_dir):
            shutil.rmtree(tmp_train_dir)
        if os.path.exists(tmp_test_dir):
            shutil.rmtree(tmp_test_dir)
        if os.path.exists(model_path):
            os.remove(model_path)
        print("[*] Cleanup complete.")

if __name__ == "__main__":
    main()
