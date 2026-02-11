---
name: data_download
description: Compatibility shim. Data download guidance has been merged into qmtsdk and rqsdk.
---

# Data Download (Compatibility Shim)

## Status
Deprecated as a standalone skill (merged on 2026-02-07).

Use:
- `qmtsdk` for QMT/xtquant data sync and diagnostics
- `rqsdk` for RiceQuant data retrieval/materialization

## Quick Routing

- QMT path:
  - `python tools/omega_qmt_daily_sync.py --start YYYYMMDD --end YYYYMMDD`
  - `python tools/check_qmt_status.py`
- RQ path:
  - use `rqdatac.get_price(...)`, `rqdatac.get_ticks(...)`
  - save to `./data/...` with audit metadata

Keep this file only for backward compatibility with old triggers.
