---
name: engineering
description: Code quality, testing, and refactoring standards for OMEGA.
---

# Skill: engineering

## When To Use

- Refactoring existing code
- Adding new modules or functions
- Reviewing PRs or performing code audits
- Setting up CI/CD or test infrastructure

## Code Standards

1. **Python 3.9+** with type hints on all function signatures
2. **Docstrings** on all public functions (purpose, params, returns)
3. **No hardcoded paths** — use `configs/node_paths.py` for host-specific paths, `config.py` for math parameters
4. **Polars over Pandas** — all new data pipelines must use Polars LazyFrames
5. **Atomic writes** — parquet outputs use `.tmp` → `rename()` pattern to prevent corrupted files on crash

## Testing Requirements

| Test Type | Command | When Required |
|---|---|---|
| Math invariants | `pytest tests/test_omega_math_core.py` | Any math change |
| Output equivalence | `pytest tests/test_stage2_output_equivalence.py` | ETL/pipeline refactors |
| Env verification | `python3 tools/env_verify.py --strict` | Before deployment |

## Refactoring Checklist

Before refactoring any module:

1. ✅ Run existing tests first — establish baseline
2. ✅ Check `__init__.py` shims — renaming files may break import paths
3. ✅ Check `handover/DEBUG_LESSONS.md` — has this been tried before?
4. ✅ Check cross-module imports — `grep -r "from old_module"` across codebase
5. ✅ Run tests after — zero regressions allowed

## Lessons Learned (from DEBUG_LESSONS.md)

- **Refactoring residue**: When renaming files, always check `__init__.py` shims for stale import paths
- **Recursive import audit**: Always check dependencies of imported modules when moving code to new environments
- **Schema contracts**: Never hardcode column names (e.g., `"time"`) — derive dynamically and fail fast if missing
- **GC in hot loops**: `gc.collect()` inside inner loops kills Numba/Polars performance. Remove.
