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

## Hash-Safe Frame Cleanup (Do Not Damage New Frames)

Use this when old run hashes (for example `4f9c786`) are mixed with current hash output.

Principle:
- Keep only `*_<gitshort>.parquet`, `*.parquet.done`, `*.parquet.meta.json`.
- Delete by suffix pattern + hash mismatch only.
- Always count/hash-audit before and after deletion.

Linux example:

```bash
# audit current hash distribution
find /omega_pool/parquet_data/v52/frames/host=linux1 -maxdepth 1 -type f -name '*.parquet' -printf '%f\n' \
  | sed -E 's/.*_([0-9a-f]{7})\.parquet/\1/' | sort | uniq -c

# delete only non-target hashes
find /omega_pool/parquet_data/v52/frames/host=linux1 -maxdepth 1 -type f \
  \( -name '*.parquet' -o -name '*.parquet.done' -o -name '*.parquet.meta.json' \) \
  ! -name '*_<gitshort>.parquet' \
  ! -name '*_<gitshort>.parquet.done' \
  ! -name '*_<gitshort>.parquet.meta.json' -delete
```

Windows example:

```powershell
$root = "D:\Omega_frames\v52\frames\host=windows1"
$keep = "<gitshort>"
Get-ChildItem -Path $root -File -ErrorAction SilentlyContinue |
  Where-Object {
    $_.Name -match "_([0-9a-f]{7})\.parquet(\.done|\.meta\.json)?$" -and $Matches[1] -ne $keep
  } | Remove-Item -Force
```

GCS cleanup by old hash (prefer `gcloud storage rm` over long `gsutil` loops):

```bash
for host in linux1 windows1; do
  gcloud storage rm "gs://omega_v52/omega/v52/frames/host=${host}/*_<oldhash>.parquet" || true
  gcloud storage rm "gs://omega_v52/omega/v52/frames/host=${host}/*_<oldhash>.parquet.done" || true
  gcloud storage rm "gs://omega_v52/omega/v52/frames/host=${host}/*_<oldhash>.parquet.meta.json" || true
done
```

## Framing + Upload in Parallel (Mac Capacity Guarded)

Target behavior:
- Framing continues on workers.
- Mac continuously uploads completed frames in small batches.
- Upload loop is detached from SSH/tool sessions.

Recommended setup:
- Keep uploader batch size around 10-15 GB (`BATCH_SIZE_GB`) to avoid Mac disk pressure.
- Run uploader in detached `screen` session.
- Every cycle: sync `linux1` then `windows1`, sleep 300s.
- Use hash-scoped incremental filtering so already uploaded parquet is skipped.
- Enforce single-uploader instance. Before restart, kill old `uplink_loop`/`mac_gateway_sync.py` processes.
- In uploader implementation, prefer retryable `scp` + explicit file-list `gcloud storage cp` (no wildcard-only copy).
- If upload logs show endless `Resuming upload ... parallel_composite_uploads`, run:
  `gcloud config set storage/parallel_composite_upload_enabled False`

Detached uploader pattern:

```bash
screen -dmS v60_uplink_<gitshort> bash -lc '
cd /Users/zephryj/work/Omega_vNext
while true; do
  PYTHONUNBUFFERED=1 python3 -u tools/mac_gateway_sync.py --bucket gs://omega_v52 --host linux1 --hash <gitshort>
  PYTHONUNBUFFERED=1 python3 -u tools/mac_gateway_sync.py --bucket gs://omega_v52 --host windows1 --hash <gitshort>
  sleep 300
done
'
```

Progress checks:

```bash
# frame progress
ssh linux1-lx "find /omega_pool/parquet_data/v52/frames/host=linux1 -maxdepth 1 -name '*_<gitshort>.parquet.done' | wc -l"
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '
$n=(Get-ChildItem -Path "D:\Omega_frames\v52\frames\host=windows1" -Filter "*_<gitshort>.parquet.done" -ErrorAction SilentlyContinue).Count
Write-Output $n
'

# gcs progress
gcloud storage ls "gs://omega_v52/omega/v52/frames/host=linux1/*_<gitshort>.parquet" | wc -l
gcloud storage ls "gs://omega_v52/omega/v52/frames/host=windows1/*_<gitshort>.parquet" | wc -l
```

Cadence:
- Frame done-count polling: every 2-3 minutes.
- Upload/GCS count polling: every 5-10 minutes.
- Escalate only when counts stop moving beyond stall threshold.

## AI Watchdog + Auto-Resume (Unattended Runs)

When the user requires hands-off continuity, run `tools/ai_incident_watchdog.py` with:
- `--trigger-debug-agent` to launch AI debug on incidents (default agent: `gemini -y`).
- `--auto-resume` to relaunch missing `autopilot`/`uplink` sessions.
- Hash-pinned session names and logs (for example `v60_autopilot_<hash>`).

Legacy compatibility:
- `--trigger-codex` is still accepted as an alias, but should not be used in new runbooks.

Recommended detached launch:

```bash
screen -dmS v60_ai_watchdog_<gitshort> bash -lc '
cd /Users/zephryj/work/Omega_vNext
PYTHONUNBUFFERED=1 python3 -u tools/ai_incident_watchdog.py \
  --hash <gitshort> \
  --trigger-debug-agent \
  --auto-resume \
  --poll-sec 120 \
  --status-stale-sec 1200 \
  --upload-stall-sec 2400 \
  --cooldown-sec 1800
'
```

Context persistence requirement:
- Keep machine-readable live state in `handover/ai-direct/live/v60_run_<hash>.json`.
- Keep append-only operations history in `handover/ai-direct/live/v60_events_<hash>.md`.
- On incident, write snapshot + AI debug report paths so another agent can resume immediately.

## Vertex Throughput/Cost Guardrails (v60)

When running v60 on Vertex in `us-west1`, do not assume desktop-size machine types are available.

1. Validate quota reality before picking machine sizes:
   - `aiplatform.googleapis.com/custom_model_training_n2_cpus` (region limit)
   - `aiplatform.googleapis.com/custom_model_training_c2_cpus` (region limit)
   - `aiplatform.googleapis.com/custom_model_training_cpus` (total region limit)
2. Prefer machine types that actually start reliably in this project:
   - Base matrix: `n2-highmem-16` (memory-safe, starts reliably)
   - Swarm optimize: `n2-highmem-16`
   - Train: `n2-standard-16`
   - Backtest: `n2-standard-8`
3. Avoid indefinite pending:
   - Always run submitter with `--force-gcloud-fallback --sync --sync-timeout-sec=<N>`.
   - On timeout/failure, cancel and retry with a smaller or more available machine type.
4. Spot policy:
   - Use Spot only with explicit one-shot on-demand fallback.
   - For critical path ETA, default to on-demand.
5. Backtest split safety:
   - Keep train and test physically disjoint (`2023,2024` vs `2025 + 202601`).
   - Use explicit date-prefix filter in backtest payload (`--test-ym=2025,202601`) to prevent future 2026 non-Jan contamination.
6. Watchdog noise control:
   - Only trigger `upload_progress_stalled` during upload-related stages.
   - Do not fire upload stall incidents during `build_base_matrix`/`vertex_optimize`/`vertex_train`/`vertex_backtest`.

## Train/Backtest Data-Split + Memory Guardrails (v60)

1. Enforce split using filename day-key (`YYYYMMDD_*`) prefix, not plain substring matching.
   - Train keep-set: `day[:4] in {2023, 2024}`.
   - Backtest keep-set: `day[:4] in {2025, 2026}` and apply explicit `--test-ym=2025,202601`.
2. Avoid hidden sampling defaults in production runs.
   - Prefer `--max-files=0` and `--max-rows-per-file=0` (full coverage).
   - Use positive caps only as emergency OOM controls.
3. Add lightweight runtime telemetry for unattended runs.
   - Every N files log: `files used`, `rows processed`, `RSS memory`.
   - Keep per-file `gc.collect()` to reduce long-run memory drift.
4. Require auditable payload scope in autopilot logs.
   - Pass train/backtest caps explicitly from `v60_autopilot.py` to payload scripts.
   - This prevents silent behavior changes after restarts.

## Resources

- `scripts/ssh_ps.py`: run PowerShell scripts over SSH safely (EncodedCommand).
- `references/windows-ssh.md`: PowerShell-over-SSH details and common failure modes.
- `references/linux-framing-stall.md`: Linux framing stall signals and recovery steps.
