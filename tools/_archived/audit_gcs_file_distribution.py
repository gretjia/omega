#!/usr/bin/env python3
"""
OMEGA v5.2 GCS Data Audit
-------------------------
Scans the GCS bucket and reports file counts per host/year/month.
Identifies gaps in the "God View" dataset.

Usage:
    python tools/audit_gcs_file_distribution.py
"""

import subprocess
import re
import sys
from collections import defaultdict

BUCKET = "gs://omega_v52_central/omega/v52/frames"

def get_file_list():
    print(f"[*] Scanning {BUCKET} recursively...")
    # Use gsutil ls -r because gcloud storage ls output format varies
    cmd = ["gsutil", "ls", "-r", f"{BUCKET}/**.parquet"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"[!] Error listing GCS: {e.stderr}")
        return []

def parse_files(file_list):
    # Map: host -> year -> month -> count
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    # Regex: .../host=([^/]+)/(\d{4})(\d{2})\d{2}_.*\.parquet
    pattern = re.compile(r"host=([^/]+)/(\d{4})(\d{2})\d{2}_")
    
    for f in file_list:
        match = pattern.search(f)
        if match:
            host, year, month = match.groups()
            stats[host][year][month] += 1
            
    return stats

def print_report(stats):
    print("\n--- OMEGA v5.2 Data Distribution Report ---")
    
    hosts = sorted(stats.keys())
    for host in hosts:
        print(f"\n[Host: {host}]")
        years = sorted(stats[host].keys())
        for year in years:
            total_year = sum(stats[host][year].values())
            print(f"  Year {year}: {total_year} files")
            
            months = sorted(stats[host][year].keys())
            line = "    "
            for m in months:
                count = stats[host][year][m]
                line += f"{m}: {count:2d} | "
            print(line)

def main():
    files = get_file_list()
    if not files:
        print("[!] No parquet files found.")
        sys.exit(1)
        
    print(f"[+] Found {len(files)} total parquet files.")
    stats = parse_files(files)
    print_report(stats)

if __name__ == "__main__":
    main()
