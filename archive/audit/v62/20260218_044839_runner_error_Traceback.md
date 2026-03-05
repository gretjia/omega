# Incident 20260218_044839_runner_error_Traceback
- ts: 2026-02-18 04:48:39
- reason: runner_error_Traceback
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-18 04:15:47",
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
    "updated_at": "2026-02-18 04:15:49"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-18 04:15:55"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-201555_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-201555_aa8abb7/base_matrix.meta.json",
    "base_matrix_exec_mode": "vertex",
    "base_matrix_machine_type": "n1-highmem-32",
    "base_matrix_spot": false
  },
  "train": {},
  "backtest": {},
  "run_id": "20260217-201555",
  "data_pattern": "gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet"
}
```

## screen -ls
```text
No Sockets found in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh

```

## Tail: autopilot runner log
```text
[2026-02-18 03:51:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=20987s
[2026-02-18 03:52:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=21019s
[2026-02-18 03:52:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=21050s
[2026-02-18 03:53:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=21081s
[2026-02-18 03:53:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=21112s
[2026-02-18 03:54:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=21143s
[2026-02-18 03:54:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=21174s
[2026-02-18 03:55:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=21205s
[2026-02-18 03:55:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=21236s
[2026-02-18 03:56:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=21267s
[2026-02-18 03:56:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=21299s
[2026-02-18 03:57:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=21330s
[2026-02-18 03:57:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=21361s
[2026-02-18 03:58:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=21392s
[2026-02-18 03:58:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=21423s
[2026-02-18 03:59:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=21454s
[2026-02-18 03:59:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=21485s
[2026-02-18 04:00:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=21516s
[2026-02-18 04:00:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=21548s
[2026-02-18 04:01:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=21579s
[2026-02-18 04:02:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=21610s
[2026-02-18 04:02:01] Traceback (most recent call last):
[2026-02-18 04:02:01]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-18 04:02:01]     submit_job(
[2026-02-18 04:02:01]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-18 04:02:01]     _submit_via_gcloud_fallback(
[2026-02-18 04:02:01]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 245, in _submit_via_gcloud_fallback
[2026-02-18 04:02:01]     raise RuntimeError(
[2026-02-18 04:02:01] RuntimeError: Fallback custom job timed out after 21610s (timeout=21600s), resource=projects/269018079180/locations/us-west1/customJobs/2730549853846241280, last_state=JOB_STATE_RUNNING
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 899, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 661, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-140142_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-140142_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 04:07:32] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-18 04:07:32] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-18 04:07:32] Spot plan base=False opt=False train=False backtest=False
[2026-02-18 04:07:32] Data caps base(chunk_days=5, max_rows_per_file=0) train(max_files=0, max_rows_per_file=0) backtest(max_files=0, max_rows_per_file=0)
[2026-02-18 04:07:32] Backtest month guard enabled: 2025,202601
[2026-02-18 04:07:32] Recursive audit passed at node=bootstrap
[2026-02-18 04:07:32] Frame progress linux=-1/484 windows=-1/263 task=unknown probe_ok=False
[2026-02-18 04:15:47] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-18 04:15:47] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-18 04:15:47] Spot plan base=False opt=False train=False backtest=False
[2026-02-18 04:15:47] Data caps base(chunk_days=5, max_rows_per_file=0) train(max_files=0, max_rows_per_file=0) backtest(max_files=0, max_rows_per_file=0)
[2026-02-18 04:15:47] Backtest month guard enabled: 2025,202601
[2026-02-18 04:15:47] Recursive audit passed at node=bootstrap
[2026-02-18 04:15:49] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-18 04:15:49] Frame stage complete.
[2026-02-18 04:15:49] Recursive audit passed at node=frame_complete
[2026-02-18 04:15:52] GCS progress linux1=484/484 windows1=263/263
[2026-02-18 04:15:52] Upload stage complete.
[2026-02-18 04:15:55] GCS counts linux1=484 windows1=263
[2026-02-18 04:15:55] Building v60 base matrix with relaxed physics gates...
[2026-02-18 04:15:55] Recursive audit passed at node=pre_base_matrix
[2026-02-18 04:15:55] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-201555_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-201555_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 04:15:56] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-18 04:15:56]   warnings.warn(
[2026-02-18 04:15:56] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-18 04:15:56]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-18 04:15:56] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-18 04:15:59] [+] Code bundle uploaded successfully.
[2026-02-18 04:15:59] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260218-041559
[2026-02-18 04:15:59] [*] Forcing gcloud fallback submission path.
[2026-02-18 04:16:03] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/568540557731692544
[2026-02-18 04:16:04]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-18 04:16:35]     [Fallback] state=JOB_STATE_PENDING elapsed=32s
[2026-02-18 04:17:06]     [Fallback] state=JOB_STATE_PENDING elapsed=63s
[2026-02-18 04:17:37]     [Fallback] state=JOB_STATE_PENDING elapsed=94s
[2026-02-18 04:18:08]     [Fallback] state=JOB_STATE_PENDING elapsed=125s
[2026-02-18 04:18:40]     [Fallback] state=JOB_STATE_PENDING elapsed=156s
[2026-02-18 04:19:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=187s
[2026-02-18 04:19:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=218s
[2026-02-18 04:20:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=250s
[2026-02-18 04:20:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=281s
[2026-02-18 04:21:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=312s
[2026-02-18 04:21:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=343s
[2026-02-18 04:22:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=374s
[2026-02-18 04:22:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=405s
[2026-02-18 04:23:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=436s
[2026-02-18 04:23:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=467s
[2026-02-18 04:24:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=499s
[2026-02-18 04:24:54]     [Fallback] state=JOB_STATE_RUNNING elapsed=530s
[2026-02-18 04:25:25]     [Fallback] state=JOB_STATE_RUNNING elapsed=561s
[2026-02-18 04:25:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=592s
[2026-02-18 04:26:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=624s
[2026-02-18 04:26:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=655s
[2026-02-18 04:37:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=1295s
[2026-02-18 04:38:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=1327s
[2026-02-18 04:38:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=1358s
[2026-02-18 04:39:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=1389s
[2026-02-18 04:39:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=1420s
[2026-02-18 04:40:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=1451s
[2026-02-18 04:40:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=1482s
[2026-02-18 04:41:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=1513s
[2026-02-18 04:41:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=1544s
[2026-02-18 04:42:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=1575s
[2026-02-18 04:42:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=1607s
[2026-02-18 04:43:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=1638s
[2026-02-18 04:45:41] Traceback (most recent call last):
[2026-02-18 04:45:41]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-18 04:45:41]     submit_job(
[2026-02-18 04:45:41]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-18 04:45:41]     _submit_via_gcloud_fallback(
[2026-02-18 04:45:41]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 223, in _submit_via_gcloud_fallback
[2026-02-18 04:45:41]     sres = subprocess.run(state_cmd, capture_output=True, text=True, check=True)
[2026-02-18 04:45:41]   File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/subprocess.py", line 528, in run
[2026-02-18 04:45:41]     raise CalledProcessError(retcode, process.args,
[2026-02-18 04:45:41] subprocess.CalledProcessError: Command '['gcloud', 'ai', 'custom-jobs', 'describe', 'projects/269018079180/locations/us-west1/customJobs/568540557731692544', '--project=gen-lang-client-0250995579', '--region=us-west1', '--format=value(state)']' returned non-zero exit status 1.
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 899, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 661, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-201555_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-201555_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5

```

## Tail: autopilot log
```text
[2026-02-18 03:43:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=20490s
[2026-02-18 03:43:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=20521s
[2026-02-18 03:44:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=20552s
[2026-02-18 03:44:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=20583s
[2026-02-18 03:45:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=20614s
[2026-02-18 03:45:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=20645s
[2026-02-18 03:46:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=20676s
[2026-02-18 03:46:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=20708s
[2026-02-18 03:47:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=20739s
[2026-02-18 03:48:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=20770s
[2026-02-18 03:48:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=20801s
[2026-02-18 03:49:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=20832s
[2026-02-18 03:49:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=20863s
[2026-02-18 03:50:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=20894s
[2026-02-18 03:50:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=20925s
[2026-02-18 03:51:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=20956s
[2026-02-18 03:51:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=20987s
[2026-02-18 03:52:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=21019s
[2026-02-18 03:52:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=21050s
[2026-02-18 03:53:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=21081s
[2026-02-18 03:53:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=21112s
[2026-02-18 03:54:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=21143s
[2026-02-18 03:54:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=21174s
[2026-02-18 03:55:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=21205s
[2026-02-18 03:55:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=21236s
[2026-02-18 03:56:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=21267s
[2026-02-18 03:56:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=21299s
[2026-02-18 03:57:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=21330s
[2026-02-18 03:57:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=21361s
[2026-02-18 03:58:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=21392s
[2026-02-18 03:58:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=21423s
[2026-02-18 03:59:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=21454s
[2026-02-18 03:59:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=21485s
[2026-02-18 04:00:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=21516s
[2026-02-18 04:00:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=21548s
[2026-02-18 04:01:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=21579s
[2026-02-18 04:02:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=21610s
[2026-02-18 04:02:01] Traceback (most recent call last):
[2026-02-18 04:02:01]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-18 04:02:01]     submit_job(
[2026-02-18 04:02:01]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-18 04:02:01]     _submit_via_gcloud_fallback(
[2026-02-18 04:02:01]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 245, in _submit_via_gcloud_fallback
[2026-02-18 04:02:01]     raise RuntimeError(
[2026-02-18 04:02:01] RuntimeError: Fallback custom job timed out after 21610s (timeout=21600s), resource=projects/269018079180/locations/us-west1/customJobs/2730549853846241280, last_state=JOB_STATE_RUNNING
[2026-02-18 04:07:32] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-18 04:07:32] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-18 04:07:32] Spot plan base=False opt=False train=False backtest=False
[2026-02-18 04:07:32] Data caps base(chunk_days=5, max_rows_per_file=0) train(max_files=0, max_rows_per_file=0) backtest(max_files=0, max_rows_per_file=0)
[2026-02-18 04:07:32] Backtest month guard enabled: 2025,202601
[2026-02-18 04:07:32] Recursive audit passed at node=bootstrap
[2026-02-18 04:07:32] Frame progress linux=-1/484 windows=-1/263 task=unknown probe_ok=False
[2026-02-18 04:15:47] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-18 04:15:47] Machine plan base=n1-highmem-32 opt=n1-highmem-32 train=n1-highmem-32 backtest=n1-highmem-32
[2026-02-18 04:15:47] Spot plan base=False opt=False train=False backtest=False
[2026-02-18 04:15:47] Data caps base(chunk_days=5, max_rows_per_file=0) train(max_files=0, max_rows_per_file=0) backtest(max_files=0, max_rows_per_file=0)
[2026-02-18 04:15:47] Backtest month guard enabled: 2025,202601
[2026-02-18 04:15:47] Recursive audit passed at node=bootstrap
[2026-02-18 04:15:49] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-18 04:15:49] Frame stage complete.
[2026-02-18 04:15:49] Recursive audit passed at node=frame_complete
[2026-02-18 04:15:52] GCS progress linux1=484/484 windows1=263/263
[2026-02-18 04:15:52] Upload stage complete.
[2026-02-18 04:15:55] GCS counts linux1=484 windows1=263
[2026-02-18 04:15:55] Building v60 base matrix with relaxed physics gates...
[2026-02-18 04:15:55] Recursive audit passed at node=pre_base_matrix
[2026-02-18 04:15:55] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-201555_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-201555_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5
[2026-02-18 04:15:56] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-18 04:15:56]   warnings.warn(
[2026-02-18 04:15:56] [*] Packaging code from repo root: /Users/zephryj/work/Omega_vNext
[2026-02-18 04:15:56]     Created archive: /Users/zephryj/work/Omega_vNext/omega_core.zip
[2026-02-18 04:15:56] [*] Uploading to gs://omega_v52/staging/code/omega_core.zip...
[2026-02-18 04:15:59] [+] Code bundle uploaded successfully.
[2026-02-18 04:15:59] [*] Submitting Custom Job: omega-v60-run_vertex_base_matrix-20260218-041559
[2026-02-18 04:15:59] [*] Forcing gcloud fallback submission path.
[2026-02-18 04:16:03] [+] Fallback submit succeeded: projects/269018079180/locations/us-west1/customJobs/568540557731692544
[2026-02-18 04:16:04]     [Fallback] state=JOB_STATE_QUEUED elapsed=1s
[2026-02-18 04:16:35]     [Fallback] state=JOB_STATE_PENDING elapsed=32s
[2026-02-18 04:17:06]     [Fallback] state=JOB_STATE_PENDING elapsed=63s
[2026-02-18 04:17:37]     [Fallback] state=JOB_STATE_PENDING elapsed=94s
[2026-02-18 04:18:08]     [Fallback] state=JOB_STATE_PENDING elapsed=125s
[2026-02-18 04:18:40]     [Fallback] state=JOB_STATE_PENDING elapsed=156s
[2026-02-18 04:19:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=187s
[2026-02-18 04:19:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=218s
[2026-02-18 04:20:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=250s
[2026-02-18 04:20:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=281s
[2026-02-18 04:21:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=312s
[2026-02-18 04:21:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=343s
[2026-02-18 04:22:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=374s
[2026-02-18 04:22:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=405s
[2026-02-18 04:23:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=436s
[2026-02-18 04:23:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=467s
[2026-02-18 04:24:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=499s
[2026-02-18 04:24:54]     [Fallback] state=JOB_STATE_RUNNING elapsed=530s
[2026-02-18 04:25:25]     [Fallback] state=JOB_STATE_RUNNING elapsed=561s
[2026-02-18 04:25:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=592s
[2026-02-18 04:26:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=624s
[2026-02-18 04:26:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=655s
[2026-02-18 04:37:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=1295s
[2026-02-18 04:38:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=1327s
[2026-02-18 04:38:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=1358s
[2026-02-18 04:39:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=1389s
[2026-02-18 04:39:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=1420s
[2026-02-18 04:40:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=1451s
[2026-02-18 04:40:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=1482s
[2026-02-18 04:41:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=1513s
[2026-02-18 04:41:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=1544s
[2026-02-18 04:42:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=1575s
[2026-02-18 04:42:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=1607s
[2026-02-18 04:43:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=1638s
[2026-02-18 04:45:41] Traceback (most recent call last):
[2026-02-18 04:45:41]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 397, in <module>
[2026-02-18 04:45:41]     submit_job(
[2026-02-18 04:45:41]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 287, in submit_job
[2026-02-18 04:45:41]     _submit_via_gcloud_fallback(
[2026-02-18 04:45:41]   File "/Users/zephryj/work/Omega_vNext/tools/submit_vertex_sweep.py", line 223, in _submit_via_gcloud_fallback
[2026-02-18 04:45:41]     sres = subprocess.run(state_cmd, capture_output=True, text=True, check=True)
[2026-02-18 04:45:41]   File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/subprocess.py", line 528, in run
[2026-02-18 04:45:41]     raise CalledProcessError(retcode, process.args,
[2026-02-18 04:45:41] subprocess.CalledProcessError: Command '['gcloud', 'ai', 'custom-jobs', 'describe', 'projects/269018079180/locations/us-west1/customJobs/568540557731692544', '--project=gen-lang-client-0250995579', '--region=us-west1', '--format=value(state)']' returned non-zero exit status 1.

```

## Tail: uplink log
```text
[2026-02-18 04:06:09] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 04:06:11] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 04:06:13] windows1 sync rc=0
[2026-02-18 04:06:13] uplink cycle sleep 300s
[2026-02-18 04:11:13] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 04:11:15] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 04:11:17] windows1 sync rc=0
[2026-02-18 04:11:17] uplink cycle sleep 300s
[2026-02-18 04:16:17] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 04:16:19] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 04:16:21] windows1 sync rc=0
[2026-02-18 04:16:21] uplink cycle sleep 300s
[2026-02-18 04:21:21] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 04:21:23] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 04:21:25] windows1 sync rc=0
[2026-02-18 04:21:25] uplink cycle sleep 300s
[2026-02-18 04:26:25] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 04:26:27] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 04:26:29] windows1 sync rc=0
[2026-02-18 04:26:29] uplink cycle sleep 300s
[2026-02-18 04:31:29] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
[!] Error listing files on zepher@192.168.3.113: Command '['ssh', '-F', '/dev/null', '-o', 'StrictHostKeyChecking=no', '-i', '/Users/zephryj/.ssh/id_ed25519', 'zepher@192.168.3.113', "find /omega_pool/parquet_data/v52/frames/host=linux1/ -maxdepth 1 -type f -name '*_aa8abb7.parquet' -printf 'P,%f,%s\\n'; find /omega_pool/parquet_data/v52/frames/host=linux1/ -maxdepth 1 -type f -name '*_aa8abb7.parquet.done' -printf 'D,%f\\n'"]' returned non-zero exit status 255.
    Stderr: ssh: connect to host 192.168.3.113 port 22: Operation timed out

    Skipping 0 already in GCS.
[2026-02-18 04:32:46] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 04:32:48] windows1 sync rc=0
[2026-02-18 04:32:48] uplink cycle sleep 300s
[2026-02-18 04:37:48] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
[!] Error listing files on zepher@192.168.3.113: Command '['ssh', '-F', '/dev/null', '-o', 'StrictHostKeyChecking=no', '-i', '/Users/zephryj/.ssh/id_ed25519', 'zepher@192.168.3.113', "find /omega_pool/parquet_data/v52/frames/host=linux1/ -maxdepth 1 -type f -name '*_aa8abb7.parquet' -printf 'P,%f,%s\\n'; find /omega_pool/parquet_data/v52/frames/host=linux1/ -maxdepth 1 -type f -name '*_aa8abb7.parquet.done' -printf 'D,%f\\n'"]' returned non-zero exit status 255.
    Stderr: ssh: connect to host 192.168.3.113 port 22: Operation timed out

    Skipping 0 already in GCS.
[2026-02-18 04:39:05] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 04:39:06] windows1 sync rc=0
[2026-02-18 04:39:06] uplink cycle sleep 300s
[2026-02-18 04:44:07] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
[!] Error listing files on zepher@192.168.3.113: Command '['ssh', '-F', '/dev/null', '-o', 'StrictHostKeyChecking=no', '-i', '/Users/zephryj/.ssh/id_ed25519', 'zepher@192.168.3.113', "find /omega_pool/parquet_data/v52/frames/host=linux1/ -maxdepth 1 -type f -name '*_aa8abb7.parquet' -printf 'P,%f,%s\\n'; find /omega_pool/parquet_data/v52/frames/host=linux1/ -maxdepth 1 -type f -name '*_aa8abb7.parquet.done' -printf 'D,%f\\n'"]' returned non-zero exit status 255.
    Stderr: ssh: connect to host 192.168.3.113 port 22: Network is unreachable

    GCS has no existing parquet for this hash/host.
[2026-02-18 04:46:15] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
[!] Error listing files on jiazi@192.168.3.112: Command '['ssh', '-F', '/dev/null', '-o', 'StrictHostKeyChecking=no', '-i', '/Users/zephryj/.ssh/id_ed25519', 'jiazi@192.168.3.112', 'powershell -NoProfile -Command "Get-ChildItem -Path \'D:\\Omega_frames\\v52\\frames\\host=windows1\\\' -Filter \'*_aa8abb7.parquet\' | ForEach-Object { \'P,\' + $_.Name + \',\' + $_.Length }; Get-ChildItem -Path \'D:\\Omega_frames\\v52\\frames\\host=windows1\\\' -Filter \'*_aa8abb7.parquet.done\' | ForEach-Object { \'D,\' + $_.Name }"']' returned non-zero exit status 255.
    Stderr: ssh: connect to host 192.168.3.112 port 22: Network is unreachable

    Skipping 0 already in GCS.
[2026-02-18 04:46:31] windows1 sync rc=0
[2026-02-18 04:46:31] uplink cycle sleep 300s

```