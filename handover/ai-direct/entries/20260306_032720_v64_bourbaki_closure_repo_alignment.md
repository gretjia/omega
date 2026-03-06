---
entry_id: 20260306_032720_v64_bourbaki_closure_repo_alignment
task_id: TASK-V64-BOURBAKI-CLOSURE-REPO-ALIGNMENT
timestamp_local: 2026-03-06 03:27:20 +0000
operator: Codex
role: agent
branch: main
tags: [v64, bourbaki-closure, kernel, stage3, tests, handover]
---

## 1. What changed
- Aligned the canonical kernel/config path with the final `Bourbaki Closure` override in `audit/v64.md`.
- Finalized `config.py` / `omega_core/kernel.py` / `omega_core/trainer.py` semantics around:
  - `signal_epi_threshold`
  - `brownian_q_threshold`
  - `topo_energy_min`
  - zero-variance -> zero signal
- Aligned Stage 3 runtime scripts so canonical names are primary:
  - `tools/forge_base_matrix.py`
  - `tools/run_vertex_xgb_train.py`
  - `tools/stage3_full_supervisor.py`
  - `tools/run_v64_smoke_backtest.py`
- Added `tests/test_v64_absolute_closure.py` to lock the four Bourbaki audit points.
- Updated `README.md` with a Bourbaki Closure section and legacy-name -> canonical-semantics mapping.
- Rewrote `tools/apply_v641_hotfix.py` into a non-authoritative compatibility breadcrumb so operators do not mistake it for the canonical implementation.

## 2. Validation
- `python3 -m py_compile` passed for all changed Python files.
- `uv run --python /usr/bin/python3.11 --with pytest --with numpy==1.26.4 --with numba==0.60.0 pytest tests/test_v64_absolute_closure.py tests/test_omega_math_core.py -q`
  - Result: `32 passed in 8.98s`
- External `gemini` audit verdict on current code state: `PASS`
  - No required fixes.

## 3. Compatibility / semantics notes
- Legacy names (`peace_threshold`, `peace_threshold_baseline`, `topo_energy_sigma_mult`) survive only as:
  - CLI aliases
  - resume-context normalization
  - explicit `legacy_compat` metadata blocks
  - documentation mapping tables
- Canonical runtime semantics are now:
  - `signal_epi_threshold`
  - `singularity_threshold`
  - `topo_energy_min`
- `omega_core/trainer.py` still accepts `peace_threshold` as a legacy keyword alias for evaluation helpers to avoid breaking old call sites.

## 4. Next agent should do
1. Use canonical Stage 3 flags first; only fall back to legacy aliases for backward compatibility.
2. If Stage 3 is launched, prefer the updated `tools/stage3_full_supervisor.py` canonical arguments.
3. If resume metadata predates this rollout, the forge resume normalizer should map old keys; if not, rerun with `--no-resume`.
4. Continue normal runtime monitoring from `handover/ai-direct/LATEST.md`.
