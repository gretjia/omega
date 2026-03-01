# Incident 20260217_160703_autopilot_status_stale
- ts: 2026-02-17 16:07:03
- reason: autopilot_status_stale
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-17 15:43:05",
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
    "updated_at": "2026-02-17 15:43:07"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-17 15:46:18"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-074618_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-074618_aa8abb7/base_matrix.meta.json"
  },
  "train": {},
  "backtest": {},
  "run_id": "20260217-074618",
  "data_pattern": "gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet"
}
```

## screen -ls
```text
There are screens on:
	76230.v60_ai_watchdog_aa8abb7	(Detached)
	38895.v60_uplink_aa8abb7	(Detached)
	25999.v60_autopilot_aa8abb7	(Detached)
3 Sockets in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
25999 SCREEN -dmS v60_autopilot_aa8abb7 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
26001 login -pflq zephryj /bin/bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
26002 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
26005 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800
38895 SCREEN -dmS v60_uplink_aa8abb7 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh

```

## Tail: autopilot runner log
```text
[2026-02-17 12:19:13] Frame progress linux=418/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:22:14] Frame progress linux=420/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:25:16] Frame progress linux=422/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:28:17] Frame progress linux=423/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:31:18] Frame progress linux=425/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:34:20] Frame progress linux=428/497 windows=250/250 task=Ready probe_ok=True
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

```

## Tail: autopilot log
```text
[2026-02-17 10:26:41] Frame progress linux=348/500 windows=216/251 task=Running
[2026-02-17 10:28:43] Frame progress linux=349/500 windows=217/251 task=Running
[2026-02-17 10:30:44] Frame progress linux=350/500 windows=218/251 task=Running
[2026-02-17 10:32:46] Frame progress linux=351/500 windows=218/251 task=Running
[2026-02-17 10:34:48] Frame progress linux=353/500 windows=219/251 task=Running
[2026-02-17 10:36:50] Frame progress linux=354/500 windows=220/251 task=Running
[2026-02-17 10:38:51] Frame progress linux=355/500 windows=221/251 task=Running
[2026-02-17 10:40:53] Frame progress linux=357/500 windows=222/251 task=Running
[2026-02-17 10:42:54] Frame progress linux=358/500 windows=223/251 task=Running
[2026-02-17 10:44:56] Frame progress linux=360/500 windows=224/251 task=Running
[2026-02-17 10:46:57] Frame progress linux=361/500 windows=224/251 task=Running
[2026-02-17 10:48:59] Frame progress linux=362/500 windows=225/251 task=Running
[2026-02-17 10:51:01] Frame progress linux=364/500 windows=226/251 task=Running
[2026-02-17 12:07:06] Autopilot started hash=aa8abb7 expected windows=250 linux=497 poll=180s stall=1800s
[2026-02-17 12:07:08] Frame progress linux=411/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:10:09] Frame progress linux=413/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:13:10] Frame progress linux=415/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:16:12] Frame progress linux=416/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:19:13] Frame progress linux=418/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:22:14] Frame progress linux=420/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:25:16] Frame progress linux=422/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:28:17] Frame progress linux=423/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:31:18] Frame progress linux=425/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:34:20] Frame progress linux=428/497 windows=250/250 task=Ready probe_ok=True
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

```

## Tail: uplink log
```text
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
./Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
......

Average throughput: 0.0B/s
[+] Batch complete. uploaded_parquet=3 uploaded_done=3

[*] Cleaning up local buffer...
[2026-02-17 15:40:37] windows1 sync rc=0
[2026-02-17 15:40:37] uplink cycle sleep 300s
[2026-02-17 15:45:37] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 15:45:39] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 15:45:41] windows1 sync rc=0
[2026-02-17 15:45:41] uplink cycle sleep 300s
[2026-02-17 15:50:41] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 15:50:44] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 15:50:46] windows1 sync rc=0
[2026-02-17 15:50:46] uplink cycle sleep 300s
[2026-02-17 15:55:46] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 15:55:50] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 15:55:52] windows1 sync rc=0
[2026-02-17 15:55:52] uplink cycle sleep 300s
[2026-02-17 16:00:52] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 16:00:55] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 16:00:57] windows1 sync rc=0
[2026-02-17 16:00:57] uplink cycle sleep 300s
[2026-02-17 16:05:57] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 16:05:59] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 16:06:02] windows1 sync rc=0
[2026-02-17 16:06:02] uplink cycle sleep 300s

```