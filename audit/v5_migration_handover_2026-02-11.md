# OMEGA v5.0 Migration Handover

**Date:** 2026-02-11
**Status:** **MIGRATION COMPLETE (Pending Reboot)**
**Next Agent:** Please read this carefully.

## 1. System State (The Great Migration)

*   **Codebase:** Moved to `C:\Omega_vNext`. (Fast NVMe System Drive)
*   **Source Data:** Moved to `E:\data\level2` (8T USB4). Verified 747/747 files.
*   **Staging/Output:** Configured to use `D:\Omega_frames\v50` (4T NVMe).
*   **Old Home:** `D:\Omega_vNext` is deprecated and contains locked files. **Delete it after reboot.**

## 2. Architecture (v5.0 "Holographic Damper")

*   **Core:** `omega_core/` (Renamed from v3, logic updated to Sato/Finzi standards).
*   **Pipeline:** `pipeline/` + `pipeline_runner.py` (New Entry Point).
*   **Config:** `configs/hardware/active_profile.yaml` (Points to C:/D:/E: correctly).

## 3. Immediate Action Items (Post-Reboot)

1.  **Environment:** Open terminal in `C:\Omega_vNext`.
2.  **Cleanup:** Delete the old `D:\Omega_vNext` to free up space.
3.  **Smoke Test:** Run the v5 pipeline smoke test:
    ```bash
    python pipeline_runner.py --stage frame --smoke
    ```
4.  **Full Run:** If smoke test passes, start the full framing:
    ```bash
    python pipeline_runner.py --stage frame
    ```

## 4. Key Context for AI

*   **Paradox 3 Fixed:** We now use Causal Volume Projection. Old v40 frames are incompatible.
*   **Hardware Profile:** We are running a 3-tier storage architecture (Code=C, Cache=D, Data=E). Do not change this without review.
*   **Monitor:** Use `tools/monitor_training.ps1` to watch CPU/Disk usage.

**Welcome to the new world.**
