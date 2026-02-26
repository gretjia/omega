---
entry_id: 20260226_123046_stage2_multiround_incident_matrix_and_gapfill
task_id: TASK-20260226-STAGE2-MULTIROUND-RCA
timestamp_local: 2026-02-26 12:30:46 +0800
timestamp_utc: 2026-02-26 04:30:46 +0000
operator: codex
role: operator
branch: codex/stage2-try2-thread-budget
git_head: fd0f5e1
hosts_touched: [controller, omega-vm, linux1-lx, windows1-w1]
status: completed
---

## 1. Objective

- Consolidate all Stage2 multi-round failures into one auditable record: what failed, why, and what was fixed.
- Backfill missing operational details that were not clearly recorded in existing handover files.

## 2. Scope

- In scope:
  - Stage2 runtime/orchestration failures on Windows and Linux.
  - Fixes in `tools/stage2_physics_compute.py`, `tools/stage2_targeted_resume.py`, and Linux Stage2 launch/guardrail operations.
  - Handover documentation gaps that affected supervision/debug speed.
- Out of scope:
  - Stage1 historical incidents.
  - Stage3 training/backtest tuning.
  - Any math formula changes for v62.

## 3. Multi-Round Incident Matrix (Stage2)

| Round | Symptom | Root Cause | Repair | Verification |
|---|---|---|---|---|
| R1 | Windows Stage2 repeatedly stalls/crashes; done count plateaus | Native crash path in Windows runtime (`_polars_runtime.pyd`, `0xc0000005`) under risky stack (Python 3.14 + user-site package mix) | Added runtime preflight + strict fail-fast policy; created isolated venv wrapper path | Event logs + resumed progress + schema parity checks in existing entries |
| R2 | “Running but production-invalid” risk (fake success) | Old flow could hide per-file failures behind run-level `rc=0` | `process_chunk` now returns structured `{ok,status,message}` and targeted runner exits non-zero if file failures exist (`RUN_FAILED`) | Runner now returns `rc=2` on run failures; fail ledger deterministic |
| R3 | Windows `import polars` preflight hangs on some hosts | `platform.machine()` WMI probe can block on Windows | Added `OMEGA_WINDOWS_WMI_MACHINE_BYPASS` path (env-based architecture fallback) in Stage2 compute + targeted runner preflight | Code guard active before `import polars`; no WMI dependency on default path |
| R4 | `WIN_FAILED` counter grows, operator confusion about whether issue is fixed | Missing metric semantics in handover docs | Clarified `FAILED_TOTAL` (cumulative unique) vs `RUN_FAILED` (this run) and done-marker truth source | Semantics now documented in `handover/ops/PIPELINE_LOGS.md` |
| R5 | Timeout in batch mode can wrongly poison untouched files | Timeout happens mid-batch but not all files started | Added marker parsing and `DEFER not-started` behavior in targeted runner | Logs now separate started vs deferred files; fail ledger no longer over-poisoned |
| R6 | `rc=4` empty-output symbol subset treated as fatal in isolation fallback | Sparse/invalid symbol subset can produce empty output without file-level failure | Treat `rc=4` as non-fatal skip for single-symbol isolation path | Empty-symbol events now logged as WARN/skip, batch continues |
| R7 | Windows isolation path still expensive on tail files | Single-symbol path could fall back to full-file scan/filter collect | Added single-pass Parquet symbol-table extraction path before fallback | Reduced repeated full scans per isolated symbol path |
| R8 | Linux host pseudo-hang/restart loops under Stage2 load | Stage2 launched in `user.slice` + `earlyoom` interference | Enforced `heavy-workload.slice` guardrails, OOM score policy, dedicated launcher, runtime preflight, and autopilot relaunch policy | Cgroup placement + `memory.events` checks + ongoing done-marker growth evidence |

## 4. Actions Taken

1. Reviewed existing Stage2 handover entries and `LATEST.md` timeline to build an end-to-end failure chain.
2. Audited Stage2 runtime code paths and extracted exact guardrail points:
   - Windows WMI bypass injection before `import polars`.
   - Runtime preflight block rules and override controls.
   - Batch marker parsing and timeout defer behavior.
   - Empty-output (`rc=4`) non-fatal handling.
   - Single-pass symbol extraction in isolated mode.
3. Identified handover gaps: log-path index incompleteness, metric semantics ambiguity, and missing consolidated RCA view.
4. Updated handover docs (this entry + README + logs index) to make Stage2 supervision deterministic for new agents.

## 5. Evidence

- Code-level evidence:
  - `tools/stage2_physics_compute.py`: Windows WMI bypass, runtime guardrails, fallback rc handling, single-pass symbol extraction.
  - `tools/stage2_targeted_resume.py`: runtime preflight, files-per-process batch orchestration, marker parsing, deferred-not-started policy, `RUN_FAILED`.
- Existing incident entries:
  - `handover/ai-direct/entries/20260225_1455_windows_stage2_rca_native_crash_and_guardrails.md`
  - `handover/ai-direct/entries/20260225_1947_windows_stage2_runtime_repair_v2.md`
  - `handover/ai-direct/entries/20260225_215700_windows_stage2_speedup_cutover_files_per_process_4.md`
- Consolidated timeline source:
  - `handover/ai-direct/LATEST.md` (multiple Stage2 updates on 2026-02-24/25)

## 6. Risks / Open Issues

- Windows runtime is still operationally sensitive under high-load files; pinned, isolated env policy must remain strict.
- Batch logs are emitted after subprocess return in targeted runner mode; if operator tails wrong log or ignores done markers, false “stuck” diagnosis can recur.
- Multi-host git remote drift (`origin` not always GitHub on workers) remains an operational risk for hotfix propagation if not normalized.

## 7. Changes Made

- Added this consolidated RCA/gapfill entry:
  - `handover/ai-direct/entries/20260226_123046_stage2_multiround_incident_matrix_and_gapfill.md`
- Updated top-level handover entry docs:
  - `handover/README.md`
- Updated Stage2 log/metric runbook details:
  - `handover/ops/PIPELINE_LOGS.md`
- Updated current truth pointer:
  - `handover/ai-direct/LATEST.md`

No feature math, schema, or output contract changes were made in this documentation task.

## 8. Next Actions (Exact)

1. On omega-vm, ensure workers normalize remotes to GitHub before next Stage2 restart window:
   - `git remote -v` on Linux/Windows and align pull target to GitHub main.
2. During live Stage2 supervision, prioritize done-marker counts + targeted runner log (`TARGETED_RESUME_*`) over `stage2_compute.log` alone.
3. If Windows `FAILED_TOTAL` keeps rising on same subset, isolate those files for dedicated single-file replay and archive exact error signatures per file.

## 9. LATEST.md Delta

- Appended one new update block:
  - `Update 2026-02-26 12:30 +0800 (Stage2 multi-round issues consolidated + handover gapfill)`
- Updated snapshot metadata timestamp and controller head for current session.
