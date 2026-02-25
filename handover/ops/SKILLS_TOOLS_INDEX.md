# Skills and Tools Index

This file is the fast operational index for executable skills and pipeline tools.

## 1. AI Skills (Primary)

| Skill | Path | Use Case |
|---|---|---|
| multi-agent-ops | `.codex/skills/multi-agent-ops/SKILL.md` | governance checks, profile switching, memory refresh, recursive audit flow |
| omega-run-ops | `.codex/skills/omega-run-ops/SKILL.md` | multi-host operations (Linux/Windows over SSH) |
| v60-multi-agent-ops | `.codex/skills/v60-multi-agent-ops/SKILL.md` | compatibility alias of `multi-agent-ops` |

## 2. Governance Commands

```bash
python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair
python3 .codex/skills/multi-agent-ops/scripts/switch_profile.py --oracle codex_xhigh --mechanic gemini_flash --auditor-primary gemini_pro --auditor-secondary codex_xhigh --debug-scribe codex_medium
```

## 3. Pipeline Tools (v62)

### 3.1 Stage 1 Base Lake

- Linux: `tools/stage1_linux_base_etl.py`
- Linux guarded launcher: `tools/launch_linux_stage1_heavy_slice.sh`
- Windows: `tools/stage1_windows_base_etl.py`
- Shared helper: `tools/stage1_incremental_writer.py`
- Resume helper: `tools/stage1_resume_utils.py`
- Shard builder: `tools/build_7z_shards.py`

### 3.2 Stage 2 Physics

- `tools/stage2_physics_compute.py` (Linux hard-guard: refuse non-`heavy-workload.slice` unless override env)
- `tools/stage2_targeted_resume.py` (per-file timeout isolation + deterministic pending/failed ledgers)
- `tools/launch_linux_stage2_heavy_slice.sh` (systemd-run launcher pinned to `heavy-workload.slice`)

### 3.3 Stage 2.5 Base Matrix

- `tools/forge_base_matrix.py`
- compatibility check: `tools/check_frame_train_backtest_compat.py`

### 3.4 Stage 3 Train/Backtest

- Vertex train launcher: `tools/run_vertex_xgb_train.py`
- Local backtest: `tools/run_local_backtest.py`
- GCS upload helper: `tools/gcp_upload.py`

## 4. Host Operations and Monitoring Tools

- Agent preflight: `tools/agent_handover_preflight.sh`
- Linux runtime preflight: `tools/linux_runtime_preflight.py`
- Linux preflight timer installer: `tools/install_linux_preflight_timer.sh`
- Windows probe from omega-vm: `tools/check_windows_from_omega.sh`
- Windows PowerShell over SSH wrapper: `.codex/skills/omega-run-ops/scripts/ssh_ps.py`
- Linux night watchdog: `tools/night_watchdog.py`

## 5. Core Code Modules

- ETL engine: `omega_core/omega_etl.py`
- Physics kernel: `omega_core/kernel.py`
- Numerical core: `omega_core/omega_math_core.py`
- Rolling math: `omega_core/omega_math_rolling.py`

## 6. Quick Command Patterns

### Linux status

```bash
ssh linux1-lx 'pgrep -af "stage1_linux_base_etl.py|stage2_physics_compute.py|stage2_targeted_resume.py" || true'
```

### Windows status

```bash
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '
Get-CimInstance Win32_Process | Where-Object {
  $_.CommandLine -like "*stage1_windows_base_etl.py*" -or
  $_.CommandLine -like "*stage2_physics_compute.py*"
} | Select-Object ProcessId,Name,CommandLine | Format-List
'
```

### List all repository tools

```bash
find tools -maxdepth 1 -type f | sort
```
