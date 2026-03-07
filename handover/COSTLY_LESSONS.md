# Costly Lessons Ledger

**Purpose:** This document records expensive mistakes (in terms of money, time, or trust) to ensure they are **never repeated**.
**Audience:** All AI Agents and Human Operators.
**Mandate:** Read this before launching any high-concurrency or long-running cloud job.
**Companion checklist:** `handover/V60_PRE_SUBMIT_CHECKLIST.md`

---

## 2026-02-18 | The $13 "Blind Retry" Incident

**Cost:** ~$13 USD (approx) + 4 hours of delay.
**Outcome:** Zero useful artifacts produced during the incident window.
**Root Cause:** A combination of Infrastructure Blindness and "Dumb" Automation.

### 1. The "Partially Approved" Quota Trap
- **Mistake:** We attempted to use `n2-highmem-32` because the GCE Quota page said "Partially Approved (400 vCPUs)".
- **Reality:** Vertex AI (managed service) often has stricter or separate quota pools than raw Compute Engine. "Partial" approval often means "Denied" for Vertex scheduling in specific zones.
- **Consequence:** Jobs were submitted, queued, provisioned, and then immediately killed by the control plane. We paid for the overhead of scheduling and partial provisioning without getting results.
- **Lesson:** **Only use Machine Types with "Approved" (Green) quotas.** If a quota is "Partial," treat it as "Denied" for automated pipelines.

### 2. The Watchdog "Cash Burn" Loop
- **Mistake:** The `ai_incident_watchdog.py` was configured to "Auto-Resume" on failure. When the job failed due to OOM (Out of Memory) or ImportError, the watchdog simply restarted it.
- **Reality:** The error (OOM/ImportError) was deterministic. Restarting it 14 times just burned 14x the money for the same failure.
- **Consequence:** 14 retry cycles of 10-minute runs = ~140 minutes of wasted high-memory compute billing.
- **Lesson:** **Never auto-restart a `JOB_STATE_FAILED` job without diagnosis.** The watchdog must now use `gemini -y` to read Cloud Logging. If the error is deterministic (OOM, Config, Code), it must **HALT** and ask for help, not retry.

### 3. The "Missing Dependency" Fee
- **Mistake:** Local environment had `python-json-logger`, but cloud container didn't.
- **Reality:** The job would spin up (billing starts), run `pip install`, import the code, crash on `ModuleNotFoundError`, and shut down.
- **Consequence:** We paid for the boot-up time of a 16-vCPU machine just to print an error message.
- **Lesson:** **Explicitly declare ALL dependencies** in the payload script. Do not rely on "implied" packages. For new payloads, run a **Canary** (tiny 1-CPU job) first to verify the environment before launching the big machine.

### 4. The "Data Gravity" Tax
- **Mistake:** We tried to compute in `us-central1` while data was in `us-west1`.
- **Reality:** Cross-region data access is slow and costs money (Egress fees).
- **Consequence:** We had to pay ~$1.26 to move the data. While necessary, it was a friction point.
- **Lesson:** **Compute where your data is.** If you must move compute, move the data *first*.

---

## Actionable Checklist for Future Jobs

Before running `v60_autopilot.py` or any Vertex Job:

1.  [ ] **Quota Check:** Is the requested machine type quota **Fully Approved** in the target region?
2.  [ ] **Dependency Check:** Are all imports in `omega_core` explicitly listed in `_install_dependencies()`?
3.  [ ] **Watchdog Check:** Is the watchdog using `gemini -y` (shell access) to diagnose failures?
4.  [ ] **Canary Check:** If this is a new code version, has a small canary job passed?

---

## 2026-02-20 | The ~$30 v60 Backtest Failure Cascade (Why many failures, why final run succeeded)

**Cost:** ~\$30 USD (operator estimate) + multiple failed/cancelled cloud runs.
**Outcome:** Final full-universe backtest succeeded after iterative root-cause fixes.

### What failed, in order

1. **Semantic causality failure (earlier payload path):**
- **Symptom:** Long runtime but semantic counters stalled (`used=0`, `rows=0`) and final failure.
- **Root Cause:** Time-series causality was severed by per-file/day isolated execution while labels required T+1 continuity.
- **Consequence:** Compute burned without producing usable processed rows.

2. **Schema contract failure (`time` hardcoded):**
- **Symptom:** Vertex backtest job failed with `ColumnNotFoundError: \"time\" not found`.
- **Root Cause:** Cloud payload assumed `time`; production frame schema used `time_end`/`bucket_id` on many artifacts.
- **Evidence:** Failed job `customJobs/8385422044799434752`; smoke-fixed confirmation on `customJobs/4089128737776336896` (`JOB_STATE_SUCCEEDED`).

3. **Memory ceiling during global materialization phase:**
- **Symptom:** Vertex terminal error `Replicas low on memory: workerpool0`.
- **Root Cause:** Peak memory occurred around load/dedup/sort/prepare boundary on full-universe materialization.
- **Evidence:** Failed jobs:
  - `customJobs/6324251159091478528` (`n2-standard-80`)
  - `customJobs/1475563210273718272` (`n2-highmem-64`)
  - `customJobs/3366793578792615936` (`n2-highmem-80`)

4. **One controlled cancellation during takeover:**
- **Evidence:** `customJobs/6945888645156962304` (`JOB_STATE_CANCELLED`).

### Why the final run succeeded

**Final successful job:** `customJobs/1959559432727691264` on `n2-highmem-80` (`JOB_STATE_SUCCEEDED`).

**Successful configuration/changes:**
- Global causal materialization preserved chronological continuity for T+1 labels.
- Schema preflight + dynamic time-key resolution (`time | time_end | time_start | bucket_id`) removed hardcoded schema risk.
- Reused precomputed physics (`reuse_precomputed_physics=true`) instead of recomputing expensive recursive physics in backtest.
- Dropped heavy trace/list columns before peak memory stages (`ofi_list`, `ofi_trace`, `vol_list`, `vol_trace`, `time_trace`).
- Bounded evaluation memory with trace cap (`--max-eval-traces=50000`).
- Added download progress telemetry and controlled downloader parallelism (`--download-workers=16`) for observability and safer throughput.

**Result evidence (final artifact):**
- `status=completed`
- `files_used=263`
- `total_proc_rows=8907595`
- `seconds=1170.03`
- `Topo_SNR=10.885431366882955`
- `Model_Alignment=0.49742754220434177`
- Artifact: `gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`

### Mandatory guardrails from this incident

1. **Do not use liveness-only monitoring.** Treat run as healthy only if semantic counters advance (`files_used > 0`, `total_proc_rows > 0`) within early time budget.
2. **Fail fast on schema contract.** Run preflight on first selected parquet before bulk download/compute.
3. **Track phase milestones explicitly.** Require ordered milestones: download -> load -> dedup -> sort -> prepare -> evaluate.
4. **Auto-cancel semantic stalls.** Example triggers: `elapsed >= 15m && total_proc_rows == 0` or long phase silence.
5. **Use canary before full-universe run** whenever payload behavior changes (schema logic, memory path, or evaluator).
6. **Prefer memory-aware compute tiers** for global materialization and keep evaluation memory bounded.

### Primary references

- `audit/runtime/v60_factual_evidence/job_timeline_selected.txt`
- `audit/runtime/v60_factual_evidence/job_describe_key_fields.txt`
- `audit/runtime/v60_factual_evidence/backtest_success_key_lines.txt`
- `audit/runtime/v60_factual_evidence/backtest_failed_key_lines.txt`
- `audit/runtime/v60_factual_evidence/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`
- `handover/DEBUG_LESSONS.md` (entries at `2026-02-19T16:13:41Z`, `2026-02-19T16:56:18Z`, `2026-02-20T02:22:00+08:00`, `2026-02-20T03:10:00+08:00`)

---

## Additional v60 Engineering Lessons (Post-Landing)

### 1) Validation Coverage Is a Deliverable, Not a Byproduct
- **Observed:** End-to-end jobs can succeed technically but still fail architectural sign-off when a mandatory requirement has no direct evidence marker.
- **Practice:** Add explicit requirement telemetry fields into artifacts and keep a requirement-to-evidence manifest per run.

### 2) KPI Contract Must Be Frozen Before Compute Spend
- **Observed:** KPI expectation drift happens when stakeholder question and executor output schema are not aligned before submit.
- **Practice:** Freeze acceptance schema to architect baseline metrics (`Topo_SNR`, `Orthogonality`, `Phys_Alignment`, `Model_Alignment`, `Vector_Alignment`) before submit.

### 3) Effective Sample Budget Must Be Gated Upfront
- **Observed:** Physics gates reduced usable training rows drastically versus base matrix scale.
- **Practice:** Add hard preflight thresholds for `mask_rows/base_rows` and `total_training_rows`; abort early when below floor.

### 4) Executed Payload Provenance Must Be Immutable
- **Observed:** Root-cause speed depends on proving exactly which cloud payload code ran.
- **Practice:** Store executed source snapshots + SHA256 in every evidence package; treat missing hash manifest as audit-incomplete.

### 5) Phase-Level Observability Prevents Silent Cost Burn
- **Observed:** State-only monitoring (`RUNNING`) hides semantic stalls and phase deadlocks.
- **Practice:** Enforce milestone-based watchdog (`download`, `load`, `dedup`, `sort`, `prepare`, `evaluate`) with timeout-based auto-cancel.

---

## 2026-03-07 | The All-Zero Smoke Trap (A P0 Validation Failure)

**Cost:** Multiple smoke cycles, probe cycles, and audit cycles across both the pre-speed route and the speed route.
**Outcome:** We temporarily mistook successful process completion for mathematical validation.

### What actually went wrong

1. **Stage2 was computing on the wrong trajectory order.**
- The defect was not in Stage1 raw parquet.
- The ETL -> kernel interface broke symbol/date continuity before rolling physics ran.
- This collapsed `topo_area`, `topo_energy`, `epiplexity`, `is_signal`, and `singularity_vector` to zero.

2. **Historical smoke design was too weak.**
- Earlier smokes proved that the pipeline could finish.
- They did not prove that the canonical V64.3 signal chain was non-degenerate.
- That allowed an `all-zero` chain to hide in plain sight.

3. **A good fail-fast idea was initially placed at the wrong granularity.**
- The first remediation smoke failed because a file-validity gate was applied at the 50-symbol worker-batch level.
- This created false negatives and delayed the real proof.

4. **Implicit defaults can silently invalidate a targeted validation.**
- `forge_base_matrix.py` defaulted to `--years=2023,2024`.
- The hot-week proof window was in `2025`.
- Without explicit year scope, valid files were filtered out and the run looked broken for the wrong reason.

### Permanent lessons

1. **A smoke is not valid unless it proves non-degenerate canonical signal activation.**
- Required minimum proof now includes non-zero:
  - `epiplexity`
  - `topo_area`
  - `topo_energy`
  - `singularity_vector`
  - `is_signal`

2. **Integration defects can have mathematical consequences.**
- Even when the canonical math core is approved, a bad ordering contract can make the runtime output mathematically meaningless.

3. **Fail-fast gates must align with the scheduler's unit of failure.**
- File/input scope and worker-batch scope are not interchangeable.

4. **Targeted smoke windows must declare year scope, path scope, and ordering assumptions explicitly.**
- No hidden CLI defaults.
- No assumed input contracts.

5. **Preserve both routes until root cause is known.**
- The correct move was to keep both the pre-speed route and the speed route alive until the `all-zero` root cause was proven.

### Required pre-submit checklist for future V64+ smoke runs

1. Prove the canonical chain is non-zero at Stage2 before running forge/training/backtest.
2. Fail fast if ordering cannot be proven or repaired.
3. Make year scope explicit for any non-baseline window.
4. Treat `all-zero` as a `P0` defect candidate, not as a neutral smoke result.
