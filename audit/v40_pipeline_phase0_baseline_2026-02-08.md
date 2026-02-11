# v40 Pipeline Debug Program - Phase 0 Baseline (2026-02-08)

## Scope
- Freeze the pre-debug state before remediation phases.
- Record constitution/skill constraints and runtime evidence.
- Define the exact gate to start Phase 1.

## Hard Constraints (locked)
- No edits to math core:
  - `omega_v3_core/kernel.py`
  - `omega_v3_core/omega_math_core.py`
  - `kernel.py`
  - `omega_math_core.py`
- Pipeline changes must remain fail-closed on train/backtest role overlap.
- Runtime state must not be written back to `config.py`.
- All fixes must comply with:
  - `OMEGA_CONSTITUTION.md`
  - `.agent/principles.yaml`
  - `.agent/skills/ops/SKILL.md`
  - `.agent/skills/engineering/SKILL.md`
  - `.agent/skills/v3_mainline_guard/SKILL.md`
  - `.agent/skills/hardcode_guard/SKILL.md`
  - `.agent/skills/data_integrity_guard/SKILL.md`
  - `.agent/skills/ai_handover/SKILL.md`

## Baseline Repository State
Observed `git status --short` at baseline:
- `M audit/v40_windows_handover_runtime_2026-02-08.md`
- `M jobs/windows_v40/README.md`
- `M jobs/windows_v40/run_v40_train_backtest_win.ps1`
- `M jobs/windows_v40/start_v40_pipeline_win.ps1`
- `M parallel_trainer/run_parallel_v31.py`
- `?? "C\357\200\242/"`
- `?? tools/preflight_dataset_split_v40.py`

Notes:
- Worktree is already dirty before this debug program.
- `tools/preflight_dataset_split_v40.py` is currently untracked while referenced by runtime pipeline.

## Baseline Runtime Evidence
- Runtime root: `audit/v40_runtime/windows/`
- Present stage artifacts:
  - frame status/log and compatibility status/log
  - train status/log
  - manifests (`train_files.txt`, `train_manifest_status.json`, `split_preflight.log`)
  - no backtest status/log in current runtime snapshot

Key status snapshots:
- `audit/v40_runtime/windows/frame/frame_status.json`
  - `status=running`
  - `archives_completed_in_run=747`
  - `archives_remaining_in_run=0`
  - `parquet_files_written_in_run=4758369`
- `audit/v40_runtime/windows/frame/frame_compat_status.json`
  - `status=completed`
  - `sample_raw_ready=96/96`
  - `sample_backtest_ready=96/96`
- `audit/v40_runtime/windows/train/train_status.json`
  - `status=ready`
  - `note=checkpoint_loaded`
  - `latest_checkpoint=artifacts\checkpoint_rows_12.pkl`
- `audit/v40_runtime/windows/manifests/train_manifest_status.json`
  - `status=completed`
  - `matched_files=2953587`
  - filters reflect official split (`2023,2024` train)

## Frozen Findings Set Entering Remediation
- Critical overlap guard normalization gap for custom backtest manifest paths.
- Untracked runtime dependency risk for split preflight script.
- Silent success risk in train/backtest runners under worker-level errors.
- Backtest final audit does not hard-fail pipeline by default.
- Smoke runner still vulnerable to native stderr promotion under strict mode.
- Policy selection/provenance and orchestration efficiency issues.

## Phase 0 Gate Result
- Constitution and skills constraints identified and locked.
- Baseline state captured with runtime evidence.
- Approved to proceed to Phase 1 remediation.

