# OMEGA Mission Charter Template

Status: Draft
Task Name:
Owner:
Commander:
Date:

## 1. Objective

- What is the task?
- Why does it matter?

## 2. Canonical Spec

Primary task-level implementation authority:

- path:
- exact section or commit:

Supporting context:

- path:
- path:

If the canonical spec conflicts with `OMEGA_CONSTITUTION.md`, escalate to the Commander.

## 3. Scope

Writable files:

- path
- path

Read-only but relevant files:

- path
- path

Explicitly out of scope:

- path
- path

## 4. Roles

Plan Agent:

- responsibility:

Coder Agent:

- writable files only:

Math Auditor:

- audit target:

Runtime Auditor:

- audit target:

## 5. Acceptance Criteria

- criterion
- criterion
- criterion

## 6. Runtime Preflight

Required before execution:

- target node:
- expected commit or branch:
- controller-only code freshness requirement (if any):
- worker deploy path via `tools/deploy.py` (workers never `git pull`):
- launcher mode:
- shard assignment:
- thread caps:
- output root:
- host isolation check:

## 7. Fail-Fast Conditions

- stop condition
- stop condition
- retry allowed only after named root cause and changed condition

## 8. Audits Required

Math audit must verify:

- item
- item

Runtime audit must verify:

- item
- item

## 9. Definition of Done

- canonical spec satisfied
- audits passed
- no blocking findings remain
- handover updated
- Commander-only commit/push completed

## 10. Run Manifest

Record after execution:

- commit hash:
- node:
- shard set:
- thread caps:
- launcher mode:
- dataset role:
- math audit verdict:
- runtime audit verdict:
