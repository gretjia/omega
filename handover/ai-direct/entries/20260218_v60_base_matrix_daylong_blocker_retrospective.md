# Handover: v60 Base Matrix Daylong Blocker Retrospective
**Date:** 2026-02-18  
**Run Hash:** `aa8abb7`  
**Status:** BLOCKED at `build_base_matrix` (not yet entered optimization/train/backtest)

## 1) Objective and Constraints
- Objective: complete v60 full chain (`frame -> upload -> base_matrix -> optimization -> train -> backtest`) under `audit/v60_optimization_audit_final.md`.
- Hard constraints respected throughout:
  - no change to v6 math principles;
  - train/test split guard kept (`train=2023,2024`, `test=2025,2026`, `test-ym=2025,202601`);
  - recursive audit checkpoints kept active in autopilot.

## 2) Executive Summary
- We spent roughly one full day blocked on `base_matrix`.
- Upstream stages are done and stable: frame/upload completed (`linux=484`, `windows=263`, GCS parquet total `747`).
- Base-matrix failure pattern had two components:
  - true OOM failures on several Vertex jobs;
  - orchestration instability (duplicate processes, stale-heartbeat false positives, cancel/overlap race, long queue `PENDING`).
- Memory mitigation code was implemented (chunked write path) without changing v6 math, but current run is still not past base_matrix due job-state/orchestration issues.

## 3) Timeline (Key Nodes)
- 2026-02-17 03:14 CST: early autopilot start, frame monitoring begins.
- 2026-02-17 ~20:02 CST: switched to full cloud base-matrix loop after frame/upload completion.
- 2026-02-17 20:02-21:41 CST: repeated base-matrix Vertex failures:
  - `702804121622675456` FAILED,
  - `2103423605734899712` FAILED,
  - `1968315616913784832` FAILED,
  - `5958504886764044288` FAILED,
  - `7968236220478128128` FAILED.
- 2026-02-17 21:47-22:02 CST: run `8578473969986830336` started; then overlap/cancel sequence happened while new run was submitted.
- 2026-02-17 22:01 CST onward: run `2730549853846241280` launched (with chunk-days arg). Later it was cancelled while workflow continued retrying.
- 2026-02-18 overnight: watchdog kept triggering stale incidents and auto-resume; restart count increased.
- 2026-02-18 04:58 CST: new autopilot session started (run_id `20260217-205904`), still at `build_base_matrix`.
- 2026-02-18 07:51 CST snapshot:
  - one base-matrix job `RUNNING`: `568540557731692544`,
  - one base-matrix job `PENDING`: `686760047950168064`,
  - no downstream stage started.

## 4) Confirmed Root Causes
1. **True OOM on base_matrix jobs**  
   Verified by Vertex errors:
   - job `7968236220478128128`: `Replicas low on memory: workerpool0`.
   - job `5958504886764044288`: `Replicas low on memory: workerpool0`.

2. **Stale heartbeat false positives during long base_matrix execution**  
   - watchdog repeatedly raised `autopilot_status_stale` while autopilot process still alive and polling job state.
   - multiple codex reports classified these as telemetry staleness, not hard crash.

3. **Overlapping recovery submissions caused cancel/race confusion**  
   - old and new base-matrix jobs coexisted/cancelled close together;
   - runner surfaced cancellation exceptions while another job was already in progress.

4. **Queue/capacity pressure in Vertex**  
   - current job `686760047950168064` stayed `PENDING` for very long intervals (thousands of seconds in runner log), while another job remained `RUNNING`.

## 5) What Was Changed During This Effort
### Code-level memory mitigation (math-preserving)
- `/Users/zephryj/work/Omega_vNext/tools/v60_build_base_matrix.py`
  - added chunked day processing (`--chunk-days`);
  - added +1-day lookahead handling for T+1 boundary correctness;
  - switched to incremental parquet writing (`ParquetWriter`) instead of all-in-memory concat;
  - added optional `--float32-output`;
  - added required-column selective loading to reduce pressure;
  - relaxed config uses empty `winsor_features` to avoid chunk-dependent distortion.
- `/Users/zephryj/work/Omega_vNext/tools/run_vertex_base_matrix.py`
  - added passthrough args: `--chunk-days`, `--float32-output`.
- `/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py`
  - added base-matrix pass-through controls (`--base-matrix-chunk-days`, `--base-matrix-float32-output`).

### Operational recovery and monitoring actions
- maintained autopilot recursive audit checkpoints and v6 split guards.
- enabled watchdog `--auto-resume` + `--trigger-codex`, resulting in repeated incident capture/debug cycles.
- removed one round of duplicate old process chains; later another drift remained (watchdog process alive but not under a detached `screen` session).

## 6) Current Runtime Snapshot (at write time)
- `autopilot status`:
  - file: `/Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json`
  - stage: `build_base_matrix`
  - run_id: `20260217-205904`
  - target base outputs:
    - `gs://omega_v52/staging/base_matrix/v60/20260217-205904_aa8abb7/base_matrix.parquet`
    - `gs://omega_v52/staging/base_matrix/v60/20260217-205904_aa8abb7/base_matrix.meta.json`
- `watchdog state`:
  - file: `/Users/zephryj/work/Omega_vNext/audit/runtime/v52/ai_watchdog_aa8abb7.state.json`
  - `autopilot_restart_count=5`
  - `trigger_count=18`
  - `last_probe.stage=build_base_matrix`
- Vertex base-matrix jobs:
  - `568540557731692544`: `JOB_STATE_RUNNING`
  - `686760047950168064`: `JOB_STATE_PENDING`

## 7) Why This Did Not Finish in One Day
- We addressed memory symptoms, but orchestration still allowed repeated long retries and queue wait without strict single-flight control.
- `autopilot_status_stale` currently measures status-file freshness, not actual liveness; long sync polling during base-matrix makes this noisy.
- Autopilot and watchdog lifecycle management drifted across multiple restarts, causing overlapping control loops at several points.

## 8) Mandatory Next-Step Plan (for next agent)
1. Enforce **single-flight base-matrix**: at most one active base-matrix job per run_id/output URI.
2. Add **heartbeat writes during run_stream polling** in `build_base_matrix` stage to suppress stale false positives.
3. Add **queue timeout policy** for `JOB_STATE_PENDING` (distinct from run timeout), then auto-cancel/re-submit with deterministic backoff.
4. Keep v6 math unchanged; do not use `max_rows_per_file` truncation as default workaround (only explicit/manual).
5. Do not advance to optimization/train/backtest until base-matrix parquet+meta exist in target URI and recursive audit passes `post_base_matrix`.

## 9) Evidence Paths
- Runner log: `/Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log`
- Watchdog log: `/Users/zephryj/work/Omega_vNext/audit/runtime/v52/ai_watchdog_aa8abb7.log`
- Incidents dir: `/Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/`
- Status files:
  - `/Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json`
  - `/Users/zephryj/work/Omega_vNext/audit/runtime/v52/ai_watchdog_aa8abb7.state.json`
- Design constraints:
  - `/Users/zephryj/work/Omega_vNext/audit/v6.md`
  - `/Users/zephryj/work/Omega_vNext/audit/v60_optimization_audit_final.md`
