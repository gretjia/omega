---
name: multi-agent-ops
description: Deploy and operate version-agnostic Omega multi-agent collaboration (Codex xhigh orchestration/planning, Gemini Flash implementation, Codex medium debug-scribe memory, Gemini Pro + Codex xhigh dual recursive auditors), with stable paths, governance drift checks, recursive-audit prompts, and hot-switch model profiles.
---

# Multi-Agent Ops

## When to use
- User asks to deploy/check multi-agent setup.
- User asks to switch active models (Gemini Pro/Flash, Codex xhigh/medium, etc.).
- User asks to capture debug lessons for cross-agent learning in `handover/`.
- User asks for dual recursive audit (Gemini + Codex independent).
- Governance drift must be repaired (`AGENTS.md`, principles path mismatch, handoff contract files).

## Workflow
0. Constitution preflight (mandatory before any task):
```bash
sed -n '1,120p' audit/constitution_v2.md
```

1. Deploy + repair + check:
```bash
python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair
```
Default behavior: auto-appends a deduplicated debug lesson into `handover/DEBUG_LESSONS.md`
when `handover/ai-direct/live/` contains a real task context.
Also auto-builds read-only memory indexes under `handover/index/` and generates
`handover/ai-direct/live/00_Lesson_Recall.md` (Top-K lesson recall before task execution).
Emergency bypass:
```bash
python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --repair --no-auto-debug-scribe
```
Optional memory bypass:
```bash
python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --no-memory-recall
```
Tune recall depth:
```bash
python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py --memory-top-k 8
```

2. Switch active profiles if needed:
```bash
python3 .codex/skills/multi-agent-ops/scripts/switch_profile.py \
  --oracle codex_xhigh \
  --mechanic gemini_flash \
  --auditor-primary gemini_pro \
  --auditor-secondary codex_xhigh \
  --debug-scribe codex_medium
```

3. Optional manual debug lesson (only if you need to override auto-generated content):
```bash
python3 .codex/skills/multi-agent-ops/scripts/log_debug_experience.py \
  --title "example_issue" \
  --task-id "TASK-000" \
  --git-hash "abc1234" \
  --symptom "what failed" \
  --root-cause "why it failed" \
  --fix "what changed" \
  --guardrail "how we prevent recurrence" \
  --refs "path/to/file.py,python3 tools/example.py --smoke"
```

4. Run independent recursive audits:
```bash
cat audit/runtime/multi_agent/recursive_audit_prompts.md handover/ai-direct/live/01_Raw_Context.md handover/ai-direct/live/03_Mechanic_Patch.md | \
  gemini -m gemini-3-pro --approval-mode plan --output-format text \
  -p "Run independent recursive audit. Do not read other auditor outputs." \
  > handover/ai-direct/live/04A_Gemini_Recursive_Audit.md

cat audit/runtime/multi_agent/recursive_audit_prompts.md handover/ai-direct/live/01_Raw_Context.md handover/ai-direct/live/03_Mechanic_Patch.md | \
  codex exec -C . -m gpt-5.3-codex -c model_reasoning_effort="xhigh" -s read-only \
  -o handover/ai-direct/live/04B_Codex_Recursive_Audit.md -
```

5. Re-check:
```bash
python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py
```

## Outputs
- Validates:
  - `audit/constitution_v2.md` (immutable highest-priority constitution)
  - `audit/multi_agents.md` (canonical stable design)
  - `audit/v60_multi_agents.md` (guiding-principle baseline)
  - `audit/runtime/multi_agent/agent_profiles.yaml`
  - `audit/runtime/multi_agent/recursive_audit_prompts.md`
  - `AGENTS.md`
  - `.agent/principles.yaml`
  - `handover/DEBUG_LESSONS.md`
  - `handover/ai-direct/live/01..05_*.md`
  - `handover/index/memory_index.jsonl`
  - `handover/index/memory_index.sqlite3`
  - `handover/ai-direct/live/00_Lesson_Recall.md`

## Boundaries
- Does not auto-commit.
- Does not auto-merge.
- Does not replace existing runtime orchestrator/autopilot.
