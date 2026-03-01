# Incident 20260218_024522_autopilot_status_stale
- ts: 2026-02-18 02:45:22
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
[2026-02-18 01:43:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=13294s
[2026-02-18 01:43:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=13325s
[2026-02-18 01:44:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=13356s
[2026-02-18 01:44:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=13387s
[2026-02-18 01:45:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=13418s
[2026-02-18 01:45:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=13449s
[2026-02-18 01:46:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=13480s
[2026-02-18 01:47:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=13511s
[2026-02-18 01:47:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=13543s
[2026-02-18 01:48:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=13574s
[2026-02-18 01:48:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=13605s
[2026-02-18 01:49:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=13636s
[2026-02-18 01:49:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=13667s
[2026-02-18 01:50:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=13698s
[2026-02-18 01:50:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=13729s
[2026-02-18 01:51:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=13760s
[2026-02-18 01:51:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=13792s
[2026-02-18 01:52:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=13823s
[2026-02-18 01:52:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=13854s
[2026-02-18 01:53:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=13885s
[2026-02-18 01:53:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=13916s
[2026-02-18 01:54:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=13947s
[2026-02-18 01:54:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=13978s
[2026-02-18 01:55:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=14010s
[2026-02-18 01:55:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=14041s
[2026-02-18 01:56:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=14072s
[2026-02-18 01:56:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=14103s
[2026-02-18 01:57:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=14134s
[2026-02-18 01:57:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=14165s
[2026-02-18 01:58:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=14196s
[2026-02-18 01:58:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=14227s
[2026-02-18 01:59:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=14259s
[2026-02-18 02:00:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=14290s
[2026-02-18 02:00:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=14321s
[2026-02-18 02:01:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=14352s
[2026-02-18 02:01:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=14383s
[2026-02-18 02:02:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=14414s
[2026-02-18 02:02:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=14445s
[2026-02-18 02:03:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=14476s
[2026-02-18 02:03:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=14508s
[2026-02-18 02:04:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=14539s
[2026-02-18 02:04:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=14570s
[2026-02-18 02:05:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=14601s
[2026-02-18 02:05:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=14632s
[2026-02-18 02:06:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=14663s
[2026-02-18 02:06:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=14694s
[2026-02-18 02:07:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=14725s
[2026-02-18 02:07:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=14757s
[2026-02-18 02:08:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=14788s
[2026-02-18 02:08:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=14819s
[2026-02-18 02:09:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=14850s
[2026-02-18 02:09:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=14881s
[2026-02-18 02:10:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=14912s
[2026-02-18 02:10:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=14943s
[2026-02-18 02:11:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=14974s
[2026-02-18 02:11:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=15005s
[2026-02-18 02:12:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=15037s
[2026-02-18 02:12:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=15068s
[2026-02-18 02:13:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=15099s
[2026-02-18 02:14:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=15130s
[2026-02-18 02:14:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=15161s
[2026-02-18 02:15:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=15192s
[2026-02-18 02:15:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=15228s
[2026-02-18 02:16:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=15261s
[2026-02-18 02:16:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=15292s
[2026-02-18 02:17:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=15323s
[2026-02-18 02:17:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=15354s
[2026-02-18 02:18:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=15385s
[2026-02-18 02:18:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=15416s
[2026-02-18 02:19:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=15448s
[2026-02-18 02:19:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=15479s
[2026-02-18 02:20:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=15510s
[2026-02-18 02:20:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=15541s
[2026-02-18 02:21:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=15572s
[2026-02-18 02:21:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=15603s
[2026-02-18 02:22:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=15634s
[2026-02-18 02:22:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=15665s
[2026-02-18 02:23:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=15697s
[2026-02-18 02:23:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=15728s
[2026-02-18 02:24:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=15759s
[2026-02-18 02:25:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=15790s
[2026-02-18 02:25:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=15821s
[2026-02-18 02:26:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=15852s
[2026-02-18 02:26:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=15883s
[2026-02-18 02:27:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=15914s
[2026-02-18 02:27:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=15945s
[2026-02-18 02:28:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=15977s
[2026-02-18 02:28:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=16008s
[2026-02-18 02:29:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=16039s
[2026-02-18 02:29:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=16070s
[2026-02-18 02:30:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=16101s
[2026-02-18 02:30:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=16132s
[2026-02-18 02:31:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=16163s
[2026-02-18 02:31:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=16194s
[2026-02-18 02:32:16]     [Fallback] state=JOB_STATE_RUNNING elapsed=16226s
[2026-02-18 02:32:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=16257s
[2026-02-18 02:33:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=16288s
[2026-02-18 02:33:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=16320s
[2026-02-18 02:34:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=16351s
[2026-02-18 02:34:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=16382s
[2026-02-18 02:35:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=16413s
[2026-02-18 02:35:54]     [Fallback] state=JOB_STATE_RUNNING elapsed=16444s
[2026-02-18 02:36:25]     [Fallback] state=JOB_STATE_RUNNING elapsed=16475s
[2026-02-18 02:36:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=16507s
[2026-02-18 02:37:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=16538s
[2026-02-18 02:37:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=16569s
[2026-02-18 02:38:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=16600s
[2026-02-18 02:39:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=16631s
[2026-02-18 02:39:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=16662s
[2026-02-18 02:40:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=16693s
[2026-02-18 02:40:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=16725s
[2026-02-18 02:41:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=16756s
[2026-02-18 02:41:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=16787s
[2026-02-18 02:42:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=16818s
[2026-02-18 02:42:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=16849s
[2026-02-18 02:43:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=16880s
[2026-02-18 02:43:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=16911s
[2026-02-18 02:44:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=16942s
[2026-02-18 02:44:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=16973s
[2026-02-18 02:45:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=17005s

```

## Tail: autopilot log
```text
[2026-02-18 01:43:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=13294s
[2026-02-18 01:43:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=13325s
[2026-02-18 01:44:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=13356s
[2026-02-18 01:44:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=13387s
[2026-02-18 01:45:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=13418s
[2026-02-18 01:45:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=13449s
[2026-02-18 01:46:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=13480s
[2026-02-18 01:47:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=13511s
[2026-02-18 01:47:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=13543s
[2026-02-18 01:48:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=13574s
[2026-02-18 01:48:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=13605s
[2026-02-18 01:49:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=13636s
[2026-02-18 01:49:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=13667s
[2026-02-18 01:50:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=13698s
[2026-02-18 01:50:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=13729s
[2026-02-18 01:51:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=13760s
[2026-02-18 01:51:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=13792s
[2026-02-18 01:52:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=13823s
[2026-02-18 01:52:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=13854s
[2026-02-18 01:53:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=13885s
[2026-02-18 01:53:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=13916s
[2026-02-18 01:54:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=13947s
[2026-02-18 01:54:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=13978s
[2026-02-18 01:55:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=14010s
[2026-02-18 01:55:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=14041s
[2026-02-18 01:56:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=14072s
[2026-02-18 01:56:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=14103s
[2026-02-18 01:57:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=14134s
[2026-02-18 01:57:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=14165s
[2026-02-18 01:58:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=14196s
[2026-02-18 01:58:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=14227s
[2026-02-18 01:59:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=14259s
[2026-02-18 02:00:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=14290s
[2026-02-18 02:00:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=14321s
[2026-02-18 02:01:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=14352s
[2026-02-18 02:01:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=14383s
[2026-02-18 02:02:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=14414s
[2026-02-18 02:02:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=14445s
[2026-02-18 02:03:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=14476s
[2026-02-18 02:03:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=14508s
[2026-02-18 02:04:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=14539s
[2026-02-18 02:04:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=14570s
[2026-02-18 02:05:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=14601s
[2026-02-18 02:05:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=14632s
[2026-02-18 02:06:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=14663s
[2026-02-18 02:06:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=14694s
[2026-02-18 02:07:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=14725s
[2026-02-18 02:07:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=14757s
[2026-02-18 02:08:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=14788s
[2026-02-18 02:08:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=14819s
[2026-02-18 02:09:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=14850s
[2026-02-18 02:09:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=14881s
[2026-02-18 02:10:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=14912s
[2026-02-18 02:10:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=14943s
[2026-02-18 02:11:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=14974s
[2026-02-18 02:11:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=15005s
[2026-02-18 02:12:27]     [Fallback] state=JOB_STATE_RUNNING elapsed=15037s
[2026-02-18 02:12:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=15068s
[2026-02-18 02:13:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=15099s
[2026-02-18 02:14:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=15130s
[2026-02-18 02:14:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=15161s
[2026-02-18 02:15:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=15192s
[2026-02-18 02:15:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=15228s
[2026-02-18 02:16:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=15261s
[2026-02-18 02:16:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=15292s
[2026-02-18 02:17:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=15323s
[2026-02-18 02:17:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=15354s
[2026-02-18 02:18:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=15385s
[2026-02-18 02:18:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=15416s
[2026-02-18 02:19:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=15448s
[2026-02-18 02:19:49]     [Fallback] state=JOB_STATE_RUNNING elapsed=15479s
[2026-02-18 02:20:20]     [Fallback] state=JOB_STATE_RUNNING elapsed=15510s
[2026-02-18 02:20:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=15541s
[2026-02-18 02:21:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=15572s
[2026-02-18 02:21:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=15603s
[2026-02-18 02:22:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=15634s
[2026-02-18 02:22:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=15665s
[2026-02-18 02:23:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=15697s
[2026-02-18 02:23:58]     [Fallback] state=JOB_STATE_RUNNING elapsed=15728s
[2026-02-18 02:24:29]     [Fallback] state=JOB_STATE_RUNNING elapsed=15759s
[2026-02-18 02:25:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=15790s
[2026-02-18 02:25:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=15821s
[2026-02-18 02:26:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=15852s
[2026-02-18 02:26:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=15883s
[2026-02-18 02:27:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=15914s
[2026-02-18 02:27:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=15945s
[2026-02-18 02:28:07]     [Fallback] state=JOB_STATE_RUNNING elapsed=15977s
[2026-02-18 02:28:38]     [Fallback] state=JOB_STATE_RUNNING elapsed=16008s
[2026-02-18 02:29:09]     [Fallback] state=JOB_STATE_RUNNING elapsed=16039s
[2026-02-18 02:29:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=16070s
[2026-02-18 02:30:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=16101s
[2026-02-18 02:30:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=16132s
[2026-02-18 02:31:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=16163s
[2026-02-18 02:31:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=16194s
[2026-02-18 02:32:16]     [Fallback] state=JOB_STATE_RUNNING elapsed=16226s
[2026-02-18 02:32:47]     [Fallback] state=JOB_STATE_RUNNING elapsed=16257s
[2026-02-18 02:33:18]     [Fallback] state=JOB_STATE_RUNNING elapsed=16288s
[2026-02-18 02:33:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=16320s
[2026-02-18 02:34:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=16351s
[2026-02-18 02:34:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=16382s
[2026-02-18 02:35:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=16413s
[2026-02-18 02:35:54]     [Fallback] state=JOB_STATE_RUNNING elapsed=16444s
[2026-02-18 02:36:25]     [Fallback] state=JOB_STATE_RUNNING elapsed=16475s
[2026-02-18 02:36:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=16507s
[2026-02-18 02:37:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=16538s
[2026-02-18 02:37:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=16569s
[2026-02-18 02:38:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=16600s
[2026-02-18 02:39:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=16631s
[2026-02-18 02:39:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=16662s
[2026-02-18 02:40:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=16693s
[2026-02-18 02:40:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=16725s
[2026-02-18 02:41:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=16756s
[2026-02-18 02:41:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=16787s
[2026-02-18 02:42:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=16818s
[2026-02-18 02:42:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=16849s
[2026-02-18 02:43:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=16880s
[2026-02-18 02:43:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=16911s
[2026-02-18 02:44:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=16942s
[2026-02-18 02:44:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=16973s
[2026-02-18 02:45:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=17005s

```

## Tail: uplink log
```text
[2026-02-18 02:04:36] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 02:04:38] windows1 sync rc=0
[2026-02-18 02:04:38] uplink cycle sleep 300s
[2026-02-18 02:09:38] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 02:09:40] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 02:09:42] windows1 sync rc=0
[2026-02-18 02:09:42] uplink cycle sleep 300s
[2026-02-18 02:14:42] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 02:14:44] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 02:14:46] windows1 sync rc=0
[2026-02-18 02:14:46] uplink cycle sleep 300s
[2026-02-18 02:19:46] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 02:19:48] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 02:19:50] windows1 sync rc=0
[2026-02-18 02:19:50] uplink cycle sleep 300s
[2026-02-18 02:24:50] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 02:24:52] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 02:24:54] windows1 sync rc=0
[2026-02-18 02:24:54] uplink cycle sleep 300s
[2026-02-18 02:29:54] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 02:29:56] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 02:29:58] windows1 sync rc=0
[2026-02-18 02:29:58] uplink cycle sleep 300s
[2026-02-18 02:34:58] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 02:35:00] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 02:35:02] windows1 sync rc=0
[2026-02-18 02:35:02] uplink cycle sleep 300s
[2026-02-18 02:40:02] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 02:40:04] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 02:40:06] windows1 sync rc=0
[2026-02-18 02:40:06] uplink cycle sleep 300s
[2026-02-18 02:45:06] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 02:45:08] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 02:45:10] windows1 sync rc=0
[2026-02-18 02:45:10] uplink cycle sleep 300s

```