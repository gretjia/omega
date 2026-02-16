# Linux omega_pool Remount Recovery

- Timestamp: 2026-02-17 01:10:37 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- Check whether Linux 8T external data disk is unmounted, recover mount, and verify usability.

## 2) Findings

- `/omega_pool` was unmounted at check time.
- Block device detected as `nvme1n1p1` with ZFS member label `omega_pool`.
- `zpool list` initially showed `no pools available`.

## 3) Recovery Actions

- Ran `sudo zpool import omega_pool` on `linux1-lx`.
- Verified pool health and datasets:
  - `zpool status omega_pool` => `ONLINE` (no known data errors)
  - `zfs list -r omega_pool` => `/omega_pool`, `/omega_pool/raw_7z_archives`, `/omega_pool/parquet_data` all mounted

## 4) Post-Recovery Verification

- `findmnt /omega_pool` => mounted as ZFS.
- Key directories visible:
  - `/omega_pool/raw_7z_archives`
  - `/omega_pool/parquet_data/v52/frames/host=linux1`
- Existing v52 frame markers are readable:
  - `*_4f9c786.parquet.done = 392`

## 5) Notes

- Workers are currently on git short `6b6b59b`, while historical frame outputs are tagged `4f9c786` in filenames.
- ZFS startup services are enabled and active (`zfs-import-cache.service`, `zfs-mount.service`).

## 6) Exact Next Step

1. If using historical v52 frames, keep filtering by `*_4f9c786.parquet`.
2. If continuing with new code commit, define whether to regenerate frames under new git short `6b6b59b`.
