#!/usr/bin/env python3
"""
Audit manifest integrity and parquet row statistics.

Usage:
  python tools/audit_manifest_parquet_rows.py \
      --manifest audit/v5_runtime/windows/manifests/train_files.txt \
      --status-json audit/v5_runtime/windows/train/train_status.json \
      --output audit/v5_runtime/windows/pipeline/train_manifest_audit.json
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Dict, Iterable, List, Optional, Tuple


def _read_manifest(path: Path) -> List[str]:
    raw = path.read_bytes()
    text = None
    for enc in ("utf-8-sig", "utf-16", "utf-16le", "utf-16be"):
        try:
            text = raw.decode(enc)
            break
        except Exception:
            continue
    if text is None:
        text = raw.decode("latin-1")
    lines = []
    for line in text.splitlines():
        s = line.strip().strip("\ufeff")
        if not s:
            continue
        lines.append(s)
    return lines


def _get_rows(path: str) -> int:
    # Prefer pyarrow metadata for speed and no full scan.
    try:
        import pyarrow.parquet as pq  # type: ignore

        return int(pq.ParquetFile(path).metadata.num_rows)
    except Exception:
        pass

    # Fallback to polars lazy count.
    import polars as pl  # type: ignore

    return int(pl.scan_parquet(path).select(pl.len()).collect().item())


def _year_from_name(path: str) -> str:
    base = os.path.basename(path)
    stem = os.path.splitext(base)[0]
    if len(stem) >= 4 and stem[:4].isdigit():
        return stem[:4]
    return "unknown"


def _root_from_path(path: str) -> str:
    # Normalize separators; keep drive prefix on Windows.
    p = path.replace("\\", "/")
    parts = p.split("/")
    if len(parts) >= 4:
        return "/".join(parts[:4])
    return p


def _top_k_pairs(items: Iterable[Tuple[str, int]], k: int) -> List[Dict[str, object]]:
    return [{"path": p, "rows": int(r)} for p, r in sorted(items, key=lambda x: x[1], reverse=True)[:k]]


def audit_manifest(manifest_path: Path, status_path: Optional[Path]) -> Dict[str, object]:
    entries = _read_manifest(manifest_path)
    total_entries = len(entries)
    counts = Counter(entries)
    duplicates = sorted([p for p, c in counts.items() if c > 1])
    unique_paths = list(counts.keys())

    missing: List[str] = []
    rows_by_path: Dict[str, int] = {}
    errors: List[Tuple[str, str]] = []

    for p in unique_paths:
        if not os.path.exists(p):
            missing.append(p)
            continue
        try:
            rows_by_path[p] = _get_rows(p)
        except Exception as exc:
            errors.append((p, str(exc)))

    row_values = list(rows_by_path.values())
    total_rows = int(sum(row_values))

    year_files = Counter()
    year_rows = defaultdict(int)
    root_files = Counter()
    root_rows = defaultdict(int)
    for p, r in rows_by_path.items():
        y = _year_from_name(p)
        rt = _root_from_path(p)
        year_files[y] += 1
        year_rows[y] += int(r)
        root_files[rt] += 1
        root_rows[rt] += int(r)

    status_obj = None
    status_compare = None
    if status_path and status_path.exists():
        status_obj = json.loads(status_path.read_text(encoding="utf-8"))
        status_rows = status_obj.get("total_rows")
        status_files = status_obj.get("files_selected", status_obj.get("total_tasks"))
        status_compare = {
            "status_total_rows": status_rows,
            "status_files_selected_or_tasks": status_files,
            "manifest_total_rows": total_rows,
            "manifest_unique_files": len(unique_paths),
            "rows_match": (int(status_rows) == total_rows) if isinstance(status_rows, int) else None,
            "files_match": (int(status_files) == len(unique_paths)) if isinstance(status_files, int) else None,
        }

    summary = {
        "manifest_path": str(manifest_path),
        "total_entries": total_entries,
        "unique_entries": len(unique_paths),
        "duplicate_entry_count": len(duplicates),
        "duplicates": duplicates[:20],
        "missing_count": len(missing),
        "missing_examples": missing[:20],
        "read_error_count": len(errors),
        "read_error_examples": [{"path": p, "error": e} for p, e in errors[:10]],
        "total_rows_from_parquet": total_rows,
        "rows_stats": {
            "count": len(row_values),
            "min": int(min(row_values)) if row_values else None,
            "max": int(max(row_values)) if row_values else None,
            "mean": float(mean(row_values)) if row_values else None,
            "median": float(median(row_values)) if row_values else None,
        },
        "top_5_largest_files": _top_k_pairs(rows_by_path.items(), 5),
        "year_breakdown": {
            y: {"files": int(year_files[y]), "rows": int(year_rows[y])}
            for y in sorted(year_files.keys())
        },
        "root_breakdown": {
            r: {"files": int(root_files[r]), "rows": int(root_rows[r])}
            for r in sorted(root_files.keys())
        },
        "status_compare": status_compare,
    }
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Path to manifest txt")
    ap.add_argument("--status-json", default="", help="Optional status json to compare totals")
    ap.add_argument("--output", required=True, help="Output json path")
    args = ap.parse_args()

    manifest = Path(args.manifest)
    status = Path(args.status_json) if args.status_json else None
    out = Path(args.output)

    result = audit_manifest(manifest, status)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    print(json.dumps(result.get("status_compare", {}), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
