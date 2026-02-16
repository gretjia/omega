#!/usr/bin/env python3
"""
OMEGA v5.2 Swarm Intelligence Aggregator
----------------------------------------
This script aggregates the distributed findings of the Vertex AI Swarm.
It does NOT just pick the max score. It searches for "Invariant Truth".

Logic:
1. Ingests all `best_params_*.json` from GCS.
2. Identifies the "Council of Elders" (Top K runs).
3. Measures Topological Dispersion (Standard Deviation of parameters).
4. If Dispersion is LOW: Calculates Weighted Center of Mass (Robust Alpha).
5. If Dispersion is HIGH: Defaults to Global Max (Hero Alpha) with warnings.

Usage:
    python tools/aggregate_swarm_results.py
"""

import warnings
# Suppress Google deprecation noise
warnings.filterwarnings("ignore", ".*Python version 3.9 past its end of life.*")
warnings.filterwarnings("ignore", ".*non-supported Python version.*")

import json
import os
import sys
import numpy as np
import subprocess
from datetime import datetime

# --- Configuration ---
BUCKET_NAME = "omega_v52"
RESULTS_PREFIX = "staging/results/"
TOP_K = 5  # Size of the "Council of Elders"

def get_gcs_files(prefix):
    """Lists all result files in GCS."""
    cmd = ["gcloud", "storage", "ls", f"gs://{BUCKET_NAME}/{prefix}best_params_*.json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        return []

def download_and_parse(gcs_uri):
    """Downloads a JSON blob and parses it."""
    try:
        content = subprocess.run(
            ["gcloud", "storage", "cat", gcs_uri], 
            capture_output=True, text=True, check=True
        ).stdout
        return json.loads(content)
    except Exception as e:
        print(f"[!] Corrupt intelligence artifact at {gcs_uri}: {e}")
        return None

def main():
    print("--- OMEGA v5.2 Swarm Intelligence Aggregator ---")
    
    # 1. Ingest
    print(f"[*] Scanning Drop Zone: gs://{BUCKET_NAME}/{RESULTS_PREFIX}...")
    files = get_gcs_files(RESULTS_PREFIX)
    
    if not files:
        print("[!] No intelligence artifacts found. The Swarm is still hunting.")
        sys.exit(1)
        
    print(f"[*] Analyzing {len(files)} returned artifacts...")
    
    results = []
    for f in files:
        data = download_and_parse(f)
        if data and data.get('value') is not None:
            results.append(data)
            
    if not results:
        print("[!] Valid artifacts found but contained no data.")
        sys.exit(1)

    # 2. The Ranking
    # Sort by Objective Value (Model Alignment) Descending
    ranked = sorted(results, key=lambda x: x['value'], reverse=True)
    hero = ranked[0]
    
    print(f"\n[+] Hero Run (Global Max):")
    print(f"    Worker ID: {hero.get('worker_id', 'unknown')}")
    print(f"    Score:     {hero['value']:.6f}")
    print(f"    Params:    {hero['params']}")

    # 3. The Council of Elders (Consensus Logic)
    elders = ranked[:TOP_K]
    
    # Extract Vectors
    alpha_vec = np.array([r['params']['y_ema_alpha'] for r in elders])
    peace_vec = np.array([r['params']['peace_threshold'] for r in elders])
    score_vec = np.array([r['value'] for r in elders])
    
    # 4. Topological Dispersion (Stability Check)
    alpha_dispersion = np.std(alpha_vec)
    peace_dispersion = np.std(peace_vec)
    
    print(f"\n[*] Council of Elders (Top {len(elders)}):")
    print(f"    Alpha Dispersion: {alpha_dispersion:.6f}")
    print(f"    Peace Dispersion: {peace_dispersion:.6f}")
    
    # Heuristic: If dispersion is > 20% of range, we have multi-modal chaos.
    # Alpha range ~0.2, so 0.04 is high dispersion.
    STABILITY_THRESHOLD = 0.04
    
    is_stable = alpha_dispersion < STABILITY_THRESHOLD and peace_dispersion < 0.15
    
    final_params = {}
    
    if is_stable:
        print(f"    [OK] Surface is STABLE. Computing Center of Mass...")
        # Weighted Average based on Score
        # We square the scores to punish low performers in the top K slightly more
        weights = score_vec ** 2
        norm = np.sum(weights)
        
        consensus_alpha = np.sum(alpha_vec * weights) / norm
        consensus_peace = np.sum(peace_vec * weights) / norm
        
        final_params = {
            "y_ema_alpha": round(consensus_alpha, 4),
            "peace_threshold": round(consensus_peace, 4)
        }
        print(f"\n[***] ROBUST CONSENSUS PARAMETERS [***]")
    else:
        print(f"    [WARNING] Surface is CHAOTIC (Multi-modal). Consensus unsafe.")
        print(f"    [!] Defaulting to Hero Run (Global Max). High overfitting risk.")
        
        final_params = {
            "y_ema_alpha": hero['params']['y_ema_alpha'],
            "peace_threshold": hero['params']['peace_threshold']
        }
        print(f"\n[***] HERO PARAMETERS (FRAGILE) [***]")

    print(json.dumps(final_params, indent=4))
    
    # Optional: Generate config snippet
    print(f"\n--- config.py snippet ---")
    print(f"PHYSICS_Y_EMA_ALPHA = {final_params['y_ema_alpha']}")
    print(f"DECISION_PEACE_THRESHOLD = {final_params['peace_threshold']}")

if __name__ == "__main__":
    main()
