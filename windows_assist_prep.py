#!/usr/bin/env python3
import os
import glob
import json
import shutil
import subprocess
from pathlib import Path

def main():
    print("=== STARTING WINDOWS ASSIST PREPARATION ===")
    
    # Paths
    pool_dir = Path("/omega_pool/parquet_data")
    assist_in_dir = pool_dir / "v63_subset_l1_assist_w1" / "host=windows1"
    assist_in_dir.mkdir(parents=True, exist_ok=True)
    mapping_file = pool_dir / "windows_assist_mapping.json"
    
    # 1. Full Backup of L2 markers and data
    backup_tar = "/home/zepher/v63_l2_backup_before_assist.tar"
    if not os.path.exists(backup_tar):
        print(f"Creating full backup of L2 state to {backup_tar}...")
        # Find all directories to backup
        l2_dirs = list(pool_dir.glob("v63_feature_l2_shard*/host=linux1"))
        
        # Build tar command
        tar_cmd = ["tar", "-cf", backup_tar]
        for d in l2_dirs:
            tar_cmd.append(str(d))
            
        try:
            subprocess.run(tar_cmd, check=True)
            print("Backup created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create backup: {e}")
            return
    else:
        print(f"Backup {backup_tar} already exists. Skipping backup step.")
        
    # 2. Identify Pending Files
    pending_files = [] # list of (filename, l1_path, shard_id)
    
    for shard_id in range(1, 5):
        l1_dir = pool_dir / f"v63_subset_l1_shard{shard_id}" / "host=linux1"
        l2_dir = pool_dir / f"v63_feature_l2_shard{shard_id}" / "host=linux1"
        
        if not l1_dir.exists():
            continue
            
        for l1_file in l1_dir.glob("*.parquet"):
            filename = l1_file.name
            done_marker = l2_dir / f"{filename}.done"
            # If done marker does not exist, it is pending
            if not done_marker.exists():
                pending_files.append((filename, l1_file, f"shard{shard_id}"))

    print(f"Total pending files on Linux across all shards: {len(pending_files)}")
    
    if len(pending_files) == 0:
        print("No pending files. Nothing to do.")
        return
        
    # 3. Sort and Select (take from the very end to avoid active worker cursors)
    # The current workers are at 202505xx. Taking highest date strings (e.g. 2026xxxx)
    pending_files.sort(key=lambda x: x[0])
    
    NUM_FILES_TO_ASSIST = 28
    
    if len(pending_files) <= NUM_FILES_TO_ASSIST:
        selected_files = pending_files[-len(pending_files):]
    else:
        selected_files = pending_files[-NUM_FILES_TO_ASSIST:]
        
    print(f"Selected {len(selected_files)} files for Windows assist (from tail).")
    for f in selected_files:
        print(f" - {f[0]} (from {f[2]})")
        
    # 4. Isolate and Generate Mapping
    mapping = {}
    if mapping_file.exists():
        with open(mapping_file, "r") as f:
            mapping = json.load(f)
            
    for filename, l1_path, shard_id in selected_files:
        target_path = assist_in_dir / filename
        print(f"Moving {filename} -> {target_path}")
        shutil.move(str(l1_path), str(target_path))
        mapping[filename] = shard_id
        
    with open(mapping_file, "w") as f:
        json.dump(mapping, f, indent=2)
        
    print(f"Mapping saved to {mapping_file}")
    print("=== PREPARATION COMPLETE ===")

if __name__ == "__main__":
    main()
