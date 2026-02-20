# v60 Vertex Train Stall: Dual-Audit Root Cause and Improvement Plan (No Execution)

- Date: 2026-02-19
- Scope: `projects/269018079180/locations/us-central1/customJobs/4026903526469795840`
- Constraint: Analysis only. No recovery execution in this document.

## 1) Evidence Freeze

1. Job state remains `JOB_STATE_RUNNING`.
2. Job `startTime` is `2026-02-19T03:24:24Z` and has run for >7 hours.
3. Last worker log for this job is `2026-02-19T03:24:33.324619290Z`.
4. No new worker logs after early bootstrap/install/copy stage.
5. Target output prefix has no artifacts:
   - missing `omega_v6_xgb_final.pkl`
   - missing `train_metrics.json`
6. Train payload is sequential over 2023/2024 files and only emits progress every 10 files.
7. Train set size is 484 files (2023:242, 2024:242).

## 2) Auditor A (Runtime-Forensics, Read-Only)

### A.1 Findings
1. The runtime is in a long silent window (log silence ~449 minutes at analysis time).
2. There is no artifact-level evidence that training has entered the finishing stage.
3. Control-plane state alone (`RUNNING`) cannot distinguish active compute from hung worker.

### A.2 Root-Cause Hypothesis (Runtime Side)
1. Primary operational root cause: no liveness/progress heartbeat in long critical section.
2. Secondary: no hard-stop policy at the payload level for silent runs.

### A.3 Verdict (A)
- `PASS_WITH_BLOCKER`: diagnosis sufficient to block blind waiting; recovery should be gated by observability fix plan.

## 3) Auditor B (Code-Path, Read-Only)

### B.1 Findings
1. `tools/run_vertex_xgb_train.py` has no stage logs before first `10-file` milestone.
2. Progress logging occurs only at:
   - `if file_idx % 10 == 0 or file_idx == len(train_files)` (`[TrainProgress] ...`).
3. Workload is unbounded per file:
   - full-row `collect()` by default,
   - frame prep,
   - DMatrix build,
   - XGBoost incremental train (`num_boost_round` from config; default 60).
4. 484 files x sequential boosting can produce long wall-clock even when not deadlocked.
5. Current code has no checkpoint/resume mid-train model state per N files.

### B.2 Root-Cause Hypothesis (Code Side)
1. High-probability structural cause: observability dead zone + heavy sequential first-window.
2. Plausible stall points without logs:
   - `fs.glob(...)` and year filtering stage,
   - first few `collect()/prepare_frames/build_dmatrix/train` cycles.

### B.3 Verdict (B)
- `PASS_WITH_BLOCKER`: architecture is valid but debug visibility is insufficient for production operations.

## 4) Dual-Audit Consensus

### 4.1 Consensus Root Cause
The primary root cause of "meaningless waiting" is not a confirmed single bug yet; it is an operations design defect:

1. The training payload has a large progress-blind zone.
2. The orchestration path has no deterministic silent-run cutoff tied to payload progress.
3. Therefore, the system cannot reliably tell "still computing" vs "stalled."

### 4.2 Confidence
1. High confidence: observability/gating defect is real and actionable.
2. Medium confidence: actual worker may be stuck in early heavy stage rather than fully dead.
3. Low confidence: exact in-process stall location (without new instrumentation).

## 5) Improvement Plan (No Execution)

## 5.1 Plan P0: Make State Decidable (Mandatory Before Next Recovery)
1. Add stage heartbeat logs in payload:
   - after glob complete (`files_matched`, `files_selected`)
   - before each file starts (at least every 1 file or every 2-3 files)
   - after each file ends (`rows`, `seconds`, `rss_gb`)
2. Emit heartbeat artifact to GCS every N files:
   - `train_heartbeat.json` (file_idx, files_total, rows, rss, last_uri, ts)
3. Add payload silent watchdog:
   - if no file completion in X minutes, raise explicit exception and fail fast.

## 5.2 Plan P1: Bound Work per Step (Without Violating Constitution)
1. Keep no time slicing.
2. Use spatial controls only:
   - symbol/ticker sharding at frame/build stage if needed.
3. Add preflight file-size sampling and expected-time estimator:
   - derive predicted first-10-files runtime before full run.
4. Make first progress line immediate:
   - print `files_total` and first URI before entering heavy compute.

## 5.3 Plan P2: Make Recovery Cheap
1. Add checkpoint model upload every N files:
   - `omega_v6_xgb_checkpoint_{k}.pkl`.
2. Persist completed file list manifest:
   - resume from remaining files only.
3. Keep final artifact contract unchanged:
   - still produce `omega_v6_xgb_final.pkl` and `train_metrics.json`.

## 5.4 Plan P3: Orchestrator Guardrails
1. Define two thresholds:
   - `no_log_timeout_min`
   - `no_heartbeat_timeout_min`
2. If both exceeded, auto-mark as `suspected_stall` and stop blind waiting.
3. Require dual-audit approval before retry profile changes.

## 6) What Not To Do

1. Do not time-slice/chunk-days to force completion.
2. Do not downcast precision as a workaround.
3. Do not blindly restart without adding observability checkpoints.

## 7) Suggested Next Step (Still Analysis-Only)

Prepare a patch proposal only (no run):
1. payload heartbeat/log schema
2. checkpoint/resume contract
3. orchestrator silent-run policy

After that, run a second dual-audit on the patch proposal before any recovery execution.
