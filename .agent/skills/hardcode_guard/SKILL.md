---
name: hardcode_guard
description: Detect and prevent hardcoded values that cause multi-node deployment failures.
---

# Skill: hardcode_guard

## When To Use

- Reviewing any code that touches file paths, IP addresses, or hostnames
- Before deploying to worker nodes (Linux/Windows)
- When adding new tools or scripts

## What to Catch

| Category | Bad Example | Correct Pattern |
|---|---|---|
| Host paths | `/home/zepher/framing_cache` | `NODE.cache_dir` from `configs/node_paths.py` |
| IP addresses | `192.168.3.113` | SSH alias from `HOSTS_REGISTRY.yaml` |
| Windows paths | `D:\\Omega_frames\\...` | `NODE.stage1_output` from `configs/node_paths.py` |
| Column names | `df["time"]` | Dynamic resolution: `time|time_end|bucket_id` |
| Git hashes | `cb6e609` in scripts | `git rev-parse --short HEAD` at runtime |
| Model names | `"Codex 5.3 xhigh"` | Role-based: `"orchestrator"`, `"implementer"` |
| Version strings | `v62_base_l1` in 10 scripts | Single constant in `configs/` |

## Quick Scan Command

```bash
# Find hardcoded paths in tools/
grep -rn '/omega_pool/\|/home/zepher\|D:\\\\' tools/ --include='*.py'

# Find hardcoded IPs
grep -rn '192\.168\.3\.' tools/ --include='*.py'
```

## Lesson: The Zombie Branch Incident

Hardcoded version strings (`v52` scattered in file paths) caused the "zombie branch" incident where a worker node appeared functional but was running v52 code against v60 data. Always use `VERSION.txt` + git hash verification.

## Prevention

New code must use:

```python
from configs.node_paths import get_node_config
cfg = get_node_config()  # auto-detects controller/linux1/windows1
```
