# Windows Stage2 RCA: Native Crash + Production Validity Guardrails

- Date: 2026-02-25 14:55 +0800
- Scope: `windows1-w1` Stage2 `v62_feature_l2`

## 1) Observed Failure Pattern

- Stage2 stuck at `147/191` with `44` pending files.
- One-file reproduction on `20241128_b07c2229.parquet` showed deterministic native crash:
  - run profile A (`batch=50`, `threads=8`) -> `rc=-1073741819` after `337s`
  - run profile B (`batch=20`, `threads=2`) -> `rc=-1073741819` after `564s`

## 2) Hard Evidence

- Windows Event Viewer:
  - `Application Error` (ID 1000): `python.exe` faulting module `_polars_runtime.pyd`, exception code `0xc0000005`
  - `Windows Error Reporting` (ID 1001): matching `APPCRASH` records
- Runtime path:
  - Python: `3.14.2`
  - Polars loaded from user site: `C:\Users\jiazi\AppData\Roaming\Python\Python314\site-packages\polars\__init__.py`

## 3) Root Cause

- Primary root cause is a Windows native-extension crash path in current Stage2 runtime stack (`python3.14 + user-site polars runtime`), not a pure timeout policy issue.
- Timeout logic is secondary and only exposes incomplete file processing.

## 4) Engineering Fixes Landed

- `tools/stage2_physics_compute.py`
  - per-file result is now structured (`ok/status/message`)
  - Stage2 exits non-zero when any file fails
  - Windows defaults reduced (`POLARS_MAX_THREADS=2`, batch default `20`)
  - runtime-risk warning emitted
- `tools/stage2_targeted_resume.py`
  - child process returns non-zero on `ok=false`
  - run-level exit code is non-zero when any file fails (`RUN_FAILED` metric added)
  - Windows runtime preflight now blocks risky runtime by default

## 5) Production Policy Update

- Fail-fast is enabled for risky Windows runtime combinations to prevent `rc=0` fake-success runs.
- Current Windows stack must not be considered production-valid for Stage2 until moved to pinned dedicated environment and re-smoked.

## 6) External Best-Practice References

- Polars docs recommend version pinning in production:
  - https://docs.pola.rs/releases/upgrade/
- Polars docs recommend isolated environments:
  - https://docs.pola.rs/user-guide/installation/
- pip docs recommend virtual environments and avoiding mixed global/user installs:
  - https://pip.pypa.io/en/stable/user_guide/
- Python 3.14 support was still active/ongoing discussion in Polars project context:
  - https://github.com/pola-rs/polars/issues/25035

