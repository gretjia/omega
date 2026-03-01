# Incident 20260218_102128_runner_error_Traceback
- ts: 2026-02-18 10:21:28
- reason: runner_error_Traceback
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-18 10:17:17",
  "git_hash": "aa8abb7",
  "bucket": "gs://omega_v52_central/omega",
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
    "updated_at": "2026-02-18 10:17:18"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-18 10:17:25"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-021725_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-021725_aa8abb7/base_matrix.meta.json",
    "base_matrix_exec_mode": "vertex",
    "base_matrix_machine_type": "e2-highmem-16",
    "base_matrix_spot": false
  },
  "train": {},
  "backtest": {},
  "run_id": "20260218-021725",
  "data_pattern": "gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet"
}
```

## screen -ls
```text
There is a screen on:
	20178.v60_autopilot_aa8abb7	(Detached)
1 Socket in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
20178 SCREEN -dmS v60_autopilot_aa8abb7 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
20180 login -pflq zephryj /bin/bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
20183 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
20186 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh

```

## Tail: autopilot runner log
```text
[2026-02-18 09:26:36]     [Fallback] state=JOB_STATE_RUNNING elapsed=187s
[2026-02-18 09:27:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=218s
[2026-02-18 09:27:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=249s
[2026-02-18 09:28:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=280s
[2026-02-18 09:28:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=312s
[2026-02-18 09:29:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=343s
[2026-02-18 09:29:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=374s
[2026-02-18 09:30:14]     [Fallback] state=JOB_STATE_FAILED elapsed=405s
[2026-02-18 09:30:14] Traceback (most recent call last):
[2026-02-18 09:30:14]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 441, in <module>
[2026-02-18 09:30:14]     submit_job(
[2026-02-18 09:30:14]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 331, in submit_job
[2026-02-18 09:30:14]     _submit_via_gcloud_fallback(
[2026-02-18 09:30:14]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 292, in _submit_via_gcloud_fallback
[2026-02-18 09:30:14]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-18 09:30:14] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-central1/customJobs/3856285710118027264
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 899, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 661, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type e2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-012321_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-012321_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 09:44:45] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-18 09:44:45] Machine plan base=e2-highmem-16 opt=c2-standard-30 train=c2-standard-30 backtest=c2-standard-30
[2026-02-18 09:44:45] Spot plan base=False opt=False train=False backtest=False
[2026-02-18 09:44:45] Data caps base(chunk_days=5, max_rows_per_file=0) train(max_files=0, max_rows_per_file=0) backtest(max_files=0, max_rows_per_file=0)
[2026-02-18 09:44:45] Backtest month guard enabled: 2025,202601
[2026-02-18 09:44:45] Recursive audit passed at node=bootstrap
[2026-02-18 09:44:47] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-18 09:44:47] Frame stage complete.
[2026-02-18 09:44:47] Recursive audit passed at node=frame_complete
[2026-02-18 09:44:50] GCS progress linux1=484/484 windows1=263/263
[2026-02-18 09:44:50] Upload stage complete.
[2026-02-18 09:44:54] GCS counts linux1=484 windows1=263
[2026-02-18 09:44:54] Building v60 base matrix with relaxed physics gates...
[2026-02-18 09:44:54] Recursive audit passed at node=pre_base_matrix
[2026-02-18 09:44:54] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type e2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-014454_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-014454_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 09:44:54] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-18 09:44:54]   warnings.warn(
[2026-02-18 09:44:54] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-18 09:44:54]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-18 09:44:54] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-18 09:44:57] [+] Code bundle uploaded successfully.
[2026-02-18 09:44:57] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260218-094457
[2026-02-18 09:44:57] [*] Forcing gcloud fallback submission path.
[2026-02-18 09:45:00] [+] Fallback submit succeeded: projects/269018079180/locations/us-central1/customJobs/8566206495417434112
[2026-02-18 09:45:02]     [Fallback] state=JOB_STATE_QUEUED elapsed=0s
[2026-02-18 09:45:37]     [Fallback] state=JOB_STATE_PENDING elapsed=31s
[2026-02-18 09:46:08]     [Fallback] state=JOB_STATE_PENDING elapsed=66s
[2026-02-18 09:46:40]     [Fallback] state=JOB_STATE_PENDING elapsed=98s
[2026-02-18 09:47:11]     [Fallback] state=JOB_STATE_PENDING elapsed=129s
[2026-02-18 09:47:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=160s
[2026-02-18 09:48:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=191s
[2026-02-18 09:48:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=223s
[2026-02-18 09:49:16]     [Fallback] state=JOB_STATE_RUNNING elapsed=254s
[2026-02-18 09:49:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=285s
[2026-02-18 09:50:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=316s
[2026-02-18 09:50:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=348s
[2026-02-18 09:51:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=379s
[2026-02-18 09:51:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=410s
[2026-02-18 09:52:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=441s
[2026-02-18 09:52:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=473s
[2026-02-18 09:53:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=504s
[2026-02-18 09:53:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=535s
[2026-02-18 09:54:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=567s
[2026-02-18 09:55:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=598s
[2026-02-18 09:55:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=629s
[2026-02-18 09:56:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=661s
[2026-02-18 09:56:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=692s
[2026-02-18 09:57:06]     [Fallback] state=JOB_STATE_FAILED elapsed=724s
[2026-02-18 09:57:06] Traceback (most recent call last):
[2026-02-18 09:57:06]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 440, in <module>
[2026-02-18 09:57:06]     submit_job(
[2026-02-18 09:57:06]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 330, in submit_job
[2026-02-18 09:57:06]     _submit_via_gcloud_fallback(
[2026-02-18 09:57:06]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 291, in _submit_via_gcloud_fallback
[2026-02-18 09:57:06]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-18 09:57:06] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-central1/customJobs/8566206495417434112
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 899, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 661, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type e2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-014454_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-014454_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 10:17:17] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-18 10:17:17] Machine plan base=e2-highmem-16 opt=c2-standard-30 train=c2-standard-30 backtest=c2-standard-30
[2026-02-18 10:17:17] Spot plan base=False opt=False train=False backtest=False
[2026-02-18 10:17:17] Data caps base(chunk_days=5, max_rows_per_file=0) train(max_files=0, max_rows_per_file=0) backtest(max_files=0, max_rows_per_file=0)
[2026-02-18 10:17:17] Backtest month guard enabled: 2025,202601
[2026-02-18 10:17:17] Recursive audit passed at node=bootstrap
[2026-02-18 10:17:18] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-18 10:17:18] Frame stage complete.
[2026-02-18 10:17:19] Recursive audit passed at node=frame_complete
[2026-02-18 10:17:22] GCS progress linux1=484/484 windows1=263/263
[2026-02-18 10:17:22] Upload stage complete.
[2026-02-18 10:17:25] GCS counts linux1=484 windows1=263
[2026-02-18 10:17:25] Building v60 base matrix with relaxed physics gates...
[2026-02-18 10:17:25] Recursive audit passed at node=pre_base_matrix
[2026-02-18 10:17:25] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type e2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-021725_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-021725_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 10:17:25] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-18 10:17:25]   warnings.warn(
[2026-02-18 10:17:26] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-18 10:17:26]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-18 10:17:26] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-18 10:17:29] [+] Code bundle uploaded successfully.
[2026-02-18 10:17:29] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260218-101729
[2026-02-18 10:17:29] [*] Forcing gcloud fallback submission path.
[2026-02-18 10:17:32] [+] Fallback submit succeeded: projects/269018079180/locations/us-central1/customJobs/2052312584379432960
[2026-02-18 10:17:33]     [Fallback] state=JOB_STATE_PENDING elapsed=0s
[2026-02-18 10:18:05]     [Fallback] state=JOB_STATE_PENDING elapsed=31s
[2026-02-18 10:18:36]     [Fallback] state=JOB_STATE_PENDING elapsed=62s
[2026-02-18 10:19:07]     [Fallback] state=JOB_STATE_PENDING elapsed=93s
[2026-02-18 10:19:38]     [Fallback] state=JOB_STATE_PENDING elapsed=124s
[2026-02-18 10:20:09]     [Fallback] state=JOB_STATE_PENDING elapsed=156s
[2026-02-18 10:20:41]     [Fallback] state=JOB_STATE_PENDING elapsed=187s
[2026-02-18 10:21:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=218s

```

## Tail: autopilot log
```text
[2026-02-18 09:23:21] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type e2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-012321_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-012321_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 09:23:21] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-18 09:23:21]   warnings.warn(
[2026-02-18 09:23:21] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-18 09:23:21]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-18 09:23:21] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-18 09:23:24] [+] Code bundle uploaded successfully.
[2026-02-18 09:23:24] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260218-092324
[2026-02-18 09:23:24] [*] Forcing gcloud fallback submission path.
[2026-02-18 09:23:27] [+] Fallback submit succeeded: projects/269018079180/locations/us-central1/customJobs/3856285710118027264
[2026-02-18 09:23:28]     [Fallback] state=JOB_STATE_QUEUED elapsed=0s
[2026-02-18 09:24:00]     [Fallback] state=JOB_STATE_PENDING elapsed=31s
[2026-02-18 09:24:31]     [Fallback] state=JOB_STATE_PENDING elapsed=62s
[2026-02-18 09:25:02]     [Fallback] state=JOB_STATE_PENDING elapsed=93s
[2026-02-18 09:25:33]     [Fallback] state=JOB_STATE_PENDING elapsed=124s
[2026-02-18 09:26:05]     [Fallback] state=JOB_STATE_PENDING elapsed=156s
[2026-02-18 09:26:36]     [Fallback] state=JOB_STATE_RUNNING elapsed=187s
[2026-02-18 09:27:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=218s
[2026-02-18 09:27:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=249s
[2026-02-18 09:28:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=280s
[2026-02-18 09:28:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=312s
[2026-02-18 09:29:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=343s
[2026-02-18 09:29:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=374s
[2026-02-18 09:30:14]     [Fallback] state=JOB_STATE_FAILED elapsed=405s
[2026-02-18 09:30:14] Traceback (most recent call last):
[2026-02-18 09:30:14]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 441, in <module>
[2026-02-18 09:30:14]     submit_job(
[2026-02-18 09:30:14]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 331, in submit_job
[2026-02-18 09:30:14]     _submit_via_gcloud_fallback(
[2026-02-18 09:30:14]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 292, in _submit_via_gcloud_fallback
[2026-02-18 09:30:14]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-18 09:30:14] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-central1/customJobs/3856285710118027264
[2026-02-18 09:44:45] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-18 09:44:45] Machine plan base=e2-highmem-16 opt=c2-standard-30 train=c2-standard-30 backtest=c2-standard-30
[2026-02-18 09:44:45] Spot plan base=False opt=False train=False backtest=False
[2026-02-18 09:44:45] Data caps base(chunk_days=5, max_rows_per_file=0) train(max_files=0, max_rows_per_file=0) backtest(max_files=0, max_rows_per_file=0)
[2026-02-18 09:44:45] Backtest month guard enabled: 2025,202601
[2026-02-18 09:44:45] Recursive audit passed at node=bootstrap
[2026-02-18 09:44:47] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-18 09:44:47] Frame stage complete.
[2026-02-18 09:44:47] Recursive audit passed at node=frame_complete
[2026-02-18 09:44:50] GCS progress linux1=484/484 windows1=263/263
[2026-02-18 09:44:50] Upload stage complete.
[2026-02-18 09:44:54] GCS counts linux1=484 windows1=263
[2026-02-18 09:44:54] Building v60 base matrix with relaxed physics gates...
[2026-02-18 09:44:54] Recursive audit passed at node=pre_base_matrix
[2026-02-18 09:44:54] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type e2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-014454_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-014454_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 09:44:54] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-18 09:44:54]   warnings.warn(
[2026-02-18 09:44:54] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-18 09:44:54]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-18 09:44:54] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-18 09:44:57] [+] Code bundle uploaded successfully.
[2026-02-18 09:44:57] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260218-094457
[2026-02-18 09:44:57] [*] Forcing gcloud fallback submission path.
[2026-02-18 09:45:00] [+] Fallback submit succeeded: projects/269018079180/locations/us-central1/customJobs/8566206495417434112
[2026-02-18 09:45:02]     [Fallback] state=JOB_STATE_QUEUED elapsed=0s
[2026-02-18 09:45:37]     [Fallback] state=JOB_STATE_PENDING elapsed=31s
[2026-02-18 09:46:08]     [Fallback] state=JOB_STATE_PENDING elapsed=66s
[2026-02-18 09:46:40]     [Fallback] state=JOB_STATE_PENDING elapsed=98s
[2026-02-18 09:47:11]     [Fallback] state=JOB_STATE_PENDING elapsed=129s
[2026-02-18 09:47:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=160s
[2026-02-18 09:48:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=191s
[2026-02-18 09:48:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=223s
[2026-02-18 09:49:16]     [Fallback] state=JOB_STATE_RUNNING elapsed=254s
[2026-02-18 09:49:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=285s
[2026-02-18 09:50:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=316s
[2026-02-18 09:50:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=348s
[2026-02-18 09:51:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=379s
[2026-02-18 09:51:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=410s
[2026-02-18 09:52:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=441s
[2026-02-18 09:52:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=473s
[2026-02-18 09:53:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=504s
[2026-02-18 09:53:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=535s
[2026-02-18 09:54:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=567s
[2026-02-18 09:55:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=598s
[2026-02-18 09:55:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=629s
[2026-02-18 09:56:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=661s
[2026-02-18 09:56:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=692s
[2026-02-18 09:57:06]     [Fallback] state=JOB_STATE_FAILED elapsed=724s
[2026-02-18 09:57:06] Traceback (most recent call last):
[2026-02-18 09:57:06]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 440, in <module>
[2026-02-18 09:57:06]     submit_job(
[2026-02-18 09:57:06]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 330, in submit_job
[2026-02-18 09:57:06]     _submit_via_gcloud_fallback(
[2026-02-18 09:57:06]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 291, in _submit_via_gcloud_fallback
[2026-02-18 09:57:06]     raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
[2026-02-18 09:57:06] RuntimeError: Fallback custom job failed with state=JOB_STATE_FAILED resource=projects/269018079180/locations/us-central1/customJobs/8566206495417434112
[2026-02-18 10:17:17] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-18 10:17:17] Machine plan base=e2-highmem-16 opt=c2-standard-30 train=c2-standard-30 backtest=c2-standard-30
[2026-02-18 10:17:17] Spot plan base=False opt=False train=False backtest=False
[2026-02-18 10:17:17] Data caps base(chunk_days=5, max_rows_per_file=0) train(max_files=0, max_rows_per_file=0) backtest(max_files=0, max_rows_per_file=0)
[2026-02-18 10:17:17] Backtest month guard enabled: 2025,202601
[2026-02-18 10:17:17] Recursive audit passed at node=bootstrap
[2026-02-18 10:17:18] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-18 10:17:18] Frame stage complete.
[2026-02-18 10:17:19] Recursive audit passed at node=frame_complete
[2026-02-18 10:17:22] GCS progress linux1=484/484 windows1=263/263
[2026-02-18 10:17:22] Upload stage complete.
[2026-02-18 10:17:25] GCS counts linux1=484 windows1=263
[2026-02-18 10:17:25] Building v60 base matrix with relaxed physics gates...
[2026-02-18 10:17:25] Recursive audit passed at node=pre_base_matrix
[2026-02-18 10:17:25] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type e2-highmem-16 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-021725_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/20260218-021725_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 10:17:25] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-18 10:17:25]   warnings.warn(
[2026-02-18 10:17:26] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-18 10:17:26]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-18 10:17:26] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-18 10:17:29] [+] Code bundle uploaded successfully.
[2026-02-18 10:17:29] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260218-101729
[2026-02-18 10:17:29] [*] Forcing gcloud fallback submission path.
[2026-02-18 10:17:32] [+] Fallback submit succeeded: projects/269018079180/locations/us-central1/customJobs/2052312584379432960
[2026-02-18 10:17:33]     [Fallback] state=JOB_STATE_PENDING elapsed=0s
[2026-02-18 10:18:05]     [Fallback] state=JOB_STATE_PENDING elapsed=31s
[2026-02-18 10:18:36]     [Fallback] state=JOB_STATE_PENDING elapsed=62s
[2026-02-18 10:19:07]     [Fallback] state=JOB_STATE_PENDING elapsed=93s
[2026-02-18 10:19:38]     [Fallback] state=JOB_STATE_PENDING elapsed=124s
[2026-02-18 10:20:09]     [Fallback] state=JOB_STATE_PENDING elapsed=156s
[2026-02-18 10:20:41]     [Fallback] state=JOB_STATE_PENDING elapsed=187s
[2026-02-18 10:21:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=218s

```

## Tail: uplink log
```text
[2026-02-18 09:40:30] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 09:40:32] windows1 sync rc=0
[2026-02-18 09:40:32] uplink cycle sleep 300s
[2026-02-18 09:45:32] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 09:45:37] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 09:45:39] windows1 sync rc=0
[2026-02-18 09:45:39] uplink cycle sleep 300s
[2026-02-18 09:50:39] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 09:50:41] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 09:50:43] windows1 sync rc=0
[2026-02-18 09:50:43] uplink cycle sleep 300s
[2026-02-18 09:55:43] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 09:55:45] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 09:55:47] windows1 sync rc=0
[2026-02-18 09:55:47] uplink cycle sleep 300s
[2026-02-18 10:00:47] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 10:00:49] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 10:00:51] windows1 sync rc=0
[2026-02-18 10:00:51] uplink cycle sleep 300s
[2026-02-18 10:05:51] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 10:05:53] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 10:05:55] windows1 sync rc=0
[2026-02-18 10:05:55] uplink cycle sleep 300s
[2026-02-18 10:10:55] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 10:10:57] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 10:10:59] windows1 sync rc=0
[2026-02-18 10:10:59] uplink cycle sleep 300s
[2026-02-18 10:15:59] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 10:16:09] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 10:16:11] windows1 sync rc=0
[2026-02-18 10:16:11] uplink cycle sleep 300s
[2026-02-18 10:21:11] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 10:21:13] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 10:21:15] windows1 sync rc=0
[2026-02-18 10:21:15] uplink cycle sleep 300s

```