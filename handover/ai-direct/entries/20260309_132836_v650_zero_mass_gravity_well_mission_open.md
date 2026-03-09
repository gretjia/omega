---
entry_id: 20260309_132836_v650_zero_mass_gravity_well_mission_open
task_id: TASK-V650-ZERO-MASS-GRAVITY-WELL
timestamp_local: 2026-03-09 13:28:36 +0000
timestamp_utc: 2026-03-09 13:28:36 +0000
operator: Codex
role: commander
branch: main
status: in_progress
---

# V650 Mission Open: Robust-Loss Escape From The Zero-Mass Gravity Well

## 1. Authority

This mission is now active under:

- `audit/v650_zero_mass_gravity_well.md`
- `handover/ai-direct/entries/20260309_131310_v650_zero_mass_gravity_well_spec_draft.md`
- `handover/ai-direct/entries/20260309_131707_v650_spec_draft_gemini_pass.md`

## 2. Owner Confirmation

Owner confirmed execution of V650.

## 3. Execution Shape

Wave 1 remains strictly:

- Path B only
- local-only
- sweep-only
- no GCP
- no holdouts
- no target transformation

## 4. Frozen Constraints

Still frozen:

- `omega_core/*`
- `canonical_v64_1` Stage3 gates
- raw `t1_excess_return` label
- `2023 -> 2024` split
- `2025` / `2026-01` holdout isolation
- `weight_mode=none`

## 5. First Wave Goal

Test whether:

- `reg:pseudohubererror`
- plus an explicit non-degeneracy gate

can produce a non-collapsed local Path B candidate that exceeds the V650 continuation gate.
