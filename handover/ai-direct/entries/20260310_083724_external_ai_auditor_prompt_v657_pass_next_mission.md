# External AI Auditor Prompt: Post-V657 Threshold Pass And Next Mission Design

Please audit the current OMEGA state after `V657 Sign-Aware Threshold Hazard Audit`.

Use repo-relative paths exactly as listed below.

Read the evidence in order and then answer the questions at the end.

This prompt is not asking for slogans. It is asking for:

- concrete guidance
- mathematical reasoning
- explicit formulas where needed
- a narrow next mission design

## 1. What V657 Actually Changed

This round did **not** change:

- `tools/forge_campaign_state.py`
- daily spine
- tradable label construction
- triple-barrier semantics
- same-sign pulse compression
- V655A soft-mass candidate stream
- V655B amplitude-aware daily fold
- V656 transition derivation formulas
- ML / Vertex / holdout closure

This round changed only:

- the **pre-ML evaluator semantics**
- from unconditional cross-sectional decile monotonic ranking
- to sign-aware, one-sided threshold / hazard evaluation

It still reused the existing V656 transition families:

- `dPsiAmpE_10d`
- `dPsiAmpE_20d`
- `dPsiAmpStar_10d`
- `dPsiAmpStar_20d`
- `FreshAmpE_10d`
- `FreshAmpE_20d`
- `FreshAmpStar_10d`
- `FreshAmpStar_20d`

## 2. What V657 Already Proved

V657 did **not** rerun forge.

It reused the frozen V655B H1 campaign matrix:

- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet`

That reused basis already had:

- `rows=271447`
- `symbols=5448`
- `raw_candidates=136439`
- `kept_pulses=30449`
- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

So by the time V657 ran, the following earlier blocker classes were already removed:

- mechanical zero-mass label defect
- candidate sparsity
- flat-signal collapse
- lack of amplitude-aware fold
- level-versus-transition ambiguity as the only explanation

## 3. What V657 Resulted In

V657 ran sign-aware threshold / hazard evaluation on the frozen V655B matrix and produced a **pass** at the evaluator stage.

Primary passing pair:

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- signed mean excess return:
  - `90.0 -> 0.003238607335437723`
  - `95.0 -> 0.004486573885058402`
  - `97.5 -> 0.0079780357263173`
- sign-aware hazard win rate:
  - `90.0 -> 0.6266216077815256`
  - `95.0 -> 0.6455278951688243`
  - `97.5 -> 0.650444762209468`
- tightening summary:
  - `signed_mean_excess_non_decreasing = true`
  - `hazard_win_rate_non_decreasing = true`
  - `tightening_improves_both = true`

Secondary passing pair:

- signal:
  - `FreshAmpStar_10d`
- side:
  - `negative`
- signed mean excess return:
  - `90.0 -> -0.006762673991573722`
  - `95.0 -> -0.0013526812097862273`
  - `97.5 -> 0.009178225074400428`
- sign-aware hazard win rate:
  - `90.0 -> 0.5486666666666666`
  - `95.0 -> 0.5733333333333333`
  - `97.5 -> 0.5933333333333333`
- tightening summary:
  - `signed_mean_excess_non_decreasing = true`
  - `hazard_win_rate_non_decreasing = true`
  - `tightening_improves_both = true`

Operationally:

- V657 **earned the one-sided threshold gate**
- V657 **did not** itself reopen ML
- no ML / Vertex / holdout run has happened after this pass

## 4. Read In This Order

### Frozen recent authorities

1. `audit/v655b_phase_amplitude_daily_fold.md`
2. `audit/v656_campaign_transition_entry_audit.md`
3. `audit/v657_sign_aware_threshold_hazard_audit.md`

### Frozen recent evidence

4. `audit/v655b_h1_amp_event_study_block_evidence.md`
5. `audit/v656_h1_transition_event_study_block_evidence.md`
6. `audit/v657_h1_sign_aware_threshold_pass_evidence.md`

### Mission specs / handover records

7. `handover/ai-direct/entries/20260310_045017_v655b_phase_amplitude_daily_fold_spec_draft.md`
8. `handover/ai-direct/entries/20260310_064256_v656_campaign_transition_entry_spec_draft.md`
9. `handover/ai-direct/entries/20260310_081031_v657_sign_aware_threshold_hazard_spec_draft.md`
10. `handover/ai-direct/entries/20260310_083550_v657_h1_sign_aware_threshold_gate_passed.md`

### Runtime artifacts

11. `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet.meta.json`
12. `audit/runtime/v656_transition_event_study_h1_2023_20260310_065013.json`
13. `audit/runtime/v657_sign_aware_threshold_h1_2023_20260310_082459/threshold_audit.json`
14. `audit/runtime/v657_sign_aware_threshold_h1_2023_20260310_082459/threshold_audit.out`

### Current tools

15. `tools/forge_campaign_state.py`
16. `tools/run_campaign_event_study.py`
17. `tools/run_campaign_transition_event_study.py`
18. `tools/run_campaign_sign_aware_threshold_audit.py`

### Current tests

19. `tests/test_campaign_event_study.py`
20. `tests/test_campaign_transition_event_study.py`
21. `tests/test_campaign_sign_aware_threshold_audit.py`

### Current live handover state

22. `handover/ops/ACTIVE_MISSION_CHARTER.md`
23. `handover/ai-direct/LATEST.md`
24. `handover/ops/ACTIVE_PROJECTS.md`

## 5. What I Need You To Determine

Please answer all of the following directly.

### A. Narrowest truthful state after V657

1. After V657, what is now the **narrowest truthful remaining blocker**?
   - Is the main problem now:
     - still pre-ML signal semantics?
     - or the translation from sign-aware threshold utility into a mathematically consistent learner / admission protocol?

2. Does V657 now justify saying:
   - “campaign-state signals have real downstream economic utility”
   but only under:
   - one-sided
   - sign-aware
   - threshold / hazard semantics
   rather than unconditional ranker semantics?

### B. Mathematical interpretation

3. Give a mathematical interpretation of why:
   - `dPsiAmpE_10d` negative tail
   - and `FreshAmpStar_10d` negative tail
   pass
   while full decile monotonic ranking failed in V655B and V656.

4. Please explicitly reason about the economics of:
   - state level
   - state transition
   - one-sided threshold trigger
   - sign-aware hazard

5. If the correct object is not a full ranker but a threshold object, write the **next correct mathematical target** explicitly.
   Examples of the level of precision wanted:
   - a trigger function
   - a sign-aware hazard label
   - a threshold-conditioned return target
   - a one-sided survival / first-passage objective

### C. Next mission design

6. Should the next mission reopen ML?
   - If yes:
     - under what exact restricted semantics?
     - with what exact labels / objective / evaluation contract?
   - If no:
     - what exact pre-ML gate is still missing?

7. If you recommend an ML-admission mission, I need you to specify the **narrowest mathematically defensible version** of it.
   Please do not answer vaguely. I need:
   - what stays frozen
   - what exact single axis changes
   - what objective function or loss is allowed
   - what validation protocol is allowed
   - what pass/fail criteria are allowed

8. If you think ML should still remain blocked, specify the exact next non-ML mission and its formulas.

### D. Weak assumptions or hidden bugs

9. Do you see any hidden implementation flaw in:
   - `tools/run_campaign_sign_aware_threshold_audit.py`
   - `tools/run_campaign_transition_event_study.py`
   - `tools/run_campaign_event_study.py`
   that could make the V657 pass misleading?

10. If not, what weak assumption is now the most dangerous one?

## 6. Required Output Structure

Please answer in this exact structure:

- `Central Claim`
- `Short Verdict`
- `What V657 Definitively Proved`
- `What Remains Unproven`
- `Top Remaining Root Cause`
- `Concrete Mathematical Interpretation`
- `Does V657 Earn ML Admission?`
- `Recommended Next Mission`
- `Single Allowed Change Axis`
- `What Must Stay Frozen`
- `Required Formulas`
- `Concrete Execution Plan`

## 7. Additional Requirement

Do not answer with only prose.

Where you recommend the next mission, include explicit formulas or pseudo-formulas for:

- the scoring object
- the label or target
- the evaluation rule
- the pass condition

The goal is not just philosophical agreement.

The goal is to produce a mathematically precise next mission that can be executed under AgentOS with minimal ambiguity.
