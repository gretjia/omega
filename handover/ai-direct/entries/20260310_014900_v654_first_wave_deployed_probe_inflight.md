---
entry_id: 20260310_014900_v654_first_wave_deployed_probe_inflight
task_id: V654-IDENTITY-PRESERVING-PULSE-COMPRESSION
timestamp_local: 2026-03-10 01:49:00 +0000
timestamp_utc: 2026-03-10 01:49:00 +0000
operator: Codex
role: commander
branch: main
git_head: 244bde7
status: in_progress
---

# V654 First Wave Deployed, First Linux Probe In Flight

## 1. Landed State

The V654 first code wave is now on `main`:

- `74242d9` `feat(v654): land pulse-compression first wave`

The first deploy-time repair is also on `main`:

- `244bde7` `fix(v654): add repo-root import path for forge`

## 2. What Landed

New V654 authority and mission documents:

- `audit/v654_identity_preserving_pulse_compression.md`
- `handover/ai-direct/entries/20260310_012744_v654_identity_preserving_pulse_compression_spec_draft.md`
- `handover/ai-direct/entries/20260310_013420_v654_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260310_013500_v654_identity_preserving_pulse_compression_mission_open.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`

Code / tests:

- `tools/forge_campaign_state.py`
- `tests/test_campaign_state_contract.py`
- `tests/test_campaign_event_study.py`

## 3. Local Verification

- `python3 -m py_compile` passed
- `uv run --with pytest --with polars --with numpy pytest tests/test_campaign_state_contract.py tests/test_campaign_event_study.py -q`
  - `15 passed in 0.81s`
- after the deploy-time import-path fix:
  - `python3 -m py_compile` passed again
  - `15 passed in 0.47s`

## 4. Deploy Sequence

First deploy attempt from a clean detached worktree exposed a deploy-path bug:

- `tools/deploy.py` derived branch name `HEAD`
- remote push failed because `HEAD` is not a valid destination refname on the worker

Workaround used:

- deploy from a clean temporary worktree with a real local branch name

Then a second deploy-time bug appeared in the live probe:

- `tools/forge_campaign_state.py` failed on `linux1-lx` with:
  - `ModuleNotFoundError: No module named 'config'`

Fix landed:

- `244bde7` adds repo-root insertion to `sys.path` before importing `config`

Current deployed linux state:

- worker synced to:
  - `deploy_v654_244bde7@244bde7`

## 5. Live Probe

Current runtime root:

- `audit/runtime/v654_probe_linux_20260310_014600`

Launch shape:

- node:
  - `linux1-lx`
- command family:
  - `python3 tools/forge_campaign_state.py`
- inputs:
  - `/omega_pool/parquet_data/latest_base_l1/host=linux1/202301*.parquet`
  - `/omega_pool/parquet_data/stage2_full_20260307_v643fix/l2/host=linux1/202301*.parquet`

Observed live state at the latest poll:

- active python PID:
  - `3680127`
- elapsed:
  - about `02:10`
- CPU:
  - about `71.6%`
- RSS:
  - about `14.6 GB`
- current log state:
  - `matched L1 files=10 L2 files=16 horizons=[5, 10, 20] pulse_mode=sign_nms pulse_min_gap=30`
  - `phase 1/4 collecting daily spine from L1`

No new traceback was observed after the import-path repair.

## 6. Current State

- V654 is active
- first code wave is landed
- linux deploy is complete
- first bounded forge probe is in flight
- ML remains closed
