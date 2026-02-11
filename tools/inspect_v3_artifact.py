import pickle
import numpy as np
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Load the checkpoint
ckpt_path = "artifacts/checkpoint_rows_31793682.pkl"
try:
    with open(ckpt_path, "rb") as f:
        data = pickle.load(f)
except FileNotFoundError:
    print(f"Error: {ckpt_path} not found.")
    sys.exit(1)

model = data["model"]
scaler = data["scaler"]
features = data["feature_cols"]

print("=== OMEGA v3.1 Model Inspection ===")
print(f"Total Rows Trained: {data.get('total_rows', 'Unknown')}")
print(f"Classes: {model.classes_}")

if hasattr(model, "coef_"):
    print("\n[Feature Importance (Linear Weights)]")
    # For SGDClassifier, coef_ is shape (1, n_features) for binary classification
    # or (n_classes, n_features) for multiclass.
    # Assuming standard setup (binary or one-vs-rest)
    
    coefs = model.coef_
    if coefs.shape[0] == 1:
        # Binary case
        weights = coefs[0]
        sorted_indices = np.argsort(np.abs(weights))[::-1]
        
        print(f"{ 'Feature':<20} | { 'Weight':<10} | { 'Interpretation'}")
        print("-" * 50)
        for i in sorted_indices:
            name = features[i]
            w = weights[i]
            
            # Auto-interpretation based on physics
            interpretation = "?"
            if name == "srl_resid":
                interpretation = "SRL Violation" if w < 0 else "Unexpected (+)"
            elif name == "topo_area":
                interpretation = "Structure (+)" if w > 0 else "Inverse (-)"
            elif name == "epiplexity":
                interpretation = "Complexity"
            elif name == "net_ofi":
                interpretation = "Flow Impetus"
            
            print(f"{name:<20} | {w:+.4f}     | {interpretation}")
    else:
        print("Multiclass model detected. Showing Top-3 features per class.")
        for cls_idx, cls_label in enumerate(model.classes_):
            print(f"\nClass {cls_label}:")
            weights = coefs[cls_idx]
            sorted_indices = np.argsort(np.abs(weights))[::-1][:3]
            for i in sorted_indices:
                print(f"  {features[i]}: {weights[i]:+.4f}")

else:
    print("Model does not expose coefficients (Not a linear model?)")

print("\n[Scaler Statistics (Standardization)]")
print(f"{ 'Feature':<20} | { 'Mean':<10} | { 'Std':<10}")
print("-" * 45)
for i, name in enumerate(features):
    print(f"{name:<20} | {scaler.mean_[i]:.4f}     | {np.sqrt(scaler.var_[i]):.4f}")