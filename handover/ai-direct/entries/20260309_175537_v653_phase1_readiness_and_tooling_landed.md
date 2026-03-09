---
entry_id: 20260309_175537_v653_phase1_readiness_and_tooling_landed
task_id: TASK-V653-FRACTAL-CAMPAIGN-AWAKENING
timestamp_local: 2026-03-09 17:55:37 +0000
timestamp_utc: 2026-03-09 17:55:37 +0000
operator: Codex
role: commander
branch: main
status: in_progress
---

# V653 Phase-1 Readiness And Tooling Landed

## 1. Readiness Verdict

Phase-1 readiness conclusion:

- `bridge first`
- no immediate Stage2 recomputation is required to open V653

## 2. Evidence

### Pulse source is already present in Stage2 L2

Observed on `linux1-lx`:

- `/omega_pool/parquet_data/stage2_full_20260307_v643fix/l2/host=linux1/20230103_fbd5c8b.parquet`

Observed columns include:

- `symbol`
- `date`
- `bucket_id`
- `open`
- `close`
- `epiplexity`
- `bits_topology`
- `singularity_vector`

Interpretation:

- current L2 is a sufficient micro pulse source for:
  - `F`
  - `A`
  - daily pulse integrals

### Daily spine can come from existing raw Stage2 input

Observed on `linux1-lx`:

- `/omega_pool/parquet_data/stage2_full_20260307_v643fix/input_linux1/20230103_fbd5c8b.parquet`

Observed on mounted Windows corpus from `linux1-lx`:

- `/home/zepher/windows_d_sshfs/Omega_frames/stage2_full_20260307_v643fix/input_windows1/20240717_b07c2229.parquet`

Observed columns include:

- `symbol`
- `date`
- `time`
- `price`

Interpretation:

- true daily `open/high/low/close` can be derived from raw ticks
- this avoids the sparse pseudo-time bug
- no immediate `omega_core/*` or Stage2 recompute is required for the first bridge

### Training-domain split reality

Observed from:

- `/home/zepher/work/Omega_vNext/audit/runtime/stage3_base_matrix_train_20260308_095850/input_files_train_2023_2024.txt`

Training manifest counts:

- total files:
  - `484`
- Linux L2:
  - `370`
- Windows L2 via sshfs:
  - `114`

Interpretation:

- V653 Phase 1 must be able to consume a dual-source training domain
- Linux can still act as the first unified execution surface because the Windows half is already mounted via sshfs

## 3. Tooling Landed

New tools:

- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py`

New tests:

- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`

## 4. Math Audit

Audit path:

- `gemini -p`

Model authority:

- default `gemini 3.1 pro preview`

Verdict:

- `PASS`

Audit focus:

- frozen V653 formulas preserved
- daily spine from raw L1 plus pulse source from L2 is mathematically acceptable
- next-open tradable label is correctly implemented
- demeaning is by `pure_date` only
- triple-barrier semantics match the frozen contract

## 5. Verification

Completed locally:

- `python3 -m py_compile`
  - `tools/forge_campaign_state.py`
  - `tools/run_campaign_event_study.py`
  - `tests/test_campaign_state_contract.py`
  - `tests/test_campaign_event_study.py`

Not yet completed:

- functional execution of the new tools
- pytest execution of the new tests

Reason:

- controller currently lacks the local `polars` runtime required for functional execution
- the next step should use the normal `commit + push + deploy` path to a node with the required runtime

## 6. Immediate Next Step

Next justified step:

- commit this V653 wave
- deploy to the target worker
- run a bounded campaign-state forge probe
- then run a first pure event-study probe before any wider execution
