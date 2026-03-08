# OMEGA Active Mission Charter

Status: Active
Task Name: V643 Stage2 pathological empty-frame remediation and Stage3 forge consumption proof
Owner: Human Owner
Commander: Codex
Date: 2026-03-08

Current checkpoint:

- `windows1-w1` main Stage2 run originally produced six failures; four are already resolved by replacing complete files from Linux and rerunning.
- A direct Linux rerun on the normal current `v643` Stage2 path reproduced the same failure pattern on all three unresolved files:
  - `[GUARDRAIL] Proactively dropping pathological symbol ...`
  - immediate `CRITICAL Error: index out of bounds`
- The mission was then executed with the Stage2 control-flow hardening patch at commit `23fd229`.
- `windows1-w1` isolated normal-path validation passed for all three previously unresolved files:
  - `20231219_b07c2229.parquet` -> `252844` rows in `86.5s`
  - `20241128_b07c2229.parquet` -> `253227` rows in `128.1s`
  - `20250908_fbd5c8b.parquet` -> `254884` rows in `169.6s`
- `windows1-w1` isolated Stage3 forge proof also passed on the three-file set using explicit `--input-file-list` and `--years 2023,2024,2025`:
  - forge input contract: `rows=760955`, `physics_valid_rows=760955`, `epi_pos_rows=716`, `topo_energy_pos_rows=4404`, `signal_gate_rows=3897`
  - forge output: `base_rows=3074`
- `linux1-lx` post-patch mirror validation could not be run in this window because `ssh linux1-lx` timed out from the controller.
- The user-required Stage3 whole-set consumption proof is satisfied; any remaining Linux rerun is now a follow-up decision, not an evidence gap on whole-set usability.

## 1. Objective

- Fix the Stage2 normal symbol-stream path so proactive pathological-symbol drops do not crash unresolved files.
- Preserve the approved `v643` math, feature schema, and normal execution path.
- Prove the repaired three-file set can be consumed together by Stage3 forge as one coherent input set.

## 2. Canonical Spec

Primary task-level implementation authority:

- `tools/stage2_physics_compute.py`
  - `_iter_complete_symbol_frames_from_parquet(...)`
  - `_filter_pathological(...)`
  - `process_chunk(...)`
- `tools/forge_base_matrix.py`
  - `_audit_forge_l2_contract(...)`
  - CLI year filtering and `--input-file-list` handling

Supporting context:

- `tests/test_stage2_pathological_symbol_skip.py`
- `handover/ai-direct/entries/20260226_154217_windows_stage2_pathological_symbol_debug_fix.md`
- `handover/ai-direct/LATEST.md`

Conflict rule:

- This mission may harden Stage2 control flow and test coverage.
- It must not silently change `omega_core/` math or Stage3 gating semantics.
- If a proposed fix requires changing canonical math or downstream contract definitions, escalate to the Commander.

## 3. Business Goal

- Remove the deterministic blocker preventing the last unresolved Stage2 files from completing on the normal `v643` path.
- Avoid wasting time on the slow fallback/pathology-discovery route.
- Unblock downstream base-matrix generation by proving the repaired outputs are consumable together, not merely individually written.

## 4. Files In Scope

Primary implementation scope:

- `tools/stage2_physics_compute.py`
- `tests/test_stage2_pathological_symbol_skip.py`
- `tests/test_stage2_pathological_empty_frame.py` (new, if needed)

Operational and evidence scope:

- `tools/forge_base_matrix.py`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ai-direct/LATEST.md`
- `handover/BOARD.md`
- `handover/ai-direct/entries/20260308_085506_stage2_pathological_empty_frame_mission_spec.md`

## 5. Out of Scope

- `omega_core/*` mathematical formulas or canonical V64.3 semantics
- `tools/stage2_targeted_resume.py` timeout tuning
- `OMEGA_STAGE2_FORCE_SCAN_FALLBACK` / slow pathology-discovery flow
- Stage1 rebuilds or input parquet reconstruction
- full-queue Stage2 relaunches on either worker
- Stage3 training or backtest validation beyond forge/base-matrix consumption proof

## 6. Required Audits

Math audit:

- confirm no `omega_core/` math or downstream canonical gate semantics were changed
- confirm the fix is pure Stage2 control-flow hardening

Runtime audit:

- confirm the three unresolved files pass on the normal Stage2 path without forced scan fallback
- confirm the repaired three-file L2 set passes `forge_base_matrix.py` input contract as one input set
- confirm Stage3 forge validation explicitly uses `--years 2023,2024,2025` so the 2025 file is not silently excluded

## 7. Runtime and Evidence Constraints

- Validation node: `linux1-lx` first, then `windows1-w1` for the two Windows-owned files only if Linux validation passes
- Use the current normal `v643` Stage2 path; do not enable forced scan fallback
- Use isolated output roots for reruns and forge validation; do not pollute authoritative `latest_feature_l2`
- Before any worker validation, respect the controller-managed deploy path and code-freshness rules
- Stage3 validation must use `tools/forge_base_matrix.py --input-file-list ... --years 2023,2024,2025`
- Mission completion requires one isolated forge/base-matrix proof for the repaired three-file set

## 8. Acceptance Criteria

1. Stage2 no longer fails with `index out of bounds` immediately after the pathological guardrail on the three unresolved files.
2. New or updated regression coverage proves proactively dropped empty symbol frames do not crash the normal non-fallback path.
3. Existing pathological crash-skip coverage still passes.
4. The repaired three-file L2 set is forged together through `tools/forge_base_matrix.py` in an isolated workspace.
5. Forge input contract passes for that three-file set:
   - required columns present
   - non-empty L2 input set
   - positive `physics_valid_rows`
   - positive `epi_pos_rows`
   - positive `topo_energy_pos_rows`
   - positive `signal_gate_rows`
6. A non-empty `base_matrix.parquet` and matching meta artifact are produced from the repaired three-file set.
7. Handover is updated with exact artifacts, commands, and verdicts.

## 9. Fail-Fast Conditions

- If the fix requires changing `omega_core/*` math, stop and escalate.
- If Linux normal-path rerun still crashes for the same reason after the control-flow hardening patch, stop and capture exact new evidence before widening scope.
- If forge validation fails because one or more repaired files are structurally unusable as a set, keep the mission open; do not declare success based only on Stage2 completion.
- Retry is allowed only after a named root cause and a changed condition.

## 10. Definition of Done

- canonical Stage2 control-flow defect is repaired
- regression coverage is in place and passes
- Linux normal-path rerun passes for the three unresolved files
- Windows normal-path rerun passes for the two Windows-owned files if still needed
- isolated forge/base-matrix validation passes on the repaired three-file set
- handover updated
- Commander-only integration decision completed

## 11. Run Manifest

Recorded execution:

- commit hash: `23fd229`
- deploy path used:
  - controller push to `origin`: PASS
  - controller `tools/deploy.py --skip-commit --nodes windows`: unavailable locally because worker deploy remotes were missing
  - Windows validation host was therefore aligned manually to `23fd229` from its `github` remote for this isolated runtime proof
- linux validation workspace:
  - blocked; `ssh linux1-lx` timed out from the controller during this session
- windows validation workspace:
  - `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2`
  - runtime logs:
    - `D:\work\Omega_vNext\audit\runtime\stage2_patho_fix_validate_20260308_091554\runner.log`
    - `D:\work\Omega_vNext\audit\runtime\stage2_patho_fix_validate_20260308_20231219\runner.log`
- forge validation workspace:
  - `D:\Omega_frames\stage3_patho_fix_forge_20260308_1728`
  - input list:
    - `D:\work\Omega_vNext\audit\runtime\stage3_patho_fix_forge_20260308_1728\input_files.txt`
- unresolved file set:
  - `20231219_b07c2229.parquet`
  - `20241128_b07c2229.parquet`
  - `20250908_fbd5c8b.parquet`
- Stage2 verdict:
  - PASS on `windows1-w1` normal path for all three unresolved files
  - no forced scan fallback used
- forge verdict:
  - PASS on `windows1-w1`
  - explicit `--years 2023,2024,2025` used
  - non-empty `base_matrix.parquet` produced with `base_rows=3074`
