# Handover: v60 Train/Backtest Vertex Guardrails
**Date:** 2026-02-17
**Run Hash:** `aa8abb7`
**Status:** ACTIVE (Base Matrix Running)

## 1) Why this was added
v52 cloud debugging showed that pipeline success is not enough; we also need:
- strict train/backtest data boundary enforcement,
- explicit memory observability,
- and no hidden sampling defaults that silently weaken result validity.

v60 changed the core optimization flow (base matrix + in-memory slicing), so downstream train/backtest guardrails were upgraded without changing math logic.

## 2) High-Impact Fixes Applied
### A. Strict date-key file filtering (anti-contamination)
- `tools/run_vertex_xgb_train.py`
  - file selection now parses filename day key `YYYYMMDD_*` and matches year by prefix (`day[:4] in train_years`).
- `tools/run_cloud_backtest.py`
  - file selection now uses the same date-key logic for `test_years` and optional `--test-ym` prefixes.

Result:
- avoids substring false-matches,
- hardens `train(2023,2024)` vs `backtest(2025,202601)` separation.

### B. Backtest defaults now full-coverage by default
- `tools/run_cloud_backtest.py`
  - `--max-files` default changed to `0` (`0 = full`), not sampled 32.
  - `--max-rows-per-file` default changed to `0` (`0 = full`), not head-capped.

Result:
- no hidden head/sample bias by default,
- runtime knobs still available if emergency memory constraints appear.

### C. Memory + progress telemetry + GC
- `tools/run_vertex_xgb_train.py` and `tools/run_cloud_backtest.py`
  - add per-N-files progress logs including RSS memory,
  - explicit `gc.collect()` after each file loop,
  - metrics now include matched/selected/used files and day span summary.

Result:
- faster detection of memory drift,
- easier unattended diagnostics from logs only.

### D. Autopilot visibility and cap pass-through
- `tools/v60_autopilot.py`
  - added explicit stage caps:
    - `--train-max-files`, `--train-max-rows-per-file`
    - `--backtest-max-files`, `--backtest-max-rows-per-file`
  - logs effective cap plan at startup,
  - forwards those args into Vertex payload submit commands.

Result:
- no implicit defaults;
- runner log shows exact data-scope behavior for recursive audit.

## 3) Compute/Memory guidance for v60 downstream
Given current project quota/capacity behavior and v60 workload shape:
- Optimization (swarm): keep high-memory CPU (`n1-highmem-32` currently stable in this run).
- Train: `n1-highmem-32` recommended for safety if base matrix remains large-scale.
- Backtest: same class for first full run; downsize only after one stable full completion.

Policy:
- prioritize successful end-to-end full run first,
- optimize cost only after stable baseline is achieved.

## 4) Non-negotiable constraints (v60)
1. No optimization stage may trigger ETL re-run.
2. Do not alter physics/math logic for speed hacks.
3. Keep train/test physically disjoint (`2023,2024` vs `2025,202601`).
4. Keep all stage args visible in autopilot runner logs for recursive audit.

## 5) Files changed in this guardrail upgrade
- `tools/run_vertex_xgb_train.py`
- `tools/run_cloud_backtest.py`
- `tools/v60_autopilot.py`
