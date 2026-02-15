#!/usr/bin/env python3
"""
Build deterministic archive manifests + two shards for distributed framing.

This is intentionally filesystem-only (no file hashing) so it can run fast on
multi-TB datasets.

Outputs (default under audit/runtime/v52/):
  - archive_manifest_7z.txt
  - shard_windows1.txt
  - shard_linux.txt
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Iterable, List, Tuple


_DATE_RE = re.compile(r"^(\\d{8})")


def _iter_archives(root: Path, ext: str) -> Iterable[Path]:
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if ext and not fn.lower().endswith(ext.lower()):
                continue
            yield Path(dirpath) / fn


def _rel_posix(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix()


def _pick_shard(rel: str, rule: str) -> int:
    """
    Returns shard id: 0 or 1.
    """
    base = Path(rel).name
    if rule == "date_mod2":
        m = _DATE_RE.match(base)
        if m:
            try:
                return int(m.group(1)) % 2
            except Exception:
                pass
        # fallback to hash if date not parseable
        rule = "hash_mod2"

    if rule == "hash_mod2":
        h = hashlib.sha1(rel.encode("utf-8", errors="replace")).digest()
        return int(h[0]) % 2

    raise ValueError(f"Unknown rule: {rule}")


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build two deterministic shards from a raw .7z dataset.")
    ap.add_argument("--root", required=True, help="Root directory containing raw .7z archives.")
    ap.add_argument("--ext", default=".7z", help="Archive extension filter (default .7z).")
    ap.add_argument("--out-dir", default="audit/runtime/v52", help="Output directory (default audit/runtime/v52).")
    ap.add_argument("--rule", choices=["date_mod2", "hash_mod2"], default="date_mod2", help="Shard rule.")
    ap.add_argument("--a-name", default="shard_windows1.txt", help="Shard A filename.")
    ap.add_argument("--b-name", default="shard_linux.txt", help="Shard B filename.")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Root not found: {root}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rels: List[str] = []
    for p in _iter_archives(root, ext=str(args.ext)):
        rels.append(_rel_posix(p, root))
    rels = sorted(set(rels))

    shard_a: List[str] = []
    shard_b: List[str] = []
    for rel in rels:
        shard = _pick_shard(rel, rule=str(args.rule))
        if shard == 0:
            shard_a.append(rel)
        else:
            shard_b.append(rel)

    _atomic_write_text(out_dir / "archive_manifest_7z.txt", "\n".join(rels) + ("\n" if rels else ""))
    _atomic_write_text(out_dir / str(args.a_name), "\n".join(shard_a) + ("\n" if shard_a else ""))
    _atomic_write_text(out_dir / str(args.b_name), "\n".join(shard_b) + ("\n" if shard_b else ""))

    summary = {
        "root": str(root),
        "ext": str(args.ext),
        "rule": str(args.rule),
        "total": len(rels),
        "shard_a": len(shard_a),
        "shard_b": len(shard_b),
        "out_dir": str(out_dir),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

