---
name: data_integrity_guard
description: Guard rails for data pipeline safety, schema contracts, and atomic writes.
---

# Skill: data_integrity_guard

## When To Use

- Modifying Stage 1 ETL or Stage 2 physics pipeline
- Changing parquet read/write logic
- Adding new data sources or modifying schema
- Debugging data corruption or missing files

## Core Rules

1. **Atomic writes**: Always write to `.tmp` first, then `os.rename()` to final path. Never write directly to the final file — a crash mid-write corrupts the parquet.
2. **Done markers**: When a file is fully processed, create `filename.parquet.done` alongside it. This enables resume without reprocessing.
3. **Fail ledger**: Failed files are recorded in a `fail_ledger.json`. Check it before retrying — the error may be deterministic (pathological symbol, OOM).
4. **Schema first**: Before bulk processing, validate schema on the *first* file. Catch `ColumnNotFoundError` before burning hours.

## Schema Contract

Stage 1 output (base L1):

```
Required: symbol, date, time_end, close, volume, bid_v1, ask_v1, ...
```

Stage 2 output (features L2):

```
Required: all Stage 1 columns + srl_resid, implied_y, topo_micro, topo_classic,
          epiplexity, effective_depth, spoof_ratio, ...
```

## Progress Monitoring

```bash
# Quick check: how many files processed?
python3 tools/cluster_health.py --quick

# Manual check on Linux:
ls /omega_pool/parquet_data/v62_feature_l2/host=linux1/*.parquet.done | wc -l
ls /omega_pool/parquet_data/v62_base_l1/host=linux1/*.parquet | wc -l
```

## Lessons from Production

- **Stage 2 total ≠ Stage 2 done count**. Stage 2 progress = done files / Stage 1 input files (not Stage 2 output files, where done==parquet always)
- **Timeout files**: Some symbols (pathological market data) consistently timeout at 5400s. These go in the fail ledger — don't keep retrying
- **Cross-symbol diff bleeding**: When computing `lob_flux` (bid/ask volume deltas), always isolate by symbol to prevent phantom values at stock boundaries
