# V653 Bounded Probe Succeeded; Event Gate Still Pending; H1 Probe Launched

Timestamp: 2026-03-09 18:56 UTC
Commander: Codex
Mission: `V653 Fractal Campaign Awakening`

## 1. Small Bounded Linux Probe: Forge Success

- Runtime root:
  - `audit/runtime/v653_probe_linux_20260309_182600`
- Commit lineage:
  - forge unblocked by `2f49a39`
  - zero-signal event-study filter aligned by `f26f76e`
- Successful forge facts:
  - `rows=85290`
  - `symbols=5372`
  - `min_date=20230103`
  - `max_date=20230131`
  - `l1_files=36`
  - `l2_files=36`
  - `total_events=8355345`

## 2. Zero-Mass Black Hole Is Gone On The Campaign Path

The crucial Phase-3 V653 result from the successful small probe:

- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

Interpretation:

- the mechanical zero-mass collapse that defined V649/V650 does **not** survive the V653 campaign-state construction
- the daily-spine + pure-date-only demeaning path is materially different from the old broken `["date", "time_key"]` excess-return construction

## 3. Small-Probe Event Study Verdict

Event-study outputs were run twice:

- initial date-neutral study:
  - `event_study_psi.json`
  - `event_study_omega.json`
- architect-aligned zero-signal-filtered study:
  - `event_study_psi_filtered.json`
  - `event_study_omega_filtered.json`

What passed:

- tool contract works
- retained-date diagnostics work
- zero-signal filtering works
- `D10 - D1` spread is often positive
- barrier win spread is often positive

What did **not** pass:

- no tested signal family / horizon achieved clean monotonic decile ordering
- top decile did not clearly dominate the interior deciles
- the small probe therefore does **not** yet satisfy the V653 event-study proof gate

## 4. Why The Small Probe Is Not Final

The bounded probe only scores:

- `20230103 .. 20230131`

because:

- horizons reach `20d`
- the small source window is only Jan-Feb 2023
- valid forward labels therefore truncate the scored dates hard

This makes the probe good for:

- tool-chain truth
- zero-mass validation
- early event-study contract validation

But not good enough for:

- final campaign monotonicity verdict

## 5. Next Automatic Step Already Running

A wider local Linux probe has already been launched:

- runtime root:
  - `audit/runtime/v653_probe_linux_h1_2023_20260309_184700`
- PID at launch:
  - `2475284`
- scope:
  - Linux-local `2023-01 .. 2023-06`
- input scale:
  - `L1 files=118`, about `313GB`
  - `L2 files=118`, about `4.5GB`

Purpose:

- obtain a materially wider scored date window
- rerun pure event study on a much stronger sample before any ML discussion

## 6. Current Verdict

- V653 forge path:
  - **working**
- V653 zero-mass fix:
  - **working**
- V653 pure event-study proof:
  - **not yet proven**
- H1 widened local probe:
  - **running**
