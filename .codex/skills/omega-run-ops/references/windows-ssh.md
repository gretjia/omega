# Windows Over SSH (PowerShell) Notes

## Defaults

- Prefer `powershell -NoProfile -NonInteractive -EncodedCommand <b64>`.
- Disable progress noise when needed: `$ProgressPreference = "SilentlyContinue"`.
- Avoid `$pid` as a variable name in scripts: it aliases the read-only `$PID`.

## Why It Feels Slow

- Every `ssh` call spawns a fresh `powershell.exe` process (cold start).
- First-time module analysis can emit "preparing modules for first use" progress.
- WMI and performance counters are expensive:
  - `Get-CimInstance Win32_Process`
  - `Get-Counter ...`

## Preferred Monitoring (Low Overhead)

1. Tail the pipeline log:
   - `Get-Content audit\_pipeline_frame.log -Tail 20 -ErrorAction SilentlyContinue`
2. Count `*.done` with the pinned git short:
   - `(Get-ChildItem D:\Omega_frames\v52\frames\host=windows1 -Filter "*_<gitshort>.parquet.done" -ErrorAction SilentlyContinue).Count`
3. If started via Task Scheduler, check task state/result:
   - `Get-ScheduledTask -TaskName Omega_v52_frame02 | Select TaskName,State`
   - `Get-ScheduledTaskInfo -TaskName Omega_v52_frame02 | Select LastRunTime,LastTaskResult`

## Long-Running Jobs: Use Task Scheduler

Problem: long runs started from an SSH session may be killed when the session ends.

Critical detail: `pipeline_runner.py` appends `os.getcwd()` to `sys.path`, so the **WorkingDirectory must be the repo root** (e.g., `D:\work\Omega_vNext`). If a task runs from `C:\Users\...\Temp`, imports like `pipeline_runner` can fail.

Use:

- `New-ScheduledTaskAction -WorkingDirectory "D:\work\Omega_vNext"`
- Python invocation uses absolute paths:
  - `C:\Python314\python.exe -u D:\work\Omega_vNext\pipeline_runner.py ...`
