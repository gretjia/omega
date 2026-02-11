# v40 Pipeline Overall Recursive Audit (Post Debug, 2026-02-08)

## Objective
Recursive alignment check after Phase 0/1/2 fixes:
- Align runtime pipeline with `audit/v40_*` design intent and handover operation model.
- Confirm no math-core mutation.
- Confirm fail-closed dataset split and evaluation behavior.

## Inputs Audited
- Design/audit references:
  - `audit/v40_windows_handover_runtime_2026-02-08.md`
  - `audit/v40_independent_audit_2026-02-08.md`
  - `audit/v40_p1_fix_2026-02-08.md`
  - `audit/v40_p2_fix_and_config_system_audit_2026-02-08.md`
  - `audit/v40_staging_debug_log_2026-02-08.md`
- Runtime entrypoints:
  - `jobs/windows_v40/start_v40_pipeline_win.ps1`
  - `jobs/windows_v40/run_v40_train_backtest_win.ps1`
  - `jobs/windows_v40/run_v40_smoke_win.ps1`
- Executors:
  - `parallel_trainer/run_parallel_v31.py`
  - `parallel_trainer/run_parallel_backtest_v31.py`

## Recursive Alignment Matrix

### A) No math-core changes (Constitution guard)
- Checked: no edits made to:
  - `omega_v3_core/kernel.py`
  - `omega_v3_core/omega_math_core.py`
- Result: PASS

### B) Dataset role isolation and fail-closed split
- Enforced in entry pipeline:
  - split preflight (`tools/preflight_dataset_split_v40.py`)
  - role manifests (`tools/build_dataset_manifest_v40.py`)
  - overlap guard with normalized absolute path compare
- Result: PASS

### C) Startup responsiveness under huge manifests
- Train/backtest now stream file-list manifests in chunks.
- Planning heartbeat emitted during scan.
- Removes monolithic pre-materialization of multi-million task lists.
- Result: PASS

### D) Memory-management behavior at startup
- Previous pattern: full task list in memory before worker loop.
- Current pattern: bounded chunk iterator + immediate worker start.
- Result: PASS

### E) Worker/error semantics and stage truthfulness
- Train:
  - worker/schema errors counted separately
  - fail-closed threshold (`--max-worker-errors`, default 0)
  - failed status JSON emitted before exception
- Backtest:
  - file error threshold (`--max-file-errors`, default 0)
  - final audit `FAILED` hard-fails by default
- Result: PASS

### F) Policy provenance
- Backtest no longer uses stale hardcoded checkpoint fallback.
- Auto policy resolves latest `checkpoint_rows_*.pkl` if `--policy` absent.
- Result: PASS

### G) Smoke semantics
- Smoke now explicitly allows audit-failed tiny sample (`--allow-audit-failed`) to validate runtime chain without weakening full-pipeline fail-closed policy.
- Result: PASS

### H) Manifest portability hardening
- UTF-8 BOM line-prefix handled in Python runners + PowerShell overlap guard.
- Result: PASS

## Residual Risks / Open Items
1. `tools/preflight_dataset_split_v40.py` remains untracked in current worktree.
   - Risk: reproducibility drift across machines if file not committed.
2. Untracked local directory `C/` exists in repo root.
   - Risk: tooling confusion/noise in audits.
3. Existing modified handover file (`audit/v40_windows_handover_runtime_2026-02-08.md`) contains encoding corruption in current local copy.
   - Risk: readability/transfer quality for next AI handover.

## Overall Verdict
- Pipeline orchestration and runner behavior: **PASS (debug closure)**
- Math core integrity: **PASS**
- Runtime fail-closed guarantees (split + errors + final audit): **PASS**
- Recommended next step: execute official fixed-split run again and monitor `audit/v40_runtime/windows/*` in real time.
