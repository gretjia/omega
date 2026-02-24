# LATEST (Authoritative Multi-Agent Snapshot)

This file is the single source of current operational truth for all agents.

## 0. Update Contract

- Keep this file focused on *current* state and next actions.
- Put detailed history in `handover/ai-direct/entries/*.md`.
- Every session must update this file before handoff.

## 1. Snapshot Metadata

- `updated_at_local`: 2026-02-24 11:14:16 +0800 (CST)
- `updated_at_utc`: 2026-02-24 03:14:16 +0000 (UTC)
- `updated_by`: Codex (GPT-5)
- `controller_repo_head`: `2d25625` (before this doc refactor commit)
- `worker_repo_head_linux`: `e26f3dc` (verified 2026-02-24 11:11:15 +0800)
- `worker_repo_head_windows`: `e26f3dc5` (verified 2026-02-24 11:11:xx +0800)

## 2. Active Projects Board

| Project ID | Scope | Status | Last Verified | Owner Host |
|---|---|---|---|---|
| V62-STAGE1-LINUX | Stage1 Base_L1 for shards `0,1,2` | IN_PROGRESS | 2026-02-24 11:11 +0800 | `linux1-lx` |
| V62-STAGE2-WINDOWS | Stage2 Physics from `v62_base_l1` to `v62_feature_l2` | IN_PROGRESS | 2026-02-24 11:12 +0800 | `windows1-w1` |
| HANDOVER-REFORM | Handover folder standardization for omega-vm agent entry | IN_PROGRESS | 2026-02-24 11:14 +0800 | `omega-vm/controller` |

Detailed board:
- `handover/ops/ACTIVE_PROJECTS.md`

## 3. Runtime State (Last Verified)

### 3.1 Linux `linux1-lx` (`100.64.97.113`)

- Stage1 process running:
  - `tools/stage1_linux_base_etl.py --years 2023,2024,2025,2026 --total-shards 4 --shard 0,1,2 --workers 1`
  - Observed PID: `454287`
- Stage1 done markers:
  - `STAGE1_DONE=535` (`/omega_pool/parquet_data/v62_base_l1/host=linux1/*.parquet.done`)
- Stage2 done markers:
  - `STAGE2_DONE=0`
- Log indicates active processing on date `20260113` during verification window.

### 3.2 Windows `windows1-w1` (`100.123.90.25`)

- Stage1 status:
  - completed (`=== FRAMING COMPLETE ===`)
  - `STAGE1_DONE=191`
- Stage2 status:
  - process running (`stage2_physics_compute.py --workers 1`)
  - observed process IDs: `7568` (`cmd.exe` wrapper), `24672` (`python.exe`)
  - `STAGE2_DONE=79` (`D:\Omega_frames\v62_feature_l2\host=windows1\*.parquet.done`)

### 3.3 omega-vm Control Plane

- Tailscale exit-node topology and SSH setup are documented in:
  - `handover/ops/SSH_NETWORK_SETUP.md`
- Pipeline supervision runbook:
  - `handover/ops/OMEGA_VM_V62_PIPELINE_MONITORING_NOTES.md`

## 4. Tools and Credentials Pointers

- Tools index: `handover/ops/SKILLS_TOOLS_INDEX.md`
- Credential/access policy: `handover/ops/ACCESS_BOOTSTRAP.md`
- Non-secret host registry: `handover/ops/HOSTS_REGISTRY.yaml`
- Logs index: `handover/ops/PIPELINE_LOGS.md`

## 5. Immediate Next Actions

1. Complete handover folder refactor and push to GitHub.
2. Pull latest on `omega-vm`, then refresh `ACTIVE_PROJECTS.md` runtime counts.
3. Continue monitoring Linux Stage1 and Windows Stage2 using runbook commands.

## 6. Quick Verification Commands

```bash
# Linux snapshot
ssh linux1-lx 'pgrep -af "stage1_linux_base_etl.py|stage2_physics_compute.py" || true; find /omega_pool/parquet_data/v62_base_l1/host=linux1 -maxdepth 1 -name "*.parquet.done" | wc -l'

# Windows snapshot
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '
$s1="D:\\Omega_frames\\v62_base_l1\\host=windows1";
$s2="D:\\Omega_frames\\v62_feature_l2\\host=windows1";
"STAGE1_DONE=" + (Get-ChildItem $s1 -Filter "*.parquet.done" -File -ErrorAction SilentlyContinue).Count;
"STAGE2_DONE=" + (Get-ChildItem $s2 -Filter "*.parquet.done" -File -ErrorAction SilentlyContinue).Count
'
```

## 7. Latest Related Entries

- `handover/ai-direct/entries/20260224_041600_omega_vm_windows_connectivity_rca_fix.md`
- `handover/ai-direct/entries/20260223_stage1_status.md`

