# Incident 20260218_071028_autopilot_status_stale
- ts: 2026-02-18 07:10:28
- reason: autopilot_status_stale
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-18 04:58:56",
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
    "updated_at": "2026-02-18 04:58:57"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-18 04:59:04"
    }
  },
  "optimization": {
    "base_matrix_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-205904_aa8abb7/base_matrix.parquet",
    "base_matrix_meta_uri": "gs://omega_v52/staging/base_matrix/v60/20260217-205904_aa8abb7/base_matrix.meta.json",
    "base_matrix_exec_mode": "vertex",
    "base_matrix_machine_type": "n1-highmem-32",
    "base_matrix_spot": false
  },
  "train": {},
  "backtest": {},
  "run_id": "20260217-205904",
  "data_pattern": "gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet"
}
```

## screen -ls
```text
There is a screen on:
	15845.v60_autopilot_aa8abb7	(Detached)
1 Socket in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
15845 SCREEN -dmS v60_autopilot_aa8abb7 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
15846 login -pflq zephryj /bin/bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
15847 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
15850 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh

```

## Tail: autopilot runner log
```text
[2026-02-18 06:08:43]     [Fallback] state=JOB_STATE_PENDING elapsed=4171s
[2026-02-18 06:09:15]     [Fallback] state=JOB_STATE_PENDING elapsed=4202s
[2026-02-18 06:09:46]     [Fallback] state=JOB_STATE_PENDING elapsed=4233s
[2026-02-18 06:10:17]     [Fallback] state=JOB_STATE_PENDING elapsed=4264s
[2026-02-18 06:10:48]     [Fallback] state=JOB_STATE_PENDING elapsed=4295s
[2026-02-18 06:11:19]     [Fallback] state=JOB_STATE_PENDING elapsed=4326s
[2026-02-18 06:11:50]     [Fallback] state=JOB_STATE_PENDING elapsed=4358s
[2026-02-18 06:12:21]     [Fallback] state=JOB_STATE_PENDING elapsed=4389s
[2026-02-18 06:12:52]     [Fallback] state=JOB_STATE_PENDING elapsed=4420s
[2026-02-18 06:13:23]     [Fallback] state=JOB_STATE_PENDING elapsed=4451s
[2026-02-18 06:13:55]     [Fallback] state=JOB_STATE_PENDING elapsed=4482s
[2026-02-18 06:14:26]     [Fallback] state=JOB_STATE_PENDING elapsed=4513s
[2026-02-18 06:14:57]     [Fallback] state=JOB_STATE_PENDING elapsed=4545s
[2026-02-18 06:15:28]     [Fallback] state=JOB_STATE_PENDING elapsed=4576s
[2026-02-18 06:16:00]     [Fallback] state=JOB_STATE_PENDING elapsed=4607s
[2026-02-18 06:16:31]     [Fallback] state=JOB_STATE_PENDING elapsed=4638s
[2026-02-18 06:17:02]     [Fallback] state=JOB_STATE_PENDING elapsed=4669s
[2026-02-18 06:17:33]     [Fallback] state=JOB_STATE_PENDING elapsed=4700s
[2026-02-18 06:18:04]     [Fallback] state=JOB_STATE_PENDING elapsed=4731s
[2026-02-18 06:18:35]     [Fallback] state=JOB_STATE_PENDING elapsed=4763s
[2026-02-18 06:19:06]     [Fallback] state=JOB_STATE_PENDING elapsed=4794s
[2026-02-18 06:19:37]     [Fallback] state=JOB_STATE_PENDING elapsed=4825s
[2026-02-18 06:20:08]     [Fallback] state=JOB_STATE_PENDING elapsed=4856s
[2026-02-18 06:20:40]     [Fallback] state=JOB_STATE_PENDING elapsed=4887s
[2026-02-18 06:21:11]     [Fallback] state=JOB_STATE_PENDING elapsed=4918s
[2026-02-18 06:21:42]     [Fallback] state=JOB_STATE_PENDING elapsed=4949s
[2026-02-18 06:22:13]     [Fallback] state=JOB_STATE_PENDING elapsed=4980s
[2026-02-18 06:22:44]     [Fallback] state=JOB_STATE_PENDING elapsed=5011s
[2026-02-18 06:23:15]     [Fallback] state=JOB_STATE_PENDING elapsed=5043s
[2026-02-18 06:23:46]     [Fallback] state=JOB_STATE_PENDING elapsed=5074s
[2026-02-18 06:24:17]     [Fallback] state=JOB_STATE_PENDING elapsed=5105s
[2026-02-18 06:24:49]     [Fallback] state=JOB_STATE_PENDING elapsed=5136s
[2026-02-18 06:25:20]     [Fallback] state=JOB_STATE_PENDING elapsed=5167s
[2026-02-18 06:25:51]     [Fallback] state=JOB_STATE_PENDING elapsed=5198s
[2026-02-18 06:26:22]     [Fallback] state=JOB_STATE_PENDING elapsed=5229s
[2026-02-18 06:26:53]     [Fallback] state=JOB_STATE_PENDING elapsed=5260s
[2026-02-18 06:27:24]     [Fallback] state=JOB_STATE_PENDING elapsed=5292s
[2026-02-18 06:27:55]     [Fallback] state=JOB_STATE_PENDING elapsed=5323s
[2026-02-18 06:28:26]     [Fallback] state=JOB_STATE_PENDING elapsed=5354s
[2026-02-18 06:28:58]     [Fallback] state=JOB_STATE_PENDING elapsed=5385s
[2026-02-18 06:29:29]     [Fallback] state=JOB_STATE_PENDING elapsed=5416s
[2026-02-18 06:30:00]     [Fallback] state=JOB_STATE_PENDING elapsed=5447s
[2026-02-18 06:30:31]     [Fallback] state=JOB_STATE_PENDING elapsed=5478s
[2026-02-18 06:31:02]     [Fallback] state=JOB_STATE_PENDING elapsed=5509s
[2026-02-18 06:31:33]     [Fallback] state=JOB_STATE_PENDING elapsed=5540s
[2026-02-18 06:32:04]     [Fallback] state=JOB_STATE_PENDING elapsed=5572s
[2026-02-18 06:32:35]     [Fallback] state=JOB_STATE_PENDING elapsed=5603s
[2026-02-18 06:33:06]     [Fallback] state=JOB_STATE_PENDING elapsed=5634s
[2026-02-18 06:33:37]     [Fallback] state=JOB_STATE_PENDING elapsed=5665s
[2026-02-18 06:34:09]     [Fallback] state=JOB_STATE_PENDING elapsed=5696s
[2026-02-18 06:34:40]     [Fallback] state=JOB_STATE_PENDING elapsed=5727s
[2026-02-18 06:35:11]     [Fallback] state=JOB_STATE_PENDING elapsed=5758s
[2026-02-18 06:35:42]     [Fallback] state=JOB_STATE_PENDING elapsed=5789s
[2026-02-18 06:36:13]     [Fallback] state=JOB_STATE_PENDING elapsed=5821s
[2026-02-18 06:36:44]     [Fallback] state=JOB_STATE_PENDING elapsed=5852s
[2026-02-18 06:37:15]     [Fallback] state=JOB_STATE_PENDING elapsed=5883s
[2026-02-18 06:37:46]     [Fallback] state=JOB_STATE_PENDING elapsed=5914s
[2026-02-18 06:38:18]     [Fallback] state=JOB_STATE_PENDING elapsed=5945s
[2026-02-18 06:38:49]     [Fallback] state=JOB_STATE_PENDING elapsed=5976s
[2026-02-18 06:39:20]     [Fallback] state=JOB_STATE_PENDING elapsed=6007s
[2026-02-18 06:39:51]     [Fallback] state=JOB_STATE_PENDING elapsed=6038s
[2026-02-18 06:40:22]     [Fallback] state=JOB_STATE_PENDING elapsed=6069s
[2026-02-18 06:40:53]     [Fallback] state=JOB_STATE_PENDING elapsed=6101s
[2026-02-18 06:41:24]     [Fallback] state=JOB_STATE_PENDING elapsed=6132s
[2026-02-18 06:41:55]     [Fallback] state=JOB_STATE_PENDING elapsed=6163s
[2026-02-18 06:42:27]     [Fallback] state=JOB_STATE_PENDING elapsed=6194s
[2026-02-18 06:42:58]     [Fallback] state=JOB_STATE_PENDING elapsed=6225s
[2026-02-18 06:43:29]     [Fallback] state=JOB_STATE_PENDING elapsed=6256s
[2026-02-18 06:44:00]     [Fallback] state=JOB_STATE_PENDING elapsed=6287s
[2026-02-18 06:44:31]     [Fallback] state=JOB_STATE_PENDING elapsed=6318s
[2026-02-18 06:45:02]     [Fallback] state=JOB_STATE_PENDING elapsed=6350s
[2026-02-18 06:45:33]     [Fallback] state=JOB_STATE_PENDING elapsed=6381s
[2026-02-18 06:46:04]     [Fallback] state=JOB_STATE_PENDING elapsed=6412s
[2026-02-18 06:46:35]     [Fallback] state=JOB_STATE_PENDING elapsed=6443s
[2026-02-18 06:47:07]     [Fallback] state=JOB_STATE_PENDING elapsed=6474s
[2026-02-18 06:47:38]     [Fallback] state=JOB_STATE_PENDING elapsed=6505s
[2026-02-18 06:48:09]     [Fallback] state=JOB_STATE_PENDING elapsed=6536s
[2026-02-18 06:48:40]     [Fallback] state=JOB_STATE_PENDING elapsed=6567s
[2026-02-18 06:49:11]     [Fallback] state=JOB_STATE_PENDING elapsed=6599s
[2026-02-18 06:49:43]     [Fallback] state=JOB_STATE_PENDING elapsed=6630s
[2026-02-18 06:50:14]     [Fallback] state=JOB_STATE_PENDING elapsed=6661s
[2026-02-18 06:50:45]     [Fallback] state=JOB_STATE_PENDING elapsed=6692s
[2026-02-18 06:51:16]     [Fallback] state=JOB_STATE_PENDING elapsed=6723s
[2026-02-18 06:51:47]     [Fallback] state=JOB_STATE_PENDING elapsed=6755s
[2026-02-18 06:52:18]     [Fallback] state=JOB_STATE_PENDING elapsed=6786s
[2026-02-18 06:52:49]     [Fallback] state=JOB_STATE_PENDING elapsed=6817s
[2026-02-18 06:53:20]     [Fallback] state=JOB_STATE_PENDING elapsed=6848s
[2026-02-18 06:53:52]     [Fallback] state=JOB_STATE_PENDING elapsed=6879s
[2026-02-18 06:54:23]     [Fallback] state=JOB_STATE_PENDING elapsed=6910s
[2026-02-18 06:54:54]     [Fallback] state=JOB_STATE_PENDING elapsed=6941s
[2026-02-18 06:55:25]     [Fallback] state=JOB_STATE_PENDING elapsed=6972s
[2026-02-18 06:55:56]     [Fallback] state=JOB_STATE_PENDING elapsed=7003s
[2026-02-18 06:56:27]     [Fallback] state=JOB_STATE_PENDING elapsed=7035s
[2026-02-18 06:56:58]     [Fallback] state=JOB_STATE_PENDING elapsed=7066s
[2026-02-18 06:57:29]     [Fallback] state=JOB_STATE_PENDING elapsed=7097s
[2026-02-18 06:58:00]     [Fallback] state=JOB_STATE_PENDING elapsed=7128s
[2026-02-18 06:58:32]     [Fallback] state=JOB_STATE_PENDING elapsed=7159s
[2026-02-18 06:59:03]     [Fallback] state=JOB_STATE_PENDING elapsed=7190s
[2026-02-18 06:59:34]     [Fallback] state=JOB_STATE_PENDING elapsed=7221s
[2026-02-18 07:00:05]     [Fallback] state=JOB_STATE_PENDING elapsed=7252s
[2026-02-18 07:00:36]     [Fallback] state=JOB_STATE_PENDING elapsed=7284s
[2026-02-18 07:01:07]     [Fallback] state=JOB_STATE_PENDING elapsed=7315s
[2026-02-18 07:01:38]     [Fallback] state=JOB_STATE_PENDING elapsed=7346s
[2026-02-18 07:02:09]     [Fallback] state=JOB_STATE_PENDING elapsed=7377s
[2026-02-18 07:02:41]     [Fallback] state=JOB_STATE_PENDING elapsed=7408s
[2026-02-18 07:03:12]     [Fallback] state=JOB_STATE_PENDING elapsed=7439s
[2026-02-18 07:03:43]     [Fallback] state=JOB_STATE_PENDING elapsed=7470s
[2026-02-18 07:04:14]     [Fallback] state=JOB_STATE_PENDING elapsed=7501s
[2026-02-18 07:04:45]     [Fallback] state=JOB_STATE_PENDING elapsed=7532s
[2026-02-18 07:05:16]     [Fallback] state=JOB_STATE_PENDING elapsed=7564s
[2026-02-18 07:05:47]     [Fallback] state=JOB_STATE_PENDING elapsed=7595s
[2026-02-18 07:06:18]     [Fallback] state=JOB_STATE_PENDING elapsed=7626s
[2026-02-18 07:06:49]     [Fallback] state=JOB_STATE_PENDING elapsed=7657s
[2026-02-18 07:07:21]     [Fallback] state=JOB_STATE_PENDING elapsed=7688s
[2026-02-18 07:07:52]     [Fallback] state=JOB_STATE_PENDING elapsed=7719s
[2026-02-18 07:08:23]     [Fallback] state=JOB_STATE_PENDING elapsed=7750s
[2026-02-18 07:08:54]     [Fallback] state=JOB_STATE_PENDING elapsed=7781s
[2026-02-18 07:09:25]     [Fallback] state=JOB_STATE_PENDING elapsed=7812s
[2026-02-18 07:09:57]     [Fallback] state=JOB_STATE_PENDING elapsed=7844s
[2026-02-18 07:10:28]     [Fallback] state=JOB_STATE_PENDING elapsed=7875s

```

## Tail: autopilot log
```text
[2026-02-18 06:08:43]     [Fallback] state=JOB_STATE_PENDING elapsed=4171s
[2026-02-18 06:09:15]     [Fallback] state=JOB_STATE_PENDING elapsed=4202s
[2026-02-18 06:09:46]     [Fallback] state=JOB_STATE_PENDING elapsed=4233s
[2026-02-18 06:10:17]     [Fallback] state=JOB_STATE_PENDING elapsed=4264s
[2026-02-18 06:10:48]     [Fallback] state=JOB_STATE_PENDING elapsed=4295s
[2026-02-18 06:11:19]     [Fallback] state=JOB_STATE_PENDING elapsed=4326s
[2026-02-18 06:11:50]     [Fallback] state=JOB_STATE_PENDING elapsed=4358s
[2026-02-18 06:12:21]     [Fallback] state=JOB_STATE_PENDING elapsed=4389s
[2026-02-18 06:12:52]     [Fallback] state=JOB_STATE_PENDING elapsed=4420s
[2026-02-18 06:13:23]     [Fallback] state=JOB_STATE_PENDING elapsed=4451s
[2026-02-18 06:13:55]     [Fallback] state=JOB_STATE_PENDING elapsed=4482s
[2026-02-18 06:14:26]     [Fallback] state=JOB_STATE_PENDING elapsed=4513s
[2026-02-18 06:14:57]     [Fallback] state=JOB_STATE_PENDING elapsed=4545s
[2026-02-18 06:15:28]     [Fallback] state=JOB_STATE_PENDING elapsed=4576s
[2026-02-18 06:16:00]     [Fallback] state=JOB_STATE_PENDING elapsed=4607s
[2026-02-18 06:16:31]     [Fallback] state=JOB_STATE_PENDING elapsed=4638s
[2026-02-18 06:17:02]     [Fallback] state=JOB_STATE_PENDING elapsed=4669s
[2026-02-18 06:17:33]     [Fallback] state=JOB_STATE_PENDING elapsed=4700s
[2026-02-18 06:18:04]     [Fallback] state=JOB_STATE_PENDING elapsed=4731s
[2026-02-18 06:18:35]     [Fallback] state=JOB_STATE_PENDING elapsed=4763s
[2026-02-18 06:19:06]     [Fallback] state=JOB_STATE_PENDING elapsed=4794s
[2026-02-18 06:19:37]     [Fallback] state=JOB_STATE_PENDING elapsed=4825s
[2026-02-18 06:20:08]     [Fallback] state=JOB_STATE_PENDING elapsed=4856s
[2026-02-18 06:20:40]     [Fallback] state=JOB_STATE_PENDING elapsed=4887s
[2026-02-18 06:21:11]     [Fallback] state=JOB_STATE_PENDING elapsed=4918s
[2026-02-18 06:21:42]     [Fallback] state=JOB_STATE_PENDING elapsed=4949s
[2026-02-18 06:22:13]     [Fallback] state=JOB_STATE_PENDING elapsed=4980s
[2026-02-18 06:22:44]     [Fallback] state=JOB_STATE_PENDING elapsed=5011s
[2026-02-18 06:23:15]     [Fallback] state=JOB_STATE_PENDING elapsed=5043s
[2026-02-18 06:23:46]     [Fallback] state=JOB_STATE_PENDING elapsed=5074s
[2026-02-18 06:24:17]     [Fallback] state=JOB_STATE_PENDING elapsed=5105s
[2026-02-18 06:24:49]     [Fallback] state=JOB_STATE_PENDING elapsed=5136s
[2026-02-18 06:25:20]     [Fallback] state=JOB_STATE_PENDING elapsed=5167s
[2026-02-18 06:25:51]     [Fallback] state=JOB_STATE_PENDING elapsed=5198s
[2026-02-18 06:26:22]     [Fallback] state=JOB_STATE_PENDING elapsed=5229s
[2026-02-18 06:26:53]     [Fallback] state=JOB_STATE_PENDING elapsed=5260s
[2026-02-18 06:27:24]     [Fallback] state=JOB_STATE_PENDING elapsed=5292s
[2026-02-18 06:27:55]     [Fallback] state=JOB_STATE_PENDING elapsed=5323s
[2026-02-18 06:28:26]     [Fallback] state=JOB_STATE_PENDING elapsed=5354s
[2026-02-18 06:28:58]     [Fallback] state=JOB_STATE_PENDING elapsed=5385s
[2026-02-18 06:29:29]     [Fallback] state=JOB_STATE_PENDING elapsed=5416s
[2026-02-18 06:30:00]     [Fallback] state=JOB_STATE_PENDING elapsed=5447s
[2026-02-18 06:30:31]     [Fallback] state=JOB_STATE_PENDING elapsed=5478s
[2026-02-18 06:31:02]     [Fallback] state=JOB_STATE_PENDING elapsed=5509s
[2026-02-18 06:31:33]     [Fallback] state=JOB_STATE_PENDING elapsed=5540s
[2026-02-18 06:32:04]     [Fallback] state=JOB_STATE_PENDING elapsed=5572s
[2026-02-18 06:32:35]     [Fallback] state=JOB_STATE_PENDING elapsed=5603s
[2026-02-18 06:33:06]     [Fallback] state=JOB_STATE_PENDING elapsed=5634s
[2026-02-18 06:33:37]     [Fallback] state=JOB_STATE_PENDING elapsed=5665s
[2026-02-18 06:34:09]     [Fallback] state=JOB_STATE_PENDING elapsed=5696s
[2026-02-18 06:34:40]     [Fallback] state=JOB_STATE_PENDING elapsed=5727s
[2026-02-18 06:35:11]     [Fallback] state=JOB_STATE_PENDING elapsed=5758s
[2026-02-18 06:35:42]     [Fallback] state=JOB_STATE_PENDING elapsed=5789s
[2026-02-18 06:36:13]     [Fallback] state=JOB_STATE_PENDING elapsed=5821s
[2026-02-18 06:36:44]     [Fallback] state=JOB_STATE_PENDING elapsed=5852s
[2026-02-18 06:37:15]     [Fallback] state=JOB_STATE_PENDING elapsed=5883s
[2026-02-18 06:37:46]     [Fallback] state=JOB_STATE_PENDING elapsed=5914s
[2026-02-18 06:38:18]     [Fallback] state=JOB_STATE_PENDING elapsed=5945s
[2026-02-18 06:38:49]     [Fallback] state=JOB_STATE_PENDING elapsed=5976s
[2026-02-18 06:39:20]     [Fallback] state=JOB_STATE_PENDING elapsed=6007s
[2026-02-18 06:39:51]     [Fallback] state=JOB_STATE_PENDING elapsed=6038s
[2026-02-18 06:40:22]     [Fallback] state=JOB_STATE_PENDING elapsed=6069s
[2026-02-18 06:40:53]     [Fallback] state=JOB_STATE_PENDING elapsed=6101s
[2026-02-18 06:41:24]     [Fallback] state=JOB_STATE_PENDING elapsed=6132s
[2026-02-18 06:41:55]     [Fallback] state=JOB_STATE_PENDING elapsed=6163s
[2026-02-18 06:42:27]     [Fallback] state=JOB_STATE_PENDING elapsed=6194s
[2026-02-18 06:42:58]     [Fallback] state=JOB_STATE_PENDING elapsed=6225s
[2026-02-18 06:43:29]     [Fallback] state=JOB_STATE_PENDING elapsed=6256s
[2026-02-18 06:44:00]     [Fallback] state=JOB_STATE_PENDING elapsed=6287s
[2026-02-18 06:44:31]     [Fallback] state=JOB_STATE_PENDING elapsed=6318s
[2026-02-18 06:45:02]     [Fallback] state=JOB_STATE_PENDING elapsed=6350s
[2026-02-18 06:45:33]     [Fallback] state=JOB_STATE_PENDING elapsed=6381s
[2026-02-18 06:46:04]     [Fallback] state=JOB_STATE_PENDING elapsed=6412s
[2026-02-18 06:46:35]     [Fallback] state=JOB_STATE_PENDING elapsed=6443s
[2026-02-18 06:47:07]     [Fallback] state=JOB_STATE_PENDING elapsed=6474s
[2026-02-18 06:47:38]     [Fallback] state=JOB_STATE_PENDING elapsed=6505s
[2026-02-18 06:48:09]     [Fallback] state=JOB_STATE_PENDING elapsed=6536s
[2026-02-18 06:48:40]     [Fallback] state=JOB_STATE_PENDING elapsed=6567s
[2026-02-18 06:49:11]     [Fallback] state=JOB_STATE_PENDING elapsed=6599s
[2026-02-18 06:49:43]     [Fallback] state=JOB_STATE_PENDING elapsed=6630s
[2026-02-18 06:50:14]     [Fallback] state=JOB_STATE_PENDING elapsed=6661s
[2026-02-18 06:50:45]     [Fallback] state=JOB_STATE_PENDING elapsed=6692s
[2026-02-18 06:51:16]     [Fallback] state=JOB_STATE_PENDING elapsed=6723s
[2026-02-18 06:51:47]     [Fallback] state=JOB_STATE_PENDING elapsed=6755s
[2026-02-18 06:52:18]     [Fallback] state=JOB_STATE_PENDING elapsed=6786s
[2026-02-18 06:52:49]     [Fallback] state=JOB_STATE_PENDING elapsed=6817s
[2026-02-18 06:53:20]     [Fallback] state=JOB_STATE_PENDING elapsed=6848s
[2026-02-18 06:53:52]     [Fallback] state=JOB_STATE_PENDING elapsed=6879s
[2026-02-18 06:54:23]     [Fallback] state=JOB_STATE_PENDING elapsed=6910s
[2026-02-18 06:54:54]     [Fallback] state=JOB_STATE_PENDING elapsed=6941s
[2026-02-18 06:55:25]     [Fallback] state=JOB_STATE_PENDING elapsed=6972s
[2026-02-18 06:55:56]     [Fallback] state=JOB_STATE_PENDING elapsed=7003s
[2026-02-18 06:56:27]     [Fallback] state=JOB_STATE_PENDING elapsed=7035s
[2026-02-18 06:56:58]     [Fallback] state=JOB_STATE_PENDING elapsed=7066s
[2026-02-18 06:57:29]     [Fallback] state=JOB_STATE_PENDING elapsed=7097s
[2026-02-18 06:58:00]     [Fallback] state=JOB_STATE_PENDING elapsed=7128s
[2026-02-18 06:58:32]     [Fallback] state=JOB_STATE_PENDING elapsed=7159s
[2026-02-18 06:59:03]     [Fallback] state=JOB_STATE_PENDING elapsed=7190s
[2026-02-18 06:59:34]     [Fallback] state=JOB_STATE_PENDING elapsed=7221s
[2026-02-18 07:00:05]     [Fallback] state=JOB_STATE_PENDING elapsed=7252s
[2026-02-18 07:00:36]     [Fallback] state=JOB_STATE_PENDING elapsed=7284s
[2026-02-18 07:01:07]     [Fallback] state=JOB_STATE_PENDING elapsed=7315s
[2026-02-18 07:01:38]     [Fallback] state=JOB_STATE_PENDING elapsed=7346s
[2026-02-18 07:02:09]     [Fallback] state=JOB_STATE_PENDING elapsed=7377s
[2026-02-18 07:02:41]     [Fallback] state=JOB_STATE_PENDING elapsed=7408s
[2026-02-18 07:03:12]     [Fallback] state=JOB_STATE_PENDING elapsed=7439s
[2026-02-18 07:03:43]     [Fallback] state=JOB_STATE_PENDING elapsed=7470s
[2026-02-18 07:04:14]     [Fallback] state=JOB_STATE_PENDING elapsed=7501s
[2026-02-18 07:04:45]     [Fallback] state=JOB_STATE_PENDING elapsed=7532s
[2026-02-18 07:05:16]     [Fallback] state=JOB_STATE_PENDING elapsed=7564s
[2026-02-18 07:05:47]     [Fallback] state=JOB_STATE_PENDING elapsed=7595s
[2026-02-18 07:06:18]     [Fallback] state=JOB_STATE_PENDING elapsed=7626s
[2026-02-18 07:06:49]     [Fallback] state=JOB_STATE_PENDING elapsed=7657s
[2026-02-18 07:07:21]     [Fallback] state=JOB_STATE_PENDING elapsed=7688s
[2026-02-18 07:07:52]     [Fallback] state=JOB_STATE_PENDING elapsed=7719s
[2026-02-18 07:08:23]     [Fallback] state=JOB_STATE_PENDING elapsed=7750s
[2026-02-18 07:08:54]     [Fallback] state=JOB_STATE_PENDING elapsed=7781s
[2026-02-18 07:09:25]     [Fallback] state=JOB_STATE_PENDING elapsed=7812s
[2026-02-18 07:09:57]     [Fallback] state=JOB_STATE_PENDING elapsed=7844s
[2026-02-18 07:10:28]     [Fallback] state=JOB_STATE_PENDING elapsed=7875s

```

## Tail: uplink log
```text
[2026-02-18 06:27:56] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 06:27:58] windows1 sync rc=0
[2026-02-18 06:27:58] uplink cycle sleep 300s
[2026-02-18 06:32:58] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 06:33:00] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 06:33:02] windows1 sync rc=0
[2026-02-18 06:33:02] uplink cycle sleep 300s
[2026-02-18 06:38:02] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 06:38:04] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 06:38:06] windows1 sync rc=0
[2026-02-18 06:38:06] uplink cycle sleep 300s
[2026-02-18 06:43:06] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 06:43:08] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 06:43:10] windows1 sync rc=0
[2026-02-18 06:43:10] uplink cycle sleep 300s
[2026-02-18 06:48:10] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 06:48:12] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 06:48:14] windows1 sync rc=0
[2026-02-18 06:48:14] uplink cycle sleep 300s
[2026-02-18 06:53:14] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 06:53:16] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 06:53:19] windows1 sync rc=0
[2026-02-18 06:53:19] uplink cycle sleep 300s
[2026-02-18 06:58:19] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 06:58:21] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 06:58:23] windows1 sync rc=0
[2026-02-18 06:58:23] uplink cycle sleep 300s
[2026-02-18 07:03:23] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 07:03:25] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 07:03:26] windows1 sync rc=0
[2026-02-18 07:03:26] uplink cycle sleep 300s
[2026-02-18 07:08:26] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 07:08:29] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 07:08:30] windows1 sync rc=0
[2026-02-18 07:08:30] uplink cycle sleep 300s

```