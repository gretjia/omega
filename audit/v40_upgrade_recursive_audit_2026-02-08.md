# v40 Upgrade Recursive Audit (2026-02-08)

## Scope
- Primary source: `audit/v40_race_patch.md`
- Secondary (non-Epiplexity only):
  - `audit/v31_math_manual_audit.md`
  - `audit/v31_math_manual_audit_patch.md`
- Explicitly excluded: further Epiplexity algorithm race decisions (already finalized)

## Phase 1 Audit (Config + Math Core)
### Checks
- `python3 -m py_compile config.py omega_v3_core/omega_math_core.py`
- Manual invariant scan: SRL race params, spoof-penalty knobs, topology race config, LZ76 default mode.

### Result
- PASS
- No syntax errors.
- v40 primitives present:
  - SRL race exponents + lane names + standard lane index.
  - Effective-depth spoof penalty controls.
  - Topology race config and scale floors.
  - Epiplexity default switched to LZ76 linear entry path.

## Phase 2 Audit (Kernel + ETL Integration)
### Checks
- `python3 -m py_compile omega_v3_core/kernel.py omega_v3_core/omega_etl.py`
- Runtime smoke (`.venv`): apply recursive physics on synthetic frame and assert output schema.

### Result
- PASS
- ETL now emits supporting traces:
  - `ofi_trace`, `vol_list`, `vol_trace`, `time_trace`
- Kernel emits race features while preserving compatibility fields:
  - `srl_resid_033`, `srl_resid_050`, `srl_resid_066`
  - `topo_micro`, `topo_classic`, `topo_trend`
  - legacy-compatible: `srl_resid`, `topo_area`, `topo_energy`
- Effective depth uses spoof-aware penalty.

## Phase 3 Audit (Trainer/Auditor + Recursive Tool)
### Checks
- `python3 -m py_compile omega_v3_core/trainer.py omega_v3_core/physics_auditor.py`
- Recursive audit tool:
  - `./.venv/bin/python tools/v40_recursive_audit.py`

### Recursive Audit Output
```json
{
  "status": "PASS",
  "checks": [
    {"name": "cfg_srl_lane_alignment", "status": "PASS"},
    {"name": "cfg_srl_standard_lane", "status": "PASS"},
    {"name": "no_literal_0.33", "status": "PASS"},
    {"name": "no_literal_0.66", "status": "PASS"},
    {"name": "runtime_smoke", "status": "PASS"}
  ]
}
```

### Result
- PASS
- Training feature space now includes v40 race feature groups (config-driven).
- Auditor prefers `topo_micro` if present, else falls back to `topo_area`.
- Added checkpoint safety guard:
  - If loaded checkpoint `feature_cols` mismatch current config feature space, trainer/parallel runner auto-reset to fresh state instead of crashing mid-run.

## Pre-Training Readiness (Interim)
- Current status: READY FOR SMOKE TEST (Phase 4).
- Next gate before formal full training:
  - Run one minimal end-to-end dry-run with real parquet batch and checkpoint write/read.

## Phase 4 Smoke Test (Training Readiness Gate)
### Smoke A: Trainer core on real frame file
- Sample file:
  - `data/level2_frames_2023/20230203_000680.SZ.parquet`
- Procedure:
  - `OmegaTrainerV3._prepare_frames(...)` -> verify no missing feature columns.
  - Single-batch `StandardScaler.partial_fit` + `SGDClassifier.partial_fit`.
- Result:
  - PASS
  - `raw_rows=46`, `proc_rows=12`, `missing_features=[]`, `fit_ok=1`.

### Smoke B: End-to-end mini parallel run (checkpoint + report)
- Command:
  - `./.venv/bin/python parallel_trainer/run_parallel_epi_race.py --file-list audit/v34_epi_manifest_round1.txt --max-files 1 --workers 2 --batch-rows 1000 --checkpoint-rows 1000 --sample-frac 1.0 --out-dir artifacts/v40_smoke --checkpoint-prefix v40_smoke_ckpt_rows_ --report-path audit/v40_smoke_report.json --stage-local --stage-dir /tmp/omega_v40_stage --stage-chunk-files 1 --no-resume`
- Artifacts:
  - `artifacts/v40_smoke/v40_smoke_ckpt_rows_12.pkl`
  - `audit/v40_smoke_report.json`
- Result:
  - PASS
  - Checkpoint and report both generated successfully.

## Final Gate Decision
- Formal training readiness: **PASS** (subject to your data-scope and compute-budget choice).
- Known caveat:
  - `run_parallel_epi_race.py` is still named and reported as Epiplexity race utility; it works as smoke harness, but for production v40 full-run we should add a dedicated `v40` runner name/report schema in next patch.
