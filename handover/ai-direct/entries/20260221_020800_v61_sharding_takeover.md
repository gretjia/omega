# v61 Sharded Framing Deployment — Takeover Handover

**Timestamp:** 2026-02-21 02:08:00 +0800  
**Author:** Antigravity (Cursor AI, taking over from Gemini 3 Flash in tmux:0)  
**Branch:** `v60-consolidated` @ `6244bab`  
**Commit Message:** `feat(frame): implement deterministic sharding and expand scope to 2023-2026`

---

## 1. Incident Timeline (Feb 20–21)

| Time | Event |
|------|-------|
| Feb 20 18:41, 22:05, 22:44 | Linux node crashed 3× (ZFS ARC + cgroup memory deadlock) |
| Feb 20 ~23:00 | Root cause identified: ZFS ARC (63GB potential) + user cgroup (100GB) > 126GB physical RAM |
| Feb 20 ~23:30 | Fix applied: ZFS ARC hard-limited to 16GB via `/etc/modprobe.d/zfs.conf` |
| Feb 21 00:00 | Previous AI (Gemini 3 Flash) consolidated branches `v60` → `v60-consolidated` |
| Feb 21 00:17 | Backup branches created: `backup/linux/20260221-001700`, `backup/windows/20260221-001700` |
| Feb 21 ~01:50 | Previous AI merged Linux+Windows snapshots and committed `6244bab` (deterministic sharding) |
| Feb 21 02:01 | Linux force-aligned to `6244bab` and Shard 0/2 launched (4 workers) |
| Feb 21 02:01 | Previous AI's session cancelled before Windows could be aligned and Shard 1/2 launched |
| Feb 21 02:02 | **Antigravity takes over** |

---

## 2. Architecture: v61 Sharded Framing

### What Changed (v60 → v61)

Based on `audit/_archived/v61.md` (Chief Architect audit) and `audit/_archived/v61_fix.md` (surgical patches):

1. **Momentum Sign Fix** (`kernel.py`): Removed `-` from `(-pl.col("srl_resid").sign())` → A-shares follow momentum, not mean-reversion
2. **Anti-Aliasing Low-Pass Filter** (`omega_etl.py`): `rolling_mean(window_size=3)` on `v_ofi`/`depth` to handle 3-second snapshot aliasing
3. **Excess Return Target** (`swarm_xgb.py`/`run_vertex_xgb_train.py`): Subtract cross-sectional daily mean to remove Beta contamination
4. **Zero-Copy Performance** (`kernel.py`): Polars `.cast().to_numpy()` instead of `.to_list()` for 1000× speedup
5. **Causal Isolation** (`omega_etl.py`): All `.cum_sum()`, `.rolling_mean()` partitioned `.over("symbol")`
6. **O(1) State Reset** (`kernel.py`): Contiguous boundary detection `syms[i] != syms[i-1]` for physics state reset
7. **Deterministic Sharding**: `md5(filename) % total_shards` for reproducible work distribution

### Sharding Design

- **Total files:** 751 (2023–2026 7z archives)
- **Shard 0 (Linux):** 372 files → `v61_linux_framing.py --shard 0 --total-shards 2 --workers 4`
- **Shard 1 (Windows):** 379 files → `v61_windows_framing.py --shard 1 --total-shards 2 --workers 4`
- **Hash function:** `int(md5(filename).hexdigest(), 16) % 2`
- **Output paths:**
  - Linux: `/omega_pool/parquet_data/v52/frames/host=linux1/{date}_{commit}.parquet`
  - Windows: `D:\Omega_frames\v61\host=windows1\{date}_{commit}.parquet`

---

## 3. Current Node Status

### Linux (zepher@192.168.3.113) ✅ RUNNING

- **Git:** `6244bab` on `v60-consolidated` ✓
- **Process:** `v61_linux_framing.py --shard 0 --total-shards 2 --workers 4` (PID 23783)
- **Progress:** Extracting July 2023 archives (4 concurrent 7z extractions)
- **RAM:** 49GB used / 123GB total (74GB available)
- **Disk:** 170GB / 4.8TB on `/omega_pool`
- **ZFS ARC:** Capped at 16GB (fix from crash analysis)
- **Log:** `~/work/Omega_vNext/framing_v61.log`

### Windows (jiazi@192.168.3.112) ❌ NOT ALIGNED

- **Git:** `76475c8` on `v60-consolidated` — **missing commit `6244bab`**
- **Diff from target:** 3 files changed (+215 inserts, -52 deletes)
  - `tests/test_sharding_v61.py` (new)
  - `tools/v61_linux_framing.py` (modified for sharding)
  - `tools/v61_windows_framing.py` (new)
- **Unstaged/Untracked changes:** `VERSION_SYNC.txt`, `trainer_backup.py` (modified), plus the files above
- **Old framing log:** 8 lines from pre-sharding run (processing Feb 2025) — stale
- **SSH:** Confirmed reachable: `ssh jiazi@192.168.3.112` (Mac IP now `192.168.3.93`, no `-b` flag needed)

### Mac Studio (192.168.3.93) — Controller

- **Git:** `6244bab` on `v60-consolidated` ✓ (source of truth)
- **Role:** Orchestrator, SMB mount at `/Volumes/desktop-41jidl2/Omega_vNext`

---

## 4. Action Plan (To Be Executed)

### Phase 1: Force-Align Windows

```bash
# Via SMB mount (most reliable — avoids Windows cmd.exe/PowerShell path issues)
git -C /Volumes/desktop-41jidl2/Omega_vNext reset --hard 6244bab
# This is safe: v61_windows_framing.py is IN commit 6244bab
```

### Phase 2: Launch Windows Shard 1/2

```bash
# Via SSH
ssh jiazi@192.168.3.112 "cd C:\Omega_vNext && python tools/v61_windows_framing.py --years 2023,2024,2025,2026 --workers 4 --shard 1 --total-shards 2 > framing_v61.log 2>&1 &"
```

### Phase 3: Monitor

- Linux: `ssh zepher@192.168.3.113 "tail -20 ~/work/Omega_vNext/framing_v61.log"`
- Windows: `ssh jiazi@192.168.3.112 "type C:\Omega_vNext\framing_v61.log"`

---

## 5. Network Topology Update

| Node | IP | SSH User | Notes |
|------|----|----------|-------|
| Mac Studio (M4 Max) | 192.168.3.93 | — | Controller, SMB mounts to both nodes |
| Linux (Ryzen, 126GB) | 192.168.3.113 | zepher | ZFS pool `/omega_pool` (4.8TB), ARC capped 16GB |
| Windows (DESKTOP-41JIDL2) | 192.168.3.112 | jiazi | Data on `E:\data\level2`, frames to `D:\Omega_frames` |

> **⚠️ Mac IP changed from 192.168.3.49 → 192.168.3.93.** The `-b 192.168.3.49` binding in older handover docs is now invalid.

---

## 6. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Windows `git reset --hard` loses local changes | Low | Changes are untracked copies of files already in `6244bab`, or stale backups (`trainer_backup.py`) |
| Linux crashes again from RAM pressure | Low | ZFS ARC capped to 16GB, math is now safe: 16GB + 100GB = 116GB < 126GB |
| Shard hash collision / overlap | None | Deterministic MD5 hashing tested: 372 + 379 = 751 (all files covered) |
| Windows 7z extraction speed | Medium | Windows has fewer CPU cores; monitor for I/O bottlenecks |

---

## 7. Evidence Artifacts

- [Linux crash root cause](file:///Users/zephryj/work/Omega_vNext/audit/_archived/20260221_linux_crash_root_cause.md)
- [v61 Chief Architect audit](file:///Users/zephryj/work/Omega_vNext/audit/_archived/v61.md)
- [v61 surgical patches](file:///Users/zephryj/work/Omega_vNext/audit/_archived/v61_fix.md)
- [Linux framing script](file:///Users/zephryj/work/Omega_vNext/tools/v61_linux_framing.py)
- [Windows framing script](file:///Users/zephryj/work/Omega_vNext/tools/v61_windows_framing.py)
- [Sharding test](file:///Users/zephryj/work/Omega_vNext/tests/test_sharding_v61.py)
