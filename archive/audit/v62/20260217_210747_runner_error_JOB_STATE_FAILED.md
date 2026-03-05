# Incident 20260217_210747_runner_error_JOB_STATE_FAILED
- ts: 2026-02-17 21:07:47
- reason: runner_error_JOB_STATE_FAILED
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-17 20:48:41",
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
    "updated_at": "2026-02-17 20:48:42"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-17 20:48:53"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.meta.json",
    "base_matrix_exec_mode": "vertex",
    "base_matrix_machine_type": "n1-highmem-32",
    "base_matrix_spot": false
  },
  "train": {},
  "backtest": {},
  "run_id": "20260217-124853",
  "data_pattern": "gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet"
}
```

## screen -ls
```text
There is a screen on:
	28054.v60_ai_watchdog_aa8abb7	(Detached)
1 Socket in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh

```

## Tail: autopilot runner log
```text
[2026-02-17 20:35:06]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 20:35:06] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 20:35:09] [+] Code bundle uploaded successfully.
[2026-02-17 20:35:09] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-203509
[2026-02-17 20:35:09] [*] Forcing gcloud fallback submission path.
[2026-02-17 20:35:13] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/1968315616913784832
[2026-02-17 20:35:15]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 20:35:46]     [Fallback] state=JOB_STATE_PENDING elapsed=32s
[2026-02-17 20:36:18]     [Fallback] state=JOB_STATE_PENDING elapsed=64s
[2026-02-17 20:36:49]     [Fallback] state=JOB_STATE_PENDING elapsed=95s
[2026-02-17 20:37:21]     [Fallback] state=JOB_STATE_PENDING elapsed=127s
[2026-02-17 20:37:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=159s
[2026-02-17 20:38:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=190s
[2026-02-17 20:38:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=221s
[2026-02-17 20:39:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=261s
[2026-02-17 20:40:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=293s
[2026-02-17 20:40:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=324s
[2026-02-17 20:41:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=355s
[2026-02-17 20:41:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=387s
[2026-02-17 20:42:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=418s
[2026-02-17 20:42:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=449s
[2026-02-17 20:43:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=480s
[2026-02-17 20:43:45]     [Fallback] state=JOB_STATE_FAILED elapsed=511s
[2026-02-17 20:43:45] Traceback (most recent call last):
[2026-02-17 20:43:45]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 20:43:45]     submit_job(
[2026-02-17 20:43:45]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 20:43:45]     _submit_via_gcloud_fallback(
[2026-02-17 20:43:45]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 20:43:45]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 20:43:45] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/1968315616913784832
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 875, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 641, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-123505_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-123505_aa8abb7/base_matrix.meta.json
[MANUAL_NOHUP_RESTART_2026-02-17_20:47:55]
[2026-02-17 20:47:39] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 20:47:39] Machine plan base=n2-highmem-16 opt=n2-highmem-16 train=n2-standard-16 backtest=n2-standard-8
[2026-02-17 20:47:39] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 20:47:39] Backtest month guard enabled: 2025,202601
[2026-02-17 20:47:39] Recursive audit passed at node=bootstrap
[2026-02-17 20:47:39] Frame progress linux=-1/484 windows=-1/263 task=unknown probe_ok=False
[2026-02-17 20:48:41] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 20:48:41] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-17 20:48:41] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 20:48:41] Backtest month guard enabled: 2025,202601
[2026-02-17 20:48:41] Recursive audit passed at node=bootstrap
[2026-02-17 20:48:42] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 20:48:42] Frame stage complete.
[2026-02-17 20:48:42] Recursive audit passed at node=frame_complete
[2026-02-17 20:48:49] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 20:48:49] Upload stage complete.
[2026-02-17 20:48:53] GCS counts linux1=484 windows1=263
[2026-02-17 20:48:53] Building v60 base matrix with relaxed physics gates...
[2026-02-17 20:48:53] Recursive audit passed at node=pre_base_matrix
[2026-02-17 20:48:53] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.meta.json
[2026-02-17 20:48:53] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 20:48:53]   warnings.warn(
[2026-02-17 20:48:54] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 20:48:54]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 20:48:54] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 20:48:58] [+] Code bundle uploaded successfully.
[2026-02-17 20:48:58] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-204858
[2026-02-17 20:48:58] [*] Forcing gcloud fallback submission path.
[2026-02-17 20:49:03] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/5958504886764044288
[2026-02-17 20:49:05]     [Fallback] state=JOB_STATE_QUEUED elapsed=2s
[2026-02-17 20:49:36]     [Fallback] state=JOB_STATE_PENDING elapsed=33s
[2026-02-17 20:50:08]     [Fallback] state=JOB_STATE_PENDING elapsed=64s
[2026-02-17 20:50:39]     [Fallback] state=JOB_STATE_PENDING elapsed=96s
[2026-02-17 20:51:11]     [Fallback] state=JOB_STATE_PENDING elapsed=128s
[2026-02-17 20:51:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=160s
[2026-02-17 20:52:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=192s
[2026-02-17 20:52:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=227s
[2026-02-17 20:53:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=260s
[2026-02-17 20:53:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=291s
[2026-02-17 20:54:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=323s
[2026-02-17 20:54:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=355s
[2026-02-17 20:55:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=388s
[2026-02-17 20:56:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=419s
[2026-02-17 20:56:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=451s
[2026-02-17 20:57:05]     [Fallback] state=JOB_STATE_RUNNING elapsed=482s
[2026-02-17 20:57:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=514s
[2026-02-17 20:58:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=545s
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
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 875, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 641, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.meta.json

```

## Tail: autopilot log
```text
[2026-02-17 20:34:56] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 20:34:56] Machine plan base=n2-highmem-16 opt=n2-highmem-16 train=n2-standard-16 backtest=n2-standard-8
[2026-02-17 20:34:56] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 20:34:56] Backtest month guard enabled: 2025,202601
[2026-02-17 20:34:56] Recursive audit passed at node=bootstrap
[2026-02-17 20:34:57] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 20:34:57] Frame stage complete.
[2026-02-17 20:34:57] Recursive audit passed at node=frame_complete
[2026-02-17 20:35:01] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 20:35:01] Upload stage complete.
[2026-02-17 20:35:05] GCS counts linux1=484 windows1=263
[2026-02-17 20:35:05] Building v60 base matrix with relaxed physics gates...
[2026-02-17 20:35:05] Recursive audit passed at node=pre_base_matrix
[2026-02-17 20:35:05] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-123505_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-123505_aa8abb7/base_matrix.meta.json
[2026-02-17 20:35:05] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 20:35:05]   warnings.warn(
[2026-02-17 20:35:06] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 20:35:06]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 20:35:06] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 20:35:09] [+] Code bundle uploaded successfully.
[2026-02-17 20:35:09] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-203509
[2026-02-17 20:35:09] [*] Forcing gcloud fallback submission path.
[2026-02-17 20:35:13] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/1968315616913784832
[2026-02-17 20:35:15]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-17 20:35:46]     [Fallback] state=JOB_STATE_PENDING elapsed=32s
[2026-02-17 20:36:18]     [Fallback] state=JOB_STATE_PENDING elapsed=64s
[2026-02-17 20:36:49]     [Fallback] state=JOB_STATE_PENDING elapsed=95s
[2026-02-17 20:37:21]     [Fallback] state=JOB_STATE_PENDING elapsed=127s
[2026-02-17 20:37:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=159s
[2026-02-17 20:38:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=190s
[2026-02-17 20:38:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=221s
[2026-02-17 20:39:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=261s
[2026-02-17 20:40:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=293s
[2026-02-17 20:40:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=324s
[2026-02-17 20:41:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=355s
[2026-02-17 20:41:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=387s
[2026-02-17 20:42:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=418s
[2026-02-17 20:42:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=449s
[2026-02-17 20:43:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=480s
[2026-02-17 20:43:45]     [Fallback] state=JOB_STATE_FAILED elapsed=511s
[2026-02-17 20:43:45] Traceback (most recent call last):
[2026-02-17 20:43:45]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-17 20:43:45]     submit_job(
[2026-02-17 20:43:45]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-17 20:43:45]     _submit_via_gcloud_fallback(
[2026-02-17 20:43:45]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 230, in _submit_via_gcloud_fallback
[2026-02-17 20:43:45]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-17 20:43:45] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-west1/customJobs/1968315616913784832
[2026-02-17 20:47:39] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 20:47:39] Machine plan base=n2-highmem-16 opt=n2-highmem-16 train=n2-standard-16 backtest=n2-standard-8
[2026-02-17 20:47:39] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 20:47:39] Backtest month guard enabled: 2025,202601
[2026-02-17 20:47:39] Recursive audit passed at node=bootstrap
[2026-02-17 20:47:39] Frame progress linux=-1/484 windows=-1/263 task=unknown probe_ok=False
[2026-02-17 20:48:41] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 20:48:41] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-17 20:48:41] Spot plan base=False opt=False train=False backtest=False
[2026-02-17 20:48:41] Backtest month guard enabled: 2025,202601
[2026-02-17 20:48:41] Recursive audit passed at node=bootstrap
[2026-02-17 20:48:42] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 20:48:42] Frame stage complete.
[2026-02-17 20:48:42] Recursive audit passed at node=frame_complete
[2026-02-17 20:48:49] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 20:48:49] Upload stage complete.
[2026-02-17 20:48:53] GCS counts linux1=484 windows1=263
[2026-02-17 20:48:53] Building v60 base matrix with relaxed physics gates...
[2026-02-17 20:48:53] Recursive audit passed at node=pre_base_matrix
[2026-02-17 20:48:53] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-124853_aa8abb7/base_matrix.meta.json
[2026-02-17 20:48:53] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 20:48:53]   warnings.warn(
[2026-02-17 20:48:54] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-17 20:48:54]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-17 20:48:54] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-17 20:48:58] [+] Code bundle uploaded successfully.
[2026-02-17 20:48:58] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260217-204858
[2026-02-17 20:48:58] [*] Forcing gcloud fallback submission path.
[2026-02-17 20:49:03] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/5958504886764044288
[2026-02-17 20:49:05]     [Fallback] state=JOB_STATE_QUEUED elapsed=2s
[2026-02-17 20:49:36]     [Fallback] state=JOB_STATE_PENDING elapsed=33s
[2026-02-17 20:50:08]     [Fallback] state=JOB_STATE_PENDING elapsed=64s
[2026-02-17 20:50:39]     [Fallback] state=JOB_STATE_PENDING elapsed=96s
[2026-02-17 20:51:11]     [Fallback] state=JOB_STATE_PENDING elapsed=128s
[2026-02-17 20:51:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=160s
[2026-02-17 20:52:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=192s
[2026-02-17 20:52:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=227s
[2026-02-17 20:53:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=260s
[2026-02-17 20:53:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=291s
[2026-02-17 20:54:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=323s
[2026-02-17 20:54:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=355s
[2026-02-17 20:55:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=388s
[2026-02-17 20:56:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=419s
[2026-02-17 20:56:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=451s
[2026-02-17 20:57:05]     [Fallback] state=JOB_STATE_RUNNING elapsed=482s
[2026-02-17 20:57:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=514s
[2026-02-17 20:58:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=545s
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

```

## Tail: uplink log
```text
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
[2026-02-17 20:35:01] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:35:03] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:35:06] windows1 sync rc=0
[2026-02-17 20:35:06] uplink cycle sleep 300s
[2026-02-17 20:40:06] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:40:08] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:40:10] windows1 sync rc=0
[2026-02-17 20:40:10] uplink cycle sleep 300s
[2026-02-17 20:45:10] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:45:13] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:45:15] windows1 sync rc=0
[2026-02-17 20:45:15] uplink cycle sleep 300s
[2026-02-17 20:50:15] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:50:19] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:50:21] windows1 sync rc=0
[2026-02-17 20:50:21] uplink cycle sleep 300s
[2026-02-17 20:55:21] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 20:55:23] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 20:55:25] windows1 sync rc=0
[2026-02-17 20:55:25] uplink cycle sleep 300s
[2026-02-17 21:00:25] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
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

```