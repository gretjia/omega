# OMEGA Active Mission Charter

Status: Completed
Task Name: V643 Stage3 holdout base-matrix build and evaluation-isolation proof
Owner: Human Owner
Commander: Codex
Date: 2026-03-09

Current checkpoint:

- The training artifact `base_matrix_train_2023_2024.parquet` is already complete and verified to contain only `2023` and `2024`.
- The optimal Stage3 allocation now requires two additional independent holdout artifacts:
  - `base_matrix_holdout_2025.parquet`
  - `base_matrix_holdout_2026_01.parquet`
- `windows1-w1` owns the relevant late-date Stage2 full-run corpus locally, including `2025*` and `202601*`.
- `linux1-lx` does not own that corpus locally.
- Prior runtime evidence showed Windows faster than Linux on the repaired path.
- Gemini externally audited the holdout execution spec and returned `PASS`.
- Execution is now complete:
  - `windows1-w1` forged `2025`
  - `linux1-lx` forged `2026-01` after Linux-local January copy
  - both clean evaluation roots were created

## 1. Objective

- Build the two missing Stage3 holdout artifacts with exact date scoping and clean downstream evaluation boundaries.
- Use idle cluster capacity efficiently without violating data locality or the canonical train/holdout split.
- Prove the resulting holdout artifacts are safe for downstream evaluation because they live outside shard workspaces and preserve exact date scope.

## 2. Canonical Spec

Primary task-level authority:

- `handover/ai-direct/entries/20260309_025500_holdout_basematrix_dual_host_execution_spec.md`
- `handover/ai-direct/entries/20260309_030257_gemini_holdout_dual_host_spec_audit.md`
- `tools/forge_base_matrix.py`

Supporting context:

- `handover/ai-direct/entries/20260309_012152_gc_swarm_optuna_project_spec.md`
- `handover/ai-direct/entries/20260309_024658_three_matrix_partition_for_stage3.md`
- `handover/ai-direct/LATEST.md`

Conflict rule:

- Date-scope isolation, clean evaluation roots, and controller authority override any convenience shortcut.
- If a proposed runtime shortcut requires Linux to read Windows parquet remotely for forge, reject it and fall back to the audited default mode.

## 3. Business Goal

- Complete the Stage3 artifact partition required for the cloud-parallel optimization roadmap:
  - train `2023,2024`
  - holdout `2025`
  - canary `2026-01`
- Do so in a way that preserves credible downstream evidence and avoids wasting wall-clock time on the slower host for the critical path.

## 4. Files In Scope

Operational scope:

- `tools/forge_base_matrix.py`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/BOARD.md`
- `handover/ai-direct/entries/20260309_025500_holdout_basematrix_dual_host_execution_spec.md`
- `handover/ai-direct/entries/20260309_030257_gemini_holdout_dual_host_spec_audit.md`

Runtime evidence scope:

- Windows-local manifests for `2025` and `202601`
- isolated holdout forge output roots
- isolated evaluation directories containing only final parquet + meta

## 5. Out of Scope

- changing canonical Stage3 gate semantics
- rebuilding the completed training artifact
- reviving cloud Optuna implementation itself
- full backtest interpretation beyond artifact and path proof
- any remote-mounted Windows parquet forge on Linux

## 6. Required Audits

Runtime audit:

- confirm the `2025` manifest contains only `2025*.parquet`
- confirm the `2026-01` manifest contains only `202601*.parquet`
- confirm each holdout forge input contract passes
- confirm each final artifact is non-empty
- confirm each evaluation directory is shard-free and date-clean

Topology audit:

- confirm `omega-vm` remains the controller
- confirm Windows-side manifest generation is invoked against Windows-local files
- confirm Linux performs only audit/controller work unless January files are copied into Linux-local storage first

## 7. Runtime and Evidence Constraints

- Default execution mode is canonical:
  - `windows1-w1` forges `2025`
  - `windows1-w1` then forges `2026-01`
  - `linux1-lx` runs validation / audit / cloud-controller work in parallel
- Optimized dual-host mode is allowed only if:
  - `202601*.parquet` is copied into Linux-local storage first
  - the copied subset is re-asserted locally before forge
- `2026-01` scope must be defined by explicit manifest, not by `--years 2026` alone
- Downstream evaluation must never point at a forge workspace that still contains shard parquet files

## 8. Acceptance Criteria

1. `base_matrix_holdout_2025.parquet` is forged successfully and contains only `2025`.
2. `base_matrix_holdout_2026_01.parquet` is forged successfully and contains only `202601`.
3. Each holdout artifact lives in a separate clean evaluation directory with only final parquet + meta.
4. No holdout evaluation reads from the training artifact.
5. Default mode uses Windows as the primary forge node for both artifacts unless a named blocking reason forces a deviation.
6. If Linux forges January in optimized mode, the January subset was copied locally and re-asserted before forge.
7. Handover records exact manifests, paths, row counts, host assignments, and verdicts.

## 9. Fail-Fast Conditions

- If `2025` forge is moved to Linux while Windows is healthy and idle without a named blocker, stop.
- If Linux attempts forge from remotely mounted Windows parquet, stop.
- If `2026-01` artifact scope depends only on `--years 2026`, stop.
- If evaluation roots contain shard parquet or mixed-year files, stop.
- If any holdout artifact includes out-of-scope dates, stop.

## 10. Definition of Done

- both holdout artifacts are built
- both artifact scopes are exact
- both evaluation roots are clean
- audited host allocation was followed or any deviation was explicitly justified
- handover updated with commands, paths, and verdicts

## 11. Run Manifest

Recorded starting facts:

- controller:
  - `omega-vm`
- primary forge node:
  - `windows1-w1`
- secondary audit/controller node:
  - `linux1-lx`
- active training artifact already complete:
  - `/omega_pool/parquet_data/stage3_base_matrix_train_20260308_095850/base_matrix_train_2023_2024.parquet`
- holdout build spec verdict:
  - Gemini `PASS`
- live capacity sample at audit time:
  - `linux1-lx`: no active Stage2 / Stage3 / train process; about `24 GiB` available memory
  - `windows1-w1`: no active `python` compute process; about `86.7 / 95.8 GiB` free/total memory
- final execution verdict:
  - `2025` holdout:
    - `base_rows=385674`
    - `date_min=20250102`
    - `date_max=20251230`
    - clean eval root:
      - `D:\Omega_frames\stage3_holdout_2025_eval_20260309_031430`
  - `2026-01` canary:
    - `base_rows=26167`
    - `date_min=20260105`
    - `date_max=20260129`
    - clean eval root:
      - `/omega_pool/parquet_data/stage3_holdout_2026_01_eval_20260309_031248`
