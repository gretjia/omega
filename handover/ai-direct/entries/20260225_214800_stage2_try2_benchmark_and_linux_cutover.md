# Stage2 Try2 Benchmark + Linux Cutover

Date: 2026-02-25 21:48 +0800

## Context
Linux was rebooted after prior SSH banner-timeout incident. Stage2/autopilot auto-restarted with old single-file subprocess runner.

## A/B Benchmark (Post-Reboot)
Benchmark root:
- `/home/zepher/work/Omega_vNext/audit/bench_stage2_try2_20260225_211640`

Fast mini A/B (same input/threads, 3 files):
- input: `input_mini3_fast` (from first row-group slices)
- old runner: `tools/stage2_targeted_resume.py` (single-file subprocess)
- new runner: `tools/stage2_targeted_resume_try2.py` (multi-file subprocess)
- env: `OMEGA_STAGE2_POLARS_THREADS=2`, `OMEGA_STAGE2_SYMBOL_BATCH_SIZE=1`

Result (`ab_mini3_fast_summary.txt`):
- `OLD_SEC=9`, `OLD_DONE=3`, `OLD_FAIL=0`
- `NEW_SEC=7`, `NEW_DONE=3`, `NEW_FAIL=0`
- `SPEEDUP_X=1.286` (about +28.6%)

## Cutover Action
Deployed new runner logic to Linux primary path:
- copied branch version to `~/work/Omega_vNext/tools/stage2_targeted_resume.py`
- compile check passed on Linux (`py_compile`)

Restarted runtime:
- `omega_stage2_autopilot.service` started and active
- new stage2 unit active: `omega_stage2_linux_20260225_214645.service`
- verified running command now includes batch-mode inline script and multiple files in one subprocess

## Current Snapshot (after cutover)
- `INPUT=552`
- `DONE=113`
- `FAIL=3` (carried historical fail ledger)
- runner log shows new headers:
  - `FILES_PER_PROCESS=8`
  - `BATCH_TOTAL=55`
  - `[batch 1/55] START ...`
