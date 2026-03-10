---
entry_id: 20260310_013500_v654_identity_preserving_pulse_compression_mission_open
task_id: V654-IDENTITY-PRESERVING-PULSE-COMPRESSION
timestamp_local: 2026-03-10 01:35:00 +0000
timestamp_utc: 2026-03-10 01:35:00 +0000
operator: Codex
role: commander
branch: main
status: in_progress
---

# V654 Mission Open: Identity-Preserving Pulse Compression

## 1. Authority

This mission is now active under:

- `audit/v654_identity_preserving_pulse_compression.md`
- `handover/ai-direct/entries/20260310_012744_v654_identity_preserving_pulse_compression_spec_draft.md`
- `handover/ai-direct/entries/20260310_013420_v654_spec_draft_gemini_pass.md`

## 2. Owner Direction

Owner directed the commander to:

- land the new external execution-grade override under `audit/`
- let AgentOS follow it as closely as possible
- preserve truth-first execution while keeping ML closed until the pure event-study gate is earned

## 3. Execution Shape

Wave 1 remains:

- local-first
- forge-first
- event-study-first
- no ML
- no Vertex / GCP
- no holdout use

## 4. Single Allowed Change Axis

Change only:

- the `Intraday -> Symbol-Day` aggregation path in `tools/forge_campaign_state.py`

Frozen:

- daily spine
- tradable labels
- triple-barrier semantics
- event-study gate
- `omega_core/*` math core

## 5. First Wave Goal

Implement identity-preserving pulse compression so that:

- overlapping same-sign intraday echoes are compressed
- Epiplexity / Topology / SRL phase remain explicit through the daily fold
- new directional campaign-state families can be tested in the unchanged pure event-study gate
