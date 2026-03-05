#!/usr/bin/env python3
import os
import sys
import glob
import shutil
import subprocess
import time
import json
import polars as pl
from pathlib import Path

# Paths
L1_BASE_DIR = "/omega_pool/parquet_data/latest_base_l1/host=linux1"
SMOKE_L1_DIR = "/omega_pool/smoke_v64/l1"
SMOKE_L2_DIR = "/omega_pool/smoke_v64/l2"
SMOKE_L3_DIR = "/omega_pool/smoke_v64/l3"
SMOKE_MODEL_DIR = "/omega_pool/smoke_v64/model"
REPO_ROOT = Path(__file__).resolve().parent.parent

def main():
    print("=== V64 EXTREMISTAN END-TO-END PIPELINE SMOKE TEST ===", flush=True)
    
    # 1. Setup Data
    for d in [SMOKE_L1_DIR, SMOKE_L2_DIR, SMOKE_L3_DIR, SMOKE_MODEL_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)
    
    l1_files = sorted(glob.glob(f"{L1_BASE_DIR}/*.parquet"))
    if not l1_files:
        print(f"[!] No L1 files found in {L1_BASE_DIR}")
        sys.exit(1)
        
    test_files = l1_files[:2] # Take 2 days to ensure t+1 target calculation works
    for f in test_files:
        dest = os.path.join(SMOKE_L1_DIR, "tiny_" + os.path.basename(f))
        print(f"[*] Slicing 5 liquid symbols from {f} for fast smoke test...", flush=True)
        # We explicitly pick liquid symbols to ensure they have >120 ticks to pass warm-up mask
        liquid_syms = ["000001.SZ", "510300.SH", "600036.SH", "000858.SZ", "601318.SH"]
        lf = pl.scan_parquet(f)
        df_tiny = lf.filter(pl.col("symbol").is_in(liquid_syms)).collect()
        df_tiny.write_parquet(dest)
            
    print(f"[*] Stage 1 Data prepared: 2 tiny files created in {SMOKE_L1_DIR}.", flush=True)
    
    # 2. Stage 2 (Physics Compute)
    print("\n[*] Running Stage 2 (Physics Compute)...", flush=True)
    cmd_stage2 = [
        sys.executable, str(REPO_ROOT / "tools/stage2_physics_compute.py"),
        "--input-dir", SMOKE_L1_DIR,
        "--output-dir", SMOKE_L2_DIR,
        "--workers", "2"
    ]
    env = os.environ.copy()
    env["OMEGA_STAGE2_ALLOW_USER_SLICE"] = "1"
    subprocess.run(cmd_stage2, check=True, env=env)
    
    l2_files = list(glob.glob(f"{SMOKE_L2_DIR}/*.parquet.done"))
    if not l2_files:
        print("[!] Stage 2 failed to produce .done files.")
        sys.exit(1)
    
    sample_l2 = l2_files[0].replace(".done", "")
    df_l2 = pl.read_parquet(sample_l2)
    if "singularity_vector" not in df_l2.columns:
        print("[!] Stage 2 output is missing 'singularity_vector' column. V64 injection failed!")
        sys.exit(1)
    print(f"[+] Stage 2 completed successfully. '{os.path.basename(sample_l2)}' has singularity_vector.", flush=True)
    
    # 3. Stage 3 (Base Matrix Forging)
    print("\n[*] Running Stage 3 (Base Matrix Forging)...", flush=True)
    base_matrix_out = os.path.join(SMOKE_L3_DIR, "base_matrix.parquet")
    cmd_stage3 = [
        sys.executable, str(REPO_ROOT / "tools/forge_base_matrix.py"),
        "--input-pattern", f"{SMOKE_L2_DIR}/tiny_*.parquet",
        "--output-parquet", base_matrix_out,
        "--symbols-per-batch", "50",
        "--max-workers", "2",
        "--no-resume",
        "--peace-threshold", "-0.1",
        "--peace-threshold-baseline", "-0.1"
    ]
    subprocess.run(cmd_stage3, check=True)
    
    if not os.path.exists(base_matrix_out):
        print("[!] Stage 3 failed to produce base_matrix.parquet.")
        sys.exit(1)
        
    df_l3 = pl.read_parquet(base_matrix_out)
    if "singularity_vector" not in df_l3.columns:
        print("[!] Stage 3 output is missing 'singularity_vector' column. V64 preservation failed!")
        sys.exit(1)
    print(f"[+] Stage 3 completed successfully. Base Matrix rows: {df_l3.height}. 'singularity_vector' preserved.", flush=True)
    
    # 4. Mock Vertex Training locally
    print("\n[*] Running Vertex Training mock (Local)...", flush=True)
    cmd_train = [
        sys.executable, str(REPO_ROOT / "tools/run_vertex_xgb_train.py"),
        f"--base-matrix-uri={base_matrix_out}",
        "--output-uri", SMOKE_MODEL_DIR,
        "--code-bundle-uri=", # empty means skip bootstrap codebase
        "--peace-threshold", "-0.1",
        "--num-boost-round", "2",
        "--xgb-max-depth", "3"
    ]
    
    # Needs CLOUD_ML_REGION="us-central1" due to Data Gravity Tax check in script
    env = os.environ.copy()
    env["CLOUD_ML_REGION"] = "us-central1"
    
    subprocess.run(cmd_train, check=True, env=env, cwd=str(REPO_ROOT))
    
    model_path = os.path.join(SMOKE_MODEL_DIR, "omega_xgb_final.pkl")
    if not os.path.exists(model_path):
        print("[!] Vertex Training failed to produce model.")
        sys.exit(1)
        
    print(f"[+] Vertex Training mock successful! Model produced at {model_path}.")
    print("\n=== V64 EXTREMISTAN END-TO-END SMOKE TEST PASSED ===")
    
    # Cleanup
    # for d in [SMOKE_L1_DIR, SMOKE_L2_DIR, SMOKE_L3_DIR, SMOKE_MODEL_DIR]:
    #     shutil.rmtree(d)

if __name__ == "__main__":
    main()