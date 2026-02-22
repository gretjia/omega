# v60 Pre-Submit Checklist

Use this checklist before launching expensive Vertex jobs (optimization, training, backtest).

## Run Metadata

- [ ] `run_id` recorded:
- [ ] `git_hash` recorded:
- [ ] region recorded:
- [ ] staging bucket recorded:
- [ ] target machine type(s) recorded:

## 1) KPI Contract Freeze

- [ ] Acceptance scope is written and approved:
  - architect baseline metrics: `Topo_SNR`, `Orthogonality`, `Phys_Alignment`, `Model_Alignment`, `Vector_Alignment`
- [ ] Expected output schema is written before submit.
- [ ] Thresholds are written before submit.

## 2) Requirement Coverage Plan

- [ ] Every mandatory requirement has at least one direct evidence field or log marker.
- [ ] Requirement-to-evidence map exists for this run.
- [ ] Telemetry fields planned in artifacts include:
  - `snapshot_interval_ms` or equivalent
  - aggregation mode
  - session filter mode
  - singularity mask counters

## 3) Data + Schema Preflight

- [ ] Probe first selected parquet object before bulk download.
- [ ] Time key resolved dynamically from `time|time_end|time_start|bucket_id`.
- [ ] T+1 required columns verified (`symbol`, `close`, `date`).
- [ ] Dedup/sort keys resolved and logged.

## 4) Effective Sample Budget Gate

- [ ] Minimum `mask_rows/base_rows` threshold defined:
- [ ] Minimum `total_training_rows` threshold defined:
- [ ] Submit blocked if sample budget below threshold.

## 5) Memory + Phase Risk Gate

- [ ] Phase milestones defined and logged:
  - download
  - load
  - dedup
  - sort
  - prepare
  - evaluate
- [ ] Memory risk phases have timeout budget and cancel policy.
- [ ] Eval memory cap configured (`max_eval_traces`).
- [ ] Heavy trace/list columns are dropped when not needed.

## 6) Watchdog and Fail-Fast

- [ ] Semantic stall rules configured:
  - `elapsed >= 15m && total_proc_rows == 0`
  - or equivalent project rule
- [ ] Health check uses semantic counters, not only `JOB_STATE_RUNNING`.
- [ ] Auto-retry policy disabled for deterministic failures (schema/OOM/code).

## 7) Provenance and Audit Package

- [ ] Executed payload source snapshots are stored.
- [ ] SHA256 manifest is stored for snapshot files.
- [ ] Job describe and key logs are captured.
- [ ] Metrics artifact URI is captured.

## 8) Canary Gate

- [ ] Canary run completed for new payload behavior.
- [ ] Canary result reviewed before full-universe run.

## 9) Go / No-Go

- [ ] All sections pass.
- [ ] Human dispatcher approved submit.
- [ ] Submit command + timestamp recorded.
