
import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path
from multiprocessing import Pool, cpu_count
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("integrity_check.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def check_7z_installed():
    for cmd in ["7z", "7zz"]:
        try:
            subprocess.run([cmd, "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return cmd
        except FileNotFoundError:
            continue
    return None

SEVEN_Z_CMD = check_7z_installed()

def verify_file(file_path):
    if not SEVEN_Z_CMD:
        return (file_path, False, "7z not installed")
        
    try:
        # t = test, -bso0 = quiet stdout, -bsp0 = quiet progress
        start = time.time()
        res = subprocess.run(
            [SEVEN_Z_CMD, "t", "-bso0", "-bsp0", str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = time.time() - start
        
        if res.returncode == 0:
            return (file_path, True, f"OK ({duration:.2f}s)")
        else:
            return (file_path, False, f"FAILED: {res.stderr.strip() or 'Exit Code ' + str(res.returncode)}")
            
    except Exception as e:
        return (file_path, False, f"ERROR: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Verify 7z/zip integrity recursively")
    parser.add_argument("root_dir", help="Root directory to scan")
    parser.add_argument("--workers", type=int, default=max(1, cpu_count() - 2), help="Number of workers")
    parser.add_argument("--ext", default=".7z", help="Extension to check (default .7z)")
    
    args = parser.parse_args()
    
    if not SEVEN_Z_CMD:
        logging.error("7z or 7zz command not found in PATH. Please install p7zip.")
        sys.exit(1)
        
    root = Path(args.root_dir)
    if not root.exists():
        logging.error(f"Root dir {root} does not exist.")
        sys.exit(1)
        
    logging.info(f"Scanning {root} for {args.ext}...")
    files = list(root.rglob(f"*{args.ext}"))
    logging.info(f"Found {len(files)} files. Starting verification with {args.workers} workers.")
    
    failures = []
    
    with Pool(args.workers) as pool:
        for i, (fpath, success, msg) in enumerate(pool.imap_unordered(verify_file, files)):
            if success:
                logging.info(f"[{i+1}/{len(files)}] {fpath.name}: PASSED")
            else:
                logging.error(f"[{i+1}/{len(files)}] {fpath.name}: {msg}")
                failures.append((fpath, msg))
                
    logging.info(f"Verification complete. {len(files) - len(failures)} passed, {len(failures)} failed.")
    
    if failures:
        logging.error("Failures:")
        for f, m in failures:
            logging.error(f"  {f}: {m}")
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
