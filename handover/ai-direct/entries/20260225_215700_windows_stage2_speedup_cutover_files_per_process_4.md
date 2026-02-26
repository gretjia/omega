# Windows Stage2 Speedup Cutover (files-per-process)

Date: 2026-02-25 21:57 +0800

## Why it can speed up
Windows Stage2 was still using single-file subprocess orchestration (`stage2_targeted_resume.py` old mode), which pays repeated Python import + pipeline bootstrap cost per file.

## Changes applied
1. Deployed batch-capable runner to Windows:
- `D:\work\Omega_vNext\tools\stage2_targeted_resume.py`

2. Updated v2 wrapper command:
- file: `D:\work\Omega_vNext\audit\run_stage2_retry_isolated_v2.cmd`
- added arg: `--files-per-process 4`

3. Reduced accidental scheduling risk:
- disabled legacy task: `Omega_v62_stage2_isolated`
- kept active task: `Omega_v62_stage2_isolated_v2`

4. Relaunched Stage2 v2 task.

## Verification
- Task states:
  - `Omega_v62_stage2_isolated` => Disabled
  - `Omega_v62_stage2_isolated_v2` => Running
- Process command line now includes batch arg:
  - `... stage2_targeted_resume.py ... --files-per-process 4`
- New log header confirms cutover:
  - `FILES_PER_PROCESS=4`
  - `BATCH_TOTAL=8`
  - `[batch 1/8] START ...`

## Snapshot after cutover
- `INPUT_TOTAL=191`
- `PENDING_TOTAL=30`
- historical `FAILED_CARRY_IN=2`

This is orchestration-only; Stage2 math/output schema logic unchanged.
