# Troubleshooting Parallel Processing (OMEGA v3)

**Critical Engineering Guidelines for Future AI Agents**

> **WARNING**: Failure to adhere to these guidelines caused a 7-hour loss of compute time on 2026-02-07. Read this before modifying any `multiprocessing` code.

## 1. The "Zombie Deadlock" Incident (IPC Saturation)

### Symptoms
*   Driver process starts workers.
*   CPU usage is high (busy wait) or zero (lock wait).
*   **No logs** are produced for hours.
*   Process appears "active" in task manager but makes zero progress.

### Root Cause
Passing **Large Objects** (e.g., `SGDClassifier` models > 50MB, huge Config objects) as arguments to `pool.map` or `pool.apply_async`.
*   Python's `multiprocessing` uses `pickle` to serialize arguments to a pipe.
*   If the object is large (85MB+) and you spawn 3 million tasks, the OS pipe buffer fills up.
*   The Main process waits for the pipe to drain; Workers wait for the pipe to fill. **Deadlock.**

### The Fix: "Load From Disk" Pattern
**NEVER** pass the model object to the worker. Pass the **File Path**.

**BAD (Deadlock Risk):**
```python
# Main
model = load_huge_model()
tasks = [(file, model) for file in files] # 3M copies of 85MB = Crash/Hang
pool.map(worker_func, tasks)
```

**GOOD (Production Safe):**
```python
# Worker
_GLOBAL_MODEL = None
def get_model(path):
    global _GLOBAL_MODEL
    if _GLOBAL_MODEL is None:
        _GLOBAL_MODEL = load(path)
    return _GLOBAL_MODEL

def worker_func(args):
    file, model_path = args
    model = get_model(model_path) # Load once per process
    ...
```

---

## 2. The "Silent Failure" (Log Buffering)

### Symptoms
*   Process runs for hours.
*   Log file is empty (0 bytes).
*   Developer assumes it is "just initializing" or "working hard".
*   Reality: It crashed or deadlocked 1 second in, but the buffer held the output.

### The Fix: Force Flush
*   Always use `flush=True` in critical progress prints.
    ```python
    print(f"Progress: {i}", flush=True)
    ```
*   When using `Start-Process` in PowerShell, monitor `stderr` separately.

---

## 3. The "Lost Progress" (Checkpoint Frequency)

### Symptoms
*   Process runs for 30 minutes then is killed (manual stop or crash).
*   Resume logic finds the checkpoint is days old.
*   **Result**: 30 minutes of compute wasted.

### Root Cause
Checkpoint frequency was too low (e.g., "Every 100 files").
If the first batch is heavy (e.g., large Parquet files with Physics calc), it might take 40 minutes to finish batch #1.

### The Fix: Frequent Commits
*   Checkpoint every **Batch** (e.g., 50 files), or time-based (every 5 minutes).
*   Do not assume "files are small". Physics calculation is CPU intensive.

---

## Summary Checklist for Parallel Scripts

1.  [ ] **IPC Check**: Are task arguments small (strings/ints)?
2.  [ ] **Global Load**: Do workers load heavy resources from disk?
3.  [ ] **Flush**: Is `print(..., flush=True)` used for heartbeat logs?
4.  [ ] **Checkpoint**: Is state saved frequently enough to lose < 5 mins of work?
