# Zero-Version Architecture & Codebase Cleanup Plan

**Context:** The OMEGA project suffers from severe "version pollution" where file names (e.g., `v61_linux_framing.py`, `v60_swarm_xgb.py`) bake in specific version numbers. This creates massive friction during upgrades (like V62) because internal imports, subprocess calls, and bash scripts break if file names change, or conversely, developers leave old names (running V62 logic in a file named `v61_xxx`).

**Goal:** Establish a "Zero-Version Codebase". Mathematical files and executable tools must have semantic, version-agnostic names. The *Git Commit Hash* and the *Git Tag* become the sole source of truth for the codebase version, not the file names. Non-essential legacy code must be archived.

---

## 1. Archiving Obsolete Files (The Great Purge)

Move all legacy, superseded, and standalone log files into the `archive/` folder to clear the workspace noise.

**Target Files to Move:**

- `omega_core/trainer_v51.py`
- `omega_core/trainer_v60_xgb.py` (assuming `trainer.py` or new structure supersedes)
- `tools/v60_autopilot.py`, `tools/v60_autopilot.py.bak`
- `tools/v60_multi_agent_*.py`
- `tools/v60_build_base_matrix.py` (legacy stub)
- `tools/v5_auditor_report.py`, `tools/v40_*.py`
- `tools/v61_watchdog.py` (superseded by `v62_night_watchdog.py`)
- `patch_autopilot_windows_only.py`, `replace_bucket_refs.py`
- All loose `.log`, `.err.log`, `.bak`, and `.bundle` files in root.
- All loose PowerShell `.ps1` and Batch `.bat` scripts in root related to older versions.

---

## 2. The Zero-Version Renaming Protocol

Rename the active operational scripts to remove `vXX_` prefixes.

**Tool Renames:**

- `tools/v61_linux_framing.py` -> `tools/linux_framing.py`
- `tools/v61_windows_framing.py` -> `tools/windows_framing.py`
- `tools/v60_forge_base_matrix_local.py` -> `tools/forge_base_matrix.py`
- `tools/v60_swarm_xgb.py` -> `tools/swarm_xgb.py`
- `tools/v61_run_local_backtest.py` -> `tools/run_local_backtest.py`
- `v62_night_watchdog.py` -> `tools/night_watchdog.py`
- `tests/verify_v61_pipeline.py` -> `tests/verify_pipeline.py`

---

## 3. Reference Refactoring (Cross-Codebase Updates)

After renaming, internal references must be updated to prevent runtime failures:

**Python Imports:**
`from tools.v60_forge_base_matrix_local import ...` -> `from tools.forge_base_matrix import ...`
(Present in `tests/verify_pipeline.py`, etc.)

**Subprocess Dispatch/Watchdogs:**
Files like `tools/night_watchdog.py` contain literal strings launching subprocesses:
`["python3", "tools/v61_linux_framing.py"]` -> `["python3", "tools/linux_framing.py"]`

**Data Output Paths:**
Scripts containing hardcoded storage paths (e.g., `D:\Omega_frames\v61\host=windows1` or `/omega_pool/parquet_data/v61`) must either:

1. Extract the active version from `config.py` (e.g., `args.version` or `GLOBAL_CFG.pipeline_version`).
2. Be parameterized via CLI: `--output-dir /omega_pool/parquet_data/v62`.
*This will be handled dynamically during the Phase 2 Framing Decoupling execution.*

---

## Execution Directives

This cleanup phase should be executed as a dedicated "Phase 0" before diving into the mathematical restructuring of V62, ensuring the workspace is pristine and future-proof.
