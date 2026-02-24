# Active Projects Board

This file tracks in-flight initiatives. `handover/ai-direct/LATEST.md` remains the single current-state summary; this board stores slightly deeper operational context.

## 1. Snapshot Metadata

- `updated_at_local`: 2026-02-24 11:14:16 +0800
- `updated_at_utc`: 2026-02-24 03:14:16 +0000
- `updated_by`: Codex (GPT-5)

## 2. In-Flight Work

### Project: V62-STAGE1-LINUX

- Status: `IN_PROGRESS`
- Host: `linux1-lx`
- Goal: complete Stage1 Base_L1 for shards `0,1,2`
- Last signals:
  - active process observed (`stage1_linux_base_etl.py --workers 1`)
  - `STAGE1_DONE=535`
  - worker git head: `e26f3dc`
- Risks:
  - long-running ETL session stability (network + host pressure)
- Next check:
  - monitor done-marker growth and log tail every 20 minutes

### Project: V62-STAGE2-WINDOWS

- Status: `IN_PROGRESS`
- Host: `windows1-w1`
- Goal: produce Feature_L2 from completed Stage1 Base_L1
- Last signals:
  - Stage1 complete marker present (`=== FRAMING COMPLETE ===`)
  - Stage2 process observed (`stage2_physics_compute.py --workers 1`)
  - `STAGE2_DONE=79`
  - worker git head: `e26f3dc5`
- Risks:
  - Stage2 log redirection inconsistency across `C:\Omega_vNext` and `D:\work\Omega_vNext`
- Next check:
  - keep done-marker trend and process uptime checks

### Project: HANDOVER-REFORM

- Status: `IN_PROGRESS`
- Host: `omega-vm/controller repo`
- Goal: make `handover/` a strict agent gateway with topology/tools/credentials/active-project clarity
- Scope:
  - rewrite entry docs and template
  - add project topology and best-practice rationale
  - enforce `LATEST.md` as single-source current truth
- Next check:
  - run consistency review, commit, push, and sync to omega-vm

## 3. Completed Recently

- `windows1` Stage1 shard completion (`STAGE1_DONE=191`, framing complete marker).
- omega-vm -> windows intermittent reachability RCA and hardening (entry: `20260224_041600_omega_vm_windows_connectivity_rca_fix.md`).

## 4. Update Rules

- Update this board when project state changes materially.
- Keep exact verification timestamps and host evidence.
- Mirror high-level status in `handover/ai-direct/LATEST.md`.

