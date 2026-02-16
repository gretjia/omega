#!/usr/bin/env python3
"""
OMEGA v5.2 Swarm Log Harvester (Regex Edition)
----------------------------------------------
Retrieves "God Params" from Vertex AI logs via simple regex.
Robust to log splitting/buffering.

Usage:
    python tools/harvest_swarm_logs.py
"""

import subprocess
import json
import os
import re
import ast

JOB_FILTER = "displayName:swarm-v52i"
PROJECT_ID = "gen-lang-client-0250995579"
REGION = "us-west1"

def get_job_ids():
    print("[*] Listing Swarm Jobs...")
    cmd = [
        "gcloud", "ai", "custom-jobs", "list",
        f"--region={REGION}",
        f"--project={PROJECT_ID}",
        f"--filter={JOB_FILTER}",
        "--format=json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[!] Error listing jobs: {result.stderr}")
        return []
    
    jobs = json.loads(result.stdout)
    ids = [j['name'].split('/')[-1] for j in jobs]
    print(f"[+] Found {len(ids)} jobs.")
    return ids

def extract_from_logs(job_id):
    print(f"[*] Scanning logs for Job {job_id}...")
    cmd = [
        "gcloud", "logging", "read",
        f'resource.type=ml_job AND resource.labels.job_id={job_id} AND textPayload:"Best Params:"',
        "--limit=10",
        "--format=value(textPayload)"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    logs = result.stdout
    
    # Looking for: ... [INFO] Best Params: ({'y_ema_alpha': 0.08..., 'peace_threshold': 0.37...})
    # And Best Value
    
    params = None
    value = None
    
    # Parse Params
    match_p = re.search(r"Best Params: (\{.*\})", logs)
    if match_p:
        try:
            params = ast.literal_eval(match_p.group(1))
        except:
            print(f"[!] Failed to eval params for {job_id}")
            
    # Get Value
    cmd_v = [
        "gcloud", "logging", "read",
        f'resource.type=ml_job AND resource.labels.job_id={job_id} AND textPayload:"Best Value:"',
        "--limit=10",
        "--format=value(textPayload)"
    ]
    result_v = subprocess.run(cmd_v, capture_output=True, text=True)
    match_v = re.search(r"Best Value: ([\d\.]+)", result_v.stdout)
    if match_v:
        value = float(match_v.group(1))
        
    if params and value is not None:
        return {
            "params": params,
            "value": value,
            "job_id": job_id
        }
    return None

def main():
    job_ids = get_job_ids()
    os.makedirs("harvested_results", exist_ok=True)
    
    found_count = 0
    for jid in job_ids:
        data = extract_from_logs(jid)
        if data:
            fname = f"harvested_results/best_params_{jid}.json"
            with open(fname, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[+] Saved {fname} (Score: {data['value']:.4f})")
            
            # Upload to GCS for aggregator
            gcs_path = f"gs://omega_v52/staging/results/best_params_{jid}.json"
            subprocess.run(["gsutil", "cp", fname, gcs_path], check=True)
            found_count += 1
        else:
            print(f"[-] No data found for {jid}")
            
    print(f"\n[***] Harvest Complete. Extracted {found_count}/{len(job_ids)} results.")

if __name__ == "__main__":
    main()
