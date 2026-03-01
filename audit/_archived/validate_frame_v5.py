import polars as pl
import os
import sys

path = "D:/Omega_frames/v50/output/20230103.parquet"
if not os.path.exists(path):
    print(f"File not found: {path}")
    sys.exit(1)

print(f"Validating {path}...")
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

# 4. Completeness (Nulls)
nulls = df.null_count()
print("Null Counts:")
print(nulls)

# 5. Consistency (Bucket Monotonicity)
# Check strictly increasing bucket_id per symbol
print("Checking Bucket Monotonicity (Sample 5 symbols)...")
sample_syms = df["symbol"].unique().head(5).to_list()
for s in sample_syms:
    sub = df.filter(pl.col("symbol") == s)
    # Buckets might not be strictly 0,1,2 if volume jumped, but should be sorted if time is sorted.
    # Actually build_l2_frames sorts by time.
    # bucket_id is derived from cum_vol.
    # So bucket_id must be non-decreasing.
    is_sorted = sub["bucket_id"].is_sorted()
    if not is_sorted:
        print(f"FAILED: Symbol {s} bucket_id is NOT sorted!")
        print(sub.select(["time_start", "bucket_id"]).head(20))
    else:
        print(f"PASSED: Symbol {s}")

# 6. Physics Range
epi = df["epiplexity"]
print(f"Epiplexity: Min={epi.min()}, Max={epi.max()}, Mean={epi.mean()}")
if epi.min() < 0 or epi.max() > 1.0:
    print("WARNING: Epiplexity out of range [0, 1] (Compression Gain).")

print("Validation Complete.")
