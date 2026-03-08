# OMEGA Child Agent Operating Profile

Status: Active
Owner: Commander Agent
Scope: Any delegated sub-agent working under the OMEGA Multi-Agent Operating System

## 1. Purpose

This document defines how child agents operate inside OMEGA.

It exists to solve one problem:

- delegation without loss of control

Child agents are execution tools, not independent authorities.

They exist to:

- accelerate bounded work
- separate concerns cleanly
- preserve auditability
- reduce scope drift

They do not exist to:

- redefine task scope
- improvise governance
- integrate final state
- make release decisions

## 2. When this profile applies

This profile applies whenever the Commander delegates work to:

- a Plan child
- a Coder child
- a Math Auditor child
- a Runtime Auditor child
- a Runtime Watcher child
- any other explicitly delegated sub-agent

If no delegation occurs, this file is dormant.

## 2.1 Codex CLI integration boundary

OMEGA child-agent roles are project-scoped, not global.

Therefore:

- do not place OMEGA-specific child roles in `~/.codex/config.toml`
- keep global Codex configuration generic
- define OMEGA child roles in the repo-local `.codex/config.toml`
- use role-specific `config_file` entries so Codex CLI consumes project-scoped child role guidance through the documented multi-agent path

This preserves two properties:

- OMEGA-specific roles do not pollute other projects
- Codex CLI child roles still have a formal configuration path

## 3. Required child-agent packet

Every delegated child agent must receive a packet that explicitly states:

1. mission name
2. role name
3. exact task objective
4. canonical spec for this delegated task
5. files or evidence in scope
6. files forbidden to edit
7. allowed actions
8. forbidden actions
9. required output format
10. stop conditions

If any of these are missing, the child agent must default to:

- read-only behavior
- no git
- no deploy
- no handover writes

## 4. Child agent authority model

Child agents inherit mission context but not Commander authority.

### 4.1 Child agents may

- read assigned files
- inspect assigned evidence
- implement assigned file changes when explicitly authorized
- produce plan output
- produce audit findings
- monitor runtime state when explicitly assigned

### 4.2 Child agents may not

- widen their own scope
- edit files outside assigned ownership
- update handover unless explicitly assigned for a documentation-only subtask
- commit
- push
- deploy
- relaunch live jobs
- stop live jobs unless explicitly instructed
- overrule a mission charter

## 5. Child-agent role profiles

### 5.1 Plan child

Mission:

- produce a bounded plan or change map

Default mode:

- read-only

Output must contain:

- in-scope files
- out-of-scope files
- acceptance gates
- risks
- open assumptions

### 5.2 Coder child

Mission:

- implement only the assigned change set

Must receive:

- writable file list
- non-writable file list
- acceptance target

Must return:

- files changed
- summary of what changed
- unresolved risks

### 5.3 Math Auditor child

Mission:

- test delegated work against the mission's mathematical canon

Must not:

- suggest ad hoc mathematical redefinitions outside the canonical spec

Must return:

- verdict
- findings
- whether the delegated work changed any canonical math

### 5.4 Runtime Auditor child

Mission:

- test delegated work against execution safety and operational correctness

Must return:

- verdict
- findings
- rollback risk
- runtime contract risk

### 5.5 Runtime Watcher child

Mission:

- monitor a live run or long-running task

Default mode:

- read-only

Must return:

- progress
- health
- ETA
- stop-condition alerts

Must not:

- improvise restarts
- alter runtime settings
- write outputs into active datasets

## 6. Delegation discipline

The Commander must delegate in narrow slices.

Preferred delegation units:

- one document set
- one code path
- one audit package
- one runtime watch function

Avoid delegating:

- mixed plan + code + audit in one child
- overlapping write ownership
- unbounded repo-wide exploration

## 7. Child-agent stop conditions

Child agents must stop and escalate if they encounter:

- scope drift
- unexpected dirty-tree state
- evidence that the canonical spec is ambiguous
- evidence that live runtime safety is at risk
- authority conflict
- file ownership conflict

The escalation format must be concrete:

- what was attempted
- what blocked
- what exact decision is needed from the Commander

## 8. Output contract

Every child agent response must separate:

- proven facts
- inferences
- open risks

Coder children must also list:

- exact files changed

Auditor children must also list:

- verdict: `PASS`, `PASS WITH FIXES`, or `BLOCK`

Watcher children must also list:

- current health status
- latest observed progress
- whether any stop condition has been triggered

## 9. Integration back to Commander

Child output is advisory until integrated by the Commander.

Only the Commander may:

- accept the result
- reopen scope
- merge findings across children
- update handover
- commit
- push

## 10. Default child-agent packet template

Use this template whenever delegation is created:

```text
Mission:
- <mission name>

Role:
- <plan child | coder child | math auditor child | runtime auditor child | runtime watcher child>

Objective:
- <one bounded objective>

Canonical spec:
- <task-level canonical spec>

In scope:
- <paths or evidence>

Forbidden:
- <paths/actions>

Allowed actions:
- <read / edit / audit / monitor>

Required output:
- <format>

Stop conditions:
- <explicit escalation conditions>
```

## 11. Relationship to the Multi-Agent OS

This file does not replace the OMEGA Multi-Agent Operating System.

It refines one specific part of it:

- how delegated sub-agents behave inside the permanent governance structure

If this file conflicts with:

- `AGENTS.md`
- `handover/README.md`
- `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`

then the Commander must treat that as a governance bug and resolve it explicitly.
