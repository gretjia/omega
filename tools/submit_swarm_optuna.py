#!/usr/bin/env python3
"""
OMEGA v5.2 Swarm Launcher
-------------------------
Launches 15 independent Spot Instances on Vertex AI.
Each instance runs a full Optuna study (50 trials) locally in RAM.
Output: best_params_*.json to GCS.

Usage:
    python tools/submit_swarm_optuna.py
"""

import warnings
warnings.filterwarnings("ignore")

import subprocess
import time
import sys

# --- Config ---
N_WORKERS = 15
PROJECT_ID = "gen-lang-client-0250995579"
REGION = "us-west1"
BUCKET_NAME = "omega_v52"
IMAGE_URI = "python:3.10" # Use 3.10 for better compatibility
MACHINE_TYPE = "n1-standard-4"

def submit_job(worker_id):
    job_name = f"swarm-v52-w{worker_id:02d}"
    output_uri = f"gs://{BUCKET_NAME}/staging/results/best_params_{job_name}.json"
    
    # The command to run inside the container
    # 1. Install download lib
    # 2. Download payload script
    # 3. Run payload script
    
    cmd = [
        "sh", "-c",
        f"pip install google-cloud-storage && "
        f"python3 -c \"from google.cloud import storage; storage.Client().bucket('{BUCKET_NAME}').blob('staging/code/run_optuna_sweep.py').download_to_filename('run_optuna_sweep.py')\" && "
        f"python3 run_optuna_sweep.py --n-trials 50 --output-uri {output_uri}"
    ]
    
    # Construct gcloud command
    gcloud_cmd = [
        "gcloud", "ai", "custom-jobs", "create",
        f"--display-name={job_name}",
        f"--region={REGION}",
        f"--project={PROJECT_ID}",
        f"--worker-pool-spec=machine-type={MACHINE_TYPE},replica-count=1,container-image-uri={IMAGE_URI}",
        f"--args={cmd[2]}" # Pass the long command string as argument to sh -c
    ]
    # We need to construct the args carefully.
    # gcloud syntax: --command="sh" --args="-c","LONG STRING"
    
    final_cmd = [
        "gcloud", "ai", "custom-jobs", "create",
        f"--display-name={job_name}",
        f"--region={REGION}",
        f"--project={PROJECT_ID}",
        f"--worker-pool-spec=machine-type={MACHINE_TYPE},replica-count=1,container-image-uri={IMAGE_URI}",
        '--command=sh',
        f'--args=-c,{cmd[2]}'
    ]
    
    print(f"[*] Launching Worker {worker_id} ({job_name})...")
    try:
        subprocess.check_call(final_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[+] Worker {worker_id} Deployed.")
    except subprocess.CalledProcessError:
        print(f"[!] Worker {worker_id} FAILED to launch.")

def main():
    print(f"--- Launching OMEGA Swarm ({N_WORKERS} Drones) ---")
    for i in range(1, N_WORKERS + 1):
        submit_job(i)
        time.sleep(1) # Gentle spacing
    print("\n[***] Swarm Airborne. ETA 20-30 mins.")
    print(f"Monitor at: https://console.cloud.google.com/vertex-ai/training/custom-jobs?project={PROJECT_ID}")

if __name__ == "__main__":
    main()
