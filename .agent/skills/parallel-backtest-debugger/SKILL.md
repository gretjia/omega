---
name: parallel-backtest-debugger
description: Comprehensive expert workflow for diagnosing silent failures, data corruption, and configuration traps in OMEGA v3.1 parallel backtests.
---

# OMEGA Parallel Backtest Debugger

Use this skill when a parallel backtest (`run_parallel_backtest_*.py`) reports 0 trades, unrealistic PnL, or fails with vague errors.

## The Six Golden Diagnostic Rules

### 1. The Environment Reset (Zombie Killer)
If code changes on disk don't reflect in logs (e.g. `NameError` on defined vars):
- **Action:** Force kill all python processes: `Get-Process python* | Stop-Process -Force`.
- **Reason:** Windows workers can become "zombies" and hold stale code in memory.

### 2. The Entire Schema Check (Input != Output)
If rows are processed but PnL is 0:
- **Action:** Explicitly verify the **Target Column** (`ret_k`) exists separately from **Feature Columns**.
- **Trap:** `if missing_features:` might be `False` if only inputs are present. Use `if "ret_k" not in df:`.

### 3. The Reality Filter (Outlier Clipping)
If PnL is astronomical (e.g., `1e+20`):
- **Action:** Apply hard clipping to returns: `np.clip(ret_k, -0.02, 0.02)`.
- **Reason:** Division by zero in raw data (price=0) is common in micro-structure datasets.

### 4. Forced Traceback (Pool Transparency)
If workers fail silently or return `{}`:
- **Action:** Wrap the entire worker logic in:
  ```python
  try:
      # core logic
  except Exception:
      import traceback
      return {"error": traceback.format_exc(), "file": str(file_path)}
  ```

### 5. Config Version Separation (v1 vs v3)
If `AttributeError` occurs on `cfg.model` or `cfg.srl`:
- **Action:** Check if the script is trying to access a v1 hierarchy on a v3 `L2PipelineConfig` object.
- **Fix:** Update `L2TrainConfig` in `config.py` and use `getattr(cfg.train, "var", default)`.

### 6. Threshold-Based Logging (No Modulo)
If progress logs are missing:
- **Action:** Change `if count % N == 0` to `if count - last_log > N`.
- **Reason:** Variable increments in multi-file processing often "jump" over strict modulo checkpoints.

## Verification Checklist
- [ ] Are all `python` processes killed before restart?
- [ ] Does `_prepare_frames` run if `ret_k` is missing?
- [ ] Is `ret_k` clipped to ±2%?
- [ ] Does the worker return a full traceback on error?
- [ ] Is `decision_margin` being pulled from `cfg.train`?