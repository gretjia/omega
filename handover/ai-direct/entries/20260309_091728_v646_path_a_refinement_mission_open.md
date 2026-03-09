---
entry_id: 20260309_091728_v646_path_a_refinement_mission_open
task_id: TASK-V646-PATH-A-REFINEMENT
timestamp_local: 2026-03-09 09:17:28 +0000
timestamp_utc: 2026-03-09 09:17:28 +0000
operator: Codex
role: commander
branch: main
git_head: bf57be0
status: active
---

# V646 Mission Open: Path A Refinement

## 1. Why The Previous Mission Now Splits

The V645 learner-interface pivot produced three decisive results:

1. `Path A` local micro-sweep proved positive validation tail alpha is reachable.
2. `Path A` fresh retrain plus fresh holdouts proved the economic signal survives into real future shards:
   - `2025` tail alpha is now positive
   - `2026-01` decile alpha is also positive
3. `Path B` was compared locally and remained weaker than `Path A`.

So the repo no longer needs a generic “Path A or Path B?” mission.

It now needs a narrower mission:

- refine the leading `Path A` branch
- keep `Path B` frozen as a comparison branch
- keep GC paused until the local branch is stronger

## 2. New Canonical Diagnosis

The main remaining defect is now narrower than the original audit claim.

Current leading-branch problem:

- `Path A` materially improved economic ranking
- but `2026-01` `alpha_top_quintile` is still negative
- and holdout `AUC` collapsed from the old high-`AUC` regime toward near coin-flip

So the next mission is not to rediscover magnitude awareness.

It is to refine the **Path A tradeoff surface**:

- preserve the economic gains
- reduce the remaining `2026-01` weakness
- avoid drifting too far into a classifier that has no useful ranking stability

## 3. Mission Objective

Run a bounded AgentOS refinement mission inside the `Path A` family only.

Hard boundaries:

- keep `omega_core/*` frozen
- keep `canonical_v64_1` Stage3 gates frozen
- keep the frozen old holdout baseline immutable
- keep the fresh `Path A` holdout outputs immutable
- keep the fresh `Path B` compare outputs immutable
- do not widen back into GC before the refined `Path A` branch earns it

## 4. Allowed Refinement Family

This mission is restricted to the `Path A` learner family:

- learner objective remains:
  - `binary:logistic`
- label remains:
  - `label = (t1_excess_return > 0)`
- magnitude remains injected through training interface refinements only

Allowed refinement directions:

- weight-shaping changes inside the `Path A` family
- local ranking-objective refinements that do not reopen `Path B`
- near-null or selective guardrail refinements if AgentOS proves they improve the compare
- retrain / holdout promotion only after a stronger local `Path A` candidate exists

This mission must not:

- reopen `Path B` as the leading branch
- reopen math-governance
- move raw L2 or Stage3 forging back into scope
- widen to GCP by default

## 5. Required Runtime Shape

The next live work under this mission must remain:

- local-first
- fresh-prefix isolated
- micro-sweep / bounded compare before any new holdout rerun

Default commander bias:

- local micro-sweep first
- then local fresh retrain
- then dual-host holdout only if the refined local `Path A` candidate clearly beats the current `Path A` reference

## 6. What Success Looks Like

The next success gate is stricter than V645:

- beat the current local `Path A` reference on validation tail alpha
- without immediately collapsing into a weaker overall ranking regime than the current branch

Only after that should the mission consider:

- fresh retrain
- fresh `2025` / `2026-01` holdout rerun

## 7. Reference Baselines That Must Stay Frozen

Frozen old holdout baseline:

- `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`

Frozen current leading `Path A` branch:

- `handover/ai-direct/entries/20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass.md`

Frozen local `Path B` compare:

- `handover/ai-direct/entries/20260309_090713_v645_path_b_local_compare_weaker_than_path_a.md`

Any new run must append evidence under fresh runtime roots.
