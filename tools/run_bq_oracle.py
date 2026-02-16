#!/usr/bin/env python3
"""
OMEGA v5.2 BigQuery Automation Console
--------------------------------------
Automates the "Oracle" and "Radar" SQL workflows without manual console interaction.

Usage:
    python tools/run_bq_oracle.py --setup    # Connects GCS to BigQuery
    python tools/run_bq_oracle.py --train    # Trains the XGBoost Oracle
    python tools/run_bq_oracle.py --explain  # Retrieves Feature Importance
    python tools/run_bq_oracle.py --radar    # Scans for Market Anomalies
"""

import warnings
# Suppress Google deprecation noise
warnings.filterwarnings("ignore", ".*Python version 3.9 past its end of life.*")
warnings.filterwarnings("ignore", ".*non-supported Python version.*")

import argparse
import sys
from google.cloud import bigquery

# --- Config ---
PROJECT_ID = "gen-lang-client-0250995579"
LOCATION = "us-west1"
DATASET = "omega_v52_analytics"
BUCKET = "omega_v52"

# --- SQL Definitions ---

SQL_SETUP = f"""
-- 1. Create Dataset
CREATE SCHEMA IF NOT EXISTS `{DATASET}`
OPTIONS(location='{LOCATION}');

-- 2. External Table (The Bridge)
CREATE OR REPLACE EXTERNAL TABLE `{DATASET}.frames_raw`
OPTIONS (
  format = 'PARQUET',
  uris = [
    'gs://{BUCKET}/omega/v52/frames/host=windows1/*.parquet',
    'gs://{BUCKET}/omega/v52/frames/host=linux1/*.parquet'
  ]
);

-- 3. View (The Filter)
CREATE OR REPLACE VIEW `{DATASET}.frames` AS
SELECT
  *,
  REGEXP_EXTRACT(_FILE_NAME, r'host=([^/]+)') AS host_machine,
  REGEXP_EXTRACT(_FILE_NAME, r'(\d{{8}})_') AS trade_date
FROM `{DATASET}.frames_raw`;
"""

SQL_TRAIN = f"""
CREATE OR REPLACE MODEL `{DATASET}.oracle_v1`
OPTIONS(
  model_type = 'BOOSTED_TREE_CLASSIFIER',
  input_label_cols = ['is_signal'],
  max_iterations = 50,
  data_split_method = 'RANDOM',
  data_split_eval_fraction = 0.2
) AS
SELECT
  -- Physics Scalars
  open, close, sigma, net_ofi, depth, 
  trade_vol, cancel_vol, price_change,
  sigma_eff, depth_eff, epiplexity,
  topo_area, topo_energy, srl_resid, srl_resid_050,
  adaptive_y, spoof_ratio, sigma_gate,
  topo_micro, topo_classic, topo_trend,
  -- Cast Booleans
  CAST(is_energy_active AS INT64) as is_energy_active,
  -- Target
  is_signal
FROM `{DATASET}.frames`
WHERE trade_date BETWEEN '20230101' AND '20241231'
  AND RAND() < 0.1; -- 10% Sample for speed
"""

SQL_EXPLAIN = f"""
SELECT
  *
FROM
  ML.FEATURE_IMPORTANCE(MODEL `{DATASET}.oracle_v1`)
ORDER BY
  importance_weight DESC;
"""

SQL_RADAR = f"""
WITH Stats AS (
  SELECT
    symbol,
    trade_date,
    AVG(epiplexity) as avg_epi,
    COUNTIF(is_signal = true) as signal_count 
  FROM `{DATASET}.frames`
  WHERE trade_date >= FORMAT_DATE('%Y%m%d', DATE_SUB(PARSE_DATE('%Y%m%d', (SELECT MAX(trade_date) FROM `{DATASET}.frames`)), INTERVAL 7 DAY))
  GROUP BY symbol, trade_date
),
Changes AS (
  SELECT
    symbol,
    trade_date,
    avg_epi,
    signal_count,
    (avg_epi - LAG(avg_epi) OVER (PARTITION BY symbol ORDER BY trade_date)) / NULLIF(LAG(avg_epi) OVER (PARTITION BY symbol ORDER BY trade_date), 0) as epi_surge_pct
  FROM Stats
)
SELECT
  symbol,
  trade_date,
  ROUND(avg_epi, 4) as structure_score,
  ROUND(epi_surge_pct * 100, 1) as surge_pct,
  signal_count
FROM Changes
WHERE trade_date = (SELECT MAX(trade_date) FROM Stats)
  AND epi_surge_pct > 0.3
ORDER BY
  epi_surge_pct DESC
LIMIT 20;
"""

def run_query(client, sql, description):
    print(f"[*] {description}...")
    try:
        query_job = client.query(sql)  # Make an API request.
        result = query_job.result()  # Wait for the job to complete.
        print(f"[+] Done.")
        return result
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action="store_true", help="Setup Tables")
    parser.add_argument("--train", action="store_true", help="Train Oracle")
    parser.add_argument("--explain", action="store_true", help="Explain Model")
    parser.add_argument("--radar", action="store_true", help="Run Radar Scan")
    args = parser.parse_args()

    client = bigquery.Client(project=PROJECT_ID, location=LOCATION)

    if args.setup:
        run_query(client, SQL_SETUP, "Setting up BigQuery Environment")
    
    if args.train:
        run_query(client, SQL_TRAIN, "Training Oracle (This may take minutes)")
        
    if args.explain:
        res = run_query(client, SQL_EXPLAIN, "Asking Oracle for Secrets")
        if res:
            print("\n--- ORACLE FEATURE IMPORTANCE ---")
            for row in res:
                print(f"{row.feature:<30} | {row.importance_weight:.4f}")

    if args.radar:
        res = run_query(client, SQL_RADAR, "Scanning Market Radar")
        if res:
            print("\n--- EPIPLEXITY SURGE RADAR ---")
            print(f"{ 'SYMBOL':<10} | {'DATE':<10} | {'EPI_AVG':<10} | {'SURGE%':<10} | {'SIGNALS'}")
            for row in res:
                print(f"{row.symbol:<10} | {row.trade_date:<10} | {row.structure_score:<10} | {row.surge_pct:<10} | {row.signal_count}")

if __name__ == "__main__":
    main()
