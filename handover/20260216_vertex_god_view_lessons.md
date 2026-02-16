# Handover: Vertex AI "God View" Debugging Lessons
**Date:** 2026-02-16
**Topic:** Cloud Native Deployment Stability (Vertex AI + BigQuery)
**Status:** CRITICAL KNOWLEDGE

## 1. The "Invisible Import" Trap (Dependency Management)
**Symptom:** Jobs fail immediately with `ModuleNotFoundError`.
**Context:** Local `trainer.py` imported `psutil` for memory safety. The minimal cloud container (`python:3.10`) did not have it.
**Solution:**
- **Recursive Audit:** Do not just check the entry script. Check every module imported by the entry script.
- **Explicit Install:** Add every non-standard library to the `pip install` command in the payload.
- **Pattern:**
  ```python
  subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "polars", "optuna", ...])
  ```

## 2. The "Zip Root" Fallacy (Code Packaging)
**Symptom:** `ModuleNotFoundError: No module named 'tools'` or `config`.
**Context:** `omega_core` is not self-contained. It imports `config.py` (root) and `tools.multi_dir_loader`. Zipping just `omega_core/` is insufficient.
**Solution:**
- **Manifest Zipping:** Explicitly include all dependencies.
- **Command:** `zip -r omega_core.zip omega_core/ config.py tools/`
- **Verification:** Always unzip locally (`unzip -l`) to verify structure before upload.

## 3. The "Ghost" Refactor (Stale Imports)
**Symptom:** `ImportError: cannot import name 'trainer_v51'`.
**Context:** We renamed `trainer_v51.py` to `trainer.py` but forgot `omega_core/__init__.py` which acted as a shim.
**Solution:**
- **Grep Audit:** After any rename, run `grep -r "old_name" .`.
- **Clean Init:** Ensure `__init__.py` exposes the *new* names.

## 4. The "Matrix Explosion" (OOM on Spot Instances)
**Symptom:** `Replicas low on memory: workerpool0`.
**Context:** Vectorized physics (`pad_traces`) converts sparse lists to dense `(N, L)` matrices. 20 files (400MB disk) became >16GB RAM.
**Solution:**
- **Cap Rows:** Explicitly limit rows (`df.head(10000)`) for hyperparameter tuning. 10k rows is statistically sufficient for parameter sensitivity analysis.
- **Garbage Collection:** Explicitly call `gc.collect()` inside optimization loops.
- **Canary Flight:** Launch **1** worker with `N_WORKERS=1` to verify memory stability before scaling to 15.

## 5. The "Dual-Channel" Telemetry (Data Recovery)
**Symptom:** GCS Upload fails (403/Timeout) at the very end of a 30-minute job. Data is lost.
**Context:** Spot instances have unstable networks/permissions during termination.
**Solution:**
- **Stdout Backup:** Always `print(json.dumps(result))` to stdout.
- **Log Scraper:** Use `gcloud logging read` to recover the JSON from logs if the file doesn't appear in GCS. This saved the "God View" operation.

## 6. BigQuery Time & Schema
- **Time:** Never use `CURRENT_DATE()` for historical data. Use `(SELECT MAX(trade_date) ...)` as the anchor.
- **Schema:** Never use `SELECT * EXCEPT(...)` for ML training. It fails on complex types (`RECORD`). Always use **Explicit Column Selection** (`SELECT open, close, sigma...`).

---
**Directive for Future Agents:**
Before submitting ANY cloud job, run a **"Pre-Flight Checklist"** against these 6 points.
