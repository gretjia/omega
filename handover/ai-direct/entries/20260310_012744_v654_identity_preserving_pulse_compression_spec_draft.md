---
entry_id: 20260310_012744_v654_identity_preserving_pulse_compression_spec_draft
task_id: V654-IDENTITY-PRESERVING-PULSE-COMPRESSION
timestamp_local: 2026-03-10 01:27:44 +0000
timestamp_utc: 2026-03-10 01:27:44 +0000
operator: Codex
role: commander
branch: main
git_head: b1ffdad
status: draft
---

# V654 Spec Draft: Identity-Preserving Pulse Compression

## 1. Mission Reason

V653 is now frozen as:

- successful on daily spine restoration
- successful on eliminating the mechanical zero-mass label defect
- blocked on pure event-study monotonicity

Canonical blocked evidence:

- `audit/v653_h1_event_study_block_evidence.md`
- `handover/ai-direct/entries/20260309_225400_v653_h1_event_study_blocked_no_ml_reopen.md`

The next mission must preserve:

- daily temporal spine
- tradable label construction
- triple-barrier semantics
- event-study decile gate

and change only one axis:

- `Intraday -> Symbol-Day` aggregation math inside the campaign-state forge

## 2. Canonical Authorities

Primary:

- `audit/v654_identity_preserving_pulse_compression.md`
- `audit/v653_fractal_campaign_awakening.md`
- `audit/v653_identity_preservation_gemini_verdict.md`

Supporting:

- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py`
- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`

## 3. Frozen Boundaries

Must remain frozen:

- real daily temporal spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier label semantics
- event-study decile monotonic gate
- `omega_core/*` mathematical core
- no ML / Vertex / holdout reopening

Permitted engineering scope:

- `tools/forge_campaign_state.py`
- minimal event-study compatibility adjustments in `tools/run_campaign_event_study.py`
- tests for the new forge contract
- handover / audit / mission docs

## 4. Core Mathematical Upgrade

### 4.1 Event-Level Identity

For each event:

- `E = max(epiplexity, 0)`
- `T = max(bits_topology, 0)`
- `Phi = srl_phase`

If `srl_phase` is absent:

- `Phi_hat = singularity_vector / (E + T + eps)`

### 4.2 Candidate Filtering

Keep only:

- `is_physics_valid = 1`
- `is_signal = 1`
- `abs(singularity_vector) > theta`

Default:

- use a minimal pulse floor
- do not open a new hyperparameter search

### 4.3 Same-Sign Pulse Compression

Within each symbol-day:

- order by stable intraday key
- keep opposite-sign candidates
- same-sign candidates closer than `pulse_min_gap` collapse via greedy NMS
- keep the larger absolute pulse

Frozen default:

- `pulse_min_gap = 30`

### 4.4 Daily Multi-Channel Aggregation

Aggregate compressed pulses into:

- `F_epi = sum(E * sign(Phi))`
- `A_epi = sum(E)`
- `F_topo = sum(T * sign(Phi))`
- `A_topo = sum(T)`
- `F_phase = sum(Phi)`
- `A_phase = sum(abs(Phi))`
- `pulse_count`
- `pulse_concentration = max(abs(s)) / (sum(abs(s)) + eps)`

### 4.5 Cross-Day Recursion

For `tau in {5,10,20}` and channels `E,T,Phi`:

- `S = EMA(F)`
- `V = EMA(A)`
- `Omega = |S| / (V + eps)`

### 4.6 Directional Signal Families

Primary event-study families:

- `PsiE_tau = S_E * Omega_E`
- `PsiT_tau = S_T * Omega_T`
- `PsiStar_tau = sign(S_Phi) * sqrt(|S_E * S_T|) * min(Omega_E, Omega_T, Omega_Phi)`

Diagnostic-only families:

- `OmegaE_tau`
- `OmegaT_tau`
- `OmegaPhase_tau`
- `OmegaStar_tau`

Keep legacy baseline columns for side-by-side comparison:

- `Psi_5d`
- `Psi_10d`
- `Psi_20d`

## 5. Phase Plan

### Phase 1: Forge-only diagnostics

Small local sample only.

Must verify:

- non-zero pulse counts
- compressed/raw ratio
- non-zero `F_epi/F_topo/F_phase`
- zero-filled no-signal dates
- zero-fraction remains `0.0`

### Phase 2: Pure event study

Test only:

- `PsiE_*`
- `PsiT_*`
- `PsiStar_*`

ML remains closed.

### Phase 3: Continuation Gate

At least one tested directional family must satisfy:

- `monotonic_non_decreasing = true`
- `d10_minus_d1 > 0`
- `barrier_win_spread_d10_minus_d1 > 0`
- `n_dates_scored` materially non-trivial

If not:

- keep ML blocked

## 6. File-Level Change Map

Primary code file:

- `tools/forge_campaign_state.py`

Secondary compatibility file:

- `tools/run_campaign_event_study.py`

Tests:

- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`

Docs:

- `audit/v654_identity_preserving_pulse_compression.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`
- `audit/README.md`

## 7. Kill Conditions

Stop if:

- stable intraday ordering key is absent
- the new forge changes label semantics
- the new forge reopens ML implicitly
- only `Omega*` improves while all directional `Psi*` families still fail monotonicity
- signal flatness remains high enough to invalidate decile ranking

## 8. Definition of Done for Wave 1

- V654 authority landed under `audit/`
- spec audited by `gemini -p`
- active charter switched
- first forge code wave landed
- local tests pass
- first local forge/event-study probe recorded
