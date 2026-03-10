# V659 Spec Draft: Fixed-Contract Replication Audit

Status: Draft for owner confirmation
Date: 2026-03-10
Mission: V659 Fixed-Contract Replication Audit

## 1. Why This Mission Exists

V657 proved that at least one OMEGA campaign-state contract has one-sided sign-aware downstream utility:

- `dPsiAmpE_10d`
- `negative`
- threshold ladder:
  - `90`
  - `95`
  - `97.5`

V658 then tested a narrow learner only inside that admitted set and failed the admission gate because both forward folds lost to the constant-baseline logloss, even though some same-count economic comparisons beat the raw baseline.

So the next honest question is not:

- broader ML reopening

It is:

- whether the fixed V657 winner replicates outside the slice on which it was selected

## 2. Single Allowed Change Axis

Change only the evaluation sample.

Specifically:

- move from the H1 2023 selection slice used by V657 / V658
- to the first non-overlapping contiguous replication block available under the same frozen forge, label, transition, and evaluator semantics

This mission must not change:

- forge math
- signal definitions
- threshold ladder
- side semantics
- learner contract
- or ML closure

## 3. Frozen Boundaries

Keep frozen:

- `tools/forge_campaign_state.py`
- the repaired daily spine
- tradable labels:
  - `entry_open_t1`
  - `excess_ret_t1_to_Hd`
- triple-barrier semantics
- same-sign pulse compression
- the V655A soft-mass candidate stream
- the V655B amplitude-aware daily fold
- the V656 transition derivation formulas
- the V657 sign-aware threshold semantics
- the V658 blocked admission probe as a read-only artifact
- all broader ML / Vertex / holdout workflows

## 4. Mission Objective

Run a pure non-ML replication audit on one frozen contract only:

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- thresholds:
  - `90`
  - `95`
  - `97.5`

The mission succeeds only if this exact contract preserves its one-sided threshold / hazard utility on a disjoint contiguous replication window under unchanged scoring semantics.

## 5. Canonical Mathematical Contract

Let:

- `x_{i,d} := dPsiAmpE_10d(i,d)`

where `dPsiAmpE_10d` is derived by the unchanged V656 transition semantics on a campaign matrix forged by unchanged V655B math.

Let the replication date set be:

- `D_rep`

with hard rules:

- `D_rep` is contiguous
- `D_rep` does not overlap the H1 2023 selection slice used in V657 / V658

For each date `d`, define the negative-side universe:

- `N_d := { i : x_{i,d} < -eps }`

For each fixed threshold `q in {0.90, 0.95, 0.975}`, define the selected set:

- `S_{d,q} := { i in N_d : |x_{i,d}| >= Q_q(|x_{j,d}| : j in N_d) }`

Signed economics remain exactly V657:

- `R_{i,d} := -excess_ret_t1_to_10d(i,d)`
- `Y_{i,d} := 1{ barrier_10d(i,d) = -1 }`

Negative-side universe baselines:

- `Rbar^N := date-neutral mean of R over N_d`
- `Hbar^N := date-neutral mean of Y over N_d`

Threshold summaries:

- `Rbar_q := date-neutral mean of R over S_{d,q}`
- `Hbar_q := date-neutral mean of Y over S_{d,q}`

This mission has:

- no learner
- no objective optimization
- no signal search
- no threshold search

## 6. Runtime Shape

### Phase 1: Replication window discovery

Discover the first non-overlapping contiguous block after the V657/V658 H1 2023 slice using the same frozen campaign forge semantics.

The discovery step may inspect:

- available L1 dates
- available L2 dates
- date continuity after horizon trimming

But it may not change forge logic.

### Phase 2: Frozen campaign forge on the replication block

Run the unchanged V655B forge on the replication window only.

Allowed change:

- input date range only

Forbidden changes:

- no formula edits
- no candidate-stream edits
- no pulse-compression edits
- no amplitude-fold edits

### Phase 3: Frozen sign-aware threshold audit

Run only the existing sign-aware evaluator semantics on:

- `dPsiAmpE_10d`
- `negative`
- `90`
- `95`
- `97.5`

No other signals, sides, or thresholds are allowed in this mission.

## 7. Large-Team AgentOS Layout

Commander:

- owns scope
- integrates code and docs
- owns git / push / handover

Formula Integrity Auditor:

- engine:
  - direct `/usr/bin/gemini`
- model rule:
  - `gemini 3.1 pro preview` only
- responsibility:
  - audit every formula-bearing or mission-boundary change against:
    - `audit/v659_fixed_contract_replication_audit.md`

Replication Window Auditor:

- responsibility:
  - prove the replication block is contiguous
  - prove it does not overlap the V657/V658 selection slice

Campaign Forge Reuse Engineer:

- responsibility:
  - rerun unchanged forge math on the replication window only

Sign-Aware Evaluator Engineer:

- responsibility:
  - reuse the frozen V657 evaluator semantics on the fixed contract only

Coverage Auditor:

- responsibility:
  - verify scored-date coverage
  - verify selected-row counts tighten monotonically

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - keep local-only / no-ML / no-cloud sequencing
  - monitor progress by actual artifacts and process evidence only

ML Readiness Gatekeeper:

- responsibility:
  - keep broader ML / Vertex / holdout closed unless V659 passes

## 8. Writable Scope

Expected writable files:

- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/*`
- `handover/BOARD.md`
- `audit/README.md`
- `audit/v659_fixed_contract_replication_audit.md`

Wave-1 code expectation:

- ideally no formula code change at all
- if a thin execution helper is needed, it must be a wrapper only and must not change frozen evaluator or forge semantics

## 9. Out Of Scope

Before V659 passes, do not:

- reopen broad ML
- reopen Vertex / GCP
- reopen holdouts
- widen the signal family
- test the positive side
- search new thresholds
- change forge math
- change labels or barriers
- change V656 transitions
- change V657 evaluator semantics
- reopen V658 with a different learner or loss

## 10. Pass Condition

V659 passes only if all of the following hold on `D_rep`:

1. Coverage:
   - `n_dates_scored(q) >= 40`
   - for each `q in {0.90, 0.95, 0.975}`
2. Tightening preserves sparsity:
   - scored-row counts are non-increasing as thresholds tighten
3. Signed-return tightening is non-decreasing:
   - `Rbar_0.90 <= Rbar_0.95 <= Rbar_0.975`
4. Sign-aware hazard tightening is non-decreasing:
   - `Hbar_0.90 <= Hbar_0.95 <= Hbar_0.975`
5. Strongest threshold beats the within-side universe baseline on both metrics:
   - `Rbar_0.975 > Rbar^N`
   - `Hbar_0.975 > Hbar^N`
6. Strongest threshold is economically positive:
   - `Rbar_0.975 > 0`

## 11. Kill Condition

Kill V659 immediately if:

- the replication window overlaps the H1 2023 selection slice
- any forge, label, barrier, transition, threshold, or side semantics are changed
- any threshold has fewer than `40` scored dates
- tightening fails on signed return
- tightening fails on sign-aware hazard
- the strongest threshold does not beat the negative-side universe on both metrics

If V659 fails, the honest interpretation is:

- the current V657 winner is not yet replicated strongly enough to justify broader ML admission

## 12. Definition Of Done For Draft Stage

This draft is ready for owner confirmation only when:

- the new auditor verdict is landed under `audit/`
- the single change axis is explicit:
  - replication sample only
- the frozen boundaries are explicit
- the multi-agent layout is explicit
- Gemini mathematical audit has passed and any required fixes are folded in

Only after owner confirmation may:

- the active charter be switched
- runtime execution begin
