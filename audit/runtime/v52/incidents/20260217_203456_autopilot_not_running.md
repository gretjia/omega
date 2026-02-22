# Incident 20260217_203456_autopilot_not_running
- ts: 2026-02-17 20:34:56
- reason: autopilot_not_running
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-17 20:22:36",
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
    "updated_at": "2026-02-17 20:22:37"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-17 20:22:44"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-122244_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-122244_aa8abb7/base_matrix.meta.json",
    "base_matrix_exec_mode": "vertex",
    "base_matrix_machine_type": "n2-highmem-16",
    "base_matrix_spot": false
  },
  "train": {},
  "backtest": {},
  "run_id": "20260217-122244",
  "data_pattern": "gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet"
}
```

## screen -ls
```text
There are screens on:
	87722.v60_ai_watchdog_aa8abb7	(Detached)
	15757.v60_autopilot_aa8abb7	(Detached)
2 Sockets in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
15757 SCREEN -dmS v60_autopilot_aa8abb7 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
15758 login -pflq zephryj /bin/bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh

```

## Tail: autopilot runner log
```text
[2026-02-17 20:02:45] GCS counts linux1=484 windows1=263
[2026-02-17 20:02:45] Building v60 base matrix with relaxed physics gates...
[2026-02-17 20:02:45] Recursive audit passed at node=pre_base_matrix
[2026-02-17 20:02:45] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-120245_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-120245_aa8abb7/base_matrix.meta.json
[2026-02-17 20:02:45] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 20:02:45]   warnings.warn(
[2026-02-17 20:02:46] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 20:02:46]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 20:02:46] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 20:02:48] [+] Code bundle uploaded successfully.
[2026-02-17 20:02:48] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-200248
[2026-02-17 20:02:48] [*] Forcing gcloud fallback submission path.
[2026-02-17 20:02:52] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/702804121622675456
[2026-02-17 20:02:53]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 20:03:24]     [Fallback] state=JOB_STATE_PENDING elapsed=32s
[2026-02-17 20:03:55]     [Fallback] state=JOB_STATE_PENDING elapsed=63s
[2026-02-17 20:04:26]     [Fallback] state=JOB_STATE_PENDING elapsed=94s
[2026-02-17 20:04:58]     [Fallback] state=JOB_STATE_PENDING elapsed=125s
[2026-02-17 20:05:29]     [Fallback] state=JOB_STATE_PENDING elapsed=156s
[2026-02-17 20:06:00]     [Fallback] state=JOB_STATE_PENDING elapsed=187s
[2026-02-17 20:06:31]     [Fallback] state=JOB_STATE_PENDING elapsed=218s
[2026-02-17 20:07:02]     [Fallback] state=JOB_STATE_PENDING elapsed=249s
[2026-02-17 20:07:34]     [Fallback] state=JOB_STATE_PENDING elapsed=281s
[2026-02-17 20:08:05]     [Fallback] state=JOB_STATE_PENDING elapsed=312s
[2026-02-17 20:08:36]     [Fallback] state=JOB_STATE_PENDING elapsed=343s
[2026-02-17 20:09:07]     [Fallback] state=JOB_STATE_PENDING elapsed=374s
[2026-02-17 20:09:38]     [Fallback] state=JOB_STATE_PENDING elapsed=406s
[2026-02-17 20:10:09]     [Fallback] state=JOB_STATE_PENDING elapsed=437s
[2026-02-17 20:10:40]     [Fallback] state=JOB_STATE_PENDING elapsed=468s
[2026-02-17 20:11:11]     [Fallback] state=JOB_STATE_PENDING elapsed=499s
[2026-02-17 20:11:43]     [Fallback] state=JOB_STATE_PENDING elapsed=530s
[2026-02-17 20:12:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=561s
[2026-02-17 20:12:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=592s
[2026-02-17 20:13:16]     [Fallback] state=JOB_STATE_RUNNING elapsed=623s
[2026-02-17 20:13:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=654s
[2026-02-17 20:14:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=685s
[2026-02-17 20:14:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=716s
[2026-02-17 20:15:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=748s
[2026-02-17 20:15:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=779s
[2026-02-17 20:16:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=810s
[2026-02-17 20:16:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=841s
[2026-02-17 20:17:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=872s
[2026-02-17 20:17:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=903s
[2026-02-17 20:18:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=934s
[2026-02-17 20:18:58]     [Fallback] state=JOB_STATE_FAILED elapsed=965s
[2026-02-17 20:18:58] Traceback (most recent call last):
[2026-02-17 20:18:58]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 20:18:58]     submit_job(
[2026-02-17 20:18:58]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 20:18:58]     _submit_via_gcloud_fallback(
[2026-02-17 20:18:58]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 20:18:58]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 20:18:58] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/702804121622675456
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 875, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 641, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-120245_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-120245_aa8abb7/base_matrix.meta.json
[2026-02-17 20:22:36] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 20:22:36] Machine plan base=n2-highmem-16 opt=n2-highmem-16 train=n2-standard-16 backtest=n2-standard-8
[2026-02-17 20:22:36] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 20:22:36] Backtest month guard enabled: 2025,202601
[2026-02-17 20:22:36] Recursive audit passed at node=bootstrap
[2026-02-17 20:22:37] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 20:22:37] Frame stage complete.
[2026-02-17 20:22:37] Recursive audit passed at node=frame_complete
[2026-02-17 20:22:41] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 20:22:41] Upload stage complete.
[2026-02-17 20:22:44] GCS counts linux1=484 windows1=263
[2026-02-17 20:22:44] Building v60 base matrix with relaxed physics gates...
[2026-02-17 20:22:44] Recursive audit passed at node=pre_base_matrix
[2026-02-17 20:22:44] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-122244_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-122244_aa8abb7/base_matrix.meta.json
[2026-02-17 20:22:44] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 20:22:44]   warnings.warn(
[2026-02-17 20:22:44] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 20:22:44]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 20:22:44] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 20:22:47] [+] Code bundle uploaded successfully.
[2026-02-17 20:22:47] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-202247
[2026-02-17 20:22:47] [*] Forcing gcloud fallback submission path.
[2026-02-17 20:22:51] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/2103423605734899712
[2026-02-17 20:22:52]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 20:23:23]     [Fallback] state=JOB_STATE_PENDING elapsed=32s
[2026-02-17 20:23:54]     [Fallback] state=JOB_STATE_PENDING elapsed=63s
[2026-02-17 20:24:25]     [Fallback] state=JOB_STATE_PENDING elapsed=94s
[2026-02-17 20:24:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=125s
[2026-02-17 20:25:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=156s
[2026-02-17 20:25:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=187s
[2026-02-17 20:26:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=218s
[2026-02-17 20:27:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=249s
[2026-02-17 20:27:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=280s
[2026-02-17 20:28:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=312s
[2026-02-17 20:28:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=343s
[2026-02-17 20:29:05]     [Fallback] state=JOB_STATE_RUNNING elapsed=374s
[2026-02-17 20:29:36]     [Fallback] state=JOB_STATE_RUNNING elapsed=405s
[2026-02-17 20:30:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=436s
[2026-02-17 20:30:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=467s
[2026-02-17 20:31:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=498s
[2026-02-17 20:31:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=529s
[2026-02-17 20:32:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=560s
[2026-02-17 20:32:43]     [Fallback] state=JOB_STATE_FAILED elapsed=591s
[2026-02-17 20:32:43] Traceback (most recent call last):
[2026-02-17 20:32:43]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 20:32:43]     submit_job(
[2026-02-17 20:32:43]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 20:32:43]     _submit_via_gcloud_fallback(
[2026-02-17 20:32:43]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 20:32:43]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 20:32:43] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/2103423605734899712
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 875, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 641, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-122244_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-122244_aa8abb7/base_matrix.meta.json

```

## Tail: autopilot log
```text
[2026-02-17 15:46:19] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
[2026-02-17 15:46:19]   warnings.warn(eol_message.format("3.9"), FutureWarning)
[2026-02-17 15:46:19] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 15:46:19]   warnings.warn(
[2026-02-17 15:46:19] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
[2026-02-17 15:46:19]   warnings.warn(eol_message.format("3.9"), FutureWarning)
[2026-02-17 20:02:37] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 20:02:37] Machine plan base=n2-highmem-16 opt=n2-highmem-16 train=n2-standard-16 backtest=n2-standard-8
[2026-02-17 20:02:37] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 20:02:37] Backtest month guard enabled: 2025,202601
[2026-02-17 20:02:37] Recursive audit passed at node=bootstrap
[2026-02-17 20:02:39] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 20:02:39] Frame stage complete.
[2026-02-17 20:02:39] Recursive audit passed at node=frame_complete
[2026-02-17 20:02:42] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 20:02:42] Upload stage complete.
[2026-02-17 20:02:45] GCS counts linux1=484 windows1=263
[2026-02-17 20:02:45] Building v60 base matrix with relaxed physics gates...
[2026-02-17 20:02:45] Recursive audit passed at node=pre_base_matrix
[2026-02-17 20:02:45] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-120245_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-120245_aa8abb7/base_matrix.meta.json
[2026-02-17 20:02:45] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 20:02:45]   warnings.warn(
[2026-02-17 20:02:46] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 20:02:46]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 20:02:46] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 20:02:48] [+] Code bundle uploaded successfully.
[2026-02-17 20:02:48] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-200248
[2026-02-17 20:02:48] [*] Forcing gcloud fallback submission path.
[2026-02-17 20:02:52] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/702804121622675456
[2026-02-17 20:02:53]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 20:03:24]     [Fallback] state=JOB_STATE_PENDING elapsed=32s
[2026-02-17 20:03:55]     [Fallback] state=JOB_STATE_PENDING elapsed=63s
[2026-02-17 20:04:26]     [Fallback] state=JOB_STATE_PENDING elapsed=94s
[2026-02-17 20:04:58]     [Fallback] state=JOB_STATE_PENDING elapsed=125s
[2026-02-17 20:05:29]     [Fallback] state=JOB_STATE_PENDING elapsed=156s
[2026-02-17 20:06:00]     [Fallback] state=JOB_STATE_PENDING elapsed=187s
[2026-02-17 20:06:31]     [Fallback] state=JOB_STATE_PENDING elapsed=218s
[2026-02-17 20:07:02]     [Fallback] state=JOB_STATE_PENDING elapsed=249s
[2026-02-17 20:07:34]     [Fallback] state=JOB_STATE_PENDING elapsed=281s
[2026-02-17 20:08:05]     [Fallback] state=JOB_STATE_PENDING elapsed=312s
[2026-02-17 20:08:36]     [Fallback] state=JOB_STATE_PENDING elapsed=343s
[2026-02-17 20:09:07]     [Fallback] state=JOB_STATE_PENDING elapsed=374s
[2026-02-17 20:09:38]     [Fallback] state=JOB_STATE_PENDING elapsed=406s
[2026-02-17 20:10:09]     [Fallback] state=JOB_STATE_PENDING elapsed=437s
[2026-02-17 20:10:40]     [Fallback] state=JOB_STATE_PENDING elapsed=468s
[2026-02-17 20:11:11]     [Fallback] state=JOB_STATE_PENDING elapsed=499s
[2026-02-17 20:11:43]     [Fallback] state=JOB_STATE_PENDING elapsed=530s
[2026-02-17 20:12:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=561s
[2026-02-17 20:12:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=592s
[2026-02-17 20:13:16]     [Fallback] state=JOB_STATE_RUNNING elapsed=623s
[2026-02-17 20:13:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=654s
[2026-02-17 20:14:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=685s
[2026-02-17 20:14:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=716s
[2026-02-17 20:15:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=748s
[2026-02-17 20:15:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=779s
[2026-02-17 20:16:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=810s
[2026-02-17 20:16:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=841s
[2026-02-17 20:17:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=872s
[2026-02-17 20:17:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=903s
[2026-02-17 20:18:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=934s
[2026-02-17 20:18:58]     [Fallback] state=JOB_STATE_FAILED elapsed=965s
[2026-02-17 20:18:58] Traceback (most recent call last):
[2026-02-17 20:18:58]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 20:18:58]     submit_job(
[2026-02-17 20:18:58]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 20:18:58]     _submit_via_gcloud_fallback(
[2026-02-17 20:18:58]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 20:18:58]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 20:18:58] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/702804121622675456
[2026-02-17 20:22:36] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 20:22:36] Machine plan base=n2-highmem-16 opt=n2-highmem-16 train=n2-standard-16 backtest=n2-standard-8
[2026-02-17 20:22:36] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 20:22:36] Backtest month guard enabled: 2025,202601
[2026-02-17 20:22:36] Recursive audit passed at node=bootstrap
[2026-02-17 20:22:37] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 20:22:37] Frame stage complete.
[2026-02-17 20:22:37] Recursive audit passed at node=frame_complete
[2026-02-17 20:22:41] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 20:22:41] Upload stage complete.
[2026-02-17 20:22:44] GCS counts linux1=484 windows1=263
[2026-02-17 20:22:44] Building v60 base matrix with relaxed physics gates...
[2026-02-17 20:22:44] Recursive audit passed at node=pre_base_matrix
[2026-02-17 20:22:44] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-122244_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-122244_aa8abb7/base_matrix.meta.json
[2026-02-17 20:22:44] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 20:22:44]   warnings.warn(
[2026-02-17 20:22:44] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 20:22:44]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 20:22:44] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 20:22:47] [+] Code bundle uploaded successfully.
[2026-02-17 20:22:47] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-202247
[2026-02-17 20:22:47] [*] Forcing gcloud fallback submission path.
[2026-02-17 20:22:51] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/2103423605734899712
[2026-02-17 20:22:52]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 20:23:23]     [Fallback] state=JOB_STATE_PENDING elapsed=32s
[2026-02-17 20:23:54]     [Fallback] state=JOB_STATE_PENDING elapsed=63s
[2026-02-17 20:24:25]     [Fallback] state=JOB_STATE_PENDING elapsed=94s
[2026-02-17 20:24:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=125s
[2026-02-17 20:25:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=156s
[2026-02-17 20:25:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=187s
[2026-02-17 20:26:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=218s
[2026-02-17 20:27:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=249s
[2026-02-17 20:27:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=280s
[2026-02-17 20:28:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=312s
[2026-02-17 20:28:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=343s
[2026-02-17 20:29:05]     [Fallback] state=JOB_STATE_RUNNING elapsed=374s
[2026-02-17 20:29:36]     [Fallback] state=JOB_STATE_RUNNING elapsed=405s
[2026-02-17 20:30:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=436s
[2026-02-17 20:30:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=467s
[2026-02-17 20:31:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=498s
[2026-02-17 20:31:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=529s
[2026-02-17 20:32:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=560s
[2026-02-17 20:32:43]     [Fallback] state=JOB_STATE_FAILED elapsed=591s
[2026-02-17 20:32:43] Traceback (most recent call last):
[2026-02-17 20:32:43]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 20:32:43]     submit_job(
[2026-02-17 20:32:43]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 20:32:43]     _submit_via_gcloud_fallback(
[2026-02-17 20:32:43]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 20:32:43]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 20:32:43] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/2103423605734899712

```

## Tail: uplink log
```text
[2026-02-17 19:49:28] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 19:49:29] windows1 sync rc=0
[2026-02-17 19:49:29] uplink cycle sleep 300s
[2026-02-17 19:54:29] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 19:54:31] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 19:54:33] windows1 sync rc=0
[2026-02-17 19:54:33] uplink cycle sleep 300s
[2026-02-17 19:59:33] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 19:59:35] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 19:59:37] windows1 sync rc=0
[2026-02-17 19:59:37] uplink cycle sleep 300s
[2026-02-17 20:04:37] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:04:39] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:04:41] windows1 sync rc=0
[2026-02-17 20:04:41] uplink cycle sleep 300s
[2026-02-17 20:09:41] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:09:43] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:09:45] windows1 sync rc=0
[2026-02-17 20:09:45] uplink cycle sleep 300s
[2026-02-17 20:14:45] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:14:47] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:14:49] windows1 sync rc=0
[2026-02-17 20:14:49] uplink cycle sleep 300s
[2026-02-17 20:19:49] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:19:51] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:19:53] windows1 sync rc=0
[2026-02-17 20:19:53] uplink cycle sleep 300s
[2026-02-17 20:24:53] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:24:55] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:24:57] windows1 sync rc=0
[2026-02-17 20:24:57] uplink cycle sleep 300s
[2026-02-17 20:29:57] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:29:59] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:30:01] windows1 sync rc=0
[2026-02-17 20:30:01] uplink cycle sleep 300s

```