# Incident 20260218_040327_runner_error_Traceback
- ts: 2026-02-18 04:03:27
- reason: runner_error_Traceback
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
[2026-02-18 03:08:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=18405s
[2026-02-18 03:09:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=18436s
[2026-02-18 03:09:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=18467s
[2026-02-18 03:10:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=18498s
[2026-02-18 03:10:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=18529s
[2026-02-18 03:11:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=18560s
[2026-02-18 03:11:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=18591s
[2026-02-18 03:12:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=18622s
[2026-02-18 03:12:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=18653s
[2026-02-18 03:13:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=18685s
[2026-02-18 03:13:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=18716s
[2026-02-18 03:14:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=18747s
[2026-02-18 03:14:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=18778s
[2026-02-18 03:15:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=18809s
[2026-02-18 03:15:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=18840s
[2026-02-18 03:16:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=18871s
[2026-02-18 03:16:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=18902s
[2026-02-18 03:17:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=18933s
[2026-02-18 03:17:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=18965s
[2026-02-18 03:18:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=18996s
[2026-02-18 03:18:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=19027s
[2026-02-18 03:19:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=19058s
[2026-02-18 03:19:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=19089s
[2026-02-18 03:20:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=19120s
[2026-02-18 03:21:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=19151s
[2026-02-18 03:21:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=19182s
[2026-02-18 03:22:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=19213s
[2026-02-18 03:22:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=19245s
[2026-02-18 03:23:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=19276s
[2026-02-18 03:23:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=19307s
[2026-02-18 03:24:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=19338s
[2026-02-18 03:24:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=19369s
[2026-02-18 03:25:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=19400s
[2026-02-18 03:25:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=19431s
[2026-02-18 03:26:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=19462s
[2026-02-18 03:26:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=19493s
[2026-02-18 03:27:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=19524s
[2026-02-18 03:27:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=19556s
[2026-02-18 03:28:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=19587s
[2026-02-18 03:28:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=19618s
[2026-02-18 03:29:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=19650s
[2026-02-18 03:29:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=19681s
[2026-02-18 03:30:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=19712s
[2026-02-18 03:30:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=19743s
[2026-02-18 03:31:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=19774s
[2026-02-18 03:31:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=19805s
[2026-02-18 03:32:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=19836s
[2026-02-18 03:32:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=19867s
[2026-02-18 03:33:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=19898s
[2026-02-18 03:34:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=19930s
[2026-02-18 03:34:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=19961s
[2026-02-18 03:35:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=19992s
[2026-02-18 03:35:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=20023s
[2026-02-18 03:36:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=20054s
[2026-02-18 03:36:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=20085s
[2026-02-18 03:37:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=20116s
[2026-02-18 03:37:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=20147s
[2026-02-18 03:38:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=20179s
[2026-02-18 03:38:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=20210s
[2026-02-18 03:39:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=20241s
[2026-02-18 03:39:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=20272s
[2026-02-18 03:40:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=20303s
[2026-02-18 03:40:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=20334s
[2026-02-18 03:41:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=20365s
[2026-02-18 03:41:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=20396s
[2026-02-18 03:42:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=20427s
[2026-02-18 03:42:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=20459s
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
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 899, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 661, in main
    run_stream(build_cmd, log)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 68, in run_stream
    raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
RuntimeError: Command failed (1): /Library/Developer/CommandLineTools/usr/bin/python3 tools/submit_vertex_sweep.py --script tools/run_vertex_base_matrix.py --machine-type n1-highmem-32 --sync --sync-timeout-sec=21600 --force-gcloud-fallback --script-arg=--input-pattern=gs://omega_v52/omega/v52/frames/host=*/*_aa8abb7.parquet --script-arg=--years=2023,2024 --script-arg=--hash=aa8abb7 --script-arg=--peace-threshold=0.1 --script-arg=--srl-resid-sigma-mult=0.5 --script-arg=--seed=42 --script-arg=--output-local=/tmp/base_matrix.parquet --script-arg=--output-meta-local=/tmp/base_matrix.parquet.meta.json --script-arg=--output-uri=gs://omega_v52/staging/base_matrix/v60/20260217-140142_aa8abb7/base_matrix.parquet --script-arg=--output-meta-uri=gs://omega_v52/staging/base_matrix/v60/20260217-140142_aa8abb7/base_matrix.meta.json --script-arg=--chunk-days=5

```

## Tail: autopilot log
```text
[2026-02-18 03:04:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=18156s
[2026-02-18 03:04:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=18187s
[2026-02-18 03:05:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=18218s
[2026-02-18 03:05:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=18249s
[2026-02-18 03:06:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=18280s
[2026-02-18 03:07:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=18311s
[2026-02-18 03:07:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=18343s
[2026-02-18 03:08:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=18374s
[2026-02-18 03:08:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=18405s
[2026-02-18 03:09:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=18436s
[2026-02-18 03:09:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=18467s
[2026-02-18 03:10:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=18498s
[2026-02-18 03:10:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=18529s
[2026-02-18 03:11:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=18560s
[2026-02-18 03:11:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=18591s
[2026-02-18 03:12:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=18622s
[2026-02-18 03:12:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=18653s
[2026-02-18 03:13:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=18685s
[2026-02-18 03:13:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=18716s
[2026-02-18 03:14:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=18747s
[2026-02-18 03:14:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=18778s
[2026-02-18 03:15:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=18809s
[2026-02-18 03:15:50]     [Fallback] state=JOB_STATE_RUNNING elapsed=18840s
[2026-02-18 03:16:21]     [Fallback] state=JOB_STATE_RUNNING elapsed=18871s
[2026-02-18 03:16:52]     [Fallback] state=JOB_STATE_RUNNING elapsed=18902s
[2026-02-18 03:17:23]     [Fallback] state=JOB_STATE_RUNNING elapsed=18933s
[2026-02-18 03:17:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=18965s
[2026-02-18 03:18:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=18996s
[2026-02-18 03:18:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=19027s
[2026-02-18 03:19:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=19058s
[2026-02-18 03:19:59]     [Fallback] state=JOB_STATE_RUNNING elapsed=19089s
[2026-02-18 03:20:30]     [Fallback] state=JOB_STATE_RUNNING elapsed=19120s
[2026-02-18 03:21:01]     [Fallback] state=JOB_STATE_RUNNING elapsed=19151s
[2026-02-18 03:21:32]     [Fallback] state=JOB_STATE_RUNNING elapsed=19182s
[2026-02-18 03:22:03]     [Fallback] state=JOB_STATE_RUNNING elapsed=19213s
[2026-02-18 03:22:34]     [Fallback] state=JOB_STATE_RUNNING elapsed=19245s
[2026-02-18 03:23:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=19276s
[2026-02-18 03:23:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=19307s
[2026-02-18 03:24:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=19338s
[2026-02-18 03:24:39]     [Fallback] state=JOB_STATE_RUNNING elapsed=19369s
[2026-02-18 03:25:10]     [Fallback] state=JOB_STATE_RUNNING elapsed=19400s
[2026-02-18 03:25:41]     [Fallback] state=JOB_STATE_RUNNING elapsed=19431s
[2026-02-18 03:26:12]     [Fallback] state=JOB_STATE_RUNNING elapsed=19462s
[2026-02-18 03:26:43]     [Fallback] state=JOB_STATE_RUNNING elapsed=19493s
[2026-02-18 03:27:14]     [Fallback] state=JOB_STATE_RUNNING elapsed=19524s
[2026-02-18 03:27:45]     [Fallback] state=JOB_STATE_RUNNING elapsed=19556s
[2026-02-18 03:28:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=19587s
[2026-02-18 03:28:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=19618s
[2026-02-18 03:29:19]     [Fallback] state=JOB_STATE_RUNNING elapsed=19650s
[2026-02-18 03:29:51]     [Fallback] state=JOB_STATE_RUNNING elapsed=19681s
[2026-02-18 03:30:22]     [Fallback] state=JOB_STATE_RUNNING elapsed=19712s
[2026-02-18 03:30:53]     [Fallback] state=JOB_STATE_RUNNING elapsed=19743s
[2026-02-18 03:31:24]     [Fallback] state=JOB_STATE_RUNNING elapsed=19774s
[2026-02-18 03:31:55]     [Fallback] state=JOB_STATE_RUNNING elapsed=19805s
[2026-02-18 03:32:26]     [Fallback] state=JOB_STATE_RUNNING elapsed=19836s
[2026-02-18 03:32:57]     [Fallback] state=JOB_STATE_RUNNING elapsed=19867s
[2026-02-18 03:33:28]     [Fallback] state=JOB_STATE_RUNNING elapsed=19898s
[2026-02-18 03:34:00]     [Fallback] state=JOB_STATE_RUNNING elapsed=19930s
[2026-02-18 03:34:31]     [Fallback] state=JOB_STATE_RUNNING elapsed=19961s
[2026-02-18 03:35:02]     [Fallback] state=JOB_STATE_RUNNING elapsed=19992s
[2026-02-18 03:35:33]     [Fallback] state=JOB_STATE_RUNNING elapsed=20023s
[2026-02-18 03:36:04]     [Fallback] state=JOB_STATE_RUNNING elapsed=20054s
[2026-02-18 03:36:35]     [Fallback] state=JOB_STATE_RUNNING elapsed=20085s
[2026-02-18 03:37:06]     [Fallback] state=JOB_STATE_RUNNING elapsed=20116s
[2026-02-18 03:37:37]     [Fallback] state=JOB_STATE_RUNNING elapsed=20147s
[2026-02-18 03:38:08]     [Fallback] state=JOB_STATE_RUNNING elapsed=20179s
[2026-02-18 03:38:40]     [Fallback] state=JOB_STATE_RUNNING elapsed=20210s
[2026-02-18 03:39:11]     [Fallback] state=JOB_STATE_RUNNING elapsed=20241s
[2026-02-18 03:39:42]     [Fallback] state=JOB_STATE_RUNNING elapsed=20272s
[2026-02-18 03:40:13]     [Fallback] state=JOB_STATE_RUNNING elapsed=20303s
[2026-02-18 03:40:44]     [Fallback] state=JOB_STATE_RUNNING elapsed=20334s
[2026-02-18 03:41:15]     [Fallback] state=JOB_STATE_RUNNING elapsed=20365s
[2026-02-18 03:41:46]     [Fallback] state=JOB_STATE_RUNNING elapsed=20396s
[2026-02-18 03:42:17]     [Fallback] state=JOB_STATE_RUNNING elapsed=20427s
[2026-02-18 03:42:48]     [Fallback] state=JOB_STATE_RUNNING elapsed=20459s
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

```

## Tail: uplink log
```text
[2026-02-18 03:20:35] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 03:20:37] windows1 sync rc=0
[2026-02-18 03:20:37] uplink cycle sleep 300s
[2026-02-18 03:25:37] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 03:25:39] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 03:25:41] windows1 sync rc=0
[2026-02-18 03:25:41] uplink cycle sleep 300s
[2026-02-18 03:30:41] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 03:30:43] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 03:30:45] windows1 sync rc=0
[2026-02-18 03:30:45] uplink cycle sleep 300s
[2026-02-18 03:35:45] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 03:35:47] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 03:35:49] windows1 sync rc=0
[2026-02-18 03:35:49] uplink cycle sleep 300s
[2026-02-18 03:40:49] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 03:40:51] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 03:40:53] windows1 sync rc=0
[2026-02-18 03:40:53] uplink cycle sleep 300s
[2026-02-18 03:45:53] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 03:45:55] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 03:45:57] windows1 sync rc=0
[2026-02-18 03:45:57] uplink cycle sleep 300s
[2026-02-18 03:50:57] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 03:50:59] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 03:51:01] windows1 sync rc=0
[2026-02-18 03:51:01] uplink cycle sleep 300s
[2026-02-18 03:56:01] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 03:56:03] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 03:56:05] windows1 sync rc=0
[2026-02-18 03:56:05] uplink cycle sleep 300s
[2026-02-18 04:01:05] uplink cycle begin
[*] Using frame hash filter: aa8abb7
=== Starting Sync for linux1 ===
[*] Scanning zepher@192.168.3.113:/omega_pool/parquet_data/v52/frames/host=linux1/ for completed frames (hash: aa8abb7)...
    Found 484 candidate frames.
    Skipping 484 already in GCS.
[2026-02-18 04:01:07] linux1 sync rc=0
[*] Using frame hash filter: aa8abb7
=== Starting Sync for windows1 ===
[*] Scanning jiazi@192.168.3.112:D:/Omega_frames/v52/frames/host=windows1/ for completed frames (hash: aa8abb7)...
    Found 263 candidate frames.
    Skipping 263 already in GCS.
[2026-02-18 04:01:09] windows1 sync rc=0
[2026-02-18 04:01:09] uplink cycle sleep 300s

```