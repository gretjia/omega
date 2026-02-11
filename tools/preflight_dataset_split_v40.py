"""
preflight_dataset_split_v40.py

Fail-closed dataset split guard for v40 training/backtest pipeline.

Checks:
1) Frame parquet filenames must follow YYYYMMDD_*.parquet (unless explicitly allowed)
2) Train/backtest role filters resolve to non-empty file sets
3) Train and backtest sets are disjoint (no overlap)
4) Emits auditable status JSON for runtime monitoring/handover
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

sys.path.append(str(Path(__file__).parent.parent))

from config import TrainerConfig


DATE_PREFIX_RE = re.compile(r"^(?P<date>\d{8})_")


def _parse_csv_list(raw: str) -> List[str]:
    if raw is None:
        return []
    s = str(raw).strip()
    if not s:
        return []
    parts = re.split(r"[,\s;]+", s)
    return [p.strip() for p in parts if p.strip()]


def _to_int_set(values: Iterable[str], expected_len: int) -> Set[int]:
    out: Set[int] = set()
    for v in values:
        if not v.isdigit() or len(v) != expected_len:
            raise ValueError(f"invalid numeric token (len={expected_len} required): {v}")
        out.add(int(v))
    return out


def _write_json_atomic(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def _load_default_split_policy() -> Tuple[Set[int], Set[int], Set[int]]:
    split = TrainerConfig().split
    train_years = {int(y) for y in split.train_years}
    backtest_years = {int(y) for y in split.test_years}
    backtest_year_months = {
        int(ym) for ym in getattr(split, "test_year_months", ())
    }
    return train_years, backtest_years, backtest_year_months


def _resolve_filters(
    train_years_raw: str,
    backtest_years_raw: str,
    backtest_year_months_raw: str,
) -> Tuple[Set[int], Set[int], Set[int]]:
    default_train_years, default_backtest_years, default_backtest_year_months = (
        _load_default_split_policy()
    )
    train_years = (
        _to_int_set(_parse_csv_list(train_years_raw), expected_len=4)
        if _parse_csv_list(train_years_raw)
        else default_train_years
    )
    backtest_years = (
        _to_int_set(_parse_csv_list(backtest_years_raw), expected_len=4)
        if _parse_csv_list(backtest_years_raw)
        else default_backtest_years
    )
    backtest_year_months = (
        _to_int_set(_parse_csv_list(backtest_year_months_raw), expected_len=6)
        if _parse_csv_list(backtest_year_months_raw)
        else default_backtest_year_months
    )

    if not train_years:
        raise ValueError("train years cannot be empty")
    if not backtest_years and not backtest_year_months:
        raise ValueError("backtest filters cannot be empty")
    return train_years, backtest_years, backtest_year_months


def _scan_frame_files(input_dir: Path, status_json_path: Path | None = None) -> Tuple[List[Tuple[str, int, int]], List[str], int]:
    if not input_dir.exists():
        raise FileNotFoundError(f"input directory not found: {input_dir}")

    rows: List[Tuple[str, int, int]] = []
    bad_prefix: List[str] = []
    total_parquet = 0
    last_log_time = time.time()
    log_interval = 50000

    for dirpath, dirnames, filenames in os.walk(input_dir):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if not filename.lower().endswith(".parquet"):
                continue
            total_parquet += 1

            # Heartbeat logging
            if total_parquet % log_interval == 0:
                elapsed = time.time() - last_log_time
                print(f"[SplitPreflight] scanning... found {total_parquet} parquet files so far ({elapsed:.2f}s since last log)", flush=True)
                last_log_time = time.time()

                if status_json_path:
                    interim_payload = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "running",
                        "input_dir": str(input_dir),
                        "scanned_count": total_parquet,
                        "message": "scanning in progress"
                    }
                    try:
                        _write_json_atomic(status_json_path, interim_payload)
                    except Exception:
                        pass # Non-blocking write failure

            m = DATE_PREFIX_RE.match(filename)
            if m is None:
                bad_prefix.append(filename)
                continue
            d = m.group("date")
            year = int(d[:4])
            ym = int(d[:6])
            rows.append((str((Path(dirpath) / filename).resolve()), year, ym))
    return rows, bad_prefix, total_parquet


def preflight(
    input_dir: Path,
    train_years: Set[int],
    backtest_years: Set[int],
    backtest_year_months: Set[int],
    allow_unparsed_date_prefix: bool,
    status_json_path: Path | None = None,
) -> Dict:
    rows, bad_prefix, total_parquet = _scan_frame_files(input_dir, status_json_path)
    
    print(f"[SplitPreflight] processing {len(rows)} rows...", flush=True)
    
    if bad_prefix and not allow_unparsed_date_prefix:
        preview = bad_prefix[:20]
        raise RuntimeError(
            "found parquet files without YYYYMMDD_ prefix; "
            f"count={len(bad_prefix)}, examples={preview}"
        )

    # Use sets for O(1) membership lookups
    train_set_lookup = {
        p
        for p, year, _ym in rows
        if year in train_years
    }
    backtest_set_lookup = {
        p
        for p, year, ym in rows
        if (year in backtest_years) or (ym in backtest_year_months)
    }

    if not train_set_lookup:
        raise RuntimeError(f"train split is empty. train_years={sorted(train_years)}")
    if not backtest_set_lookup:
        raise RuntimeError(
            "backtest split is empty. "
            f"backtest_years={sorted(backtest_years)} "
            f"backtest_year_months={sorted(backtest_year_months)}"
        )

    print("[SplitPreflight] checking overlap...", flush=True)
    overlap = sorted(train_set_lookup.intersection(backtest_set_lookup))
    if overlap:
        raise RuntimeError(
            f"train/backtest overlap detected: count={len(overlap)}, examples={overlap[:20]}"
        )

    train_year_counter: Counter[str] = Counter()
    train_month_counter: Counter[str] = Counter()
    backtest_year_counter: Counter[str] = Counter()
    backtest_month_counter: Counter[str] = Counter()
    
    print("[SplitPreflight] calculating distributions...", flush=True)
    for i, (p, year, ym) in enumerate(rows):
        if i > 0 and i % 1000000 == 0:
            print(f"[SplitPreflight] ... processed {i} rows for distribution", flush=True)
            
        if p in train_set_lookup:
            train_year_counter[str(year)] += 1
            train_month_counter[str(ym)] += 1
        if p in backtest_set_lookup:
            backtest_year_counter[str(year)] += 1
            backtest_month_counter[str(ym)] += 1

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "completed",
        "input_dir": str(input_dir),
        "total_parquet_seen": total_parquet,
        "allow_unparsed_date_prefix": bool(allow_unparsed_date_prefix),
        "unparsed_date_prefix_count": len(bad_prefix),
        "unparsed_date_prefix_examples": bad_prefix[:20],
        "filters": {
            "train_years": sorted(int(x) for x in train_years),
            "backtest_years": sorted(int(x) for x in backtest_years),
            "backtest_year_months": sorted(int(x) for x in backtest_year_months),
        },
        "train": {
            "files": len(train_set_lookup),
            "year_distribution": dict(sorted(train_year_counter.items())),
            "month_distribution": dict(sorted(train_month_counter.items())),
        },
        "backtest": {
            "files": len(backtest_set_lookup),
            "year_distribution": dict(sorted(backtest_year_counter.items())),
            "month_distribution": dict(sorted(backtest_month_counter.items())),
        },
        "overlap_count": 0,
        "overlap_examples": [],
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fail-closed dataset split preflight for v40.")
    p.add_argument("--input-dir", required=True, type=str)
    p.add_argument("--train-years", type=str, default="")
    p.add_argument("--backtest-years", type=str, default="")
    p.add_argument("--backtest-year-months", type=str, default="")
    p.add_argument("--allow-unparsed-date-prefix", action="store_true")
    p.add_argument("--status-json", type=str, default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        train_years, backtest_years, backtest_year_months = _resolve_filters(
            train_years_raw=args.train_years,
            backtest_years_raw=args.backtest_years,
            backtest_year_months_raw=args.backtest_year_months,
        )
        payload = preflight(
            input_dir=Path(args.input_dir),
            train_years=train_years,
            backtest_years=backtest_years,
            backtest_year_months=backtest_year_months,
            allow_unparsed_date_prefix=bool(args.allow_unparsed_date_prefix),
            status_json_path=Path(args.status_json) if args.status_json else None,
        )
        print(
            "[SplitPreflight] ok total={total} train={train} backtest={backtest} "
            "filters(train={train_years}, backtest={backtest_years}, ym={ym})".format(
                total=payload["total_parquet_seen"],
                train=payload["train"]["files"],
                backtest=payload["backtest"]["files"],
                train_years=payload["filters"]["train_years"],
                backtest_years=payload["filters"]["backtest_years"],
                ym=payload["filters"]["backtest_year_months"],
            )
        )
        if args.status_json:
            _write_json_atomic(Path(args.status_json), payload)
        return 0
    except Exception as exc:
        payload = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "failed",
            "input_dir": args.input_dir,
            "error": str(exc),
        }
        if args.status_json:
            _write_json_atomic(Path(args.status_json), payload)
        print(f"[SplitPreflight] failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
