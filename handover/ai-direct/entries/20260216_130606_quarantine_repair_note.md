# v52 Quarantine Corrupt Package Repair Note

- Timestamp: 2026-02-16 13:06:06 +0800
- Scope: Windows1 + Linux1 framing gap recovery (quarantine archives)
- Pinned git short: `4f9c786`

## 1) Corrupted Packages Found

Original corrupted files were under quarantine and failed `7z t`:

- `E:\data\level2\2025\202512\quarantine\20251226.7z` (Windows1)
- `E:\data\level2\2025\202512\quarantine\20251229.7z` (Windows1)
- `E:\data\level2\2025\202512\quarantine\20251231.7z` (Windows1)

## 2) Repair Source Packages

Verified good source packages (non-quarantine same-day archives):

- `E:\data\level2\2025\202512\20251226.7z`
- `E:\data\level2\2025\202512\20251229.7z`
- `E:\data\level2\2025\202512\20251231.7z`

Action taken:

- Windows1 replaced quarantine corrupted files with same-day good source files.
- Linux1 synchronized repaired packages for missing shard dates:
  - `/omega_pool/raw_7z_archives/2025/202512/quarantine/20251229.7z`
  - `/omega_pool/raw_7z_archives/2025/202512/quarantine/20251231.7z`

All repaired files passed `7z t` validation.

## 3) Framing Recovery Execution

- Windows1 recovery list:
  - `audit/runtime/v52/recovery/rerun_windows1_quarantine_20251226.txt`
  - Result: `Processed 1/1 archives`
- Linux1 recovery list:
  - `audit/runtime/v52/recovery/rerun_linux1_quarantine_20251229_31.txt`
  - Result: `Processed 2/2 archives`

## 4) Current Completion State

- Windows1 done count (`*_4f9c786.parquet.done`): `359`
- Linux1 done count (`*_4f9c786.parquet.done`): `392`
- Shard gap check: `missing=0` for both workers.
- Runtime state: no active framing process; recovery tasks completed.

