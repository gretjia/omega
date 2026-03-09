# V653 First Linux Probe Failed On Alias Resolution; Fix Landed

Timestamp: 2026-03-09 18:24 UTC
Commander: Codex
Mission: `V653 Fractal Campaign Awakening`

## What Happened

- The first bounded Linux forge probe used runtime root:
  - `audit/runtime/v653_probe_linux_20260309_180719`
- It exited after a long L1 scan with:
  - `polars.exceptions.ColumnNotFoundError: unable to find column "Omega_5d"`
- Failure evidence:
  - `audit/runtime/v653_probe_linux_20260309_180719/forge.out`

## Root Cause

- `tools/forge_campaign_state.py` built `Omega_*` and `Psi_*` in the same `with_columns(...)` call.
- Under the worker Polars runtime, `Psi_*` could not reference the freshly aliased `Omega_*` columns inside that same call.
- This is an engineering alias-resolution bug, not a formula bug.

## Fixes Landed On Controller

- `tools/forge_campaign_state.py`
  - rewrote `Psi = S * Omega` as an inline equivalent expression:
    - `S * (abs(S) / (V + eps))`
  - added phase logging with flush
  - added duplicate `symbol/pure_date` guard
  - added zero-pulse-mass guard before forging a campaign matrix
- `tools/run_campaign_event_study.py`
  - upgraded the event-study aggregation to date-neutral aggregation
  - added retained-date / flat-signal coverage diagnostics
- `tests/test_campaign_state_contract.py`
  - added duplicate-key guard coverage
- `tests/test_campaign_event_study.py`
  - added date-neutral aggregation coverage

## Verification

- `python3 -m py_compile`
  - passed
- `uv run --with pytest --with polars --with numpy pytest tests/test_campaign_state_contract.py tests/test_campaign_event_study.py -q`
  - `6 passed in 0.45s`
- `gemini -p`
  - verdict:
    - `PASS`
  - conclusion:
    - the diff preserves the frozen V653 formulas
    - the changes are engineering correctness / observability only

## Runtime Interpretation

- The old Linux probe is not worth continuing.
- It consumed substantial read I/O from the Jan-Feb 2023 bounded batch and then failed on the confirmed alias bug.
- Correct next step:
  - commit + push the fix
  - deploy to `linux1-lx`
  - relaunch the same bounded forge probe under a fresh isolated runtime root

## Files Changed

- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py`
- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`
