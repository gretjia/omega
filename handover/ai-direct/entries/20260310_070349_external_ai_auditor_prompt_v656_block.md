# External AI Auditor Prompt: V656 Transition Block

Please audit the current OMEGA state after `V656 Campaign-Transition Entry Audit`.

Use repo-relative paths exactly as listed below.

Read the evidence in order and then answer the questions at the end.

Do not assume success just because the system has already repaired earlier layers.

## 1. What This Round Actually Changed

This round did **not** change:

- daily spine
- tradable label construction
- triple-barrier semantics
- pulse compression
- V655A soft-mass candidate stream
- V655B amplitude-aware daily fold
- the pure event-study gate

This round changed only:

- the **scored signal semantics**
- from campaign-state **level**
- to campaign-state **transition**

The new transition families were:

- `dPsiAmpE_10d`
- `dPsiAmpE_20d`
- `dPsiAmpStar_10d`
- `dPsiAmpStar_20d`
- `FreshAmpE_10d`
- `FreshAmpE_20d`
- `FreshAmpStar_10d`
- `FreshAmpStar_20d`

## 2. What Problems Were Encountered In This Round

There were two **engineering glue** problems, both already fixed:

1. The first remote runtime tried to execute the new V656 tool before it had been deployed to `linux1-lx`.
   Evidence:
   - `handover/BOARD.md`
   - `tools/run_campaign_transition_event_study.py`

2. After deploy, the tool still failed once because it lacked repo-root import bootstrap for:
   - `from tools.run_campaign_event_study import compute_event_study_for_signal`
   That was fixed by adding repo-root `sys.path` bootstrapping.
   Evidence:
   - `tools/run_campaign_transition_event_study.py`
   - git history around commit `efc0ce4`

These two issues are no longer the blocker.

The remaining blocker is **statistical**, not deployment-related:

- all eight transition families were non-flat
- but all eight still failed:
  - `monotonic_non_decreasing = false`

So the system is still blocked at the unchanged pure event-study gate.

## 3. Read In This Order

### Current V656 authority and result

1. `audit/v656_campaign_transition_entry_audit.md`
2. `handover/ai-direct/entries/20260310_064256_v656_campaign_transition_entry_spec_draft.md`
3. `handover/ai-direct/entries/20260310_064500_v656_spec_gemini_pass.md`
4. `handover/ai-direct/entries/20260310_064600_v656_campaign_transition_mission_open.md`
5. `audit/v656_h1_transition_event_study_block_evidence.md`
6. `handover/ai-direct/entries/20260310_065045_v656_h1_transition_event_study_blocked.md`

### The immediate predecessor that V656 reused

7. `audit/v655b_phase_amplitude_daily_fold.md`
8. `audit/v655b_h1_amp_event_study_block_evidence.md`
9. `handover/ai-direct/entries/20260310_054208_v655b_h1_amp_primary_event_study_blocked.md`

### The transition tool and the unchanged gate

10. `tools/run_campaign_transition_event_study.py`
11. `tests/test_campaign_transition_event_study.py`
12. `tools/run_campaign_event_study.py`
13. `tests/test_campaign_event_study.py`

### The frozen campaign-state forge that V656 did not change

14. `tools/forge_campaign_state.py`
15. `audit/v655a_h1_soft_mass_block_evidence.md`
16. `audit/v654_h1_psi_event_study_block_evidence.md`

### Runtime artifacts

17. `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet.meta.json`
18. `audit/runtime/v656_transition_event_study_h1_2023_20260310_065013.json`
19. `audit/runtime/v656_transition_event_study_h1_2023_20260310_065013.out`

## 4. Key Facts You Should Explicitly Verify

### From V655B forge basis

- `rows=271447`
- `symbols=5448`
- `raw_candidates=136439`
- `kept_pulses=30449`
- `excess_ret_t1_to_5d_zero_fraction = 0.0`
- `excess_ret_t1_to_10d_zero_fraction = 0.0`
- `excess_ret_t1_to_20d_zero_fraction = 0.0`

### From V656 transition study

All tested transition families had:

- `date_frac_flat_signal = 0.0`

But all also had:

- `monotonic_non_decreasing = false`

Representative outcomes:

- `dPsiAmpE_10d`
  - `d10_minus_d1=-0.0018636415316508632`
- `dPsiAmpStar_20d`
  - `d10_minus_d1=-0.009933468598393516`
- `FreshAmpE_20d`
  - `d10_minus_d1=0.004375280933147704`
  - still `monotonic_non_decreasing=false`
- `FreshAmpStar_10d`
  - `d10_minus_d1=0.0004144596430242656`
  - still `monotonic_non_decreasing=false`

## 5. Core Audit Questions

Please answer all of the following directly.

1. After V656, what is the **narrowest truthful remaining blocker**?
   - Is the system now failing because:
     - level semantics were wrong but transition semantics are still the wrong family?
     - or because the entire task of forcing these signals into an **unconditional cross-sectional decile ranker** is itself the wrong target?

2. Do the V656 results strengthen the hypothesis that:
   - OMEGA campaign-state signals may be usable only as:
     - one-sided threshold triggers
     - sign-aware hazard filters
     - regime-entry conditions
   rather than as full monotonic decile sorters?

3. Do you see any hidden implementation flaw in:
   - `tools/run_campaign_transition_event_study.py`
   - especially around:
     - symbol-boundary lagging
     - signal naming / label mapping
     - reuse of the unchanged gate
   or is the block genuinely about signal semantics rather than code correctness?

4. Given that:
   - zero-mass is gone
   - candidate mass is no longer sparse
   - amplitude fold is live
   - transition signals are non-flat
   - but monotonicity still fails
   what exact **single next mission axis** would you open?

5. If you think the next truthful target is:
   - one-sided thresholding
   - sign-aware hazard event study
   - top-decile-only entry logic
   - long/short asymmetric scoring
   then specify the narrowest mathematically defensible version of that mission.

## 6. Output Format Requested

Please respond in this exact structure:

- `Central Claim`
- `Short Verdict`
- `What V656 Definitively Proved`
- `What Remains Unproven`
- `Top Remaining Root Cause`
- `Is The Current Cross-Sectional Monotonic Gate Still The Right Gate?`
- `Concrete Bugs Or Weak Assumptions Found`
- `Recommended Next Mission`
- `Single Allowed Change Axis`
- `What Must Stay Frozen`

If you recommend a next mission, keep it narrow and operational.
