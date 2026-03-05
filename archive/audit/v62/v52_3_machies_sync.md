# OMEGA v5.2 Distributed Architecture Implementation Plan

## 1. Goal Description

Transition OMEGA from a single-machine SMB workflow to a distributed "Controller-Worker" architecture.
**Core Philosophy:**

- **Mac:** The "Brain" (Git Controller, Config Authority).
- **Windows/Linux:** The "Muscle" (Read-Only Git Workers, Execution Nodes).
- **Audit Trail:** Every run is cryptographically pinned to a Git Commit and Config Hash.

## 2. User Review Required
>
> [!IMPORTANT]
> **Data Separation Policy:**
> The `.gitignore` is the single most critical component. It MUST prevent raw data (`.7z`), frames (`.parquet`), and model artifacts from entering Git.
> If this repo is **already** a git repo: skip `git init` and focus on verifying `.gitignore` + removing any accidentally tracked large files via `git rm --cached`.

## 3. Proposed Changes

### 3.1 [UPDATE] `.gitignore` (Root)

Establish the "Code Only" boundary.

See repo root `.gitignore` (keep adding ignore rules here, do not create per-host exceptions inside git).

### 3.2 [NEW] `audit/runtime/v52/run_meta.template.json`

Create the standard schema for run auditing.

```json
{
    "run_id": "v52-run-YYYYMMDD-x",
    "git_tag": "v52-run-YYYYMMDD-x",
    "git_commit": "FULL_COMMIT_HASH",
    "config_hash": "SHA256_OF_CONFIG_PY",
    "node": "HOSTNAME",
    "shard": "SHARD_ID",
    "status": "pending"
}
```

### 3.3 [MODIFY] `pipeline_runner.py`

Add support for `--archive-list` to allow zero-copy framing on workers where data is on a separate disk.

## 4. Execution Workflow (Standard Operating Procedure)

This section defines the "Manual" operations for the Controller.

### Phase A: Architecture Initialization (One-Time)

1. **Mac:** Clone `Omega_vNext` to local disk (do not work out of SMB/mapped disk).
2. **Mac:** Verify `.gitignore` is correct; remove any tracked data files if needed.
3. **Mac:** Commit code/doc changes.
4. **Mac:** Ensure branch `v52` exists (or create it).
5. **Mac:** Setup Bare Origin (`mkdir -p ~/git/Omega_vNext.git && git init --bare`).
6. **Mac:** Push to local bare `origin`.

### Transport Options (Pick One)

Workers need a way to fetch from the Mac bare origin.

1. **Option A: SSH (requires enabling Remote Login on macOS)**
   - Enable: System Settings -> General -> Sharing -> Remote Login (SSH).
   - Worker clone URL (example): `ssh://<mac_user>@<mac_ip>/Users/<mac_user>/git/Omega_vNext.git`

2. **Option B: `git://` daemon (read-only, no admin required)**
   - On Mac (controller), serve the bare repo for fetch/clone:
     ```bash
     touch ~/git/Omega_vNext.git/git-daemon-export-ok
     git daemon --reuseaddr --base-path=$HOME/git --listen=0.0.0.0 --port=9418 $HOME/git/Omega_vNext.git
     ```
   - Worker clone URL (example): `git://<mac_ip>/Omega_vNext.git`
   - Note: `git://` is read-only and unauthenticated. Use on trusted LAN only.

### Phase B: Worker Setup (One-Time)

1. **Win/Lin:** Setup credentials if using SSH (or skip for `git://`).
2. **Win/Lin:** `git clone <mac_url>`.
3. **Win/Lin:** Install `pre-commit` hook (Physical Block).

### Phase C: Distributed Run (Routine)

1. **Mac:** Commit changes.
2. **Mac:** `git tag -a v52-run-01 -m "..."`.
3. **Mac:** `git push --tags`.
4. **Win/Lin:** `git fetch --tags && git checkout v52-run-01`.
5. **Win/Lin:** Run Pipeline.

## 5. Verification Plan

### 5.1 Verification: Git Filter

**Command:**

```bash
# Verify that NO large files are tracked
git ls-files | grep -E "\.(7z|parquet|model|joblib)$"
# EXPECTED OUTPUT: (Empty)
```

### 5.2 Verification: Import Integriy

**Command (On All Nodes):**

```bash
python -c "import omega_core.trainer; print(omega_core.trainer.__file__)"
# EXPECTED: .../omega_core/trainer.py
```

---

## 6. Raw Data Mirror Protocol (Windows USB4 Disk <-> Linux USB4 Disk)

你现在在 Windows1 与 Linux 各有一块 USB4 8T NVMe SSD，内部原始 `.7z` 数据完全一致。
为了在“未来数据发生变更”时仍保持双备份一致，采用 **manifest 驱动** 的同步流程，避免拍脑袋复制。

### 6.1 建议策略（强烈推荐）

1. 原始 `.7z` 当作 **不可变数据集**。
   - 优先只做“新增文件”的 append-only 更新。
   - 如果供应商给了修正文件，建议改名/新路径保存，不要静默覆盖旧文件。
2. 同步是“需要时执行”，不做持续实时同步（避免长时间扫描 2.6TB 目录影响磁盘寿命）。

### 6.2 生成两台机器各自的 raw manifest

在 **Windows1** 与 **Linux** 上分别运行（默认只记录 `size + mtime_ns`，很快）：

```bash
python tools/gen_raw_manifest.py --root <RAW_ROOT> --ext .7z --out <OUT_MANIFEST.jsonl>
```

如果怀疑出现“静默损坏”，可以改用强校验（慢，但最可靠）：

```bash
python tools/gen_raw_manifest.py --root <RAW_ROOT> --ext .7z --hash sha256 --out <OUT_MANIFEST.jsonl>
```

### 6.3 比对 manifest 并生成差异清单

在任意一台机器（通常是 Mac 控制塔）执行：

```bash
python tools/compare_raw_manifests.py \
  --a <manifest_source_of_truth.jsonl> \
  --b <manifest_mirror.jsonl> \
  --out-missing-in-b audit/runtime/v52/raw_missing_or_changed_in_mirror.txt
```

`raw_missing_or_changed_in_mirror.txt` 是一个 **相对路径 files-from 列表**：包含 mirror 端缺失或变更的文件。

### 6.4 同步建议（按你的环境选一个）

- Linux 友好：`rsync --files-from=...` 通过局域网/SSH 拉取缺失文件。
- 跨平台统一：`rclone copy`（Windows + Linux 都可用）。
- Windows-only：`robocopy`（按“缺失/更新”复制）。

同步完成后：两端重新生成 manifest，再次 compare，确认 `missing_in_b == 0` 且 `changed_in_b == 0`。
