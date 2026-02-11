import polars as pl
import os
import glob
import sys

# Find latest parquet
output_dir = "D:/Omega_frames/v50/output"
files = sorted(glob.glob(os.path.join(output_dir, "*.parquet")), key=os.path.getmtime)
if not files:
    print("No parquet files found.")
    sys.exit(1)

path = files[-1]
print(f"Validating LATEST frame: {path}")

df = pl.read_parquet(path)

# 1. Schema Check
required_cols = ["symbol", "bucket_id", "open", "close", "epiplexity", "srl_resid", "adaptive_y"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    print(f"FAILED: Missing columns: {missing}")
else:
    print("PASSED: Schema check")

# 2. Row Count
print(f"Rows: {df.height}")
if df.height < 100000:
    print("WARNING: Row count suspiciously low for full market.")

# 3. Symbol Count
n_sym = df["symbol"].n_unique()
print(f"Symbols: {n_sym}")
if n_sym < 4000:
    print("WARNING: Symbol count low (expected >4000).")

# 4. Consistency (Bucket Monotonicity)
print("Checking Bucket Monotonicity (Sample 5 symbols)...")
sample_syms = df["symbol"].unique().head(5).to_list()
for s in sample_syms:
    sub = df.filter(pl.col("symbol") == s)
    is_sorted = sub["bucket_id"].is_sorted()
    if not is_sorted:
        print(f"FAILED: Symbol {s} bucket_id is NOT sorted!")
        print(sub.select(["time_start", "bucket_id"]).head(20))
    else:
        print(f"PASSED: Symbol {s}")

# 5. Physics Range
epi = df["epiplexity"]
print(f"Epiplexity: Min={epi.min():.4f}, Max={epi.max():.4f}, Mean={epi.mean():.4f}")
if epi.min() < 0 or epi.max() > 1.0:
    print("WARNING: Epiplexity out of range [0, 1].")

print("Validation Complete.")
