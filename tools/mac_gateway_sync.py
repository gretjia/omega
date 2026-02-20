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
import shutil
import sys
import re
from pathlib import Path

# --- Configuration ---
BUFFER_DIR = Path.home() / "Omega_uplink_buffer"
BATCH_SIZE_GB = 15  # Keep buffer well below free space limit
IDENTITY_FILE = Path.home() / ".ssh" / "id_ed25519"
SCP_RETRIES = 3
SCP_RETRY_SLEEP_SEC = 5
GCS_CP_CHUNK = 64

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


def detect_git_hash() -> str:
    """Best-effort local git short hash detection."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return res.stdout.strip()
    except Exception:
        return ""

def check_dependencies():
    """Ensure gcloud, scp/ssh are available."""
    if not shutil.which("gcloud"):
        print("[!] Error: 'gcloud' not found. Please install Google Cloud SDK.")
        sys.exit(1)
    if not shutil.which("ssh"):
        print("[!] Error: 'ssh' not found.")
        sys.exit(1)
    if not shutil.which("scp"):
        print("[!] Error: 'scp' not found.")
        sys.exit(1)

def get_ssh_cmd(target, command):
    """Returns the SSH command list with specific options to bypass bad config."""
    # -F /dev/null: Ignore user config (avoids BindAddress issues)
    # -o StrictHostKeyChecking=no: Auto-accept keys (safe for LAN)
    # -i ...: Identity file
    return ["ssh", "-F", "/dev/null", "-o", "StrictHostKeyChecking=no", "-i", str(IDENTITY_FILE), target, command]

def get_scp_download_cmd(target, remote_path, local_path):
    return [
        "scp",
        "-F",
        "/dev/null",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "ConnectTimeout=20",
        "-o",
        "ServerAliveInterval=15",
        "-o",
        "ServerAliveCountMax=3",
        "-i",
        str(IDENTITY_FILE),
        "-q",
        f"{target}:{remote_path}",
        str(local_path),
    ]


def scp_download_with_retry(target: str, remote_path: str, local_dir: Path, label: str) -> bool:
    """Download one file with retry; returns True on success."""
    for attempt in range(1, SCP_RETRIES + 1):
        res = subprocess.run(
            get_scp_download_cmd(target, remote_path, local_dir),
            check=False,
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            return True

        print(
            f"    [!] Download failed ({attempt}/{SCP_RETRIES}): {label} "
            f"(rc={res.returncode})"
        )
        err = (res.stderr or "").strip()
        if err:
            print(f"        {err.splitlines()[-1]}")
        if attempt < SCP_RETRIES:
            time.sleep(SCP_RETRY_SLEEP_SEC)
    return False


def upload_files_to_gcs(local_paths: list[Path], gcs_target: str) -> None:
    """Upload local files to GCS in bounded chunks."""
    if not local_paths:
        return

    for i in range(0, len(local_paths), GCS_CP_CHUNK):
        chunk = local_paths[i : i + GCS_CP_CHUNK]
        cmd = ["gcloud", "storage", "cp"] + [str(p) for p in chunk] + [gcs_target]
        subprocess.run(cmd, check=True)


def get_gcs_existing_parquet_names(gcs_bucket: str, dest_subpath: str, git_hash: str) -> set[str]:
    """
    Returns parquet filenames already present in GCS for this host/hash.
    """
    prefix = f"{gcs_bucket.rstrip('/')}/omega/v52/frames/{dest_subpath}"
    pattern = f"{prefix}/*_{git_hash}.parquet"
    cmd = ["gcloud", "storage", "ls", pattern]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return set()

    out: set[str] = set()
    for raw in res.stdout.splitlines():
        line = raw.strip()
        if not line:
            continue
        name = line.rsplit("/", 1)[-1]
        if re.match(rf".*_{re.escape(git_hash)}\.parquet$", name):
            out.add(name)
    return out

def get_remote_file_list(host_config, git_hash, year_filter=None):
    """
    Lists completed parquet files (`*.parquet` with matching `.done`) on the remote host.
    Returns a list of (filename, size_bytes).
    """
    if not git_hash:
        raise ValueError("git_hash is required")

    target = host_config["ssh_target"]
    path = host_config["source_path"]
    print(
        f"[*] Scanning {target}:{path} for completed frames (hash: {git_hash})"
        + (f" (Year: {year_filter})" if year_filter else "")
        + "..."
    )

    files = []
    
    try:
        hash_pat = f"*_{git_hash}.parquet"
        done_pat = f"*_{git_hash}.parquet.done"
        if "windows" in target.lower() or "jiazi" in target.lower():
            # Windows PowerShell: emit tagged lines so we can intersect parquet + done safely.
            win_path = path.replace('/', '\\')
            ps_cmd = (
                f"Get-ChildItem -Path '{win_path}' -Filter '{hash_pat}' "
                f"| ForEach-Object {{ 'P,' + $_.Name + ',' + $_.Length }}; "
                f"Get-ChildItem -Path '{win_path}' -Filter '{done_pat}' "
                f"| ForEach-Object {{ 'D,' + $_.Name }}"
            )
            cmd = get_ssh_cmd(target, f"powershell -NoProfile -Command \"{ps_cmd}\"")
        else:
            # Linux shell: emit tagged lines so we can intersect parquet + done safely.
            shell_cmd = (
                f"find {path} -maxdepth 1 -type f -name '{hash_pat}' -printf 'P,%f,%s\\n'; "
                f"find {path} -maxdepth 1 -type f -name '{done_pat}' -printf 'D,%f\\n'"
            )
            cmd = get_ssh_cmd(target, shell_cmd)

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        parquet_sizes = {}
        done_set = set()
        for line in result.stdout.splitlines():
            raw = line.strip()
            if not raw:
                continue
            parts = raw.split(",")
            tag = parts[0].strip() if parts else ""
            if tag == "P" and len(parts) >= 3:
                name = parts[1].strip()
                try:
                    parquet_sizes[name] = int(parts[2].strip())
                except ValueError:
                    continue
            elif tag == "D" and len(parts) >= 2:
                done_name = parts[1].strip()
                if done_name.endswith(".done"):
                    done_set.add(done_name[:-5])

        for name, size in sorted(parquet_sizes.items()):
            if year_filter and str(year_filter) not in name:
                continue
            if name in done_set:
                files.append((name, size))

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

    if local_batch_dir.exists():
        shutil.rmtree(local_batch_dir)
    local_batch_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Processing batch of {len(files_to_sync)} files from {host_key}...")
    downloaded: list[str] = []
    gcs_target = f"{gcs_bucket}/omega/v52/frames/{host_cfg['dest_subpath']}/"

    try:
        for fname, _ in files_to_sync:
            # Use forward slashes for SCP, even on Windows (OpenSSH handles it)
            remote_path = f"{remote_dir}/{fname}".replace("//", "/")
            print(f"    < Downloading: {fname}")
            ok = scp_download_with_retry(
                target=target,
                remote_path=remote_path,
                local_dir=local_batch_dir,
                label=fname,
            )
            if not ok:
                print(f"    [!] Skipping after retries: {fname}")
                continue

            downloaded.append(fname)

            # Download Meta (best effort)
            meta_name = fname + ".meta.json"
            meta_remote = f"{remote_dir}/{meta_name}".replace("//", "/")
            scp_download_with_retry(
                target=target,
                remote_path=meta_remote,
                local_dir=local_batch_dir,
                label=meta_name,
            )

        if not downloaded:
            print("[!] No parquet downloaded successfully in this batch; skipping upload.")
            return

        # 2. Upload batch payload (explicit files to avoid wildcard ambiguities)
        print(f"[*] Uploading batch to {gcs_bucket}...")
        upload_paths: list[Path] = []
        for fname in downloaded:
            pq = local_batch_dir / fname
            if pq.exists():
                upload_paths.append(pq)
            meta = local_batch_dir / (fname + ".meta.json")
            if meta.exists():
                upload_paths.append(meta)
        upload_files_to_gcs(upload_paths, gcs_target)

        # 3. Handle .done files (best effort)
        print("[*] Verifying and finalizing (.done markers)...")
        done_paths: list[Path] = []
        for fname in downloaded:
            done_name = fname + ".done"
            remote_path_done = f"{remote_dir}/{done_name}".replace("//", "/")
            ok = scp_download_with_retry(
                target=target,
                remote_path=remote_path_done,
                local_dir=local_batch_dir,
                label=done_name,
            )
            if ok:
                done_paths.append(local_batch_dir / done_name)
        upload_files_to_gcs(done_paths, gcs_target)

        print(f"[+] Batch complete. uploaded_parquet={len(downloaded)} uploaded_done={len(done_paths)}\n")
    finally:
        print("[*] Cleaning up local buffer...")
        if local_batch_dir.exists():
            shutil.rmtree(local_batch_dir)
        local_batch_dir.mkdir(parents=True, exist_ok=True)

def run_sync(bucket_name, git_hash, target_host=None, year_filter=None):
    check_dependencies()
    
    hosts_to_sync = [target_host] if target_host else HOSTS.keys()
    
    for host_key in hosts_to_sync:
        if host_key not in HOSTS:
            print(f"[!] Unknown host: {host_key}")
            continue
            
        print(f"=== Starting Sync for {host_key} ===")
        files = get_remote_file_list(HOSTS[host_key], git_hash=git_hash, year_filter=year_filter)
        existing = get_gcs_existing_parquet_names(
            gcs_bucket=bucket_name,
            dest_subpath=HOSTS[host_key]["dest_subpath"],
            git_hash=git_hash,
        )
        if existing:
            before = len(files)
            files = [item for item in files if item[0] not in existing]
            print(f"    Skipping {before - len(files)} already in GCS.")
        else:
            print("    GCS has no existing parquet for this hash/host.")

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
    parser.add_argument("--hash", default="", help="Frame git short hash suffix (default: local HEAD short hash)")
    args = parser.parse_args()
    
    if not args.bucket.startswith("gs://"):
        print("[!] Bucket must start with gs://")
        sys.exit(1)

    git_hash = args.hash.strip() or detect_git_hash()
    if not git_hash:
        print("[!] Could not determine git short hash. Pass --hash explicitly.")
        sys.exit(1)

    try:
        print(f"[*] Using frame hash filter: {git_hash}")
        run_sync(args.bucket, git_hash=git_hash, target_host=args.host, year_filter=args.year)
    except KeyboardInterrupt:
        print("\n[!] Sync interrupted by user.")
        sys.exit(1)
