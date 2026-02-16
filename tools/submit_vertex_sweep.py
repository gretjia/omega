#!/usr/bin/env python3
"""
OMEGA v5.2 Vertex AI Sweep Submitter (With Code Injection)
----------------------------------------------------------
1. Zips the local 'omega_core' module.
2. Uploads it to GCS.
3. Submits the 'run_optuna_sweep.py' payload to Vertex AI.

Usage:
    python tools/submit_vertex_sweep.py --script tools/run_optuna_sweep.py
"""

import argparse
import sys
import shutil
import os
import zipfile
import warnings
# Suppress annoying Google Cloud Python 3.9 deprecation warnings
warnings.filterwarnings("ignore", ".*Python version 3.9 past its end of life.*")
warnings.filterwarnings("ignore", ".*non-supported Python version.*")

from datetime import datetime
from google.cloud import aiplatform
from google.cloud import storage

# Defaults
PROJECT_ID = "gen-lang-client-0250995579"
REGION = "us-west1"
STAGING_BUCKET = "gs://omega_v52/staging"
CODE_BUCKET_PATH = "gs://omega_v52/staging/code/omega_core.zip"

def zip_and_upload_code(repo_root, gcs_uri):
    """
    Builds a self-contained bundle with the modules required by cloud payloads.
    Includes:
      - omega_core/
      - tools/
      - config.py
      - config_v6.py (if present)
    """
    print(f"[*] Packaging code from repo root: {repo_root}")

    include_paths = ["omega_core", "tools", "config.py", "config_v6.py"]
    archive_path = os.path.join(repo_root, "omega_core.zip")
    if os.path.exists(archive_path):
        os.remove(archive_path)

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in include_paths:
            abs_path = os.path.join(repo_root, rel)
            if not os.path.exists(abs_path):
                if rel == "config_v6.py":
                    continue
                print(f"[!] Warning: missing bundle path: {abs_path}")
                continue

            if os.path.isdir(abs_path):
                for dirpath, _, filenames in os.walk(abs_path):
                    for fn in filenames:
                        if fn.endswith((".pyc", ".pyo")):
                            continue
                        if fn == ".DS_Store":
                            continue
                        full = os.path.join(dirpath, fn)
                        arcname = os.path.relpath(full, repo_root)
                        zf.write(full, arcname=arcname)
            else:
                zf.write(abs_path, arcname=rel)

    print(f"    Created archive: {archive_path}")
    
    # Upload
    print(f"[*] Uploading to {gcs_uri}...")
    storage_client = storage.Client(project=PROJECT_ID)
    
    # Parse bucket/blob
    bucket_name = gcs_uri.replace("gs://", "").split("/")[0]
    blob_name = "/".join(gcs_uri.replace("gs://", "").split("/")[1:])
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(archive_path)
    
    print("[+] Code bundle uploaded successfully.")
    
    # Cleanup local zip
    os.remove(archive_path)

def submit_job(script_path, machine_type="c2-standard-60", script_args=None, sync=False):
    """Submits the job."""
    if script_args is None:
        script_args = []
    if not script_args and os.path.basename(script_path) == "run_optuna_sweep.py":
        script_args = ["--n-trials", "50"]
    
    aiplatform.init(
        project=PROJECT_ID,
        location=REGION,
        staging_bucket=STAGING_BUCKET
    )

    script_stem = os.path.splitext(os.path.basename(script_path))[0]
    job_name = f"omega-v60-{script_stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"[*] Submitting Custom Job: {job_name}")

    job = aiplatform.CustomJob.from_local_script(
        display_name=job_name,
        script_path=script_path,
        container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.0-23:latest",
        replica_count=1,
        machine_type=machine_type,
        args=script_args,
    )

    job.run(sync=bool(sync))
    
    print(f"\n[+] Job submitted! Check Cloud Console.")
    print(f"    Dashboard: {job.dashboard_uri}")
    print(f"    Resource : {job.resource_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, help="Payload script")
    parser.add_argument("--machine-type", default="c2-standard-60")
    parser.add_argument(
        "--script-arg",
        action="append",
        default=[],
        help="Argument forwarded to payload script (repeatable).",
    )
    parser.add_argument("--sync", action="store_true", help="Wait until Vertex job completes")
    args = parser.parse_args()

    # 1. Inject Code
    # Assumes omega_core is in CWD or ../omega_core
    # We look for it relative to this script or CWD
    repo_root = os.getcwd() # Assumption: running from repo root
    code_path = os.path.join(repo_root, "omega_core")
    
    if not os.path.exists(code_path):
        print(f"[!] Error: omega_core not found at {code_path}")
        sys.exit(1)
        
    zip_and_upload_code(repo_root, CODE_BUCKET_PATH)

    # 2. Submit Job
    submit_job(args.script, args.machine_type, script_args=args.script_arg, sync=args.sync)
