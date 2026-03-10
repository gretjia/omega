# V655A Gemini Pass, Deploy, And H1 Probe In Flight

Status: In-flight runtime checkpoint
Date: 2026-03-10 03:42 UTC
Mission: V655A Soft-Mass Campaign Accumulation Audit

## What completed

- `gemini -p` math audit passed without required fixes
- mission authority is now:
  - `audit/v655_soft_mass_campaign_accumulation.md`
- spec pass record:
  - `handover/ai-direct/entries/20260310_033545_v655a_spec_gemini_pass.md`
- mission-open record:
  - `handover/ai-direct/entries/20260310_033700_v655a_soft_mass_mission_open.md`
- code commit pushed:
  - `16b24dc`
  - `feat(v655a): widen campaign accumulation stream`
- clean-worktree deploy succeeded to:
  - `linux1-lx`
- remote synced to:
  - `deploy_v655a_16b24dc_a@16b24dc`

## What changed in code

- `tools/forge_campaign_state.py`
  - default `--require-is-signal` changed from `1` to `0`
  - log prefix updated to `V655A`
- `tests/test_campaign_state_contract.py`
  - added coverage that soft-mass collection admits physics-valid rows even when `is_signal == 0`

## Local verification

- `uv run --with pytest --with polars --with numpy pytest tests/test_campaign_state_contract.py tests/test_campaign_event_study.py -q`
  - `17 passed in 0.94s`
- `python3 -m py_compile`
  - passed

## Live runtime

Runtime root:

- `audit/runtime/v655a_probe_linux_h1_2023_20260310_034020`

Launch shape:

- `years=2023`
- `horizons=5,10,20`
- `pulse_mode=sign_nms`
- `pulse_min_gap=30`
- `pulse_floor=1e-12`
- `require_is_signal=0`
- `require_is_physics_valid=1`

Latest live facts:

- active python PID:
  - `655335`
- latest forge log lines:
  - `[V655A] matched L1 files=72 L2 files=72 horizons=[5, 10, 20] pulse_mode=sign_nms pulse_min_gap=30`
  - `[V655A] phase 1/4 collecting daily spine from L1`

## Comparison Note

This V655A launch currently reports:

- `matched L2 files=72`

while the frozen V654 H1 evidence recorded:

- `l2_files=98`

Current read-only explanation:

- remote `glob_count=98`
- current regex-kept file count under the live expansion path:
  - `72`

This is recorded as a comparison caveat, not yet as a blocker.
