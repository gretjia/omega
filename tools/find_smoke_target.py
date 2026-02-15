import os
import glob
from pathlib import Path
from config import load_l2_pipeline_config

def find_smoke_target():
    cfg = load_l2_pipeline_config()
    root = cfg.io.input_root # Default: ./data/level2
    
    # Try to find 2025 data first
    patterns = [
        "2025/202501/*.7z",
        "2024/202401/*.7z",
        "**/*.7z"
    ]
    
    found = []
    for p in patterns:
        search_path = os.path.join(root, p)
        found = sorted(glob.glob(search_path, recursive=True))
        if found:
            break
            
    if found:
        # Take up to 5 files (approx 1 week)
        return found[:5]
    return []

if __name__ == "__main__":
    targets = find_smoke_target()
    if targets:
        print(f"FOUND_TARGETS={','.join(targets)}")
    else:
        print("FOUND_TARGETS=NONE")
