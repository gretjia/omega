# v60 Backtest Cloud Runtime Audit (For External Auditor)

- Audit file: `audit/v60_backtest_audit.md`
- Generated at: `2026-02-19 22:29:02 CST (+0800)`
- Auditor: Codex (read/analysis only; no stop/cancel action executed in this audit)
- Target run hash: `aa8abb7`
- Target backtest job: `projects/269018079180/locations/us-central1/customJobs/4745526734198145024`
- Scope: Diagnose why current cloud backtest is progressing with `used=0 rows=0` and assess failure risk, using direct source code + direct cloud/runtime data.

---

## 1) Executive Verdict

### 1.1 Verdict
Current backtest job (`4745526734198145024`) is **high-probability failure** due to deterministic data-preparation emptiness, not OOM.

### 1.2 Confidence
- Root-cause confidence: **Very High** (multiple independent evidence chains converge)
- Failure-probability estimate: **>99%** (if code path and data scope remain unchanged)

### 1.3 Immediate operational constraint
Per request, this audit did **not** cancel/stop/restart the current cloud job. This file is evidence-only.

---

## 2) Cloud Job Identity and Live Runtime Evidence

### 2.1 Direct job metadata (`gcloud ai custom-jobs describe`)

Command:
```bash
gcloud ai custom-jobs describe 4745526734198145024 \
  --region=us-central1 \
  --project=gen-lang-client-0250995579 \
  --format=json
```

Raw output (excerpt, key fields):
```json
{
  "createTime": "2026-02-19T13:10:48.617413Z",
  "displayName": "omega-v60-run_cloud_backtest-20260219-211045",
  "name": "projects/269018079180/locations/us-central1/customJobs/4745526734198145024",
  "startTime": "2026-02-19T13:13:42Z",
  "state": "JOB_STATE_RUNNING",
  "updateTime": "2026-02-19T13:13:52.211001Z"
}
```

### 2.2 Container launch script confirms exact payload file

Command:
```bash
gcloud ai custom-jobs describe 4745526734198145024 \
  --region=us-central1 \
  --project=gen-lang-client-0250995579 \
  --format='value(jobSpec.workerPoolSpecs[0].containerSpec.args[0])'
```

Raw output (exact execution script):
```bash
set -euxo pipefail
python3 -m pip install --quiet google-cloud-storage
python3 - <<'PY'
from google.cloud import storage
import shutil

def dl(uri: str, out: str) -> None:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)

dl("gs://omega_v52_central/omega/staging/code/omega_core_20260219-125410_78e36d9.zip", "omega_core.zip")
dl("gs://omega_v52/staging/code/payloads/omega-v60-run_cloud_backtest-20260219-211045_run_cloud_backtest.py", "payload.py")
shutil.unpack_archive("omega_core.zip", extract_dir=".")
PY
python3 -u payload.py --code-bundle-uri=gs://omega_v52_central/omega/staging/code/omega_core_20260219-125410_78e36d9.zip '--data-pattern=gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet' --test-years=2025,2026 --test-ym=2025,202601 --max-files=0 --max-rows-per-file=0 --workers=1 --workers-min=1 --workers-max=1 --workers-start=1 --workers-mem-headroom-gb=24 --workers-est-mem-gb=6 --model-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl --output-uri=gs://omega_v52_central/omega/staging/backtest/v6/20260219-125410_78e36d9/backtest_metrics_retry_highmem16_w1.json --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958
```

---

## 3) Runtime Behavior Evidence (Cloud Logging)

### 3.1 Progress logs keep advancing, but `used=0 rows=0`

Command:
```bash
gcloud logging read \
 'resource.type="ml_job" AND resource.labels.job_id="4745526734198145024" AND textPayload:"Backtest progress"' \
 --project=gen-lang-client-0250995579 --limit=8 \
 --format='value(timestamp,textPayload)'
```

Raw output:
```text
2026-02-19T14:26:04.154323046Z	2026-02-19 14:26:04,097 [INFO] Backtest progress files=60/263 used=0 rows=0 inflight=0 target=1 rss_gb=5.51
2026-02-19T14:15:01.554928230Z	2026-02-19 14:15:01,363 [INFO] Backtest progress files=50/263 used=0 rows=0 inflight=0 target=1 rss_gb=5.50
2026-02-19T14:02:32.954718839Z	2026-02-19 14:02:32,933 [INFO] Backtest progress files=40/263 used=0 rows=0 inflight=0 target=1 rss_gb=5.00
2026-02-19T13:50:27.154454170Z	2026-02-19 13:50:26,993 [INFO] Backtest progress files=30/263 used=0 rows=0 inflight=0 target=1 rss_gb=4.96
2026-02-19T13:39:02.554377313Z	2026-02-19 13:39:02,455 [INFO] Backtest progress files=20/263 used=0 rows=0 inflight=0 target=1 rss_gb=4.87
2026-02-19T13:28:03.154076125Z	2026-02-19 13:28:03,015 [INFO] Backtest progress files=10/263 used=0 rows=0 inflight=0 target=1 rss_gb=3.95
```

### 3.2 Every processed file emits `empty_processed`

Command:
```bash
gcloud logging read \
 'resource.type="ml_job" AND resource.labels.job_id="4745526734198145024"' \
 --project=gen-lang-client-0250995579 --limit=25 \
 --format='value(timestamp,textPayload)'
```

Raw output (excerpt):
```text
2026-02-19T14:28:15.954816042Z	2026-02-19 14:28:15,862 [WARNING] Skip gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250526_aa8abb7.parquet: empty_processed
2026-02-19T14:27:19.354855322Z	2026-02-19 14:27:19,269 [WARNING] Skip gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250523_aa8abb7.parquet: empty_processed
2026-02-19T14:26:04.154310926Z	2026-02-19 14:26:04,096 [WARNING] Skip gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250521_aa8abb7.parquet: empty_processed
2026-02-19T14:24:57.754626090Z	2026-02-19 14:24:57,740 [WARNING] Skip gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250520_aa8abb7.parquet: empty_processed
...
2026-02-19T14:02:32.954705889Z	2026-02-19 14:02:32,933 [WARNING] Skip gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250403_aa8abb7.parquet: empty_processed
```

Interpretation: job is not hung; it is consuming files and systematically producing zero valid prepared rows.

---

## 4) Data-Scope Evidence (Selected Files Are Single-Day Shards)

### 4.1 Selected file set and host distribution

Raw output:
```text
selected_count= 263
host_distribution:
host=linux1 176
host=windows1 87
first_8:
gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250103_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250106_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250107_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250109_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250110_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250113_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250115_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=linux1/20250116_aa8abb7.parquet
first_windows:
gs://omega_v52_central/omega/omega/v52/frames/host=windows1/20250102_aa8abb7.parquet
last_8:
gs://omega_v52_central/omega/omega/v52/frames/host=windows1/20251224_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=windows1/20251230_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=windows1/20260107_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=windows1/20260113_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=windows1/20260116_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=windows1/20260119_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=windows1/20260122_aa8abb7.parquet
gs://omega_v52_central/omega/omega/v52/frames/host=windows1/20260128_aa8abb7.parquet
```

### 4.2 Sample-file reality: one file contains one trading day only

Raw output:
```text
file /tmp/20250103_aa8abb7.parquet
rows 230123
date_unique 1
date_minmax ('20250103', '20250103')
t_plus_1_horizon_days 1
```

This directly shows: each file is single-day, while labeling horizon requires next day (`t_plus_1_horizon_days=1`).

---

## 5) Controlled Reproduction on Real Production Files

### 5.1 Single-file reproduction (linux and windows)

Raw output:
```text
linux_20250103_raw_rows 230123 prepared_rows 0
windows_sample_raw_rows 248883 prepared_rows 0
```

### 5.2 Counterfactual proof (concatenate two adjacent days)

Raw output:
```text
single_day_rows 0
two_days_rows 64044
two_days_day1_rows 64044
two_days_day2_rows 0
```

This is the decisive experiment:
- same code,
- same thresholds,
- same data domain,
- only changed from single-day input to two-day concatenated input.

Result: prepared rows recover immediately (64044) when next-day context exists.

---

## 6) Source-Code Evidence (Line-Referenced)

### 6.1 Backtest consumes each URI independently and rejects empty prepared frames

File: `tools/run_cloud_backtest.py`

```text
266-280:
  df_raw = lazy.collect()
  if df_raw.height <= 0: return empty_raw
  df_proc = trainer._prepare_frames(df_raw, cfg)
  if df_proc.height <= 0: return empty_processed

395-396:
  if not per_file:
      raise RuntimeError("Backtest produced no valid processed frames.")
```

Direct line dump evidence:
```text
   266    def _consume(uri: str) -> dict:
   275            df_raw = lazy.collect()
   276            if df_raw.height <= 0:
   277                return {"ok": False, "source_uri": uri, "error": "empty_raw"}
   278            df_proc = trainer._prepare_frames(df_raw, cfg)
   279            if df_proc.height <= 0:
   280                return {"ok": False, "source_uri": uri, "error": "empty_processed"}
...
   395    if not per_file:
   396        raise RuntimeError("Backtest produced no valid processed frames.")
```

### 6.2 Trainer label construction requires T+1 day context

File: `omega_core/trainer.py`

- Build T+1 target with daily close shifted by `-t1_days`
- Then compute `close_fwd`, `ret_k`
- Then `drop_nulls` on these fields

Direct line dump evidence:
```text
    90    def _build_t_plus_one_targets(self, df: pl.DataFrame, cfg: L2PipelineConfig) -> tuple[pl.DataFrame, bool]:
    91        t1_days = int(max(0, getattr(cfg.micro, "t_plus_1_horizon_days", 0)))
...
   114            daily = daily.with_columns(pl.col("_day_close").shift(-t1_days).over(over_cols).alias("t1_close"))
   116            daily = daily.with_columns(pl.col("_day_close").shift(-t1_days).alias("t1_close"))
...
   151        if use_t1:
   154                    pl.col("t1_close").alias("close_fwd"),
   155                    (pl.col("t1_close") - pl.col("close")).alias("fwd_change"),
...
   195            .drop_nulls(subset=["close_valid", "ret_k", "sigma_ret", self.label_col, "t1_fwd_return"])
```

### 6.3 Configuration hardcodes T+1 horizon to 1 day

File: `config.py`

Direct line dump evidence:
```text
   772    @dataclass(frozen=True)
   773    class AShareMicrostructureConfig:
...
   780        t_plus_1_horizon_days: int = 1
```

---

## 7) Why Training Succeeded But Backtest Fails (Not Contradictory)

Training metrics (actual cloud artifact):
```json
{
  "status": "completed",
  "base_matrix_uri": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet",
  "base_rows": 5780139,
  "mask_rows": 2188,
  "total_training_rows": 2067,
  "seconds": 1.04,
  "job_id": "6022297228557680640"
}
```

Interpretation:
- Training uses pre-built **global base_matrix** (cross-day context already embedded), so valid rows exist.
- Backtest currently processes **single-day file in isolation**, so T+1 label fields become null and are dropped.

Therefore, train success + backtest empty is internally consistent.

---

## 8) Failure Mechanism (Deterministic Chain)

1. Backtest iterates one `YYYYMMDD_*.parquet` at a time (`_consume(uri)`).
2. For a single day file, `_build_t_plus_one_targets` cannot find next-day close (`t1_close` null).
3. `close_fwd/ret_k/t1_fwd_return` null.
4. `drop_nulls(...)` removes all rows.
5. `_consume` returns `empty_processed` for every file.
6. `per_file` remains empty to end-of-run.
7. `RuntimeError("Backtest produced no valid processed frames.")` is raised.

This chain has been proven both in code and in actual data experiments.

---

## 9) Cloud Runtime ETA Snapshot (as of audit time)

From progress logs:
- `files=10/263` at `13:28:03Z`
- `files=60/263` at `14:26:04Z`

Approx rate: ~`0.86 files/min`, remaining `203` files (at 60/263 checkpoint), implying ~3.9h additional runtime from that checkpoint before terminal state.

Given persistent `used=0 rows=0`, expected terminal state is failure-by-empty-data, not success.

---

## 10) Exact Cloud-Executing Backtest Source Code (Full Copy-Paste)

Per request, below is the **full file** currently pulled by the running cloud job:

- Source object URI: `gs://omega_v52/staging/code/payloads/omega-v60-run_cloud_backtest-20260219-211045_run_cloud_backtest.py`
- Object size: `18861 bytes` (from `gcloud storage ls -l`)
- Local copy path used in this audit: `/tmp/cloud_run_cloud_backtest_payload.py`
- SHA256: `fc4959907931252bd8a80ab8054d8e94d8397c186d534ff2ead6f07e02294daf`
- Equality check against workspace `tools/run_cloud_backtest.py`: `IDENTICAL: yes`

```python
#!/usr/bin/env python3
"""
OMEGA v6 cloud backtest payload.

Design constraints:
- Strict day-key split filtering (YYYYMMDD prefix in filename).
- Full-coverage defaults (`max-files=0`, `max-rows-per-file=0`).
- Lightweight runtime telemetry for unattended runs.
"""

from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import gc
import json
import logging
import math
import os
import pickle
import re
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import replace
from pathlib import Path

import numpy as np


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("omega_backtest")


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _download_file(gcs_uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.check_call(["gsutil", "cp", gcs_uri, str(local_path)])
        return
    except Exception:
        pass

    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))


def _upload_json(payload: dict, gcs_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    tmp = Path("backtest_metrics.json")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(tmp))


def _install_dependencies() -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "polars",
            "gcsfs",
            "fsspec",
            "scikit-learn",
            "numpy",
            "google-cloud-storage",
            "psutil",
            "xgboost",
        ]
    )


def _bootstrap_codebase(code_bundle_uri: str) -> None:
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())


def _extract_day_key(path_or_uri: str) -> str:
    name = str(path_or_uri).rsplit("/", 1)[-1]
    match = re.match(r"^(\d{8})_", name)
    return match.group(1) if match else ""


def _to_gcs_uri(item: str) -> str:
    s = str(item)
    return s if s.startswith("gs://") else f"gs://{s}"


def _day_summary(uris: list[str]) -> dict:
    days = sorted({d for d in (_extract_day_key(x) for x in uris) if d})
    if not days:
        return {"count": 0, "first": None, "last": None}
    return {"count": int(len(days)), "first": days[0], "last": days[-1]}


def _select_backtest_files(fs, data_pattern: str, test_years: list[str], test_ym: list[str], max_files: int) -> tuple[list[str], list[str]]:
    files = [_to_gcs_uri(x) for x in sorted(fs.glob(data_pattern))]
    filtered = []
    year_set = {str(y).strip() for y in test_years if str(y).strip()}
    ym_prefixes = [str(x).strip() for x in test_ym if str(x).strip()]

    for uri in files:
        day = _extract_day_key(uri)
        if not day:
            continue
        if year_set and day[:4] not in year_set:
            continue
        if ym_prefixes and not any(day.startswith(prefix) for prefix in ym_prefixes):
            continue
        filtered.append(uri)

    if max_files <= 0 or len(filtered) <= max_files:
        return filtered, list(filtered)

    # Uniformly sample across the full span to avoid head-only bias.
    idx = np.linspace(0, len(filtered) - 1, num=max_files, dtype=int).tolist()
    selected = [filtered[int(i)] for i in idx]
    return filtered, selected


def _load_model_payload(model_uri: str) -> tuple[object | None, object | None, list[str] | None]:
    if not model_uri:
        return None, None, None
    local_model = Path("omega_model.pkl")
    _download_file(model_uri, local_model)
    with local_model.open("rb") as f:
        payload = pickle.load(f)
    model = payload.get("model")
    scaler = payload.get("scaler")
    feature_cols = payload.get("feature_cols", payload.get("features"))
    return model, scaler, list(feature_cols) if feature_cols else None


def _apply_cfg_overrides(cfg, args: argparse.Namespace):
    sig = cfg.signal
    if args.peace_threshold is not None:
        sig = replace(sig, peace_threshold=float(args.peace_threshold))
    if args.srl_resid_sigma_mult is not None:
        sig = replace(sig, srl_resid_sigma_mult=float(args.srl_resid_sigma_mult))
    if args.topo_energy_sigma_mult is not None:
        sig = replace(sig, topo_energy_sigma_mult=float(args.topo_energy_sigma_mult))
    return replace(cfg, signal=sig)


def _resolve_worker_plan(args: argparse.Namespace, cpu_total: int, mem_total_gb: float) -> dict:
    requested = int(max(0, args.workers))
    min_workers = int(max(1, args.workers_min))
    if requested > 0:
        candidate_max = requested
    else:
        candidate_max = int(max(1, math.floor(float(cpu_total) * float(args.workers_cpu_frac))))

    if int(args.workers_max) > 0:
        candidate_max = min(candidate_max, int(args.workers_max))

    if float(args.workers_mem_headroom_gb) > 0 and float(args.workers_est_mem_gb) > 0:
        mem_budget = max(0.0, float(mem_total_gb) - float(args.workers_mem_headroom_gb))
        mem_cap = int(max(1, math.floor(mem_budget / float(args.workers_est_mem_gb)))) if mem_budget > 0 else 1
        candidate_max = min(candidate_max, mem_cap)

    max_workers = int(max(min_workers, candidate_max))
    if int(args.workers_start) > 0:
        start_workers = int(args.workers_start)
    else:
        start_workers = int(max(min_workers, math.ceil(max_workers * 0.35)))
    start_workers = int(min(max_workers, max(min_workers, start_workers)))

    return {
        "requested": requested,
        "min_workers": min_workers,
        "max_workers": max_workers,
        "start_workers": start_workers,
        "adaptive": bool(max_workers > min_workers and int(args.workers_adjust_step) > 0),
    }


def run_backtest(args: argparse.Namespace) -> dict:
    import gcsfs
    import polars as pl
    import psutil
    from config import L2PipelineConfig
    from omega_core.trainer import OmegaTrainerV3, evaluate_frames

    fs = gcsfs.GCSFileSystem()
    matched, selected = _select_backtest_files(
        fs=fs,
        data_pattern=args.data_pattern,
        test_years=list(args.test_years),
        test_ym=list(args.test_ym),
        max_files=int(max(0, args.max_files)),
    )
    if not matched:
        raise RuntimeError(
            f"No backtest files matched: data_pattern={args.data_pattern}, test_years={args.test_years}, test_ym={args.test_ym}"
        )

    logger.info(
        "Backtest file scope matched=%d selected=%d max_files=%d",
        len(matched),
        len(selected),
        int(max(0, args.max_files)),
    )

    cfg = _apply_cfg_overrides(L2PipelineConfig(), args)
    model, scaler, feature_cols = _load_model_payload(args.model_uri)

    metric_keys = ["Topo_SNR", "Orthogonality", "Phys_Alignment", "Model_Alignment", "Vector_Alignment"]
    weighted_sum = {k: 0.0 for k in metric_keys}
    total_rows = 0
    per_file: list[dict] = []
    used_uris: list[str] = []
    started = time.time()
    max_rows_per_file = int(max(0, args.max_rows_per_file))

    proc = psutil.Process(os.getpid())
    cpu_total = int(psutil.cpu_count(logical=True) or 1)
    mem_total_gb = float(psutil.virtual_memory().total / (1024 ** 3))
    worker_plan = _resolve_worker_plan(args=args, cpu_total=cpu_total, mem_total_gb=mem_total_gb)
    target_workers = int(worker_plan["start_workers"])
    min_workers = int(worker_plan["min_workers"])
    max_workers = int(worker_plan["max_workers"])
    adaptive = bool(worker_plan["adaptive"])
    adjust_step = int(max(1, args.workers_adjust_step))
    poll_sec = float(max(0.5, args.workers_poll_sec))

    logger.info(
        "Worker plan requested=%d min=%d max=%d start=%d adaptive=%s cpu_total=%d mem_total_gb=%.1f",
        int(worker_plan["requested"]),
        min_workers,
        max_workers,
        target_workers,
        adaptive,
        cpu_total,
        mem_total_gb,
    )

    thread_local = threading.local()

    def _ctx() -> dict:
        local = getattr(thread_local, "ctx", None)
        if local is None:
            local = {
                "trainer": OmegaTrainerV3(cfg),
                "model": model,
                "scaler": scaler,
                "feature_cols": feature_cols,
            }
            thread_local.ctx = local
        return local

    def _consume(uri: str) -> dict:
        df_raw = None
        df_proc = None
        try:
            local = _ctx()
            trainer = local["trainer"]
            lazy = pl.scan_parquet(uri)
            if max_rows_per_file > 0:
                lazy = lazy.head(max_rows_per_file)
            df_raw = lazy.collect()
            if df_raw.height <= 0:
                return {"ok": False, "source_uri": uri, "error": "empty_raw"}
            df_proc = trainer._prepare_frames(df_raw, cfg)
            if df_proc.height <= 0:
                return {"ok": False, "source_uri": uri, "error": "empty_processed"}
            metrics = evaluate_frames(
                df_proc,
                cfg,
                model=local["model"],
                scaler=local["scaler"],
                feature_cols=local["feature_cols"],
            )
            return {
                "ok": True,
                "source_uri": uri,
                "raw_rows": int(df_raw.height),
                "proc_rows": int(df_proc.height),
                "metrics": {k: float(metrics.get(k, float("nan"))) for k in metric_keys},
            }
        except Exception as exc:
            return {"ok": False, "source_uri": uri, "error": str(exc)}
        finally:
            del df_raw, df_proc
            gc.collect()

    def _apply(item: dict) -> None:
        nonlocal total_rows
        if not bool(item.get("ok")):
            logger.warning("Skip %s: %s", item.get("source_uri"), item.get("error", "unknown"))
            return

        weight = int(item.get("proc_rows", 0))
        total_rows += weight
        for key in metric_keys:
            value = item.get("metrics", {}).get(key)
            if value is None:
                continue
            if isinstance(value, float) and not math.isfinite(value):
                continue
            weighted_sum[key] += float(value) * weight

        per_file.append(
            {
                "source_uri": str(item.get("source_uri")),
                "raw_rows": int(item.get("raw_rows", 0)),
                "proc_rows": int(item.get("proc_rows", 0)),
                **{k: float(item.get("metrics", {}).get(k, float("nan"))) for k in metric_keys},
            }
        )
        used_uris.append(str(item.get("source_uri")))

    pending = list(selected)
    inflight: dict = {}
    completed = 0
    last_adjust_ts = time.time()
    psutil.cpu_percent(interval=None)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        while pending or inflight:
            if adaptive and (time.time() - last_adjust_ts) >= poll_sec:
                cpu_now = float(psutil.cpu_percent(interval=0.0))
                mem_now = psutil.virtual_memory()
                mem_available_gb = float(mem_now.available / (1024 ** 3))
                prev = target_workers
                if cpu_now >= float(args.workers_cpu_util_high) or mem_available_gb < float(args.workers_mem_headroom_gb):
                    target_workers = int(max(min_workers, target_workers - adjust_step))
                elif cpu_now <= float(args.workers_cpu_util_low) and mem_available_gb > (
                    float(args.workers_mem_headroom_gb) + float(args.workers_est_mem_gb)
                ):
                    target_workers = int(min(max_workers, target_workers + adjust_step))
                if prev != target_workers:
                    rss_gb = proc.memory_info().rss / float(1024 ** 3)
                    logger.info(
                        "Adaptive workers %d -> %d (cpu=%.1f%% avail=%.1fGB rss=%.2fGB inflight=%d pending=%d)",
                        prev,
                        target_workers,
                        cpu_now,
                        mem_available_gb,
                        rss_gb,
                        len(inflight),
                        len(pending),
                    )
                last_adjust_ts = time.time()

            while pending and len(inflight) < target_workers:
                uri = pending.pop(0)
                fut = pool.submit(_consume, uri)
                inflight[fut] = uri

            if not inflight:
                continue

            done, _ = wait(list(inflight.keys()), timeout=poll_sec, return_when=FIRST_COMPLETED)
            if not done:
                continue

            for fut in done:
                src = inflight.pop(fut, None)
                completed += 1
                try:
                    item = fut.result()
                except Exception as exc:
                    logger.warning("Skip %s: %s", src, exc)
                    continue
                _apply(item)

                if completed % 10 == 0 or completed == len(selected):
                    rss_gb = proc.memory_info().rss / float(1024 ** 3)
                    logger.info(
                        "Backtest progress files=%d/%d used=%d rows=%d inflight=%d target=%d rss_gb=%.2f",
                        completed,
                        len(selected),
                        len(per_file),
                        total_rows,
                        len(inflight),
                        target_workers,
                        rss_gb,
                    )

    if not per_file:
        raise RuntimeError("Backtest produced no valid processed frames.")

    summary = {}
    for key in metric_keys:
        summary[key] = float(weighted_sum[key] / total_rows) if total_rows > 0 else float("nan")

    result = {
        "status": "completed",
        "files_matched": int(len(matched)),
        "files_selected": int(len(selected)),
        "files_used": int(len(per_file)),
        "day_span_selected": _day_summary(selected),
        "day_span_used": _day_summary(used_uris),
        "total_proc_rows": int(total_rows),
        "seconds": round(time.time() - started, 2),
        "model_uri": args.model_uri or None,
        "data_pattern": args.data_pattern,
        "test_years": list(args.test_years),
        "test_ym": list(args.test_ym),
        "split_guard": {
            "enforced": True,
            "test_years": list(args.test_years),
            "test_ym": list(args.test_ym),
        },
        "overrides": {
            "peace_threshold": args.peace_threshold,
            "srl_resid_sigma_mult": args.srl_resid_sigma_mult,
            "topo_energy_sigma_mult": args.topo_energy_sigma_mult,
            "max_rows_per_file": int(max_rows_per_file),
            "max_files": int(max(0, args.max_files)),
        },
        "worker_plan": {
            "requested": int(worker_plan["requested"]),
            "min_workers": min_workers,
            "max_workers": max_workers,
            "start_workers": int(worker_plan["start_workers"]),
            "adaptive": adaptive,
            "cpu_total": cpu_total,
            "mem_total_gb": round(mem_total_gb, 2),
            "cpu_util_low": float(args.workers_cpu_util_low),
            "cpu_util_high": float(args.workers_cpu_util_high),
            "mem_headroom_gb": float(args.workers_mem_headroom_gb),
            "est_mem_per_worker_gb": float(args.workers_est_mem_gb),
        },
        "summary": summary,
        "per_file_count": int(len(per_file)),
        "per_file": per_file,
    }
    return result


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="OMEGA v6 cloud backtest payload")
    ap.add_argument("--code-bundle-uri", required=True, help="Run-pinned code bundle URI.")
    ap.add_argument("--data-pattern", default="gs://omega_v52/omega/v52/frames/host=*/*.parquet")
    ap.add_argument("--test-years", default="")
    ap.add_argument("--test-ym", default="")
    ap.add_argument("--model-uri", default="", help="Optional trained model pkl in GCS")
    ap.add_argument("--max-files", type=int, default=0, help="0 means full coverage.")
    ap.add_argument("--max-rows-per-file", type=int, default=0, help="0 means full file rows.")
    ap.add_argument("--output-uri", required=True, help="GCS json path (e.g. gs://bucket/path/backtest_metrics.json)")
    ap.add_argument("--peace-threshold", type=float, default=None)
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=None)
    ap.add_argument("--topo-energy-sigma-mult", type=float, default=None)
    ap.add_argument("--workers", type=int, default=0, help="0=auto, >0 explicit max workers.")
    ap.add_argument("--workers-min", type=int, default=1)
    ap.add_argument("--workers-max", type=int, default=0)
    ap.add_argument("--workers-start", type=int, default=0)
    ap.add_argument("--workers-cpu-frac", type=float, default=0.70)
    ap.add_argument("--workers-cpu-util-low", type=float, default=55.0)
    ap.add_argument("--workers-cpu-util-high", type=float, default=88.0)
    ap.add_argument("--workers-mem-headroom-gb", type=float, default=12.0)
    ap.add_argument("--workers-est-mem-gb", type=float, default=3.0)
    ap.add_argument("--workers-adjust-step", type=int, default=1)
    ap.add_argument("--workers-poll-sec", type=float, default=2.0)

    args = ap.parse_args()
    args.test_years = [x.strip() for x in str(args.test_years).split(",") if x.strip()]
    args.test_ym = [x.strip() for x in str(args.test_ym).split(",") if x.strip()]
    if not args.test_years:
        raise SystemExit("--test-years cannot be empty (fail-closed split guard).")
    args.workers_min = max(1, int(args.workers_min))
    if float(args.workers_cpu_frac) <= 0:
        args.workers_cpu_frac = 0.70
    if float(args.workers_cpu_util_high) <= float(args.workers_cpu_util_low):
        args.workers_cpu_util_high = float(args.workers_cpu_util_low) + 5.0
    args.workers_adjust_step = max(1, int(args.workers_adjust_step))
    args.workers_poll_sec = max(0.5, float(args.workers_poll_sec))
    return args


def main() -> None:
    args = parse_args()
    _install_dependencies()
    _bootstrap_codebase(args.code_bundle_uri)
    result = run_backtest(args)
    _upload_json(result, args.output_uri)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
```

---

## 11) Repro Commands Used in This Audit

```bash
# 1) Cloud job identity + launch args
 gcloud ai custom-jobs describe 4745526734198145024 --region=us-central1 --project=gen-lang-client-0250995579 --format=json
 gcloud ai custom-jobs describe 4745526734198145024 --region=us-central1 --project=gen-lang-client-0250995579 --format='value(jobSpec.workerPoolSpecs[0].containerSpec.args[0])'

# 2) Runtime logs
 gcloud logging read 'resource.type="ml_job" AND resource.labels.job_id="4745526734198145024" AND textPayload:"Backtest progress"' --project=gen-lang-client-0250995579 --limit=8 --format='value(timestamp,textPayload)'
 gcloud logging read 'resource.type="ml_job" AND resource.labels.job_id="4745526734198145024"' --project=gen-lang-client-0250995579 --limit=25 --format='value(timestamp,textPayload)'

# 3) Payload source capture
 gcloud storage cat gs://omega_v52/staging/code/payloads/omega-v60-run_cloud_backtest-20260219-211045_run_cloud_backtest.py > /tmp/cloud_run_cloud_backtest_payload.py
 shasum -a 256 /tmp/cloud_run_cloud_backtest_payload.py
 cmp -s tools/run_cloud_backtest.py /tmp/cloud_run_cloud_backtest_payload.py && echo identical

# 4) Data scope and sample-file checks
 gcloud storage ls 'gs://omega_v52_central/omega/omega/v52/frames/host=*/*_aa8abb7.parquet' ...
 python3 (polars) to check date_unique, _prepare_frames(single-day), _prepare_frames(two-day)
```

---

## 12) Auditor Summary

- The failure mode is not speculative; it is already visible in cloud logs and reproducible offline with production files.
- This is a **data granularity vs label horizon mismatch**:
  - label horizon: T+1 day,
  - execution granularity: one-day-per-file independent processing.
- The exact cloud-executing source code has been included in full above for external auditor verification.


---

## 13) Optimization Stage: Full Evidence Package

### 13.1 Cloud job identity (actual executed job)

- Job name: `projects/269018079180/locations/us-central1/customJobs/8392580415252070400`
- Display name: `omega-v60-v60_swarm_xgb-20260219-111545`
- State: `JOB_STATE_SUCCEEDED`
- Start: `2026-02-19T03:19:50Z`
- End: `2026-02-19T03:21:21Z`
- Machine type: `e2-highmem-16`

Launch command (from `gcloud ai custom-jobs describe ... --format=json`):
```bash
set -euxo pipefail
python3 -m pip install --quiet google-cloud-storage
python3 - <<'PY'
from google.cloud import storage
import shutil

def dl(uri: str, out: str) -> None:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)

dl("gs://omega_v52/staging/code/omega_core.zip", "omega_core.zip")
dl("gs://omega_v52/staging/code/payloads/omega-v60-v60_swarm_xgb-20260219-111545_v60_swarm_xgb.py", "payload.py")
shutil.unpack_archive("omega_core.zip", extract_dir=".")
PY
python3 -u payload.py --bootstrap-code --install-deps --base-matrix-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet --n-trials=50 --min-samples=2000 --seed=42 --output-uri=gs://omega_v52_central/omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json
```

### 13.2 Optimization output artifacts (complete)

Object listing:
```text
900  2026-02-19T03:21:15Z  gs://omega_v52_central/omega/staging/optimization/v60/20260219-030000_aa8abb7/swarm_best.json
TOTAL: 1 objects, 900 bytes
```

Full `swarm_best.json`:
```json
{
  "status": "completed",
  "best_params": {
    "peace_threshold": 0.5253567667772991,
    "srl_resid_sigma_mult": 1.9773888188507172,
    "topo_energy_sigma_mult": 5.427559578121958,
    "max_depth": 5,
    "learning_rate": 0.006525909043483982,
    "subsample": 0.9382970275902356,
    "colsample_bytree": 0.7855991276821759
  },
  "best_value": 0.6101452643370191,
  "n_trials": 50,
  "n_completed": 20,
  "base_matrix": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet",
  "feature_cols": [
    "sigma_eff",
    "net_ofi",
    "depth_eff",
    "epiplexity",
    "srl_resid",
    "topo_area",
    "topo_energy",
    "topo_micro",
    "topo_classic",
    "topo_trend",
    "price_change",
    "bar_duration_ms",
    "adaptive_y",
    "epi_x_srl_resid",
    "epi_x_topo_area",
    "epi_x_net_ofi"
  ],
  "seconds": 28.56,
  "job_id": "8392580415252070400"
}
```

### 13.3 Optimization input dataset format evidence (base_matrix)

Base matrix GCS object:
```text
970685813  2026-02-19T03:15:38Z  gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet
37260      2026-02-19T03:15:41Z  gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.meta.json
```

Base matrix meta summary (`base_matrix.meta.json` top-level):
```text
mode local_ticker_sharding
input_file_count 40
raw_rows 7466620
base_rows 5780139
merged_rows 5780139
merged_files 112
symbols_total 5576
symbols_per_batch 50
batch_count 112
worker_count 8
years ['2023', '2024']
hash aa8abb7
seconds 705.91
batch_stats_len 112
physics_gates {'peace_threshold': 0.1, 'peace_threshold_baseline': 0.1, 'srl_resid_sigma_mult': 0.5, 'topo_energy_sigma_mult': 10.0}
dtype_invariants {'strict_float64_required': True, 'required_float_dtype': 'Float64', 'forbidden_float_dtypes': ['Float16', 'Float32'], 'forbidden_float_dtypes_detected': False, 'checked_column_count': 25}
```

Base matrix parquet schema (actual):
```json
[
  {"name":"sigma_eff","type":"double","nullable":true},
  {"name":"net_ofi","type":"double","nullable":true},
  {"name":"depth_eff","type":"double","nullable":true},
  {"name":"epiplexity","type":"double","nullable":true},
  {"name":"srl_resid","type":"double","nullable":true},
  {"name":"topo_area","type":"double","nullable":true},
  {"name":"topo_energy","type":"double","nullable":true},
  {"name":"topo_micro","type":"double","nullable":true},
  {"name":"topo_classic","type":"double","nullable":true},
  {"name":"topo_trend","type":"double","nullable":true},
  {"name":"price_change","type":"double","nullable":true},
  {"name":"bar_duration_ms","type":"int64","nullable":true},
  {"name":"adaptive_y","type":"double","nullable":true},
  {"name":"epi_x_srl_resid","type":"double","nullable":true},
  {"name":"epi_x_topo_area","type":"double","nullable":true},
  {"name":"epi_x_net_ofi","type":"double","nullable":true},
  {"name":"symbol","type":"large_string","nullable":true},
  {"name":"date","type":"large_string","nullable":true},
  {"name":"bucket_id","type":"int64","nullable":true},
  {"name":"time_end","type":"int64","nullable":true},
  {"name":"srl_resid_050","type":"double","nullable":true},
  {"name":"is_signal","type":"bool","nullable":true},
  {"name":"is_physics_valid","type":"bool","nullable":true},
  {"name":"t1_fwd_return","type":"double","nullable":true},
  {"name":"direction_label","type":"double","nullable":true}
]
```

### 13.4 Optimization cloud payload source (full copy-paste)

- Payload URI: `gs://omega_v52/staging/code/payloads/omega-v60-v60_swarm_xgb-20260219-111545_v60_swarm_xgb.py`
- Size: `9789 bytes`
- SHA256: `bb1b6eee6616f910d0edc44ec805ca931b3abbcbf84df46c86ece1901484ce25`
- Local parity check: `cmp -s /tmp/cloud_v60_swarm_xgb_payload.py tools/v60_swarm_xgb.py` -> exit `0` (identical)

```python
#!/usr/bin/env python3
"""
v60 in-memory manifold slicing swarm (Optuna + XGBoost).

Key constraints from v60 optimization audit:
- Never rerun ETL per trial.
- Search physics gates + XGBoost hyperparameters jointly.
- Use in-memory boolean slicing for O(1)-style trial filtering.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _download_file(gcs_uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.check_call(["gsutil", "cp", gcs_uri, str(local_path)])
        return
    except Exception:
        pass

    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))


def _upload_json(payload: dict, gcs_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    tmp = Path("v60_swarm_result.json")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(tmp))


def _install_dependencies() -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "optuna",
            "xgboost",
            "numpy",
            "polars",
            "google-cloud-storage",
            "gcsfs",
            "fsspec",
            "psutil",
        ]
    )


def _bootstrap_codebase(code_bundle_uri: str) -> None:
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())


class EpistemicSwarmV6:
    def __init__(self, base_matrix_path: str, feature_cols: list[str]):
        import polars as pl

        print(f"Loading Base Matrix into RAM: {base_matrix_path}", flush=True)
        self.df = pl.read_parquet(base_matrix_path)

        required = [
            "epiplexity",
            "srl_resid_050",
            "sigma_eff",
            "topo_area",
            "topo_energy",
            "t1_fwd_return",
        ]
        missing = [c for c in required if c not in self.df.columns]
        if missing:
            raise ValueError(f"Base matrix missing required columns: {missing}")

        feat_missing = [c for c in feature_cols if c not in self.df.columns]
        if feat_missing:
            raise ValueError(f"Base matrix missing feature columns: {feat_missing}")

        self.feature_cols = list(feature_cols)
        self.epi = self.df.get_column("epiplexity").to_numpy()
        self.srl = self.df.get_column("srl_resid_050").to_numpy()
        self.sigma = self.df.get_column("sigma_eff").to_numpy()
        self.topo_area = self.df.get_column("topo_area").to_numpy()
        self.topo_energy = self.df.get_column("topo_energy").to_numpy()

        self.X = self.df.select(self.feature_cols).to_numpy()
        self.y = (self.df.get_column("t1_fwd_return").to_numpy() > 0).astype(int)

    def objective(
        self,
        trial,
        min_samples: int,
        nfold: int,
        early_stopping_rounds: int,
        num_boost_round: int,
        seed: int,
    ) -> float:
        import optuna
        import xgboost as xgb

        peace_threshold = trial.suggest_float("peace_threshold", 0.30, 0.95)
        srl_mult = trial.suggest_float("srl_resid_sigma_mult", 1.0, 8.0)
        topo_energy_mult = trial.suggest_float("topo_energy_sigma_mult", 2.0, 15.0)

        xgb_params = {
            "max_depth": trial.suggest_int("max_depth", 3, 7),
            "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.1, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "tree_method": "hist",
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "n_jobs": -1,
            "seed": int(seed),
        }

        physics_mask = (
            (self.epi > peace_threshold)
            & (np.abs(self.srl) > srl_mult * self.sigma)
            & (self.topo_energy > topo_energy_mult * self.sigma)
        )

        n_mask = int(np.sum(physics_mask))
        if n_mask < int(min_samples):
            raise optuna.TrialPruned("Physics collapse too severe. Insufficient signals.")

        X_clean = self.X[physics_mask]
        y_clean = self.y[physics_mask]
        weights_clean = (self.epi * np.log1p(np.abs(self.topo_area)))[physics_mask]

        finite = np.isfinite(weights_clean) & (weights_clean > 1e-8)
        if int(np.sum(finite)) < int(min_samples):
            raise optuna.TrialPruned("Insufficient finite weighted samples.")

        X_clean = X_clean[finite]
        y_clean = y_clean[finite]
        weights_clean = weights_clean[finite]

        dtrain = xgb.DMatrix(X_clean, label=y_clean, weight=weights_clean, feature_names=self.feature_cols)

        cv_results = xgb.cv(
            params=xgb_params,
            dtrain=dtrain,
            num_boost_round=int(num_boost_round),
            nfold=int(nfold),
            early_stopping_rounds=int(early_stopping_rounds),
            seed=int(seed),
        )
        if cv_results.empty:
            raise optuna.TrialPruned("Empty CV result.")
        return float(cv_results["test-auc-mean"].max())


def _resolve_base_matrix_path(path_or_uri: str) -> str:
    if path_or_uri.startswith("gs://"):
        local = Path("base_matrix.parquet").resolve()
        _download_file(path_or_uri, local)
        return str(local)
    p = Path(path_or_uri)
    if not p.exists():
        raise FileNotFoundError(f"Base matrix not found: {path_or_uri}")
    return str(p)


def main() -> int:
    ap = argparse.ArgumentParser(description="v60 swarm optimizer (in-memory manifold slicing)")
    ap.add_argument("--base-matrix", default="")
    ap.add_argument("--base-matrix-uri", default="")
    ap.add_argument("--n-trials", type=int, default=50)
    ap.add_argument("--min-samples", type=int, default=2000)
    ap.add_argument("--nfold", type=int, default=5)
    ap.add_argument("--early-stopping-rounds", type=int, default=15)
    ap.add_argument("--num-boost-round", type=int, default=150)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--output-local", default="")
    ap.add_argument("--output-uri", default="")
    ap.add_argument("--install-deps", action="store_true")
    ap.add_argument("--bootstrap-code", action="store_true")
    ap.add_argument("--code-bundle-uri", default="gs://omega_v52/staging/code/omega_core.zip")
    args = ap.parse_args()

    if args.install_deps:
        _install_dependencies()

    if args.bootstrap_code:
        _bootstrap_codebase(args.code_bundle_uri)

    from config_v6 import FEATURE_COLS
    import optuna
    from optuna.trial import TrialState

    base_matrix_ref = args.base_matrix_uri.strip() or args.base_matrix.strip()
    if not base_matrix_ref:
        raise SystemExit("Either --base-matrix or --base-matrix-uri is required.")

    base_matrix_path = _resolve_base_matrix_path(base_matrix_ref)
    swarm = EpistemicSwarmV6(base_matrix_path=base_matrix_path, feature_cols=list(FEATURE_COLS))

    t0 = time.time()
    study = optuna.create_study(direction="maximize")
    study.optimize(
        lambda trial: swarm.objective(
            trial,
            min_samples=int(args.min_samples),
            nfold=int(args.nfold),
            early_stopping_rounds=int(args.early_stopping_rounds),
            num_boost_round=int(args.num_boost_round),
            seed=int(args.seed),
        ),
        n_trials=int(args.n_trials),
    )

    completed_trials = [t for t in study.trials if t.state == TrialState.COMPLETE]
    if completed_trials:
        result = {
            "status": "completed",
            "best_params": dict(study.best_params),
            "best_value": float(study.best_value),
            "n_trials": int(len(study.trials)),
            "n_completed": int(len(completed_trials)),
            "base_matrix": str(base_matrix_ref),
            "feature_cols": list(FEATURE_COLS),
            "seconds": round(time.time() - t0, 2),
            "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
        }
    else:
        result = {
            "status": "no_complete_trials",
            "best_params": {},
            "best_value": None,
            "n_trials": int(len(study.trials)),
            "n_completed": 0,
            "base_matrix": str(base_matrix_ref),
            "feature_cols": list(FEATURE_COLS),
            "seconds": round(time.time() - t0, 2),
            "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
            "message": "All trials pruned; relax min-samples or use a larger base matrix.",
        }

    if args.output_local:
        out = Path(args.output_local)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.output_uri:
        _upload_json(result, args.output_uri)

    print("--- V60 SWARM RESULT JSON START ---")
    print(json.dumps(result, ensure_ascii=False))
    print("--- V60 SWARM RESULT JSON END ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 14) Training Stage: Full Evidence Package

### 14.1 Cloud job identity (actual executed job)

- Job name: `projects/269018079180/locations/us-central1/customJobs/6022297228557680640`
- Display name: `omega-v60-run_vertex_xgb_train-20260219-205414`
- State: `JOB_STATE_SUCCEEDED`
- Start: `2026-02-19T12:56:47Z`
- End: `2026-02-19T12:57:47Z`
- Machine type: `n2-standard-16`

Launch command (from `gcloud ai custom-jobs describe ... --format=json`):
```bash
set -euxo pipefail
python3 -m pip install --quiet google-cloud-storage
python3 - <<'PY'
from google.cloud import storage
import shutil

def dl(uri: str, out: str) -> None:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    storage.Client().bucket(bucket).blob(blob).download_to_filename(out)

dl("gs://omega_v52_central/omega/staging/code/omega_core_20260219-125410_78e36d9.zip", "omega_core.zip")
dl("gs://omega_v52/staging/code/payloads/omega-v60-run_vertex_xgb_train-20260219-205414_run_vertex_xgb_train.py", "payload.py")
shutil.unpack_archive("omega_core.zip", extract_dir=".")
PY
python3 -u payload.py --base-matrix-uri=gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet --code-bundle-uri=gs://omega_v52_central/omega/staging/code/omega_core_20260219-125410_78e36d9.zip --output-uri=gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9 --peace-threshold=0.5253567667772991 --srl-resid-sigma-mult=1.9773888188507172 --topo-energy-sigma-mult=5.427559578121958 --xgb-max-depth=5 --xgb-learning-rate=0.006525909043483982 --xgb-subsample=0.9382970275902356 --xgb-colsample-bytree=0.7855991276821759
```

### 14.2 Training output artifacts (complete)

Object listing:
```text
355684  2026-02-19T12:57:20Z  gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl
746     2026-02-19T12:57:20Z  gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/train_metrics.json
TOTAL: 2 objects, 356430 bytes
```

Full `train_metrics.json`:
```json
{
  "status": "completed",
  "base_matrix_uri": "gs://omega_v52_central/omega/staging/base_matrix/v60/resume_aa8abb7/base_matrix.parquet",
  "base_rows": 5780139,
  "mask_rows": 2188,
  "total_training_rows": 2067,
  "seconds": 1.04,
  "job_id": "6022297228557680640",
  "model_uri": "gs://omega_v52_central/omega/staging/models/v6/20260219-125410_78e36d9/omega_v6_xgb_final.pkl",
  "overrides": {
    "peace_threshold": 0.5253567667772991,
    "srl_resid_sigma_mult": 1.9773888188507172,
    "topo_energy_sigma_mult": 5.427559578121958,
    "xgb_max_depth": 5,
    "xgb_learning_rate": 0.006525909043483982,
    "xgb_subsample": 0.9382970275902356,
    "xgb_colsample_bytree": 0.7855991276821759,
    "num_boost_round": 150,
    "seed": 42
  }
}
```

Model payload structure (from directly loading `omega_v6_xgb_final.pkl`):
```text
payload_type dict
keys ['model', 'scaler', 'feature_cols']
model_type xgboost.core.Booster
scaler_is_none True
feature_cols_type list len 16
feature_cols ["sigma_eff","net_ofi","depth_eff","epiplexity","srl_resid","topo_area","topo_energy","topo_micro","topo_classic","topo_trend","price_change","bar_duration_ms","adaptive_y","epi_x_srl_resid","epi_x_topo_area","epi_x_net_ofi"]
```

### 14.3 Training cloud payload source (full copy-paste)

- Payload URI: `gs://omega_v52/staging/code/payloads/omega-v60-run_vertex_xgb_train-20260219-205414_run_vertex_xgb_train.py`
- Size: `8567 bytes`
- SHA256: `d67f0328d058cedec50ca83fd99f6e9ebbe3d0438443cc7fe02509f7a1659c6e`
- Local parity check: `cmp -s /tmp/cloud_run_vertex_xgb_train_payload.py tools/run_vertex_xgb_train.py` -> exit `0` (identical)

```python
#!/usr/bin/env python3
"""
OMEGA v6 Vertex payload: global in-memory XGBoost training on base_matrix.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import pickle
import shutil
import subprocess
import sys
import time
from pathlib import Path


def _install_dependencies() -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "polars",
            "gcsfs",
            "fsspec",
            "numpy",
            "xgboost",
            "google-cloud-storage",
            "scikit-learn",
        ]
    )


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _download_file(gcs_uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    if not gcs_uri.startswith("gs://"):
        if Path(gcs_uri).resolve() != local_path.resolve():
            shutil.copyfile(gcs_uri, local_path)
        return
    try:
        subprocess.check_call(["gsutil", "cp", gcs_uri, str(local_path)])
        return
    except Exception:
        pass
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))


def _upload_file(local_path: Path, gcs_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(local_path))


def _bootstrap_codebase(code_bundle_uri: str) -> None:
    if not code_bundle_uri:
        return
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())


def run_global_training(args: argparse.Namespace) -> None:
    import numpy as np
    import polars as pl
    import xgboost as xgb
    from config_v6 import FEATURE_COLS

    base_uri = str(args.base_matrix_uri).strip()
    if not base_uri:
        raise RuntimeError("--base-matrix-uri is required and must not be empty.")
    local_matrix = Path("base_matrix_train.parquet")
    print(f"[*] Downloading base matrix: {base_uri}", flush=True)
    _download_file(base_uri, local_matrix)

    print("[*] Loading global manifold into RAM...", flush=True)
    started = time.time()
    df = pl.read_parquet(local_matrix)

    required_cols = {
        "epiplexity",
        "srl_resid_050",
        "sigma_eff",
        "topo_area",
        "topo_energy",
        "t1_fwd_return",
        *list(FEATURE_COLS),
    }
    missing = sorted([c for c in required_cols if c not in df.columns])
    if missing:
        raise RuntimeError(f"base_matrix missing columns: {missing}")

    epi = df.get_column("epiplexity").to_numpy()
    srl = df.get_column("srl_resid_050").to_numpy()
    sigma = df.get_column("sigma_eff").to_numpy()
    topo_area = df.get_column("topo_area").to_numpy()
    topo_energy = df.get_column("topo_energy").to_numpy()
    X_all = df.select(list(FEATURE_COLS)).to_numpy()
    y_all = (df.get_column("t1_fwd_return").to_numpy() > 0).astype(int)

    print(
        "[*] Applying physics gates "
        f"(peace={args.peace_threshold}, srl_mult={args.srl_resid_sigma_mult}, topo_mult={args.topo_energy_sigma_mult})...",
        flush=True,
    )
    physics_mask = (
        (epi > float(args.peace_threshold))
        & (np.abs(srl) > float(args.srl_resid_sigma_mult) * sigma)
        & (topo_energy > float(args.topo_energy_sigma_mult) * sigma)
    )

    mask_rows = int(np.sum(physics_mask))
    X_clean = X_all[physics_mask]
    y_clean = y_all[physics_mask]
    weights_clean = (epi * np.log1p(np.abs(topo_area)))[physics_mask]

    finite = np.isfinite(weights_clean) & (weights_clean > 1e-8)
    X_clean = X_clean[finite]
    y_clean = y_clean[finite]
    weights_clean = weights_clean[finite]

    base_rows = int(df.height)
    train_rows = int(len(y_clean))
    print(f"[*] Sliced rows for training: {train_rows} / {base_rows} (mask_rows={mask_rows})", flush=True)
    if train_rows <= 0:
        raise RuntimeError("Physics gates removed all rows; cannot train.")

    del df, epi, srl, sigma, topo_area, topo_energy, X_all, y_all, physics_mask, finite
    gc.collect()

    dtrain = xgb.DMatrix(
        X_clean,
        label=y_clean,
        weight=weights_clean,
        feature_names=list(FEATURE_COLS),
    )

    params = {
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "max_depth": int(args.xgb_max_depth),
        "eta": float(args.xgb_learning_rate),
        "subsample": float(args.xgb_subsample),
        "colsample_bytree": float(args.xgb_colsample_bytree),
        "tree_method": "hist",
        "n_jobs": int(args.n_jobs),
        "seed": int(args.seed),
    }
    rounds = int(max(1, args.num_boost_round))
    print("[*] Running one-shot global xgb.train()...", flush=True)
    model = xgb.train(params=params, dtrain=dtrain, num_boost_round=rounds)

    payload = {
        "model": model,
        "scaler": None,
        "feature_cols": list(FEATURE_COLS),
    }
    model_name = "omega_v6_xgb_final.pkl"
    with open(model_name, "wb") as f:
        pickle.dump(payload, f)

    seconds = round(time.time() - started, 2)
    output_prefix = str(args.output_uri).rstrip("/")
    model_uri = f"{output_prefix}/{model_name}"
    _upload_file(Path(model_name), model_uri)

    metrics = {
        "status": "completed",
        "base_matrix_uri": base_uri,
        "base_rows": base_rows,
        "mask_rows": mask_rows,
        "total_training_rows": train_rows,
        "seconds": seconds,
        "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
        "model_uri": model_uri,
        "overrides": {
            "peace_threshold": float(args.peace_threshold),
            "srl_resid_sigma_mult": float(args.srl_resid_sigma_mult),
            "topo_energy_sigma_mult": float(args.topo_energy_sigma_mult),
            "xgb_max_depth": int(args.xgb_max_depth),
            "xgb_learning_rate": float(args.xgb_learning_rate),
            "xgb_subsample": float(args.xgb_subsample),
            "xgb_colsample_bytree": float(args.xgb_colsample_bytree),
            "num_boost_round": rounds,
            "seed": int(args.seed),
        },
    }
    metrics_path = Path("train_metrics.json")
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    _upload_file(metrics_path, f"{output_prefix}/train_metrics.json")
    print(json.dumps(metrics, ensure_ascii=False), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="OMEGA v6 global XGBoost trainer payload")
    ap.add_argument("--base-matrix-uri", required=True, help="GCS URI for base_matrix.parquet")
    ap.add_argument("--output-uri", required=True, help="GCS prefix for model output")

    ap.add_argument("--peace-threshold", type=float, default=0.10)
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=0.5)
    ap.add_argument("--topo-energy-sigma-mult", type=float, default=2.0)
    ap.add_argument("--xgb-max-depth", type=int, default=5)
    ap.add_argument("--xgb-learning-rate", type=float, default=0.03)
    ap.add_argument("--xgb-subsample", type=float, default=0.9)
    ap.add_argument("--xgb-colsample-bytree", type=float, default=0.8)
    ap.add_argument("--num-boost-round", type=int, default=150)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-jobs", type=int, default=-1)

    # Legacy args kept for compatibility with old submitters.
    ap.add_argument("--code-bundle-uri", required=True, help="Run-pinned code bundle URI.")
    ap.add_argument("--data-pattern", default="")
    ap.add_argument("--train-years", default="")
    ap.add_argument("--max-files", type=int, default=0)
    ap.add_argument("--max-rows-per-file", type=int, default=0)

    args, _ = ap.parse_known_args()
    if str(args.data_pattern).strip():
        raise RuntimeError("`--data-pattern` is forbidden for this training payload. Use `--base-matrix-uri` only.")
    if str(args.train_years).strip():
        raise RuntimeError("`--train-years` is forbidden for this training payload. Use prebuilt base_matrix scope.")
    _install_dependencies()
    _bootstrap_codebase(args.code_bundle_uri)
    run_global_training(args)


if __name__ == "__main__":
    main()
```

---

## 15) Anti-Format / Anti-Category Error Guardrail (For New Backtest Script Author)

This section is intentionally strict to prevent mistakes in file format, argument category, and output schema.

### 15.1 Category boundaries (must not mix)

- `optimization` stage input category:
  - **Only** `base_matrix` (`--base-matrix-uri` or `--base-matrix`)
  - Never raw frame glob as optimization input.
- `training` stage input category:
  - **Only** `base_matrix` (`--base-matrix-uri` required)
  - `--data-pattern` and `--train-years` are explicitly forbidden in training payload.
- `backtest` stage input category:
  - Raw frame files via `--data-pattern` + split guards (`--test-years`, optional `--test-ym`)
  - Not base_matrix.

### 15.2 URI/path naming format (observed runtime conventions)

- Payload script URI format:
  - `gs://omega_v52/staging/code/payloads/omega-v60-<entry>-<timestamp>_<script>.py`
- Code bundle URI format:
  - `gs://omega_v52_central/omega/staging/code/omega_core_<run_id>_<git>.zip`
- Optimization result URI format:
  - `gs://omega_v52_central/omega/staging/optimization/v60/<run_id>_<hash>/swarm_best.json`
- Training output URI prefix format:
  - `gs://omega_v52_central/omega/staging/models/v6/<run_id>_<git>/`
  - Contains `omega_v6_xgb_final.pkl` and `train_metrics.json`
- Backtest output URI format:
  - `gs://omega_v52_central/omega/staging/backtest/v6/<run_id>_<git>/<metrics_name>.json`

### 15.3 JSON schema contracts (hard contract)

`swarm_best.json` required keys:
- `status: str`
- `best_params: object`
- `best_value: number|null`
- `n_trials: int`
- `n_completed: int`
- `base_matrix: str`
- `feature_cols: list[str]`
- `seconds: number`
- `job_id: str`

`train_metrics.json` required keys:
- `status: str`
- `base_matrix_uri: str`
- `base_rows: int`
- `mask_rows: int`
- `total_training_rows: int`
- `seconds: number`
- `job_id: str`
- `model_uri: str`
- `overrides: object`

### 15.4 Parquet schema contracts (training/optimization input)

Base matrix must include at least:
- Physics gate columns: `epiplexity`, `srl_resid_050`, `sigma_eff`, `topo_energy`, `topo_area`
- Label column: `t1_fwd_return`
- Feature columns: exactly the feature set consumed by `config_v6.FEATURE_COLS` (16 columns in this run)

Actual observed primitive types:
- Most numeric features: `double`
- Time/bucket: `int64`
- Boolean flags: `bool`
- Id/date fields: `large_string`

### 15.5 Argument-level fail-closed rules (from cloud payload source)

Training payload fail-closed:
- `--base-matrix-uri` required
- `--code-bundle-uri` required
- If `--data-pattern` non-empty -> hard error
- If `--train-years` non-empty -> hard error

Backtest payload fail-closed (already evidenced earlier):
- `--test-years` cannot be empty
- `if not per_file: raise RuntimeError("Backtest produced no valid processed frames.")`

### 15.6 Practical lint checklist before submit (copy this to PR description)

1. Verify stage category mapping: optimization/train consume `base_matrix`, backtest consume raw frames.
2. Verify every URI matches expected prefix and run-id/hash namespace.
3. Validate output JSON keys/types against section 15.3.
4. Validate input parquet columns and primitive types against section 15.4.
5. Confirm fail-closed checks are present and not bypassed.
6. Confirm payload source uploaded to GCS is the exact script intended (hash + object size recorded).

