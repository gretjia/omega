---
entry_id: 20260309_161916_v652_campaign_state_revelation_spec_draft
task_id: TASK-V652-CAMPAIGN-STATE-REVELATION
timestamp_local: 2026-03-09 16:19:16 +0000
timestamp_utc: 2026-03-09 16:19:16 +0000
operator: Codex
role: commander
branch: main
git_head: c95c959
status: draft_pending_owner_confirmation
---

# V652 Spec Draft: Campaign-State Revelation Upgrade

## 1. Why This Mission Exists

New top-level architect authority:

- `audit/v652_campaign_state_revelation.md`

That override reframes the problem at a higher level than V651:

- the issue is not merely that `t1` is too short
- the issue is that OMEGA is still trying to map a campaign-scale physical process into microscopic payoff logic

The owner has also made the operating philosophy explicit:

- not high-frequency
- not next-tick gambling
- several days to at least 4 weeks of campaign release are economically meaningful

Therefore the next upgrade must lift OMEGA from a micro-return interface into a **campaign-state machine** while keeping the architect formulas frozen as the real red line.

## 2. Absolute Freeze Rules

These rules are non-negotiable:

- the formulas in `audit/v652_campaign_state_revelation.md` are frozen
- `delta = 0.5` is frozen
- `canonical_v64_1` Stage3 gates are frozen
- no edits are allowed to the core mathematical meaning of:
  - `F`
  - `A`
  - `C`
  - `Omega`
  - `M`
  - `Y_ret`
  - triple-barrier hazard

Allowed implementation freedom:

- file layout
- artifact schema
- grouping-key cleanup
- field plumbing
- runtime orchestration
- variable-name typo correction where the frozen formulas already make the intent unambiguous
- necessary code changes inside:
  - `omega_core/*`
  - `tools/*`

provided that:

- the mathematical meaning of the formulas does not change
- every formula-bearing diff is audited against the frozen architect formulas

## 3. Mission Objective

Open a large AgentOS upgrade mission that does three things in sequence:

1. forge a local campaign-state matrix from the frozen V64 feature lineage
2. prove the mechanical zero-mass bug disappears under the corrected campaign-state target construction
3. prove campaign-state monotonicity through a pure event study before any ML escalation

ML remains a later phase, not the opening move.

## 4. Canonical Mathematical Contract

### Layer 1: Intraday -> Symbol-Day

For each symbol `i` and trade date `d`:

- `F_{i,d} = sum_b SingularityVector_{i,d,b}`
- `A_{i,d} = sum_b |SingularityVector_{i,d,b}|`
- `C_{i,d} = |F_{i,d}| / (A_{i,d} + eps)`

### Layer 2: Symbol-Day -> Multi-Week Campaign

For campaign horizon `H`:

- `Omega_{i,d}^{(H)} = |sum_{k=0}^{H-1} F_{i,d-k}| / (sum_{k=0}^{H-1} A_{i,d-k} + eps)`
- `M_{i,d}^{(H)} = Omega_{i,d}^{(H)} * sum_{k=0}^{H-1} F_{i,d-k}`

### Layer 3: Labels

True excess return:

- `Y_ret_{i,d,H} = (P_{i,d+H} / P_{i,d} - 1) - Rbar_{d,H}`

Triple barrier:

- `+2 sigma` first:
  - `1`
- `-1 sigma` first:
  - `-1`
- otherwise:
  - `0`

Hard demeaning rule:

- cross-sectional demeaning must be by:
  - `pure_date`
- never by:
  - `["date", "time_key"]`

## 5. Initial Campaign Horizons

The bounded first ladder is:

- `5d`
- `10d`
- `20d`

Interpretation:

- `5d`:
  - about 1 trading week
- `10d`:
  - about 2 trading weeks
- `20d`:
  - about 4 trading weeks

These horizons are part of the frozen campaign-state contract for wave 1.

They are separate fixed analyses.

V652 must not:

- blend horizons
- average horizons into one target
- open a larger horizon race before the first ladder is audited

## 6. Engineering Translation Plan

The architect pseudocode targets `base_matrix.parquet`, but the current live base-matrix contract does not expose all required fields as ready-made output columns.

So V652 uses a two-step engineering translation while preserving the frozen math:

### Step A: Campaign-ready train matrix bridge

Create a fresh local train-only artifact for `2023,2024` that preserves the fields needed by the campaign forge, including at minimum:

- `symbol`
- `date`
- `bucket_id` or `time_end`
- `close`
- `singularity_vector`
- `epiplexity`
- `bits_topology` if available from the frozen lineage

This bridge may require engineering work in:

- `tools/forge_base_matrix.py`
- `omega_core/*` if strictly required to preserve the frozen formulas through the canonical core

but such changes are allowed only as implementation translation, not as formula redefinition.

### Step B: Campaign matrix forge

Create:

- `tools/forge_campaign_matrix.py`

This tool must:

- normalize `date -> pure_date`
- collapse intraday rows to symbol-day
- build `F`, `A`, `C`
- build campaign `Omega` and `M` over `5d/10d/20d`
- compute `raw_fwd_ret_{H}d`
- compute `excess_ret_{H}d` with pure-date-only demeaning
- compute `barrier_hit_{H}d`

### Step C: Event-study gate

Create:

- `tools/run_campaign_event_study.py`

This tool must:

- sort symbols into deciles by `camp_momentum_{H}d`
- compute future mean excess return by decile
- compute decile spread:
  - `D10 - D1`
- compute barrier hit rates by decile
- measure monotonicity

## 7. Large-Team AgentOS Design

This mission needs more than the default trio.

### Commander

- owns scope, integration, git, deployment, and handover

### Formula Integrity Auditor

- engine:
  - `gemini -p`
- authority:
  - every formula-bearing diff must be audited against `audit/v652_campaign_state_revelation.md`

### Campaign Forge Engineer

- ownership:
  - `tools/forge_campaign_matrix.py`
  - any narrow bridge work in `tools/forge_base_matrix.py`

### Core Integration Engineer

- ownership:
  - any required `omega_core/*` changes needed to faithfully implement the frozen campaign-state formulas
- restriction:
  - may not redefine formulas
  - may only translate them into the canonical core

### Data Contract Auditor

- ownership:
  - schema correctness
  - field availability
  - no accidental loss of required columns

### Distribution Auditor

- ownership:
  - verify zero-mass collapse disappears
  - verify demeaning is by `pure_date` only

### Event Study Auditor

- ownership:
  - verify decile monotonicity
  - verify barrier-hit asymmetry
  - decide whether ML phase may open

### Runtime Orchestrator

- ownership:
  - node assignment
  - artifact isolation
  - no-cloud/no-holdout discipline for early phases

### ML Readiness Gatekeeper

- ownership:
  - block any XGBoost / Vertex step until event-study gate is passed

## 8. Runtime Shape

### Phase 0: Formula Freeze

- land the new architect override
- audit the spec with `gemini -p`
- no execution yet

### Phase 1: Campaign-ready train matrix bridge

- node bias:
  - `windows1-w1` first, because previous local forge work was faster there
- dataset role:
  - `2023,2024` train-only
- no holdouts
- no GCP

### Phase 2: Campaign matrix forge

- local-only
- fresh isolated prefixes
- no overwrite of existing V64 / V645 / V650 evidence

### Phase 3: Event study

- pure research gate
- no ML
- no cloud

### Phase 4: ML admission review

- only opens if event study passes
- may later create a separate ML sub-mission

## 9. Writable Scope

Expected writable files:

- `omega_core/*` where strictly required by the frozen architect formulas
- `tools/forge_base_matrix.py` (bridge only, if required)
- `tools/forge_campaign_matrix.py`
- `tools/run_campaign_event_study.py`
- `tests/test_campaign_matrix_contract.py`
- `tests/test_campaign_event_study.py`
- handover / audit docs for V652

Deferred until Phase 4 only:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`

## 10. Hard Out-Of-Scope For Early Phases

Before event-study pass, V652 must not:

- reopen Path A
- launch Vertex / GCP
- consume `2025` or `2026-01` holdouts
- tune XGBoost
- alter the frozen formulas

## 11. Phase-2 / Phase-3 Acceptance Gates

The campaign forge and event study earn continuation only if all of the following happen:

1. **Zero-mass collapse is materially reduced**
   - `excess_ret_10d` and/or `excess_ret_20d` must no longer show the pathological near-all-zero profile seen under `t1`
2. **Campaign-state fields are non-degenerate**
   - `camp_momentum_5d/10d/20d` must have real cross-sectional variance
3. **Event-study edge is structurally positive**
   - for at least one horizon:
     - `D10 mean excess return > 0`
     - `D10 - D1 > 0`
     - top-decile barrier win rate exceeds bottom-decile barrier win rate
4. **Monotonicity is visible**
   - at least one horizon must show clear positive ordering from lower to higher deciles

## 12. Kill Condition

Kill the branch before ML if:

- pure-date demeaning is corrected
- campaign-state matrix is successfully forged
- but the event study still fails to show positive monotonicity or positive top-decile asymmetry across `5d/10d/20d`

If that happens, the next mission is no longer an engineering glue mission.

It becomes a deeper mathematical or market-regime reinterpretation mission.

## 13. AgentOS Convergence Used In This Draft

Plan child:

- returned `PASS WITH FIXES`
- warned that formula text must be treated as the canonical boundary

Commander codebase readback:

- current live base matrix contract only persists `t1_fwd_return`
- current downstream excess-return construction still uses a time-key demeaning path
- current forge pipeline already sees `close` and `singularity_vector` in the raw lineage
- `bits_topology` exists in frozen kernel outputs, but may require an explicit bridge to persist into the campaign-ready matrix

Math audit for final draft approval is delegated to:

- `gemini -p`

## 14. Definition Of Done For Draft Stage

This draft is ready for owner confirmation only when:

- the architect override is landed under `audit/`
- the formulas are frozen in writing
- the new team structure is explicit
- `gemini -p` has audited the draft and any required fixes are folded in

Only after owner confirmation may:

- the active charter be switched
- Phase 1 execution begin
