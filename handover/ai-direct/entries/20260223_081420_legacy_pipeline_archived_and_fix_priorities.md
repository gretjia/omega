# Legacy Pipeline Archived + Remaining-Issue Priority Check

- Timestamp: 2026-02-23 08:14:20 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- Ensure old `pipeline_runner/framer` path is archived and blocked.
- Re-evaluate the remaining issues raised earlier and decide whether each requires immediate repair.

## 2) Completed in This Session

- Archived legacy runtime sources:
  - `pipeline_runner.py` -> `archive/legacy_v50/pipeline_runner_v50.py`
  - `pipeline/engine/framer.py` -> `archive/legacy_v50/pipeline_engine_framer_v52.py`
- Replaced active-path files with deprecation guards:
  - `pipeline_runner.py` now exits with `[DEPRECATED]` message and points to v62 stage1/stage2 scripts.
  - `pipeline/engine/framer.py` is now a shim that raises `RuntimeError` on use.
- Updated documentation to avoid old entrypoint drift:
  - `README.md`
  - `pipeline/README.md`
  - `jobs/windows_v40/README.md`
  - `archive/legacy_v50/README.md` (new)

## 3) Current Runtime Status

- Mac: repo updated with archive + guardrail changes.
- Windows1: stage1 task remains under v62 tools path; not switched to legacy runner.
- Linux1: stage1 remains active under `heavy-workload.slice`; unaffected by legacy archive action.

## 4) Remaining Issue Priority (From Previous Discussion)

1. `pipeline_runner/framer` version drift
   - Status: **Fixed (archived + blocked)**.
   - Severity before fix: **Critical** (entrypoint could fail with import mismatch or mislead operators).
2. Throughput loss from conservative concurrency (`workers` reduction, frequent worker recycle)
   - Status: **Needs tuning, not immediate correctness blocker**.
   - Recommendation: run controlled benchmark after current stable run, then tune thread/worker matrix.
3. Two-stage extra write/read I/O (Stage1 L1 + Stage2 L2)
   - Status: **Architectural tradeoff**; keep for now because it isolates failure domains.
   - Recommendation: optimize around it (compression/row-group/batching), do not revert to monolithic path during incident period.
4. Stage2 repeated scan per symbol-batch (`lf.filter(...).collect()` loop)
   - Status: **High-value performance fix candidate**.
   - Recommendation: repair next (post-stability window), because it likely causes repeated parquet scans and wasted I/O.
5. Added feature load (split-join, temporal rolling, MDL arena)
   - Status: **Expected compute cost**, not a defect by itself.
   - Recommendation: profile hotspots before disabling physics features.
6. “for i loop too many” hypothesis
   - Status: **Rejected as primary cause** (kernel hot loop is now in Numba JIT path).

## 5) Artifacts / Paths

- `archive/legacy_v50/pipeline_runner_v50.py`
- `archive/legacy_v50/pipeline_engine_framer_v52.py`
- `archive/legacy_v50/README.md`
- `pipeline_runner.py`
- `pipeline/engine/framer.py`
- `README.md`
- `pipeline/README.md`
- `jobs/windows_v40/README.md`

## 6) Commands Executed (Key Only)

- `cp pipeline_runner.py archive/legacy_v50/pipeline_runner_v50.py`
- `cp pipeline/engine/framer.py archive/legacy_v50/pipeline_engine_framer_v52.py`
- `python3 pipeline_runner.py` (verified deprecation exit)
- `python3 -c "import pipeline.engine.framer"` (import ok, use blocked by runtime error)

## 7) Exact Next Steps

1. After current stable run ends, patch `tools/stage2_physics_compute.py` to reduce repeated parquet scans per symbol-batch.
2. Benchmark `POLARS_MAX_THREADS`/workers matrix under fixed cgroup settings (`CPUQuota=2400%`) and lock the best point.
3. Keep legacy files read-only in archive; do not rewire orchestrators back to `pipeline_runner.py`.
