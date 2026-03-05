# Incident 20260217_121232_runner_error_Traceback
- ts: 2026-02-17 12:12:33
- reason: runner_error_Traceback
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-17 12:07:06",
  "git_hash": "aa8abb7",
  "bucket": "gs://omega_v52",
  "windows_expected": 250,
  "linux_expected": 497,
  "stage": "monitor_frame",
  "frame": {
    "linux_done": 413,
    "windows_done": 250,
    "windows_task_state": "Ready",
    "probe_linux": 413,
    "probe_windows": 250,
    "probe_ok": true,
    "updated_at": "2026-02-17 12:10:09"
  },
  "upload": {},
  "train": {},
  "backtest": {}
}
```

## screen -ls
```text
There are screens on:
	66268.v60_autopilot_aa8abb7	(Detached)
	38895.v60_uplink_aa8abb7	(Detached)
2 Sockets in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
38895 SCREEN -dmS v60_uplink_aa8abb7 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh
60241 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -u tools/mac_gateway_sync.py --bucket gs://omega_v52 --host windows1 --hash aa8abb7
66268 SCREEN -dmS v60_autopilot_aa8abb7 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
66270 login -pflq zephryj /bin/bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
66271 bash -lc cd /Users/zephryj/work/Omega_vNext && PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
66274 /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -u tools/v60_autopilot.py --hash aa8abb7 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800

```

## Tail: autopilot runner log
```text
[2026-02-17 07:20:04] Frame progress linux=217/500 windows=134/251 task=Running
[2026-02-17 07:22:06] Frame progress linux=219/500 windows=135/251 task=Running
[2026-02-17 07:24:08] Frame progress linux=221/500 windows=136/251 task=Running
[2026-02-17 07:26:09] Frame progress linux=222/500 windows=137/251 task=Running
[2026-02-17 07:28:11] Frame progress linux=224/500 windows=138/251 task=Running
[2026-02-17 07:30:13] Frame progress linux=225/500 windows=139/251 task=Running
[2026-02-17 07:32:14] Frame progress linux=227/500 windows=140/251 task=Running
[2026-02-17 07:34:16] Frame progress linux=228/500 windows=141/251 task=Running
[2026-02-17 07:36:18] Frame progress linux=230/500 windows=142/251 task=Running
[2026-02-17 07:38:20] Frame progress linux=231/500 windows=143/251 task=Running
[2026-02-17 07:40:21] Frame progress linux=233/500 windows=144/251 task=Running
[2026-02-17 07:42:23] Frame progress linux=234/500 windows=145/251 task=Running
[2026-02-17 07:44:24] Frame progress linux=236/500 windows=145/251 task=Running
[2026-02-17 07:46:26] Frame progress linux=238/500 windows=146/251 task=Running
[2026-02-17 07:48:28] Frame progress linux=239/500 windows=147/251 task=Running
[2026-02-17 07:50:30] Frame progress linux=241/500 windows=148/251 task=Running
[2026-02-17 07:52:31] Frame progress linux=242/500 windows=149/251 task=Running
[2026-02-17 07:54:33] Frame progress linux=244/500 windows=150/251 task=Running
[2026-02-17 07:56:34] Frame progress linux=246/500 windows=151/251 task=Running
[2026-02-17 07:58:36] Frame progress linux=247/500 windows=151/251 task=Running
[2026-02-17 08:00:38] Frame progress linux=249/500 windows=152/251 task=Running
[2026-02-17 08:02:39] Frame progress linux=251/500 windows=153/251 task=Running
[2026-02-17 08:04:41] Frame progress linux=252/500 windows=154/251 task=Running
[2026-02-17 08:06:43] Frame progress linux=254/500 windows=155/251 task=Running
[2026-02-17 08:08:44] Frame progress linux=255/500 windows=156/251 task=Running
[2026-02-17 08:10:46] Frame progress linux=257/500 windows=157/251 task=Running
[2026-02-17 08:12:48] Frame progress linux=259/500 windows=157/251 task=Running
[2026-02-17 08:14:49] Frame progress linux=260/500 windows=158/251 task=Running
[2026-02-17 08:16:51] Frame progress linux=262/500 windows=159/251 task=Running
[2026-02-17 08:18:53] Frame progress linux=264/500 windows=160/251 task=Running
[2026-02-17 08:20:55] Frame progress linux=265/500 windows=161/251 task=Running
[2026-02-17 08:22:56] Frame progress linux=267/500 windows=162/251 task=Running
[2026-02-17 08:24:58] Frame progress linux=269/500 windows=163/251 task=Running
[2026-02-17 08:26:59] Frame progress linux=270/500 windows=164/251 task=Running
[2026-02-17 08:29:00] Frame progress linux=272/500 windows=165/251 task=Running
[2026-02-17 08:31:02] Frame progress linux=274/500 windows=165/251 task=Running
[2026-02-17 08:33:04] Frame progress linux=275/500 windows=166/251 task=Running
[2026-02-17 08:35:06] Frame progress linux=277/500 windows=167/251 task=Running
[2026-02-17 08:37:08] Frame progress linux=278/500 windows=168/251 task=Running
[2026-02-17 08:39:09] Frame progress linux=279/500 windows=169/251 task=Running
[2026-02-17 08:41:11] Frame progress linux=280/500 windows=170/251 task=Running
[2026-02-17 08:43:13] Frame progress linux=281/500 windows=171/251 task=Running
[2026-02-17 08:45:14] Frame progress linux=283/500 windows=172/251 task=Running
[2026-02-17 08:47:16] Frame progress linux=284/500 windows=173/251 task=Running
[2026-02-17 08:49:17] Frame progress linux=285/500 windows=173/251 task=Running
[2026-02-17 08:51:19] Frame progress linux=286/500 windows=174/251 task=Running
[2026-02-17 08:53:21] Frame progress linux=288/500 windows=175/251 task=Running
[2026-02-17 08:55:22] Frame progress linux=289/500 windows=176/251 task=Running
[2026-02-17 08:57:24] Frame progress linux=290/500 windows=177/251 task=Running
[2026-02-17 08:59:25] Frame progress linux=291/500 windows=178/251 task=Running
[2026-02-17 09:01:27] Frame progress linux=292/500 windows=179/251 task=Running
[2026-02-17 09:03:28] Frame progress linux=293/500 windows=180/251 task=Running
[2026-02-17 09:05:30] Frame progress linux=295/500 windows=181/251 task=Running
[2026-02-17 09:07:31] Frame progress linux=296/500 windows=181/251 task=Running
[2026-02-17 09:09:33] Frame progress linux=297/500 windows=182/251 task=Running
[2026-02-17 09:11:35] Frame progress linux=299/500 windows=183/251 task=Running
[2026-02-17 09:13:37] Frame progress linux=300/500 windows=184/251 task=Running
[2026-02-17 09:15:39] Frame progress linux=301/500 windows=185/251 task=Running
[2026-02-17 09:17:46] Frame progress linux=303/500 windows=186/251 task=Running
[2026-02-17 09:19:48] Frame progress linux=304/500 windows=187/251 task=Running
[2026-02-17 09:21:49] Frame progress linux=305/500 windows=188/251 task=Running
[2026-02-17 09:23:51] Frame progress linux=307/500 windows=189/251 task=Running
[2026-02-17 09:25:52] Frame progress linux=308/500 windows=190/251 task=Running
[2026-02-17 09:27:54] Frame progress linux=309/500 windows=190/251 task=Running
[2026-02-17 09:29:56] Frame progress linux=311/500 windows=191/251 task=Running
[2026-02-17 09:31:57] Frame progress linux=312/500 windows=192/251 task=Running
[2026-02-17 09:33:59] Frame progress linux=314/500 windows=193/251 task=Running
[2026-02-17 09:36:01] Frame progress linux=315/500 windows=194/251 task=Running
[2026-02-17 09:38:03] Frame progress linux=316/500 windows=195/251 task=Running
[2026-02-17 09:40:04] Frame progress linux=318/500 windows=196/251 task=Running
[2026-02-17 09:42:06] Frame progress linux=319/500 windows=197/251 task=Running
[2026-02-17 09:44:07] Frame progress linux=321/500 windows=198/251 task=Running
[2026-02-17 09:46:09] Frame progress linux=322/500 windows=199/251 task=Running
[2026-02-17 09:48:10] Frame progress linux=323/500 windows=200/251 task=Running
[2026-02-17 09:50:12] Frame progress linux=324/500 windows=200/251 task=Running
[2026-02-17 09:52:13] Frame progress linux=326/500 windows=201/251 task=Running
[2026-02-17 09:54:15] Frame progress linux=327/500 windows=202/251 task=Running
[2026-02-17 09:56:17] Frame progress linux=328/500 windows=203/251 task=Running
[2026-02-17 09:58:19] Frame progress linux=329/500 windows=204/251 task=Running
[2026-02-17 10:00:20] Frame progress linux=331/500 windows=205/251 task=Running
[2026-02-17 10:02:22] Frame progress linux=332/500 windows=206/251 task=Running
[2026-02-17 10:04:23] Frame progress linux=333/500 windows=207/251 task=Running
[2026-02-17 10:06:25] Frame progress linux=335/500 windows=207/251 task=Running
[2026-02-17 10:08:26] Frame progress linux=336/500 windows=208/251 task=Running
[2026-02-17 10:10:28] Frame progress linux=337/500 windows=209/251 task=Running
[2026-02-17 10:12:30] Frame progress linux=338/500 windows=210/251 task=Running
[2026-02-17 10:14:32] Frame progress linux=340/500 windows=211/251 task=Running
[2026-02-17 10:16:33] Frame progress linux=341/500 windows=212/251 task=Running
[2026-02-17 10:18:35] Frame progress linux=342/500 windows=213/251 task=Running
[2026-02-17 10:20:36] Frame progress linux=344/500 windows=214/251 task=Running
[2026-02-17 10:22:38] Frame progress linux=345/500 windows=214/251 task=Running
[2026-02-17 10:24:40] Frame progress linux=346/500 windows=215/251 task=Running
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
Traceback (most recent call last):
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 310, in <module>
    raise SystemExit(main())
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 194, in main
    lin = linux_done_count(git_hash)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 86, in linux_done_count
    res = run(cmd)
  File "/Users/zephryj/work/Omega_vNext/tools/v60_autopilot.py", line 28, in run
    return subprocess.run(cmd, cwd=REPO_ROOT, check=check, capture_output=True, text=True)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/subprocess.py", line 528, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['ssh', 'linux1-lx', "find /omega_pool/parquet_data/v52/frames/host=linux1 -maxdepth 1 -type f -name '*_aa8abb7.parquet.done' 2>/dev/null | wc -l"]' returned non-zero exit status 255.
[2026-02-17 12:07:06] Autopilot started hash=aa8abb7 expected windows=250 linux=497 poll=180s stall=1800s
[2026-02-17 12:07:08] Frame progress linux=411/497 windows=250/250 task=Ready probe_ok=True
[2026-02-17 12:10:09] Frame progress linux=413/497 windows=250/250 task=Ready probe_ok=True

```

## Tail: autopilot log
```text
[2026-02-17 06:55:46] Frame progress linux=200/500 windows=123/251 task=Running
[2026-02-17 06:57:47] Frame progress linux=201/500 windows=124/251 task=Running
[2026-02-17 06:59:49] Frame progress linux=203/500 windows=125/251 task=Running
[2026-02-17 07:01:50] Frame progress linux=204/500 windows=126/251 task=Running
[2026-02-17 07:03:52] Frame progress linux=206/500 windows=127/251 task=Running
[2026-02-17 07:05:53] Frame progress linux=207/500 windows=128/251 task=Running
[2026-02-17 07:07:54] Frame progress linux=209/500 windows=129/251 task=Running
[2026-02-17 07:09:56] Frame progress linux=210/500 windows=130/251 task=Running
[2026-02-17 07:11:58] Frame progress linux=211/500 windows=130/251 task=Running
[2026-02-17 07:13:59] Frame progress linux=213/500 windows=131/251 task=Running
[2026-02-17 07:16:01] Frame progress linux=214/500 windows=132/251 task=Running
[2026-02-17 07:18:03] Frame progress linux=216/500 windows=133/251 task=Running
[2026-02-17 07:20:04] Frame progress linux=217/500 windows=134/251 task=Running
[2026-02-17 07:22:06] Frame progress linux=219/500 windows=135/251 task=Running
[2026-02-17 07:24:08] Frame progress linux=221/500 windows=136/251 task=Running
[2026-02-17 07:26:09] Frame progress linux=222/500 windows=137/251 task=Running
[2026-02-17 07:28:11] Frame progress linux=224/500 windows=138/251 task=Running
[2026-02-17 07:30:13] Frame progress linux=225/500 windows=139/251 task=Running
[2026-02-17 07:32:14] Frame progress linux=227/500 windows=140/251 task=Running
[2026-02-17 07:34:16] Frame progress linux=228/500 windows=141/251 task=Running
[2026-02-17 07:36:18] Frame progress linux=230/500 windows=142/251 task=Running
[2026-02-17 07:38:20] Frame progress linux=231/500 windows=143/251 task=Running
[2026-02-17 07:40:21] Frame progress linux=233/500 windows=144/251 task=Running
[2026-02-17 07:42:23] Frame progress linux=234/500 windows=145/251 task=Running
[2026-02-17 07:44:24] Frame progress linux=236/500 windows=145/251 task=Running
[2026-02-17 07:46:26] Frame progress linux=238/500 windows=146/251 task=Running
[2026-02-17 07:48:28] Frame progress linux=239/500 windows=147/251 task=Running
[2026-02-17 07:50:30] Frame progress linux=241/500 windows=148/251 task=Running
[2026-02-17 07:52:31] Frame progress linux=242/500 windows=149/251 task=Running
[2026-02-17 07:54:33] Frame progress linux=244/500 windows=150/251 task=Running
[2026-02-17 07:56:34] Frame progress linux=246/500 windows=151/251 task=Running
[2026-02-17 07:58:36] Frame progress linux=247/500 windows=151/251 task=Running
[2026-02-17 08:00:38] Frame progress linux=249/500 windows=152/251 task=Running
[2026-02-17 08:02:39] Frame progress linux=251/500 windows=153/251 task=Running
[2026-02-17 08:04:41] Frame progress linux=252/500 windows=154/251 task=Running
[2026-02-17 08:06:43] Frame progress linux=254/500 windows=155/251 task=Running
[2026-02-17 08:08:44] Frame progress linux=255/500 windows=156/251 task=Running
[2026-02-17 08:10:46] Frame progress linux=257/500 windows=157/251 task=Running
[2026-02-17 08:12:48] Frame progress linux=259/500 windows=157/251 task=Running
[2026-02-17 08:14:49] Frame progress linux=260/500 windows=158/251 task=Running
[2026-02-17 08:16:51] Frame progress linux=262/500 windows=159/251 task=Running
[2026-02-17 08:18:53] Frame progress linux=264/500 windows=160/251 task=Running
[2026-02-17 08:20:55] Frame progress linux=265/500 windows=161/251 task=Running
[2026-02-17 08:22:56] Frame progress linux=267/500 windows=162/251 task=Running
[2026-02-17 08:24:58] Frame progress linux=269/500 windows=163/251 task=Running
[2026-02-17 08:26:59] Frame progress linux=270/500 windows=164/251 task=Running
[2026-02-17 08:29:00] Frame progress linux=272/500 windows=165/251 task=Running
[2026-02-17 08:31:02] Frame progress linux=274/500 windows=165/251 task=Running
[2026-02-17 08:33:04] Frame progress linux=275/500 windows=166/251 task=Running
[2026-02-17 08:35:06] Frame progress linux=277/500 windows=167/251 task=Running
[2026-02-17 08:37:08] Frame progress linux=278/500 windows=168/251 task=Running
[2026-02-17 08:39:09] Frame progress linux=279/500 windows=169/251 task=Running
[2026-02-17 08:41:11] Frame progress linux=280/500 windows=170/251 task=Running
[2026-02-17 08:43:13] Frame progress linux=281/500 windows=171/251 task=Running
[2026-02-17 08:45:14] Frame progress linux=283/500 windows=172/251 task=Running
[2026-02-17 08:47:16] Frame progress linux=284/500 windows=173/251 task=Running
[2026-02-17 08:49:17] Frame progress linux=285/500 windows=173/251 task=Running
[2026-02-17 08:51:19] Frame progress linux=286/500 windows=174/251 task=Running
[2026-02-17 08:53:21] Frame progress linux=288/500 windows=175/251 task=Running
[2026-02-17 08:55:22] Frame progress linux=289/500 windows=176/251 task=Running
[2026-02-17 08:57:24] Frame progress linux=290/500 windows=177/251 task=Running
[2026-02-17 08:59:25] Frame progress linux=291/500 windows=178/251 task=Running
[2026-02-17 09:01:27] Frame progress linux=292/500 windows=179/251 task=Running
[2026-02-17 09:03:28] Frame progress linux=293/500 windows=180/251 task=Running
[2026-02-17 09:05:30] Frame progress linux=295/500 windows=181/251 task=Running
[2026-02-17 09:07:31] Frame progress linux=296/500 windows=181/251 task=Running
[2026-02-17 09:09:33] Frame progress linux=297/500 windows=182/251 task=Running
[2026-02-17 09:11:35] Frame progress linux=299/500 windows=183/251 task=Running
[2026-02-17 09:13:37] Frame progress linux=300/500 windows=184/251 task=Running
[2026-02-17 09:15:39] Frame progress linux=301/500 windows=185/251 task=Running
[2026-02-17 09:17:46] Frame progress linux=303/500 windows=186/251 task=Running
[2026-02-17 09:19:48] Frame progress linux=304/500 windows=187/251 task=Running
[2026-02-17 09:21:49] Frame progress linux=305/500 windows=188/251 task=Running
[2026-02-17 09:23:51] Frame progress linux=307/500 windows=189/251 task=Running
[2026-02-17 09:25:52] Frame progress linux=308/500 windows=190/251 task=Running
[2026-02-17 09:27:54] Frame progress linux=309/500 windows=190/251 task=Running
[2026-02-17 09:29:56] Frame progress linux=311/500 windows=191/251 task=Running
[2026-02-17 09:31:57] Frame progress linux=312/500 windows=192/251 task=Running
[2026-02-17 09:33:59] Frame progress linux=314/500 windows=193/251 task=Running
[2026-02-17 09:36:01] Frame progress linux=315/500 windows=194/251 task=Running
[2026-02-17 09:38:03] Frame progress linux=316/500 windows=195/251 task=Running
[2026-02-17 09:40:04] Frame progress linux=318/500 windows=196/251 task=Running
[2026-02-17 09:42:06] Frame progress linux=319/500 windows=197/251 task=Running
[2026-02-17 09:44:07] Frame progress linux=321/500 windows=198/251 task=Running
[2026-02-17 09:46:09] Frame progress linux=322/500 windows=199/251 task=Running
[2026-02-17 09:48:10] Frame progress linux=323/500 windows=200/251 task=Running
[2026-02-17 09:50:12] Frame progress linux=324/500 windows=200/251 task=Running
[2026-02-17 09:52:13] Frame progress linux=326/500 windows=201/251 task=Running
[2026-02-17 09:54:15] Frame progress linux=327/500 windows=202/251 task=Running
[2026-02-17 09:56:17] Frame progress linux=328/500 windows=203/251 task=Running
[2026-02-17 09:58:19] Frame progress linux=329/500 windows=204/251 task=Running
[2026-02-17 10:00:20] Frame progress linux=331/500 windows=205/251 task=Running
[2026-02-17 10:02:22] Frame progress linux=332/500 windows=206/251 task=Running
[2026-02-17 10:04:23] Frame progress linux=333/500 windows=207/251 task=Running
[2026-02-17 10:06:25] Frame progress linux=335/500 windows=207/251 task=Running
[2026-02-17 10:08:26] Frame progress linux=336/500 windows=208/251 task=Running
[2026-02-17 10:10:28] Frame progress linux=337/500 windows=209/251 task=Running
[2026-02-17 10:12:30] Frame progress linux=338/500 windows=210/251 task=Running
[2026-02-17 10:14:32] Frame progress linux=340/500 windows=211/251 task=Running
[2026-02-17 10:16:33] Frame progress linux=341/500 windows=212/251 task=Running
[2026-02-17 10:18:35] Frame progress linux=342/500 windows=213/251 task=Running
[2026-02-17 10:20:36] Frame progress linux=344/500 windows=214/251 task=Running
[2026-02-17 10:22:38] Frame progress linux=345/500 windows=214/251 task=Running
[2026-02-17 10:24:40] Frame progress linux=346/500 windows=215/251 task=Running
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

```

## Tail: uplink log
```text
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240124_aa8abb7.parquet to gs://omega_v52/omega/v52/frames/host=windows1/20240124_aa8abb7.parquet
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240124_aa8abb7.parquet.meta.json to gs://omega_v52/omega/v52/frames/host=windows1/20240124_aa8abb7.parquet.meta.json
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240130_aa8abb7.parquet to gs://omega_v52/omega/v52/frames/host=windows1/20240130_aa8abb7.parquet
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240130_aa8abb7.parquet.meta.json to gs://omega_v52/omega/v52/frames/host=windows1/20240130_aa8abb7.parquet.meta.json
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240202_aa8abb7.parquet to gs://omega_v52/omega/v52/frames/host=windows1/20240202_aa8abb7.parquet
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240202_aa8abb7.parquet.meta.json to gs://omega_v52/omega/v52/frames/host=windows1/20240202_aa8abb7.parquet.meta.json
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240205_aa8abb7.parquet to gs://omega_v52/omega/v52/frames/host=windows1/20240205_aa8abb7.parquet
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240205_aa8abb7.parquet.meta.json to gs://omega_v52/omega/v52/frames/host=windows1/20240205_aa8abb7.parquet.meta.json
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240208_aa8abb7.parquet to gs://omega_v52/omega/v52/frames/host=windows1/20240208_aa8abb7.parquet
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240208_aa8abb7.parquet.meta.json to gs://omega_v52/omega/v52/frames/host=windows1/20240208_aa8abb7.parquet.meta.json
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240220_aa8abb7.parquet to gs://omega_v52/omega/v52/frames/host=windows1/20240220_aa8abb7.parquet
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240220_aa8abb7.parquet.meta.json to gs://omega_v52/omega/v52/frames/host=windows1/20240220_aa8abb7.parquet.meta.json
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240223_aa8abb7.parquet to gs://omega_v52/omega/v52/frames/host=windows1/20240223_aa8abb7.parquet
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240223_aa8abb7.parquet.meta.json to gs://omega_v52/omega/v52/frames/host=windows1/20240223_aa8abb7.parquet.meta.json
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240226_aa8abb7.parquet to gs://omega_v52/omega/v52/frames/host=windows1/20240226_aa8abb7.parquet
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240226_aa8abb7.parquet.meta.json to gs://omega_v52/omega/v52/frames/host=windows1/20240226_aa8abb7.parquet.meta.json
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240229_aa8abb7.parquet to gs://omega_v52/omega/v52/frames/host=windows1/20240229_aa8abb7.parquet
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20240229_aa8abb7.parquet.meta.json to gs://omega_v52/omega/v52/frames/host=windows1/20240229_aa8abb7.parquet.meta.json
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
../Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/auth/__init__.py:54: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
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
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
./Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
Resuming upload for omega/v52/frames/host=windows1/20240208_aa8abb7.parquet
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
.............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
```