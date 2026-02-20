# AGENTS.md (Omega_vNext)

## Scope
Applies to the full repository at `/Users/zephryj/work/Omega_vNext`.

## Priority Sources
1. `audit/constitution_v2.md` (immutable, highest authority)
2. `audit/multi_agents.md` (canonical multi-agent governance)
3. `audit/runtime/multi_agent/agent_profiles.yaml` (runtime profile source)
4. `.codex/skills/*/SKILL.md` (executable workflows)
5. `.agent/principles.yaml` (cross-agent rule source)

## Agent Role Policy (Stable)
- Oracle/Planner/Orchestrator: Codex 5.3 xhigh (read only)
- Mechanic/Implementer: Gemini 3 Flash (writer by default)
- Debug Scribe/Lesson Writer: Codex 5.3 medium (writes to `handover/DEBUG_LESSONS.md`)
- Recursive Auditor A: Gemini CLI (read only, independent from B)
- Recursive Auditor B: Codex 5.3 xhigh in read-only mode (independent from A)
- Human: final dispatcher and final merge owner

## Skill Routing
- Use `.codex/skills/multi-agent-ops/SKILL.md` for:
  - multi-agent deployment checks
  - model profile switching
  - governance drift repair
- Use `.codex/skills/omega-run-ops/SKILL.md` for distributed framing/upload/watchdog operations.

## Important Clarification
- `.agent/skills/*` are mostly policy templates in this repository.
- Executable operations should prefer `.codex/skills/*` scripts and workflows.
- Historical compatibility documents may retain versioned filenames, but they are not primary decision anchors.

## Hard Rules
- Before any planning/implementation/audit task, every agent must read `audit/constitution_v2.md` once.
- `audit/constitution_v2.md` is immutable in normal task flow; agents must not modify it.
- Do not auto-merge code across multiple agent CLIs.
- Keep handoff through `handover/ai-direct/live/01..05_*.md`.
- `deploy_and_check.py` must auto-maintain anti-regression debug memory in `handover/DEBUG_LESSONS.md` (manual append is override-only).
- Log model/profile switches in `handover/ai-direct/LATEST.md`.
- Default control policy: `oracle=codex_xhigh`, `mechanic=gemini_flash`, `auditor_primary=gemini_pro`, `auditor_secondary=codex_xhigh`, `debug_scribe=codex_medium`.
