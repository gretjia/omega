# 2026-03-08 09:30 UTC - V643 Stage2 pathological empty-frame Windows runtime proof and Stage3 whole-set forge proof

## Summary

- Remediation commit under test: `23fd229`
- Objective:
  - prove the patched normal `v643` Stage2 path no longer crashes on the three previously unresolved files
  - prove the repaired three-file L2 set is consumable together by Stage3 forge
- Outcome:
  - Stage2 isolated runtime proof: PASS on `windows1-w1`
  - Stage3 whole-set forge proof: PASS on `windows1-w1`
  - Linux mirror rerun: not executed in this session because `ssh linux1-lx` timed out from the controller

## Deploy And Reachability Notes

- Controller push to `origin` succeeded for commit `23fd229`.
- The local controller repo had no worker deploy remotes configured for `tools/deploy.py`, so `tools/deploy.py --skip-commit --nodes windows` could not be used for this validation window.
- For this isolated proof only, `windows1-w1` was aligned manually to `23fd229` from its `github` remote.
- `ssh linux1-lx` timed out repeatedly during the same window, so no post-patch Linux mirror rerun was possible.

## Stage2 Runtime Proof

Windows isolated Stage2 workspaces:

- main L2 output root:
  - `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2`
- runner logs:
  - `D:\work\Omega_vNext\audit\runtime\stage2_patho_fix_validate_20260308_091554\runner.log`
  - `D:\work\Omega_vNext\audit\runtime\stage2_patho_fix_validate_20260308_20231219\runner.log`

Validated files and outcomes:

- `20241128_b07c2229.parquet`
  - output file:
    - `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2\20241128_b07c2229.parquet`
  - result:
    - `Completed: 253227 rows in 128.1s`
- `20250908_fbd5c8b.parquet`
  - output file:
    - `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2\20250908_fbd5c8b.parquet`
  - result:
    - `Completed: 254884 rows in 169.6s`
- `20231219_b07c2229.parquet`
  - output file:
    - `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2\20231219_b07c2229.parquet`
  - result:
    - `Completed: 252844 rows in 86.5s`

Important runtime verdict:

- all three files completed on the normal current `v643` path
- no forced scan fallback was enabled
- no `guardrail -> index out of bounds` recurrence was observed

## Stage3 Whole-Set Forge Proof

Windows isolated Stage3 workspace:

- output root:
  - `D:\Omega_frames\stage3_patho_fix_forge_20260308_1728`
- input list:
  - `D:\work\Omega_vNext\audit\runtime\stage3_patho_fix_forge_20260308_1728\input_files.txt`

Input set used:

- `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2\20231219_b07c2229.parquet`
- `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2\20241128_b07c2229.parquet`
- `D:\Omega_frames\stage2_patho_fix_validate_20260308_091554\l2\20250908_fbd5c8b.parquet`

Forge command properties:

- `tools/forge_base_matrix.py`
- `--input-file-list ...`
- `--years 2023,2024,2025`
- `--output-parquet D:\Omega_frames\stage3_patho_fix_forge_20260308_1728\base_matrix.parquet`
- `--output-meta D:\Omega_frames\stage3_patho_fix_forge_20260308_1728\base_matrix.parquet.meta.json`

Forge input contract verdict:

- PASS
- diagnostic:
  - `rows=760955`
  - `physics_valid_rows=760955`
  - `epi_pos_rows=716`
  - `topo_energy_pos_rows=4404`
  - `signal_gate_rows=3897`

Forge output verdict:

- PASS
- output parquet:
  - `D:\Omega_frames\stage3_patho_fix_forge_20260308_1728\base_matrix.parquet`
- output meta:
  - `D:\Omega_frames\stage3_patho_fix_forge_20260308_1728\base_matrix.parquet.meta.json`
- key result fields:
  - `input_file_count=3`
  - `raw_rows=760955`
  - `base_rows=3074`
  - `merged_rows=3074`
  - `symbols_total=7525`
  - `worker_count=2`
  - `seconds=40.13`

## Operational Conclusion

- The repaired three-file set is not merely writable at Stage2.
- It is consumable together by the real Stage3 forge path as one coherent input set.
- The user requirement for whole-set Stage3 usability is satisfied.
- The only remaining follow-up question is whether the Owner still wants a Linux mirror proof after controller-to-Linux SSH is restored.
