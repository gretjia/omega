#!/usr/bin/env python3
"""
verify_v40_data_contract.py

Audit v40 frame/train/backtest data-contract alignment from runtime artifacts.

This script does NOT load parquet bodies; it validates status+manifest evidence:
1) split policy (2023/2024 train, 2025 + 202601 backtest)
2) manifest overlap guard
3) frame compatibility status
4) train/backtest runtime error counters
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


DATE_PREFIX_RE = re.compile(r"\\(?P<date>\d{8})_")


def _load_json(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_manifest(path: Path) -> List[str]:
    out: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip().lstrip("\ufeff")
            if s:
                out.append(s)
    return out


def _extract_year_month(path_str: str) -> Tuple[int, int]:
    m = DATE_PREFIX_RE.search(path_str)
    if m is None:
        raise ValueError(f"missing YYYYMMDD_ prefix: {path_str}")
    d = m.group("date")
    return int(d[:4]), int(d[:6])


def _check_manifest_role(
    files: Sequence[str],
    *,
    role: str,
    train_years: Iterable[int],
    backtest_years: Iterable[int],
    backtest_year_months: Iterable[int],
) -> Tuple[int, int]:
    ok = 0
    bad = 0
    train_years_set = set(int(x) for x in train_years)
    backtest_years_set = set(int(x) for x in backtest_years)
    backtest_ym_set = set(int(x) for x in backtest_year_months)

    for p in files:
        try:
            y, ym = _extract_year_month(p)
        except Exception:
            bad += 1
            continue

        if role == "train":
            if y in train_years_set:
                ok += 1
            else:
                bad += 1
        else:
            if (y in backtest_years_set) or (ym in backtest_ym_set):
                ok += 1
            else:
                bad += 1
    return ok, bad


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify v40 frame/train/backtest data contract from runtime artifacts.")
    ap.add_argument(
        "--runtime-root",
        type=str,
        default="audit/v40_runtime/windows",
        help="Runtime root produced by windows pipeline.",
    )
    ap.add_argument(
        "--strict-close-guard",
        action="store_true",
        help="Require frame_compat checks.close_positive_guard=true (fails if key missing).",
    )
    args = ap.parse_args()

    runtime_root = Path(args.runtime_root)
    manifests_dir = runtime_root / "manifests"
    frame_dir = runtime_root / "frame"
    train_dir = runtime_root / "train"
    backtest_dir = runtime_root / "backtest"

    required_files = {
        "split_preflight": manifests_dir / "split_preflight_status.json",
        "train_manifest_status": manifests_dir / "train_manifest_status.json",
        "backtest_manifest_status": manifests_dir / "backtest_manifest_status.json",
        "train_manifest": manifests_dir / "train_files.txt",
        "backtest_manifest": manifests_dir / "backtest_files.txt",
        "frame_compat_status": frame_dir / "frame_compat_status.json",
        "train_status": train_dir / "train_status.json",
        "backtest_status": backtest_dir / "backtest_status.json",
    }

    missing = [name for name, p in required_files.items() if not p.exists()]
    if missing:
        print(f"[FAIL] missing runtime artifacts: {missing}")
        return 2

    split = _load_json(required_files["split_preflight"])
    train_manifest_status = _load_json(required_files["train_manifest_status"])
    backtest_manifest_status = _load_json(required_files["backtest_manifest_status"])
    frame_compat = _load_json(required_files["frame_compat_status"])
    train_status = _load_json(required_files["train_status"])
    backtest_status = _load_json(required_files["backtest_status"])
    train_files = _load_manifest(required_files["train_manifest"])
    backtest_files = _load_manifest(required_files["backtest_manifest"])

    failures: List[str] = []
    notes: List[str] = []

    # 1) Split policy
    expected_train_years = [2023, 2024]
    expected_backtest_years = [2025]
    expected_backtest_ym = [202601]

    filters = split.get("filters", {})
    if list(filters.get("train_years", [])) != expected_train_years:
        failures.append(f"split train_years mismatch: {filters.get('train_years')} != {expected_train_years}")
    if list(filters.get("backtest_years", [])) != expected_backtest_years:
        failures.append(f"split backtest_years mismatch: {filters.get('backtest_years')} != {expected_backtest_years}")
    if list(filters.get("backtest_year_months", [])) != expected_backtest_ym:
        failures.append(
            f"split backtest_year_months mismatch: {filters.get('backtest_year_months')} != {expected_backtest_ym}"
        )
    if split.get("status") != "completed":
        failures.append(f"split_preflight status != completed: {split.get('status')}")
    if int(split.get("overlap_count", -1)) != 0:
        failures.append(f"split_preflight overlap_count != 0: {split.get('overlap_count')}")

    # 2) Manifest consistency
    if train_manifest_status.get("status") != "completed":
        failures.append(f"train_manifest_status != completed: {train_manifest_status.get('status')}")
    if backtest_manifest_status.get("status") != "completed":
        failures.append(f"backtest_manifest_status != completed: {backtest_manifest_status.get('status')}")
    if int(train_manifest_status.get("matched_files", -1)) != len(train_files):
        failures.append(
            f"train manifest count mismatch: status={train_manifest_status.get('matched_files')} file={len(train_files)}"
        )
    if int(backtest_manifest_status.get("matched_files", -1)) != len(backtest_files):
        failures.append(
            f"backtest manifest count mismatch: status={backtest_manifest_status.get('matched_files')} file={len(backtest_files)}"
        )

    overlap = set(train_files).intersection(backtest_files)
    if overlap:
        failures.append(f"manifest overlap found: {len(overlap)} files")

    train_ok, train_bad = _check_manifest_role(
        train_files,
        role="train",
        train_years=expected_train_years,
        backtest_years=expected_backtest_years,
        backtest_year_months=expected_backtest_ym,
    )
    backtest_ok, backtest_bad = _check_manifest_role(
        backtest_files,
        role="backtest",
        train_years=expected_train_years,
        backtest_years=expected_backtest_years,
        backtest_year_months=expected_backtest_ym,
    )
    if train_bad > 0:
        failures.append(f"train manifest contains {train_bad} files outside train years")
    if backtest_bad > 0:
        failures.append(f"backtest manifest contains {backtest_bad} files outside backtest policy")

    # 3) Frame compatibility
    if frame_compat.get("status") != "completed":
        failures.append(f"frame_compat status != completed: {frame_compat.get('status')}")
    checks = frame_compat.get("checks", {})
    required_true_checks = [
        "has_files",
        "has_sample",
        "raw_ready_nonzero",
        "raw_ready_ratio_ok",
        "backtest_ready_nonzero",
        "smoke_ok_nonzero",
    ]
    for key in required_true_checks:
        if not bool(checks.get(key, False)):
            failures.append(f"frame_compat checks.{key} is not true")

    if "close_positive_guard" in checks:
        if not bool(checks.get("close_positive_guard", False)):
            failures.append("frame_compat checks.close_positive_guard is not true")
    else:
        msg = "frame_compat status has no close_positive_guard (likely generated by older checker build)"
        if args.strict_close_guard:
            failures.append(msg)
        else:
            notes.append(msg)

    # 4) Train/backtest runtime errors
    if train_status.get("status") != "completed":
        failures.append(f"train status != completed: {train_status.get('status')}")
    if int(train_status.get("files_schema_errors", 0)) != 0:
        failures.append(f"train files_schema_errors != 0: {train_status.get('files_schema_errors')}")
    if int(train_status.get("files_worker_errors", 0)) != 0:
        failures.append(f"train files_worker_errors != 0: {train_status.get('files_worker_errors')}")

    backtest_err = int(backtest_status.get("error_count", 0))
    if backtest_err != 0:
        failures.append(f"backtest error_count != 0: {backtest_err}")
    backtest_phase = str(backtest_status.get("phase", ""))
    if backtest_phase not in ("in_progress", "complete", "done_no_tasks"):
        notes.append(f"backtest unusual phase: {backtest_phase}")

    # Report
    print("[VERIFY] v40 data contract summary")
    print(f"- runtime_root: {runtime_root}")
    print(f"- train_manifest_files: {len(train_files)} (ok={train_ok}, bad={train_bad})")
    print(f"- backtest_manifest_files: {len(backtest_files)} (ok={backtest_ok}, bad={backtest_bad})")
    print(f"- overlap: {len(overlap)}")
    print(f"- train_status: {train_status.get('status')}")
    print(f"- backtest_status: {backtest_status.get('status')} phase={backtest_phase}")

    if notes:
        print("[NOTE]")
        for n in notes:
            print(f"- {n}")

    if failures:
        print("[FAIL]")
        for f in failures:
            print(f"- {f}")
        return 1

    print("[PASS] v40 frame -> train/backtest data contract is aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
