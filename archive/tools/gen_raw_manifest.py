#!/usr/bin/env python3
"""
Generate a lightweight manifest for raw Level-2 archives (e.g., .7z) to support
cross-machine mirroring and drift detection without moving data through Git.

Example:
  python tools/gen_raw_manifest.py \\
    --root /mnt/usb4/raw_level2 \\
    --ext .7z \\
    --out audit/runtime/v52/raw_manifest_linux.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Iterator, Optional, Tuple


def _iter_files(root: Path, ext: str) -> Iterator[Path]:
    # Use os.walk for predictable, low-overhead traversal.
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if ext and not fn.lower().endswith(ext.lower()):
                continue
            yield Path(dirpath) / fn


def _sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _relpath(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    # Force POSIX separators for cross-OS portability.
    return rel.as_posix()


def build_manifest(root: Path, ext: str, hash_mode: str) -> Tuple[int, int, list[dict]]:
    items: list[dict] = []
    n = 0
    total = 0
    for p in sorted(_iter_files(root, ext), key=lambda x: x.as_posix()):
        try:
            st = p.stat()
        except FileNotFoundError:
            continue
        entry: dict = {
            "rel": _relpath(p, root),
            "size": int(st.st_size),
            "mtime_ns": int(st.st_mtime_ns),
        }
        if hash_mode == "sha256":
            entry["sha256"] = _sha256_file(p)
        items.append(entry)
        n += 1
        total += int(st.st_size)
    return n, total, items


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate raw archive manifest (jsonl).")
    ap.add_argument("--root", required=True, help="Root directory to scan.")
    ap.add_argument("--ext", default=".7z", help="File extension filter (default: .7z). Use '' for all files.")
    ap.add_argument("--hash", dest="hash_mode", choices=["none", "sha256"], default="none", help="Optional per-file hash.")
    ap.add_argument("--out", required=True, help="Output manifest path (jsonl).")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")

    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)

    n, total, items = build_manifest(root, ext=str(args.ext), hash_mode=str(args.hash_mode))

    # JSONL for streaming + diff friendliness.
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    summary = {
        "root": str(root),
        "ext": str(args.ext),
        "hash": str(args.hash_mode),
        "files": int(n),
        "total_bytes": int(total),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

