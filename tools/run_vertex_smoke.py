
import argparse
import sys
import subprocess
from google.cloud import aiplatform

# --- Configuration ---
# Uses the project/bucket you provided
PROJECT_ID = "gen-lang-client-0250995579"
LOCATION = "us-west1"
STAGING_BUCKET = "gs://omega_v52/staging"
TIMESTAMP = "20260216_smoke"

# --- The Actual Training Code to Run on Vertex ---
# We embed this as a string to write it to a file, then submit that file.
TRAINING_SCRIPT_CONTENT = """
import logging
import os
import sys
import subprocess

# Install dependencies on the fly (Vertex Custom Job environment)
def install_dependencies():
    logging.info("Installing dependencies: polars gcsfs")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "polars", "gcsfs", "fsspec"])

install_dependencies()

import polars as pl
import gcsfs
from sklearn.linear_model import SGDClassifier
import numpy as np

# Setup Logging
logging.basicConfig(level=logging.INFO)

def run_smoke_test():
    logging.info("--- OMEGA v5.2 Cloud Smoke Test ---")
    
    # 1. Define GCS Pattern (Looking for ANY uploaded frame)
    # We use a wildcard to find at least one file.
    gcs_pattern = "gs://omega_v52/omega/v52/frames/host=*/*_4f9c786.parquet"
    
    logging.info(f"Scanning for files matching: {gcs_pattern}")
    
    try:
        # Use Polars to scan (lazy) then take 1 file
        # We need to find a concrete file first because scan_parquet with wildcard might be heavy if not careful,
        # but for smoke test, let's just try to read ONE specific file if we can list them, 
        # or rely on Polars globbing.
        
        # Use gcsfs to list one file to be safe and fast
        fs = gcsfs.GCSFileSystem()
        files = fs.glob(gcs_pattern)
        
        if not files:
            logging.error("No Parquet files found in GCS! Upload might have failed.")
            sys.exit(1)
            
        target_file = "gs://" + files[0]
        logging.info(f"Targeting specific file: {target_file}")
        
        # 2. Load Data
        logging.info("Reading Parquet file...")
        df = pl.read_parquet(target_file)
        logging.info(f"Successfully read dataframe. Shape: {df.shape}")
        
        if df.is_empty():
            logging.error("Dataframe is empty!")
            sys.exit(1)

        # 3. Dummy Training
        logging.info("Simulating Training Step (partial_fit)...")
        
        # Assume some feature columns exist (float/int). 
        # For smoke test, we just select numeric columns.
        numeric_cols = [c for c, t in df.schema.items() if t in (pl.Float32, pl.Float64, pl.Int32, pl.Int64)]
        
        if not numeric_cols:
            logging.warning("No numeric columns found. Creating dummy data.")
            X = np.random.rand(10, 5)
        else:
            # Take top 5 numeric cols, top 100 rows to save memory
            X = df.select(numeric_cols[:5]).head(100).to_numpy()
            # Handle NaNs if any (simple fill)
            X = np.nan_to_num(X)
            
        # Dummy target
        y = np.random.randint(0, 2, size=X.shape[0])
        
        # Use 'log' instead of 'log_loss' for backward compatibility with older sklearn in container
        model = SGDClassifier(loss="log")
        model.partial_fit(X, y, classes=np.array([0, 1]))
        
        logging.info("Model partial_fit completed successfully.")
        logging.info("--- Smoke Test PASSED ---")

    except Exception as e:
        logging.error(f"Smoke Test FAILED with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_smoke_test()
"""

def create_and_submit_job():
    # 1. Write the script locally
    script_path = "smoke_test_payload.py"
    with open(script_path, "w") as f:
        f.write(TRAINING_SCRIPT_CONTENT)
    
    print(f"[*] Created payload: {script_path}")

    # 2. Initialize Vertex AI
    print(f"[*] Initializing Vertex AI (Project: {PROJECT_ID}, Region: {LOCATION})")
    aiplatform.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET
    )

    # 3. Create Custom Job
    # We use a standard pre-built image. We pip install extra libs inside the script.
    job = aiplatform.CustomJob.from_local_script(
        display_name=f"omega-smoke-{TIMESTAMP}",
        script_path=script_path,
        container_uri="us-docker.pkg.dev/vertex-ai/training/scikit-learn-cpu.0-23:latest",
        requirements=[], # We install inside script to be sure
        replica_count=1,
        machine_type="n1-standard-4", # Small machine for smoke test
    )

    # 4. Submit
    print("[*] Submitting Smoke Test to Vertex AI...")
    job.run(sync=True) # Block until complete to give user immediate feedback
    
    print("[+] Job completed.")
    
    # Cleanup
    if os.path.exists(script_path):
        os.remove(script_path)

if __name__ == "__main__":
    create_and_submit_job()
