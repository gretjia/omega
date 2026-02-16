-- OMEGA v5.2 BigQuery Oracle & Radar
-- ===================================
-- The Vibe: No Python. No Pipelines. Pure SQL.
-- Copy-paste these blocks into https://console.cloud.google.com/bigquery

-- -----------------------------------------------------------------------------
-- BLOCK 1: The "External Table" Setup (Connecting GCS Parquet to SQL)
-- -----------------------------------------------------------------------------
-- 1. Create a Dataset (Folder) in BigQuery
CREATE SCHEMA IF NOT EXISTS `omega_v52_analytics`
OPTIONS(location='us-west1');

-- 2. Mount GCS Parquet as a Virtual Table (Zero Copy, Zero Cost until queried)
-- Replace 'omega_v52' with your actual bucket name if different.
CREATE OR REPLACE EXTERNAL TABLE `omega_v52_analytics.frames_raw`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://omega_v52/omega/v52/frames/host=*/*.parquet']
);

-- 3. Create a clean View to parse metadata from filenames
CREATE OR REPLACE VIEW `omega_v52_analytics.frames` AS
SELECT
  *,
  -- Parse host from hive partition (e.g., host=windows1)
  REGEXP_EXTRACT(_FILE_NAME, r'host=([^/]+)') AS host_machine,
  -- Parse date from filename (e.g., 20251231_4f9c786.parquet)
  REGEXP_EXTRACT(_FILE_NAME, r'(\d{8})_') AS trade_date
FROM `omega_v52_analytics.frames_raw`;


-- -----------------------------------------------------------------------------
-- BLOCK 2: The "Non-Linear Oracle" (AutoML -> Interaction Terms)
-- -----------------------------------------------------------------------------
-- 1. Train the Oracle (Boosted Tree Classifier)
-- This asks Google to train an XGBoost model on your data to find what matters.
CREATE OR REPLACE MODEL `omega_v52_analytics.oracle_v1`
OPTIONS(
  model_type = 'BOOSTED_TREE_CLASSIFIER',
  -- We predict 'is_signal' or whatever your target column is named (e.g., 'target_1d')
  -- Ensure this column exists in your Parquet files!
  input_label_cols = ['target'], 
  max_iterations = 50,
  data_split_method = 'RANDOM',
  data_split_eval_fraction = 0.2
) AS
SELECT
  * EXCEPT(host_machine, trade_date, _FILE_NAME) -- Use all features, ignore metadata
FROM `omega_v52_analytics.frames`
WHERE trade_date >= '20240101' -- Focus on recent regime
  AND RAND() < 0.1; -- Sample 10% of rows for speed/cost efficiency

-- 2. Ask the Oracle: "What matters?"
-- This extracts the Global Feature Importance. Look for interactions!
SELECT
  *
FROM
  ML.GLOBAL_EXPLAIN(MODEL `omega_v52_analytics.oracle_v1`)
ORDER BY
  attribution DESC;


-- -----------------------------------------------------------------------------
-- BLOCK 3: The "Crowding Radar" (Epiplexity Surge)
-- -----------------------------------------------------------------------------
-- Finds stocks where structural entropy (Epiplexity) is skyrocketing.
-- This indicates a "Phase Transition" or "Crowded Trade".

WITH Stats AS (
  SELECT
    symbol,
    trade_date,
    AVG(epiplexity) as avg_epi,
    -- Count how many times your signal fired today
    COUNTIF(target = 1) as signal_count 
  FROM `omega_v52_analytics.frames`
  -- Look at the last 5 trading days
  WHERE trade_date >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY))
  GROUP BY symbol, trade_date
),
Changes AS (
  SELECT
    symbol,
    trade_date,
    avg_epi,
    signal_count,
    -- Calculate Day-over-Day Epiplexity Surge %
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
-- Filter for the latest date available in data
WHERE trade_date = (SELECT MAX(trade_date) FROM Stats)
  AND epi_surge_pct > 0.3 -- Filter: Surge > 30%
ORDER BY
  epi_surge_pct DESC
LIMIT 20;
