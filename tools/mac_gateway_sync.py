#!/usr/bin/env python3
"""
OMEGA v5.2 Mac Gateway Sync Tool (Batch & Burn)
-----------------------------------------------
Acts as a bridge between local LAN machines (Windows/Linux) and Google Cloud Storage.
Due to Mac disk constraints (~147GB) and total data size (>113GB), this tool:
1.  Connects to remote hosts via SSH/SCP.
2.  Transfers a small batch of COMPLETED frames (e.g., 10GB) to a local buffer.
3.  Uploads the batch to GCS.
4.  Deletes the local buffer to free space.
5.  Repeats until sync is complete.

Usage:
    python tools/mac_gateway_sync.py --bucket gs://your-bucket-name

Configuration:
    - Edit the HOSTS dictionary below to match your LAN setup.
    - Ensure SSH keys are set up for passwordless access to 'windows1-w1' and 'linux1-lx'.
"""

import warnings
# Suppress annoying Google Cloud Python 3.9 deprecation warnings
warnings.filterwarnings("ignore", ".*Python version 3.9 past its end of life.*")
warnings.filterwarnings("ignore", ".*non-supported Python version.*")

import argparse
import time
import subprocess
import os
import shutil
import glob
import sys
from pathlib import Path

# --- Configuration ---
BUFFER_DIR = Path.home() / "Omega_uplink_buffer"
BATCH_SIZE_GB = 15  # Keep buffer well below free space limit
IDENTITY_FILE = Path.home() / ".ssh" / "id_ed25519"

# Host Definitions
# source_path: The directory containing the frames ON THE REMOTE MACHINE.
# dest_subpath: The subdirectory in GCS/Buffer to organize files.
HOSTS = {
    "linux1": {
        "ssh_target": "zepher@192.168.3.113",
        "source_path": "/omega_pool/parquet_data/v52/frames/host=linux1/",
        "dest_subpath": "host=linux1"
    },
    "windows1": {
        "ssh_target": "jiazi@192.168.3.112",
        "source_path": "D:/Omega_frames/v52/frames/host=windows1/",
        "dest_subpath": "host=windows1"
    }
}

def check_dependencies():
    """Ensure gcloud, scp/ssh are available."""
    if not shutil.which("gcloud"):
        print("[!] Error: 'gcloud' not found. Please install Google Cloud SDK.")
        sys.exit(1)
    if not shutil.which("ssh"):
        print("[!] Error: 'ssh' not found.")
        sys.exit(1)

def get_ssh_cmd(target, command):
    """Returns the SSH command list with specific options to bypass bad config."""
    # -F /dev/null: Ignore user config (avoids BindAddress issues)
    # -o StrictHostKeyChecking=no: Auto-accept keys (safe for LAN)
    # -i ...: Identity file
    return ["ssh", "-F", "/dev/null", "-o", "StrictHostKeyChecking=no", "-i", str(IDENTITY_FILE), target, command]

def get_scp_download_cmd(target, remote_path, local_path):
    return ["scp", "-F", "/dev/null", "-o", "StrictHostKeyChecking=no", "-i", str(IDENTITY_FILE), "-q", f"{target}:{remote_path}", str(local_path)]

def get_remote_file_list(host_config, year_filter=None):
    """
    Lists COMPLETED parquet files on the remote host.
    Returns a list of (filename, size_bytes).
    """
    target = host_config["ssh_target"]
    path = host_config["source_path"]
    print(f"[*] Scanning {target}:{path} for completed frames" + (f" (Year: {year_filter})" if year_filter else "") + "...")

    files = []
    
    try:
        if "windows" in target.lower() or "jiazi" in target.lower():
            # Windows PowerShell command
            win_path = path.replace('/', '\\')
            filter_str = f"*{year_filter}*_4f9c786.parquet" if year_filter else "*_4f9c786.parquet"
            ps_cmd = f"Get-ChildItem -Path '{win_path}' -Filter '{filter_str}' | Select-Object Name, Length | ForEach-Object {{ $_.Name + ',' + $_.Length }}"
            cmd = get_ssh_cmd(target, f"powershell -NoProfile -Command \"{ps_cmd}\"")
        else:
            # Linux find command
            name_pattern = f"*{year_filter}*_4f9c786.parquet" if year_filter else "*_4f9c786.parquet"
            cmd = get_ssh_cmd(target, f"find {path} -name '{name_pattern}' -printf '%f,%s\\n'")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if "," in line:
                try:
                    name, size = line.split(",")
                    files.append((name.strip(), int(size.strip())))
                except ValueError:
                    continue

    except subprocess.CalledProcessError as e:
        print(f"[!] Error listing files on {target}: {e}")
        # Print stderr for debugging
        print(f"    Stderr: {e.stderr}")
        return []
        
    print(f"    Found {len(files)} candidate frames.")
    return files

def sync_batch(host_key, files_to_sync, gcs_bucket):
    """
    Downloads a batch of files, uploads them, and cleans up.
    """
    host_cfg = HOSTS[host_key]
    target = host_cfg["ssh_target"]
    remote_dir = host_cfg["source_path"]
    local_batch_dir = BUFFER_DIR / host_cfg["dest_subpath"]
    
    local_batch_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Processing batch of {len(files_to_sync)} files from {host_key}...")
    
    for fname, _ in files_to_sync:
        # Use forward slashes for SCP, even on Windows (OpenSSH handles it)
        # Avoid double slashes
        remote_path = f"{remote_dir}/{fname}".replace("//", "/")
        
        # Check if file already exists in GCS?
        # Ideally we should, but for batch & burn we assume we want to sync.
        # Adding a simple check using gsutil ls could be slow.
        # We rely on the user to filter or overwrite.
        
        # Download Parquet
        print(f"    < Downloading: {fname}")
        subprocess.run(get_scp_download_cmd(target, remote_path, local_batch_dir), check=True)
        
        # Download Meta
        meta_name = fname + ".meta.json"
        meta_remote = f"{remote_dir}/{meta_name}".replace("//", "/")
        subprocess.run(get_scp_download_cmd(target, meta_remote, local_batch_dir), check=False)

    # 2. Upload Batch to GCS
    print(f"[*] Uploading batch to {gcs_bucket}...")
    gcs_target = f"{gcs_bucket}/omega/v52/frames/{host_cfg['dest_subpath']}/"
    
    cmd = ["gcloud", "storage", "cp", "-r", str(local_batch_dir) + "/*", gcs_target]
    subprocess.run(cmd, check=True)
    
    # 3. Handle .done files
    print("[*] Verifying and finalizing (.done markers)...")
    for fname, _ in files_to_sync:
        done_name = fname + ".done"
        # Always use forward slashes for SCP
        remote_path_done = f"{remote_dir}/{done_name}".replace("//", "/")
             
        res = subprocess.run(get_scp_download_cmd(target, remote_path_done, local_batch_dir), check=False)
        if res.returncode == 0:
            subprocess.run(["gcloud", "storage", "cp", str(local_batch_dir / done_name), gcs_target], check=True)

    # 4. Cleanup Buffer
    print("[*] Cleaning up local buffer...")
    shutil.rmtree(local_batch_dir)
    local_batch_dir.mkdir(parents=True, exist_ok=True)
    print("[+] Batch complete.\n")

def run_sync(bucket_name, target_host=None, year_filter=None):
    check_dependencies()
    
    hosts_to_sync = [target_host] if target_host else HOSTS.keys()
    
    for host_key in hosts_to_sync:
        if host_key not in HOSTS:
            print(f"[!] Unknown host: {host_key}")
            continue
            
        print(f"=== Starting Sync for {host_key} ===")
        files = get_remote_file_list(HOSTS[host_key], year_filter)
        
        current_batch = []
        current_batch_size = 0
        
        for fname, size in files:
            current_batch.append((fname, size))
            current_batch_size += size
            
            if current_batch_size >= BATCH_SIZE_GB * 1024 * 1024 * 1024:
                sync_batch(host_key, current_batch, bucket_name)
                current_batch = []
                current_batch_size = 0
        
        if current_batch:
            sync_batch(host_key, current_batch, bucket_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OMEGA v5.2 Mac Gateway Sync")
    parser.add_argument("--bucket", default="gs://omega_v52", help="GCS Bucket Name (default: gs://omega_v52)")
    parser.add_argument("--host", help="Specific host to sync (linux1 or windows1)")
    parser.add_argument("--year", help="Filter by year (e.g., 2025)")
    args = parser.parse_args()
    
    if not args.bucket.startswith("gs://"):
        print("[!] Bucket must start with gs://")
        sys.exit(1)

    try:
        run_sync(args.bucket, args.host, args.year)
    except KeyboardInterrupt:
        print("\n[!] Sync interrupted by user.")
        sys.exit(1)
