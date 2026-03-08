# Why windows1 is materially faster than linux1 in the current full Stage2 run

Date: 2026-03-07 UTC
Run tag: `stage2_full_20260307_v643fix`
Commit: `6b0afff`

## Current conclusion
`windows1-w1` is materially faster than `linux1-lx`, but not because it was assigned an easier half of the corpus.

## Evidence
### Input split is not lighter on windows
- `linux1-lx`
  - `371` files
  - average input size about `2.75 GB/file`
  - suffix mix: `fbd5c8b:280`, `b07c2229:91`
- `windows1-w1`
  - `372` files
  - average input size about `3.62 GB/file`
  - suffix mix: `fbd5c8b:255`, `b07c2229:100`, `e26f3dc:17`

Interpretation:
- windows is not winning because it got smaller files
- if anything, the average file size on windows is larger

### Runtime speed gap is real
Observed live averages:
- `linux1-lx`: about `244.33 s/file`
- `windows1-w1`: about `125.82 s/file`

Windows is therefore roughly `1.9x` faster on the current single-file Stage2 path.

### Neither machine is close to saturation
- `linux1-lx`: load around `2.63` on `32` cores; hottest Stage2 python process around `55% CPU`
- `windows1-w1`: total CPU around `4-5%`

Interpretation:
- this is not a hardware ceiling problem
- the current live launcher is intentionally conservative and throughput-limited

## Most likely reasons
### 1. Launcher model dominates
Current live full Stage2 runs through `tools/stage2_targeted_resume.py` with effective launcher behavior:
- `files-per-process=1`
- single-file serial progression at the launcher level
- bounded native threads inside the file path

This means both hosts are underutilized by design.

### 2. Batch-size asymmetry is a credible contributor
`tools/stage2_physics_compute.py` currently defaults to:
- Windows: `OMEGA_STAGE2_SYMBOL_BATCH_SIZE=20`
- Linux: `OMEGA_STAGE2_SYMBOL_BATCH_SIZE=50`

Under the repaired ordering-contract path, a smaller symbol batch likely reduces:
- batch concat cost
- reorder overhead
- memory pressure / allocator churn
- per-batch contract-gate cost

This is a plausible reason windows is faster on the same logical algorithm.

### 3. File-internal layout may favor the windows slice
Not in the sense of smaller files, but in terms of:
- parquet row-group layout
- symbol locality
- amount of repairable ordering disorder per file
- arrow/polars ingestion behavior

This remains a plausible secondary factor.

## Recommendations for future linux throughput optimization
### A. Highest ROI: redesign the live launcher
Do not keep the current single-file serial launcher as the long-term full Stage2 execution model.

Future direction:
- multiple files in parallel per host
- while preserving thread-budget guardrails inside each file worker

Target style:
- not `1 file x many threads`
- more likely `3-4 files x bounded threads each`

### B. Benchmark smaller symbol batch sizes on linux
Run a dedicated benchmark later with at least:
- `50` (current linux default)
- `25`
- `20` (current windows default)

### C. Run same-file cross-host profiling
Use identical parquet files on both hosts and compare:
- rows/s
- batch count
- reorder/gate diagnostics
- peak RSS

That is the correct way to turn the current inference into hard engineering proof.

## Operational guidance
Do **not** change launcher model or batch-size defaults during the current live full Stage2 run.
This is a follow-up optimization mission, not an in-flight change.
