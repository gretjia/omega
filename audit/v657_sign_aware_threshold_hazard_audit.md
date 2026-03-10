# V657 Sign-Aware Threshold Hazard Audit

Status: Frozen external audit authority
Date: 2026-03-10
Scope: Post-V656 contingent upgrade

## Central Judgment

The narrowest truthful remaining blocker is no longer:

- label construction
- daily-spine continuity
- candidate sparsity
- amplitude-aware folding
- simple level-versus-transition semantics

The strongest remaining blocker is:

- the assumption that OMEGA campaign-state signals should behave as unconditional, date-neutral cross-sectional decile rankers

V656 changed only the scored signal semantics from level to transition, kept forge and gate frozen, and all eight transition families were non-flat yet still failed the unchanged monotonic gate.

## Short Verdict

ML must remain blocked.

The current evidence now points more toward:

- one-sided
- sign-aware
- threshold / trigger / hazard behavior

rather than toward:

- a full monotonic decile-sorting edge

## Frozen Facts From V655B And V656

Evidence:

- `audit/v655b_h1_amp_event_study_block_evidence.md`
- `audit/v656_h1_transition_event_study_block_evidence.md`
- `audit/runtime/v655b_probe_linux_h1_2023_20260310_050315/campaign_matrix.parquet.meta.json`
- `audit/runtime/v656_transition_event_study_h1_2023_20260310_065013.json`

Frozen facts:

- `rows=271447`
- `symbols=5448`
- `raw_candidates=136439`
- `kept_pulses=30449`
- all widened zero fractions remain:
  - `0.0`
- V655B amplitude-aware families were non-flat and still failed monotonicity
- V656 transition families were non-flat and still failed monotonicity

Representative V656 results:

- `FreshAmpE_20d`
  - `d10_minus_d1=0.004375280933147704`
  - `monotonic_non_decreasing=false`
- `FreshAmpStar_10d`
  - `d10_minus_d1=0.0004144596430242656`
  - `monotonic_non_decreasing=false`

## Exact Next Axis

Do not change:

- `tools/forge_campaign_state.py`
- daily temporal spine
- tradable label construction
- triple-barrier semantics
- same-sign pulse compression
- the V655A soft-mass candidate stream
- the V655B amplitude-aware daily fold
- the V656 transition derivation formulas
- ML / Vertex / holdout boundaries

Change only:

- the pre-ML evaluator semantics

Specifically:

- move from unconditional cross-sectional decile monotonicity
- to sign-aware, one-sided threshold / hazard evaluation

## Frozen Mathematical Upgrade

### 1. Reuse Existing Signals

Wave 1 should reuse existing V656 transition families:

- `dPsiAmpE_10d`
- `dPsiAmpE_20d`
- `dPsiAmpStar_10d`
- `dPsiAmpStar_20d`
- `FreshAmpE_10d`
- `FreshAmpE_20d`
- `FreshAmpStar_10d`
- `FreshAmpStar_20d`

No new signal family is allowed in wave 1.

### 2. One-Sided Threshold Ladder

For each signal, evaluate sides separately:

- positive tail
- negative tail

Use a small threshold ladder such as:

- `90th`
- `95th`
- `97.5th`

Positive side semantics:

- trigger names whose signal is in the positive upper tail
- score with:
  - `excess_ret_t1_to_Hd`
  - `barrier_Hd == 1`

Negative side semantics:

- trigger names whose signal is in the negative lower tail
- score with:
  - `-excess_ret_t1_to_Hd`
  - `barrier_Hd == -1`

### 3. Date-Neutral Aggregation Stays

Keep date-neutral aggregation.

The question changes from:

- “is the whole decile curve monotonic?”

to:

- “does the relevant one-sided tail improve as thresholds tighten?”

## V657 Success Criteria

All of the following must hold:

1. forge remains frozen
2. signal derivations remain frozen
3. evaluator is sign-aware and one-sided
4. at least one signal-side-horizon pair shows:
   - positive signed excess return
   - positive sign-aware hazard edge
5. that pair improves as thresholds tighten

## V657 Kill Condition

Kill V657 and keep ML closed if:

- evaluator semantics are changed cleanly to the one-sided threshold / hazard form
- forge and signal derivations remain frozen
- but no signal-side-horizon pair shows a positive signed edge that strengthens as thresholds tighten

That result would justify a deeper re-interpretation, but not ML reopening.
