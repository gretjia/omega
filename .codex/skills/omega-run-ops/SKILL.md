---
name: omega-run-ops
description: Operate Omega_vNext multi-host runs (Mac controller + Windows/Linux workers) with pinned git tags, smoke gates, shard manifests, robust long-running job launch (Task Scheduler/nohup), and low-overhead monitoring via logs and *.done markers. Use when coordinating framing/training/backtest across Windows+Linux via SSH, or when PowerShell-over-SSH performance/quoting issues and worker lifecycle problems appear.
---

# Omega Run Ops

## Overview

Run Omega_vNext pipelines across Windows/Linux workers without losing reproducibility or wasting time on slow remote introspection.

## Workflow

1. Pin everything to a tag/commit; do not change worker working trees mid-run.
2. Run smoke gates (frame + compat; optionally train/backtest smoke) before full runs.
3. Split work by `archive_manifest_7z.txt` + shard lists; keep shards disjoint.
4. Start long jobs in a way that survives SSH disconnects.
5. Monitor progress using only file-based signals (log tail + `*.done` count) by default.
6. Escalate to heavier diagnostics only when signals stop moving.

## Low-Overhead Status Checks

Prefer these checks because they are fast, stable, and avoid WMI/perf-counter slowness.

Always substitute `<gitshort>` with the pinned commit short hash for this run (e.g., `git rev-parse --short HEAD`).

### Linux

```bash
ssh linux1-lx '
  cd /home/zepher/work/Omega_vNext &&
  tail -n 20 audit/_pipeline_frame.log 2>/dev/null || true
'

ssh linux1-lx '
  find /omega_pool/parquet_data/v52/frames/host=linux1 -maxdepth 1 -type f \
    -name "*_<gitshort>.parquet.done" 2>/dev/null | wc -l
'
```

### Windows (PowerShell)

Do not run heavy WMI/perf queries in tight loops. Start with: `tail log` + `done count` + `scheduled task state`.

Use `-EncodedCommand` or the wrapper script `scripts/ssh_ps.py` to avoid quoting issues.

Example (inline PowerShell via `ssh_ps.py`):

```bash
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '
$ProgressPreference="SilentlyContinue"
cd D:\work\Omega_vNext
(Get-ChildItem -Path "D:\Omega_frames\v52\frames\host=windows1" -Filter "*_<gitshort>.parquet.done" -ErrorAction SilentlyContinue).Count
Get-Content "audit\_pipeline_frame.log" -Tail 20 -ErrorAction SilentlyContinue
'
```

## Starting Long Jobs (Survive SSH Disconnect)

### Linux: prefer nohup

```bash
cd /home/zepher/work/Omega_vNext
nohup .venv/bin/python -u pipeline_runner.py --stage frame --config configs/hardware/linux.yaml \
  --archive-list audit/runtime/v52/shard_linux.txt > audit/_pipeline_frame.nohup.log 2>&1 &
echo $! > artifacts/runtime/v52/frame_linux1.pid
```

### Windows: prefer Task Scheduler

Why:
- OpenSSH sessions can kill child processes on disconnect.
- `pipeline_runner.py` relies on `os.getcwd()` for imports; **WorkingDirectory must be the repo root**.

Minimal pattern (PowerShell):

```powershell
$task = "Omega_v52_frame02"
$root = "D:\work\Omega_vNext"
$py = "C:\Python314\python.exe"
$args = "-u D:\work\Omega_vNext\pipeline_runner.py --stage frame --config D:\work\Omega_vNext\configs\hardware\windows1.yaml --archive-list D:\work\Omega_vNext\audit\runtime\v52\shard_windows1.txt"

$action = New-ScheduledTaskAction -Execute $py -Argument $args -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 7)

Register-ScheduledTask -TaskName $task -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
Start-ScheduledTask -TaskName $task
Get-ScheduledTask -TaskName $task | Select TaskName,State
Get-ScheduledTaskInfo -TaskName $task | Select LastRunTime,LastTaskResult
```

## Why SSH Introspection Can Be Slow (Record of Pitfalls)

1. Each `ssh` call cold-starts a new PowerShell process; first-time module prep can be very slow.
2. `Get-CimInstance Win32_Process` and `Get-Counter` are high-latency (WMI/perf counters). Avoid polling them.
3. Quoting in `zsh -> ssh -> powershell` is fragile; prefer `-EncodedCommand`.
4. Avoid the variable name `$pid` in PowerShell: it aliases the read-only `$PID` automatic variable.

## Troubleshooting Escalation

Escalate only if `*.done` is not increasing and log `LastWriteTime` stops moving.

1. Verify the job is still alive.
2. Check staging directory growth (I/O bound vs stuck).
3. On Linux, if it stalls after the first archive and processes sit in `futex_`, suspect `fork` + Polars runtime deadlock; use a tag that enforces `spawn` + pool reuse.

## Completion and Stale PID Hygiene

Use this order to mark a run as completed:

1. Log tail contains `Complete. Processed X/X archives.`
2. `*.done` count matches expected shard cardinality (or explicit rerun list size).
3. Runtime launcher state is terminal:
   - Windows Task Scheduler state is `Ready` (not `Running`)
   - Linux has no `pipeline_runner.py --stage frame` process

Important:
- Do not treat a PID file alone as liveness. PID files can be stale after normal completion.
- Keep status checks low-overhead (log tail + done count + scheduler/process existence) and avoid WMI/perf polling loops.

## Resources

- `scripts/ssh_ps.py`: run PowerShell scripts over SSH safely (EncodedCommand).
- `references/windows-ssh.md`: PowerShell-over-SSH details and common failure modes.
- `references/linux-framing-stall.md`: Linux framing stall signals and recovery steps.
