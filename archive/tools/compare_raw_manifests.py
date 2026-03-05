#!/usr/bin/env python3
"""
Compare two raw manifests produced by tools/gen_raw_manifest.py.

Outputs a summary and (optionally) a files-from list you can feed into rsync/rclone.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple


def _load_manifest(path: Path) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            obj = json.loads(line)
            rel = str(obj.get("rel", ""))
            if not rel:
                continue
            out[rel] = obj
    return out


def _same(a: dict, b: dict) -> bool:
    # Prefer sha256 if present in both; otherwise size+mtime.
    if "sha256" in a and "sha256" in b:
        return str(a.get("sha256")) == str(b.get("sha256"))
    return int(a.get("size", -1)) == int(b.get("size", -2)) and int(a.get("mtime_ns", -1)) == int(b.get("mtime_ns", -2))


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare two raw manifests (jsonl).")
    ap.add_argument("--a", required=True, help="Manifest A (source-of-truth).")
    ap.add_argument("--b", required=True, help="Manifest B (mirror).")
    ap.add_argument("--out-missing-in-b", default="", help="Optional output: relpaths missing or changed in B.")
    args = ap.parse_args()

    a_path = Path(args.a)
    b_path = Path(args.b)
    a = _load_manifest(a_path)
    b = _load_manifest(b_path)

    missing_in_b = []
    changed_in_b = []
    extra_in_b = []

    for rel, a_ent in a.items():
        b_ent = b.get(rel)
        if b_ent is None:
            missing_in_b.append(rel)
            continue
        if not _same(a_ent, b_ent):
            changed_in_b.append(rel)

    for rel in b.keys():
        if rel not in a:
            extra_in_b.append(rel)

    summary = {
        "a_files": len(a),
        "b_files": len(b),
        "missing_in_b": len(missing_in_b),
        "changed_in_b": len(changed_in_b),
        "extra_in_b": len(extra_in_b),
    }
    print(json.dumps(summary, ensure_ascii=False))

    if args.out_missing_in_b:
        out = Path(args.out_missing_in_b)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as f:
            for rel in missing_in_b:
                f.write(rel + "\n")
            for rel in changed_in_b:
                f.write(rel + "\n")
        print(str(out))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

