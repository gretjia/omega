# v6.1 Anti-Fragile Framing Session Handover

**Date:** 2026-02-21 02:00 ~ 09:00 (7 hours)  
**Agent:** Antigravity (Gemini 3 Pro via Cursor)  
**Branch:** `v60-consolidated`  
**Latest Commit:** `ce2df71`  
**Result:** ❌ Framing failed — 0 parquet files produced in ~5.5 hours of runtime

---

## 1. Session Objective

Apply 8 anti-fragile patches from `tools/v61_fix_final.md` and `tools/v61_fix_final_2.md` to core code, then restart and run the distributed framing pipeline (Linux Shard 0/2, Windows Shard 1/2) to produce Level-2 physics frames from raw 7z tick archives.

---

## 2. Patches Applied (All Committed, All in `ce2df71`)

### From `v61_fix_final.md` (commit `551edaf`)

| # | Patch | File | Change |
|---|-------|------|--------|
| F1 | Overnight Phase Transition | `omega_core/kernel.py:203` | Added `dates[i] != dates[i-1]` to boundary reset — prevents yesterday's `current_y` from contaminating today's opening |
| F2 | Infinity Shield | `omega_core/kernel.py:82-87` | Replaced slow Python loop `_to_f64()` with vectorized `np.nan_to_num()` in `_safe_f64_col` |
| F3 | Anti-Fragile Memory (backtest) | `tools/v61_run_local_backtest.py:242` | `Pool(maxtasksperchild=1)` — forces jemalloc page release |
| F4 | Anti-Fragile Memory (framing) | `tools/v61_linux_framing.py`, `v61_windows_framing.py` | Same `maxtasksperchild` fix, later relaxed to `5` |

### From `v61_fix_final_2.md` (commit `6e8f520`)

| # | Patch | File | Change |
|---|-------|------|--------|
| 2-1 | Safe Column Extract | `omega_core/trainer.py:449-451` | `merged.get_column("fwd_return")` instead of `merged["fwd_return"]`. Rejected `fwd_excess_return` re-introduction |
| 2-2 | **LOB Flux Isolation** ⚠️ | `omega_core/omega_etl.py:254-259,284` | `_lob_flux_expr(group_col)` with `.diff().over(group_col)` — CRITICAL: was crossing symbol boundaries, poisoning `cancel_vol` |
| 2-3 | I/O Panic Prevention | `tools/v61_run_local_backtest.py:108-124` | Sequential single-file scan + `diagonal_relaxed` concat instead of bulk `pl.scan_parquet(files)` |
| 2-4 | Singularity Immunity | `omega_core/trainer.py:457-471` | Added `is_physics_valid` to eval mask in `_vector_alignment` |

### Additional Fixes (commit `ddcfb2c`)

| # | Patch | File | Change |
|---|-------|------|--------|
| E1 | CSV Schema Mismatch | `omega_core/omega_etl.py:50-54` | `pl.concat(lfs, how="diagonal_relaxed")` in `scan_l2_quotes` — early 2023 CSVs have 13 cols vs 50 |

### Performance Tuning (commit `ce2df71`)

| # | Change | File | Effect |
|---|--------|------|--------|
| P1 | `maxtasksperchild=5` | `tools/v61_linux_framing.py` | Relaxed from 1 to 5 (cold-start savings negligible at 0.5%) |

---

## 3. Framing Deployment Attempts — All Failed

### Attempt 1: 2 workers, no tmpfs (02:41)

- **Config:** 2 workers, `maxtasksperchild=1`, `POLARS_MAX_THREADS=8`
- **Result:** Swap 8GB/8GB full within minutes. Workers consumed ~15GB RSS each
- **Root Cause:** Polars jemalloc hoards memory, never releases to OS

### Attempt 2: 2 workers, no tmpfs, previous Gemini CLI process interference (02:38-02:41)

- **Config:** Gemini CLI had also launched a 4-worker process from tmux
- **Result:** Double processes competing for memory
- **Root Cause:** Multiple agents launching framing simultaneously

### Attempt 3: 3 workers + tmpfs 35GB + ARC=16GB (03:27)

- **Config:** `sudo mount -t tmpfs -o size=35G tmpfs /omega_pool/temp_framing/`, 3 workers
- **Result:** Swap 8GB/8GB full. tmpfs 20GB used (extraction working), but total memory > 123GB
- **Root Cause:** 3 × 20GB Polars + 20GB tmpfs + 16GB ZFS ARC ≈ 96GB + OS > 123GB

### Attempt 4: 3 workers + tmpfs 35GB + ARC=8GB (03:33)

- **Config:** `echo 8589934592 | sudo tee /sys/module/zfs/parameters/zfs_arc_max`, 3 workers
- **Result:** Swap 7GB/7GB full within 3 minutes
- **Root Cause:** Even with ARC=8GB, 3 workers × 20GB+ Polars peak > available RAM

### Attempt 5: 2 workers + tmpfs 35GB + ARC=8GB (03:40) — Overnight run

- **Config:** 2 workers, maxtasksperchild=5, tmpfs, ARC=8GB
- **Result:** 5.5 hours, 0 files completed. Memory 119GB/123GB, swap 7GB/7GB. Workers RSS shows 6KB (zombie?), tmpfs stuck at 18GB
- **Root Cause:** Workers likely OOM-killed or hanging on 7z extraction → Polars ETL pipeline. earlyoom may have killed worker sub-processes while main process stayed alive

### Windows Attempt (03:33)

- **Config:** 2 workers, `maxtasksperchild=1`, commit `6e8f520`
- **Result:** Processing started but schema errors on early 2023 CSVs. `diagonal_relaxed` produced frames with ALL null L2 depth columns — garbage output
- **Root Cause:** `diagonal_relaxed` fills missing columns with null, but the ETL pipeline then tries to compute `microprice`, `depth`, `ofi` from null values → meaningless frames

---

## 4. Root Cause Analysis — Why Framing Cannot Run

### Problem 1: Polars Memory Explosion Per Worker (~20-30GB)

Each worker's lifecycle: `7z extract 2GB→7.6GB CSV` → `Polars scan_l2_quotes()` → `build_l2_frames()`.

The `build_l2_frames()` function creates massive intermediate DataFrames:

- Raw CSV: ~7.6GB (millions of tick rows × 50 columns)
- Polars lazy eval materializes everything at `.collect()` time
- Rolling means, cumulative sums, group_by aggregations create copies
- Peak RSS per worker: **20-30GB**, not the estimated 15GB

With 123GB RAM, 16GB ZFS ARC (now 8GB), and OS overhead:

- **Max safe workers = 1** (leaves ~90GB for a single Polars pipeline)
- **2 workers = marginal** (2 × 25GB + 8GB ARC + 30GB OS = 88GB, but peak bursts exceed)
- **3 workers = impossible**

### Problem 2: CSV Schema Heterogeneity

Early 2023 7z archives contain CSVs with only 4-13 columns (missing L2 depth data). When `diagonal_relaxed` concats them, ALL depth columns become null. The ETL then produces garbage frames. These files need to be **skipped entirely**, not concated.

### Problem 3: ZFS + tmpfs + Polars Three-Way Memory Competition

- ZFS ARC: even at 8GB, competes for RAM
- tmpfs: holds extracted CSVs in RAM (up to 7.6GB per archive)
- Polars: builds DataFrame from those CSVs, ALSO in RAM
- Result: the same data exists **twice** in memory (tmpfs + Polars DataFrame)

### Problem 4: `maxtasksperchild` Doesn't Help Enough

Whether 1 or 5, the memory problem is WITHIN a single task execution. The worker uses 20-30GB to process ONE file. Restarting after that file doesn't prevent the peak during processing.

---

## 5. Current System State

### Code State

- **Branch:** `v60-consolidated` at `ce2df71`
- **All 8+2 patches committed and pushed to both nodes**
- Both nodes were `git reset --hard` to latest

### Infrastructure State

| Node | State | Memory | Swap | ZFS ARC | tmpfs |
|------|-------|--------|------|---------|-------|
| Linux (192.168.3.113) | **STOPPED** | ~94GB/123GB (recovering) | 0/7GB (just reset) | 8GB (lowered from 16GB) | 35GB mounted at `/omega_pool/temp_framing/` |
| Windows (192.168.3.112) | **STOPPED** | Normal | N/A | N/A | N/A |

### Data State

- **0 new parquet frames produced** — all previous frames were deleted during cleanup
- Raw 7z archives: intact at `/omega_pool/7z_archives/` (Linux) and `D:\7z_archives\` (Windows)
- `audit/v61.zip`: regenerated (145KB, 48 files)

---

## 6. Critical Recommendations for Next AI

### Immediate Priority: Fix Framing to Actually Produce Output

1. **Reduce Polars memory footprint** — The ETL pipeline needs to be refactored to:
   - Process CSVs in streaming/chunked mode (not full materialization)
   - Use `pl.scan_csv().collect(streaming=True)` if available
   - Or split large CSVs into chunks before Polars processes them

2. **Skip incomplete CSVs instead of diagonal_relaxed** — In `scan_l2_quotes`, if a CSV lacks L2 depth columns (`bid_p1` etc.), **skip it entirely** rather than filling with null. Add schema validation before concat.

3. **Serial single-worker mode as fallback** — If nothing else works, run with `--workers 1`. Slower but guaranteed to work within memory.

4. **Consider dropping tmpfs** — tmpfs doubles memory usage (CSV in RAM + Polars DataFrame from that CSV). Regular disk may be slower for I/O but saves ~8GB per concurrent extraction.

5. **ZFS ARC is currently at 8GB** — The next AI needs to be aware this was manually lowered. To restore: `echo 17179869184 | sudo tee /sys/module/zfs/parameters/zfs_arc_max`

### Do NOT

- Do NOT try 3 workers on the 123GB Linux node — proven to fail
- Do NOT use `diagonal_relaxed` for concat of CSVs with different schemas — produces garbage
- Do NOT trust that earlyoom won't kill workers — it will, silently
- Do NOT assume `maxtasksperchild` solves memory issues — the peak is within a single task

---

## 7. Files Modified This Session

| File | Change |
|------|--------|
| `omega_core/kernel.py` | ACTION 2 (overnight reset) + ACTION 3 (infinity shield) |
| `omega_core/trainer.py` | ACTION 1 (safe extract) + ACTION 4 (singularity immunity) |
| `omega_core/omega_etl.py` | LOB flux `.over()` isolation + `diagonal_relaxed` concat |
| `tools/v61_run_local_backtest.py` | `maxtasksperchild=1` + sequential single-file scan |
| `tools/v61_linux_framing.py` | `maxtasksperchild=5` + anti-fragile rewrites (prior session) |
| `tools/v61_windows_framing.py` | `maxtasksperchild=1` |
| `tools/v61_fix_final.md` | [NEW] First set of patch directives |
| `tools/v61_fix_final_2.md` | [NEW] Second set of patch directives |
| `audit/_archived/v61_audit_README.md` | [NEW] Audit zip topology guide |
| `audit/v61.zip` | Regenerated with all patches |

---

## 8. Commit History (This Session)

```
ce2df71 perf(frame): maxtasksperchild=5, prepare for tmpfs silver bullet
6e8f520 fix(etl+trainer+bt): v61 final-2 armor — 4 surgical patches
ddcfb2c fix(etl+frame): diagonal_relaxed concat + maxtasksperchild=1
551edaf fix(kernel+backtest): apply v61 final armor — 4 anti-fragile patches
80091e7 fix(frame): anti-fragile rewrite — cap Polars threads, global cfg, reduce workers to 2
```
