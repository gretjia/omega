# Skill Library Governance (Less Is More)

Updated: 2026-02-07

## Objective

Preserve model intelligence and execution speed by minimizing always-on skill load.

## Always-On Core (6)

1. `.agent/skills/math_core/SKILL.md`
2. `.agent/skills/physics/SKILL.md`
3. `.agent/skills/engineering/SKILL.md`
4. `.agent/skills/v3_mainline_guard/SKILL.md`
5. `.agent/skills/hardcode_guard/SKILL.md`
6. `.agent/skills/ops/SKILL.md`

## On-Demand Skills

- `.agent/skills/config_promotion_protocol/SKILL.md`
- `.agent/skills/innovation_sandbox/SKILL.md`
- `.agent/skills/multi_agent_rule_sync/SKILL.md`
- `.agent/skills/math_consistency/SKILL.md`
- `.agent/skills/data_integrity_guard/SKILL.md`
- `.agent/skills/evidence_based_reasoning/SKILL.md`
- `.agent/skills/evolution_knowledge/SKILL.md`
- `.agent/skills/qmtsdk/SKILL.md`
- `.agent/skills/rqsdk/SKILL.md`
- `.agent/skills/ai_handover/SKILL.md`
- `.agent/skills/omega_data/SKILL.md`
- `.agent/skills/omega_development/SKILL.md`
- `.agent/skills/parallel-backtest-debugger/SKILL.md`
- `.agent/skills/pipeline_performance/SKILL.md`

## Compatibility Shims (Deprecated, Keep for Trigger Backward-Compat)

- `.agent/skills/data_download/SKILL.md` (merged into `qmtsdk` / `rqsdk`)
- `.agent/skills/omega_engineering/SKILL.md` (merged into `omega_development`)

## Merge / Archive Candidates

- Completed: `data_download` -> `qmtsdk` / `rqsdk` (2026-02-07)
- Completed: `omega_engineering` -> `omega_development` (2026-02-07)
- Archive candidate (low-frequency): `omega_data` after merging data path notes into `qmtsdk` / `rqsdk`

## Governance Rules

1. One-in-one-out: adding one always-on skill requires removing one.
2. 30-day inactivity review: no trigger for 30 days -> archive candidate.
3. Process-heavy skills default to on-demand, not always-on.
