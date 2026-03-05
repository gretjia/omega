#!/usr/bin/env python3
import os
import glob
import json
import shutil
from pathlib import Path

def main():
    print("=== STARTING WINDOWS SHADOW COPY ===")
    
    pool_dir = Path("/omega_pool/parquet_data")
    shadow_in_dir = pool_dir / "v63_subset_l1_shadow_w1" / "host=windows1"
    shadow_in_dir.mkdir(parents=True, exist_ok=True)
    mapping_file = pool_dir / "windows_shadow_mapping.json"
    
    pending_files = [] # (filename, original_path, shard_id)
    
    # 1. Safely identify files without .done markers
    for shard_id in range(1, 5):
        l1_dir = pool_dir / f"v63_subset_l1_shard{shard_id}" / "host=linux1"
        l2_dir = pool_dir / f"v63_feature_l2_shard{shard_id}" / "host=linux1"
        
        if not l1_dir.exists():
            continue
            
        for l1_file in l1_dir.glob("*.parquet"):
            filename = l1_file.name
            done_marker = l2_dir / f"{filename}.done"
            if not done_marker.exists():
                pending_files.append((filename, l1_file, f"shard{shard_id}"))

    print(f"Total pending files identified on Linux: {len(pending_files)}")
    if len(pending_files) == 0:
        print("No pending files. Nothing to do.")
        return
        
    # 2. Sort to process chronologically
    pending_files.sort(key=lambda x: x[0])
    
    # 3. COPY files (do NOT move) to avoid disturbing Linux workers
    mapping = {}
    if mapping_file.exists():
        with open(mapping_file, "r") as f:
            mapping = json.load(f)
            
    for fn, path, shard in pending_files:
        target_path = shadow_in_dir / fn
        if not target_path.exists():
            print(f"Shadowing {fn}...")
            shutil.copy2(str(path), str(target_path)) # Using copy2 to preserve metadata
        mapping[fn] = shard
        
    with open(mapping_file, "w") as f:
        json.dump(mapping, f, indent=2)
        
    print(f"Shadow copy complete. Mapping saved to {mapping_file}")

if __name__ == "__main__":
    main()
