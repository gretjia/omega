---
entry_id: 20260309_172447_v653_fractal_campaign_awakening_spec_draft
task_id: TASK-V653-FRACTAL-CAMPAIGN-AWAKENING
timestamp_local: 2026-03-09 17:24:47 +0000
timestamp_utc: 2026-03-09 17:24:47 +0000
operator: Codex
role: commander
branch: main
git_head: 45e81f3
status: draft_gemini_passed_pending_owner_confirmation
---

# V653 Spec Draft: Fractal Campaign Awakening

## 1. Why This Mission Exists

New top-level architect authority:

- `audit/v653_fractal_campaign_awakening.md`

This override supersedes V652 before execution.

The new truth is:

- the old problem is not just target horizon,
- and not just campaign rolling windows,
- but the absence of a real daily temporal spine plus the wrong state equation.

So the upgrade must move from:

- sparse micro-return logic

to:

- a **daily-spine recursive campaign-state machine**

## 2. Absolute Freeze Rules

Non-negotiable mathematical freeze:

- the formulas in `audit/v653_fractal_campaign_awakening.md` are frozen
- `delta = 0.5` remains frozen
- `canonical_v64_1` Stage3 gates remain frozen unless truth-first implementation proves they must be recomputed identically through a fresh run
- no edits may change the mathematical meaning of:
  - `F`
  - `A`
  - `S`
  - `V`
  - `Omega`
  - `Psi`
  - tradable `Y_ret`
  - triple-barrier first-passage label

Allowed implementation freedom:

- `omega_core/*`
- `tools/*`
- Stage2 recomputation
- schema redesign
- daily-spine artifact creation
- Numba kernel implementation

provided that:

- the mathematical meaning of the frozen formulas does not change
- all formula-bearing diffs are audited with:
  - `gemini -p`
  - default `gemini 3.1 pro preview`

## 3. Mission Objective

Open a large AgentOS upgrade that executes four truth-first phases:

1. rebuild or validate a real daily spine
2. forge recursive campaign-state tensors from micro singularity pulses
3. prove edge through pure event study and first-passage barriers
4. only then decide whether ML is worth reopening

ML is downstream of proof, not part of proof.

## 4. Canonical Mathematical Contract

### 4.1 Pulse Compression & Daily Fold

For symbol `i`, trade date `d`, intraday event set `E_{i,d}`:

- `F_{i,d} = sum_{e in E_{i,d}} s_{i,d,e}`
- `A_{i,d} = sum_{e in E_{i,d}} |s_{i,d,e}|`

Hard rule:

- use a real continuous trading-date spine
- valid no-signal dates are explicitly:
  - `F = 0`
  - `A = 0`

### 4.2 Recursive Campaign State

For half-life `tau in {5, 10, 20}`:

- `S_{i,d}^{(tau)} = EMA_tau(F_{i,d})`
- `V_{i,d}^{(tau)} = EMA_tau(A_{i,d})`
- `Omega_{i,d}^{(tau)} = |S_{i,d}^{(tau)}| / (V_{i,d}^{(tau)} + eps)`
- `Psi_{i,d}^{(tau)} = S_{i,d}^{(tau)} * Omega_{i,d}^{(tau)}`

### 4.3 Tradable Excess Label

For horizon `H in {5, 10, 20}`:

- entry:
  - `P_open(i, d+1)`
- exit:
  - `P_close(i, d+H)`
- label:
  - `Y_ret_{i,d,H} = P_close(i,d+H) / P_open(i,d+1) - 1 - Rbar_date,H`

Hard demeaning rule:

- only by:
  - `pure_date`
- never by:
  - `["date", "time_key"]`

### 4.4 Triple-Barrier Hazard

For horizon `H in {5, 10, 20}`:

- entry price:
  - `entry = P_open(i, d+1)`
- profit barrier:
  - `entry * (1 + 2 * sigma)`
- stop barrier:
  - `entry * (1 - 1 * sigma)`
- conservative precedence:
  - stop/tie wins first

## 5. Large-Team AgentOS Design

This mission uses an expanded luxury team.

### Commander

- owns scope, integration, git, deployment, and handover

### Formula Integrity Auditor

- engine:
  - `gemini -p`
- model rule:
  - only default `gemini 3.1 pro preview`
- authority:
  - every formula-bearing diff

### Temporal Spine Engineer

- ownership:
  - daily spine artifact construction
  - zero-fill alignment on real trading dates

### Stage2 Integrity / Recompute Engineer

- ownership:
  - determine whether current Stage2 outputs are sufficient
  - if not, execute a truth-first Stage2 recompute plan

### Campaign State Forge Engineer

- ownership:
  - `tools/forge_campaign_state.py`
  - state tensor implementation

### Numba Barrier Kernel Engineer

- ownership:
  - O(N) first-passage kernel
  - correctness and speed of barrier labeling

### Core Integration Engineer

- ownership:
  - any required `omega_core/*` changes
- restriction:
  - implementation translation only
  - no formula drift

### Data Contract Auditor

- ownership:
  - required columns
  - schema continuity
  - artifact lineage

### Distribution Auditor

- ownership:
  - verify zero-mass bug is gone
  - verify correct date-only demeaning

### Event Study Auditor

- ownership:
  - decile monotonicity
  - top-vs-bottom spread
  - barrier-hit asymmetry

### Runtime Orchestrator

- ownership:
  - node assignment
  - runtime isolation
  - truth-first sequencing

### ML Readiness Gatekeeper

- ownership:
  - block all ML until event study passes

## 6. Engineering Translation Plan

### Phase A: Daily Spine

Create a canonical daily-spine artifact for the target years that contains at minimum:

- `symbol`
- `pure_date`
- `open`
- `high`
- `low`
- `close`

This must be calendar-dense over valid trading dates.

### Phase B: Micro Pulse Source

Use current Stage2 outputs if they already provide the required pulse source:

- `singularity_vector`

If they do not, Stage2 recomputation is authorized.

### Phase C: Campaign Forge

Create:

- `tools/forge_campaign_state.py`

This tool must:

- read:
  - daily spine
  - Stage2/source matrix with singularity pulses
- fold micro events to symbol-day `F/A`
- zero-fill no-signal dates on the real daily spine
- compute `S/V/Omega/Psi` via EMA with `tau in {5,10,20}`
- compute:
  - `excess_ret_t1_to_5d`
  - `excess_ret_t1_to_10d`
  - `excess_ret_t1_to_20d`
- compute:
  - `barrier_5d`
  - `barrier_10d`
  - `barrier_20d`

### Phase D: Pure Event Study

Create:

- `tools/run_campaign_event_study.py`

This tool must, for at least `Psi_10d` and `Psi_20d`:

- decile-sort names
- compute mean future excess return by decile
- compute barrier-hit win rate by decile
- compute:
  - `D10 - D1`
- test monotonicity

## 7. Runtime Shape

### Phase 0: Spec / Formula Freeze

- land architect override
- audit spec with `gemini -p`
- no execution

### Phase 1: Data/Spine Readiness

- default node bias:
  - controller for small proofs
  - `windows1-w1` for heavy local forge if faster
  - `linux1-lx` for parity / overflow / recompute work

### Phase 2: Campaign Forge

- local-only
- no cloud
- no holdout use yet
- fresh isolated prefixes

### Phase 3: Event Study

- local-only
- no ML
- no Vertex

### Phase 4: ML Admission Review

- only if event study proves monotonicity
- ML may become a separate sub-mission

## 8. Writable Scope

Expected writable files:

- `omega_core/*` where strictly required
- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py`
- `tools/forge_base_matrix.py` if bridging is still needed
- `tools/stage2_physics_compute.py` only if truth-first Stage2 recompute becomes necessary
- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`
- V653 handover / audit docs

Deferred until ML admission only:

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`

## 9. Hard Out-Of-Scope Before Event-Study Pass

Before event study passes, V653 must not:

- reopen Path A
- launch Vertex / GCP
- consume `2025` or `2026-01` holdouts
- tune XGBoost
- alter the frozen formulas

## 10. Acceptance Gates Before Any ML

The branch earns continuation only if:

1. **Temporal spine is repaired**
   - no sparse pseudo-time rolling
2. **Zero-mass bug is eliminated**
   - campaign labels no longer show the pathological near-all-zero profile of old `t1_excess_return`
3. **Campaign tensors are non-degenerate**
   - `Psi_5d/10d/20d` have real cross-sectional variance
4. **Pure event study is structurally positive**
   - for at least one horizon:
     - `D10 mean excess return > 0`
     - `D10 - D1 > 0`
     - top-decile barrier hit rate exceeds bottom-decile barrier hit rate
5. **Monotonicity is visible**
   - at least one horizon shows clear positive decile ordering

## 11. Kill Condition

Kill ML escalation if:

- daily spine is corrected
- campaign state is correctly forged
- but event-study monotonicity still does not appear across `5d/10d/20d`

If that happens, the next mission is not an engineering patch.

It becomes a deeper physical reinterpretation or market-structure mission.

## 12. Commander Notes

- V652 is superseded before execution
- truth-first may justify `omega_core/*` changes
- truth-first may justify Stage2 recomputation
- math audit must always use:
  - `gemini -p`
  - default `gemini 3.1 pro preview`

## 13. Definition Of Done For Draft Stage

This draft is ready for owner confirmation only when:

- the architect override is landed under `audit/`
- the formulas are frozen in writing
- the large-team structure is explicit
- `gemini -p` has audited the draft and any required fixes are folded in

Only after owner confirmation may:

- the active charter be switched
- V653 execution begin
