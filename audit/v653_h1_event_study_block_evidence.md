# V653 H1 Event-Study Block: Evidence-Only Packet

## Scope

This file records evidence and block reasons only.

It does not include:

- hypotheses
- recommendations
- preferred next steps

## Canonical Authorities

- `audit/v653_fractal_campaign_awakening.md`
- `audit/v653_identity_preservation_gemini_verdict.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`

## Freeze Context

Under V653:

- daily temporal spine is required
- campaign-state forge must precede ML
- pure event study must pass before any ML reopening

## Runtime Sequence

### 1. First repaired bounded probe failed on engineering alias bug

- runtime root:
  - `audit/runtime/v653_probe_linux_20260309_180719`
- failure file:
  - `audit/runtime/v653_probe_linux_20260309_180719/forge.out`
- error:
  - `polars.exceptions.ColumnNotFoundError`
  - missing alias:
    - `Omega_5d`

### 2. Repaired bounded probe succeeded

- runtime root:
  - `audit/runtime/v653_probe_linux_20260309_182600`
- forge log:
  - `audit/runtime/v653_probe_linux_20260309_182600/forge.out`
- output parquet:
  - `audit/runtime/v653_probe_linux_20260309_182600/campaign_matrix.parquet`
- output meta:
  - `audit/runtime/v653_probe_linux_20260309_182600/campaign_matrix.parquet.meta.json`

Bounded forge facts:

- `rows=85290`
- `symbols=5372`
- `min_date=20230103`
- `max_date=20230131`
- `l1_files=36`
- `l2_files=36`

Bounded zero-mass evidence:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

### 3. Widened H1 probe succeeded

- runtime root:
  - `audit/runtime/v653_probe_linux_h1_2023_20260309_184700`
- forge log:
  - `audit/runtime/v653_probe_linux_h1_2023_20260309_184700/forge.out`
- output parquet:
  - `audit/runtime/v653_probe_linux_h1_2023_20260309_184700/campaign_matrix.parquet`
- output meta:
  - `audit/runtime/v653_probe_linux_h1_2023_20260309_184700/campaign_matrix.parquet.meta.json`

H1 forge facts:

- `rows=518905`
- `symbols=5511`
- `min_date=20230103`
- `max_date=20230531`
- `l1_files=118`
- `l2_files=118`

H1 zero-mass evidence:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

## Event-Study Evidence

### Bounded probe event-study artifacts

- `audit/runtime/v653_probe_linux_20260309_182600/event_study_psi_filtered.json`
- `audit/runtime/v653_probe_linux_20260309_182600/event_study_omega_filtered.json`

### H1 event-study artifacts

- `audit/runtime/v653_probe_linux_h1_2023_20260309_184700/event_study_psi_filtered.json`
- `audit/runtime/v653_probe_linux_h1_2023_20260309_184700/event_study_omega_filtered.json`

H1 scored-date width:

- `n_dates_scored = 98`

### H1 filtered PSI results

- `Psi_5d`
  - `d10_mean_excess_return = -0.00122505142537985`
  - `d10_minus_d1 = 1.0902873522151664e-05`
  - `d10_barrier_win_rate = 0.2722273357461816`
  - `d1_barrier_win_rate = 0.26957221001244164`
  - `monotonic_non_decreasing = false`
  - `monotonic_positive_steps = 5`
- `Psi_10d`
  - `d10_mean_excess_return = -0.0008988553994493845`
  - `d10_minus_d1 = 0.001339827279053391`
  - `d10_barrier_win_rate = 0.3181663462647412`
  - `d1_barrier_win_rate = 0.3210096269165291`
  - `monotonic_non_decreasing = false`
  - `monotonic_positive_steps = 5`
- `Psi_20d`
  - `d10_mean_excess_return = -0.0028047225791250335`
  - `d10_minus_d1 = 0.0028107046754516102`
  - `d10_barrier_win_rate = 0.3383449865700851`
  - `d1_barrier_win_rate = 0.3405313741379188`
  - `monotonic_non_decreasing = false`
  - `monotonic_positive_steps = 5`

### H1 filtered OMEGA results

- `Omega_5d`
  - `d10_mean_excess_return = 0.0007551942603080546`
  - `d10_minus_d1 = -5.220172951263637e-05`
  - `d10_barrier_win_rate = 0.28014759320389604`
  - `d1_barrier_win_rate = 0.2718804073009678`
  - `monotonic_non_decreasing = false`
  - `monotonic_positive_steps = 4`
- `Omega_10d`
  - `d10_mean_excess_return = 0.0013096913912808723`
  - `d10_minus_d1 = 0.002140549464599314`
  - `d10_barrier_win_rate = 0.32920348525752247`
  - `d1_barrier_win_rate = 0.32680940263425173`
  - `monotonic_non_decreasing = false`
  - `monotonic_positive_steps = 5`
- `Omega_20d`
  - `d10_mean_excess_return = 0.0006244142947801914`
  - `d10_minus_d1 = 0.0023298773561849333`
  - `d10_barrier_win_rate = 0.346148321557985`
  - `d1_barrier_win_rate = 0.34430832586317733`
  - `monotonic_non_decreasing = false`
  - `monotonic_positive_steps = 5`

## Block Reasons

Blocked reasons are evidence-linked only:

1. The widened H1 pure event study did not produce `monotonic_non_decreasing = true` for any tested `Psi_*` or `Omega_*` signal family.
2. The widened H1 event study therefore did not establish clean top-decile monotonic domination.
3. Under the V653 freeze context, pure event-study proof is required before ML reopening.
4. Therefore ML reopening remained blocked.

## Formal Runtime Gate Record

- handover record:
  - `handover/ai-direct/entries/20260309_225400_v653_h1_event_study_blocked_no_ml_reopen.md`
- live operational state:
  - `handover/ai-direct/LATEST.md`
  - `handover/ops/ACTIVE_PROJECTS.md`

## External Math/Runtime Audit Verdict

- audit mode:
  - `gemini -p`
- runtime gate verdict:
  - `BLOCK`
