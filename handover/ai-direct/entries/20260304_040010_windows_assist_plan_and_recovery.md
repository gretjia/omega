# Entry: 2026-03-04 04:00 +0800 (Windows Assist Plan & Recovery Protocol for V63 Stage 2)

## 1. Context & Objective
The Linux node (`linux1-lx`) is currently processing the remaining ~117 files for V63 Stage 2 across 4 isolated Shard workers. The Windows node (`windows1-w1`) has finished its assigned 60 files and is now idle (its supervisor successfully exited after processing).
To minimize the overall completion time (from ~17 hours down to <15 hours), we are executing a **Windows Assist Plan**. This involves dynamically reallocating ~28 unprocessed files from the Linux queue tail to the idle Windows node.

## 2. Risk Assessment & Mitigations
Modifying file queues while workers are active carries extreme risk of race conditions, data corruption, and downstream pipeline failure. The following mandatory constraints have been designed:
1. **Cursor Collision Risk:** If we move a file that a Linux worker is currently computing, the worker will crash (Core Dump).
   - **Mitigation:** Strict reverse-chronological extraction. Workers are processing `202505xx`. We extract `2026xxxx` from the absolute tail end of the queue.
2. **Merge Failure Risk:** Stage 3 (`forge_base_matrix.py`) expects all files to reside in `v63_feature_l2_shard*/host=linux1/`. Moving files around arbitrarily breaks this rigid structure.
   - **Mitigation:** Use a JSON mapping dictionary (`windows_assist_mapping.json`). Every extracted file's original `shard_id` is recorded. When returning from Windows, files are deterministically spliced exactly back into their source directories.
3. **Catastrophic State Loss:** If any script deletes or scrambles `.done` markers, all completed progress is lost.
   - **Mitigation:** A full, physical `tar` backup of all current L2 state markers and data on Linux is created *before* any file movement occurs.

## 3. The Execution Protocol (Whitebox Python Scripts)
We are strictly avoiding opaque LLM bash commands. All file manipulations are governed by two audited Python scripts located on `linux1-lx` at `/home/zepher/`:

### Phase 1: Isolation & Mapping (`windows_assist_prep.py`)
1. **Backup:** Executes `tar -cf /home/zepher/v63_l2_backup_before_assist.tar /omega_pool/parquet_data/v63_feature_l2_shard*/host=linux1`
2. **Scan:** Finds all `.parquet` files lacking a corresponding `.done` marker.
3. **Extract:** Sorts remaining files by name, takes the **last 28 files**.
4. **Move & Record:** Physically moves them to `/omega_pool/parquet_data/v63_subset_l1_assist_w1/host=windows1/` and writes `windows_assist_mapping.json`.

### Phase 2: Windows Execution
1. Windows environment is synced with the latest codebase.
2. The Numba seal is broken via strict environmental overrides:
   `$env:OMEGA_STAGE2_FORCE_SCAN_FALLBACK='0'; $env:OMEGA_DISABLE_NUMBA='0'; $env:OMEGA_STAGE2_ISOLATE_SYMBOL_BATCH='0'`
3. A new targeted supervisor is launched on Windows pointing to the assist input dir.

### Phase 3: Seamless Merge (`windows_assist_merge.py`)
1. Windows returns processed `.parquet` and `.done` files.
2. The script reads `windows_assist_mapping.json`.
3. It precisely routes each file back to its specific `v63_feature_l2_shard{X}/host=linux1/` directory.

## 4. Emergency Recovery Procedure (If Anything Goes Wrong)
If the system crashes, files go missing, or the mapping JSON is corrupted, execute the following immediately:

1. **Stop Windows Assist:** Kill any running supervisor on `windows1-w1`.
2. **Restore Linux State:**
   ```bash
   cd /
   tar -xvf /home/zepher/v63_l2_backup_before_assist.tar
   ```
   *This instantly restores all `.done` markers and processed `.parquet` files to their exact state before this plan was initiated.*
3. **Return Pending Files:**
   Move all files from `/omega_pool/parquet_data/v63_subset_l1_assist_w1/host=windows1/` back into any of the active Linux shard input directories. The Linux workers will natively pick them up and continue.

---
*State Updates:*
- **[2026-03-04 04:00]**: Plan established. Python scripts written and deployed to `linux1-lx`. Awaiting execution command.