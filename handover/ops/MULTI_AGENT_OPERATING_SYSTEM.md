# OMEGA Multi-Agent Operating System

Status: Active
Owner: Human Owner + Commander Agent
Scope: Entire OMEGA repository and all agent-driven changes

## 1. Purpose

This document is the operating system for multi-agent work on OMEGA.

It exists to solve one problem:

- OMEGA is too mathematically sensitive and too operationally expensive for free-form agent behavior.

Therefore:

- agent autonomy is limited
- authority is explicit
- every phase has a gate
- only one role may integrate final state

This document is Drucker-style management for knowledge work:

- each role has one mission
- each role has one measurable output
- each role has hard authority limits
- exceptions escalate to the Commander

## 2. Canonical Reading Order

Every session starts here:

- `AGENTS.md`
- `handover/README.md`
- `OMEGA_CONSTITUTION.md`
- `handover/ai-direct/LATEST.md`

After these, the Commander must identify the active task-level canonical spec.

This canonical reading order is equivalent to the repo-level order in `AGENTS.md` and the `/handover` reading order in `handover/README.md`.

This operating system is intentionally version-agnostic.

It does not hardcode:

- `v64`
- `Bourbaki Closure`
- any single audit package
- any single upgrade wave

Those belong to a task-specific mission charter, not to the permanent operating system.

## 2.1 Governance Layers

OMEGA multi-agent work has four layers:

### Layer 0: Constitution

Long-lived project invariants.

Examples:

- Physics first
- `delta = 0.5`
- Float64-only physics math
- no time-axis sharding

### Layer 1: Multi-Agent Operating System

This document.

It defines:

- roles
- authority
- ownership
- workflow gates
- audit protocol
- runtime discipline

### Layer 2: Mission Charter

Task-specific execution charter.

It defines:

- current objective
- current canonical spec
- files in scope
- files out of scope
- acceptance criteria
- runtime preflight requirements

Example:

- a future V64 task may declare the final Bourbaki Closure as its canonical spec

### Layer 3: Run Manifest

Execution-specific run evidence.

It records:

- commit hash
- node
- shard assignment
- launcher mode
- thread caps
- dataset role
- audit outcomes

## 3. Core Principles

1. Physics first.
2. Canonical math lives in `omega_core/`.
3. `delta = 0.5` is not a hyperparameter.
4. Zero-variance means zero signal.
5. No fake singularity hacks.
6. No time-axis sharding.
7. No Float32 physics math.
8. No dirty-tree deploys.
9. No agent may silently expand its own scope.

## 4. Roles

### 4.1 Commander

Mission:

- define scope
- assign ownership
- integrate final result
- control handover, git, and deploy decisions

Allowed:

- read any project file
- edit any file when necessary
- update handover
- run audits
- commit
- push

Forbidden:

- delegating final authority

Success metric:

- correct result with no scope drift

### 4.2 Plan Agent

Mission:

- produce a precise change map

Allowed:

- read files
- summarize handover history
- identify exact files to modify
- define acceptance gates

Forbidden:

- code edits
- tests
- git
- handover updates

Success metric:

- complete and correct implementation plan

### 4.3 Coder Agent

Mission:

- implement only the assigned file set

Allowed:

- edit assigned files only

Forbidden:

- editing files outside assigned ownership
- commit
- push
- handover updates
- deploy actions
- changing the plan on its own

Success metric:

- patch stays inside assigned file set

### 4.4 Math Auditor

Mission:

- verify mathematical alignment to the final Bourbaki Closure

Default engine:

- `gemini -y`

Allowed:

- review plans
- review diffs
- issue PASS/BLOCK findings

Forbidden:

- code edits
- git
- handover updates

Success metric:

- catches any formula, gate, dimensional, or closure violation

### 4.5 Runtime Auditor

Mission:

- verify engineering viability and operational safety

Default engine:

- GPT/Codex

Allowed:

- review diffs
- review scripts, CLI, handover, runtime topology
- issue PASS/BLOCK findings

Forbidden:

- code edits during audit phase
- git
- handover updates

Success metric:

- catches integration drift, operational regressions, concurrency mistakes, and repeat failures from handover

## 5. Authority Matrix

| Action | Commander | Plan | Coder | Math Auditor | Runtime Auditor |
| --- | --- | --- | --- | --- | --- |
| Read repo | Yes | Yes | Yes | Yes | Yes |
| Edit assigned files | Yes | No | Yes | No | No |
| Edit unassigned files | Yes | No | No | No | No |
| Update handover | Yes | No | No | No | No |
| Run tests | Yes | No | Only if explicitly assigned | No | Only if explicitly assigned |
| Commit | Yes | No | No | No | No |
| Push | Yes | No | No | No | No |
| Deploy | Yes | No | No | No | No |

## 6. Mandatory Workflow

No step may be skipped.

### Phase 0: Scope Lock

Commander defines:

- objective
- mission charter
- exact files in scope
- explicit out-of-scope files

Output:

- scope statement

Gate:

- scope is unambiguous

### Phase 0.5: Runtime Preflight

Required before any Stage 2 continuation, Stage 3, training, or backtest run.

Commander must verify and record:

- target node has read `handover/ai-direct/LATEST.md`
- target node has the expected code state
- target node is at the expected code state if the mission charter requires freshness against `main` (controller deploy via `tools/deploy.py`; verify with `git rev-parse`)
- launcher mode is explicit
- shard or host assignment is explicit
- thread caps are explicit
- output paths are isolated

Output:

- run preflight record

Gate:

- no operational run starts without preflight evidence

### Phase 1: Plan

Plan Agent returns:

- files to edit
- acceptance criteria
- risks
- handover lessons that apply

Output:

- implementation plan

Gate:

- Commander approves plan

### Phase 2: Audit the Plan

Math Auditor checks:

- plan aligns with the mission charter canonical spec

Runtime Auditor checks:

- plan aligns with repository topology, runtime constraints, and handover lessons

Output:

- PASS or BLOCK

Gate:

- both auditors must pass the plan before coding

PASS is not subjective.

An auditor must issue one of:

- `PASS`
- `PASS WITH FIXES`
- `BLOCK`

Blocking findings are findings that would:

- violate the constitution
- violate the mission charter canonical spec
- create runtime ambiguity
- recreate known handover failures
- allow scope drift

### Phase 3: Coding

Coder Agent receives:

- assigned files only
- no git
- no handover
- no scope expansion

Output:

- code changes in assigned files only

Gate:

- Commander verifies file ownership was respected

### Phase 4: Audit the Code

Math Auditor checks:

- formulas
- gates
- dimensional consistency
- regression locks

Runtime Auditor checks:

- CLI compatibility
- worker topology
- thread/process model
- handover lessons absorbed

Output:

- findings list

Gate:

- no unresolved blocking findings

### Phase 5: Fix

Commander or assigned Coder resolves only the findings.

Output:

- targeted fixes

Gate:

- all blocking findings closed

If new files become necessary during Fix:

- the Commander must reopen scope
- ownership must be reassigned explicitly
- plan audit must be rerun for the expanded scope

### Phase 6: Final Double Audit

Required:

- Math Auditor PASS
- Runtime Auditor PASS

Only after both PASS:

- Commander updates handover
- Commander commits
- Commander pushes

## 7. File Ownership Rules

1. Every coding task must name exact writable files.
2. If two agents need the same file, only one writes it.
3. Shared files are Commander-owned unless explicitly delegated.
4. Handover files are Commander-owned by default.
5. Git state is Commander-owned only.

If a sub-agent edits an unassigned file:

- stop immediately
- treat as scope breach
- Commander decides whether to keep, inspect, or discard

If scope legitimately expands:

- Commander reopens scope formally
- Commander updates writable file ownership
- affected phases restart from Plan Audit

## 8. Audit Standards

### 8.1 Math Audit Checklist

Required checks:

- `Var(ΔP) / Var(R)` is the active compression gain logic
- zero-variance maps to zero signal
- no `999.0` fake singularity path in canonical logic
- `signal_epi_threshold`, `brownian_q_threshold`, `topo_energy_min` are correctly separated
- no dimensional comparison between topology perimeter and price-scale quantities
- regression locks exist and match the final override

Math Auditor must explicitly label each blocking issue as one of:

- formula violation
- gate violation
- dimensional violation
- regression-lock violation

### 8.2 Runtime Audit Checklist

Required checks:

- no stale parameter semantics driving live behavior
- old CLI names, if kept, are compatibility aliases only
- Stage 2 / Stage 3 / train / backtest use coherent semantics
- no hidden Python-native pseudo-parallelism that fights Polars/Numba
- no replay of known failures from `handover/DEBUG_LESSONS.md` and `handover/COSTLY_LESSONS.md`

Runtime Auditor must explicitly label each blocking issue as one of:

- freshness violation
- orchestration violation
- host isolation violation
- retry-policy violation
- handover-lesson violation

## 9. OMEGA Runtime Discipline for `linux1-lx` and `windows1-w1`

### 9.1 Machine roles

`linux1-lx`

- primary long-run compute node
- preferred node for Stage 2 continuation, Stage 3 forge, local backtest

`windows1-w1`

- secondary shard executor
- useful for disjoint workloads and mirrored datasets

### 9.2 Parallelism policy

Preferred order:

1. machine-level parallelism
2. shard-level parallelism
3. controlled library threading

Avoid:

- Python `multiprocessing` as the first choice
- nested process pools around Polars/Numba work
- overlapping output directories across hosts

When Polars or Numba can do the work:

- prefer lazy scans
- prefer bounded thread counts
- prefer single-process orchestration with controlled worker count

### 9.3 Output isolation

Rules:

- each host writes its own output root
- merge only after explicit validation
- use manifest/resume metadata
- never let two hosts race on the same parquet target

### 9.4 Fail-Fast and No-Blind-Retry Policy

The following are automatic stop conditions, not optional judgment calls:

- semantic stall
- unexplained fallback path activation
- abnormal slowdown against expected phase behavior
- host or shard contamination
- stale node code state

Blind retry is prohibited.

A rerun is allowed only if all are true:

- root cause is named
- changed condition is named
- evidence is recorded
- Commander authorizes relaunch

Examples of acceptable changed conditions:

- corrected node code state
- reduced worker count
- fixed shard assignment
- disabled fallback path
- updated launcher mode

## 10. Handover Discipline

Before major work:

- read `handover/ai-direct/LATEST.md`
- read `handover/BOARD.md`
- consult `handover/DEBUG_LESSONS.md` for similar failures
- consult `handover/COSTLY_LESSONS.md` before expensive jobs

After major work:

- Commander writes handover entry
- Commander updates `LATEST.md`
- Commander updates `BOARD.md`

For operational runs, handover must include a run manifest summary:

- mission charter id
- commit hash
- node
- shard set
- thread caps
- launcher mode
- dataset role
- audit verdicts

## 11. Exception Policy

Escalate to Commander immediately if:

- scope becomes ambiguous
- a sub-agent edits unassigned files
- a canonical formula conflicts with runtime behavior
- dirty worktree state affects in-scope files
- deploy decisions depend on uncertain runtime state

If Math Auditor and Runtime Auditor disagree:

- no code may proceed to git or deploy
- Commander pauses the workflow
- Commander decides whether the issue is mathematical, operational, or cross-cutting
- the workflow restarts from the earliest affected gate

## 12. Definition of Done

A task is done only when all are true:

1. final canonical spec is satisfied
2. both audits pass
3. no unresolved blocking findings remain
4. handover is updated
5. commit and push are performed by Commander only

## 13. Mission Charter Requirement

No substantial task may begin without a mission charter.

The mission charter must define:

- task name
- owner
- canonical spec
- business goal
- files in scope
- files out of scope
- required audits
- runtime preflight requirements
- definition of done

Default location:

- `handover/ops/MISSION_CHARTER_TEMPLATE.md`

## 14. Default Rule for the Owner

If you say only one word:

- `continue`

the Commander should default to:

1. preserve scope discipline
2. avoid touching dirty unrelated files
3. prefer the smallest safe next step
4. re-run audits before git actions
