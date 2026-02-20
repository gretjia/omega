task_id: TASK-20260219-v60-train-backtest-rewrite
git_hash: 78e36d9
timestamp_utc: 2026-02-19T12:24:27Z

# Oracle Insight

Primary failure mode in prior training path is architectural:
- reverted to raw-frame scanning and incremental `xgb.train(xgb_model=...)` loops,
- causing I/O stall + tree explosion risk.

Required corrected topology:
- base matrix built on edge,
- cloud train consumes one base matrix snapshot,
- one-shot global train,
- backtest keeps explicit temporal split and auditable telemetry.

Merge gate before deploy:
- independent read-only audit verdict must be PASS.
