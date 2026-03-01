# OMEGA v6.0 Validation Results (v60 Run, Evidence-Only)

## 1. Scope
- Target standard: `audit/v6.md`
- Target run package: `audit/runtime/v60_factual_evidence/`
- Target implementation files:
  - `config.py`
  - `omega_core/omega_etl.py`
  - `omega_core/omega_etl_ashare.py`
  - `omega_core/trainer.py`
  - `tools/run_vertex_xgb_train.py`
  - `orchestrator.py`
- Date context of run artifacts (UTC): 2026-02-19 to 2026-02-20

## 2. Validation Rule Applied
- Phase requirements are taken from `audit/v6.md:73`, `audit/v6.md:79`, `audit/v6.md:85`.
- Full validation is granted only when all mandatory Phase 1/2/3 items are directly evidenced by code and/or runtime artifacts.
- If any mandatory item has no direct evidence in this run package, result is `NOT VALIDATED (full sign-off)`.

## 3. Source Integrity (Evidence File Fingerprints)
From `audit/runtime/v60_factual_evidence/source_file_sha256.txt`:

```text
ec6040680a625c423b8c475ce8c1db969a4ffdfce630ee29ac136f57f883d873  audit/runtime/v60_factual_evidence/source_tools_v60_build_base_matrix.py
bb1b6eee6616f910d0edc44ec805ca931b3abbcbf84df46c86ece1901484ce25  audit/runtime/v60_factual_evidence/source_tools_v60_swarm_xgb.py
d67f0328d058cedec50ca83fd99f6e9ebbe3d0438443cc7fe02509f7a1659c6e  audit/runtime/v60_factual_evidence/source_tools_run_vertex_xgb_train.py
f6a32966668988726e2f79cefefed879aee0ece02f1b5c82940b80838d393d0e  audit/runtime/v60_factual_evidence/source_tools_run_cloud_backtest.py
2dbaab8127a5cf8a0af8474614ec1b3db140a20f9537c3e8124a6ee29c385ae3  audit/runtime/v60_factual_evidence/source_omega_core_trainer.py
```

From `audit/runtime/v60_factual_evidence/source_file_line_counts.txt`:

```text
      24 audit/runtime/v60_factual_evidence/source_tools_v60_build_base_matrix.py
     283 audit/runtime/v60_factual_evidence/source_tools_v60_swarm_xgb.py
     243 audit/runtime/v60_factual_evidence/source_tools_run_vertex_xgb_train.py
     413 audit/runtime/v60_factual_evidence/source_tools_run_cloud_backtest.py
     615 audit/runtime/v60_factual_evidence/source_omega_core_trainer.py
```

## 4. End-to-End v60 Run Facts

### 4.1 Framing and Upload Facts
From `audit/runtime/v60_factual_evidence/autopilot_aa8abb7.status.json`:

```json
{
  "windows_expected": 263,
  "linux_expected": 484,
  "frame": {
    "linux_done": 484,
    "windows_done": 263,
    "probe_ok": true,
    "updated_at": "2026-02-19 10:59:52"
  },
  "upload": {
    "gcs_counts": {
      "linux1": 484,
      "windows1": 263,
      "checked_at": "2026-02-19 11:00:00"
    }
  }
}
```

### 4.2 Base Matrix Facts
From `audit/runtime/v60_factual_evidence/base_matrix_resume_aa8abb7.meta.json`:

```json
{
  "mode": "local_ticker_sharding",
  "input_file_count": 40,
  "raw_rows": 7466620,
  "base_rows": 5780139,
  "symbols_total": 5576,
  "batch_count": 112,
  "worker_count": 8,
  "seconds": 705.91,
  "dtype_invariants": {
    "strict_float64_required": true,
    "required_float_dtype": "Float64",
    "forbidden_float_dtypes_detected": false
  }
}
```

Local parquet schema check on `artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix.parquet`:
- row count: `5,780,139`
- column count: `25`
- includes columns: `is_physics_valid`, `t1_fwd_return`, `bar_duration_ms`, `symbol`, `date`, `time_end`

### 4.3 Optimization Facts
From `audit/runtime/v60_factual_evidence/swarm_best_20260219-030000_aa8abb7.json`:

```json
{
  "status": "completed",
  "best_value": 0.6101452643370191,
  "n_trials": 50,
  "n_completed": 20,
  "best_params": {
    "peace_threshold": 0.5253567667772991,
    "srl_resid_sigma_mult": 1.9773888188507172,
    "topo_energy_sigma_mult": 5.427559578121958,
    "max_depth": 5,
    "learning_rate": 0.006525909043483982,
    "subsample": 0.9382970275902356,
    "colsample_bytree": 0.7855991276821759
  }
}
```

Vertex job state from `audit/runtime/v60_factual_evidence/job_8392580415252070400.describe.json`:
- `state=JOB_STATE_SUCCEEDED`
- `machineType=e2-highmem-16`

### 4.4 Training Facts
From `audit/runtime/v60_factual_evidence/train_metrics_20260219-125410_78e36d9.json`:

```json
{
  "status": "completed",
  "base_rows": 5780139,
  "mask_rows": 2188,
  "total_training_rows": 2067,
  "seconds": 1.04,
  "job_id": "6022297228557680640",
  "model_uri": "gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl"
}
```

Vertex job state from `audit/runtime/v60_factual_evidence/job_6022297228557680640.describe.json`:
- `state=JOB_STATE_SUCCEEDED`
- `machineType=n2-standard-16`

### 4.5 Backtest Facts
From `audit/runtime/v60_factual_evidence/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`:

```json
{
  "status": "completed",
  "files_used": 263,
  "day_span_used": {
    "count": 263,
    "first": "20250102",
    "last": "20260130"
  },
  "total_proc_rows": 8907595,
  "seconds": 1170.03,
  "worker_plan": {
    "cpu_total": 80,
    "architecture": "global_causal_materialization",
    "reuse_precomputed_physics": true
  },
  "summary": {
    "Topo_SNR": 10.885431366882955,
    "Orthogonality": -0.0448054206835012,
    "Phys_Alignment": 0.5011822897884255,
    "Model_Alignment": 0.49742754220434177,
    "Vector_Alignment": 0.49742754220434177
  }
}
```

#### 4.5.1 Model-Alignment Definition and Threshold Check
- Metric values (from Section 4.5 JSON):
  - `Topo_SNR=10.885431366882955`
  - `Orthogonality=-0.0448054206835012`
  - `Phys_Alignment=0.5011822897884255`
  - `Model_Alignment=0.49742754220434177`
- `Model_Alignment` implementation definition (code evidence):
  - High-epiplexity subset is selected by `epi >= q80` where `epi_q = quantile(epi, 0.8)` in `omega_core/trainer.py:450` and `omega_core/trainer.py:451`.
  - Alignment is computed as equality rate between model direction sign and forward-return sign in `omega_core/trainer.py:491`.
- Validation threshold and pass/fail logic:
  - Threshold is `vector_alignment_min=0.6` in `config.py:696`.
  - DoD check requires `align_metric > vector_alignment_min` in `omega_core/trainer.py:560` and `omega_core/trainer.py:562`.
  - Current `Model_Alignment=0.49742754220434177`, therefore this condition is not satisfied.
  - Absolute distance to `0.5` is `0.00257245779565823`.

Vertex job state from `audit/runtime/v60_factual_evidence/job_1959559432727691264.describe.json`:
- `state=JOB_STATE_SUCCEEDED`
- `machineType=n2-highmem-80`

### 4.6 Backtest Failure/Recovery Timeline Facts
From `audit/runtime/v60_factual_evidence/job_timeline_selected.txt` and `audit/runtime/v60_factual_evidence/job_describe_key_fields.txt`:
- Failed jobs due memory:
  - `6324251159091478528` (`n2-standard-80`) `JOB_STATE_FAILED`, error code `8`, message `Replicas low on memory`
  - `1475563210273718272` (`n2-highmem-64`) `JOB_STATE_FAILED`, error code `8`, message `Replicas low on memory`
  - `3366793578792615936` (`n2-highmem-80`) `JOB_STATE_FAILED`, error code `8`, message `Replicas low on memory`
- Cancelled intermediate:
  - `6945888645156962304` `JOB_STATE_CANCELLED`
- Final successful backtest:
  - `1959559432727691264` (`n2-highmem-80`) `JOB_STATE_SUCCEEDED`

## 5. v6 Requirement-to-Evidence Matrix
Requirements source lines: `audit/v6.md:73-88`.

| Requirement (`audit/v6.md`) | Evidence | Status |
|---|---|---|
| Phase 1: A-share session times (`09:30-11:30`, `13:00-15:00`) | `config.py:756-765` defines A-share session windows; `omega_core/omega_etl.py:105-112` applies session filter with morning/afternoon windows | PASS |
| Phase 1: Lunch break paused in causal volume time | `omega_core/omega_etl.py:148-157` folds lunch gap (`otherwise(morning_len)`); `omega_core/omega_etl.py:276-279` uses folded elapsed fraction | PASS |
| Phase 1: Limit-up/down singularity mask | `config.py:777-780` defines `limit_singularity_eps` and `t_plus_1_horizon_days`; `omega_core/omega_etl.py:309-317` creates singularity mask from `bid_v1/ask_v1`; base matrix includes `is_physics_valid` | PASS |
| Phase 1: 3-second snapshot aggregation handling | Requirement text at `audit/v6.md:75` and `audit/v6.md:43`; in this run package no direct runtime field/log proves snapshot interval execution path. Keyword scan over `audit/runtime/v60_factual_evidence/job_*.logs.json` for `3-second|snapshot` returned no hits; produced bars show median `bar_duration_ms` of `333000` (sample frame) and `321000` (base matrix) | NOT EVIDENCED |
| Phase 2: Replace linear model with XGBoost/LightGBM | `tools/run_vertex_xgb_train.py:146-167` builds `xgb.DMatrix` and trains via `xgb.train`; training job `6022297228557680640` succeeded | PASS |
| Phase 2: Epistemic sample weighting `epiplexity * log1p(abs(topo_area))` | `tools/run_vertex_xgb_train.py:130` computes `weights_clean = (epi * np.log1p(np.abs(topo_area)))[physics_mask]` | PASS |
| Phase 2: T+1 target shift | `omega_core/trainer.py:92-122` shifts daily close with `shift(-t1_days)` and joins as `t1_close`; base matrix includes `t1_fwd_return`; backtest log contains `Valid processed rows after T+1 causality shift: 8907595` (`backtest_success_key_lines.txt`) | PASS |
| Phase 3: Orchestrator dispatch from Mac to workers | `orchestrator.py:129-138` dispatch command; `orchestrator.py:47-48` SSH transport; `orchestrator.py:175-178` CLI `dispatch-frame` | PASS |
| Phase 3: GCS sync and Vertex trigger pipeline | `orchestrator.py:141-149` `sync-gcs`; `orchestrator.py:152-168` `trigger-vertex`; actual GCS outputs and Vertex jobs present in evidence package | PASS |

## 6. Quantitative Runtime Evidence for Snapshot-Item Assessment
Local measured outputs from produced artifacts:

```text
Frame file: artifacts/runtime/v52/frames/host=windows1/20230104_aa8abb7.parquet
rows=180398
bar_min=26000
bar_median=333000
bar_q90=829000
bar_max=19791009

Base matrix: artifacts/runtime/v60/base_matrix/aa8abb7/base_matrix.parquet
rows=5780139
bar_min=25000
bar_median=321000
bar_q90=804000
bar_max=19797006
```

Keyword scan result over v60 factual logs/json:

```text
pattern: 3-second|3 second|snapshot|snapshots
result: no matches
```

## 7. Validation Decision
- Decision by rule in Section 2: **NOT VALIDATED (full v6.0 sign-off)**
- Factual blocker: mandatory Phase 1 item for `3-second L2 snapshot aggregation handling` is **not directly evidenced** by this run package.

## 8. Artifact Registry (Direct Repo Paths)
- Standard: `audit/v6.md`
- Report: `audit/v60_v6_validation_results.md`
- Full evidence directory: `audit/runtime/v60_factual_evidence/`
- Key files:
  - `audit/runtime/v60_factual_evidence/autopilot_aa8abb7.status.json`
  - `audit/runtime/v60_factual_evidence/base_matrix_resume_aa8abb7.meta.json`
  - `audit/runtime/v60_factual_evidence/swarm_best_20260219-030000_aa8abb7.json`
  - `audit/runtime/v60_factual_evidence/train_metrics_20260219-125410_78e36d9.json`
  - `audit/runtime/v60_factual_evidence/backtest_metrics_global_causal_rewrite_n2highmem80_reusephysics_dw16_20260220-024848.json`
  - `audit/runtime/v60_factual_evidence/job_timeline_selected.txt`
  - `audit/runtime/v60_factual_evidence/job_describe_key_fields.txt`
  - `audit/runtime/v60_factual_evidence/backtest_success_key_lines.txt`
  - `audit/runtime/v60_factual_evidence/training_log_key_lines.txt`
  - `audit/runtime/v60_factual_evidence/optimization_log_key_lines.txt`
  - `audit/runtime/v60_factual_evidence/source_file_sha256.txt`
