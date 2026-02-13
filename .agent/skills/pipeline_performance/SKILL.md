---
name: pipeline_performance
description: Top-level design guidance for this skill domain.
---

# Skill: pipeline_performance

## Intent
Top-level design guidance for this skill domain.

## When To Use
- Use when the task clearly falls into this skill domain.
- Prioritize this skill over ad-hoc instructions in the same domain.
- Combine with other skills only when responsibilities are non-overlapping.

## Core Principles
- Keep the guidance abstract and reusable across versions, environments, and machines.
- Prefer safe, incremental, and verifiable execution.
- Separate policy decisions from implementation details.
- Preserve consistency with project-wide governance and audit expectations.

## Standard Workflow
1. Clarify task objective, constraints, and acceptance criteria.
2. Assess current state and identify key risks.
3. Choose the minimum viable approach for forward progress.
4. Execute changes in small steps and validate outcomes.
5. Summarize decisions, evidence, and follow-up actions.

## Expected Output
- A concise decision summary with assumptions.
- A traceable list of actions taken and validation results.
- Explicit risks, tradeoffs, and next-step recommendations.

## Boundaries
- Do not hardcode version-specific paths, one-off commands, or runtime-local artifacts in this top-level skill file.
- Put implementation details in task-specific docs/scripts, not in the skill definition.
