# Pipeline Log Index (v62)

This document provides the standard log file locations for monitoring the Stage 1, Stage 2, and Stage 3 pipeline runs.

## Stage 1: Base Lake ETL

| Host | Log Type | Path (Relative to Repo Root) |
|------|----------|-----------------------------|
| **Linux** | ETL Output | `audit/stage1_linux_v62.log` |
| **Linux** | Supervisor | `audit/linux_stage1_supervisor.log` |
| **Linux** | Systemd | `sudo journalctl -u omega_stage1_linux_* -f` |
| **Windows**| ETL Output | `audit/stage1_windows_v62.log` |

## Stage 2: Physics Compute

Currently, `tools/stage2_physics_compute.py` outputs directly to `stdout`/`stderr`. 
*   **Recommended Command:** `python3 tools/stage2_physics_compute.py [args] 2>&1 | tee audit/stage2_compute.log`

## Stage 3: Training & Backtest

*   **GCP Vertex AI:** Logs are available in the [Google Cloud Console Logs Explorer](https://console.cloud.google.com/logs/).
*   **Local Backtest:** `python3 tools/run_local_backtest.py [args] 2>&1 | tee audit/local_backtest.log`

## Monitoring Shortcuts (Linux)

```bash
# Watch Stage 1 progress
tail -f audit/stage1_linux_v62.log

# Check for OOM or Systemd errors
sudo journalctl -u heavy-workload.slice -n 100
```
