task_id: TASK-20260219-v60-train-backtest-rewrite
git_hash: 78e36d9
timestamp_utc: 2026-02-19T12:24:27Z

# Raw Context

## User Request
Read `audit/v60_training_final.md`, strictly follow Chief Architect guidance, rewrite cloud `training` + `backtest` programs, and deploy/run.
Before deploy, run an independent auditor agent with no execution-agent context.

## Non-Negotiable Constraints
1. Must preserve constitution constraints in `audit/constitution_v2.md`.
2. For training payload:
- move to `--base-matrix-uri` input.
- load base matrix once into memory.
- apply physics masks in memory.
- build one global `xgb.DMatrix`.
- call `xgb.train()` exactly once (no incremental append loop).
3. Update autopilot train stage to pass `--base-matrix-uri` (not `--data-pattern`).
4. Backtest must keep strict split guardrails (`test years` + explicit month prefix support, default full coverage caps).

## Audit Scope
Files under review:
- `tools/run_vertex_xgb_train.py`
- `tools/run_cloud_backtest.py`
- `tools/v60_autopilot.py`

## Independent-Audit Requirement
Auditor must run in read-only mode and reason only from:
- constitution + recursive audit prompts
- this `01_Raw_Context.md`
- `03_Mechanic_Patch.md`
No execution-agent chain-of-thought/context is provided.
