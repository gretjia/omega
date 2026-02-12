# Optimization Plan: Pipeline V5.0

## Phase 1: Framing Optimization (COMPLETED)
- [x] Implement `-mmt=on` for multithreaded 7z extraction.
- [x] Implement Symbol Chunking in `framer.py`.
- [x] Transition `stage_root` to 48GB RAM Disk (`R:`).
- [x] Balance workers to 40 for Ryzen AI 395.

## Phase 2: Stage-Awareness (COMPLETED)
- [x] Update `pipeline_runner.py` to differentiate RAM strategy by stage.
- [x] Ensure Training stage releases RAM Disk resources.

## Phase 3: 2025 Scaling (PENDING)
- [ ] Monitor Feb 2024 - Dec 2024 progress.
- [ ] Trigger RAM Disk resize to 60GB before 2025 ingestion.
- [ ] Verify 2025 extraction headroom (>5GB).

## Current Status
- **Framing Speed:** 91.6s (18% improvement).
- **ETA:** 2026-02-13 00:45.
