task_id: TASK-20260219-v60-train-backtest-rewrite
git_hash: 78e36d9
timestamp_utc: 2026-02-19T12:24:27Z

# Mechanic Patch

## 1) `tools/run_vertex_xgb_train.py`
- Rewritten to base-matrix-first training flow.
- `--base-matrix-uri` is mandatory (fail-closed).
- `--code-bundle-uri` is mandatory (run-pinned reproducibility).
- Legacy `--data-pattern` / `--train-years` now hard-fail if provided.
- Loads base matrix once, applies physics masks in RAM, computes epistemic weights.
- Builds one global `xgb.DMatrix` and runs one-shot `xgb.train()`.
- Outputs model + metrics to GCS (`omega_v6_xgb_final.pkl`, `train_metrics.json`).

## 2) `tools/run_cloud_backtest.py`
- Rewritten with strict day-key split filtering (`YYYYMMDD_` prefix).
- Enforces year/month prefix filtering (`--test-years`, `--test-ym`).
- `--test-years` is explicit-required fail-closed (`default=""` + empty hard-fail).
- `--test-ym` default is empty (explicit-only month slicing).
- `--code-bundle-uri` is mandatory (run-pinned reproducibility).
- Default caps remain full coverage (`--max-files=0`, `--max-rows-per-file=0`).
- Preserves threaded execution and adaptive worker controls with telemetry logs.
- Emits full `per_file` audit data (plus `per_file_count`), no silent truncation.
- Emits `split_guard` evidence in output JSON.

## 3) `tools/v60_autopilot.py`
- Recursive-audit anchor switched to `audit/v60_training_final.md`.
- Train stage now requires/resolves `optimization.base_matrix_uri`.
- Train submit command now passes `--base-matrix-uri=...`.
- Removed train-stage `--data-pattern` / `--train-years` injection.
- Backtest month filter is explicit-only now: `--test-year-months` default empty.
- Enforces fail-closed split inputs: empty `--train-years` / `--test-years` hard-fail.
- Recursive audit now fails when train/test year sets are empty.
- Status JSON always records split evidence (`backtest.split_guard`) and effective month-prefix list.
- Introduced run-pinned code bundle URI: `.../omega_core_<run_id>_<git_hash>.zip`.
- Passes run-pinned bundle URI to submitter and payload args for swarm/train/backtest.

## 4) `tools/submit_vertex_sweep.py`
- `--code-bundle-uri` changed to mandatory (no mutable default).
- `submit_job()` now fail-closes when `code_bundle_uri` is empty.
- Bundle upload and fallback execution both use the same explicit code bundle URI.

## Validation
Executed:
`python3 -m py_compile tools/run_vertex_xgb_train.py tools/run_cloud_backtest.py tools/v60_autopilot.py tools/submit_vertex_sweep.py`
Result: success (no syntax errors).
