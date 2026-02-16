#!/usr/bin/env python3
"""
OMEGA v5.2 Backtest Launcher
----------------------------
Submits the Backtest Job to Vertex AI.
"""

import subprocess
import time

# --- Config ---
PROJECT_ID = "gen-lang-client-0250995579"
REGION = "us-west1"
BUCKET_NAME = "omega_v52"
IMAGE_URI = "python:3.10"
MACHINE_TYPE = "n1-standard-4"
JOB_NAME = "omega-backtest-v52-final-retry-3"

def main():
    print(f"--- Launching OMEGA Backtest ({JOB_NAME}) ---")
    
    # Upload payload
    subprocess.check_call(["gsutil", "cp", "tools/run_cloud_backtest.py", f"gs://{BUCKET_NAME}/staging/code/run_cloud_backtest.py"])
    
    cmd = [
        "sh", "-c",
        f"pip install google-cloud-storage && "
        f"python3 -c \"from google.cloud import storage; storage.Client().bucket('{BUCKET_NAME}').blob('staging/code/run_cloud_backtest.py').download_to_filename('run_cloud_backtest.py')\" && "
        f"python3 run_cloud_backtest.py"
    ]
    
    gcloud_cmd = [
        "gcloud", "ai", "custom-jobs", "create",
        f"--display-name={JOB_NAME}",
        f"--region={REGION}",
        f"--project={PROJECT_ID}",
        f"--worker-pool-spec=machine-type={MACHINE_TYPE},replica-count=1,container-image-uri={IMAGE_URI}",
        '--command=sh',
        f'--args=-c,{cmd[2]}'
    ]
    
    try:
        subprocess.check_call(gcloud_cmd)
        print(f"[+] Backtest Deployed.")
        print(f"Monitor at: https://console.cloud.google.com/vertex-ai/training/custom-jobs?project={PROJECT_ID}")
    except subprocess.CalledProcessError:
        print(f"[!] Backtest FAILED to launch.")

if __name__ == "__main__":
    main()
