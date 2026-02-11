"""
build_dataset_manifest_v40.py

Build strict role-based manifests for v40 train/backtest from frame parquet files.

Rules:
1. Assign files by date prefix in filename: YYYYMMDD_*.parquet
2. train role uses train years
3. backtest role uses backtest years and optional year-month prefixes
4. optional overlap guard against another manifest
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


def _load_manifest_set(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    items: Set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            items.add(str(Path(s).resolve()))
    return items


def _load_default_split_policy() -> Tuple[Set[int], Set[int], Set[int]]:
    split = TrainerConfig().split
    train_years = {int(y) for y in split.train_years}
    backtest_years = {int(y) for y in split.test_years}
    backtest_year_months = {
        int(ym) for ym in getattr(split, "test_year_months", ())  # backward compatible
    }
    return train_years, backtest_years, backtest_year_months


def _resolve_role_filters(
    role: str,
    train_years_raw: str,
    backtest_years_raw: str,
    backtest_year_months_raw: str,
) -> Tuple[Set[int], Set[int]]:
    default_train_years, default_backtest_years, default_backtest_year_months = (
        _load_default_split_policy()
    )

    if role == "train":
        years_raw = _parse_csv_list(train_years_raw)
        if years_raw:
            years = _to_int_set(years_raw, expected_len=4)
        else:
            years = default_train_years
        if not years:
            raise ValueError("train years cannot be empty")
        return years, set()

    # backtest
    years_raw = _parse_csv_list(backtest_years_raw)
    ym_raw = _parse_csv_list(backtest_year_months_raw)

    if years_raw:
        years = _to_int_set(years_raw, expected_len=4)
    else:
        years = default_backtest_years

    year_months = (
        _to_int_set(ym_raw, expected_len=6) if ym_raw else default_backtest_year_months
    )
    if not years and not year_months:
        raise ValueError("backtest filters cannot be empty (years and year-months both empty)")
    return years, year_months


def build_manifest(
    input_dir: Path,
    out_file: Path,
    role: str,
    years: Set[int],
    year_months: Set[int],
    allow_empty: bool,
    allow_unparsed_date_prefix: bool,
    overlap_manifest: Path | None,
) -> Dict:
    if not input_dir.exists():
        raise FileNotFoundError(f"input directory not found: {input_dir}")

    matched: List[str] = []
    bad_prefix: List[str] = []
    year_counter = Counter()
    month_counter = Counter()
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
                print(f"[Manifest] scanning for {role}... found {total_parquet} parquet files so far ({elapsed:.2f}s since last log)", flush=True)
                last_log_time = time.time()

            m = DATE_PREFIX_RE.match(filename)
            if m is None:
                bad_prefix.append(filename)
                continue
            d = m.group("date")
            year = int(d[:4])
            ym = int(d[:6])

            include = False
            if years and year in years:
                include = True
            if year_months and ym in year_months:
                include = True

            if include:
                abs_path = str((Path(dirpath) / filename).resolve())
                matched.append(abs_path)
                year_counter[str(year)] += 1
                month_counter[str(ym)] += 1

    if bad_prefix and not allow_unparsed_date_prefix:
        preview = bad_prefix[:20]
        raise RuntimeError(
            "found parquet files without YYYYMMDD_ prefix; "
            f"count={len(bad_prefix)}, examples={preview}"
        )

    matched = sorted(set(matched))
    if not matched and not allow_empty:
        raise RuntimeError(
            f"manifest is empty for role={role}. "
            f"filters years={sorted(years)} year_months={sorted(year_months)}"
        )

    overlap_count = 0
    overlap_examples: List[str] = []
    if overlap_manifest is not None:
        other = _load_manifest_set(overlap_manifest)
        if other:
            overlap = sorted(set(matched).intersection(other))
            overlap_count = len(overlap)
            overlap_examples = overlap[:20]
            if overlap_count > 0:
                raise RuntimeError(
                    f"role overlap detected with {overlap_manifest}: "
                    f"count={overlap_count}, examples={overlap_examples}"
                )

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8", newline="\n") as f:
        for p in matched:
            f.write(p + "\n")

    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "role": role,
        "input_dir": str(input_dir),
        "output_manifest": str(out_file),
        "total_parquet_seen": total_parquet,
        "matched_files": len(matched),
        "filters": {
            "years": sorted(int(x) for x in years),
            "year_months": sorted(int(x) for x in year_months),
        },
        "allow_empty": bool(allow_empty),
        "allow_unparsed_date_prefix": bool(allow_unparsed_date_prefix),
        "unparsed_date_prefix_count": len(bad_prefix),
        "unparsed_date_prefix_examples": bad_prefix[:20],
        "year_distribution": dict(sorted(year_counter.items())),
        "month_distribution": dict(sorted(month_counter.items())),
        "overlap_manifest": str(overlap_manifest) if overlap_manifest else "",
        "overlap_count": overlap_count,
        "overlap_examples": overlap_examples,
    }
    return payload


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build strict role-based manifest for v40.")
    p.add_argument("--input-dir", required=True, type=str)
    p.add_argument("--out-file", required=True, type=str)
    p.add_argument("--role", required=True, choices=("train", "backtest"))
    p.add_argument("--train-years", type=str, default="")
    p.add_argument("--backtest-years", type=str, default="")
    p.add_argument("--backtest-year-months", type=str, default="")
    p.add_argument("--allow-empty", action="store_true")
    p.add_argument("--allow-unparsed-date-prefix", action="store_true")
    p.add_argument("--disallow-overlap-with", type=str, default="")
    p.add_argument("--status-json", type=str, default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        years, year_months = _resolve_role_filters(
            role=args.role,
            train_years_raw=args.train_years,
            backtest_years_raw=args.backtest_years,
            backtest_year_months_raw=args.backtest_year_months,
        )
        payload = build_manifest(
            input_dir=Path(args.input_dir),
            out_file=Path(args.out_file),
            role=args.role,
            years=years,
            year_months=year_months,
            allow_empty=bool(args.allow_empty),
            allow_unparsed_date_prefix=bool(args.allow_unparsed_date_prefix),
            overlap_manifest=Path(args.disallow_overlap_with)
            if args.disallow_overlap_with
            else None,
        )
        payload["status"] = "completed"
        print(
            "[Manifest] role={role}, matched={matched}, total={total}, years={years}, year_months={ym}".format(
                role=args.role,
                matched=payload["matched_files"],
                total=payload["total_parquet_seen"],
                years=payload["filters"]["years"],
                ym=payload["filters"]["year_months"],
            ),
            flush=True
        )
        if args.status_json:
            _write_json_atomic(Path(args.status_json), payload)
        return 0
    except Exception as exc:
        payload = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "failed",
            "role": args.role,
            "input_dir": args.input_dir,
            "output_manifest": args.out_file,
            "error": str(exc),
        }
        if args.status_json:
            _write_json_atomic(Path(args.status_json), payload)
        print(f"[Manifest] failed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
