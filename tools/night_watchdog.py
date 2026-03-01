#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import glob
import logging
from datetime import datetime

# --- Configuration ---
POLL_INTERVAL_SEC = 300  # 5 minutes
GCS_BUCKET = "gs://omega_central"
YEAR = "2026"
GIT_HASH = "ed6a760"

# Target directories to check for completion
# We know framing is done when the expected number of `.done` files exist.
# For Option A (1 week), we expect ~150-160 files per Node. We'll use the 
# Mac Gateway's log to see if it finishes uploading, or simply check if the 
# number of done files stops growing for 30 minutes, OR we can just run the pipeline
# and let it crash/retry.
# A better approach: Run mac_gateway_sync.py. If it finds 0 new files, AND we know 
# Linux/Windows are done, we proceed. Since ssh is running in tmux, we'll just check 
# GCS parquet count. 

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def get_gcs_parquet_count() -> int:
    """Use gsutil to count the number of parquet files currently in GCS for 2026."""
    cmd = f"gsutil ls {GCS_BUCKET}/omega/latest/frames/host=*/{YEAR}*_{GIT_HASH}.parquet | wc -l"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        count = int(result.stdout.strip())
        return count
    except Exception as e:
        logging.warning(f"Failed to count GCS parquets: {e}")
        return -1

def run_command(cmd_list, step_name):
    logging.info(f"========== STARTING PHASE: {step_name} ==========")
    cmd_str = " ".join(cmd_list)
    logging.info(f"Running: {cmd_str}")
    
    # We use Popen so we can stream output to the log
    process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with open(f"watchdog_{step_name.replace(' ', '_').lower()}.log", "w") as log_file:
        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)
            log_file.write(line)
            log_file.flush()
    
    process.wait()
    if process.returncode != 0:
        logging.error(f"PHASE FAILED: {step_name} (Exit code {process.returncode})")
        return False
    
    logging.info(f"========== PHASE SUCCESS: {step_name} ==========")
    return True

def main():
    logging.info("Starting V62 Autonomous Night Watchdog...")
    
    # PHASE 1: Wait for Framing to Complete
    # A full 5-day week for 5000+ stocks is roughly 5000 * 5 = 25,000 files. 
    # But files are batched. Usually ~140-160 parquet files per node for a full week.
    # Total expected: ~300 parquets.
    # We will wait until we see at least 250 parquets, AND the count hasn't changed in 3 polls.
    
    EXPECTED_MIN_PARQUETS = 250
    stable_count = 0
    last_count = -1
    
    while True:
        # Before counting GCS, trigger the Mac Gateway to upload anything pending
        logging.info("Triggering Mac Gateway Sync to push local frames to GCS...")
        subprocess.run(["python3", "tools/mac_gateway_sync.py", "--bucket", GCS_BUCKET, "--year", YEAR, "--hash", GIT_HASH], capture_output=True)
        
        count = get_gcs_parquet_count()
        logging.info(f"Current GCS Parquet Count for {YEAR} ({GIT_HASH}): {count}")
        
        if count >= EXPECTED_MIN_PARQUETS:
            if count == last_count:
                stable_count += 1
                logging.info(f"Count has been stable for {stable_count} polls.")
                if stable_count >= 3:
                    logging.info("Framing appears complete and stable. Proceeding to Base Matrix!")
                    break
            else:
                stable_count = 0
        
        last_count = count
        logging.info(f"Sleeping for {POLL_INTERVAL_SEC} seconds...")
        time.sleep(POLL_INTERVAL_SEC)
        
    # PHASE 2: Forge Base Matrix
    base_matrix_success = run_command([
        "python3", "tools/forge_base_matrix.py", 
        "--years", YEAR, 
        "--cpu-workers", "12"
    ], "Base Matrix Forge")
    
    if not base_matrix_success:
        logging.critical("Watchdog halting due to Base Matrix failure.")
        sys.exit(1)
        
    # PHASE 3: Optuna Swarm Optimization (MDL + Target Orthogonalization check)
    swarm_success = run_command([
        "python3", "tools/swarm_xgb.py",
        "--n-trials", "10",  # Smoke test, just 10 trials
        "--min-samples", "50000" # Explicitly testing the collapse threshold
    ], "Swarm XGBoost Smoke Test")
    
    if not swarm_success:
        logging.critical("Watchdog halting due to Swarm failure.")
        sys.exit(1)
        
    # PHASE 4: Local Backtest (Testing OOM defense & full inference)
    # We'll run it on the tiny 2026 week just to see if the engine survives
    backtest_success = run_command([
        "python3", "tools/run_local_backtest.py",
        "--years", YEAR,
        "--output-dir", "smoke_test_results"
    ], "Local Backtest Inference")
    
    if not backtest_success:
        logging.critical("Watchdog halting due to Backtest failure.")
        sys.exit(1)
        
    logging.info("🎉 All V62 Smoke Test Phases Completed Successfully! 🎉")

if __name__ == "__main__":
    main()
