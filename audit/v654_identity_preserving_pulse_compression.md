# V654 Identity-Preserving Pulse Compression

Status: Frozen external execution-grade override
Date: 2026-03-10
Scope: V653 blocked event-study path -> next repair axis

## Central Judgment

V653 correctly fixed two upstream defects:

- the real daily temporal spine is now in place
- the mechanical zero-mass label defect is gone

Evidence already frozen:

- `handover/ai-direct/entries/20260309_225400_v653_h1_event_study_blocked_no_ml_reopen.md`
- `audit/v653_h1_event_study_block_evidence.md`

Under the widened H1 2023 pure event study, all tested `Psi_*` and `Omega_*` families still failed the `monotonic_non_decreasing` gate.

Therefore:

- ML reopening remains blocked
- that block is correct

## Exact Next Axis

Do not change:

- daily temporal spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier labels
- event-study decile gate
- `omega_core/*` mathematical core
- ML / Vertex / holdout boundaries

Change only:

- the `Intraday -> Symbol-Day` aggregation mathematics inside the campaign-state forge

## Canonical Diagnosis

Current `tools/forge_campaign_state.py` performs:

- daily `F_force = sum(singularity_vector)`
- daily `A_action = sum(abs(singularity_vector))`
- then campaign recursion is built only from:
  - `F_force`
  - `A_action`

Although the current forge also carries:

- `day_epi_integral`
- `day_topo_integral`

those channels do not actually participate in the campaign-state transition.

This means the current daily aggregation compresses:

- Epiplexity
- Topology
- SRL direction / phase

too early into one scalar pulse stream before EMA recursion.

## Frozen Mathematical Upgrade

### 1. Event-Level Three-Channel Identity

For each Stage2 event row `e = (i, d, b)`:

- `E_e := max(epiplexity_e, 0)`
- `T_e := max(bits_topology_e, 0)`
- `Phi_e := srl_phase_e`

Stable fallback only if `srl_phase` is absent:

- `Phi_hat_e = singularity_vector_e / (E_e + T_e + eps)`

The three channels must stay explicit.

Do not collapse them to a single scalar before pulse compression.

### 2. Candidate Filtering Before Compression

Define the intraday candidate set:

- `C_{i,d} = { e : is_physics_valid_e = 1, is_signal_e = 1, |s_e| > theta }`

Initial rule:

- reuse the current signal floor or a minimal pulse floor
- do not open a large new hyperparameter race

### 3. Same-Sign Pulse Compression

Compression must happen before daily aggregation.

Rules:

- sort intraday candidates by a stable intraday key
- priority:
  - `time_end`
  - else `bucket_id`
  - else `time`
- let `m_e = |s_e|`
- apply greedy same-sign non-maximum suppression
- if two same-sign candidates are closer than `pulse_min_gap`, keep only the larger `m_e`
- opposite-sign candidates both survive

Frozen default:

- `pulse_min_gap = 30` bars

Physical meaning:

- overlapping 60-bar rolling-window echoes must be compressed back into distinct pulses

### 4. Daily Multi-Channel Aggregation

For the compressed pulse set `P_{i,d}`:

- `F^E_{i,d} = sum_{e in P_{i,d}} E_e * sign(Phi_e)`
- `A^E_{i,d} = sum_{e in P_{i,d}} E_e`

- `F^T_{i,d} = sum_{e in P_{i,d}} T_e * sign(Phi_e)`
- `A^T_{i,d} = sum_{e in P_{i,d}} T_e`

- `F^Phi_{i,d} = sum_{e in P_{i,d}} Phi_e`
- `A^Phi_{i,d} = sum_{e in P_{i,d}} |Phi_e|`

Add diagnostics:

- `N_{i,d} = |P_{i,d}|`
- `K_{i,d} = max_e |s_e| / (sum_e |s_e| + eps)`

Interpretation:

- `N` is pulse count
- `K` is pulse concentration

### 5. Cross-Day Recursion Per Channel

For each half-life `tau in {5, 10, 20}` and each channel `X in {E, T, Phi}`:

- `S^{X,tau}_{i,d} = (1 - alpha_tau) * S^{X,tau}_{i,d-1} + alpha_tau * F^X_{i,d}`
- `V^{X,tau}_{i,d} = (1 - alpha_tau) * V^{X,tau}_{i,d-1} + alpha_tau * A^X_{i,d}`
- `Omega^{X,tau}_{i,d} = |S^{X,tau}_{i,d}| / (V^{X,tau}_{i,d} + eps)`

### 6. Directional Signal Families For Event Study

Pure coherence must not be used as the main directional alpha.

Primary event-study signal families:

- `PsiE_{i,d,tau} = S^{E,tau}_{i,d} * Omega^{E,tau}_{i,d}`
- `PsiT_{i,d,tau} = S^{T,tau}_{i,d} * Omega^{T,tau}_{i,d}`
- `PsiStar_{i,d,tau} = sign(S^{Phi,tau}_{i,d}) * sqrt(|S^{E,tau}_{i,d} * S^{T,tau}_{i,d}|) * min(Omega^{E,tau}_{i,d}, Omega^{T,tau}_{i,d}, Omega^{Phi,tau}_{i,d})`

`Omega*` families remain:

- diagnostic
- gate support
- not the primary directional event-study alpha

## Required Code Translation

### A. `tools/forge_campaign_state.py`

Replace current direct daily scalar summation with two explicit stages:

1. `_collect_intraday_candidates_from_l2()`
2. `_pulse_compress_and_aggregate_daily()`

Input columns required at minimum:

- `symbol`
- `date`
- `singularity_vector`
- `epiplexity`
- `bits_topology`
- `is_signal`
- `is_physics_valid`
- one stable intraday ordering key:
  - `time_end`
  - or `bucket_id`
  - or `time`
- `srl_phase` preferred
- or a stable fallback derivation path for phase

Fail fast:

- if no stable intraday ordering key exists, stop
- do not fake pulse compression over unordered intraday data

Add a Numba kernel such as:

- `compress_same_sign_peaks(...)`

Return at minimum:

- `F_epi`
- `A_epi`
- `F_topo`
- `A_topo`
- `F_phase`
- `A_phase`
- `pulse_count`
- `pulse_concentration`

Then expand campaign-state recursion to:

- channel-specific `S`
- channel-specific `V`
- channel-specific `Omega`
- channel-specific `Psi`

Keep baseline columns for direct comparison:

- `Psi_5d`
- `Psi_10d`
- `Psi_20d`

Add new columns:

- `PsiE_5d/10d/20d`
- `PsiT_5d/10d/20d`
- `PsiStar_5d/10d/20d`
- `OmegaE_*`
- `OmegaT_*`
- `OmegaPhase_*`
- `OmegaStar_*`

### B. `tools/run_campaign_event_study.py`

Keep the gate unchanged.

Do not redefine:

- deciling
- monotonicity
- barrier spread logic

Only align default signal coverage toward:

- `PsiE_*`
- `PsiT_*`
- `PsiStar_*`

### C. Tests

Required contract tests in:

- `tests/test_campaign_state_contract.py`

At minimum:

1. `test_same_sign_overlap_collapses_to_one_peak`
2. `test_opposite_sign_close_peaks_both_survive`
3. `test_no_signal_days_left_join_to_zero_daily_state`
4. `test_day_epi_and_day_topo_flow_into_campaign_state`
5. `test_missing_intraday_order_key_fails_fast`
6. `test_zero_fraction_remains_zero_after_v654_forge`

Required event-study compatibility tests in:

- `tests/test_campaign_event_study.py`

At minimum:

1. `test_new_signal_names_map_to_correct_horizon_labels`
2. `test_monotonic_gate_still_unchanged`
3. `test_psi_star_columns_can_be_scored_without_parser_breakage`

## Execution Order

### Phase 1: Forge only

Run a small local sample first.

Inspect:

- pulse-count distribution
- compressed/raw ratio
- `F_epi / F_topo / F_phase` non-degeneracy
- zero-filled no-signal days
- zero-fraction remains `0.0`

### Phase 2: Pure event study only

Test:

- `PsiE_*`
- `PsiT_*`
- `PsiStar_*`

Do not open ML.

### Phase 3: Gate

Promotion requires at least one directional family to satisfy:

- `monotonic_non_decreasing = true`
- `d10_minus_d1 > 0`
- `barrier_win_spread_d10_minus_d1 > 0`
- `n_dates_scored` materially non-trivial

Failure patterns that keep ML blocked:

- no directional family passes monotonicity
- only `Omega*` diagnostics look good while `Psi*` fails
- signals are too flat and `date_frac_flat_signal` remains high

## Canonical CLI Shape

Expected forge interface:

```bash
python tools/forge_campaign_state.py \
  --l1-input-pattern \"data/l1/*.parquet\" \
  --l2-input-pattern \"data/stage2/*.parquet\" \
  --output-path \"audit/runtime/v654_probe/campaign_matrix.parquet\" \
  --years 2023 \
  --horizons 5,10,20 \
  --pulse-mode sign_nms \
  --pulse-min-gap 30 \
  --require-is-signal 1 \
  --require-is-physics-valid 1
```

Expected event-study interface:

```bash
python tools/run_campaign_event_study.py \
  --campaign-path \"audit/runtime/v654_probe/campaign_matrix.parquet\" \
  --signal-col PsiE_10d \
  --signal-col PsiT_10d \
  --signal-col PsiStar_10d \
  --signal-col PsiE_20d \
  --signal-col PsiT_20d \
  --signal-col PsiStar_20d
```

## Final Mission Intent

V653 proved:

- the temporal spine is corrected
- the label contract no longer collapses into the mechanical zero-mass defect

V654 must prove:

- daily campaign-state aggregation preserves identity
- overlapping intraday echoes are compressed
- the resulting campaign-state signals yield a monotone event-study edge before any ML is reopened
