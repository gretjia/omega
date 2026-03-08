# 2026-03-08 10:01 UTC - Linux Stage3 base-matrix launch for training years 2023,2024

## Summary

- Objective:
  - restore Linux reachability
  - verify whether Stage2 is sufficiently complete to begin Stage3 base-matrix generation
  - launch Linux training base matrix for `2023,2024`
- Outcome:
  - Linux SSH: PASS
  - Linux repo freshness: PASS (`699818f`)
  - Linux Stage3 base-matrix launch: PASS (running)

## Connectivity And Repo State

- `ssh linux1-lx` succeeded again from the controller.
- Linux repo before sync:
  - `main@6b0afff`
- Controller pushed current `HEAD` directly to Linux:
  - Linux repo after sync:
    - `main@699818f`

## Stage2 Readiness Assessment

Linux-side observations:

- authoritative Linux run directory:
  - `/omega_pool/parquet_data/stage2_full_20260307_v643fix/l2/host=linux1`
- local file count:
  - `370` parquet files

Windows-side observations:

- authoritative Windows run directory:
  - `D:\Omega_frames\stage2_full_20260307_v643fix\l2\host=windows1`
- `2024*` official output count:
  - `112`
- isolated repaired files available:
  - `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2\20231219_b07c2229.parquet`
  - `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2\20241128_b07c2229.parquet`

Key conclusion:

- Stage2 was sufficiently complete to begin the `2023,2024` training base matrix once Windows files became locally visible to Linux.
- The blocker was Linux-side visibility and default-path mismatch, not missing math outputs.

## Windows Visibility On Linux

- Linux already had the correct worker key material locally:
  - `~/.ssh/id_ed25519`
  - public key comment:
    - `omega-vm->workers-fixed`
- Windows `authorized_keys` already trusted that same key.
- Linux only lacked a host alias for `windows1-w1`.
- Added Linux SSH config entry for:
  - `Host windows1-w1`
  - `HostName 100.123.90.25`
  - `User jiazi`
  - `IdentityFile ~/.ssh/id_ed25519`
- Mounted Windows `D:` on Linux via `sshfs`:
  - mount point:
    - `/home/zepher/windows_d_sshfs`

## Stage3 Launch

Run id:

- `stage3_base_matrix_train_20260308_095850`

Training manifest:

- path:
  - `/home/zepher/work/Omega_vNext/audit/runtime/stage3_base_matrix_train_20260308_095850/input_files_train_2023_2024.txt`
- count:
  - `484`

Manifest composition:

- `370` Linux full-run outputs from:
  - `/omega_pool/parquet_data/stage2_full_20260307_v643fix/l2/host=linux1`
- `112` Windows official `2024*` outputs from:
  - `/home/zepher/windows_d_sshfs/Omega_frames/stage2_full_20260307_v643fix/l2/host=windows1`
- repaired `20231219_b07c2229.parquet`
- repaired `20241128_b07c2229.parquet`

Launched command:

- entrypoint:
  - `tools/forge_base_matrix.py`
- runtime:
  - `.venv/bin/python`
- years:
  - `2023,2024`
- output parquet:
  - `/omega_pool/parquet_data/stage3_base_matrix_train_20260308_095850/base_matrix_train_2023_2024.parquet`
- output meta:
  - `/omega_pool/parquet_data/stage3_base_matrix_train_20260308_095850/base_matrix_train_2023_2024.parquet.meta.json`
- shard dir:
  - `/omega_pool/parquet_data/stage3_base_matrix_train_20260308_095850/shards`
- PID:
  - `1474539`
- log:
  - `/home/zepher/work/Omega_vNext/audit/runtime/stage3_base_matrix_train_20260308_095850/forge.log`

## Important Split Constraint

Observed current code behavior:

- `tools/stage3_full_supervisor.py` only accepts year-level `--train-years` / `--backtest-years`
- `tools/run_local_backtest.py` filters years by `date.str.slice(0, 4)`

Operational implication:

- `2026-01` cannot be expressed directly through current `--backtest-years`
- the training base matrix launch is therefore cleanly scoped to `2023,2024`
- the later holdout for `2025 + 2026-01` will require:
  - an explicit file-list, or
  - a date-scoped wrapper around the current year-only interface
