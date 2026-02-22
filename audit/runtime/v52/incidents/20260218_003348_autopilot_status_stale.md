# Incident 20260218_003348_autopilot_status_stale
- ts: 2026-02-18 00:33:48
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
There is a screen on:
	5611.v60_autopilot_aa8abb7	(Detached)
1 Socket in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


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
[2026-02-18 00:03:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=7285s
[2026-02-18 00:03:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=7316s
[2026-02-18 00:04:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=7347s
[2026-02-18 00:04:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=7379s
[2026-02-18 00:05:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=7410s
[2026-02-18 00:05:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=7441s
[2026-02-18 00:06:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=7472s
[2026-02-18 00:06:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=7503s
[2026-02-18 00:07:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=7534s
[2026-02-18 00:07:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=7565s
[2026-02-18 00:08:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=7596s
[2026-02-18 00:08:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=7627s
[2026-02-18 00:09:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=7659s
[2026-02-18 00:10:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=7690s
[2026-02-18 00:10:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=7721s
[2026-02-18 00:11:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=7752s
[2026-02-18 00:11:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=7783s
[2026-02-18 00:12:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=7814s
[2026-02-18 00:12:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=7845s
[2026-02-18 00:13:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=7876s
[2026-02-18 00:13:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=7907s
[2026-02-18 00:14:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=7939s
[2026-02-18 00:14:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=7972s
[2026-02-18 00:15:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=8003s
[2026-02-18 00:15:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=8034s
[2026-02-18 00:16:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=8065s
[2026-02-18 00:16:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=8097s
[2026-02-18 00:17:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=8128s
[2026-02-18 00:17:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=8159s
[2026-02-18 00:18:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=8190s
[2026-02-18 00:18:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=8221s
[2026-02-18 00:19:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=8252s
[2026-02-18 00:19:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=8284s
[2026-02-18 00:20:25]     [Fallback] state=JOB_STATE_RUNNING elapsed=8315s
[2026-02-18 00:20:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=8346s
[2026-02-18 00:21:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=8377s
[2026-02-18 00:21:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=8408s
[2026-02-18 00:22:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=8439s
[2026-02-18 00:23:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=8470s
[2026-02-18 00:23:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=8501s
[2026-02-18 00:24:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=8533s
[2026-02-18 00:24:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=8564s
[2026-02-18 00:25:05]     [Fallback] state=JOB_STATE_RUNNING elapsed=8595s
[2026-02-18 00:25:36]     [Fallback] state=JOB_STATE_RUNNING elapsed=8626s
[2026-02-18 00:26:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=8657s
[2026-02-18 00:26:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=8688s
[2026-02-18 00:27:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=8719s
[2026-02-18 00:27:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=8750s
[2026-02-18 00:28:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=8781s
[2026-02-18 00:28:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=8813s
[2026-02-18 00:29:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=8844s
[2026-02-18 00:29:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=8875s
[2026-02-18 00:30:16]     [Fallback] state=JOB_STATE_RUNNING elapsed=8906s
[2026-02-18 00:30:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=8937s
[2026-02-18 00:31:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=8968s
[2026-02-18 00:31:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=8999s
[2026-02-18 00:32:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=9030s
[2026-02-18 00:32:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=9061s
[2026-02-18 00:33:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=9093s

```

## Tail: autopilot log
```text
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
[2026-02-18 00:03:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=7285s
[2026-02-18 00:03:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=7316s
[2026-02-18 00:04:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=7347s
[2026-02-18 00:04:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=7379s
[2026-02-18 00:05:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=7410s
[2026-02-18 00:05:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=7441s
[2026-02-18 00:06:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=7472s
[2026-02-18 00:06:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=7503s
[2026-02-18 00:07:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=7534s
[2026-02-18 00:07:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=7565s
[2026-02-18 00:08:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=7596s
[2026-02-18 00:08:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=7627s
[2026-02-18 00:09:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=7659s
[2026-02-18 00:10:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=7690s
[2026-02-18 00:10:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=7721s
[2026-02-18 00:11:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=7752s
[2026-02-18 00:11:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=7783s
[2026-02-18 00:12:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=7814s
[2026-02-18 00:12:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=7845s
[2026-02-18 00:13:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=7876s
[2026-02-18 00:13:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=7907s
[2026-02-18 00:14:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=7939s
[2026-02-18 00:14:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=7972s
[2026-02-18 00:15:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=8003s
[2026-02-18 00:15:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=8034s
[2026-02-18 00:16:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=8065s
[2026-02-18 00:16:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=8097s
[2026-02-18 00:17:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=8128s
[2026-02-18 00:17:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=8159s
[2026-02-18 00:18:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=8190s
[2026-02-18 00:18:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=8221s
[2026-02-18 00:19:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=8252s
[2026-02-18 00:19:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=8284s
[2026-02-18 00:20:25]     [Fallback] state=JOB_STATE_RUNNING elapsed=8315s
[2026-02-18 00:20:56]     [Fallback] state=JOB_STATE_RUNNING elapsed=8346s
[2026-02-18 00:21:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=8377s
[2026-02-18 00:21:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=8408s
[2026-02-18 00:22:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=8439s
[2026-02-18 00:23:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=8470s
[2026-02-18 00:23:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=8501s
[2026-02-18 00:24:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=8533s
[2026-02-18 00:24:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=8564s
[2026-02-18 00:25:05]     [Fallback] state=JOB_STATE_RUNNING elapsed=8595s
[2026-02-18 00:25:36]     [Fallback] state=JOB_STATE_RUNNING elapsed=8626s
[2026-02-18 00:26:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=8657s
[2026-02-18 00:26:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=8688s
[2026-02-18 00:27:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=8719s
[2026-02-18 00:27:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=8750s
[2026-02-18 00:28:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=8781s
[2026-02-18 00:28:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=8813s
[2026-02-18 00:29:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=8844s
[2026-02-18 00:29:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=8875s
[2026-02-18 00:30:16]     [Fallback] state=JOB_STATE_RUNNING elapsed=8906s
[2026-02-18 00:30:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=8937s
[2026-02-18 00:31:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=8968s
[2026-02-18 00:31:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=8999s
[2026-02-18 00:32:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=9030s
[2026-02-18 00:32:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=9061s
[2026-02-18 00:33:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=9093s

```

## Tail: uplink log
```text
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
[2026-02-18 00:02:59] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 00:03:01] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 00:03:03] windows1 sync rc=0
[2026-02-18 00:03:03] uplink cycle sleep 300s
[2026-02-18 00:08:03] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 00:08:05] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 00:08:07] windows1 sync rc=0
[2026-02-18 00:08:07] uplink cycle sleep 300s
[2026-02-18 00:13:07] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 00:13:09] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 00:13:11] windows1 sync rc=0
[2026-02-18 00:13:11] uplink cycle sleep 300s
[2026-02-18 00:18:11] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 00:18:13] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 00:18:14] windows1 sync rc=0
[2026-02-18 00:18:14] uplink cycle sleep 300s
[2026-02-18 00:23:14] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 00:23:17] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 00:23:18] windows1 sync rc=0
[2026-02-18 00:23:18] uplink cycle sleep 300s
[2026-02-18 00:28:18] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 00:28:20] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 00:28:22] windows1 sync rc=0
[2026-02-18 00:28:22] uplink cycle sleep 300s
[2026-02-18 00:33:22] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 00:33:24] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 00:33:26] windows1 sync rc=0
[2026-02-18 00:33:26] uplink cycle sleep 300s

```