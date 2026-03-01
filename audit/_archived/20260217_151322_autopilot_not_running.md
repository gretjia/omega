# Incident 20260217_151322_autopilot_not_running
- ts: 2026-02-17 15:13:22
- reason: autopilot_not_running
- autopilot_status: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.status.json
- autopilot_runner_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log
- autopilot_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.log
- uplink_log: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log

## Status JSON
```json
{
  "started_at": "2026-02-17 14:41:51",
  "git_hash": "aa8abb7",
  "bucket": "gs://omega_v52",
  "windows_expected": 250,
  "linux_expected": 497,
  "stage": "monitor_frame",
  "frame": {
    "linux_done": 484,
    "windows_done": 250,
    "windows_task_state": "Ready",
    "probe_linux": 484,
    "probe_windows": 250,
    "probe_ok": true,
    "updated_at": "2026-02-17 15:12:07"
  },
  "upload": {},
  "optimization": {},
  "train": {},
  "backtest": {}
}
```

## screen -ls
```text
There are screens on:
	76230.v60_ai_watchdog_aa8abb7	(Detached)
	14560.v60_delegate_aa8abb7	(Detached)
	38895.v60_uplink_aa8abb7	(Detached)
3 Sockets in /var/folders/w3/17p860vj3174xqzb2z010qth0000gn/T/.screen.


```

## pgrep
```text
14560 SCREEN -dmS v60_delegate_aa8abb7 bash -lc cd /Users/zephryj/work/Omega_vNext && codex exec "$(cat /Users/zephryj/work/Omega_vNext/audit/runtime/v52/delegate_prompt_aa8abb7.txt)" >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/delegate_aa8abb7.log 2>&1
14563 login -pflq zephryj /bin/bash -lc cd /Users/zephryj/work/Omega_vNext && codex exec "$(cat /Users/zephryj/work/Omega_vNext/audit/runtime/v52/delegate_prompt_aa8abb7.txt)" >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/delegate_aa8abb7.log 2>&1
14566 bash -lc cd /Users/zephryj/work/Omega_vNext && codex exec "$(cat /Users/zephryj/work/Omega_vNext/audit/runtime/v52/delegate_prompt_aa8abb7.txt)" >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/delegate_aa8abb7.log 2>&1
14571 node /Users/zephryj/.npm-global/bin/codex exec 严格按 /Users/zephryj/work/Omega_vNext/audit/v60_optimization_audit_final.md 执行并监督全链路。
当前已知上下文：Linux 有 13 个 2024-11/12 的 7z 在 Linux 上 Header Error；Windows 对这 13 个包 7z t rc=0 可读；需要补帧并确保上传后继续 optimization->train->backtest。
你的任务：
1) 只做与 v60 主链相关动作，不改数学逻辑。
2) 每次动作都写入 /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md（追加时间戳和结论）。
3) 遇到阻塞，给出最小修复并执行，不要停在分析。
4) 结束时输出状态到 /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json。
14572 /Users/zephryj/.npm-global/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/codex/codex exec 严格按 /Users/zephryj/work/Omega_vNext/audit/v60_optimization_audit_final.md 执行并监督全链路。
当前已知上下文：Linux 有 13 个 2024-11/12 的 7z 在 Linux 上 Header Error；Windows 对这 13 个包 7z t rc=0 可读；需要补帧并确保上传后继续 optimization->train->backtest。
你的任务：
1) 只做与 v60 主链相关动作，不改数学逻辑。
2) 每次动作都写入 /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md（追加时间戳和结论）。
3) 遇到阻塞，给出最小修复并执行，不要停在分析。
4) 结束时输出状态到 /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json。
38895 SCREEN -dmS v60_uplink_aa8abb7 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38898 login -pflq zephryj /bin/bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38900 bash -lc /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
38903 bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh

```

## Tail: autopilot runner log
```text
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

```

## Tail: autopilot log
```text
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

```

## Tail: uplink log
```text
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
............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................

Average throughput: 5.5MiB/s
[*] Verifying and finalizing (.done markers)...
WARNING:  Python 3.9 will be deprecated on January 27th, 2026. Please use Python version 3.10 and up.
To reinstall gcloud, run:
    $ gcloud components reinstall

This will also prompt to install a compatible version of Python.

If you have a compatible Python interpreter installed, you can use it by setting
the CLOUDSDK_PYTHON environment variable to point to it.

Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20260119_aa8abb7.parquet.done to gs://omega_v52/omega/v52/frames/host=windows1/20260119_aa8abb7.parquet.done
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20260122_aa8abb7.parquet.done to gs://omega_v52/omega/v52/frames/host=windows1/20260122_aa8abb7.parquet.done
  
Copying file:///Users/zephryj/Omega_uplink_buffer/host=windows1/20260128_aa8abb7.parquet.done to gs://omega_v52/omega/v52/frames/host=windows1/20260128_aa8abb7.parquet.done
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
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/oauth2/__init__.py:40: FutureWarning: You are using a Python version 3.9 past its end of life. Google will update google-auth with critical bug fixes on a best-effort basis, but not with any other fixes or features. Please upgrade your Python version, and then update google-auth.
  warnings.warn(eol_message.format("3.9"), FutureWarning)
/Users/zephryj/Library/Python/3.9/lib/python/site-packages/google/api_core/_python_version_support.py:246: FutureWarning: You are using a non-supported Python version (3.9.6). Google will not post any further updates to google.api_core supporting this Python version. Please upgrade to the latest Python version, or at least Python 3.10, and then update google.api_core.
  warnings.warn(message, FutureWarning)
......

Average throughput: 0.0B/s
[+] Batch complete. uploaded_parquet=3 uploaded_done=3

[*] Cleaning up local buffer...
[2026-02-17 15:09:46] windows1 sync rc=0
[2026-02-17 15:09:46] uplink cycle sleep 300s

```