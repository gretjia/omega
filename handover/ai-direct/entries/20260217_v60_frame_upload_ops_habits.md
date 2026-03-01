# Handover: v60 Framing + Uplink Engineering Habits
**Date:** 2026-02-17  
**Status:** ACTIVE RUN PLAYBOOK

## 1. Goal
Guarantee long-running v60 delivery (frame -> upload -> train -> backtest) without wasting frame compute or breaking v6 physics constraints.

## 2. Non-Negotiables
1. Keep architecture aligned to `audit/_archived/v6.md` at all times.
2. Do not modify mathematical logic for speed hacks.
3. Run smoke gate before expensive full framing.
4. Never trust PID files alone; verify by log + done-count movement.

## 3. Frame Hygiene (Hash-Scoped)
When old frame hashes remain (for example v52 artifacts), cleanup must be hash-safe:
- Keep only current hash triplet:
  - `*_<hash>.parquet`
  - `*_<hash>.parquet.done`
  - `*_<hash>.parquet.meta.json`
- Delete only files that match frame suffixes but not current hash.
- Validate before/after with hash distribution counts on both Linux and Windows.

Why:
- Prevents accidental deletion of new v60 frames.
- Removes ambiguity in downstream upload/train data selection.

## 4. Framing Throughput Policy
- Linux is materially faster than Windows for framing.
- Use shard ratio `windows:linux = 1:2` (~33% : ~67%).
- Generate shard manifests with:
  - `python3 tools/_archived/build_7z_shards.py --root /omega_pool/raw_7z_archives --ratio 1:2`

## 5. Uplink Policy (Frame While Uploading)
Use Mac as gateway with disk guardrails:
- Small batch sync (10-15 GB) to avoid local disk exhaustion.
- Incremental sync by checking existing GCS parquet names per host/hash.
- Detached loop (recommended `screen`) to survive terminal/session disconnect.
- Cycle order: `linux1` then `windows1`, then sleep.
- Keep only one uploader loop alive. Duplicate loops will race on local buffer and create false I/O errors.

Operational cadence:
- Frame progress polling: every 2-3 min.
- GCS upload count polling: every 5-10 min.
- Escalate only when both local done counts and GCS counts stall.

## 6. Debug Habits That Saved Time
1. Prefer low-overhead signals (`*.done`, log tail, scheduler state) over heavy WMI/perf probes.
2. For bulk GCS old-hash cleanup, prefer `gcloud storage rm` hash patterns over fragile long `gsutil` loops.
3. Keep upload script idempotent (skip already uploaded parquet) so retries are safe.
4. Harden transfer path: `scp` retry + skip failed file + explicit file-list GCS upload (avoid wildcard ambiguity).
5. Track run state in JSON + plain-text logs to support unattended monitoring.
6. If `gcloud` repeatedly logs `Resuming upload ... parallel_composite_uploads`, disable composite mode:
   - `gcloud config set storage/parallel_composite_upload_enabled False`

## 7. File Anchors
- Skill standard: `.codex/skills/omega-run-ops/SKILL.md`
- Run status JSON: `audit/runtime/v52/autopilot_<hash>.status.json`
- Uplink loop log: `audit/runtime/v52/uplink_<hash>.log`

---
**Directive for future upgrades:** Reuse this playbook before launching any new major frame campaign. The costliest failure is invalid frames discovered after hours of compute.
