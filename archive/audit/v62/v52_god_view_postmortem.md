# OMEGA v5.2 "God View" Implementation Post-Mortem
**Date:** 2026-02-16
**Topic:** Cloud Native Swarm & Oracle Deployment Debugging Log

## Executive Summary
The transition to a "Cloud Native" architecture (Vertex AI Swarm + BigQuery Oracle) encountered several friction points. These were primarily related to **Dependency Management**, **Code Packaging**, and **Cloud/Local Environment Divergence**.

## 🔴 Critical Failures & Fixes

### 1. The "Hidden Import" Trap (`psutil`)
- **Symptom:** Swarm jobs failed immediately with `ModuleNotFoundError: No module named 'psutil'`.
- **Root Cause:** The local `trainer.py` imports `psutil` for memory safety checks. The lightweight cloud container (`python:3.10`) does not include this. The payload script's `install_dependencies` function did not list it.
- **Fix:** Added `psutil` to the `pip install` command in `tools/run_optuna_sweep.py`.
- **Lesson:** **Audit imports recursively.** Just because the *entry point* script works doesn't mean the *imported library code* (like `omega_core`) has all its dependencies met.

### 2. The "Refactoring Ghost" (`__init__.py`)
- **Symptom:** `ImportError: cannot import name 'trainer_v51'`.
- **Root Cause:** We consolidated `trainer_v51.py` into `trainer.py` locally but forgot to update `omega_core/__init__.py`, which was acting as a shim/alias. The zipped code bundle propagated this broken link.
- **Fix:** Rewrote `omega_core/__init__.py` to remove the dead reference.
- **Lesson:** **Grep is your friend.** When deleting or renaming a file, run `grep -r "old_name" .` to find lingering references immediately.

### 3. The "Zip Root" Confusion (Code Packaging)
- **Symptom:** Uncertainty about whether `import config` would work inside the container.
- **Root Cause:** The project structure has `config.py` in the root and `omega_core/` as a subdirectory. Zipping just the folder `omega_core/` excludes `config.py`.
- **Fix:** Created a custom zip command: `zip -r omega_core.zip omega_core/ config.py`.
- **Lesson:** **Define a Manifest.** Do not rely on ad-hoc zipping. Create a `tools/build_cloud_bundle.py` that reads a manifest of required files and structures the zip exactly as the remote python path expects.

### 4. BigQuery "Wall Clock" vs. "Data Clock"
- **Symptom:** Radar queries returned 0 results.
- **Root Cause:** SQL used `DATE_SUB(CURRENT_DATE(), ...)` but the uploaded dataset ended 18 days ago.
- **Fix:** Changed SQL to use `(SELECT MAX(trade_date) ...)` as the anchor.
- **Lesson:** **Never use `CURRENT_DATE()`** for analytics on static or batched datasets. Always derive the "Now" from the data itself.

### 5. BigQuery "Schema Fragility"
- **Symptom:** `SELECT * EXCEPT(...)` failed repeatedly due to complex Parquet types (`trace`, `ofi_list`) that BQML couldn't handle, even when "excluded".
- **Root Cause:** `EXCEPT` logic on complex schemas is brittle. Ghost columns or slightly mismatched type definitions cause implicit cast errors.
- **Fix:** Switched to **Explicit Column Selection** (`SELECT open, close, sigma...`).
- **Lesson:** **Be Explicit.** In production pipelines, list every single column you need. It serves as documentation and prevents schema drift breakage.

### 6. The "Relative Import" Blindspot (`tools`)
- **Symptom:** `ModuleNotFoundError: No module named 'tools'`.
- **Root Cause:** `trainer.py` imports `tools.multi_dir_loader`. The zip only contained `omega_core/` and `config.py`.
- **Fix:** Added `tools/` to the zip bundle.
- **Lesson:** **Walk the Graph.** Use tools like `modulegraph` or simple grep to find ALL top-level packages imported by your code, not just the one you are running.

## 🟢 Best Practices for Future Upgrades

1.  **Simulation First:** Before launching 15 machines, launch **1** "Canary" job. Wait for it to pass the "Import & Setup" phase before scaling out.
2.  **Self-Contained Payloads:** The `run_optuna_sweep.py` evolved to be a robust, self-installing payload. This "Trojan Horse" pattern (script installs its own deps and downloads code) is highly effective for ad-hoc cloud jobs.
3.  **Status Dashboarding:** Writing `tools/check_god_view_status.py` provided immediate visibility. Build observability tools *alongside* the deployment tools.
4.  **Versioned Names:** Using `swarm-v52b`, `swarm-v52c` prevented confusion between failed and retried jobs. Always tag/version batch jobs.

## Action Items
- [ ] Create `tools/build_payload.py` to automate the zipping of `omega_core`, `config.py`, and `tools/`.
- [ ] Add a "Dry Run" flag to Swarm tools that runs the setup logic locally in a clean venv to catch missing imports.
