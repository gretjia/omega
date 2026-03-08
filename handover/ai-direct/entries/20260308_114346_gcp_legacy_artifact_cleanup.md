# 2026-03-08 11:43 UTC - GCP Legacy Artifact Cleanup

## Scope
- Goal: remove billable Google Cloud Storage artifacts from `v63` or earlier runs to reduce spend.
- Reachable buckets from the controller credential:
  - `gs://omega_v52_central`
  - `gs://omega_v52`

## Safety Check
- Verified Vertex AI custom jobs in OMEGA project `gen-lang-client-0250995579` (`projectNumber=269018079180`) for both `us-central1` and `us-west1`.
- Matching legacy jobs were all in terminal states (`JOB_STATE_SUCCEEDED`, `JOB_STATE_FAILED`, or `JOB_STATE_CANCELLED`).
- No active job was left pointing at the old `v63` or earlier artifact paths during deletion.

## Pre-Delete Findings
- `gs://omega_v52/**` already reported `0 B`.
- `gs://omega_v52_central/omega/omega/v52/frames/**` reported about `126.24 GiB`.
- `gs://omega_v52_central/omega/staging/base_matrix/v63/**` reported about `337.98 MiB`.
- `gs://omega_v52_central/omega/staging/models/v63/**` reported about `272.66 KiB`.
- `gs://omega_v52_central/omega/staging/backtest/v6/**` reported about `3.5 KiB`.
- `gs://omega_v52_central/staging/code/**` reported about `242.05 KiB`.
- Additional residual legacy objects remained after the first pass:
  - `gs://omega_v52_central/omega/staging/code/omega_core_*.zip`
  - `gs://omega_v52_central/staging/aiplatform-*.tar.gz`
  - stale zero-byte `.done` markers under `gs://omega_v52_central/omega/v52/frames/host=windows1/`

## Deleted Objects
- `gs://omega_v52_central/omega/omega/v52/frames/**`
- `gs://omega_v52_central/omega/staging/base_matrix/v63/**`
- `gs://omega_v52_central/omega/staging/models/v63/**`
- `gs://omega_v52_central/omega/staging/backtest/v6/**`
- `gs://omega_v52_central/staging/code/omega_core_stage3.zip`
- `gs://omega_v52_central/staging/code/payloads/v63_q1q9/**`
- remaining `gs://omega_v52_central/omega/staging/code/omega_core_*.zip`
- remaining `gs://omega_v52_central/staging/aiplatform-*.tar.gz`
- remaining `gs://omega_v52_central/omega/v52/frames/host=windows1/*.done`

## Execution Notes
- Primary delete completed with `gsutil -m rm -r` over about `2.3k` objects.
- Residual small-object cleanup completed with a follow-up `gsutil -m rm` over `21` objects.

## Post-Delete Verification
- `gsutil du -sh gs://omega_v52_central/**` now reports `0 B`.
- `gsutil du -sh gs://omega_v52/**` remains `0 B`.
- `gsutil ls -r` still prints some empty prefix paths under `omega/omega/` and `omega/v52/frames/`, but no billable objects remain in the reachable legacy bucket.

## Operational Impact
- Current local Stage3 base-matrix run on `linux1-lx` is unaffected.
- Any future cloud Stage3/Vertex work must stage fresh artifacts; the old `omega_v52*` bucket contents should be treated as intentionally purged.
