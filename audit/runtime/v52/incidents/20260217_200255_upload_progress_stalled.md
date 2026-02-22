# Incident 20260217_200255_upload_progress_stalled
- ts: 2026-02-17 20:02:55
- reason: upload_progress_stalled
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-17 20:02:37",
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
    "updated_at": "2026-02-17 20:02:39"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-17 20:02:45"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-120245_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-120245_aa8abb7/base_matrix.meta.json",
    "base_matrix_exec_mode": "vertex",
    "base_matrix_machine_type": "n2-highmem-16",
    "base_matrix_spot": false
  },
  "train": {},
  "backtest": {},
  "run_id": "20260217-120245",
  "data_pattern": "gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet"
}
```

## screen -ls
```text
There are screens on:
	86977.v60_ai_watchdog_aa8abb7	(Detached)
	86775.v60_autopilot_aa8abb7	(Detached)
2 Sockets in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh
86775 SCREEN -dmS v60_autopilot_aa8abb7 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
86776 login -pflq zephryj /bin/bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
86777 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
86780 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

```

## Tail: autopilot runner log
```text
[2026-02-17 13:31:45] Frame progress linux=461/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:34:47] Frame progress linux=463/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:37:48] Frame progress linux=465/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:40:49] Frame progress linux=467/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:43:51] Frame progress linux=468/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:46:52] Frame progress linux=470/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:50:27] Frame progress linux=472/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:53:28] Frame progress linux=473/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:56:30] Frame progress linux=475/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:59:31] Frame progress linux=476/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:02:32] Frame progress linux=478/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:05:34] Frame progress linux=479/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:08:35] Frame progress linux=481/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:11:37] Frame progress linux=482/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:14:38] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:17:39] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:20:41] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:23:42] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:26:43] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:29:45] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:32:46] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:35:47] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:38:49] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:41:50] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:41:51] Autopilot started hash=aa8abb7 expected windows=250 linux=497 poll=180s stall=1800s optimization=True
[2026-02-17 14:41:52] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:44:54] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:47:55] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:50:57] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:53:58] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:56:59] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:00:01] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:03:02] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:06:04] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:09:05] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:12:07] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 561, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 319, in main
    diag = collect_diag(args.windows_task_name)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 153, in collect_diag
    win_out = run([sys.executable, str(SSH_PS), WINDOWS_SSH_TARGET, "--command", win_ps], check=False).stdout
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 31, in run
    return subprocess.run(cmd, cwd=REPO_ROOT, check=check, capture_output=True, text=True)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/subprocess.py", line 507, in run
    stdout, stderr = process.communicate(input, timeout=timeout)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/subprocess.py", line 1134, in communicate
    stdout, stderr = self._communicate(input, endtime, timeout)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/subprocess.py", line 2017, in _communicate
    stdout = self._translate_newlines(stdout,
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/subprocess.py", line 1011, in _translate_newlines
    data = data.decode(encoding, errors)
UnicodeDecodeError: 'utf-8' codec can't decode bytes in position 1394-1395: invalid continuation byte
[2026-02-17 15:14:37] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 15:14:39] Frame progress linux=484/484 windows=251/263 task=Ready probe_ok=True
[2026-02-17 15:17:40] Frame progress linux=484/484 windows=252/263 task=Ready probe_ok=True
[2026-02-17 15:20:42] Frame progress linux=484/484 windows=254/263 task=Ready probe_ok=True
[2026-02-17 15:23:43] Frame progress linux=484/484 windows=255/263 task=Ready probe_ok=True
[2026-02-17 15:26:45] Frame progress linux=484/484 windows=256/263 task=Ready probe_ok=True
[2026-02-17 15:29:46] Frame progress linux=484/484 windows=258/263 task=Ready probe_ok=True
[2026-02-17 15:32:48] Frame progress linux=484/484 windows=259/263 task=Ready probe_ok=True
[2026-02-17 15:35:50] Frame progress linux=484/484 windows=260/263 task=Ready probe_ok=True
[2026-02-17 15:38:52] Frame progress linux=484/484 windows=261/263 task=Ready probe_ok=True
[2026-02-17 15:41:53] Frame progress linux=484/484 windows=262/263 task=Ready probe_ok=True
[2026-02-17 15:43:05] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 15:43:05] Recursive audit passed at node=bootstrap
[2026-02-17 15:43:07] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 15:43:07] Frame stage complete.
[2026-02-17 15:43:07] Recursive audit passed at node=frame_complete
[2026-02-17 15:43:10] GCS progress linux1=484/484 windows1=262/263
[2026-02-17 15:44:54] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 15:44:54] Frame stage complete.
[2026-02-17 15:44:58] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 15:44:58] Upload stage complete.
[2026-02-17 15:45:02] GCS counts linux1=484 windows1=263
[2026-02-17 15:45:02] Building v60 base matrix with relaxed physics gates...
[2026-02-17 15:45:02] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/v60_build_base_matrix.py --input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --years=2023,2024 --hash=aa8abb7 --peace-threshold=0.1 --srl-resid-sigma-mult=0.5 --output-parquet=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/20260217-074502_aa8abb7/base_matrix.parquet --output-meta=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/20260217-074502_aa8abb7/base_matrix.parquet.meta.json --output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-074502_aa8abb7/base_matrix.parquet --output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-074502_aa8abb7/base_matrix.meta.json --seed=42
[2026-02-17 15:45:03] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
[2026-02-17 15:45:03]   warnings.warn(eol_message.format("3.9"), FutureWarning)
[2026-02-17 15:45:03] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 15:45:03]   warnings.warn(
[2026-02-17 15:45:03] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
[2026-02-17 15:45:03]   warnings.warn(eol_message.format("3.9"), FutureWarning)
[2026-02-17 15:46:14] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 15:46:14] Upload stage complete.
[2026-02-17 15:46:18] GCS counts linux1=484 windows1=263
[2026-02-17 15:46:18] Building v60 base matrix with relaxed physics gates...
[2026-02-17 15:46:18] Recursive audit passed at node=pre_base_matrix
[2026-02-17 15:46:18] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/v60_build_base_matrix.py --input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --years=2023,2024 --hash=aa8abb7 --peace-threshold=0.1 --srl-resid-sigma-mult=0.5 --output-parquet=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/20260217-074618_aa8abb7/base_matrix.parquet --output-meta=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/20260217-074618_aa8abb7/base_matrix.parquet.meta.json --output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-074618_aa8abb7/base_matrix.parquet --output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-074618_aa8abb7/base_matrix.meta.json --seed=42
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

```

## Tail: autopilot log
```text
[2026-02-17 12:37:21] Frame progress linux=429/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:40:22] Frame progress linux=432/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:43:24] Frame progress linux=433/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:46:25] Frame progress linux=435/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:49:26] Frame progress linux=437/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:52:28] Frame progress linux=438/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:55:29] Frame progress linux=440/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:58:30] Frame progress linux=442/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:01:32] Frame progress linux=444/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:04:33] Frame progress linux=445/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:07:34] Frame progress linux=447/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:10:36] Frame progress linux=449/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:13:37] Frame progress linux=450/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:16:38] Frame progress linux=452/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:19:40] Frame progress linux=454/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:22:41] Frame progress linux=456/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:25:43] Frame progress linux=458/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:28:44] Frame progress linux=459/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:31:45] Frame progress linux=461/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:34:47] Frame progress linux=463/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:37:48] Frame progress linux=465/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:40:49] Frame progress linux=467/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:43:51] Frame progress linux=468/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:46:52] Frame progress linux=470/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:50:27] Frame progress linux=472/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:53:28] Frame progress linux=473/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:56:30] Frame progress linux=475/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 13:59:31] Frame progress linux=476/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:02:32] Frame progress linux=478/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:05:34] Frame progress linux=479/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:08:35] Frame progress linux=481/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:11:37] Frame progress linux=482/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:14:38] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:17:39] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:20:41] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:23:42] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:26:43] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:29:45] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:32:46] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:35:47] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:38:49] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:41:50] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:41:51] Autopilot started hash=aa8abb7 expected windows=250 linux=497 poll=180s stall=1800s optimization=True
[2026-02-17 14:41:52] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:44:54] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:47:55] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:50:57] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:53:58] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 14:56:59] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:00:01] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:03:02] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:06:04] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:09:05] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:12:07] Frame progress linux=484/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 15:14:37] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 15:14:39] Frame progress linux=484/484 windows=251/263 task=Ready probe_ok=True
[2026-02-17 15:17:40] Frame progress linux=484/484 windows=252/263 task=Ready probe_ok=True
[2026-02-17 15:20:42] Frame progress linux=484/484 windows=254/263 task=Ready probe_ok=True
[2026-02-17 15:23:43] Frame progress linux=484/484 windows=255/263 task=Ready probe_ok=True
[2026-02-17 15:26:45] Frame progress linux=484/484 windows=256/263 task=Ready probe_ok=True
[2026-02-17 15:29:46] Frame progress linux=484/484 windows=258/263 task=Ready probe_ok=True
[2026-02-17 15:32:48] Frame progress linux=484/484 windows=259/263 task=Ready probe_ok=True
[2026-02-17 15:35:50] Frame progress linux=484/484 windows=260/263 task=Ready probe_ok=True
[2026-02-17 15:38:52] Frame progress linux=484/484 windows=261/263 task=Ready probe_ok=True
[2026-02-17 15:41:53] Frame progress linux=484/484 windows=262/263 task=Ready probe_ok=True
[2026-02-17 15:43:05] Autopilot started hash=aa8abb7 expected windows=263 linux=484 poll=180s stall=1800s optimization=True
[2026-02-17 15:43:05] Recursive audit passed at node=bootstrap
[2026-02-17 15:43:07] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 15:43:07] Frame stage complete.
[2026-02-17 15:43:07] Recursive audit passed at node=frame_complete
[2026-02-17 15:43:10] GCS progress linux1=484/484 windows1=262/263
[2026-02-17 15:44:54] Frame progress linux=484/484 windows=263/263 task=Ready probe_ok=True
[2026-02-17 15:44:54] Frame stage complete.
[2026-02-17 15:44:58] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 15:44:58] Upload stage complete.
[2026-02-17 15:45:02] GCS counts linux1=484 windows1=263
[2026-02-17 15:45:02] Building v60 base matrix with relaxed physics gates...
[2026-02-17 15:45:02] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/v60_build_base_matrix.py --input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --years=2023,2024 --hash=aa8abb7 --peace-threshold=0.1 --srl-resid-sigma-mult=0.5 --output-parquet=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/20260217-074502_aa8abb7/base_matrix.parquet --output-meta=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/20260217-074502_aa8abb7/base_matrix.parquet.meta.json --output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-074502_aa8abb7/base_matrix.parquet --output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-074502_aa8abb7/base_matrix.meta.json --seed=42
[2026-02-17 15:45:03] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
[2026-02-17 15:45:03]   warnings.warn(eol_message.format("3.9"), FutureWarning)
[2026-02-17 15:45:03] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
[2026-02-17 15:45:03]   warnings.warn(
[2026-02-17 15:45:03] /Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
[2026-02-17 15:45:03]   warnings.warn(eol_message.format("3.9"), FutureWarning)
[2026-02-17 15:46:14] GCS progress linux1=484/484 windows1=263/263
[2026-02-17 15:46:14] Upload stage complete.
[2026-02-17 15:46:18] GCS counts linux1=484 windows1=263
[2026-02-17 15:46:18] Building v60 base matrix with relaxed physics gates...
[2026-02-17 15:46:18] Recursive audit passed at node=pre_base_matrix
[2026-02-17 15:46:18] + /Library/Developer/CommandLineTools/usr/bin/python3 tools/v60_build_base_matrix.py --input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --years=2023,2024 --hash=aa8abb7 --peace-threshold=0.1 --srl-resid-sigma-mult=0.5 --output-parquet=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/20260217-074618_aa8abb7/base_matrix.parquet --output-meta=/Users/zephryj/work/Omega_vNext/artifacts/runtime/v60/20260217-074618_aa8abb7/base_matrix.parquet.meta.json --output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-074618_aa8abb7/base_matrix.parquet --output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-074618_aa8abb7/base_matrix.meta.json --seed=42
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

```

## Tail: uplink log
```text
[2026-02-17 19:19:04] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 19:19:06] windows1 sync rc=0
[2026-02-17 19:19:06] uplink cycle sleep 300s
[2026-02-17 19:24:06] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 19:24:08] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 19:24:10] windows1 sync rc=0
[2026-02-17 19:24:10] uplink cycle sleep 300s
[2026-02-17 19:29:10] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 19:29:12] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 19:29:14] windows1 sync rc=0
[2026-02-17 19:29:14] uplink cycle sleep 300s
[2026-02-17 19:34:14] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 19:34:16] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 19:34:18] windows1 sync rc=0
[2026-02-17 19:34:18] uplink cycle sleep 300s
[2026-02-17 19:39:18] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 19:39:20] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 19:39:22] windows1 sync rc=0
[2026-02-17 19:39:22] uplink cycle sleep 300s
[2026-02-17 19:44:22] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 19:44:24] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 19:44:26] windows1 sync rc=0
[2026-02-17 19:44:26] uplink cycle sleep 300s
[2026-02-17 19:49:26] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
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

```