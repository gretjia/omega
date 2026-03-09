# V653 H1 Event Study Blocked; No ML Reopening

Timestamp: 2026-03-09 22:54 UTC
Commander: Codex
Mission: `V653 Fractal Campaign Awakening`

## 1. H1 Campaign Forge Succeeded

Runtime root:

- `audit/runtime/v653_probe_linux_h1_2023_20260309_184700`

Forge result:

- `rows=518905`
- `symbols=5511`
- `min_date=20230103`
- `max_date=20230531`
- `l1_files=118`
- `l2_files=118`
- `phase 1/4 done rows=629655 symbols=5634`
- `phase 2/4 done rows=629366 total_events=26897838`

## 2. Zero-Mass Collapse Remains Eliminated

Meta confirms:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

So the V649/V650 mechanical zero-mass bug is not present on the V653 campaign-state path, even on the widened H1 sample.

## 3. H1 Pure Event Study Result

Event-study artifacts:

- `audit/runtime/v653_probe_linux_h1_2023_20260309_184700/event_study_psi_filtered.json`
- `audit/runtime/v653_probe_linux_h1_2023_20260309_184700/event_study_omega_filtered.json`

Scored-date width:

- `n_dates_scored = 98`

Strongest family by raw appearance:

- `Omega_10d`
- `d10_mean_excess_return = 0.0013096913912808723`
- `d10_minus_d1 = 0.002140549464599314`
- `barrier_win_spread_d10_minus_d1 = 0.0023940826232707324`

But critical gate failure remains:

- `monotonic_non_decreasing = false` for:
  - `Psi_5d`
  - `Psi_10d`
  - `Psi_20d`
  - `Omega_5d`
  - `Omega_10d`
  - `Omega_20d`

Interpretation:

- the widened H1 sample still does **not** show clean top-decile monotonic domination
- therefore the pure event-study proof gate is not passed

## 4. Gemini Runtime Gate Audit

Audit mode:

- `gemini -p`

Verdict:

- `BLOCK`

Gemini conclusion:

- V653 has **not** earned ML reopening
- pure event-study monotonicity was not proven for any tested feature family

## 5. Mission-State Consequence

Automatic progression stops here.

- V653 forge path:
  - working
- V653 zero-mass fix:
  - working
- V653 pure event-study proof:
  - blocked
- ML / Vertex / XGBoost reopening:
  - **not allowed**

## 6. Final State For This Wave

This is a valid scientific result:

- the campaign-state construction fixed the mechanical target pathology
- but the widened H1 sample still failed to produce the required monotonic event-study evidence

So V653 remains a blocked research branch, not a production or ML-admitted branch.
