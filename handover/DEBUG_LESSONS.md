# Debug Lessons Ledger

This file is the shared anti-regression memory for all agents.
Write only reproducible, technical lessons.

## Entry Template

## 0000-00-00T00:00:00Z | short_title
- task_id: TODO
- git_hash: TODO
- role: debug_scribe
- model_profile: codex_medium
- auto_key: optional_for_auto_entries
- symptom: TODO
- root_cause: TODO
- fix: TODO
- guardrail: TODO
- refs: TODO

## 2026-02-18T09:50:00Z | Vertex AI Quota "Partially Approved" Trap
- task_id: base_matrix_stall
- git_hash: aa8abb7
- role: debug_scribe
- model_profile: gemini_pro
- symptom: Vertex AI Custom Job fails immediately with `RESOURCE_EXHAUSTED` for N2 CPUs, despite GCE Quota page showing "Partially Approved (400 vCPUs)".
- root_cause: "Partially Approved" GCE quotas often do not propagate effectively to the Vertex AI managed service layer, or are restricted to specific zones that Vertex AI's scheduler might not pick. Vertex AI has its own effective quota limits that can be stricter than GCE's.
- fix: Switch to machine types with **Fully Approved** quotas (e.g., `e2-highmem-16` or `n1-standard-32` in `us-central1`) or "Custom model training CPUs for N1/E2". Avoid "Partially Approved" resources for automated pipelines.
- guardrail: In `submit_vertex_sweep.py`, catch `subprocess.CalledProcessError` from `gcloud` and print `stderr` to immediately expose quota errors instead of swallowing them.

## 2026-02-18T09:50:00Z | Region Migration & Data Gravity
- task_id: region_migration
- git_hash: aa8abb7
- role: debug_scribe
- model_profile: gemini_pro
- symptom: `us-west1` suffered from severe N1 stockouts (PENDING > 2hrs) and N2 quota limits.
- root_cause: Region resource exhaustion.
- fix: Migrated entire pipeline to `us-central1`. Critical step: Used `gcloud storage cp -r` to move data bucket *before* switching compute region to avoid egress costs and latency.
- guardrail: When changing `REGION` in config, always verify `STAGING_BUCKET` is in the same region.

## 2026-02-18T09:50:00Z | Hidden Python Dependency in Cloud Payloads
- task_id: vertex_crash
- git_hash: aa8abb7
- role: debug_scribe
- model_profile: gemini_pro
- symptom: Vertex job stuck in PENDING/RUNNING loop, then FAILED. Logs showed `ModuleNotFoundError: No module named 'pythonjsonlogger'`.
- root_cause: The local python environment had `python-json-logger` installed (likely as a transitive dep or dev tool), but it was missing from the explicit `pip install` list in the cloud payload script `tools/run_vertex_base_matrix.py`. `omega_core` imported it for structured logging.
- fix: Explicitly add `python-json-logger` to the `subprocess.check_call([sys.executable, "-m", "pip", "install", ...])` list in the cloud wrapper script.
- guardrail: Audit `omega_core` imports against the payload's installation list.

## 2026-02-18T12:20:00Z | Vertex AI Silent Failures (OOM)
- task_id: base_matrix_oom
- git_hash: aa8abb7
- role: debug_scribe
- model_profile: gemini_pro
- symptom: Vertex AI Custom Job fails with `JOB_STATE_FAILED` after running for 5-10 minutes. Local runner logs only show the generic state change, no stack trace.
- root_cause: Out of Memory (OOM) or system termination. These errors are logged in Cloud Logging (server-side), not stdout/stderr of the wrapper script, so the local logs miss them.
- fix: Use `gcloud logging read "resource.type=ml_job AND resource.labels.job_id=JOB_ID" --limit 50` to find the real error (e.g., "Replicas low on memory").
- guardrail: When debug agents see `JOB_STATE_FAILED` without a traceback, they **MUST** query Cloud Logging before assuming it's a transient flake and restarting.

## 2026-02-18T07:04:12Z | TASK-20260218-V60-OBJECTION-REAUDIT_reject
- task_id: TASK-20260218-V60-OBJECTION-REAUDIT
- git_hash: 5ca36a3
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260218-V60-OBJECTION-REAUDIT|5ca36a3
- symptom: Hardening in `v60_autopilot.py` correctly enforces the rejection of `--base-matrix-exec-mode vertex`, effectively disabling the forbidden cloud path.
- root_cause: Root cause captured across mechanic and recursive auditor artifacts.
- fix: Required Fixes:
- guardrail: Ticker sharding logic introduces potential IO overhead on Darwin systems; however, the `chunk-days` rejection prevents inefficient temporal fragmentation.
- refs: `handover/ai-direct/live/04A_Gemini_Recursive_Audit.md`, `handover/ai-direct/live/03_Mechanic_Patch.md`, `handover/ai-direct/live/02_Oracle_Insight.md`, `handover/ai-direct/live/01_Raw_Context.md`

## 2026-02-18T17:56:06Z | TASK-20260218-WIN-MEM-GUARD-DOUBLE-AUDIT_reject
- task_id: TASK-20260218-WIN-MEM-GUARD-DOUBLE-AUDIT
- git_hash: 5ca36a3
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260218-WIN-MEM-GUARD-DOUBLE-AUDIT|5ca36a3
- symptom: REJECT** (dual independent auditors A/B both reject)
- root_cause: Privilege/Permission Mismatch:** `register_windows_memory_guard.ps1` configures the task with `-RunLevel Limited`. In a standard Windows environment, a limited principal cannot stop scheduled tasks or terminate processes owned by other sessions. Furthermore, `CommandLine` access via CIM/WMI is often restricted for non-elevated users, which would cause the targeting logic to fail silently.
- fix: Current script baseline is **not accepted for production stability** until required fixes are applied and re-audited.
- guardrail: ## Required Fix Gate Before Approval
- refs: `handover/ai-direct/live/05_Final_Audit_Decision.md`, `handover/ai-direct/live/04A_Gemini_Recursive_Audit.md`, `handover/ai-direct/live/04B_Codex_Recursive_Audit.md`, `handover/ai-direct/live/03_Mechanic_Patch.md`, `handover/ai-direct/live/02_Oracle_Insight.md`, `handover/ai-direct/live/01_Raw_Context.md`

## 2026-02-18T20:21:44Z | TASK-20260219-V60-MULTI-AGENT-GOVERNED-ROLLOUT_reject
- task_id: TASK-20260219-V60-MULTI-AGENT-GOVERNED-ROLLOUT
- git_hash: working-tree
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260219-V60-MULTI-AGENT-GOVERNED-ROLLOUT|working-tree
- symptom: verdict: REJECT
- root_cause: Root cause captured across mechanic and recursive auditor artifacts.
- fix: Linux Sync Isolation:** The `linux-bootstrap` role handles GCS-to-Linux streaming. While idempotent, it assumes the `linux_frame_dir` is correctly mounted and writable; a mount failure (as noted in the context) is correctly detected but requires manual recovery if the auto-mount fix fails.
- guardrail: smoke_gate: PASS
- refs: `handover/ai-direct/live/05_Final_Audit_Decision.md`, `handover/ai-direct/live/04A_Gemini_Recursive_Audit.md`, `handover/ai-direct/live/04B_Codex_Recursive_Audit.md`, `handover/ai-direct/live/03_Mechanic_Patch.md`, `handover/ai-direct/live/02_Oracle_Insight.md`, `handover/ai-direct/live/01_Raw_Context.md`

## 2026-02-19T02:55:31Z | TASK-20260218-V60-BASE-MATRIX-MEM-OPT_debug
- task_id: TASK-20260218-V60-BASE-MATRIX-MEM-OPT
- git_hash: 5ca36a3
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260218-V60-BASE-MATRIX-MEM-OPT|5ca36a3
- symptom: Implementation or audit surfaced a defect in current task context.
- root_cause: Auditor A used fallback mode because Gemini CLI OAuth was unavailable in this non-interactive terminal context.
- fix: Required Fixes
- guardrail: smoke_gate: PASS
- refs: `handover/ai-direct/live/05_Final_Audit_Decision.md`, `handover/ai-direct/live/04A_Gemini_Recursive_Audit.md`, `handover/ai-direct/live/04B_Codex_Recursive_Audit.md`, `handover/ai-direct/live/03_Mechanic_Patch.md`, `handover/ai-direct/live/02_Oracle_Insight.md`, `handover/ai-direct/live/01_Raw_Context.md`

## 2026-02-19T07:51:51Z | TASK-20260219-BACKTEST-FLEX-LOAD-AUDIT_reject
- task_id: TASK-20260219-BACKTEST-FLEX-LOAD-AUDIT
- git_hash: 78e36d9
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260219-BACKTEST-FLEX-LOAD-AUDIT|78e36d9
- symptom: Memory Guardrail:** Wrap `lf.collect()` in a targeted try-except to catch `MemoryError` and immediately set `target_workers = min_workers` for the remainder of the run.
- root_cause: Root cause captured across mechanic and recursive auditor artifacts.
- fix: ### Required Fixes
- guardrail: task_id: TASK-20260219-BACKTEST-FLEX-LOAD-AUDIT
- refs: `handover/ai-direct/live/05_Final_Audit_Decision.md`, `handover/ai-direct/live/04A_Gemini_Recursive_Audit.md`, `handover/ai-direct/live/04B_Codex_Recursive_Audit.md`, `handover/ai-direct/live/03_Mechanic_Patch.md`, `handover/ai-direct/live/02_Oracle_Insight.md`, `handover/ai-direct/live/01_Raw_Context.md`

## 2026-02-19T16:13:41Z | Backtest Semantic Fail-Fast (used=0 rows=0 burn)
- task_id: TASK-20260219-v60-backtest-causality-failfast
- git_hash: 78e36d9
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260219-v60-backtest-causality-failfast|78e36d9
- symptom: Cloud backtest ran for hours with normal `RUNNING` status and increasing `files=x/y`, but `used=0 rows=0` stayed flat; final result failed after unnecessary GCP spend.
- root_cause: Monitoring tracked liveness/state only, not semantic validity. Old backtest path processed single-day files independently while label logic requires T+1 (`t_plus_1_horizon_days=1`), so `_prepare_frames` returned empty for each file (`empty_processed`) and only hard-failed at end when `per_file` stayed empty.
- fix: Introduce hard fail-fast controls at 3 layers. (1) Preflight gate before submit: if T+1 labels are enabled and execution unit is single-day file, block submit unless global/causal materialization mode is used. (2) Runtime watchdog: cancel job when any of these trigger: `completed_files >= 10 && files_used == 0`, or `elapsed >= 15m && total_proc_rows == 0`, or `empty_processed_ratio >= 0.95` over a sliding window. (3) Cost guard: set max wall-clock budget and cancel when exceeded without non-zero semantic progress.
- guardrail: Do not rely on `JOB_STATE_RUNNING` as health signal. A backtest run is healthy only if semantic counters move (`files_used > 0` and `total_proc_rows > 0`) within early runtime. Enforce automatic cancel on semantic stall to cap loss.
- refs: `tools/run_cloud_backtest.py`, `omega_core/trainer.py`, `config.py`, `audit/_archived/v60_backtest_audit.md`, `audit/_archived/v60_backtest_final.md`, `audit/runtime/v52/backtest_takeover_aa8abb7.log`

## 2026-02-19T16:56:18Z | n2-standard-80 Backtest Schema Contract Break (time vs time_end)
- task_id: TASK-20260220-N2STD80-SCHEMA-CONTRACT
- git_hash: 78e36d9
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260220-N2STD80-SCHEMA-CONTRACT|78e36d9
- symptom: Vertex backtest on `n2-standard-80` failed after ~12 minutes (`JOB_STATE_FAILED`) with `polars.exceptions.ColumnNotFoundError: "time" not found`.
- root_cause: Cloud payload hardcoded `df_raw.unique(subset=["symbol","time"])` and `df_raw.sort(["symbol","time"])`, but production frame schema uses `time_end`/`bucket_id` (no `time` column). Job downloaded and materialized large data before hitting this deterministic schema error.
- fix: Updated `tools/run_cloud_backtest.py` to (1) add schema fail-fast preflight on first selected GCS file, (2) dynamically resolve causal time key from `time|time_end|time_start|bucket_id`, (3) build dedup/sort keys safely (`symbol,date,time_key`), and (4) enforce required schema for T+1 (`symbol`,`close`,`date` when enabled). Verified by smoke job `customJobs/4089128737776336896` on `n2-standard-80` with output status `completed` and `total_proc_rows=62842`.
- guardrail: Every backtest submit must include schema preflight before bulk download/compute. Never hardcode time key names in cloud payloads; derive from schema and fail fast if unresolved.
- refs: `tools/run_cloud_backtest.py`, `gcloud ai custom-jobs describe 8385422044799434752`, `gcloud logging read resource.labels.job_id=8385422044799434752`, `gcloud ai custom-jobs describe 4089128737776336896`, `gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_smoke_n2std80_schemafix_20260219-164409.json`

## 2026-02-20T02:22:00+08:00 | Full Backtest OOM Phase Fingerprint (n2-standard-80 / n2-highmem-64)
- task_id: TASK-20260220-BACKTEST-OOM-PHASE-FORENSICS
- git_hash: 78e36d9
- role: debug_scribe
- model_profile: codex_medium
- symptom: Full backtest jobs on `n2-standard-80` (`customJobs/6324251159091478528`) and `n2-highmem-64` (`customJobs/1475563210273718272`) failed with Vertex terminal error `Replicas low on memory: workerpool0`, but plain state polling could not reveal which compute phase triggered OOM.
- root_cause: OOM is not a startup/schema issue. Forensic logs show both jobs completed `Schema preflight` + `Parallel download complete`, then entered `Loading all raw data` / `Resolved causal keys` / `Deduplicating`; failure happened at or immediately after this boundary (before/around sort+physical-engine peak memory). One failed run shows container restart fingerprints (`+ python3 -m pip install ...`, `+ python3 -u payload.py` repeating near terminal window), confirming memory pressure can trigger worker recycle before final fail.
- fix: Treat `load->dedup->sort/apply` as OOM risk zone and gate it explicitly: capture phase checkpoints from Cloud Logging, enforce phase-level watchdog thresholds, and prefer larger-memory tier (`n2-highmem-80`) when full-universe global materialization is required.
- guardrail: Do not rely on `JOB_STATE_RUNNING` liveness. A run is considered healthy only if phase milestones advance within bounded time (`download_complete`, `loaded`, `dedup_done`, `sort_done`, `prepare_done`, `evaluating`). If a phase stalls beyond threshold, auto-cancel and relaunch with safer memory profile instead of waiting hours.
- refs: `gcloud ai custom-jobs describe 6324251159091478528 --region=us-central1`, `gcloud ai custom-jobs describe 1475563210273718272 --region=us-central1`, `gcloud logging read 'resource.labels.job_id=\"6324251159091478528\"' --order=desc`, `gcloud logging read 'resource.labels.job_id=\"1475563210273718272\"' --order=desc`, `gcloud logging read 'resource.labels.job_id=\"3366793578792615936\"' --order=desc`

## 2026-02-20T03:10:00+08:00 | Backtest Recovery Path Succeeded (n2-highmem-80)
- task_id: TASK-20260220-BACKTEST-RECOVERY-SUCCESS
- git_hash: 78e36d9
- role: debug_scribe
- model_profile: codex_medium
- symptom: Full-universe backtest repeatedly failed OOM or entered long opaque stalls; cost risk escalated due limited observability during download/prepare/evaluate phases.
- root_cause: (1) Expensive recursive physics recompute in backtest duplicated work already materialized in frame parquet. (2) Unbounded trace collection for Topo_SNR (`to_list()` over full column) inflated memory at evaluation. (3) Download path had no progress telemetry and excessive parallelism, creating blind spots for stall decisions.
- fix: Shipped and validated three production fixes:
- fix: `tools/run_cloud_backtest.py`: added `--download-workers` (used `16`) and progress logs (`Download progress: x/263`), added precomputed-physics reuse gate, dropped heavy list columns (`ofi_list/ofi_trace/vol_list/vol_trace/time_trace`) before sort+prepare when reuse is available, preserved schema contract and causal ordering.
- fix: `omega_core/trainer.py`: added `OMEGA_REUSE_PRECOMPUTED_PHYSICS` path to skip recursive kernel recompute when precomputed physics columns exist; optimized `_collect_traces` to `head(max_traces)` before `to_list()` to avoid full-column Python materialization.
- fix: Capped eval traces in cloud backtest (`--max-eval-traces=50000`) for bounded validation memory.
- guardrail: Backtest is approved only when logs show this milestone chain in order: `Rapid downloading` -> incremental `Download progress` -> `Parallel download complete` -> `Enabled precomputed physics reuse` -> `Applying physical engine` -> `Valid processed rows` -> `Evaluating`.
- guardrail: If no new milestone for >20 minutes in a single phase, cancel and relaunch with explicit lower download workers and preserved progress telemetry.
- evidence:
- evidence: Vertex job `customJobs/1959559432727691264` reached `JOB_STATE_SUCCEEDED` (`start=2026-02-19T18:49:11Z`, `end=2026-02-19T19:09:19Z`).
- evidence: Result artifact `gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`.
- evidence: Key payload metrics: `status=completed`, `files_used=263`, `total_proc_rows=8907595`, `seconds=1170.03`, `reuse_precomputed_physics=true`.
- refs: `tools/run_cloud_backtest.py`, `omega_core/trainer.py`, `gcloud ai custom-jobs describe 1959559432727691264`, `gcloud storage cat gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`

## 2026-02-20T02:34:29Z | v60 Validation Evidence Coverage Gap
- task_id: TASK-20260220-V60-VALIDATION-COVERAGE
- git_hash: 78e36d9
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260220-V60-VALIDATION-COVERAGE|78e36d9
- symptom: Run chain completed but full v6 sign-off remained blocked because one mandatory requirement could not be evidenced from runtime artifacts.
- root_cause: Requirement-level observability was incomplete: mandatory PHASE-1 3-second snapshot handling had no explicit runtime marker or metric field in produced evidence package.
- fix: Add requirement coverage telemetry into backtest/base-matrix artifacts (for example snapshot_interval_ms, aggregation_mode, session_filter_mode, singularity_mask_hit_count) and publish a per-run requirement-evidence manifest.
- guardrail: No run can be marked VALIDATED unless every mandatory requirement has at least one direct artifact field/log marker linked in the validation matrix.
- refs: `audit/_archived/v6.md`, `audit/_archived/v60_v6_validation_results.md`, `audit/runtime/v60_factual_evidence/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`, `audit/runtime/v60_factual_evidence/job_1959559432727691264.logs.json`

## 2026-02-20T02:34:29Z | Backtest KPI Contract Mismatch (Architect Metrics Baseline)
- task_id: TASK-20260220-V60-KPI-CONTRACT
- git_hash: 78e36d9
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260220-V60-KPI-CONTRACT|78e36d9
- symptom: Stakeholder asked for profitability proof, but produced backtest output contained only structural/model-alignment metrics and no trading PnL fields.
- root_cause: Current v60 backtest implementation is a model/physics evaluator, not a portfolio simulator; output schema excludes position sizing, costs, turnover, equity curve, Sharpe, and drawdown.
- fix: Freeze acceptance on architect baseline metrics and keep v60 backtest output contract aligned to model/physics evaluator scope.
- guardrail: Before launching expensive cloud runs, freeze KPI contract in writing (required output fields + thresholds) and do not block v60 architectural validation on profitability schema.
- refs: `tools/run_cloud_backtest.py`, `omega_core/trainer.py`, `audit/runtime/v60_factual_evidence/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`, `config.py`

## 2026-02-20T02:34:29Z | Physics-Gate Sample Collapse Needs Preflight
- task_id: TASK-20260220-V60-SAMPLE-COLLAPSE
- git_hash: 78e36d9
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260220-V60-SAMPLE-COLLAPSE|78e36d9
- symptom: Training operated on a very small effective subset relative to base matrix size (millions -> thousands), increasing instability risk and interpretation drift.
- root_cause: Physics gates are intentionally strict and can collapse effective samples after mask + finite-weight filters; this was not enforced as a hard pre-submit budget gate.
- fix: Add preflight checks for effective sample budget (mask_rows/base_rows ratio and total_training_rows minimum) and fail early when below agreed floor.
- guardrail: Require explicit minimum effective training rows and signal density threshold before submitting full train/backtest pipeline.
- refs: `audit/runtime/v60_factual_evidence/train_metrics_20260219-125410_78e36d9.json`, `tools/run_vertex_xgb_train.py`, `audit/runtime/v60_factual_evidence/base_matrix_resume_aa8abb7.meta.json`

## 2026-02-20T02:34:29Z | Immutable Payload Snapshot is Mandatory for Forensics
- task_id: TASK-20260220-V60-FORENSIC-REPRO
- git_hash: 78e36d9
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260220-V60-FORENSIC-REPRO|78e36d9
- symptom: Root-cause attribution is slow when run-time code and local workspace diverge or when payload provenance is ambiguous.
- root_cause: Cloud jobs execute packaged payloads; without immutable source snapshots and hashes, post-mortem analysis can confuse local files with executed code.
- fix: Persist executed payload sources and SHA256 manifests for each run alongside metrics and job describes.
- guardrail: A run is audit-incomplete unless source snapshot files and hash manifest are present in the evidence package.
- refs: `audit/runtime/v60_factual_evidence/source_tools_run_cloud_backtest.py`, `audit/runtime/v60_factual_evidence/source_tools_run_vertex_xgb_train.py`, `audit/runtime/v60_factual_evidence/source_omega_core_trainer.py`, `audit/runtime/v60_factual_evidence/source_file_sha256.txt`

## 2026-02-22T11:29:44Z | TASK-20260222-V62-DUAL-STAGE1-RELAUNCH-MONITOR_debug
- task_id: TASK-20260222-V62-DUAL-STAGE1-RELAUNCH-MONITOR
- git_hash: 47acc72+working-tree
- role: debug_scribe
- model_profile: codex_medium
- auto_key: TASK-20260222-V62-DUAL-STAGE1-RELAUNCH-MONITOR|47acc72+working-tree
- symptom: `/Users/zephryj/work/Omega_vNext/omega_core/kernel.py`: replace stale `build_l2_frames` import path with current ETL chain.
- root_cause: Root cause captured across mechanic and recursive auditor artifacts.
- fix: Patch applied and validated under current multi-agent flow.
- guardrail: Mandatory next gates before declaring run healthy:
- refs: `handover/ai-direct/live/05_Final_Audit_Decision.md`, `handover/ai-direct/live/04A_Gemini_Recursive_Audit.md`, `handover/ai-direct/live/04B_Codex_Recursive_Audit.md`, `handover/ai-direct/live/03_Mechanic_Patch.md`, `handover/ai-direct/live/02_Oracle_Insight.md`, `handover/ai-direct/live/01_Raw_Context.md`
