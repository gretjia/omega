# Pre-Task Lesson Recall

- generated_by: `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py`
- source_of_truth: `handover/ai-direct/entries/*.md` and `handover/DEBUG_LESSONS.md`
- index_layer: `handover/index/memory_index.jsonl` and `handover/index/memory_index.sqlite3` (derived read-only)
- indexed_records: 32
- recall_top_k: 5
- query_task_id: TASK-20260219-BACKTEST-FLEX-LOAD-AUDIT
- query_keywords: tools, run_vertex_xgb_train, train, v60_autopilot, pass, run_cloud_backtest, backtest, code-bundle-uri, empty, bundle, data-pattern, default, git_hash, with, adaptive, base-matrix-uri, e36d9, explicit
- query_components: tools, run_cloud_backtest, tmp, backtest_takeover_aa8abb7, run_vertex_xgb_train, v60_autopilot, submit_vertex_sweep, audit, v60_training_final, constitution_v2, task-20260219-backtest-flex-load-audit, task_id, git_hash, timestamp_utc, constitution_preflight, mechanic_patch_smoke

## Top Matches
1. `handover_entry` | score=23.85 | Handover: Flexible Load Design (Audited and Approved)
   - task_id: TASK-20260219-BACKTEST-FLEX-LOAD-AUDIT
   - timestamp: 2026-02-19 15:56:28 +0800
   - source: `handover/ai-direct/entries/20260219_155539_flexible_load_audited_design.md`
   - why: task_id exact, keyword x3, component x6
   - keyword_overlap: adaptive, backtest, train
   - component_overlap: audit, backtest_takeover_aa8abb7, run_cloud_backtest, task-20260219-backtest-flex-load-audit, tmp
2. `handover_entry` | score=14.25 | Handover: v60 Train/Backtest Vertex Guardrails
   - task_id: N/A
   - timestamp: 2026-02-17
   - source: `handover/ai-direct/entries/20260217_v60_train_backtest_vertex_guardrails.md`
   - why: keyword x7, component x4
   - keyword_overlap: backtest, default, explicit, run_cloud_backtest, run_vertex_xgb_train
   - component_overlap: run_cloud_backtest, run_vertex_xgb_train, tools, v60_autopilot
3. `handover_entry` | score=13.05 | Handover: v60 Vertex Capacity + Cost Playbook
   - task_id: N/A
   - timestamp: 2026-02-17
   - source: `handover/ai-direct/entries/20260217_v60_vertex_capacity_cost_playbook.md`
   - why: keyword x4, component x4
   - keyword_overlap: backtest, tools, train, with
   - component_overlap: run_cloud_backtest, submit_vertex_sweep, tools, v60_autopilot
4. `handover_entry` | score=11.85 | Handover: v60 Training Audit Evidence Package
   - task_id: TASK-20260219-V60-TRAINING-AUDIT-PACKAGE
   - timestamp: 2026-02-19 19:50:18 +0800
   - source: `handover/ai-direct/entries/20260219_195018_v60_training_audit_package.md`
   - why: keyword x3, component x4
   - keyword_overlap: backtest, tools, train
   - component_overlap: audit, backtest_takeover_aa8abb7, run_cloud_backtest, run_vertex_xgb_train
5. `debug_lesson` | score=11.40 | Backtest Semantic Fail-Fast (used=0 rows=0 burn)
   - task_id: TASK-20260219-v60-backtest-causality-failfast
   - timestamp: 2026-02-19T16:13:41Z
   - source: `handover/DEBUG_LESSONS.md`
   - why: keyword x2, component x4
   - keyword_overlap: backtest, empty
   - component_overlap: audit, backtest_takeover_aa8abb7, run_cloud_backtest, tools
   - symptom: Cloud backtest ran for hours with normal `RUNNING` status and increasing `files=x/y`, but `used=0 rows=0` stayed flat; final result failed after unnecessary GCP spend.
   - root_cause: Monitoring tracked liveness/state only, not semantic validity. Old backtest path processed single-day files independently while label logic requires T+1 (`t_plus_1_horizon_days=1`), so `_prepare_frames` returned empty for each file (`empty_processed`) and only hard-failed at end when `per_file` stayed empty.
   - fix: Introduce hard fail-fast controls at 3 layers. (1) Preflight gate before submit: if T+1 labels are enabled and execution unit is single-day file, block submit unless global/causal materialization mode is used. (2) Runtime watchdog: cancel job when any of these trigger: `completed_files >= 10 && files_used == 0`, or `elapsed >= 15m && total_proc_rows == 0`, or `empty_processed_ratio >= 0.95` over a sliding window. (3) Cost guard: set max wall-clock budget and cancel when exceeded without non-zero semantic progress.
   - guardrail: Do not rely on `JOB_STATE_RUNNING` as health signal. A backtest run is healthy only if semantic counters move (`files_used > 0` and `total_proc_rows > 0`) within early runtime. Enforce automatic cancel on semantic stall to cap loss.
