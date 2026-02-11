# OMEGA Parallel Trainer (`parallel_trainer`)

> Last updated: 2026-02-11 (v5.0 Holographic Damper Integration)

## v5.0 Integration Status
This module is fully integrated into the OMEGA v5.0 Pipeline. 
The script `run_parallel_v31.py` automatically uses `omega_core.trainer.OmegaTrainerV3`, inheriting:
*   **Holographic Damper** logic.
*   **Universal SRL** ($\delta=0.5$).
*   **Multi-Symbol** compatibility.

### Usage in v5.0
**Phase 2 (Training):**
```bash
python parallel_trainer/run_parallel_v31.py --stage-dir D:/Omega_train_stage
```
*Note: We recommend using D: drive for staging to avoid system drive contention.*

**Phase 3 (Backtest):**
```bash
python parallel_trainer/run_parallel_backtest_v31.py
```

---

## 模块职责

`parallel_trainer` 的目标是“语义不变的加速”：
1. 并行执行单文件特征生成（多进程）
2. 串行执行 `StandardScaler` / `SGDClassifier.partial_fit`（保持更新顺序）
3. 提供 checkpoint / resume（可恢复训练）

## 关键文件

1. `parallel_trainer/parallel_config.py`
2. `parallel_trainer/parallel_dataflow.py`
3. `parallel_trainer/parallel_trainer.py`
4. `parallel_trainer/run_parallel_v31.py`
5. `parallel_trainer/run_parallel_backtest_v31.py`

## v40 并行运行约定（Frame / Train / Backtest）

*(Legacy v40 instructions preserved for reference)*

1. 并行 Frame（从 `data/level2/*.7z`）
```bash
./.venv/bin/python tools/run_l2_audit_driver.py \
  --workers 12 \
  --year 2026 \
  --output-dir data/level2_frames_v40 \
  --skip-report
```

2. 并行 Train（推荐 `file-list`，避免共享盘目录扫描阻塞）
```bash
./.venv/bin/python parallel_trainer/run_parallel_v31.py \
  --file-list audit/v34_epi_manifest_round1.txt \
  --workers 12 \
  --batch-rows 200000
```

3. 并行 Backtest（同样支持 `file-list` / `max-files`）
```bash
./.venv/bin/python parallel_trainer/run_parallel_backtest_v31.py \
  --policy artifacts/checkpoint_rows_XXXX.pkl \
  --file-list audit/v34_epi_manifest_round1.txt \
  --workers 12
```

---

## 📜 Feb 7th Master Debugging Chronicle: The Full Backtest Journey

*(Historical record of v3.1/v40 debugging - Key Lessons for AI)*

### 🚩 Trap 1: The Zombie Process & Stale Environment
- **Symptom:** `NameError: name 'policy_cfg' is not defined` even though the code on disk was correct.
- **Cause:** A previous Python process (PID 5372) was likely running in a corrupted state or with stale `__pycache__` entries.
- **Solution:** Hard reset. Use `Stop-Process -Id <PID> -Force` and clean up all `python` processes before restarting.
- **Lesson:** **Code on disk != Code in memory.** In parallel environments, zombie workers can hold onto old logic.

### 🚩 Trap 2: The "Partial Success" Illusion (Missing `ret_k`)
- **Symptom:** Process running perfectly, millions of rows processed, but **0 PnL and 0 Trades**.
- **Cause:** Raw data already had features (`epiplexity`, etc.) but lacked labels (`ret_k`). The code optimization `if missing_features: run_prep()` skipped label generation because features were already present.
- **Fix:** Explicitly check for both inputs and targets: `if missing_features or "ret_k" not in df: run_prep()`.
- **Lesson:** **Feature existence does not imply label existence.** Verify the *entire* schema, not just the inputs.

### 🚩 Trap 3: The "Denominator Trap" (Astronomical PnL)
- **Symptom:** PnL reporting values like `7.29e+20`.
- **Cause:** Data corruption in raw CSVs (e.g., price = 0.0 or near-zero) caused division by zero in return calculation (`ret_k = change / price`). 
- **Fix:** Implemented hard clipping in the simulation: `ret_k_clipped = np.clip(ret_k, -0.02, 0.02)`. 
- **Lesson:** **Never trust raw data returns in backtests.** Always apply a "Reality Filter" (clipping) to handle micro-structure outliers.

### 🚩 Trap 4: The Multi-Process Error Swallow
- **Symptom:** Workers failing silently or returning empty dicts `{}`.
- **Cause:** Standard `multiprocessing.Pool` often loses the context of exceptions. 
- **Fix:** Wrap the *entire* worker core in a `try...except` that returns `traceback.format_exc()`.
- **Lesson:** **Multiprocessing is a black hole for errors.** Forced traceback reporting is mandatory.

### 🚩 Trap 5: The Version Configuration Mismatch
- **Symptom:** `AttributeError: 'L2PipelineConfig' object has no attribute 'model'`.
- **Cause:** Reusing v1 logic (which had `cfg.model`) in v3.1 (which uses `cfg.train`).
- **Fix:** Updated `config.py` to include `decision_margin` in `L2TrainConfig` and used `getattr(cfg.train, "decision_margin", 0.05)` for robustness.
- **Lesson:** **Strictly separate v1/v2 vs v3 architecture.** Don't assume config hierarchies are preserved across major versions.

### 🚩 Trap 6: The Modulo Progress Ghost
- **Symptom:** No progress logs appearing for a long time.
- **Cause:** `if count % 500000 == 0:` check. If a worker returns 500,001 rows, the modulo check skips the log indefinitely.
- **Fix:** Use a threshold-based check: `if total_rows - last_log_rows >= 500000:`.
- **Lesson:** **Avoid strict modulo for logging in variable-increment loops.**

---

## 🛠️ Summary of Applied Fixes

1.  **Script:** `run_parallel_backtest_v31.py`
    - Added `traceback` logging.
    - Added `has_ret_k` validation.
    - Added `np.clip` for returns.
    - Implemented `getattr` for dynamic margin.
2.  **Config:** `config.py`
    - Added `decision_margin` to `L2TrainConfig`.
3.  **Skills:** Created `parallel-backtest-debugger` skill.

**Final Status:** Backtest finished successfully with 1.39M trades and 3220.99 PnL units.
