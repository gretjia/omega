#!/usr/bin/env python3
import os
import json
import shutil
import subprocess
from pathlib import Path

def main():
    print("=== STARTING WINDOWS ASSIST MERGE ===")
    
    pool_dir = Path("/omega_pool/parquet_data")
    assist_out_dir = pool_dir / "v63_feature_l2_assist_w1" / "host=windows1"
    mapping_file = pool_dir / "windows_assist_mapping.json"
    
    if not mapping_file.exists():
        print(f"Error: Mapping file {mapping_file} not found. Cannot merge!")
        return
        
    with open(mapping_file, "r") as f:
        mapping = json.load(f)
        
    if not assist_out_dir.exists():
        print(f"Error: Assist output directory {assist_out_dir} not found.")
        return
        
    # Move returned files to their respective shards
    for l2_file in assist_out_dir.glob("*.parquet"):
        filename = l2_file.name
        shard_id = mapping.get(filename)
        
        if not shard_id:
            print(f"Warning: {filename} not found in mapping! Skipping.")
            continue
            
        target_dir = pool_dir / f"v63_feature_l2_{shard_id}" / "host=linux1"
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Move the .parquet file
        target_path = target_dir / filename
        print(f"Moving {filename} -> {target_path}")
        shutil.move(str(l2_file), str(target_path))
        
        # Move the .done marker if it exists
        done_marker = assist_out_dir / f"{filename}.done"
        if done_marker.exists():
            target_done_path = target_dir / f"{filename}.done"
            print(f"Moving {done_marker.name} -> {target_done_path}")
            shutil.move(str(done_marker), str(target_done_path))
        else:
            print(f"Warning: .done marker for {filename} is missing from Windows output.")
            
    print("=== MERGE COMPLETE ===")

if __name__ == "__main__":
    main()
