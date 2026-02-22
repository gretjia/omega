# Handover: Infrastructure Migration to US-Central1 (Completed)

**Date:** 2026-02-18 09:05:00 +0800
**Topic:** Migration from US-West1 to US-Central1 & Quota Optimization
**Status:** **RUNNING** (Optimized Configuration)

## Context
- `us-west1` suffered from N1 stockouts and N2 quota limits.
- Migrated to `us-central1` to leverage approved quotas:
  - **N2 CPUs:** 400 vCPUs (Approved).
  - **C2 CPUs:** 300 vCPUs (Approved).
  - **Spot/Preemptible:** Denied (Disabled in config).

## Actions Executed
1. **Data Migration:** Copied `gs://omega_v52` -> `gs://omega_v52_central`.
   - *Fix:* Used `--bucket gs://omega_v52_central/omega` to handle nested path structure.
2. **Autopilot Restart:**
   - Launched with `n2-highmem-32` for base matrix.
   - Launched with `c2-standard-30` for compute-heavy tasks.
   - Disabled spot instances.

## Current Status
- **Active Job:** `omega-v60-run_vertex_base_matrix-20260218-090004`
- **Region:** `us-central1`
- **Machine:** `n2-highmem-32`
- **Pipeline:** Autopilot running autonomously.

## Next Steps
- Monitor `audit/runtime/v52/autopilot_aa8abb7.runner.log` for completion of base matrix.
- Verify `c2-standard-30` provisioning during the optimization phase.
