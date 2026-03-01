# Stage 2 Windows `.done` Marker Bug RCA & Stage 3 BaseMatrix Launch

## 1. Issue: The "Schrödinger's 191" Windows Files
- **Symptom:** `LATEST.md` falsely reported the Windows Stage 2 queue as completed or empty for the new `latest` (V63) workload. However, inspection revealed the Windows directory `latest_feature_l2/host=windows1` had 191 massive `.parquet` files created on March 1st but exactly 0 `.done` markers.
- **RCA:** A cross-platform silent failure in `tools/stage2_physics_compute.py` occurred on the Windows node (`windows1-w1`). The line `done_path.touch()` executed without throwing a Python exception, but failed to actually write the `0-byte` file to the NTFS/SMB filesystem. 
- **Impact:** Subsequent orchestrator runs (and AI agents) scanning for `*.done` misread the directory as "0 progress", almost leading to throwing away 20 hours of valid V63 Stage 2 computation on the Windows side. Additionally, an incomplete BaseMatrix (Stage 3) was almost triggered using only the Linux node's 552 files.

## 2. Remediation Steps Taken
- **Process Halting:** Immediately terminated the mistakenly relaunched Stage 2 process on Windows and cleaned up its `.tmp` fragment. Stopped the prematurely launched `forge_base_matrix` on Linux.
- **Marker Retrofitting:** Verified the 191 Parquet files generated on March 1st were 100% complete via `stage2_targeted_resume_windows.log` (`__BATCH_OK__` / `DONE_NOW=191`). Manually generated the 191 `*.parquet.done` files on Windows via PowerShell.
- **Data Convergence:** SCP'd the 7.1GB of Windows Stage 2 data (`host=windows1`) across the LAN directly into the Linux node's `/omega_pool/parquet_data/latest_feature_l2/`.
- **Validation:** Linux node now holds the mathematically complete A-Share dataset for V63: `552 (Linux) + 191 (Windows) = 743 Total Done`.

## 3. Current State
- The V63 BaseMatrix forging process (`tools/forge_base_matrix.py`) is now safely running in the background on `linux1-lx`.
- Input pattern explicitly encompasses both hosts: `--input-pattern "/omega_pool/parquet_data/latest_feature_l2/host=*/*.parquet"`.
- It is dynamically capped at 1 worker due to memory guardrails (~26GB available RAM) and processing 155 total batches. Outputting to `audit/v63_basematrix.parquet`.
