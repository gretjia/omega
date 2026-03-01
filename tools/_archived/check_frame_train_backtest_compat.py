"""
check_frame_train_backtest_compat.py

Sample-based compatibility gate between frame outputs and train/backtest consumers.

Design goals:
1. Avoid loading full dataset into memory.
2. Validate columns required by the real v40 train/backtest code paths.
3. Smoke-test `_prepare_frames` on a small sample before pipeline chaining.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import Counter, deque
from pathlib import Path
from typing import Deque, Dict, List, Tuple

try:
    import polars as pl
except Exception as exc:  # pragma: no cover - environment dependent
    pl = None
    _POLARS_IMPORT_ERROR = exc
else:
    _POLARS_IMPORT_ERROR = None

sys.path.append(str(Path(__file__).parent.parent))


RAW_REQUIRED_COLUMNS: Tuple[str, ...] = (
    "open",
    "close",
    "sigma",
    "depth",
    "net_ofi",
    "trace",
    "ofi_list",
    "trade_vol",
    "cancel_vol",
)


def _write_json_atomic(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def _collect_parquet_sample(
    input_dir: Path, sample_files: int, seed: int
) -> Tuple[int, List[Path]]:
    sample_files = max(3, int(sample_files))
    first_n = max(1, sample_files // 3)
    last_n = max(1, sample_files // 3)
    reservoir_n = max(1, sample_files - first_n - last_n)

    rng = random.Random(int(seed))
    first: List[Path] = []
    last: Deque[Path] = deque(maxlen=last_n)
    reservoir: List[Path] = []
    total = 0

    for dirpath, dirnames, filenames in os.walk(input_dir):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if not filename.lower().endswith(".parquet"):
                continue
            p = Path(dirpath) / filename
            total += 1

            if len(first) < first_n:
                first.append(p)
            last.append(p)

            if len(reservoir) < reservoir_n:
                reservoir.append(p)
            else:
                j = rng.randint(1, total)
                if j <= reservoir_n:
                    reservoir[j - 1] = p

    ordered = first + list(last) + reservoir
    dedup: List[Path] = []
    seen = set()
    for p in ordered:
        k = str(p)
        if k in seen:
            continue
        seen.add(k)
        dedup.append(p)
    return total, dedup


def _schema_columns(path: Path) -> List[str]:
    schema = pl.read_parquet_schema(path)
    return list(schema.keys())


def run_check(
    input_dir: Path,
    sample_files: int,
    prepare_smoke_files: int,
    min_raw_ready_ratio: float,
    seed: int,
    status_json: Path | None,
) -> int:
    started_at = time.time()

    if pl is None:
        payload = {
            "stage": "frame_compat",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "failed",
            "error": f"polars import failed: {_POLARS_IMPORT_ERROR}",
        }
        if status_json:
            _write_json_atomic(status_json, payload)
        print(payload["error"])
        return 2

    if not input_dir.exists():
        payload = {
            "stage": "frame_compat",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "failed",
            "error": f"input directory not found: {input_dir}",
        }
        if status_json:
            _write_json_atomic(status_json, payload)
        print(payload["error"])
        return 2

    from config import load_l2_pipeline_config
    from omega_core.trainer import OmegaTrainerV3

    cfg = load_l2_pipeline_config()
    trainer = OmegaTrainerV3(cfg)
    feature_cols = list(trainer.feature_cols)
    feature_set = set(feature_cols)

    total_files, sample = _collect_parquet_sample(input_dir, sample_files, seed)
    sample_total = len(sample)

    sample_raw_ready = 0
    sample_backtest_ready = 0
    schema_error_count = 0
    sample_rows_scanned = 0
    sample_nonpositive_close_rows = 0
    sample_close_check_errors = 0
    raw_ready_paths: List[Path] = []
    missing_counter = Counter()
    schema_errors: List[Dict] = []
    close_anomaly_files: List[Dict] = []
    sample_results: List[Dict] = []

    for p in sample:
        try:
            cols = _schema_columns(p)
            colset = set(cols)
        except Exception as exc:
            schema_error_count += 1
            schema_errors.append({"file": str(p), "error": str(exc)})
            sample_results.append(
                {"file": str(p), "schema_ok": False, "error": str(exc)}
            )
            continue

        raw_missing = [c for c in RAW_REQUIRED_COLUMNS if c not in colset]
        raw_ready = len(raw_missing) == 0
        if raw_ready:
            sample_raw_ready += 1
            raw_ready_paths.append(p)
        else:
            for c in raw_missing:
                missing_counter[c] += 1

        has_feature_stack = feature_set.issubset(colset)
        has_ret_k = "ret_k" in colset
        backtest_ready = raw_ready or (has_feature_stack and has_ret_k)
        if backtest_ready:
            sample_backtest_ready += 1

        close_rows = None
        nonpositive_close_rows = None
        close_min = None
        close_max = None
        close_stats_error = None
        if "close" in colset:
            try:
                close_probe = (
                    pl.scan_parquet(str(p))
                    .select(
                        [
                            pl.len().alias("rows"),
                            (pl.col("close") <= 0.0).sum().alias("nonpositive_close"),
                            pl.col("close").min().alias("close_min"),
                            pl.col("close").max().alias("close_max"),
                        ]
                    )
                    .collect()
                )
                close_rows = int(close_probe["rows"][0])
                nonpositive_close_rows = int(close_probe["nonpositive_close"][0])
                close_min_v = close_probe["close_min"][0]
                close_max_v = close_probe["close_max"][0]
                close_min = float(close_min_v) if close_min_v is not None else None
                close_max = float(close_max_v) if close_max_v is not None else None
                sample_rows_scanned += close_rows
                sample_nonpositive_close_rows += nonpositive_close_rows
                if nonpositive_close_rows > 0 and len(close_anomaly_files) < 12:
                    close_anomaly_files.append(
                        {
                            "file": str(p),
                            "rows": close_rows,
                            "nonpositive_close_rows": nonpositive_close_rows,
                            "close_min": close_min,
                            "close_max": close_max,
                        }
                    )
            except Exception as exc:
                sample_close_check_errors += 1
                close_stats_error = str(exc)

        sample_results.append(
            {
                "file": str(p),
                "schema_ok": True,
                "raw_ready": raw_ready,
                "raw_missing": raw_missing,
                "feature_stack_ready": has_feature_stack,
                "ret_k_present": has_ret_k,
                "backtest_ready": backtest_ready,
                "close_rows": close_rows,
                "nonpositive_close_rows": nonpositive_close_rows,
                "close_min": close_min,
                "close_max": close_max,
                "close_stats_error": close_stats_error,
            }
        )

    smoke_target = max(1, int(prepare_smoke_files))
    smoke_candidates = raw_ready_paths[:smoke_target]
    smoke_ok = 0
    smoke_errors: List[Dict] = []

    for p in smoke_candidates:
        try:
            df = pl.scan_parquet(str(p)).head(256).collect()
            if df.height == 0:
                smoke_errors.append(
                    {"file": str(p), "error": "sample dataframe is empty"}
                )
                continue
            out = trainer._prepare_frames(df, cfg)
            missing_features = [c for c in feature_cols if c not in out.columns]
            if missing_features:
                smoke_errors.append(
                    {
                        "file": str(p),
                        "error": f"missing model features after _prepare_frames: {missing_features}",
                    }
                )
                continue
            smoke_ok += 1
        except Exception as exc:
            smoke_errors.append({"file": str(p), "error": str(exc)})

    raw_ready_ratio = (sample_raw_ready / sample_total) if sample_total > 0 else 0.0
    backtest_ready_ratio = (
        sample_backtest_ready / sample_total if sample_total > 0 else 0.0
    )

    checks = {
        "has_files": total_files > 0,
        "has_sample": sample_total > 0,
        "raw_ready_nonzero": sample_raw_ready > 0,
        "raw_ready_ratio_ok": raw_ready_ratio >= float(min_raw_ready_ratio),
        "backtest_ready_nonzero": sample_backtest_ready > 0,
        "smoke_ok_nonzero": smoke_ok > 0,
        "close_positive_guard": (
            sample_close_check_errors == 0 and sample_nonpositive_close_rows == 0
        ),
    }
    compatible = all(checks.values())

    payload = {
        "stage": "frame_compat",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "completed" if compatible else "failed",
        "input_dir": str(input_dir),
        "total_parquet_files_seen": int(total_files),
        "sample_size": int(sample_total),
        "sample_raw_ready": int(sample_raw_ready),
        "sample_backtest_ready": int(sample_backtest_ready),
        "sample_schema_errors": int(schema_error_count),
        "sample_close_rows_scanned": int(sample_rows_scanned),
        "sample_nonpositive_close_rows": int(sample_nonpositive_close_rows),
        "sample_close_check_errors": int(sample_close_check_errors),
        "raw_ready_ratio": float(raw_ready_ratio),
        "backtest_ready_ratio": float(backtest_ready_ratio),
        "min_raw_ready_ratio": float(min_raw_ready_ratio),
        "prepare_smoke_target": int(smoke_target),
        "prepare_smoke_ok": int(smoke_ok),
        "prepare_smoke_errors": int(len(smoke_errors)),
        "checks": checks,
        "missing_raw_columns_top": missing_counter.most_common(12),
        "close_anomaly_files": close_anomaly_files,
        "schema_errors": schema_errors[:10],
        "smoke_errors": smoke_errors[:10],
        "sample_results": sample_results[:40],
        "elapsed_sec": max(0.0, time.time() - started_at),
    }

    if status_json is not None:
        _write_json_atomic(status_json, payload)

    print("=== Frame Compatibility Check ===")
    print(f"Input dir: {input_dir}")
    print(f"Parquet files seen: {total_files}")
    print(f"Sample size: {sample_total}")
    print(
        "Raw-ready sample: "
        f"{sample_raw_ready}/{sample_total} ({raw_ready_ratio:.3f}), "
        f"Backtest-ready sample: {sample_backtest_ready}/{sample_total} "
        f"({backtest_ready_ratio:.3f})"
    )
    print(
        f"Prepare smoke: ok={smoke_ok}/{smoke_target}, "
        f"errors={len(smoke_errors)}"
    )
    print(
        "Close sanity: "
        f"rows={sample_rows_scanned}, "
        f"nonpositive={sample_nonpositive_close_rows}, "
        f"errors={sample_close_check_errors}"
    )

    if compatible:
        print("[PASS] frame outputs are compatible with train/backtest pipeline.")
        return 0

    print("[FAIL] frame outputs are not compatible enough for safe chaining.")
    for k, v in checks.items():
        if not v:
            print(f"  - failed check: {k}")
    return 2


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Sample-based frame->train/backtest compatibility preflight."
    )
    p.add_argument("--input-dir", required=True, type=str)
    p.add_argument("--sample-files", type=int, default=96)
    p.add_argument("--prepare-smoke-files", type=int, default=3)
    p.add_argument("--min-raw-ready-ratio", type=float, default=0.9)
    p.add_argument("--seed", type=int, default=20260208)
    p.add_argument("--status-json", type=str, default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    return run_check(
        input_dir=Path(args.input_dir),
        sample_files=max(3, int(args.sample_files)),
        prepare_smoke_files=max(1, int(args.prepare_smoke_files)),
        min_raw_ready_ratio=float(args.min_raw_ready_ratio),
        seed=int(args.seed),
        status_json=Path(args.status_json) if args.status_json else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())
