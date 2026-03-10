# External AI Auditor Prompt: V658 Block And Next-Step Narrowing

Please perform a recursive audit on the current frozen OMEGA evidence chain and return a concrete next-step recommendation with explicit mathematical reasoning.

This prompt is not asking for a generic opinion. It is asking for:

- a precise interpretation of the current blocker after V658
- a ranked root-cause list
- explicit guidance on what single axis should change next
- explicit guidance on what must remain frozen
- formula-level next-mission design
- concrete pass / fail criteria for that next mission

Use repo-relative paths throughout your answer.

## 1. Read These First

Core math / governance:

- `OMEGA_CONSTITUTION.md`
- `audit/v64_audit_evolution.md`
- `audit/v643.md`
- `audit/v643_auditor_pass.md`
- `audit/v653_fractal_campaign_awakening.md`
- `audit/v653_identity_preservation_gemini_verdict.md`

Campaign-state and post-V653 audit chain:

- `audit/v654_identity_preserving_pulse_compression.md`
- `audit/v654_h1_psi_event_study_block_evidence.md`
- `audit/v655_soft_mass_campaign_accumulation.md`
- `audit/v655a_h1_soft_mass_block_evidence.md`
- `audit/v655b_phase_amplitude_daily_fold.md`
- `audit/v655b_h1_amp_event_study_block_evidence.md`
- `audit/v656_campaign_transition_entry_audit.md`
- `audit/v656_h1_transition_event_study_block_evidence.md`
- `audit/v657_sign_aware_threshold_hazard_audit.md`
- `audit/v657_h1_sign_aware_threshold_pass_evidence.md`
- `audit/v658_negative_tail_hazard_admission_probe.md`
- `audit/v658_h1_ml_admission_probe_block_evidence.md`

Current live mission records:

- `handover/ai-direct/entries/20260310_081031_v657_sign_aware_threshold_hazard_spec_draft.md`
- `handover/ai-direct/entries/20260310_081335_v657_spec_gemini_pass.md`
- `handover/ai-direct/entries/20260310_083550_v657_h1_sign_aware_threshold_gate_passed.md`
- `handover/ai-direct/entries/20260310_084200_v658_negative_tail_hazard_admission_probe_spec_draft.md`
- `handover/ai-direct/entries/20260310_092918_v658_spec_gemini_pass.md`
- `handover/ai-direct/entries/20260310_093000_v658_negative_tail_hazard_admission_mission_open.md`
- `handover/ai-direct/entries/20260310_093716_v658_code_delta_gemini_pass.md`
- `handover/ai-direct/entries/20260310_095900_v658_h1_ml_admission_probe_blocked.md`
- `handover/ai-direct/LATEST.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`

Implementation files:

- `tools/forge_campaign_state.py`
- `tools/run_campaign_event_study.py`
- `tools/run_campaign_transition_event_study.py`
- `tools/run_campaign_sign_aware_threshold_audit.py`
- `tools/run_campaign_ml_admission_probe.py`
- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`
- `tests/test_campaign_transition_event_study.py`
- `tests/test_campaign_sign_aware_threshold_audit.py`
- `tests/test_campaign_ml_admission_probe.py`

Primary runtime artifacts:

- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet`
- `audit/runtime/v657_sign_aware_threshold_h1_2023_20260310_082459/threshold_audit.json`
- `audit/runtime/v658_ml_admission_probe_h1_2023_20260310_094420/admission_probe.json`
- `audit/runtime/v658_ml_admission_probe_h1_2023_20260310_094420/probe.out`

## 2. Frozen Facts You Must Respect

Please audit under these already-frozen facts:

1. V655B already eliminated the old zero-mass and candidate-sparsity failure modes on the H1 campaign matrix.
2. V656 showed that changing only from level semantics to transition semantics still did not rescue the old unconditional monotonic-decile gate.
3. V657 proved that at least some OMEGA campaign-state signals do have downstream economic utility when treated as one-sided, sign-aware threshold / hazard objects rather than as unconditional cross-sectional rankers.
4. V658 then opened only a narrow local ML-admission probe on the cleanest V657 contract:
   - signal:
     - `dPsiAmpE_10d`
   - side:
     - `negative`
   - horizon:
     - `10d`
   - threshold:
     - negative-side `90th` percentile absolute tail
   - learner:
     - fixed low-capacity `binary:logistic`
5. V658 did **not** rerun forge, did **not** reopen Vertex, did **not** touch holdouts, and did **not** widen the search surface.
6. V658 result:
   - `mission_pass=false`
   - because both forward folds failed the constant-baseline logloss gate
   - even though some same-count economic comparisons were better than the raw baseline

## 3. Most Important Runtime Numbers

From `audit/v658_h1_ml_admission_probe_block_evidence.md` and `audit/runtime/v658_ml_admission_probe_h1_2023_20260310_094420/admission_probe.json`:

Coverage:

- `n_rows_input=265999`
- `n_rows_negative_side=16117`
- `n_rows_admitted=1654`
- `n_dates_admitted=51`

Fold A:

- `logloss_model=0.6873002195762993`
- `logloss_constant=0.6868685069000361`
- `fold_pass=false`
- `alpha=0.50`
  - model beats raw on both signed return and hazard:
    - `true`
- `alpha=0.25`
  - model beats raw on both:
    - `false`

Fold B:

- `logloss_model=0.6552068498403909`
- `logloss_constant=0.6330215280784024`
- `fold_pass=false`
- `alpha=0.50`
  - model beats raw on both signed return and hazard:
    - `true`
- `alpha=0.25`
  - model beats raw on both signed return and hazard:
    - `true`

This means:

- the learner did not clearly dominate the raw same-count baseline in a trivial way
- but it also did not earn admission under the frozen calibration gate

## 4. Questions You Must Answer

Please answer these directly.

### Q1. Narrowest truthful blocker

After V658, what is the narrowest truthful remaining blocker?

I do **not** want a broad answer like “generalization risk remains.”

I want the most precise statement you can defend from the evidence.

### Q2. How should V658 be interpreted mathematically?

Please explain the exact mathematical meaning of this pattern:

- some admitted-set economic metrics improve over the raw baseline
- but logloss still loses to a constant baseline on both folds

Does this mean:

- the learner is sharpening tail selection but destroying calibration
- the admission set is too positively imbalanced / too easy for a constant baseline
- the current binary hazard objective is already misaligned
- or something else?

### Q3. Is the current V658 gate still the correct gate?

For the narrow question “should broader ML reopen now?”, is the V658 gate still the correct falsification gate?

If yes, explain why.

If no, explain exactly which part is too strong or too weak, and why changing it would still be mathematically honest rather than a goalpost move.

### Q4. What single axis should change next?

Please identify one and only one next-axis change.

I do **not** want a menu of options.

I want the narrowest next mission that you believe is mathematically defensible after V658.

### Q5. What must stay frozen?

Please explicitly list what must remain frozen from:

- forge math
- daily spine
- tradable label semantics
- barrier semantics
- V655A candidate stream
- V655B amplitude fold
- V656 transition derivations
- V657 sign-aware threshold semantics
- V658 admission contract

### Q6. Give a formula-level next mission

Please write the next mission as an execution-grade mathematical spec.

That means:

- define the object being predicted or filtered
- define the feature set
- define the loss or scoring function
- define the baseline
- define the exact pass condition
- define the exact kill condition

If you believe the next mission should remain non-ML, say so and give the formulas for that instead.

### Q7. Address selection risk directly

Please discuss the post-selection risk created by V657:

- 8 signals
- 2 sides
- 3 thresholds

If V658 was built on the cleanest selected pair from that surface, how much of the current blocker may be “picked the winner from a 48-contract search” rather than real semantic truth?

I need a concrete answer, not just a cautionary sentence.

## 5. Output Format Required

Please structure your answer in exactly this shape:

1. `Central Claim`
2. `Short Verdict`
3. `What V658 Actually Proved`
4. `Top Remaining Root Cause`
5. `Is The Current V658 Gate Still Correct?`
6. `Concrete Bugs Or Weak Assumptions Found`
7. `Recommended Next Mission`
8. `Single Allowed Change Axis`
9. `What Must Stay Frozen`
10. `Exact Mathematical Contract For The Next Mission`
11. `Pass Condition`
12. `Kill Condition`

Be explicit. Use formulas where needed. Use repo-relative paths throughout.
