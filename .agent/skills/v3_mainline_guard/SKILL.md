---
name: v3_mainline_guard
description: Enforce omega_v3_core as the default mainline and keep root-level legacy files as compatibility shims only.
---

# v3 Mainline Guard

Use this skill whenever a task touches trading logic, math kernels, trainers, adapters, or project architecture.

## Canonical Routing

- Active mainline:
  - `omega_v3_core/kernel.py`
  - `omega_v3_core/omega_math_core.py`
  - `omega_v3_core/trainer.py`
- Legacy source:
  - `legacy_model/v1/*`
- Compatibility shims only:
  - root `kernel.py`, `omega_math_core.py`, `trainer.py`, `feature_extractor.py`, `data_adapter.py`, `artifact_loader.py`

Default rule:
- If user does not explicitly request v1 maintenance, implement in `omega_v3_core/*`.

## Mandatory Workflow

1. Classify request target:
   - `v3` by default
   - `v1` only when explicitly requested
2. Apply edits only in the chosen mainline.
3. If root shim files are touched:
   - keep them as thin forwarding wrappers only
   - do not add business logic there
4. Keep docs/rules aligned with v3 core paths.

## Quick Verification

```bash
python3 tools/sync_agent_rules.py --check
```

```bash
grep -nE "versions/v1300|qmt_v1300" \
  README.md .vscode/launch.json .codex/rules.md .gemini/context.md .trae/instruction.md .cursorrules
```

Any hit in active docs/rules is a migration drift and must be resolved.
