#!/usr/bin/env python3
"""
OMEGA v5.2 Data Sync Tool (GCP Upload)
--------------------------------------
A robust wrapper around 'gcloud storage rsync' to synchronize local
Parquet feature frames to the Google Cloud Storage Data Lake.

Usage:
    python tools/gcp_upload.py --source ./data/parquet --bucket gs://omega-data-lake/features

Prerequisites:
    1. Google Cloud SDK installed and authenticated (gcloud auth login).
    2. A GCS bucket created.
"""

import argparse
import subprocess
import sys
import shutil
from pathlib import Path

def check_gcloud_installed():
    """Verifies that 'gcloud' is in the system PATH."""
    if not shutil.which("gcloud"):
        print("Error: 'gcloud' command not found. Please install the Google Cloud SDK.")
        print("Visit: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)

def sync_to_gcs(source_dir, gcs_bucket_path, dry_run=False):
    """
    Synchronizes a local directory to a GCS bucket using 'gcloud storage rsync'.
    
    Args:
        source_dir (str): Local path to the directory.
        gcs_bucket_path (str): GCS URI (e.g., gs://my-bucket/path).
        dry_run (bool): If True, only shows what would be copied.
    """
    source_path = Path(source_dir).resolve()
    if not source_path.exists():
        print(f"Error: Source directory '{source_path}' does not exist.")
        sys.exit(1)

    print(f"[*] Starting sync from local: {source_path}")
    print(f"[*] Target GCS bucket:      {gcs_bucket_path}")

    # Construct the gcloud command
    # -r: recursive
    # -d: delete extra files in destination (mirroring) - OPTIONAL, usually safer NOT to use -d for data lakes unless specified
    # We will NOT use -d by default to avoid accidental data loss.
    # --parallel: usage of multiple threads/processes
    cmd = [
        "gcloud", "storage", "rsync",
        "-r",  # Recursive
        str(source_path),
        gcs_bucket_path
    ]

    if dry_run:
        cmd.append("--dry-run")
        print("[*] DRY RUN MODE: No changes will be made.")

    try:
        # Check if 'gcloud storage' is available (newer CLI), otherwise fall back to 'gsutil rsync'
        # Actually 'gcloud storage' is the modern standard.
        print(f"[*] Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("\n[+] Sync completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Sync failed with exit code {e.returncode}")
        print("    Please check your network connection and GCS permissions.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OMEGA v5.2 GCP Upload Tool")
    parser.add_argument("--source", required=True, help="Local directory containing Parquet files")
    parser.add_argument("--bucket", required=True, help="Target GCS URI (e.g., gs://omega-data-lake/features)")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run to see what would happen")

    args = parser.parse_args()

    check_gcloud_installed()
    sync_to_gcs(args.source, args.bucket, args.dry_run)
