# V657 Mission Open: Sign-Aware Threshold Hazard Audit

Status: Active
Date: 2026-03-10 08:14 UTC
Mission: V657 Sign-Aware Threshold Hazard Audit

## Authority

- `audit/v657_sign_aware_threshold_hazard_audit.md`
- `handover/ai-direct/entries/20260310_081031_v657_sign_aware_threshold_hazard_spec_draft.md`
- `handover/ai-direct/entries/20260310_081335_v657_spec_gemini_pass.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`

## Frozen boundaries

- keep `tools/forge_campaign_state.py` frozen
- keep the daily spine frozen
- keep tradable labels and triple-barrier semantics frozen
- keep the V655A soft-mass candidate stream frozen
- keep the V655B amplitude-aware daily fold frozen
- keep the V656 transition derivation formulas frozen
- keep ML / Vertex / holdout closed

## Single allowed change axis

- change only the pre-ML evaluator semantics
- move from unconditional decile monotonic ranking
- to sign-aware, one-sided threshold / hazard evaluation

## Wave 1 writable files

- `tools/run_campaign_sign_aware_threshold_audit.py`
- `tests/test_campaign_sign_aware_threshold_audit.py`
- handover / audit records for V657

## Runtime basis

- reuse the frozen V655B H1 campaign matrix
- no forge rerun
- no new signal family
- no ML reopen before the V657 threshold gate passes
