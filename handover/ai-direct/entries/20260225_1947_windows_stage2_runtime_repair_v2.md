---
entry_id: 20260225_1947_windows_stage2_runtime_repair_v2
created_at: 2026-02-25 19:47 +0800
author: codex
---

## Summary
- Objective: fix recurring Windows Stage2 stop/crash behavior and recover deterministic progress.
- Outcome: landed runtime repair v2, validated with smoke, and relaunched backlog processing.

## Evidence
- Historic crash signature (pre-fix): Windows `Application Error` / `WER` with `_polars_runtime.pyd`, `0xc0000005`.
- Old runner forced `POLARS_FORCE_PKG=64` while fresh venv only had `polars-runtime-32`, causing:
  - `Polars binary is missing`
  - `CRITICAL Error: name 'PyLazyFrame' is not defined`

## Changes Applied
1. Built dedicated runtime:
   - `D:\work\Omega_vNext\.venv_stage2_win`
2. Installed pinned deps:
   - `polars==1.38.1`
   - `pyarrow==23.0.0`
   - `numpy==2.4.1`
   - `pandas==2.3.3`
   - `psutil`, `pyyaml`
3. New runner wrapper:
   - `D:\work\Omega_vNext\audit\run_stage2_retry_isolated_v2.cmd`
   - uses `PYTHONNOUSERSITE=1`
   - uses `D:\work\Omega_vNext\.venv_stage2_win\Scripts\python.exe`
   - removed `POLARS_FORCE_PKG=64`
4. New scheduler task:
   - `Omega_v62_stage2_isolated_v2`
5. New logs/ledgers:
   - `audit/stage2_targeted_resume_isolated_v2.log`
   - `audit/stage2_targeted_failed_isolated_v2.txt`
   - `audit/stage2_pending_isolated_v2.txt`

## Validation
- Smoke completed with new runtime:
  - file: `20250707_b07c2229.parquet`
  - elapsed: `602.8s`
  - done advanced: `149 -> 150`
- Schema parity check passed (`schema_equal=True`) between:
  - `20250707_b07c2229.parquet`
  - `20250612_b07c2229.parquet`
- Key types remained stable:
  - `n_ticks=uint32`
  - `dominant_probe=uint32`

## Current State
- Windows Stage2 resumed from backlog:
  - `WIN_STAGE2=150/191`
  - currently processing from `20250704_b07c2229.parquet`
- Linux reference:
  - progressing normally (`LNX_STAGE2` increasing)

## Risk / Follow-up
- Python 3.13 migration not yet complete due package source/install friction.
- Temporary Windows run still sets `OMEGA_STAGE2_ALLOW_RISKY_RUNTIME=1`.
- Next hardening target: complete Python 3.13/3.12 runtime migration and remove risky override.
