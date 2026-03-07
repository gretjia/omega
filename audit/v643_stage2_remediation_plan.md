# V64 Stage2 Ordering-Contract Remediation Plan

Date: 2026-03-07  
Author: Codex  
Status: plan draft, pending dual-audit approval

## 1. Mission objective

Fix the Stage 2 integration defect identified in:

- [v643_all_0_root_cause.md](/home/zephryj/projects/omega/audit/v643_all_0_root_cause.md)

Without changing the approved V64.3 canonical runtime math core, restore correct rolling-trajectory semantics by repairing the ordering contract between:

- `build_l2_features_from_l1()`
- `apply_recursive_physics()`

At the same time, add fail-fast input-contract gates so that each expensive stage refuses bad inputs before consuming major compute.

## 2. Governing constraints

Canonical math must remain untouched:

- `Delta k = 0`
- `bits_srl` remains forbidden
- `has_singularity` must not rewrite `srl_resid`
- canonical topology remains closed-area / closed-perimeter geometry

This mission is strictly:

- Stage 2 remediation
- input-gate hardening
- no Stage 1 recompute
- no release commit/push in this phase

## 3. Root cause recap

Current root-cause evidence indicates:

1. raw Stage 1 parquet remains symbol-contiguous
2. `build_l2_features_from_l1()` emits bucket frames in symbol-interleaved order
3. `apply_recursive_physics()` derives `is_boundary` and `dist_to_boundary` from row adjacency
4. rolling topology / compression / SRL warm-up therefore operate on broken trajectories
5. canonical signal-chain outputs collapse to zero

This is an ETL -> kernel interface defect, not a Stage 1 defect.

## 4. Remediation strategy

Two remediation locations are possible:

### Option A: Repair ordering at ETL output

Enforce symbol/date/time continuity at the end of `build_l2_features_from_l1()`.

Pros:

- fixes the contract at the producer boundary
- benefits every kernel consumer
- keeps `apply_recursive_physics()` assumptions coherent with actual input order

Cons:

- any downstream component that implicitly depended on the historical interleaved order will change behavior

### Option B: Repair ordering only inside kernel

Before rolling physics begins, sort a local working copy of frames by:

- `symbol`
- `date`
- `time_end` when present
- else `bucket_id`

Then restore original row order after physics outputs are computed.

Pros:

- smallest blast radius
- leaves upstream ETL artifact order unchanged
- directly targets the defective interface

Cons:

- kernel must manage an explicit reorder / inverse-reorder contract
- any future rolling consumer outside kernel would still inherit the old ETL output order

### Option C: Combined producer and consumer hardening

Use Option B as the immediate safe fix, and add producer-side validation to detect interleaving without forcing producer reordering yet.

Pros:

- minimal risk immediate repair
- explicit detection of future regressions
- easier rollback

Cons:

- leaves ETL output order historically non-canonical until a later cleanup mission

## 5. Recommended implementation choice

### Recommendation: Option C

Immediate code fix:

- apply local reorder inside `apply_recursive_physics()`
- preserve original row order in returned DataFrame

Immediate fail-fast hardening:

- add input-contract checks in Stage 2 and downstream stage entrypoints
- detect non-contiguous or insufficient inputs before expensive work begins

Reason:

- it is the lowest-risk repair for the proven defect
- it does not require redefining artifact order globally in the same mission
- it creates a path to later unify ETL output semantics in a separate cleanup if desired

## 6. Planned code scope

Primary implementation scope:

- [omega_core/kernel.py](/home/zephryj/projects/omega/omega_core/kernel.py)

Secondary scope for Stage 2 gating:

- [tools/stage2_physics_compute.py](/home/zephryj/projects/omega/tools/stage2_physics_compute.py)

Downstream stage gate scope:

- [tools/forge_base_matrix.py](/home/zephryj/projects/omega/tools/forge_base_matrix.py)
- [tools/run_vertex_xgb_train.py](/home/zephryj/projects/omega/tools/run_vertex_xgb_train.py)
- [tools/run_local_backtest.py](/home/zephryj/projects/omega/tools/run_local_backtest.py)

Tests:

- [tests/test_v64_absolute_closure.py](/home/zephryj/projects/omega/tests/test_v64_absolute_closure.py)
- [tests/test_v64_fastpath_equivalence.py](/home/zephryj/projects/omega/tests/test_v64_fastpath_equivalence.py)
- new ordering-contract / gate tests as needed

Non-scope:

- no changes to `omega_math_rolling.py` formula definitions in this mission
- no Stage 1 changes
- no training-hyperparameter policy changes

## 7. Detailed implementation plan

### Step 1: Kernel local reorder

Inside `_apply_recursive_physics()`:

1. detect stable sort keys from existing columns:
   - `symbol`
   - `date`
   - `time_end`
   - fallback `bucket_id`
2. attach an explicit original row index (`orig_idx`) before any local reorder
3. build a stable locally sorted working frame for physics computation
4. compute rolling topology / SRL / compression on the sorted frame
5. restore original row order using `orig_idx` before returning

Required property:

- output DataFrame must preserve the original row order seen by downstream code
- only the internal physics working order is corrected
- if `time_end` is missing, the fallback sort must be deterministic:
  - use `bucket_id`
  - then `orig_idx` as final tie-breaker

Rollback hardening:

- gate the internal reorder with an explicit feature flag:
  - recommended env: `OMEGA_STAGE2_FIX_KERNEL_ORDERING=1`
- allow temporary disablement for A/B validation and rollback
- rollout default:
  - implementation default in this mission should be `enabled`
  - rollback path is explicit opt-out (`OMEGA_STAGE2_FIX_KERNEL_ORDERING=0`)
  - no ambiguous tri-state default at runtime

### Step 2: Stage 2 input gate

At the Stage 2 file-processing entrypoint:

1. verify required input columns exist
2. verify `symbol` and `date` exist when rolling physics is enabled
3. inspect a bounded sample for contiguous symbol ordering
4. if ordering is not contiguous:
   - classify the defect as either:
     - `repairable_by_kernel_reorder`
     - `not_repairable`
   - for `repairable_by_kernel_reorder`:
     - record the violation
     - continue only if the kernel-ordering fix flag is enabled
   - for `not_repairable`:
     - fail-fast before expensive physics

Additional gate:

- verify that at least some symbol/date groups can theoretically satisfy `window_len`
- if no symbol/day can reach the rolling window at all, fail-fast and skip expensive physics
- verify ordering keys are present enough to support deterministic local reorder:
  - `symbol`
  - `date`
  - and at least one of:
    - `time_end`
    - `bucket_id`

Repairability rules:

- classify as `repairable_by_kernel_reorder` only if all are true:
  - required identity keys exist:
    - `symbol`
    - `date`
  - deterministic ordering keys exist:
    - `time_end` or `bucket_id`
  - at least one symbol/date group can theoretically satisfy `window_len`
- classify as `not_repairable` and fail-fast if any are true:
  - `symbol` missing
  - `date` missing
  - both `time_end` and `bucket_id` missing
  - no symbol/date group can reach `window_len`
  - duplicate-row ambiguity prevents deterministic within-group ordering

Detection strategy:

- do not rely on a small bounded sample alone
- use a two-level approach:
  1. a bounded sample for quick diagnostics/logging
  2. a cheap global disorder fingerprint or counter over the full frame/file to detect pervasive interleaving

### Step 3: Downstream stage gates

#### Forge gate

Before shard/base-matrix work starts:

- verify required L2 columns exist:
  - `epiplexity`
  - `topo_area`
  - `topo_energy`
  - `srl_resid`
  - `singularity_vector`
  - `is_signal`
- verify rows are not trivially empty
- verify there is a minimum non-empty sample size before expensive shard/materialization work
- verify sortability / identity keys needed by downstream joins remain present
- emit structured gate diagnostics before work proceeds

#### Training gate

Before model training:

- verify base-matrix required columns exist
- verify label columns are constructible/present
- verify training rows exceed a minimum threshold
- verify `t1_close` contract or its reconstruction path is valid
- verify the incoming matrix preserves the time-order keys required for T+1 target logic
- fail-fast on structurally empty or trivially non-trainable datasets
- emit structured gate diagnostics before work proceeds

#### Backtest gate

Before backtest:

- verify model artifact compatibility
- verify frame schema compatibility
- verify T+1 target path is available or reconstructible
- verify minimum evaluable frame count before inference begins
- reject obviously degenerate datasets before costly full-file traversal
- emit structured gate diagnostics before work proceeds

## 8. Planned tests

### Test A: kernel ordering repair

Construct a symbol-interleaved input frame where:

- raw rows are intentionally interleaved
- sorted same-symbol windows should produce non-zero topology

Assert:

- internal reorder recovers non-zero topology for eligible groups
- returned output order matches original row order
- feature flag off reproduces the old broken behavior
- feature flag on restores intended rolling behavior

### Test B: Stage 2 gate

Use a synthetic input where no symbol/day can ever reach `window_len`.

Assert:

- Stage 2 fails fast instead of spending expensive compute
- non-contiguous-but-repairable input is only allowed when kernel reorder flag is on
- `not_repairable` inputs are rejected deterministically
- global disorder fingerprint catches cases that a small head/tail sample would miss

### Test C: downstream gates

Construct missing-column and structurally-invalid inputs for:

- forge
- training
- backtest

Assert:

- each stage rejects invalid inputs before heavy work begins

### Test D: ordering-repair numerical equivalence

Use a small dataset that can be represented in:

- canonical symbol-contiguous order
- intentionally interleaved order

Assert:

- after kernel local reorder, both produce the same physics outputs for the same logical trajectories
- including:
  - `topo_area`
  - `topo_energy`
  - `epiplexity`
  - `srl_resid`
  - `singularity_vector`

## 9. Audit questions for plan approval

### Math audit questions

1. Does the plan preserve the approved V64.3 canonical runtime math core?
2. Is local reorder inside kernel mathematically legitimate as a way to restore intended trajectory semantics?
3. Does any part of the plan implicitly redefine the math object instead of restoring correct input semantics?

### Engineering audit questions

1. Is Option C the lowest-risk implementation path?
2. Is rollback preserved?
3. Do the proposed input gates materially reduce wasted compute?
4. Is the planned test scope sufficient before smoke?
5. Are severe contract violations fail-fast rather than merely logged?

## 10. Observability requirements

The implementation must emit structured diagnostics sufficient for rollback and triage, including:

- whether kernel reorder was applied
- whether the reorder flag was explicitly disabled
- disorder fingerprint / ordering diagnostics
- repairable violations count
- not-repairable rejection count
- window-reachability diagnostics

These diagnostics must be available in stage logs before expensive compute proceeds.

## 11. Post-plan workflow

No code changes may begin until this plan receives:

- math audit approval
- engineering audit approval

After plan approval:

1. implement the minimal repair
2. run code audit
3. if code audit passes, draft a smoke spec for Owner approval
