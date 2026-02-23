# Linux Freeze Best-Practice Landed Updates

- Timestamp: 2026-02-23 00:26:30 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- Convert research conclusions into executable landing artifacts under `handover/` and repo tooling.

## 2) Completed in This Session

- Landed new Linux guarded launcher:
  - `tools/launch_linux_stage1_heavy_slice.sh`
  - Enforces `systemd-run --slice=heavy-workload.slice`, not default `user.slice`.
  - Adds `OOMPolicy=kill` and appends output to `audit/stage1_linux_v62.log`.
- Updated operations index for next agents:
  - `handover/ops/SKILLS_TOOLS_INDEX.md`
  - Added launcher path and one-line remote usage example.
- Updated runtime anchor:
  - `handover/ai-direct/LATEST.md`
  - Added research+landing summary and mandatory launcher rule for next Linux Stage1 start.
- Executed validations:
  - Local script syntax: pass.
  - Local `--help`: pass.
  - Linux host dry-run: pass.
    - confirmed `user.slice` is `16G/20G`
    - confirmed `heavy-workload.slice` is `90G/100G`
    - generated launch command correctly targets `heavy-workload.slice`.

## 3) Current Runtime Status

- Mac:
  - Landing artifacts written in workspace and handover updated.
- Windows1:
  - Unchanged in this landing session.
- Linux1:
  - Host reachable and responsive.
  - Dry-run completed; no production job was started by this update.

## 4) Critical Findings / Risks

- If operators bypass the new launcher and run Stage1 directly in a normal user session, memcg OOM regression risk remains high.
- ZFS suspend risk from storage-link disruption is still operationally relevant and requires separate hardware/link hardening.

## 5) Artifacts / Paths

- `tools/launch_linux_stage1_heavy_slice.sh`
- `handover/ops/SKILLS_TOOLS_INDEX.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/20260223_002256_linux_freeze_best_practice_research.md`
- `handover/ai-direct/entries/20260223_002630_linux_freeze_best_practice_landed_updates.md`

## 6) Commands Executed (Key Only)

- `chmod +x tools/launch_linux_stage1_heavy_slice.sh`
- `bash -n tools/launch_linux_stage1_heavy_slice.sh`
- `bash tools/launch_linux_stage1_heavy_slice.sh --help`
- `scp tools/launch_linux_stage1_heavy_slice.sh zepher@192.168.3.113:/home/zepher/work/Omega_vNext/tools/launch_linux_stage1_heavy_slice.sh`
- `ssh zepher@192.168.3.113 'cd /home/zepher/work/Omega_vNext && bash tools/launch_linux_stage1_heavy_slice.sh --dry-run -- --years 2026 --total-shards 4 --shard 0,1,2 --workers 1'`

## 7) Exact Next Steps

1. Start next Linux Stage1 run only through:
   - `bash tools/launch_linux_stage1_heavy_slice.sh -- --years 2023,2024,2025,2026 --total-shards 4 --shard 0,1,2 --workers 1`
2. Watch `journalctl -u <unit>` and `audit/stage1_linux_v62.log` for first `DONE` marker.
3. If ZFS suspend signature reappears (`zio ... error=5`, `pool suspended`), pivot to storage-link incident workflow before restarting ETL.
