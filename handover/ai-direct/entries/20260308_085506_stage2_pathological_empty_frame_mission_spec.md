# V643 Stage2 Pathological Empty-Frame Mission Spec

- Entry ID: `20260308_085506_stage2_pathological_empty_frame_mission_spec`
- Timestamp UTC: `2026-03-08 08:55:06 +0000`
- Operator: `Codex`
- Status: `active_spec_locked`
- Mission: `V643-STAGE2-PATHO-EMPTY-FRAME-REMEDIATION`

## 1. Objective

- Formalize the new remediation mission around the remaining three unresolved Stage2 failures.
- Lock the mission to the normal `v643` Stage2 path, not the slow forced fallback path.
- Make downstream Stage3 forge consumption proof part of the mission definition of done.

## 2. Confirmed Evidence

- Remaining unresolved files:
  - Linux: `20231219_b07c2229.parquet`
  - Windows: `20241128_b07c2229.parquet`, `20250908_fbd5c8b.parquet`
- Direct Linux rerun on the current normal `v643` Stage2 path reproduced the same failure family on all three files:
  - guardrail log: `Proactively dropping pathological symbol`
  - immediate failure: `CRITICAL Error: index out of bounds`
- Code-level narrowing:
  - `_filter_pathological()` can return `tbl.slice(0, 0)` for a pathological symbol frame.
  - the normal `process_chunk()` symbol-stream path indexes `symbol_df.column("symbol")[0]` without a zero-row guard.

## 3. Spec Decisions

- Canonical problem statement:
  - `Stage2 normal symbol-stream path does not tolerate empty symbol frames produced by pathological-symbol guardrail.`
- Canonical implementation authority:
  - `tools/stage2_physics_compute.py`
  - `tools/forge_base_matrix.py`
- Out of scope:
  - `omega_core/*` math changes
  - fallback-path performance tuning
  - Stage1 rebuild
  - full-queue reruns
- Required downstream proof:
  - the repaired three-file L2 set must be consumable together by `tools/forge_base_matrix.py`

## 4. Stage3 Validation Rule

- Stage3 validation must use the real forge entrypoint, not an ad hoc reader.
- Validation must run on `linux1-lx` in an isolated workspace with `--input-file-list`.
- Validation must explicitly pass `--years 2023,2024,2025`.
- Reason:
  - forge defaults to `--years=2023,2024`
  - without explicit years, the `20250908` file would be silently excluded and the proof would be invalid

## 5. Acceptance Gates

- Stage2 no longer crashes with `index out of bounds` after the pathological guardrail on the three unresolved files.
- Regression coverage exists for the proactive empty-frame case on the normal non-fallback path.
- Existing crash-skip tests still pass.
- Forge input contract passes on the repaired three-file set.
- Non-empty `base_matrix.parquet` and meta artifacts are produced from that same three-file set.

## 6. Immediate Next Actions

1. Patch `tools/stage2_physics_compute.py` to make the normal symbol-stream path tolerate zero-row symbol frames.
2. Add regression coverage for the proactive-drop empty-frame case.
3. Validate the three unresolved files on Linux using the normal `v643` Stage2 path.
4. Run isolated forge validation on the repaired three-file set with explicit year scope.
