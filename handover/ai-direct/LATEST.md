# LATEST (Authoritative Multi-Agent Snapshot)

This file is the single source of current operational truth for all agents.

## 0. Update Contract

- Keep this file focused on current state and next actions.
- Put detailed history in `handover/ai-direct/entries/*.md`.
- Every session must update this file before handoff.

## 1. Snapshot Metadata

- `updated_at_local`: 2026-02-24 16:53:12 +0800 (CST)
- `updated_at_utc`: 2026-02-24 08:53:12 +0000 (UTC)
- `updated_by`: Codex (GPT-5)
- `controller_repo_head`: `e682bf5` (pre-rebase)
- `worker_repo_head_linux`: `e26f3dc` (pre-sync)
- `worker_repo_head_windows`: `b42f110` (pre-sync)

## 2. Active Projects Board

| Project ID | Scope | Status | Last Verified | Owner Host |
|---|---|---|---|---|
| V62-STAGE1-LINUX | Stage1 Base_L1 for shards `0,1,2` | COMPLETED | 2026-02-24 16:47 +0800 | `linux1-lx` |
| V62-STAGE2-WINDOWS | Stage2 Physics from `v62_base_l1` to `v62_feature_l2` | IN_PROGRESS | 2026-02-24 16:53 +0800 | `windows1-w1` |
| V62-STAGE2-LINUX | Stage2 Physics for `host=linux1` | BLOCKED (dependency) | 2026-02-24 16:53 +0800 | `linux1-lx` |
| HANDOVER-MAINTENANCE | keep handover as entrypoint + run-state truth | IN_PROGRESS | 2026-02-24 16:53 +0800 | `controller` |

Detailed board:
- `handover/ops/ACTIVE_PROJECTS.md`

## 3. Runtime State (Last Verified)

### 3.1 Linux `linux1-lx` (`100.64.97.113`)

- Stage1 status:
  - completed after archive recovery and backfill rerun
  - final unit: `omega_stage1_linux_20260224_160352.service`
  - final metrics: `ASSIGNED=555`, `COMPLETED=10`, `SKIPPED=545`, `ERROR=0`, `FRAMING_COMPLETE=1`
  - `STAGE1_DONE=552` (`/omega_pool/parquet_data/v62_base_l1/host=linux1/*.parquet.done`)
- Stage2 status:
  - currently not running
  - blocker: `.venv` missing `numba` (`ModuleNotFoundError`)
  - `LNX_STAGE2_DONE=0`

### 3.2 Windows `windows1-w1` (`100.123.90.25`)

- Stage1 status:
  - completed (`STAGE1_DONE=191`)
- Stage2 status:
  - running process: `stage2_physics_compute.py --workers 1`
  - snapshot: `WIN_STAGE2_DONE=113 / 191`
  - active log: `D:\work\Omega_vNext\audit\stage2_compute.log`

### 3.3 Data Recovery Note

Recovered broken Linux archives from Windows verified copies:
- `20241104, 20241107, 20241111, 20241113, 20241114, 20241115, 20241119, 20241121, 20241202, 20241211, 20241204, 20241212`

Historical broken files are kept as backups:
- `*.7z.bad_20260224_*`

## 4. Tools and Credentials Pointers

- Tools index: `handover/ops/SKILLS_TOOLS_INDEX.md`
- Credential/access policy: `handover/ops/ACCESS_BOOTSTRAP.md`
- Non-secret host registry: `handover/ops/HOSTS_REGISTRY.yaml`
- Logs index: `handover/ops/PIPELINE_LOGS.md`

## 5. Immediate Next Actions (User-Directed Sequence)

1. Sync updated `handover/` docs to GitHub.
2. Run `git pull` on `windows1`, `linux1`, and `omega-vm`.
3. Install `numba` into Linux `.venv` if still missing.
4. Start Linux Stage2 in `heavy-workload.slice`.
5. Verify Linux Stage2 done-marker growth.

## 6. Quick Verification Commands

```bash
# Windows Stage2
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '
$in="D:\\Omega_frames\\v62_base_l1\\host=windows1";
$out="D:\\Omega_frames\\v62_feature_l2\\host=windows1";
"WIN_STAGE2=" + (Get-ChildItem $out -Filter "*.parquet.done" -File -ErrorAction SilentlyContinue).Count + "/" + (Get-ChildItem $in -Filter "*.parquet" -File -ErrorAction SilentlyContinue).Count
'

# Linux Stage2 dependency gate
ssh linux1-lx '/home/zepher/work/Omega_vNext/.venv/bin/python -c "import numba, llvmlite; print(numba.__version__, llvmlite.__version__)"'
```

## 7. Latest Related Entries

- `handover/ai-direct/entries/20260224_165312_linux_stage1_repair_and_stage2_gate.md`
- `handover/ai-direct/entries/20260224_041600_omega_vm_windows_connectivity_rca_fix.md`

