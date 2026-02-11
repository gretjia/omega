# v40 Upgrade Patch-02 Recursive Audit (2026-02-08)

## Scope
- Primary source: `audit/v40_race_patch_02.md`
- Goal: keep v40 math purity while importing v31 survival behavior via **data-derived priors** (no hard-coded business constants in math core).

## Phase 1 - Config & Loader (Meta-Priors Wiring)
### Changes
- `config.py`
  - `L2EpiplexityConfig` added:
    - `sigma_gate_enabled`
    - `sigma_gate` (PLANCK_SIGMA_GATE)
    - `sigma_gate_quantile`
    - `prior_sample_files`
    - `prior_min_sigma_points`
    - `prior_min_y_points`
  - `L2SRLConfig` added:
    - `anchor_y` (ANCHOR_Y)
    - `anchor_weight`
    - `anchor_clip_min`
    - `anchor_clip_max`
- `load_l2_pipeline_config(...)` now also loads from `AUTO_LEARNED_PARAMS`:
  - `PLANCK_SIGMA_GATE`
  - `ANCHOR_Y`
  - optional `EPI_BLOCK_MIN_LEN`
  - optional `EPI_SYMBOL_THRESH`

### Recursive Check
- Config override smoke passed (temp JSON -> dataclass values updated as expected).

## Phase 2 - Kernel Physics Gate + Anchor Recursion
### Changes
- `omega_v3_core/kernel.py`
  - Added **energy gate**:
    - if `sigma_eff < sigma_gate`, mark `is_energy_active=False`, set epiplexity to fallback.
  - Added **anchor recursion**:
    - regular adaptive update kept.
    - then apply `current_y = (1-anchor_w)*current_y + anchor_w*anchor_y`.
    - clip to `anchor_clip_[min,max]`.
  - Added output columns:
    - `is_energy_active`
    - `sigma_gate`
  - Signal synthesis now explicitly requires `is_energy_active == True`.

### Recursive Check
- `tools/v40_recursive_audit.py` runtime checks passed, including gate behavior.

## Phase 3 - Auditor Derives Priors from Data Distribution
### Changes
- `omega_v3_core/physics_auditor.py`
  - Added `derive_market_priors()`:
    - learns `PLANCK_SIGMA_GATE` from sigma quantile.
    - learns `ANCHOR_Y` from median implied Y.
    - includes minimum-point guards to avoid small-sample drift.
  - `run_continuous_calibration()` now derives priors first and exports them.
  - `_export_config(...)` now writes `PLANCK_SIGMA_GATE` and `ANCHOR_Y` into `AUTO_LEARNED_PARAMS`.
  - Added `_load_debug_frames(...)` to support both:
    - raw quote inputs (kernel path),
    - prebuilt frame parquet inputs (direct recursive application).

### Recursive Check
- Small local sample smoke passed (returns default priors when sample points below thresholds).

## Phase 4 - Parallel Pipeline Hardening (Frame/Train/Backtest)
### Changes
- `tools/run_l2_audit_driver.py` (parallel frame)
  - Added cross-platform `resolve_7z_exe()` (macOS/Linux supports `7zz/7z/7za` from PATH).
  - Added CLI: `--seven-zip`.
  - Worker now receives resolved 7z path (no Windows-only lookup in workers).
- `parallel_trainer/run_parallel_v31.py` (parallel train)
  - Added CLI + input controls:
    - `--file-list`
    - `--max-files`
    - `--workers`
    - `--batch-rows`
    - `--no-resume`
- `parallel_trainer/run_parallel_backtest_v31.py` (parallel backtest)
  - Added CLI + input controls:
    - `--policy`
    - `--file-list`
    - `--max-files`
    - `--data-dir` (repeatable)
    - `--workers`

### Result Semantics
- Math logic unchanged in parallel scripts; only task discovery and execution controls improved.

## Phase 5 - Smoke Tests
### 1) Parallel Frame Smoke (macOS)
- Created tiny local test archive under `data/level2/000001/00000101.7z`.
- Command:
  - `./.venv/bin/python tools/run_l2_audit_driver.py --year "/000001/" --limit 1 --workers 2 --output-dir /tmp/v40_frame_smoke_out4 --skip-report`
- Output:
  - `/tmp/v40_frame_smoke_out4/00000101_000001.SZ.parquet` generated.

### 2) Parallel Train Smoke
- Command:
  - `./.venv/bin/python parallel_trainer/run_parallel_v31.py --file-list audit/v34_epi_manifest_round1.txt --max-files 1 --workers 2 --batch-rows 1000 --no-resume`
- Output:
  - `artifacts/checkpoint_rows_12.pkl` generated.

### 3) Parallel Backtest Smoke
- Local manifest used to avoid shared-mount I/O stall.
- Command:
  - `./.venv/bin/python parallel_trainer/run_parallel_backtest_v31.py --policy artifacts/checkpoint_rows_12.pkl --file-list /tmp/v40_backtest_manifest2.txt --max-files 1 --workers 2`
- Output:
  - backtest completed and produced full report block.

## Final Verdict
- v40 patch-02 upgrade status: **PASS**
- Formal training readiness: **PASS**
- Operational note:
  - For shared Windows mount, prefer `--file-list` + local staged samples to prevent directory scan stalls.
