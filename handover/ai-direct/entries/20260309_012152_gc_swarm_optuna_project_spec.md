---
entry_id: 20260309_012152_gc_swarm_optuna_project_spec
task_id: TASK-V643-GC-SWARM-OPTUNA-REVIVAL-SPEC
timestamp_local: 2026-03-09 01:21:52 +0000
timestamp_utc: 2026-03-09 01:21:52 +0000
operator: Codex
role: architect
branch: main
status: proposed
---

# Project Spec: V643-GC-SWARM-OPTUNA-REVIVAL

## 1. Objective

- Restore the original cloud value proposition of OMEGA on current `v643` code:
  - genuine cloud-parallel XGBoost optimization
  - not just single remote training offload
- Consume one immutable train-only base matrix for `2023,2024`.
- Define two separate holdout base-matrix artifacts:
  - one for `2025`
  - one for `2026-01`
- Produce a ranked Optuna leaderboard and a final deterministic champion retrain.
- Preserve strict holdout isolation:
  - training/optimization: `2023,2024`
  - holdout/backtest: `2025` and `2026-01`

## 2. Why This Project Exists

The baseline train that just completed proves the Stage3 corpus is now usable, but it also proves the current cloud path is too weak:

- active `tools/run_vertex_xgb_train.py` is a one-shot single-model trainer
- active `tools/submit_vertex_sweep.py` submits one `replicaCount=1` Vertex custom job
- active `tools/stage3_full_supervisor.py` wires only that single-train path

That is managed offload, not cloud-parallel optimization.

## 3. Historical Authority

The previous cloud rationale is not ambiguous:

1. Constitution:
   - `OMEGA_CONSTITUTION.md` reserves cloud for `XGBoost swarm optimization via compressed .parquet on GCS`
2. `v60` capacity/cost playbook:
   - swarm optimize was a distinct stage with its own machine/spot policy
3. `v62` watchdog:
   - explicitly launched `v60_swarm_xgb.py --min-samples 50000 --n-trials 10`
4. Archived implementation:
   - `archive/tools/submit_swarm_optuna.py` launched many independent jobs
   - `archive/tools/swarm_xgb.py` ran Optuna studies locally inside each worker over one in-memory base matrix

So the historical lesson is:

- the useful cloud pattern was horizontal fan-out across many independent workers
- not multi-replica distributed XGBoost
- not raw-L2 ETL on cloud

## 4. v643 Compatibility Decisions

This revival must preserve current canonical governance, not revive all old behavior blindly.

### 4.1 Keep

- edge/cloud airgap:
  - raw `Feature_L2` stays local
  - cloud sees only a staged train-only base matrix parquet
- run-pinned code bundles
- single-replica workers
- spot-preferred scheduling with bounded retry
- immutable train/backtest split

### 4.2 Do Not Revive

- archived joint search over physics gates and XGBoost params
- archived random CV pattern via generic `xgb.cv` across mixed dates
- any workflow that requires rerunning ETL per trial

Reason:

- current canonical governance explicitly treats Stage3 physical gates as fixed runtime semantics, not ML hyperparameters
- current active scripts emit `stage3_param_contract=canonical_v64_1`

## 5. Canonical Constraints

### 5.1 Frozen canonical parameters

The project must keep these fixed unless a separate math-governance mission is opened:

- `signal_epi_threshold`
- `singularity_threshold`
- `srl_resid_sigma_mult`
- `topo_energy_min`

### 5.2 Search space

Phase-1 search space is XGBoost-only. Recommended initial knobs:

- `max_depth`
- `learning_rate`
- `subsample`
- `colsample_bytree`
- `min_child_weight`
- `gamma`
- `reg_lambda`
- `reg_alpha`
- `num_boost_round`

Optional later knobs:

- class weighting / positive weighting
- deterministic multi-seed stability reruns for top candidates

### 5.3 Data isolation

- optimization input:
  - the completed `2023,2024` train-only base matrix only
- final retrain:
  - same `2023,2024` base matrix
- holdout:
  - `2025` and `2026-01` are excluded from all Optuna scoring and champion selection
- these holdout periods must be forged as separate Stage3 artifacts, not appended into the training base matrix

Important current limitation:

- active backtest entrypoints are year-only
- `2026-01` cannot be expressed through current `--backtest-years`
- any later holdout evaluation must use an explicit date-scoped manifest or prefix wrapper

### 5.4 Required Stage3 artifact partition

The project must maintain three distinct Stage3 artifacts:

1. Training artifact:
   - `base_matrix_train_2023_2024.parquet`
2. Outer holdout artifact:
   - `base_matrix_holdout_2025.parquet`
3. Final canary artifact:
   - `base_matrix_holdout_2026_01.parquet`

Rules:

- Optuna and champion selection may read only artifact 1
- artifact 2 may be used only for outer holdout evaluation after champion selection
- artifact 3 may be used only for the final release-canary check
- if artifact 2 is used to revise search space or champion logic, then it ceases to be holdout evidence and the protocol must be re-declared explicitly
- artifact 3 must remain the last untouched evaluation slice

### 5.5 Generation order

Required sequence:

1. Build or confirm `base_matrix_train_2023_2024.parquet`
2. Build `base_matrix_holdout_2025.parquet`
3. Build `base_matrix_holdout_2026_01.parquet` through explicit date-scoped file selection
4. Run cloud optimization only on artifact 1
5. Run outer holdout evaluation on artifact 2
6. If artifact 2 is accepted, retrain the champion on the chosen final training horizon
7. Run the last untouched canary check on artifact 3

## 6. Proposed Architecture

### 6.1 Controller/orchestrator

Add a new active launcher in `tools/`, for example:

- `tools/launch_vertex_swarm_optuna.py`

Responsibilities:

- stage or verify one immutable base-matrix URI
- stage one run-pinned code bundle URI
- launch `N` independent Vertex workers
- prefer `--spot`
- retry each failed/preempted worker at most once on on-demand
- collect result URIs
- aggregate leaderboard
- select champion
- optionally trigger final retrain

### 6.2 Worker payload

Add a new active payload in `tools/`, for example:

- `tools/run_optuna_sweep.py`

Responsibilities:

- download the run-pinned code bundle
- download the immutable base matrix
- load it into RAM once
- materialize the temporal split exactly once:
  - train rows = `2023`
  - validation rows = `2024`
- hard-assert temporal separation in code before any trial starts:
  - `max(train_date) < min(val_date)`
- build `xgb.DMatrix` objects exactly once outside the Optuna trial loop and reuse them across all trials on that worker
- run `n_trials_per_worker` Optuna trials locally
- score with temporal validation only
- emit:
  - `study_summary.json`
  - `trials.jsonl` or `trials.parquet`
  - frozen canonical-gate fingerprint for that worker
  - validation metrics including AUC plus alpha/excess-return proxy diagnostics
  - optional diagnostic metrics JSON

### 6.3 Aggregation

Add a lightweight aggregator, for example:

- `tools/aggregate_vertex_swarm_results.py`

Responsibilities:

- merge per-worker trial tables
- verify all workers used the same frozen canonical-gate contract
- rank by objective and tie-breakers
- if validation AUC delta between candidates is below a fixed epsilon threshold, prefer the simpler model:
  - lower `max_depth`
  - lower `num_boost_round`
- enforce minimum trial completeness
- emit a single leaderboard manifest and champion params JSON

### 6.4 Final champion retrain

Reuse the active training payload:

- `tools/run_vertex_xgb_train.py`

But use it only after champion selection, with:

- frozen canonical Stage3 gates
- winning XGBoost params injected
- full `2023,2024` base matrix as training input

## 7. Validation Strategy

The revived swarm must not use non-temporal random folds as the authoritative score.

Required Phase-1 scoring plan:

- train split:
  - all rows from `2023`
- validation split:
  - all rows from `2024`
- mandatory runtime assertion:
  - `max(train_date) < min(val_date)`

Allowed Phase-2 enhancement:

- time-ordered rolling validation inside `2023,2024`
- but still never mixing future rows into past training folds

Recommended objective:

- primary:
  - validation AUC on the temporal holdout inside `2023,2024`
- secondary guards:
  - no collapsed sample set
  - required signal-chain columns present
  - deterministic artifact logging for every trial
  - validation alpha / excess-return proxy diagnostics logged for every trial
  - explicit champion tie-breaker that penalizes unnecessary model complexity when score deltas are negligible

## 8. Runtime Policy

### 8.1 Concurrency model

- parallelism is job-level, not replica-level
- each Vertex worker is `replicaCount=1`
- scale by number of workers

### 8.2 Spot policy

- default launch mode: spot-preferred
- fallback:
  - one explicit on-demand retry per failed/preempted worker
- no infinite retry loops

### 8.3 Machine policy

Start with a quota-aware pilot in `us-central1`:

- pilot worker class:
  - `n2-standard-16`
- if memory telemetry shows pressure:
  - promote optimization workers to `n2-highmem-16`

Reason:

- the current baseline train succeeded on `n2-standard-16`
- but historical cloud lessons require respecting real Vertex capacity/quota behavior, not assumed GCE limits

## 9. Bucket and URI Governance

This project must fix bucket authority before implementation is considered complete.

Current mismatch:

- active supervisor still points to `gs://omega_central/...`
- live successful staging in this session used `gs://omega_v52_central/...`

Required rule:

- define one authoritative active staging bucket for:
  - base matrix
  - code bundles
  - Optuna payloads
  - worker outputs
  - leaderboard artifacts

Until `omega_central` actually exists, the live implementable authority is:

- `gs://omega_v52_central`

## 10. File Scope

### In scope

- `tools/submit_vertex_sweep.py`
- `tools/run_vertex_xgb_train.py`
- new active swarm launcher/payload/aggregator files under `tools/`
- tests for:
  - dataset isolation
  - worker output aggregation
  - champion param handoff
- handover docs

### Out of scope

- raw Stage1/Stage2 recompute
- changing `omega_core/*` math
- turning cloud optimization into distributed multi-replica XGBoost
- final production backtest implementation for `2025 + 2026-01`

## 11. Acceptance Criteria

### Pilot acceptance

1. At least `4` Vertex workers are simultaneously active.
2. Spot launch works end-to-end for the pilot.
3. At least one forced fallback path is validated:
   - preempted or failed worker retried once on on-demand
4. Aggregate completed trials are non-trivial:
   - at least `40` completed trials across workers
5. Leaderboard artifact exists and ranks trials deterministically.
6. Every worker proves temporal isolation in code:
   - emitted metadata confirms `max(train_date) < min(val_date)`
7. Every worker proves fixed-matrix reuse:
   - `dtrain` / `dval` are constructed once per worker, not once per trial
8. The project has distinct materialized Stage3 artifacts for:
   - `2023,2024`
   - `2025`
   - `2026-01`

### Full project acceptance

1. The system demonstrates real cloud fan-out:
   - target `8+` concurrent workers
2. The system completes a materially larger search than a local one-shot baseline:
   - target `100+` completed trials aggregate
3. Champion params are exported as a stable JSON artifact.
4. Final deterministic retrain on full `2023,2024` completes successfully.
5. No train/holdout contamination is introduced.
6. Aggregation proves all completed workers used an identical frozen canonical-gate fingerprint.
7. Leaderboard includes:
   - validation AUC
   - alpha / excess-return proxy diagnostics
   - explicit complexity tie-break metadata
8. Outer holdout evaluation is run only against `base_matrix_holdout_2025.parquet`.
9. Final canary evaluation is run only against `base_matrix_holdout_2026_01.parquet`.
10. Handover records exact:
   - bucket paths
   - worker counts
   - spot/on-demand outcomes
   - total/completed/pruned trials
   - champion params
   - final model URI

## 12. Fail-Fast Conditions

- Any design that uploads raw L2 to cloud: reject.
- Any design that reintroduces physics-gate search without explicit Owner approval: reject.
- Any design that uses non-temporal mixed-date CV as the authoritative score: reject.
- Any worker implementation that rebuilds train/validation `DMatrix` inside each Optuna trial: reject.
- Any worker implementation that lacks a hard temporal split assertion `max(train_date) < min(val_date)`: reject.
- Any aggregation result that mixes workers with inconsistent frozen canonical-gate fingerprints: reject.
- Any design that evaluates `2025` or `2026-01` from the training base matrix instead of separate holdout artifacts: reject.
- Any design that assumes `gs://omega_central/...` works without verifying bucket existence: reject.
- Any design that cannot prove real concurrent Vertex workers: reject.

## 13. Recommended Implementation Order

1. Fix bucket authority and make it explicit in one active config path.
2. Reactivate an Optuna payload under `tools/` with temporal validation.
3. Add a swarm launcher that fans out many single-replica workers using the existing submitter.
4. Add result aggregation and champion export.
5. Run a small pilot swarm.
6. Scale to full swarm.
7. Build and verify `base_matrix_holdout_2025.parquet`.
8. Build and verify `base_matrix_holdout_2026_01.parquet`.
9. Retrain champion on the approved final training horizon.
10. Run outer holdout and final canary in that order.

## 14. Final Verdict

This project is worth doing.

But only if it restores the cloud property that local cannot match:

- many concurrent independent optimization workers
- with spot-aware economics
- over one immutable train-only base matrix

If it degenerates back into one remote training job, it is not fulfilling the original cloud design intent.
