import polars as pl
import datetime
df = pl.DataFrame({"__time_ms": [1000, 2000, 3000, 4000, 5000, 10000], "v_ofi": [1, 2, 3, 4, 5, 20]})

df = df.with_columns(
    pl.from_epoch(pl.col("__time_ms"), time_unit="ms").alias("timestamp_dt")
)

df = df.rolling(index_column="timestamp_dt", period="3s").agg(
    pl.col("v_ofi").mean().alias("v_ofi_mean")
)
print(df)
