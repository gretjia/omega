---
entry_id: 20260309_034012_holdout_matrices_dual_host_execution_complete
task_id: TASK-V643-STAGE3-HOLDOUT-MATRIX-BUILD
timestamp_local: 2026-03-09 03:40:12 +0000
timestamp_utc: 2026-03-09 03:40:12 +0000
operator: Codex
role: executor
branch: main
status: completed
---

# Execution Complete: Stage3 Holdout Matrices On Dual Hosts

## 1. Objective

- Execute the externally audited holdout build spec, not just document it.
- Build:
  - `base_matrix_holdout_2025.parquet`
  - `base_matrix_holdout_2026_01.parquet`
- Keep the artifacts separate from the completed training matrix and prepare clean downstream evaluation roots.

## 2. Actual Host Allocation Used

Execution followed the audited optimized mode:

- `windows1-w1`
  - forged the heavy `2025` holdout artifact
- `linux1-lx`
  - first copied the `202601*.parquet` subset into Linux-local storage
  - then forged the January canary locally from that copied subset

Why this mode was accepted live:

- the January subset was small:
  - `19` files
  - about `0.824 GiB`
- Linux already had an `sshfs` mount of Windows `D:`
- the copied Linux-local manifest passed a strict `202601*.parquet` assertion before forge

## 3. Runtime Lessons Discovered During Execution

1. The Windows project `.venv` was not sufficient for Stage3 forge
   - `D:\work\Omega_vNext\.venv\Scripts\python.exe` failed immediately with:
     - `ModuleNotFoundError: No module named 'yaml'`
   - the successful Windows forge therefore used:
     - `C:\Python314\python.exe`

2. PowerShell manifest generation must avoid BOM
   - `Set-Content -Encoding utf8` produced a BOM-prefixed first line
   - that corrupted the first path in `--input-file-list`
   - the fix was to write manifests with:
     - `.NET UTF8Encoding($false)` (UTF-8 without BOM)

3. Windows background launch via `Start-Process` over SSH was unreliable for this workflow
   - the stable execution method was a persistent controller-managed exec session

## 4. Artifact Results

### 4.1 2025 outer holdout

- Forge host:
  - `windows1-w1`
- Output root:
  - `D:\Omega_frames\stage3_holdout_2025_20260309_031430`
- Clean eval root:
  - `D:\Omega_frames\stage3_holdout_2025_eval_20260309_031430`
- Final artifact:
  - `D:\Omega_frames\stage3_holdout_2025_20260309_031430\base_matrix_holdout_2025.parquet`
- Result:
  - `base_rows=385674`
  - `input_file_count=239`
  - `symbols_total=8640`
  - `batch_count=44`
  - `worker_count=2`
  - `seconds=999.62`
- Scope audit:
  - `year_min=2025`
  - `year_max=2025`
  - `year_count=1`
  - `date_min=20250102`
  - `date_max=20251230`

### 4.2 2026-01 final canary

- Source copy root:
  - `/omega_pool/parquet_data/stage3_holdout_2026_01_sourcecopy_20260309_031248/l2_input`
- Linux-local manifest:
  - `/home/zepher/work/Omega_vNext/audit/runtime/stage3_holdout_2026_01_linux_20260309_031248/input_files_202601_linux_local.txt`
- Forge host:
  - `linux1-lx`
- Output root:
  - `/omega_pool/parquet_data/stage3_holdout_2026_01_linux_20260309_031248`
- Clean eval root:
  - `/omega_pool/parquet_data/stage3_holdout_2026_01_eval_20260309_031248`
- Final artifact:
  - `/omega_pool/parquet_data/stage3_holdout_2026_01_linux_20260309_031248/base_matrix_holdout_2026_01.parquet`
- Result:
  - `base_rows=26167`
  - `input_file_count=19`
  - `symbols_total=7580`
  - `batch_count=38`
  - `worker_count=1`
  - `seconds=1281.99`
- Scope audit:
  - `year_min=2026`
  - `year_max=2026`
  - `year_count=1`
  - `date_min=20260105`
  - `date_max=20260129`

## 5. Clean Evaluation Roots

Both holdout artifacts were copied into shard-free evaluation directories containing only:

- final parquet
- final meta json

This satisfies the audited rule that downstream evaluation must not point at forge workspaces containing `_shards/`.

## 6. Verdict

- `PASS`
- Both missing holdout Stage3 artifacts now exist.
- Both artifacts are date-clean and non-empty.
- Both artifacts are isolated from the training matrix.
- Both artifacts now have clean evaluation roots for downstream holdout use.
