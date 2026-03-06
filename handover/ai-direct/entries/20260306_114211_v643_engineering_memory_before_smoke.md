# Entry ID: 20260306_114211_v643_engineering_memory_before_smoke

## Summary

- This entry captures the engineering lessons learned during the V64.3 Bourbaki Completion mission before the final full smoke run.
- The main value is operational: these lessons should become durable memory for future agents, not just narrative context for this one patch set.

## Canonical scope

- Task-level spec: `audit/v643.md`
- Final architect authority: latest `[ SYSTEM ARCHITECT FINAL OVERRIDE: THE BOURBAKI COMPLETION ]`
- Mission mode: dual-audit closure first, then full smoke, then `commit + push`; no new full Stage 2 launch after smoke

## Fixed engineering memory

### 1. Spec confirmation is a hard gate, not etiquette

- A new task-level override must not move into coding or audit until the Owner explicitly confirms the mission spec.
- If the Commander starts patching before spec confirmation, execution must freeze and the patch must be treated as draft-only until the Owner confirms the canonical spec, workflow, and release gates.

### 2. README is a high-level governance surface owned by the Commander

- `README.md` and `omega_core/README.md` are not trailing documentation files.
- They are active semantic interfaces for humans, auditors, and future agents.
- Correct placement in the workflow:
  - first lock code/config/tests
  - then pass code audit
  - then Commander-normalize README
  - then run final double audit

### 3. Repo-wide semantic purges must cover literal surfaces, not only executable code

- A repo can still fail closure after the runtime logic is corrected if the prohibited term survives in docstrings, comments, or string-scan tests.
- In V64.3, the repo-wide purge of the old `delta_k` penalty only became audit-clean after the exact literal was removed from the legacy helper docstrings as well as the executable formula.

### 4. Controller and runtime node are different environments

- The controller workspace may have no local scientific stack (`numpy`, `polars`, `pytest`), so local validation can be impossible even when the patch is correct.
- Full validation must therefore be routed early to a prepared runtime node, with dependency installation made explicit instead of assumed.
- In this repo, the durable pattern is:
  - edit/govern on controller
  - sync draft tree to a dedicated remote smoke workspace
  - run validation there with `uv run`

### 5. Handover authority must move with the patch

- When the task-level canonical spec changes, `handover/ai-direct/LATEST.md` must immediately distinguish:
  - the current active mission
  - historical smoke evidence from the previous version
- A prior smoke pass is not release evidence for a newer semantic patch set unless `LATEST.md` explicitly says it still applies.

### 6. Fresh auditors beat stale cached verdicts

- If one audit thread latches onto an old conclusion, do not wait indefinitely for it to self-correct.
- Start a fresh read-only audit thread or external audit, and compare against the current tree state.
- Audit freshness is more important than agent continuity.

## Immediate operational implication

- Before the V64.3 smoke starts, future agents should already know:
  - the spec is confirmed
  - README is Commander-owned
  - repo-wide purges include literal surfaces
  - runtime validation belongs on prepared nodes
  - `LATEST.md` must reflect versioned authority in real time

## Release note

- This memory entry is written before the final V64.3 smoke run and before release.
- It should be read as durable engineering guidance, not as evidence that V64.3 smoke has already passed.
