# OMEGA Multi-Machine Git Hub Workflow

Last updated: 2026-02-12

## Goal

Use one code hub for `mac + windows1 + windows2`, while keeping heavy mutable data local.

This avoids:
- manual copy/paste for every upgrade
- branch drift between machines
- slow full-folder sync for `data/` and `artifacts/`

## Recommended Topology

- `windows1` hosts a **bare** Git repository (hub).
- `mac` is a development/publish node (pushes code).
- `windows1` and `windows2` are execution nodes (pull latest code).
- `data/`, `artifacts/`, runtime logs remain local on each machine and stay out of Git.

## Repo Hygiene (already aligned)

The repository already ignores large mutable directories in `.gitignore`, including:
- `data/`
- `artifacts/`
- `archive/`

Do not remove these ignore rules.

## One-Time Setup

### 1) On windows1: initialize hub

Run in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File tools\git_sync\windows_init_hub.ps1 `
  -SourceRepoPath C:\Omega_vNext `
  -BareHubPath C:\Git\Omega_vNext.git `
  -RemoteName hub
```

This will:
- create/validate `C:\Git\Omega_vNext.git` as a bare repo
- configure remote `hub` in `C:\Omega_vNext`
- push all branches/tags to `hub`

### 2) On mac: add hub remote

```bash
cd /path/to/Omega_vNext
git remote add hub "ssh://<user>@windows1/C:/Git/Omega_vNext.git"
```

If `hub` already exists:

```bash
git remote set-url hub "ssh://<user>@windows1/C:/Git/Omega_vNext.git"
```

### 3) On windows2: clone from hub

```powershell
git clone "ssh://<user>@windows1/C:/Git/Omega_vNext.git" C:\Omega_vNext
cd C:\Omega_vNext
git remote rename origin hub
```

## Daily Workflow

### A) One-click publish + rollout from mac (recommended)

```bash
cd /path/to/Omega_vNext
./tools/git_sync/mac_publish_and_rollout.sh --remote hub --branch main
```

Release publish with tag:

```bash
./tools/git_sync/mac_publish_and_rollout.sh --remote hub --branch main --tag v2026.02.12-r1
```

Specify rollout targets:

```bash
./tools/git_sync/mac_publish_and_rollout.sh --remote hub --branch main --hosts windows1-w1,windows2-w2
```

### B) Publish only from mac (without rollout)

```bash
cd /path/to/Omega_vNext
./tools/git_sync/mac_publish_to_hub.sh --remote hub --branch main
```

Release publish with tag:

```bash
./tools/git_sync/mac_publish_to_hub.sh --remote hub --branch main --tag v2026.02.12-r1
```

### C) Update windows1/windows2

```powershell
powershell -ExecutionPolicy Bypass -File tools\git_sync\windows_update_from_hub.ps1 `
  -RepoPath C:\Omega_vNext `
  -RemoteName hub `
  -Branch main
```

This script:
- fetches latest refs and tags
- switches to target branch
- pulls with `--ff-only` to avoid hidden merge commits

## Branch and Release Rules

- Develop on feature branches.
- Merge to `main` only after verification.
- Use tags for deployment milestones.
- Windows execution nodes should update from a known branch/tag, not ad-hoc local commits.

## Data Strategy

- Keep code and scripts in Git.
- Keep parquet/checkpoints/logs local.
- For cross-machine data transfer, use dedicated tools (`robocopy`, `rsync`, external SSD), not Git.

## Quick Recovery

If a machine has bad local changes and cannot fast-forward:

1. Commit or stash local changes.
2. Re-run `windows_update_from_hub.ps1`.
3. If still blocked, clone a fresh working copy from the hub.
