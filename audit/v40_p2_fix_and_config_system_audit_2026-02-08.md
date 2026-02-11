# v40 P2 Fix + Config System Audit (2026-02-08)

## Scope
1. Close P2 issues from independent audit:
   - renormalization penalty constants hardcoded in auditor
   - ops skill drift from v40 runtime pipeline
2. Clarify v40 config architecture:
   - what is active
   - what is legacy/compatibility only
   - whether current v40 is audited and executable

## P2-1: Renormalization penalty constants moved to config

### Changes
- Added in `L2ValidationConfig`:
  - `renorm_ortho_penalty_threshold`
  - `renorm_ortho_penalty_factor`
  - file: `config.py:665`
- Added optional runtime overrides from `AUTO_LEARNED_PARAMS`:
  - `RENORM_ORTHO_PENALTY_THRESHOLD`
  - `RENORM_ORTHO_PENALTY_FACTOR`
  - file: `config.py:782`
- Updated auditor scoring logic:
  - removed direct literals from score path
  - now uses `self.cfg.validation.*`
  - file: `omega_v3_core/physics_auditor.py:233`

### Result
- P2 hardcoding issue resolved for renorm scoring path.

## P2-2: Ops skill aligned to v40 operational reality

### Changes
- Updated `ops` skill to prioritize:
  - `jobs/windows_v40/start_v40_pipeline_win.ps1`
  - runtime status paths under `audit/v40_runtime/windows/*`
  - Mac monitoring with `tools/v40_runtime_status.py`
  - direct v40 script entry (`run_l2_audit_driver.py`, `run_parallel_v31.py`, `run_parallel_backtest_v31.py`)
  - file: `.agent/skills/ops/SKILL.md:13`

### Result
- P2 documentation/process drift resolved for operations entrypoints and observability paths.

---

## v40 Config System Audit

## 1) Active config authority (v40)

1. **Primary source of truth**: `config.py`
   - v40 business and math control parameters live in `L2*` dataclasses.
2. **Runtime learned overlay**: `model_audit/production_config.json`
   - loaded via `load_l2_pipeline_config()`
   - used for audited promotions (for example `TARGET_FRAMES_DAY`, `PLANCK_SIGMA_GATE`, `ANCHOR_Y`).

Evidence:
- `omega_v3_core/README.md:26`
- `config.py:765`

## 2) Non-primary/legacy config files

Discovered config files (repo depth <= 3):
1. `./config.py` (active v40 mainline)
2. `./parallel_trainer/parallel_config.py` (historical parallel adapter settings, non-business-math source)
3. `./omega_trainer_v1/config.py` (legacy)
4. `./archive/config.py` (archived legacy copy)
5. `./openclaw_config.json` (separate tool/config domain; not v40 kernel math source)

Conclusion:
- v40 mainline does **not** rely on legacy `omega_trainer_v1/config.py` or `archive/config.py` for kernel math.
- these files are retained for history/compatibility, not as upgrade targets.

Evidence:
- `omega_v3_core/README.md:51`
- `parallel_trainer/parallel_config.py:1`
- `omega_trainer_v1/config.py:1`
- `archive/config.py:1`

## 3) Has v40 config migration been audited and is it executable?

Current answer: **Yes (with known scope)**.

Evidence of audited/executable state:
1. recursive audit:
   - `./.venv/bin/python tools/v40_recursive_audit.py` -> PASS
2. syntax sanity:
   - `./.venv/bin/python -m py_compile config.py omega_v3_core/physics_auditor.py parallel_trainer/run_parallel_backtest_v31.py` -> PASS
3. README sync gate:
   - `python3 tools/check_readme_sync.py` -> PASS
4. P1 and P2 closure records exist:
   - `audit/v40_p1_fix_2026-02-08.md`
   - this document

---

## Final Verdict

1. P2 engineering issues are closed.
2. v40 config system is now explicitly documented as:
   - single active config authority (`config.py`)
   - audited runtime overlay (`production_config.json`)
   - legacy config files retained but not part of v40 mainline control plane.
3. v40 remains executable under current audited pipeline and smoke gates.
