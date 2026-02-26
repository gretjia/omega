# Claude Agent Entry Point

> **All agent rules are in [`AGENTS.md`](AGENTS.md).** Read that file first.

This file exists because Claude Code and some Claude-based tools auto-load `CLAUDE.md`.
It is a pointer — do not add rules here. All rules belong in `AGENTS.md`.

## Quick Context for Claude

- **Project:** OMEGA vNext — quant trading system (Python 3.9+, Polars, Numba)
- **Constitution:** `OMEGA_CONSTITUTION.md` — read before any physics task
- **Project manual:** `handover/README.md` — complete file map and onboarding
- **Live state:** `handover/ai-direct/LATEST.md`
- **Math kernels:** `omega_core/omega_math_core.py`, `omega_core/kernel.py`
- **Config:** `config.py` (math params), `configs/node_paths.py` (host paths)
- **Tests:** `python3 -m pytest tests/ -q`

## References

- [AGENTS.md](AGENTS.md) — Unified agent rules and protocols
- [handover/README.md](handover/README.md) — Full project manual
- [.agent/principles.yaml](.agent/principles.yaml) — Machine-readable rules
