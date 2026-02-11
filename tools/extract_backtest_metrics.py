import json
import sys
from pathlib import Path

def extract_metrics(state_path):
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    sums = state.get("metric_sums", {})
    n = sums.get("n_valid", 0)
    
    if n == 0:
        print("No valid metric samples yet.")
        return

    def get_avg(key):
        val = sums.get(key)
        if val is None:
            return 0.0
        return val / n

    print(f"--- Physics Audit Metrics (n={n:,}) ---")
    print(f"Topo SNR:         {get_avg('Topo_SNR'):.4f}")
    print(f"Orthogonality:    {get_avg('Orthogonality'):.4f}")
    print(f"Vector Alignment: {get_avg('Vector_Alignment'):.4f}")
    print("-" * 40)

if __name__ == "__main__":
    extract_metrics("audit/v40_runtime/windows/backtest/backtest_state.json")