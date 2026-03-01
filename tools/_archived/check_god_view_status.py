#!/usr/bin/env python3
"""
OMEGA v5.2 God View Status Dashboard
-----------------------------------
Checks the status of:
1. BigQuery Oracle Training (XGBoost)
2. Vertex AI Swarm Jobs (Optuna)
3. GCS Artifacts (Results)

Usage:
    python tools/check_god_view_status.py
"""

import warnings
warnings.filterwarnings("ignore")

import subprocess
import json
import sys
import time
from datetime import datetime

BUCKET_NAME = "omega_v52"
PROJECT_ID = "gen-lang-client-0250995579"
REGION = "us-west1"

def check_bq_jobs():
    print("\n--- [1] BigQuery Oracle Status ---")
    try:
        # List recent jobs
        cmd = ["bq", "ls", "-j", "-n", "5", "--format=json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[!] Error checking BigQuery: {result.stderr}")
            return

        stdout = result.stdout
        # Find the start of the JSON list
        json_start = stdout.find('[')
        if json_start != -1:
            stdout = stdout[json_start:]
            jobs = json.loads(stdout)
        else:
            print(f"[!] Could not find JSON output in: {stdout[:100]}...")
            return

        running = 0
        latest_status = "UNKNOWN"
        
        for job in jobs:
            state = job['status']['state']
            if state == 'RUNNING':
                running += 1
                print(f"  >>> Job {job['jobReference']['jobId']} is RUNNING ({job['configuration']['jobType']})")
            
            # Check for our specific Oracle training job signature if possible
            # (Hard to filter by query text in JSON list without details, but RUNNING query is a good sign)
            
        if running == 0:
            print("  [.] No active jobs. Oracle is likely sleeping or finished.")
        else:
            print(f"  [*] {running} Job(s) Crunching Data.")
            
    except Exception as e:
        print(f"  [!] Failed to parse BQ status: {e}")

def check_vertex_jobs():
    print("\n--- [2] Vertex AI Swarm Status ---")
    try:
        # List Custom Jobs
        cmd = [
            "gcloud", "ai", "custom-jobs", "list",
            f"--region={REGION}",
            f"--project={PROJECT_ID}",
            "--filter=state=JOB_STATE_RUNNING OR state=JOB_STATE_PENDING",
            "--limit=20",
            "--format=json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[!] Error checking Vertex AI: {result.stderr}")
            return
            
        jobs = json.loads(result.stdout)
        
        if not jobs:
            print("  [.] No Active Swarm Jobs. (Did they finish or fail?)")
        else:
            states = {}
            for j in jobs:
                s = j['state']
                states[s] = states.get(s, 0) + 1
            
            print(f"  [*] Active Drones: {len(jobs)}")
            for s, count in states.items():
                print(f"      - {s}: {count}")

    except Exception as e:
        print(f"  [!] Failed to parse Vertex status: {e}")

def check_gcs_artifacts():
    print("\n--- [3] Intelligence Artifacts (GCS) ---")
    try:
        cmd = ["gsutil", "ls", f"gs://{BUCKET_NAME}/staging/results/best_params_*.json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("  [.] No artifacts found yet.")
        else:
            files = result.stdout.strip().splitlines()
            print(f"  [+] Found {len(files)} 'best_params' JSON files.")
            print(f"      Latest: {files[-1] if files else 'None'}")
            
    except Exception as e:
        print(f"  [!] Failed to check GCS: {e}")

def main():
    print(f"OMEGA v5.2 God View Monitor | {datetime.now().strftime('%H:%M:%S')}")
    check_bq_jobs()
    check_vertex_jobs()
    check_gcs_artifacts()
    print("\n-----------------------------------")

if __name__ == "__main__":
    main()
