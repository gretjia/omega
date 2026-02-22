# V62 Linux Re-Debug + Controlled Reboot + Stage1 Relaunch

- Timestamp: 2026-02-22 23:23:06 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- Re-debug Linux deeply, execute controlled reboot, and recover Stage1 into verified running state.

## 2) Completed in This Session

- Confirmed direct SSH path (`zepher@192.168.3.113`), executed deep pre-reboot checks.
- Verified cache policy compliance:
  - `/home` mounted on `Samsung SSD 990 PRO 4TB`.
  - active cache path remains `/home/zepher/framing_cache`.
- Executed controlled reboot:
  - reboot trigger sent at `23:18:40 +0800`.
  - host down/up + SSH restoration verified (`23:19:19 +0800`).
- Pulled cross-boot forensic evidence from kernel logs:
  - older boot shows `task 7z blocked for more than 60 seconds` on ZFS call stack.
  - later boots show repeated `polars-* invoked oom-killer` events in memory pressure windows.
- Relaunched Linux Stage1 with conservative throttle:
  - `python3 -u tools/stage1_linux_base_etl.py --years 2023,2024,2025,2026 --total-shards 4 --shard 0,1,2 --workers 1`
- Rotated stale log and cleared stale extraction dirs before relaunch.
- Performed early stability monitoring (multi-window):
  - cache bytes grew `~1.1G -> 4.5G -> 8.7G -> 13.1G -> 21.0G`.
  - log transitioned from extraction to active CSV scans (`_scan_split_l2_quotes SUCCESS`).
  - SSH probe latency stayed low (`~0.16-0.25s` over 5 probes).

## 3) Current Runtime Status

- Mac:
  - Controller healthy; Linux orchestration completed.
  - Windows refresh probe via `ssh_ps.py` failed due local tunnel/proxy closure (`127.0.0.1:7897`).
- Windows1:
  - Not refreshed in this session (use prior last-known from `LATEST.md`).
- Linux1:
  - Booted and reachable.
  - Stage1 active (`PID=3779`).
  - `audit/stage1_linux_v62.log` actively growing.
  - `DONE_HASH=0` at checkpoint (still within first large archive/day processing).

## 4) Critical Findings / Risks

- Deep root-cause evidence (historical boots):
  - ZFS path contention can block `7z` threads in kernel (`zio_wait`/`zfs_read` stack).
  - memory pressure windows can trigger OOM-killer from `polars-*` contexts.
- Immediate run is currently healthy, but first-shard long dwell means `DONE_HASH` may lag while compute is still valid.
- Windows status visibility is partially degraded until local tunnel/proxy for `ssh_ps.py` is restored.

## 5) Artifacts / Paths

- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/20260222_232306_v62_linux_redebug_reboot_relaunch.md`
- `/home/zepher/work/Omega_vNext/audit/stage1_linux_v62.log`
- `/home/zepher/work/Omega_vNext/artifacts/runtime/v62/stage1_linux.pid`

## 6) Commands Executed (Key Only)

- `ssh zepher@192.168.3.113 '... free -h; swapon --show; zpool status -x; findmnt -T /home/zepher/framing_cache; lsblk ...'`
- `ssh zepher@192.168.3.113 'sudo systemctl reboot'`
- reboot wait loop: ping down/up + SSH readiness checks
- `ssh zepher@192.168.3.113 'sudo journalctl --list-boots'`
- `ssh zepher@192.168.3.113 'sudo journalctl -k -b -2/-3/-4 | rg ...'`
- relaunch:
  - `nohup python3 -u tools/stage1_linux_base_etl.py --years 2023,2024,2025,2026 --total-shards 4 --shard 0,1,2 --workers 1 > audit/stage1_linux_v62.log 2>&1 &`

## 7) Exact Next Steps

1. Keep Linux Stage1 running; monitor every 2-3 minutes via:
   - log tail + log mtime/size
   - `DONE_HASH` count
   - stage1 process existence
2. Restore Windows tunnel/proxy path, then refresh:
   - `Omega_v62_stage1_win` task state
   - Windows `DONE_HASH` and log mtime
3. If Linux shows no log growth and no `DONE_HASH` movement for >20 minutes:
   - capture `pgrep`, `tail`, cache size delta, quick SSH latency probe
   - then perform controlled reboot/relaunch procedure again.
