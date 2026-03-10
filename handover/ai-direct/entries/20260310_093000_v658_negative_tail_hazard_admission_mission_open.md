# V658 Mission Open: Negative-Tail Hazard Admission Probe

Status: Active
Date: 2026-03-10 09:30 UTC
Mission: V658 Negative-Tail Hazard Admission Probe

## Authority

- `audit/v658_negative_tail_hazard_admission_probe.md`
- `handover/ai-direct/entries/20260310_084200_v658_negative_tail_hazard_admission_probe_spec_draft.md`
- `handover/ai-direct/entries/20260310_092918_v658_spec_gemini_pass.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`

## Frozen boundaries

- keep `tools/forge_campaign_state.py` frozen
- keep daily spine frozen
- keep `entry_open_t1`, `excess_ret_t1_to_Hd`, and triple-barrier semantics frozen
- keep same-sign pulse compression frozen
- keep the V655A soft-mass candidate stream frozen
- keep the V655B amplitude-aware daily fold frozen
- keep the V656 transition derivation formulas frozen
- keep the frozen V655B H1 campaign matrix frozen
- keep ML / Vertex / holdout closed outside this narrow admission probe

## Single allowed change axis

- change only the admission protocol
- from raw threshold trigger
- to trigger-conditioned hazard learner

## Frozen primary contract

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- horizon:
  - `10d`
- admission threshold:
  - negative-side `90th` percentile of absolute magnitude

## Wave 1 writable files

- `tools/run_campaign_ml_admission_probe.py`
- `tests/test_campaign_ml_admission_probe.py`
- handover / audit records for V658
