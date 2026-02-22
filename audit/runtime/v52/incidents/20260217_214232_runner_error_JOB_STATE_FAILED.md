# Incident 20260217_214232_runner_error_JOB_STATE_FAILED
- ts: 2026-02-17 21:42:32
- reason: runner_error_JOB_STATE_FAILED
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-17 21:25:52",
  "git_hash": "aa8abb7",
  "bucket": "gs://omega_v52",
  "windows_expected": 263,
  "linux_expected": 484,
  "stage": "build_base_matrix",
  "frame": {
    "linux_done": 484,
    "windows_done": 263,
    "windows_task_state": "Ready",
    "probe_linux": 484,
    "probe_windows": 263,
    "probe_ok": true,
    "updated_at": "2026-02-17 21:25:53"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-17 21:26:00"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-132600_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-132600_aa8abb7/base_matrix.meta.json",
    "base_matrix_exec_mode": "vertex",
    "base_matrix_machine_type": "n1-highmem-32",
    "base_matrix_spot": false
  },
  "train": {},
  "backtest": {},
  "run_id": "20260217-132600",
  "data_pattern": "gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet"
}
```

## screen -ls
```text
There is a screen on:
	74306.v60_ai_watchdog_aa8abb7	(Detached)
1 Socket in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh
74306 SCREEN -dmS v60_ai_watchdog_aa8abb7 bash -lc 
cd /Users/zephryj/work/Omega_vNext && \
PYTHONUNBUFFERED=1 python3 -u tools/ai_incident_watchdog.py \
  --hash aa8abb7 \
  --bucket gs://omega_v52 \
  --repo-root /Users/zephryj/work/Omega_vNext \
  --poll-sec 120 \
  --status-stale-sec 7200 \
  --upload-stall-sec 1800 \
  --cooldown-sec 1800 \
  --max-triggers 20 \
  --auto-resume \
  --context-file audit/v60_optimization_audit_final.md \
  --context-file audit/v6.md \
  --context-file handover/ai-direct/entries/20260216_vertex_god_view_lessons.md \
  --autopilot-upload-mode wait_existing \
  --autopilot-launch "PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1" \
  >> audit/runtime/v52/ai_watchdog_aa8abb7.log 2>&1

74307 login -pflq zephryj /bin/bash -lc 
cd /Users/zephryj/work/Omega_vNext && \
PYTHONUNBUFFERED=1 python3 -u tools/ai_incident_watchdog.py \
  --hash aa8abb7 \
  --bucket gs://omega_v52 \
  --repo-root /Users/zephryj/work/Omega_vNext \
  --poll-sec 120 \
  --status-stale-sec 7200 \
  --upload-stall-sec 1800 \
  --cooldown-sec 1800 \
  --max-triggers 20 \
  --auto-resume \
  --context-file audit/v60_optimization_audit_final.md \
  --context-file audit/v6.md \
  --context-file handover/ai-direct/entries/20260216_vertex_god_view_lessons.md \
  --autopilot-upload-mode wait_existing \
  --autopilot-launch "PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1" \
  >> audit/runtime/v52/ai_watchdog_aa8abb7.log 2>&1

74308 bash -lc 
cd /Users/zephryj/work/Omega_vNext && \
PYTHONUNBUFFERED=1 python3 -u tools/ai_incident_watchdog.py \
  --hash aa8abb7 \
  --bucket gs://omega_v52 \
  --repo-root /Users/zephryj/work/Omega_vNext \
  --poll-sec 120 \
  --status-stale-sec 7200 \
  --upload-stall-sec 1800 \
  --cooldown-sec 1800 \
  --max-triggers 20 \
  --auto-resume \
  --context-file audit/v60_optimization_audit_final.md \
  --context-file audit/v6.md \
  --context-file handover/ai-direct/entries/20260216_vertex_god_view_lessons.md \
  --autopilot-upload-mode wait_existing \
  --autopilot-launch "PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1" \
  >> audit/runtime/v52/ai_watchdog_aa8abb7.log 2>&1

74311 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -u tools/ai_incident_watchdog.py --hash aa8abb7 --bucket gs://omega_v52 --repo-root /Users/zephryj/work/Omega_vNext --poll-sec 120 --status-stale-sec 7200 --upload-stall-sec 1800 --cooldown-sec 1800 --max-triggers 20 --auto-resume --context-file audit/v60_optimization_audit_final.md --context-file audit/v6.md --context-file handover/ai-direct/entries/20260216_vertex_god_view_lessons.md --autopilot-upload-mode wait_existing --autopilot-launch PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

```

## Tail: autopilot runner log
```text
[2026-02-17 21:07:04]     [Fallback] state=JOB_STATE_FAILED elapsed=1080s
[2026-02-17 21:07:04] Traceback (most recent call last):
[2026-02-17 21:07:04]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 21:07:04]     submit_job(
[2026-02-17 21:07:04]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 21:07:04]     _submit_via_gcloud_fallback(
[2026-02-17 21:07:04]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 21:07:04]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 21:07:04] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/5958504886764044288
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 875, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 641, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.meta.json
[2026-02-17 21:20:14] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 21:20:14] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-17 21:20:14] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 21:20:14] Backtest month guard enabled: 2025,202601
[2026-02-17 21:20:14] Recursive audit passed at node=bootstrap
[2026-02-17 21:20:15] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 21:20:15] Frame stage complete.
[2026-02-17 21:20:15] Recursive audit passed at node=frame_complete
[2026-02-17 21:20:19] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 21:20:19] Upload stage complete.
[2026-02-17 21:20:23] GCS counts linux1=484 windows1=263
[2026-02-17 21:20:23] Building v60 base matrix with relaxed physics gates...
[2026-02-17 21:20:23] Recursive audit passed at node=pre_base_matrix
[2026-02-17 21:20:23] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132023_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132023_aa8abb7/base_matrix.meta.json --script-arg=--max-rows-per-file=10000
[2026-02-17 21:20:23] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 21:20:23]   warnings.warn(
[2026-02-17 21:20:24] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 21:20:24]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 21:20:24] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 21:20:27] [+] Code bundle uploaded successfully.
[2026-02-17 21:20:27] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-212027
[2026-02-17 21:20:27] [*] Forcing gcloud fallback submission path.
[2026-02-17 21:20:31] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/178134765034012672
[2026-02-17 21:20:33]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 21:21:04]     [Fallback] state=JOB_STATE_PENDING elapsed=33s
[2026-02-17 21:21:35]     [Fallback] state=JOB_STATE_PENDING elapsed=64s
[2026-02-17 21:22:07]     [Fallback] state=JOB_STATE_PENDING elapsed=95s
[2026-02-17 21:22:38]     [Fallback] state=JOB_STATE_PENDING elapsed=126s
[2026-02-17 21:23:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=157s
[2026-02-17 21:23:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=189s
[2026-02-17 21:24:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=220s
[2026-02-17 21:24:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=251s
[2026-02-17 21:25:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=282s
[2026-02-17 21:25:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=315s
[2026-02-17 21:25:52] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 21:25:52] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-17 21:25:52] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 21:25:52] Backtest month guard enabled: 2025,202601
[2026-02-17 21:25:52] Recursive audit passed at node=bootstrap
[2026-02-17 21:25:53] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 21:25:53] Frame stage complete.
[2026-02-17 21:25:53] Recursive audit passed at node=frame_complete
[2026-02-17 21:25:56] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 21:25:56] Upload stage complete.
[2026-02-17 21:26:00] GCS counts linux1=484 windows1=263
[2026-02-17 21:26:00] Building v60 base matrix with relaxed physics gates...
[2026-02-17 21:26:00] Recursive audit passed at node=pre_base_matrix
[2026-02-17 21:26:00] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132600_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132600_aa8abb7/base_matrix.meta.json
[2026-02-17 21:26:00] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 21:26:00]   warnings.warn(
[2026-02-17 21:26:01] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 21:26:01]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 21:26:01] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 21:26:04] [+] Code bundle uploaded successfully.
[2026-02-17 21:26:04] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-212604
[2026-02-17 21:26:04] [*] Forcing gcloud fallback submission path.
[2026-02-17 21:26:08] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/7968236220478128128
[2026-02-17 21:26:09]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 21:26:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=32s
[2026-02-17 21:27:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=63s
[2026-02-17 21:27:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=95s
[2026-02-17 21:28:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=126s
[2026-02-17 21:28:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=157s
[2026-02-17 21:29:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=188s
[2026-02-17 21:29:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=219s
[2026-02-17 21:30:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=251s
[2026-02-17 21:30:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=282s
[2026-02-17 21:31:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=314s
[2026-02-17 21:31:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=346s
[2026-02-17 21:32:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=377s
[2026-02-17 21:32:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=411s
[2026-02-17 21:33:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=442s
[2026-02-17 21:34:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=473s
[2026-02-17 21:34:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=505s
[2026-02-17 21:35:05]     [Fallback] state=JOB_STATE_RUNNING elapsed=536s
[2026-02-17 21:35:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=568s
[2026-02-17 21:36:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=600s
[2026-02-17 21:36:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=631s
[2026-02-17 21:37:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=662s
[2026-02-17 21:37:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=693s
[2026-02-17 21:38:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=725s
[2026-02-17 21:38:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=757s
[2026-02-17 21:39:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=788s
[2026-02-17 21:39:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=819s
[2026-02-17 21:40:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=851s
[2026-02-17 21:40:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=883s
[2026-02-17 21:41:23]     [Fallback] state=JOB_STATE_FAILED elapsed=914s
[2026-02-17 21:41:23] Traceback (most recent call last):
[2026-02-17 21:41:23]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 21:41:23]     submit_job(
[2026-02-17 21:41:23]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 21:41:23]     _submit_via_gcloud_fallback(
[2026-02-17 21:41:23]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 21:41:23]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 21:41:23] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/7968236220478128128
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 875, in <module>
    recursive_audit_checkpoint(
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 641, in main
    state["optimization"]["base_matrix_spot_error"] = str(spot_exc)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132600_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132600_aa8abb7/base_matrix.meta.json

```

## Tail: autopilot log
```text
[2026-02-17 20:58:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=577s
[2026-02-17 20:59:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=608s
[2026-02-17 20:59:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=639s
[2026-02-17 21:00:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=671s
[2026-02-17 21:00:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=703s
[2026-02-17 21:01:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=734s
[2026-02-17 21:01:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=766s
[2026-02-17 21:02:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=797s
[2026-02-17 21:02:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=830s
[2026-02-17 21:03:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=861s
[2026-02-17 21:03:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=892s
[2026-02-17 21:04:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=923s
[2026-02-17 21:04:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=956s
[2026-02-17 21:05:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=987s
[2026-02-17 21:06:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=1018s
[2026-02-17 21:06:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=1049s
[2026-02-17 21:07:04]     [Fallback] state=JOB_STATE_FAILED elapsed=1080s
[2026-02-17 21:07:04] Traceback (most recent call last):
[2026-02-17 21:07:04]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 21:07:04]     submit_job(
[2026-02-17 21:07:04]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 21:07:04]     _submit_via_gcloud_fallback(
[2026-02-17 21:07:04]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 21:07:04]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 21:07:04] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/5958504886764044288
[2026-02-17 21:20:14] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 21:20:14] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-17 21:20:14] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 21:20:14] Backtest month guard enabled: 2025,202601
[2026-02-17 21:20:14] Recursive audit passed at node=bootstrap
[2026-02-17 21:20:15] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 21:20:15] Frame stage complete.
[2026-02-17 21:20:15] Recursive audit passed at node=frame_complete
[2026-02-17 21:20:19] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 21:20:19] Upload stage complete.
[2026-02-17 21:20:23] GCS counts linux1=484 windows1=263
[2026-02-17 21:20:23] Building v60 base matrix with relaxed physics gates...
[2026-02-17 21:20:23] Recursive audit passed at node=pre_base_matrix
[2026-02-17 21:20:23] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132023_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132023_aa8abb7/base_matrix.meta.json --script-arg=--max-rows-per-file=10000
[2026-02-17 21:20:23] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 21:20:23]   warnings.warn(
[2026-02-17 21:20:24] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 21:20:24]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 21:20:24] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 21:20:27] [+] Code bundle uploaded successfully.
[2026-02-17 21:20:27] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-212027
[2026-02-17 21:20:27] [*] Forcing gcloud fallback submission path.
[2026-02-17 21:20:31] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/178134765034012672
[2026-02-17 21:20:33]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 21:21:04]     [Fallback] state=JOB_STATE_PENDING elapsed=33s
[2026-02-17 21:21:35]     [Fallback] state=JOB_STATE_PENDING elapsed=64s
[2026-02-17 21:22:07]     [Fallback] state=JOB_STATE_PENDING elapsed=95s
[2026-02-17 21:22:38]     [Fallback] state=JOB_STATE_PENDING elapsed=126s
[2026-02-17 21:23:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=157s
[2026-02-17 21:23:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=189s
[2026-02-17 21:24:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=220s
[2026-02-17 21:24:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=251s
[2026-02-17 21:25:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=282s
[2026-02-17 21:25:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=315s
[2026-02-17 21:25:52] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 21:25:52] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-17 21:25:52] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 21:25:52] Backtest month guard enabled: 2025,202601
[2026-02-17 21:25:52] Recursive audit passed at node=bootstrap
[2026-02-17 21:25:53] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 21:25:53] Frame stage complete.
[2026-02-17 21:25:53] Recursive audit passed at node=frame_complete
[2026-02-17 21:25:56] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 21:25:56] Upload stage complete.
[2026-02-17 21:26:00] GCS counts linux1=484 windows1=263
[2026-02-17 21:26:00] Building v60 base matrix with relaxed physics gates...
[2026-02-17 21:26:00] Recursive audit passed at node=pre_base_matrix
[2026-02-17 21:26:00] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132600_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-132600_aa8abb7/base_matrix.meta.json
[2026-02-17 21:26:00] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 21:26:00]   warnings.warn(
[2026-02-17 21:26:01] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 21:26:01]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 21:26:01] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 21:26:04] [+] Code bundle uploaded successfully.
[2026-02-17 21:26:04] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-212604
[2026-02-17 21:26:04] [*] Forcing gcloud fallback submission path.
[2026-02-17 21:26:08] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/7968236220478128128
[2026-02-17 21:26:09]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 21:26:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=32s
[2026-02-17 21:27:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=63s
[2026-02-17 21:27:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=95s
[2026-02-17 21:28:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=126s
[2026-02-17 21:28:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=157s
[2026-02-17 21:29:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=188s
[2026-02-17 21:29:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=219s
[2026-02-17 21:30:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=251s
[2026-02-17 21:30:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=282s
[2026-02-17 21:31:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=314s
[2026-02-17 21:31:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=346s
[2026-02-17 21:32:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=377s
[2026-02-17 21:32:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=411s
[2026-02-17 21:33:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=442s
[2026-02-17 21:34:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=473s
[2026-02-17 21:34:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=505s
[2026-02-17 21:35:05]     [Fallback] state=JOB_STATE_RUNNING elapsed=536s
[2026-02-17 21:35:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=568s
[2026-02-17 21:36:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=600s
[2026-02-17 21:36:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=631s
[2026-02-17 21:37:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=662s
[2026-02-17 21:37:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=693s
[2026-02-17 21:38:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=725s
[2026-02-17 21:38:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=757s
[2026-02-17 21:39:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=788s
[2026-02-17 21:39:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=819s
[2026-02-17 21:40:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=851s
[2026-02-17 21:40:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=883s
[2026-02-17 21:41:23]     [Fallback] state=JOB_STATE_FAILED elapsed=914s
[2026-02-17 21:41:23] Traceback (most recent call last):
[2026-02-17 21:41:23]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 21:41:23]     submit_job(
[2026-02-17 21:41:23]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 21:41:23]     _submit_via_gcloud_fallback(
[2026-02-17 21:41:23]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 21:41:23]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 21:41:23] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/7968236220478128128

```

## Tail: uplink log
```text
[2026-02-17 21:00:29] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 21:00:31] windows1 sync rc=0
[2026-02-17 21:00:31] uplink cycle sleep 300s
[2026-02-17 21:05:31] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 21:05:34] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 21:05:36] windows1 sync rc=0
[2026-02-17 21:05:36] uplink cycle sleep 300s
[2026-02-17 21:10:36] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 21:10:39] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 21:10:42] windows1 sync rc=0
[2026-02-17 21:10:42] uplink cycle sleep 300s
[2026-02-17 21:15:42] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 21:15:44] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 21:15:46] windows1 sync rc=0
[2026-02-17 21:15:46] uplink cycle sleep 300s
[2026-02-17 21:20:46] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 21:20:49] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 21:20:51] windows1 sync rc=0
[2026-02-17 21:20:51] uplink cycle sleep 300s
[2026-02-17 21:25:51] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 21:25:53] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 21:25:55] windows1 sync rc=0
[2026-02-17 21:25:55] uplink cycle sleep 300s
[2026-02-17 21:30:55] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 21:30:57] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 21:30:59] windows1 sync rc=0
[2026-02-17 21:30:59] uplink cycle sleep 300s
[2026-02-17 21:35:59] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 21:36:04] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 21:36:07] windows1 sync rc=0
[2026-02-17 21:36:07] uplink cycle sleep 300s
[2026-02-17 21:41:07] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 21:41:10] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 21:41:12] windows1 sync rc=0
[2026-02-17 21:41:12] uplink cycle sleep 300s

```