# Linux Freeze Best-Practice Research (Internet + On-Host Evidence)

- Timestamp: 2026-02-23 00:22:56 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- Re-run Linux freeze root-cause research using external best-practice sources, then map guidance to current `linux1` evidence.

## 2) Completed in This Session

- Re-confirmed dual-root-cause pattern on `zepher@192.168.3.113`:
  - **Memory cgroup throttling/OOM on `user-1000.slice`**:
    - `/etc/systemd/system/user-.slice.d/memory.conf` sets `MemoryHigh=16G`, `MemoryMax=20G`.
    - Kernel logs in boot `-4/-3/-1` show repeated `oom-kill:constraint=CONSTRAINT_MEMCG` under `/user.slice/user-1000.slice`.
  - **Storage-link incident causing ZFS suspend and hung tasks**:
    - At `2026-02-22 10:42:52 CST`, kernel logged `thunderbolt ... disconnected` + `pciehp Link Down`.
    - Immediately followed by `zio ... error=5` and repeated `Pool 'omega_pool' ... suspended`.
    - At `10:44:22 CST`, multiple `task 7z ... blocked for more than 60 seconds` stuck in `zio_wait` / ZFS read path.
- Verified current health snapshot:
  - Host uptime recovered after reboot.
  - `zpool status -x` currently healthy.
  - NVMe SMART for all three devices reports `PASSED`, `media_errors=0`.
- Derived internet-aligned best-practice strategy:
  1. Run heavy ETL in dedicated slice/service, not default `user.slice`.
  2. Use `MemoryHigh` for pressure control and `MemoryMax` only as hard stop.
  3. Use `OOMPolicy=kill` for workload unit to fail fast and avoid desktop/session collateral kills.
  4. Keep swap enabled to improve userspace OOM daemon effectiveness.
  5. Treat ZFS pool suspend as storage-path incident (`zpool events`, `zpool clear`, link recovery).
  6. Avoid single-point storage topology for production framing (single-device top-level vdev risk).

## 3) Current Runtime Status

- Mac: Connected and able to perform Linux forensics.
- Windows1: Not modified in this session.
- Linux1:
  - Reachable by SSH.
  - No active Stage1 ETL process at capture time.
  - `user.slice` memory cap still present and remains a recurrent risk.

## 4) Critical Findings / Risks

- Risk A: Any future ETL started from normal interactive session can re-enter `user-1000.slice` and hit the 20G cap, recreating memcg OOM storms.
- Risk B: External PCIe/TB link instability can still suspend `omega_pool`, causing D-state hangs and perceived system freezes even when memory looks healthy.
- Risk C: `omega_pool` is single top-level device; transient link/device faults have outsized blast radius.

## 5) Artifacts / Paths

- Research entry:
  - `handover/ai-direct/entries/20260223_002256_linux_freeze_best_practice_research.md`
- Supporting local evidence references:
  - `audit/_archived/20260221_linux_crash_root_cause.md`
  - `audit/_archived/20260221_linux_crash_investigation.md`

## 6) Commands Executed (Key Only)

- `ssh zepher@192.168.3.113 'journalctl --list-boots --no-pager'`
- `ssh zepher@192.168.3.113 'journalctl -k -b -5 --since "2026-02-22 10:42:35" --until "2026-02-22 10:45:10" --no-pager'`
- `ssh zepher@192.168.3.113 'systemctl show user-1000.slice -p MemoryHigh -p MemoryMax --no-pager'`
- `ssh zepher@192.168.3.113 'sudo -n zpool status -v'`
- `ssh zepher@192.168.3.113 'sudo -n smartctl -x /dev/nvme2n1 | head -n 220'`

## 7) Exact Next Steps

1. Land a standard launcher so Linux Stage1 always starts in `heavy-workload.slice`.
2. Update handover routing (`LATEST.md` + tools index) to enforce the launcher path for next operators.
3. Record a post-landing update entry with executed commands and verification output.

## 8) External Source Index

- [systemd resource control](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html)
- [systemd-run](https://www.freedesktop.org/software/systemd/man/devel/systemd-run.html)
- [systemd-oomd](https://www.freedesktop.org/software/systemd/man/systemd-oomd.html)
- [Linux cgroup v2 guide](https://docs.kernel.org/5.15/admin-guide/cgroup-v2.html)
- [OpenZFS message ZFS-8000-HC](https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-HC/index.html)
- [OpenZFS zpool properties (`failmode`)](https://openzfs.github.io/openzfs-docs/man/v2.0/8/zpoolprops.8.html)
- [OpenZFS `zpool clear`](https://openzfs.github.io/openzfs-docs/man/v2.1/8/zpool-clear.8.html)
- [OpenZFS `zpool events`](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-events.8.html)
- [OpenZFS pool concepts](https://openzfs.github.io/openzfs-docs/man/v2.2/7/zpoolconcepts.7.html)
- [Linux Thunderbolt admin guide](https://docs.kernel.org/admin-guide/thunderbolt.html)
- [earlyoom project](https://github.com/rfjakob/earlyoom)
