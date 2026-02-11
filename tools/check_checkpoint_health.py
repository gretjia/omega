import pickle
import numpy as np
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def check_health(path):
    print(f"--- Checking Checkpoint: {path} ---")
    with open(path, "rb") as f:
        data = pickle.load(f)
    
    model = data.get("model")
    scaler = data.get("scaler")
    features = data.get("feature_cols", [])
    total_rows = data.get("total_rows", 0)
    
    print(f"Total Rows: {total_rows:,}")
    print(f"Features Count: {len(features)}")
    
    if model is None or scaler is None:
        print("ERROR: Model or Scaler missing!")
        return

    # Check Model Coefficients
    coef = model.coef_
    intercept = model.intercept_
    
    nan_count = np.isnan(coef).sum()
    inf_count = np.isinf(coef).sum()
    
    print(f"NaN in coef: {nan_count}")
    print(f"Inf in coef: {inf_count}")
    
    if nan_count > 0 or inf_count > 0:
        print("CRITICAL: Model contains invalid numbers!")
    
    # Check Weight Distribution
    abs_coef = np.abs(coef)
    print(f"Coef Mean (abs): {np.mean(abs_coef):.6f}")
    print(f"Coef Max (abs): {np.max(abs_coef):.6f}")
    print(f"Coef Min (abs): {np.min(abs_coef):.6f}")
    
    # Check Scaler
    if hasattr(scaler, "mean_"):
        print(f"Scaler Mean Range: [{np.min(scaler.mean_):.4f}, {np.max(scaler.mean_):.4f}]")
        print(f"Scaler Var Range: [{np.min(scaler.var_):.4f}, {np.max(scaler.var_):.4f}]")
    
    # Show Top 5 and Bottom 5 features by weight
    if len(features) == coef.shape[1]:
        flat_coef = coef[0]
        sorted_idx = np.argsort(np.abs(flat_coef))
        print("\nTop 5 Strongest Features:")
        for i in range(1, 6):
            idx = sorted_idx[-i]
            print(f"  {features[idx]}: {flat_coef[idx]:.6f}")
            
        print("\nTop 5 Weakest Features:")
        for i in range(5):
            idx = sorted_idx[i]
            print(f"  {features[idx]}: {flat_coef[idx]:.6f}")
    
    print("-" * 40)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_health(sys.argv[1])
    else:
        print("Usage: python tools/check_checkpoint_health.py <path_to_pkl>")