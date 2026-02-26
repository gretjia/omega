# Stage2 A/B Benchmark Blocked: Linux SSH Banner Timeout

Date: 2026-02-25 21:35 +0800

## Goal
Run A/B benchmark on Linux for Stage2 runner change:
- baseline: `tools/stage2_targeted_resume.py` (single-file subprocess)
- candidate: `tools/stage2_targeted_resume_try2.py` (multi-file subprocess)

## Actions Completed
- Created branch-side implementation locally (`files-per-process` batching and marker-safe timeout handling).
- Copied candidate runner to Linux as `tools/stage2_targeted_resume_try2.py` (non-destructive, no replacement).
- Stopped active Linux Stage2/autopilot units to avoid benchmark interference.
- Prepared benchmark workspace and input subset under:
  - `/home/zepher/work/Omega_vNext/audit/bench_stage2_try2_20260225_211640`

## Blocker Observed
Linux host became SSH-unusable during benchmark attempts:
- ICMP ping to `192.168.3.113` remains healthy (0% loss, ~1ms RTT).
- TCP 22 is open (`nc -vz` succeeds).
- SSH handshake fails repeatedly with:
  - `Connection timed out during banner exchange`

This indicates host-side SSH daemon/session starvation (service reachable but not sending SSH banner), consistent with prior Linux instability pattern.

## Current Impact
- Cannot collect benchmark completion metrics yet.
- Cannot safely relaunch Stage2 on Linux until SSH recovers.
- Windows node remains reachable and normal.

## Immediate Recovery Plan
1. Recover Linux shell access (local console or reboot).
2. Verify sshd responsiveness (`ssh localhost` on Linux).
3. Re-run A/B benchmark from prepared bench dir:
   - baseline old runner
   - candidate new runner with `--files-per-process 8`
4. Record throughput delta (`files/hour`, fail count) and decide cutover.
