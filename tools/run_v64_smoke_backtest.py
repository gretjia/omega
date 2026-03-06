import sys
import os
from pathlib import Path
import polars as pl
import xgboost as xgb
import pickle

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from config import load_l2_pipeline_config
from omega_core.trainer import evaluate_frames

def main():
    print("=== V64 EXTREMISTAN BACKTEST SMOKE TEST ===")
    model_path = "/omega_pool/smoke_v64/model/omega_xgb_final.pkl"
    l2_path = "/omega_pool/smoke_v64/l2/tiny_20230103_fbd5c8b.parquet"
    
    if not os.path.exists(model_path) or not os.path.exists(l2_path):
        print("Missing required smoke test artifacts.")
        sys.exit(1)
        
    with open(model_path, "rb") as f:
        payload = pickle.load(f)
        model = payload["model"]
        feature_cols = payload["feature_cols"]
        
    df = pl.read_parquet(l2_path)
    cfg = load_l2_pipeline_config()
    
    # Needs a dummy target for evaluation if not present in basic L2. Let's rely on direction.
    singularity_threshold = -0.1
    metrics = evaluate_frames(
        df, cfg, 
        model=model, 
        scaler=None, # V64 removes scaling
        feature_cols=feature_cols,
        peace_threshold=singularity_threshold, # legacy evaluate_frames keyword; semantic gate is singularity_vector amplitude
    )
    
    print("\nBacktest Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
        
    assert metrics["n_frames"] > 0, "No frames evaluated."
    print("✅ V64 Backtest logic smoke test passed.")

if __name__ == "__main__":
    main()
