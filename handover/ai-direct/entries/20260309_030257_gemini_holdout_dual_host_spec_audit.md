---
entry_id: 20260309_030257_gemini_holdout_dual_host_spec_audit
task_id: TASK-V643-STAGE3-HOLDOUT-MATRIX-BUILD-SPEC
timestamp_local: 2026-03-09 03:02:57 +0000
timestamp_utc: 2026-03-09 03:02:57 +0000
operator: Codex
role: auditor
branch: main
status: completed
---

# Gemini Audit: Holdout Base-Matrix Dual-Host Spec

## 1. Objective

- Use `gemini -y` as an external gate on the Stage3 holdout base-matrix execution spec.
- Confirm that the plan really uses idle cluster capacity intelligently while respecting data locality, date-scope isolation, and downstream evaluation safety.

## 2. Review Scope

- Spec under review:
  - `handover/ai-direct/entries/20260309_025500_holdout_basematrix_dual_host_execution_spec.md`
- Hard context embedded into the audit prompt:
  - controller is `omega-vm`
  - `windows1-w1` owns the late-date Stage2 full-run corpus including `2025*` and `202601*`
  - `linux1-lx` does not own that corpus locally
  - Windows was empirically faster than Linux on the repaired path
  - January 2026 scope must come from an explicit manifest
  - evaluation directories must be kept clean of shard parquet files

## 3. Live Resource Verification

At audit time, both workers were idle enough to execute the holdout plan:

- `linux1-lx`
  - no active Stage2 / Stage3 / train process found
  - available memory sample: about `24 GiB`
- `windows1-w1`
  - no active `python` compute process found
  - memory sample:
    - `FreeGB=86.7`
    - `TotalGB=95.8`

Interpretation:

- host allocation can be driven by throughput and locality, not by current contention

## 4. Gemini Verdict

- Verdict: `PASS`

Gemini’s accepted conclusions:

- Windows is correctly chosen as the primary forge node because it has both:
  - the required local `2025*` / `202601*` inputs
  - the stronger observed throughput
- The spec correctly forbids fake dual-host parallelism where Linux reads Windows parquet remotely
- The spec correctly enforces clean holdout evaluation directories outside shard workspaces
- The three-matrix governance is preserved:
  - `2023,2024` train
  - `2025` outer holdout
  - `2026-01` final canary
- The default mode and optimized mode are both sensible
- The January scope is correctly defined by explicit manifest, not by `--years 2026` alone
- Controller authority is correctly assigned to `omega-vm`

## 5. Locked Execution Interpretation

The externally audited recommendation is now:

1. Default mode
   - `windows1-w1` forges `base_matrix_holdout_2025.parquet`
   - `windows1-w1` then forges `base_matrix_holdout_2026_01.parquet`
   - `linux1-lx` runs the audit / validation / cloud-controller lane in parallel
2. Optimized mode
   - allowed only if `202601*.parquet` is first copied into Linux-local storage
   - Linux may then forge the January canary locally
   - remote-mounted Windows parquet on Linux remains forbidden

## 6. Result

- The holdout build spec is now externally audited and usable as the canonical execution plan
- No code was changed in this audit cycle
- The next step can move from architecture to actual holdout artifact generation
