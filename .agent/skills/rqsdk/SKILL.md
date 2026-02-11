---
name: rqsdk
description: Utility for interacting with RiceQuant SDK (RQSDK) and RQData.
---

# RQSDK Skill

## Overview
This skill provides instructions and patterns for using the RiceQuant SDK (RQSDK) and RQData Python API within the OMEGA project.

## Scope
- Use this skill for RiceQuant-side data acquisition/validation workflows.
- For QMT/XTQuant syncing, use `qmtsdk`.
- This skill now includes the RQ-related part of legacy `data_download`.

## Initialization
In the `omega` Conda environment, `rqdatac` or `rqsdk` can be used. Always ensure the license is configured.

```python
import rqdatac
# Ensure initialization if required by the environment
# rqdatac.init() 
```

## Data Retrieval Patterns

### Get Real-time Price
```python
import rqdatac
price = rqdatac.current_snapshot('000001.SZ').last
```

### Get Historical Daily Bars
```python
import rqdatac
df = rqdatac.get_price('000001.SZ', start_date='20230101', end_date='20231231', frequency='1d')
```

### Get Tick Data
```python
import rqdatac
ticks = rqdatac.get_ticks('000001.SZ', start_dt='2023-01-01', end_dt='2023-01-02')
```

## Download/Materialization Practice

When materializing data for OMEGA pipelines:
1. Query with `rqdatac` / `rqsdk`.
2. Save outputs under project-relative `./data/...`.
3. Record date window, symbol universe, and command in audit/handover notes.

## Documentation Lookup
Primary index:
- `.agent/knowledge/ricequant-doc-index.md`

Compatibility fallback:
- `.claude/knowledge/ricequant-doc-index.md`

Use the index to find the correct deep-link for specific API needs (Stocks, Futures, Factors, etc.).
