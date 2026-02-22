# Incident 20260218_000255_autopilot_status_stale
- ts: 2026-02-18 00:02:55
- reason: autopilot_status_stale
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-17 22:01:34",
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
    "updated_at": "2026-02-17 22:01:36"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-17 22:01:42"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-140142_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-140142_aa8abb7/base_matrix.meta.json",
    "base_matrix_exec_mode": "vertex",
    "base_matrix_machine_type": "n1-highmem-32",
    "base_matrix_spot": false
  },
  "train": {},
  "backtest": {},
  "run_id": "20260217-140142",
  "data_pattern": "gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet"
}
```

## screen -ls
```text
There are screens on:
	5611.v60_autopilot_aa8abb7	(Detached)
	5633.v60_ai_watchdog_aa8abb7	(Detached)
2 Sockets in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
5611 SCREEN -dmS v60_autopilot_aa8abb7 bash -lc 
cd /Users/zephryj/work/Omega_vNext && \
PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py \
  --hash aa8abb7 \
  --linux-expected 484 \
  --windows-expected 263 \
  --upload-mode wait_existing \
  --poll-sec 180 \
  --stall-sec 1800 \
  --base-matrix-exec-mode vertex \
  --base-matrix-machine-type n1-highmem-32 \
  --base-matrix-max-rows-per-file=0 \
  --base-matrix-chunk-days=5 \
  --optimization-machine-type n1-highmem-32 \
  --train-machine-type n1-highmem-32 \
  --backtest-machine-type n1-highmem-32 \
  --base-matrix-sync-timeout-sec 21600 \
  --optimization-sync-timeout-sec 10800 \
  --train-sync-timeout-sec 21600 \
  --backtest-sync-timeout-sec 10800 \
  --test-years 2025,2026 \
  --test-year-months 2025,202601 \
  >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

5612 login -pflq zephryj /bin/bash -lc 
cd /Users/zephryj/work/Omega_vNext && \
PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py \
  --hash aa8abb7 \
  --linux-expected 484 \
  --windows-expected 263 \
  --upload-mode wait_existing \
  --poll-sec 180 \
  --stall-sec 1800 \
  --base-matrix-exec-mode vertex \
  --base-matrix-machine-type n1-highmem-32 \
  --base-matrix-max-rows-per-file=0 \
  --base-matrix-chunk-days=5 \
  --optimization-machine-type n1-highmem-32 \
  --train-machine-type n1-highmem-32 \
  --backtest-machine-type n1-highmem-32 \
  --base-matrix-sync-timeout-sec 21600 \
  --optimization-sync-timeout-sec 10800 \
  --train-sync-timeout-sec 21600 \
  --backtest-sync-timeout-sec 10800 \
  --test-years 2025,2026 \
  --test-year-months 2025,202601 \
  >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

5635 bash -lc 
cd /Users/zephryj/work/Omega_vNext && \
PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py \
  --hash aa8abb7 \
  --linux-expected 484 \
  --windows-expected 263 \
  --upload-mode wait_existing \
  --poll-sec 180 \
  --stall-sec 1800 \
  --base-matrix-exec-mode vertex \
  --base-matrix-machine-type n1-highmem-32 \
  --base-matrix-max-rows-per-file=0 \
  --base-matrix-chunk-days=5 \
  --optimization-machine-type n1-highmem-32 \
  --train-machine-type n1-highmem-32 \
  --backtest-machine-type n1-highmem-32 \
  --base-matrix-sync-timeout-sec 21600 \
  --optimization-sync-timeout-sec 10800 \
  --train-sync-timeout-sec 21600 \
  --backtest-sync-timeout-sec 10800 \
  --test-years 2025,2026 \
  --test-year-months 2025,202601 \
  >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

5638 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh

```

## Tail: autopilot runner log
```text
[2026-02-17 23:00:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=3547s
[2026-02-17 23:01:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=3578s
[2026-02-17 23:01:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=3609s
[2026-02-17 23:02:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=3640s
[2026-02-17 23:03:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=3672s
[2026-02-17 23:03:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=3703s
[2026-02-17 23:04:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=3734s
[2026-02-17 23:04:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=3765s
[2026-02-17 23:05:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=3796s
[2026-02-17 23:05:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=3827s
[2026-02-17 23:06:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=3858s
[2026-02-17 23:06:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=3889s
[2026-02-17 23:07:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=3920s
[2026-02-17 23:07:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=3952s
[2026-02-17 23:08:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=3983s
[2026-02-17 23:08:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=4014s
[2026-02-17 23:09:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=4045s
[2026-02-17 23:09:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=4076s
[2026-02-17 23:10:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=4107s
[2026-02-17 23:10:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=4138s
[2026-02-17 23:11:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=4169s
[2026-02-17 23:11:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=4200s
[2026-02-17 23:12:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=4231s
[2026-02-17 23:12:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=4263s
[2026-02-17 23:13:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=4294s
[2026-02-17 23:13:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=4325s
[2026-02-17 23:14:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=4356s
[2026-02-17 23:14:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=4387s
[2026-02-17 23:15:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=4418s
[2026-02-17 23:15:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=4449s
[2026-02-17 23:16:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=4480s
[2026-02-17 23:17:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=4512s
[2026-02-17 23:17:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=4543s
[2026-02-17 23:18:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=4574s
[2026-02-17 23:18:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=4605s
[2026-02-17 23:19:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=4636s
[2026-02-17 23:19:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=4667s
[2026-02-17 23:20:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=4698s
[2026-02-17 23:20:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=4729s
[2026-02-17 23:21:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=4760s
[2026-02-17 23:21:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=4791s
[2026-02-17 23:22:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=4823s
[2026-02-17 23:22:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=4854s
[2026-02-17 23:23:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=4885s
[2026-02-17 23:23:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=4916s
[2026-02-17 23:24:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=4947s
[2026-02-17 23:24:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=4978s
[2026-02-17 23:25:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=5009s
[2026-02-17 23:25:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=5040s
[2026-02-17 23:26:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=5071s
[2026-02-17 23:26:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=5103s
[2026-02-17 23:27:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=5134s
[2026-02-17 23:27:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=5165s
[2026-02-17 23:28:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=5196s
[2026-02-17 23:28:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=5227s
[2026-02-17 23:29:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=5258s
[2026-02-17 23:29:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=5289s
[2026-02-17 23:30:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=5320s
[2026-02-17 23:31:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=5351s
[2026-02-17 23:31:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=5382s
[2026-02-17 23:32:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=5414s
[2026-02-17 23:32:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=5445s
[2026-02-17 23:33:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=5476s
[2026-02-17 23:33:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=5507s
[2026-02-17 23:34:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=5538s
[2026-02-17 23:34:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=5569s
[2026-02-17 23:35:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=5600s
[2026-02-17 23:35:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=5631s
[2026-02-17 23:36:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=5663s
[2026-02-17 23:36:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=5694s
[2026-02-17 23:37:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=5725s
[2026-02-17 23:37:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=5756s
[2026-02-17 23:38:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=5787s
[2026-02-17 23:38:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=5818s
[2026-02-17 23:39:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=5849s
[2026-02-17 23:39:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=5880s
[2026-02-17 23:40:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=5911s
[2026-02-17 23:40:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=5943s
[2026-02-17 23:41:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=5974s
[2026-02-17 23:41:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=6005s
[2026-02-17 23:42:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=6036s
[2026-02-17 23:42:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=6067s
[2026-02-17 23:43:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=6098s
[2026-02-17 23:43:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=6129s
[2026-02-17 23:44:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=6160s
[2026-02-17 23:45:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=6191s
[2026-02-17 23:45:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=6223s
[2026-02-17 23:46:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=6254s
[2026-02-17 23:46:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=6285s
[2026-02-17 23:47:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=6316s
[2026-02-17 23:47:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=6347s
[2026-02-17 23:48:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=6378s
[2026-02-17 23:48:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=6409s
[2026-02-17 23:49:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=6440s
[2026-02-17 23:49:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=6472s
[2026-02-17 23:50:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=6503s
[2026-02-17 23:50:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=6534s
[2026-02-17 23:51:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=6565s
[2026-02-17 23:51:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=6596s
[2026-02-17 23:52:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=6627s
[2026-02-17 23:52:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=6658s
[2026-02-17 23:53:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=6689s
[2026-02-17 23:53:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=6720s
[2026-02-17 23:54:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=6752s
[2026-02-17 23:54:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=6783s
[2026-02-17 23:55:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=6814s
[2026-02-17 23:55:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=6845s
[2026-02-17 23:56:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=6876s
[2026-02-17 23:56:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=6907s
[2026-02-17 23:57:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=6938s
[2026-02-17 23:57:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=6969s
[2026-02-17 23:58:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=7001s
[2026-02-17 23:59:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=7032s
[2026-02-17 23:59:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=7065s
[2026-02-18 00:00:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=7098s
[2026-02-18 00:00:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=7129s
[2026-02-18 00:01:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=7160s
[2026-02-18 00:01:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=7191s
[2026-02-18 00:02:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=7222s
[2026-02-18 00:02:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=7253s

```

## Tail: autopilot log
```text
[2026-02-17 23:00:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=3547s
[2026-02-17 23:01:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=3578s
[2026-02-17 23:01:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=3609s
[2026-02-17 23:02:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=3640s
[2026-02-17 23:03:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=3672s
[2026-02-17 23:03:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=3703s
[2026-02-17 23:04:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=3734s
[2026-02-17 23:04:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=3765s
[2026-02-17 23:05:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=3796s
[2026-02-17 23:05:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=3827s
[2026-02-17 23:06:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=3858s
[2026-02-17 23:06:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=3889s
[2026-02-17 23:07:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=3920s
[2026-02-17 23:07:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=3952s
[2026-02-17 23:08:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=3983s
[2026-02-17 23:08:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=4014s
[2026-02-17 23:09:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=4045s
[2026-02-17 23:09:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=4076s
[2026-02-17 23:10:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=4107s
[2026-02-17 23:10:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=4138s
[2026-02-17 23:11:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=4169s
[2026-02-17 23:11:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=4200s
[2026-02-17 23:12:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=4231s
[2026-02-17 23:12:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=4263s
[2026-02-17 23:13:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=4294s
[2026-02-17 23:13:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=4325s
[2026-02-17 23:14:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=4356s
[2026-02-17 23:14:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=4387s
[2026-02-17 23:15:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=4418s
[2026-02-17 23:15:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=4449s
[2026-02-17 23:16:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=4480s
[2026-02-17 23:17:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=4512s
[2026-02-17 23:17:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=4543s
[2026-02-17 23:18:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=4574s
[2026-02-17 23:18:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=4605s
[2026-02-17 23:19:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=4636s
[2026-02-17 23:19:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=4667s
[2026-02-17 23:20:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=4698s
[2026-02-17 23:20:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=4729s
[2026-02-17 23:21:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=4760s
[2026-02-17 23:21:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=4791s
[2026-02-17 23:22:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=4823s
[2026-02-17 23:22:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=4854s
[2026-02-17 23:23:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=4885s
[2026-02-17 23:23:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=4916s
[2026-02-17 23:24:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=4947s
[2026-02-17 23:24:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=4978s
[2026-02-17 23:25:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=5009s
[2026-02-17 23:25:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=5040s
[2026-02-17 23:26:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=5071s
[2026-02-17 23:26:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=5103s
[2026-02-17 23:27:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=5134s
[2026-02-17 23:27:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=5165s
[2026-02-17 23:28:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=5196s
[2026-02-17 23:28:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=5227s
[2026-02-17 23:29:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=5258s
[2026-02-17 23:29:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=5289s
[2026-02-17 23:30:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=5320s
[2026-02-17 23:31:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=5351s
[2026-02-17 23:31:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=5382s
[2026-02-17 23:32:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=5414s
[2026-02-17 23:32:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=5445s
[2026-02-17 23:33:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=5476s
[2026-02-17 23:33:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=5507s
[2026-02-17 23:34:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=5538s
[2026-02-17 23:34:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=5569s
[2026-02-17 23:35:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=5600s
[2026-02-17 23:35:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=5631s
[2026-02-17 23:36:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=5663s
[2026-02-17 23:36:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=5694s
[2026-02-17 23:37:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=5725s
[2026-02-17 23:37:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=5756s
[2026-02-17 23:38:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=5787s
[2026-02-17 23:38:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=5818s
[2026-02-17 23:39:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=5849s
[2026-02-17 23:39:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=5880s
[2026-02-17 23:40:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=5911s
[2026-02-17 23:40:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=5943s
[2026-02-17 23:41:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=5974s
[2026-02-17 23:41:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=6005s
[2026-02-17 23:42:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=6036s
[2026-02-17 23:42:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=6067s
[2026-02-17 23:43:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=6098s
[2026-02-17 23:43:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=6129s
[2026-02-17 23:44:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=6160s
[2026-02-17 23:45:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=6191s
[2026-02-17 23:45:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=6223s
[2026-02-17 23:46:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=6254s
[2026-02-17 23:46:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=6285s
[2026-02-17 23:47:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=6316s
[2026-02-17 23:47:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=6347s
[2026-02-17 23:48:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=6378s
[2026-02-17 23:48:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=6409s
[2026-02-17 23:49:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=6440s
[2026-02-17 23:49:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=6472s
[2026-02-17 23:50:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=6503s
[2026-02-17 23:50:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=6534s
[2026-02-17 23:51:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=6565s
[2026-02-17 23:51:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=6596s
[2026-02-17 23:52:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=6627s
[2026-02-17 23:52:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=6658s
[2026-02-17 23:53:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=6689s
[2026-02-17 23:53:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=6720s
[2026-02-17 23:54:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=6752s
[2026-02-17 23:54:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=6783s
[2026-02-17 23:55:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=6814s
[2026-02-17 23:55:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=6845s
[2026-02-17 23:56:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=6876s
[2026-02-17 23:56:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=6907s
[2026-02-17 23:57:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=6938s
[2026-02-17 23:57:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=6969s
[2026-02-17 23:58:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=7001s
[2026-02-17 23:59:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=7032s
[2026-02-17 23:59:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=7065s
[2026-02-18 00:00:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=7098s
[2026-02-18 00:00:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=7129s
[2026-02-18 00:01:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=7160s
[2026-02-18 00:01:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=7191s
[2026-02-18 00:02:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=7222s
[2026-02-18 00:02:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=7253s

```

## Tail: uplink log
```text
[2026-02-17 23:17:25] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 23:17:27] windows1 sync rc=0
[2026-02-17 23:17:27] uplink cycle sleep 300s
[2026-02-17 23:22:27] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 23:22:29] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 23:22:31] windows1 sync rc=0
[2026-02-17 23:22:31] uplink cycle sleep 300s
[2026-02-17 23:27:31] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 23:27:33] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 23:27:35] windows1 sync rc=0
[2026-02-17 23:27:35] uplink cycle sleep 300s
[2026-02-17 23:32:35] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 23:32:37] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 23:32:39] windows1 sync rc=0
[2026-02-17 23:32:39] uplink cycle sleep 300s
[2026-02-17 23:37:39] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 23:37:41] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 23:37:43] windows1 sync rc=0
[2026-02-17 23:37:43] uplink cycle sleep 300s
[2026-02-17 23:42:43] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 23:42:45] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 23:42:47] windows1 sync rc=0
[2026-02-17 23:42:47] uplink cycle sleep 300s
[2026-02-17 23:47:47] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 23:47:49] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 23:47:51] windows1 sync rc=0
[2026-02-17 23:47:51] uplink cycle sleep 300s
[2026-02-17 23:52:51] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 23:52:53] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 23:52:55] windows1 sync rc=0
[2026-02-17 23:52:55] uplink cycle sleep 300s
[2026-02-17 23:57:55] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-17 23:57:57] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-17 23:57:59] windows1 sync rc=0
[2026-02-17 23:57:59] uplink cycle sleep 300s

```