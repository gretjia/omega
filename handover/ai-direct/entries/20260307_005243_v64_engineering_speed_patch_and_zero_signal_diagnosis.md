---
task_id: TASK-V64-ENGINEERING-SPEED-PATCH-EVAL-AND-ZERO-SIGNAL-DIAGNOSIS
date: 2026-03-07
author: Codex
status: in_progress
---

# V64 engineering speed patch evaluation and zero-signal diagnosis

## 1. Context

This entry records all progress made after the successful V64.3 release smoke. The new workstream had two distinct goals:

1. evaluate an engineering-only speed patch without changing the approved V64.3 canonical runtime math core
2. find a non-zero informative slice so that legacy-vs-file-stream backtest equivalence could be tested on meaningful signals rather than on all-zero smoke outputs

The Owner explicitly required:

- no `git commit` or `git push` before a successful, owner-approved smoke
- preserve the previous successful smoke workspace as the rollback anchor
- preserve every intermediate smoke workspace for comparison

## 2. Preserved workspaces and rollback anchors

- baseline smoke workspace:
  - `/home/zepher/work/Omega_vNext_v643_smoke`
- first speed smoke workspace:
  - `/home/zepher/work/Omega_vNext_v643_speed_smoke`
- training-comparison smoke workspace:
  - `/home/zepher/work/Omega_vNext_v643_traincmp_smoke`
- non-zero discovery probe workspace:
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke`
- controller repo rollback anchor:
  - `origin/main = a0e65e6`

## 3. Engineering speed smoke result

### 3.1 Initial speed smoke verdict

The first engineering speed smoke was marked `NO PASS`.

Reason:

- `Stage 2`: faster, passed
- `forge/base_matrix`: passed
- `backtest`: much faster, passed structurally
- `training`: severe slowdown

Measured training contrast:

- baseline smoke:
  - `xgb_max_depth = 3`
  - `num_boost_round = 2`
  - `seconds = 10.98`
- first speed smoke:
  - `xgb_max_depth = 5`
  - `num_boost_round = 150`
  - `seconds = 774.09`

At this point the upgrade could not be released because the smoke comparison was no longer apples-to-apples.

### 3.2 Training slowdown root cause

A narrow comparison smoke was run to determine whether the slowdown came from the new engineering path or from smoke-contract drift.

Comparison smoke:

- workspace:
  - `/home/zepher/work/Omega_vNext_v643_traincmp_smoke`
- explicitly pinned training params:
  - `--xgb-max-depth 3`
  - `--num-boost-round 2`

Result:

- training returned to `10.98s`
- the fast backtest path remained fast (`~3.9s`)

Conclusion:

- the training slowdown was caused by smoke harness parameter drift
- it was not evidence that the new engineering fast paths had broken the training path

## 4. Backtest speed interpretation

The backtest speedup was judged plausible on engineering grounds:

- old path rescanned all input files for many symbol batches
- new path builds a compact `symbol/date -> t1_close` map once, then streams each file once

However, the smoke slice still had weak evidentiary value because the resulting backtest metrics were all zero. That led to the next task: find a non-zero informative slice.

## 5. Non-zero slice discovery

### 5.1 Monthly tiny-symbol discovery pass

Method:

- sample one representative day per month
- keep a tiny set of liquid symbols
- run narrow Stage 2 discovery probes

Artifacts:

- manifest:
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/monthly_probe_manifest.json`
- rankings:
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/probe_rankings.json`

Outcome:

- `37` monthly tiny probes completed
- every one of them remained zero under strict V64.3 semantics

### 5.2 Full-day full-market probe pass: `fbd5c8b`

Candidate files:

- `20250901_fbd5c8b.parquet`
- `20251013_fbd5c8b.parquet`
- `20251105_fbd5c8b.parquet`
- `20251202_fbd5c8b.parquet`
- `20260105_fbd5c8b.parquet`

Artifacts:

- candidate manifest:
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/fullprobe_candidates.json`
- log:
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/fullprobe.log`

Outcome:

- all `5` full-day probes completed successfully
- all `5` remained canonical zero-output:
  - `epiplexity = 0`
  - `is_signal = 0`
  - `singularity_vector = 0`

### 5.3 Full-day full-market probe pass: `b07c2229`

These dates were chosen from real pathological/debug/assist history in `/handover`, not by random sampling.

Candidate files:

- `20240717_b07c2229.parquet`
- `20250704_b07c2229.parquet`
- `20250725_b07c2229.parquet`
- `20250828_b07c2229.parquet`
- `20251022_b07c2229.parquet`

Artifacts:

- candidate manifest:
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/fullprobe2_candidates.json`
- log:
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/fullprobe2.log`
- rankings:
  - `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/fullprobe2_rankings.json`

Outcome:

- all `5` full-day probes completed successfully
- all `5` also remained canonical zero-output

## 6. Gate-chain diagnosis

Because repeated date discovery failed, a gate-chain diagnosis was run against all `10` full-day probe outputs.

Authoritative artifact:

- `/home/zepher/work/Omega_vNext_v643_probe_smoke/audit/runtime/v643_probe/gate_chain_diagnosis.json`

Key totals across `2,631,868` rows:

- `physics_valid_rows = 2,631,868`
- `energy_active_rows = 2,631,868`
- `sigma_gate_rows = 1,442,120`
- `spoof_ok_rows = 847,836`
- `epi_pos_rows = 0`
- `epi_gate_rows = 0`
- `topo_area_rows = 0`
- `topo_energy_rows = 0`
- `full_signal_gate_rows = 0`

This established:

- the signal chain is not being killed primarily by later `sigma` or `spoof` gates
- the collapse happens earlier:
  - `epiplexity` never becomes positive
  - topology outputs stay zero

## 7. Important false lead that was eliminated

At first the topology fast path looked like a new regression from the engineering patch. A real-symbol reference check on `20250725_b07c2229.parquet` showed that many `60`-bucket windows should produce non-zero closed-area / closed-perimeter geometry, but the stored `topo_area` and `topo_energy` remained zero.

However, the deeper check showed something more important:

- the Stage 2 full-day smoke outputs are heavily symbol-interleaved, not symbol-contiguous
- sampled files show `max_consecutive_same_symbol <= 5`
- therefore the current rolling boundary contract rarely accumulates long same-symbol segments in file order

This means the zero-topology condition is not yet proven to be a new fast-path regression. It could reflect a longer-standing ordering/input contract issue.

## 8. Baseline truth check

To avoid blaming the speed patch incorrectly, the original successful baseline smoke workspace was re-checked directly:

- workspace:
  - `/home/zepher/work/Omega_vNext_v643_smoke`

Result:

- baseline `20230320 -> 20230324` L2 outputs are also all zero for:
  - `epiplexity`
  - `is_signal`
  - `singularity_vector`
  - `topo_area`
  - `topo_energy`
- baseline rows are also highly symbol-interleaved

This is the most important corrective finding from this entire investigation:

- the zero-output phenomenon predates the engineering speed patch
- it is not valid evidence that the speed patch introduced a new canonical-signal regression

## 9. Current interpretation

The work is now clearly split into two problem classes.

### 9.1 Engineering speed patch evaluation

Current state:

- still uncommitted
- still unpushed
- training slowdown explained by smoke contract drift, not by the speed patch itself
- backtest file-stream path remains plausibly faster and structurally valid

### 9.2 Long-standing zero-signal / informative-slice problem

Current state:

- unresolved
- already present in the historical baseline smoke
- therefore it requires a separate scope and should not be silently folded into the engineering speed-patch verdict

## 10. Recommended next step

Do not conflate the remaining zero-signal diagnosis with the engineering speed-patch release decision.

The next mission should be split cleanly:

1. a fair engineering-evaluation mission for the speed patch
2. a separate long-standing runtime/math-contract diagnosis mission for why the approved V64.3 smoke slices remain all-zero and non-informative

## 11. Owner decision after this checkpoint

The Owner explicitly decided that both engineering routes must be preserved until the all-zero root cause is found.

This means:

- the old pre-speed engineering route remains a live baseline / fallback route
- the new engineering-speed route remains a live candidate route
- neither route may be discarded, declared canonical, or retired yet
- no release verdict may assume that the all-zero phenomenon belongs uniquely to either route until the root cause is identified
