import pickle
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
import json
from dataclasses import asdict

def sanitize(obj):
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def dump_checkpoint(path):
    print(f"Loading checkpoint: {path}")
    with open(path, "rb") as f:
        data = pickle.load(f)
    
    print("\n=== CHECKPOINT METADATA ===")
    print(f"Total Rows: {data.get('total_rows', 'N/A')}")
    print(f"Processed Files: {len(data.get('processed_files', []))}")
    
    features = data.get("feature_cols", [])
    model = data.get("model")
    scaler = data.get("scaler")
    
    print("\n=== FEATURE WEIGHTS (COEFFICIENTS) ===")
    if model and hasattr(model, "coef_"):
        coefs = model.coef_[0]
        indices = np.argsort(np.abs(coefs))[::-1]
        print(f"{'Rank':<5} {'Feature':<25} {'Weight':<10} {'AbsWeight':<10}")
        print("-" * 55)
        for rank, idx in enumerate(indices, 1):
            fname = features[idx] if idx < len(features) else f"feat_{idx}"
            w = coefs[idx]
            print(f"{rank:<5} {fname:<25} {w:<10.6f} {abs(w):<10.6f}")
            
    print("\n=== MODEL INTERCEPT ===")
    if model and hasattr(model, "intercept_"):
        print(f"Intercept: {model.intercept_}")

    print("\n=== SCALER STATISTICS ===")
    if scaler:
        print(f"{'Feature':<25} {'Mean':<20} {'Scale (Std)':<20}")
        print("-" * 65)
        for i, fname in enumerate(features):
            m = scaler.mean_[i] if i < len(scaler.mean_) else 0
            s = scaler.scale_[i] if i < len(scaler.scale_) else 0
            print(f"{fname:<25} {m:<20.6f} {s:<20.6f}")

    print("\n=== CONFIGURATION DUMP ===")
    cfg = data.get("cfg")
    if cfg:
        try:
            cfg_dict = asdict(cfg)
            print(json.dumps(cfg_dict, default=sanitize, indent=2))
        except Exception as e:
            print(f"Could not serialize config: {e}")
            print(str(cfg))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dump_v40_checkpoint.py <path_to_pkl>")
        sys.exit(1)
    dump_checkpoint(sys.argv[1])