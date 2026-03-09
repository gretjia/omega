---
entry_id: 20260309_025500_holdout_basematrix_dual_host_execution_spec
task_id: TASK-V643-STAGE3-HOLDOUT-MATRIX-BUILD-SPEC
timestamp_local: 2026-03-09 02:55:00 +0000
timestamp_utc: 2026-03-09 02:55:00 +0000
operator: Codex
role: architect
branch: main
status: audited_pass
---

# Spec: Stage3 Holdout Base-Matrix Dual-Host Execution

## 1. Objective

- Build the two missing holdout Stage3 artifacts required by the optimal allocation protocol:
  - `base_matrix_holdout_2025.parquet`
  - `base_matrix_holdout_2026_01.parquet`
- Use both idle hosts efficiently without violating data locality or the canonical train/holdout split.
- Minimize wall-clock time by assigning the heavy forge path to the host with both:
  - the relevant local data
  - the stronger observed throughput

## 2. Current Verified Facts

### 2.1 Training artifact is already complete

- Existing Stage3 training artifact:
  - `/omega_pool/parquet_data/stage3_base_matrix_train_20260308_095850/base_matrix_train_2023_2024.parquet`
- Verified scope:
  - `years=['2023', '2024']`
  - `year_min=2023`
  - `year_max=2024`
  - `year_count=2`

### 2.2 Linux does not own the 2025 / 2026-01 full-run corpus

- Linux full-run Stage2 output path:
  - `/omega_pool/parquet_data/stage2_full_20260307_v643fix/l2/host=linux1`
- Direct check:
  - `2025_count = 0`
  - `202601_count = 0`

Interpretation:

- Linux is not the natural owner of the holdout L2 corpus.

### 2.3 Windows owns the later contiguous slice

- Windows full-run Stage2 path:
  - `D:\Omega_frames\stage2_full_20260307_v643fix\l2\host=windows1`
- Direct directory evidence:
  - earliest sample:
    - `20240717_b07c2229.parquet`
  - latest sample:
    - `20260130_fbd5c8b.parquet`

Interpretation:

- The holdout domain `2025` and `2026-01` lives on Windows-local Stage2 outputs.

### 2.4 Windows has already been observed faster than Linux on the current repaired path

Authority:

- `handover/ai-direct/entries/20260307_110209_windows_faster_than_linux_stage2_analysis.md`

Recorded evidence:

- `linux1-lx`: about `244.33 s/file`
- `windows1-w1`: about `125.82 s/file`
- Windows was roughly `1.9x` faster

Interpretation:

- Even before considering data locality, Windows is currently the faster execution node.

## 3. Core Decision

The holdout base-matrix build should not be split evenly across hosts.

It should be split by critical-path weight:

1. `windows1-w1` is the primary forge node
   - owner of the heavy `2025` holdout artifact
2. `linux1-lx` is the secondary controller / audit node
   - it does not own any holdout forge that depends on Windows-resident L2 data

This is the optimal allocation because:

- the heavy workload goes to the faster host with local data
- the January canary also remains data-local on Windows
- Linux stays useful, but on orchestration and audit work instead of fake cross-node ETL parallelism

## 4. Artifact Contract

Three Stage3 artifacts must now exist as independent outputs:

1. Training:
   - `base_matrix_train_2023_2024.parquet`
2. Outer holdout:
   - `base_matrix_holdout_2025.parquet`
3. Final canary:
   - `base_matrix_holdout_2026_01.parquet`

Governance:

- Optuna and champion selection may read only artifact 1
- outer holdout evaluation may read only artifact 2
- final release-canary evaluation may read only artifact 3

## 5. Topology And Host Allocation Plan

### 5.1 Controller identity

The control plane owner for this mission is:

- `omega-vm` (controller)

Not:

- `linux1-lx`

Implication:

- manifest generation, remote launch, artifact bookkeeping, and cloud staging decisions belong to `omega-vm`
- `windows1-w1` and `linux1-lx` are data-plane workers only
### 5.2 Windows primary task

`windows1-w1` will build:

- `base_matrix_holdout_2025.parquet`

Why:

- all relevant Stage2 L2 inputs are Windows-local
- Windows is the faster observed node
- `2025` is the heavy holdout slice and therefore the true critical path

### 5.3 Windows secondary forge task

After `2025` completes, `windows1-w1` will also build:

- `base_matrix_holdout_2026_01.parquet`

Default policy:

- sequential, not forced parallel

Reason:

- both holdout slices are Windows-local
- Windows is the faster observed node
- avoiding cross-node Parquet reads is more important than artificial host symmetry

### 5.4 Linux task

Default role for `linux1-lx`:

- generate and assert manifests
- run post-forge contract audits
- prepare cloud-side swarm/controller staging
- validate date scopes and artifact metadata

Refined rule:

- Linux must not generate manifests by scanning Windows local filesystems
- Linux must not participate in any holdout forge that depends on remotely mounted Windows parquet reads

Allowed optimized parallel mode:

- Linux may forge `base_matrix_holdout_2026_01.parquet` only if the January subset is first copied into Linux-local storage and verified locally
- in that mode, Linux is doing a true local forge, not remote data-parallel theater

## 6. Exact Scoping Rules

### 6.1 2025 holdout

Authority:

- all files with day-key prefix `2025` from:
  - `D:\Omega_frames\stage2_full_20260307_v643fix\l2\host=windows1`

Preferred invocation shape:

- use `tools/forge_base_matrix.py --input-file-list ... --years 2025`

Scope is defined by:

- the manifest contents
- with `--years 2025` as an additional guard

### 6.2 2026-01 holdout

Authority:

- only files whose day-key prefix is `202601`

Critical rule:

- the January scope must be defined by the explicit manifest itself
- it must not rely on `--years 2026` for correctness

Reason:

- current tooling only supports year-level filtering
- `2026` would include dates beyond January if they were present

Preferred invocation shape:

- `tools/forge_base_matrix.py --input-file-list january_2026_manifest.txt`

Optional extra guard:

- `--years 2026`

But that flag is not the source of truth for the January boundary.

## 7. Execution Sequence

### Phase A: manifest and path prep

Controller responsibilities:

1. from `omega-vm`, remotely invoke Windows-local manifest generation for `2025`
2. from `omega-vm`, remotely invoke Windows-local manifest generation for `2026-01`
3. verify no file outside target prefixes enters either manifest
4. hard-assert before forge:
   - every `2025` manifest entry matches `2025*.parquet`
   - every January manifest entry matches `202601*.parquet`

### Phase B: execution modes

#### Mode 1: safe default

1. launch Windows forge for `2025`
2. Linux prepares audit scripts / contract checks while Windows is forging
3. after `2025` completes, launch Windows forge for `2026-01`
4. Linux audits each artifact as soon as it lands

#### Mode 2: true dual-host optimized

This mode is allowed only if:

- the January subset is copied from Windows into Linux-local storage first
- the copied file set is re-asserted locally on Linux as `202601*.parquet` only

Sequence:

1. Windows forges `2025`
2. in parallel, controller copies `202601*.parquet` subset from Windows to Linux-local holdout staging
3. Linux forges `2026-01` from its local copied subset
4. both outputs are audited independently

If the January copy/preflight is noisy or slow, abort Mode 2 and fall back to Mode 1.

### Phase C: post-build validation

For each artifact:

- verify forge input contract passed
- verify output is non-empty
- verify date scope is exact
- verify `stage3_param_contract` compatibility remains canonical
- verify evaluation directory contains only the final parquet + meta and not the forge shard tree

### Phase D: evaluation isolation prep

Before any downstream evaluation:

- each holdout artifact must live in its own clean directory
- `_shards` build directories must be deleted, moved away, or kept outside the evaluation root

Required clean layout examples:

- `.../holdout_2025_eval/base_matrix_holdout_2025.parquet`
- `.../holdout_2025_eval/base_matrix_holdout_2025.parquet.meta.json`
- `.../holdout_2026_01_eval/base_matrix_holdout_2026_01.parquet`
- `.../holdout_2026_01_eval/base_matrix_holdout_2026_01.parquet.meta.json`

Forbidden:

- pointing evaluation at a forge workspace root that still contains `_shards/`
- mixing January canary output in a directory that also contains other `2026*.parquet`

## 8. Runtime Parameters

### Windows / 2025

Recommended starting forge profile:

- `--symbols-per-batch 200`
- `--max-workers 2`
- `--reserve-mem-gb 40`
- `--worker-mem-gb 10`

Reason:

- this matches the stable profile used in the recent successful training base-matrix run
- avoid speculative tuning during holdout artifact construction

### Windows / 2026-01

Recommended starting profile:

- `--symbols-per-batch 200`
- `--max-workers 2`

Reason:

- January is smaller than full `2025`
- but keeping the same known-good Windows profile reduces avoidable branching in the holdout build path

## 9. Acceptance Criteria

1. `base_matrix_holdout_2025.parquet` is forged successfully and contains only `2025`
2. `base_matrix_holdout_2026_01.parquet` is forged successfully and contains only `202601`
3. Neither holdout artifact is derived from or merged into `base_matrix_train_2023_2024.parquet`
4. Both holdout forge workloads run on Windows while Windows is healthy and available
5. In the optimized dual-host mode, Linux may forge January only from a Linux-local copied subset, never from remote Windows reads
6. Manifest generation is executed against Windows-local files by Windows-side commands under `omega-vm` control
7. Each holdout artifact has its own clean evaluation directory containing no forge shards
8. Any evaluation of January points only to a directory containing the January artifact and its meta
9. Linux performs the parallel contract-validation / audit / cloud-controller lane
10. Handover records:
   - manifests
   - exact artifact paths
   - exact date scopes
   - host assignments
   - row counts
   - contract verdicts

## 10. Fail-Fast Conditions

- If `2025` is forged on Linux while Windows is healthy and idle: reject unless Windows path is proven blocked
- If `2026-01` is forged on Linux from remotely mounted Windows parquet: reject
- If `2026-01` is forged on Linux from copied parquet but the copied subset was not locally re-asserted as `202601*.parquet` only: reject
- If `2026-01` scope is defined only by `--years 2026` and not by an explicit January manifest: reject
- If any holdout artifact includes dates outside its intended window: reject
- If any implementation evaluates `2025` or `2026-01` from the training artifact instead of a separately forged holdout artifact: reject
- If manifest generation lacks hard prefix assertions for `2025` and `202601`: reject
- If evaluation points at a directory containing forge shards or mixed-year parquet files: reject

## 11. Final Recommendation

Use asymmetric allocation with two allowed modes:

### Default mode

- Windows:
  - `2025` holdout forge
  - `2026-01` canary forge
- Linux:
  - validation / audit / cloud-controller lane

### Optimized mode

- Windows:
  - `2025` holdout forge
- Linux:
  - `2026-01` forge only after January subset becomes Linux-local
  - plus validation / audit / cloud-controller lane

The default mode is safer.

The optimized mode is faster only if the January subset copy is demonstrably cheap and clean.

## 12. External Audit Status

- Auditor:
  - `gemini -y`
- Verdict:
  - `PASS`
- Locked operational interpretation:
  - default execution mode is the canonical path
  - Windows remains the primary forge node for both holdout artifacts because it has the local corpus and the stronger observed throughput
  - Linux is valuable in parallel, but in the audit/controller lane unless the January subset is first copied into Linux-local storage
