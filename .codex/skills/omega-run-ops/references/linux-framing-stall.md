# Linux Framing Stall Signals (And What To Do)

## Fast Triage

1. Log keeps moving?
   - `tail -n 50 audit/_pipeline_frame.log`
2. `*.done` count increasing for the pinned git short?
   - `find /omega_pool/parquet_data/v52/frames/host=linux1 -maxdepth 1 -name "*_<gitshort>.parquet.done" | wc -l`
3. Stage dir growing?
   - `du -sh /home/zepher/Omega_frames/v52/stage_linux/* | tail`

If log and stage are moving but CPU is low: you're likely I/O or decompression bound; this is normal.

## "After First Archive It Freezes" Pattern

Symptom:
- Second archive never reaches `[Done]`
- Parent/children processes show `wchan=futex_` and near-zero CPU

Cause (common):
- `fork`-based multiprocessing after Polars runtime threads are initialized can deadlock.

Fix:
- Use a code/tag that forces:
  - `spawn` multiprocessing context
  - reuse a single `ProcessPoolExecutor` across archives (do not create a new pool per archive)

Recovery steps:

1. Stop the stalled parent + children.
2. Remove the partially extracted stage folder for the active date.
3. Restart framing pinned to the fixed tag/commit.

## Detaching Long Jobs

Prefer `nohup` (or `systemd-run`) so the process survives SSH disconnect:

```bash
nohup .venv/bin/python -u pipeline_runner.py --stage frame --config configs/hardware/linux.yaml \
  --archive-list audit/runtime/v52/shard_linux.txt > audit/_pipeline_frame.nohup.log 2>&1 &
echo $! > artifacts/runtime/v52/frame_linux1.pid
```
