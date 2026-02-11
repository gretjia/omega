# Storage Estimation: Extending L2 Data to 2020-2022

**Date:** 2026-02-10  
**Context:** Extending dataset from 2023-2026 to include 2020-2022.

## 1. The "Expansion Ratio" Discovery

We analyzed the actual on-disk footprint of your data:
*   **Source (Jan 2023):** 35.2 GB (`.7z` Archives)
*   **Output (Jan 2023):** 3.66 GB (`.parquet` Frames)
*   **The Surprise:** The output is **~10% of the source size**.
    *   *Why?* The `.7z` archives likely contain full L2 tick data (very dense), while your framing process extracts a specific subset (snapshots/features) or the Parquet compression is extremely efficient for this schema.
    *   *Benefit:* Storage pressure will come from the **Source Archives**, not the Output Frames.

## 2. Historical & Projected Data Volume

Based on market volatility trends (China L2) and your file sizes:
*   **2020:** Volatile (COVID). Est. 2.5 GB/day.
*   **2021:** High Volume. Est. 2.8 GB/day.
*   **2022:** Bear Market. Est. 2.4 GB/day.
*   **2023:** Verified Baseline. ~2.5 GB/day.
*   **2024:** High Volatility. ~4.5 GB/day.
*   **2025:** Current Baseline. ~4.2 GB/day.

| Year | Trading Days | Avg Archive Size | Total Source (.7z) | Total Output (.parquet) | Total Year Footprint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2020 (New)** | 242 | 2.5 GB | 605 GB | 60 GB | **665 GB** |
| **2021 (New)** | 242 | 2.8 GB | 677 GB | 68 GB | **745 GB** |
| **2022 (New)** | 242 | 2.4 GB | 580 GB | 58 GB | **638 GB** |
| **2023** | 242 | 2.5 GB | 607 GB | 61 GB | **668 GB** |
| **2024** | 242 | 4.5 GB | 1,089 GB | 109 GB | **1,198 GB** |
| **2025** | 243 | 4.2 GB | 1,020 GB | 102 GB | **1,122 GB** |
| **2026** | 242 (Proj) | 4.5 GB | 1,089 GB | 109 GB | **1,198 GB** |
| **TOTAL** | | | **5,667 GB** | **567 GB** | **6,234 GB** |

## 3. Storage Recommendations

### Option A: dedicated "Active Working" Drive (Recommended)
If you keep "Cold" archives on a slow HDD and only keep "Active" archives + Output on NVMe.
*   **Requirement:** 2020-2022 Source + Output = ~2.1 TB.
*   **Purchase:** **4TB NVMe SSD.**
*   *Why?* Gives you enough room for the 2TB of new data, plus scratch space for staging, with ~50% breathing room for performance (SSDs slow down when full).

### Option B: "All-Hot" Storage (Everything on NVMe)
If you want **ALL** years (2020-2026) source and output on one fast drive.
*   **Requirement:** ~6.25 TB Total.
*   **Purchase:** **8TB NVMe SSD.**
    *   *Recommendation:* **Sabrent Rocket 4 Plus 8TB** or **Samsung 870 QVO 8TB** (SATA, if M.2 slots are full, but NVMe is preferred).
    *   *Alternative:* 2x **4TB NVMe** in RAID 0 (Riskier) or independent volumes (e.g., Data_A and Data_B).

## 4. Summary for Shopping
*   **To add 2020-2022 only:** You need **~2.1 TB** of space. Buy a **4TB NVMe**.
*   **To host EVERYTHING (2020-2026):** You need **~6.3 TB** of space. Buy an **8TB NVMe**.

**Critical Tip:** Don't forget the **Staging Drive** advice from the previous report. If you buy a 4TB drive, use it for **Data Storage**. Buy a separate small (1TB) drive for **Staging** to maximize IOPS.
