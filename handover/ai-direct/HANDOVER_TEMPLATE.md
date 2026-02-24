# Handover Entry Template (Required)

Use this template for each new file in `handover/ai-direct/entries/`.

```markdown
---
entry_id: YYYYMMDD_HHMMSS_short_topic
task_id: TASK-XXXX
timestamp_local: YYYY-MM-DD HH:MM:SS +TZ
timestamp_utc: YYYY-MM-DD HH:MM:SS +0000
operator: <agent/human>
role: <oracle|mechanic|auditor|operator>
branch: <branch>
git_head: <short_hash>
hosts_touched: [omega-vm, linux1-lx, windows1-w1]
status: <in_progress|blocked|completed>
---

## 1. Objective

- What this session needed to achieve.

## 2. Scope

- What was in-scope.
- What was intentionally out-of-scope.

## 3. Actions Taken

- Ordered list of concrete actions and command groups.

## 4. Evidence

- Command outputs summary.
- Log files checked.
- Artifact counts/paths.

## 5. Risks / Open Issues

- Active risks.
- Known unknowns.

## 6. Changes Made

- Files changed.
- Key logic or behavior impact.

## 7. Next Actions (Exact)

1. Exact command or operation.
2. Exact command or operation.
3. Escalation condition if blocked.

## 8. LATEST.md Delta

- The exact lines or sections updated in `handover/ai-direct/LATEST.md`.
```

