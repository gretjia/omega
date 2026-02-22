# Handover: v60 Auto-Resume + Context Memory Protocol
**Date:** 2026-02-17
**Status:** ACTIVE

## 1. Goal
Keep the v60 pipeline unattended-safe: incident detection -> AI debug -> automatic resume -> persistent handover memory.

## 2. Runtime Sources of Truth
1. `audit/runtime/v52/autopilot_<hash>.status.json`: stage and per-stage status.
2. `audit/runtime/v52/autopilot_<hash>.runner.log`: full stdout/stderr of autopilot process.
3. `audit/runtime/v52/incidents/`: incident snapshots and Codex debug reports.

## 3. Handover Memory (Agent Handoff)
1. Live JSON snapshot (polled heartbeat):
   - `handover/ai-direct/live/v60_run_<hash>.json`
2. Event stream (append-only):
   - `handover/ai-direct/live/v60_events_<hash>.md`

Policy:
- Any automatic recovery action must be written to the event stream.
- Any agent takeover starts from live JSON, then reads the latest event entries.

## 4. Auto-Resume Behavior
Enabled in watchdog via `--auto-resume`:
1. If `autopilot` process disappears before completion, watchdog relaunches detached screen session `v60_autopilot_<hash>` after grace/cooldown checks.
2. If uplink loop disappears during frame/upload stages, watchdog relaunches detached screen session `v60_uplink_<hash>`.
3. On incident signatures (traceback/stall/status stale), watchdog captures snapshot and can trigger `codex exec` for autonomous debug.

## 5. Safety Constraints
1. Do not alter v6 math logic/principles (`audit/v6.md`).
2. Keep fixes operational (process recovery, cloud/runtime robustness), not model-physics changes.
3. Preserve reproducibility: keep hash-pinned artifacts and explicit logs.

## 6. Takeover Quick Checklist
1. Check `handover/ai-direct/live/v60_run_<hash>.json`.
2. Check latest entries in `handover/ai-direct/live/v60_events_<hash>.md`.
3. Verify screen sessions (`v60_autopilot_<hash>`, `v60_uplink_<hash>`, `v60_ai_watchdog_<hash>`).
4. Confirm frame and GCS parquet counts continue moving.
