import sys
import os
import glob

# Ensure project root is in path
sys.path.append(os.getcwd())

from config import load_l2_pipeline_config

def setup_smoke_data():
    cfg = load_l2_pipeline_config()
    # Force the source root to what we expect on this machine if default fails
    # But usually cfg.io.input_root is correct (default ./data/level2 or E:/data/level2)
    
    roots_to_try = [
        cfg.io.input_root,
        "E:/data/level2",
        "D:/Omega_vNext/data/level2",
        "./data/level2"
    ]
    
    all_archives = []
    
    print(f"Scanning for .7z archives...")
    for root in roots_to_try:
        if os.path.exists(root):
            print(f"Checking root: {root}")
            # Try recursive scan
            files = sorted(glob.glob(os.path.join(root, "**", "*.7z"), recursive=True))
            if files:
                all_archives = files
                print(f"Found {len(files)} archives in {root}")
                break
    
    if not all_archives:
        print("[Error] No .7z archives found in any candidate root.")
        return None, None

    # Sort by name (usually implies date)
    all_archives.sort()
    
    # Select Week 1 (Train) and Week 2 (Backtest)
    # We need at least 2 files, ideally 10.
    if len(all_archives) < 2:
        print(f"[Error] Not enough archives found ({len(all_archives)}). Need at least 2.")
        return None, None
        
    # Take first 5 for train, next 5 for backtest (or split half/half if small)
    mid = min(5, len(all_archives) // 2)
    train_files = all_archives[:mid]
    backtest_files = all_archives[mid:mid+5] # Up to next 5
    
    print(f"\n[Smoke Test Plan]")
    print(f"Training Data ({len(train_files)}):")
    for f in train_files: print(f"  - {os.path.basename(f)}")
    
    print(f"Backtest Data ({len(backtest_files)}):")
    for f in backtest_files: print(f"  - {os.path.basename(f)}")
    
    return train_files, backtest_files

if __name__ == "__main__":
    setup_smoke_data()
