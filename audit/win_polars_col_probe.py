import polars as pl
import pyarrow.parquet as pq
p=r'D:\Omega_frames\v62_base_l1\host=windows1\20250828_b07c2229.parquet'
cols=pq.ParquetFile(p).schema.names
bad=[]
for c in cols:
    try:
        pl.scan_parquet(p).select(pl.col(c)).limit(5).collect()
    except BaseException as e:
        bad.append((c, type(e).__name__, str(e)[:200]))
print('bad_count', len(bad))
for x in bad:
    print(x)
