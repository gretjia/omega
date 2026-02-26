# Handover: omega-vm -> windows1-w1 Intermittent Reachability RCA + Fix

- Timestamp: 2026-02-24 04:16 +0800 (2026-02-23 20:16 +0000)
- Operator: Codex (on omega-vm)
- Scope: Tailnet transport stability and false-positive DOWN diagnosis correction

## 1) Problem
A prior status note marked `windows1-w1` as `CRITICAL / DOWN` based on a single failed window (`tailscale ping` timeout + SSH timeout from `omega-vm`).

## 2) Root Cause (Validated)
This was not a confirmed OS crash. It was an intermittent tailnet path idle/rebuild window:
- During failure window: `omega-vm -> windows1-w1` probes timed out.
- At same time, Windows local state remained healthy (`tailscale` and `sshd` running; port 22 listening).
- Cross-checks showed asymmetry: `windows -> omega` and `linux -> windows` worked while `omega -> windows` briefly failed.
- Later probes recovered without reboot.

Conclusion: classify as **intermittent transport reachability**, not immediate host-dead.

## 3) Landed Fixes

### A. Windows keepalive task (reduce idle path decay)
- Script path: `C:\Omega_vNext\tools\windows_tailscale_keepalive.ps1`
- Scheduled task: `Omega_Tailscale_Keepalive`
- Runtime model: long-running loop (`120s` interval), pinging:
  - `10.88.0.1` (omega-vm via WireGuard)
  - `100.64.97.113` (linux1-lx)
- Current state: task `Running`

### B. omega-vm retry-based probe (prevent false CRITICAL)
- Script added: `tools/check_windows_from_omega.sh`
- Logic: 5 attempts with delay; evaluate 3 independent signals each round:
  1. `tailscale ping`
  2. `TCP/22` connect test
  3. `ssh` handshake (`BatchMode`)
- Exit policy:
  - `0`: `REACHABLE_OR_RECOVERING`
  - `2`: `UNREACHABLE_AFTER_RETRIES`

## 4) Verification Evidence
- Repeated omega->windows probe: 5/5 rounds `PING_OK` + `TCP22_OK`
- `tools/check_windows_from_omega.sh` output: `RESULT=REACHABLE_OR_RECOVERING`
- Windows task status:
  - `Omega_Tailscale_Keepalive`: `Running`
- Current Stage1 snapshot:
  - Linux: `DONE=426`, service active
  - Windows: `DONE=191`, `Omega_v62_stage1_win` in `Ready` (stage complete for shard)

## 5) Operational Rule Update
Do not mark Windows as `CRITICAL / DOWN` from a single timeout sample.
Use retry window + multi-signal probe first. Escalate only after repeated failures.
