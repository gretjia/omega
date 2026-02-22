# Linux 4T Samsung 990 Pro Cache Policy Codification

- Timestamp: 2026-02-22 23:12:40 +0800
- Operator: Codex (GPT-5)
- Session Type: `normal-handoff`

## 1) Objective

- Verify whether handover explicitly encoded the user-mandated Linux cache policy:
  - all Stage1/ETL temp cache must use 4T Samsung 990 Pro.

## 2) Completed in This Session

- Audited `handover/` for cache policy wording.
- Confirmed existing notes only mentioned:
  - historical `4TB NVMe` deadlock symptom
  - `framing_cache` cleanup/recovery actions
- Confirmed runtime script already points Linux temp cache to:
  - `/home/zepher/framing_cache` in `tools/stage1_linux_base_etl.py`
- Added explicit mandatory cache policy block into `handover/ai-direct/LATEST.md` with pre-launch verification commands.

## 3) Current Runtime Status

- Mac: Handover policy patch only; no runtime job launched from this session.
- Windows1: Unchanged by this update.
- Linux1: Unchanged by this update.

## 4) Critical Findings / Risks

- Prior handover state lacked an explicit "MUST use 4T Samsung 990 Pro" statement, so takeover agents could miss this hardware constraint.
- If Linux cache drifts from `/home/zepher/framing_cache` to non-target disks, risk includes severe I/O contention, SSH stalls, and run instability.

## 5) Artifacts / Paths

- `handover/ai-direct/LATEST.md`
- `handover/ai-direct/entries/20260222_231240_linux_cache_policy_990pro.md`
- `tools/stage1_linux_base_etl.py`

## 6) Commands Executed (Key Only)

- `rg -n --no-heading -S "990|Samsung|三星|4T|4TB|cache|缓存|framing_cache|NVMe|SSD" handover`
- `rg -n --no-heading -S "framing_cache|tmp/framing|omega_framing|990|Samsung|4T|4TB|nvme" handover/ai-direct/entries`
- `rg -n --no-heading -S "framing_cache|cache_root|tmp/framing|omega_framing|CACHE" tools/stage1_linux_base_etl.py tools/stage1_windows_base_etl.py audit/v62_framing_rebuild.md`

## 7) Exact Next Steps

1. Before any Linux Stage1 restart, run mount/model gate:
   - `findmnt -T /home/zepher/framing_cache`
   - `lsblk -o NAME,SIZE,MODEL,MOUNTPOINTS | rg -n "990|framing_cache|nvme"`
2. If gate fails, fix mount/bind first; do not launch Stage1.
3. Keep this policy mirrored in new handover entries whenever runtime changes.
