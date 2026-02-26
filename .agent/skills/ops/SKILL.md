---
name: ops
description: Cluster operations, deployment, and monitoring for OMEGA's multi-node architecture.
---

# Skill: ops

## When To Use

- Deploying code to worker nodes
- Diagnosing cluster health issues
- Managing Stage 1/2 pipeline runs
- Troubleshooting SSH connectivity or git sync

## Architecture

```
Mac (Controller)  ──SSH──>  Linux (zepher-linux, 192.168.3.113)
                  ──SMB──>  Windows (DESKTOP-41JIDL2, 192.168.3.112)
```

Workers are on isolated LANs — they cannot reach GitHub or the internet.

## Deployment (Hassle-Free Protocol)

```bash
# Step 1: Commit locally
git add . && git commit -m "..."

# Step 2: Push to workers
python3 tools/deploy.py              # full deploy
python3 tools/deploy.py --dry-run    # preview only
python3 tools/deploy.py --nodes linux # single node

# Step 3: Verify
python3 tools/cluster_health.py      # check all nodes
```

## Banned Operations

- ❌ `scp` for code (destroys git hash integrity)
- ❌ `git pull origin` on workers (they have no internet — will hang forever)
- ❌ Deploying dirty working tree (commit first)

## Monitoring Commands

```bash
# Full cluster status
python3 tools/cluster_health.py

# Environment consistency
python3 tools/env_verify.py --strict

# Quick health (skip slow checks)
python3 tools/cluster_health.py --quick
```

## Lessons from Production ($43 Costly Lessons)

1. **Canary before swarm**: Launch 1 worker to verify setup before launching all. We burned $13 retrying an OOM job 14 times.
2. **Never auto-retry deterministic failures**: If a job fails with OOM or ImportError, diagnose first — don't auto-restart.
3. **Compute where data lives**: Moving data between regions costs money and time. Match compute region to data bucket.
4. **VERSION.txt on startup**: Every deployment script should write commit hash + date. Check with `git rev-parse --short HEAD`.
5. **Pre-flight check**: Run `git remote -v` and `git status` before deployment to catch zombie branches.

## Key Files

- `tools/deploy.py` — one-click deployment
- `tools/cluster_health.py` — cluster status dashboard
- `tools/env_verify.py` — environment consistency check
- `handover/ops/HOSTS_REGISTRY.yaml` — node definitions
- `handover/ops/SSH_NETWORK_SETUP.md` — SSH topology
