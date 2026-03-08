# Stage2 live progress, utilization explanation, and input-file failures

Date: 2026-03-07 UTC
Run tag: `stage2_full_20260307_v643fix`
Commit: `6b0afff`

## Progress snapshot
- `linux1-lx`
  - `done=34`
  - `fail=0`
  - current file: `20230227_fbd5c8b.parquet`
  - observed average runtime: about `230.7s/file`
  - health: healthy, continuing to emit `__BATCH_OK__`
- `windows1-w1`
  - `done=68`
  - `fail=4`
  - current file: `20241105_b07c2229.parquet`
  - prior observed average runtime on successful files: about `88s/file`
  - health: progressing, but not clean-green because of 4 hard input failures

## Why the machines do not feel fully loaded
This is real, not a perception error.

Current live Stage2 is not running a multi-file parallel launcher. The active full-run path is:
- `tools/stage2_targeted_resume.py`
- default `files-per-process=1`
- one file per subprocess batch
- direct call into `process_chunk()`

That means the current full Stage2 on each machine is effectively:
- single-file serial at the launcher level
- symbol-batch processing inside the file
- bounded native threading under guardrails

It is therefore expected that:
- fans do not ramp like an all-core burn
- chassis temperature does not spike like a saturated throughput run
- host load stays materially below machine maximum

This is a throughput limitation of the current live launcher model, not evidence that the job is idle.

## Guardrail contribution to low utilization
The live route also intentionally caps nested native thread pools:
- `POLARS_MAX_THREADS`
- `NUMBA_NUM_THREADS`
- `OPENBLAS_NUM_THREADS`
- `MKL_NUM_THREADS`
- `OMP_NUM_THREADS`
- `NUMEXPR_NUM_THREADS`
- `VECLIB_MAXIMUM_THREADS`

This is correct for stability, but it further reduces the chance of "fan-up" behavior.

## Windows hard failures
Current failed files on `windows1-w1`:
- `20240828_fbd5c8b.parquet`
- `20240902_fbd5c8b.parquet`
- `20240903_fbd5c8b.parquet`
- `20240905_fbd5c8b.parquet`

Observed failure mode:
- `schema probe failed: parquet: File out of specification: The file must end with PAR1`

Interpretation:
- these are input parquet corruption / truncation failures
- not V64.3 canonical math failures
- not evidence against the ordering-contract fix

Operational implication:
- current run may proceed for the healthy majority of files
- these 4 files must be handled later as an input-data remediation item

## Future improvement note
A later mission should redesign the live Stage2 launcher for higher host utilization:
- multi-file parallelism per machine
- while preserving thread-budget guardrails and recoverability

Do not change the live launcher during this full run.
