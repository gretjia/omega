---
name: hardcode_guard
description: Prevent hardcoded strategy thresholds in production paths and enforce config/artifact-driven parameterization.
---

# Hardcode Guard

Use this skill whenever code changes may introduce numeric thresholds, gates, stops, scaling factors, or decision cutoffs.

## Policy

Forbidden in production paths (`omega_v3_core/*`, active adapters, active strategy logic):
- Direct hardcoded trading thresholds such as `x > 0.5`, fixed stop-loss/take-profit, static trigger floors.

Required:
- Put tunables in `config.py` dataclasses.
- Or load audited values from frozen artifacts/snapshots.

Allowed exceptions:
- Numerical stability constants (`1e-12`, denominator floors) with explicit naming and comments.
- Exchange constraints (for example T+1 and limit-up/down) when they are physical rules, not model tuning.
- Unit-test fixtures in test-only files.

## Mandatory Workflow

1. Detect literals in decision logic.
2. Promote tunables into config/artifact fields.
3. Thread those fields through function boundaries.
4. For train/test-discovered promotions into `config.py`:
   - require audit evidence
   - require versioned artifact snapshot
   - require explicit approval before merge

## Quick Scan

```bash
grep -R -nE "(threshold|floor|gate|ratio|stop|take|alpha|beta)[[:space:]]*=[[:space:]]*-?[0-9]+(\\.[0-9]+)?" omega_v3_core rq tools
```

```bash
grep -R -nE "[<>]=?[[:space:]]*-?[0-9]+(\\.[0-9]+)?" omega_v3_core rq
```

Review hits manually to separate legitimate constants from policy violations.
