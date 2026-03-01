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


_DATE_RE = re.compile(r"^(\d{8})")


def _iter_archives(root: Path, ext: str) -> Iterable[Path]:
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if ext and not fn.lower().endswith(ext.lower()):
                continue
            yield Path(dirpath) / fn


def _rel_posix(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix()


def _pick_shard(rel: str, rule: str, ratio: Tuple[int, int]) -> int:
    """
    Returns shard id: 0 (A) or 1 (B).
    """
    wa, wb = ratio
    total_w = wa + wb
    
    # Deterministic hash for weighted split
    # MD5 is stable across platforms/python versions for this purpose
    h = int(hashlib.md5(rel.encode("utf-8", errors="replace")).hexdigest(), 16)
    
    # If rule is date-based, we use date integer as the seed for stability per day
    base = Path(rel).name
    m = _DATE_RE.match(base)
    if rule == "date_mod" and m:
        seed = int(m.group(1))
    else:
        # Fallback to file hash or if rule is "hash"
        seed = h

    # Modulo arithmetic for weights
    # 0 .. wa-1 -> Shard A
    # wa .. total-1 -> Shard B
    
    if (seed % total_w) < wa:
        return 0
    else:
        return 1


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build two deterministic shards from a raw .7z dataset.")
    ap.add_argument("--root", required=True, help="Root directory containing raw .7z archives.")
    ap.add_argument("--ext", default=".7z", help="Archive extension filter (default .7z).")
    ap.add_argument("--out-dir", default="audit/runtime/v52", help="Output directory (default audit/runtime/v52).")
    ap.add_argument("--rule", choices=["date_mod", "hash"], default="date_mod", help="Shard rule (date_mod uses YYYYMMDD, hash uses filename).")
    ap.add_argument("--ratio", default="1:1", help="Split ratio 'Windows:Linux' (e.g., '1:2' for 33%% Win / 66%% Lin).")
    ap.add_argument("--a-name", default="shard_windows1.txt", help="Shard A filename (Windows).")
    ap.add_argument("--b-name", default="shard_linux.txt", help="Shard B filename (Linux).")
    args = ap.parse_args()

    # Parse ratio
    try:
        parts = args.ratio.split(":")
        ratio = (int(parts[0]), int(parts[1]))
        if ratio[0] < 0 or ratio[1] < 0 or (ratio[0]+ratio[1]) == 0:
            raise ValueError
    except Exception:
        print(f"[!] Invalid ratio: {args.ratio}. Use '1:1', '1:2', etc.")
        return 1

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
        shard = _pick_shard(rel, rule=str(args.rule), ratio=ratio)
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
        "ratio": f"{ratio[0]}:{ratio[1]} (Win:Lin)",
        "total": len(rels),
        "shard_a_win": len(shard_a),
        "shard_b_lin": len(shard_b),
        "out_dir": str(out_dir),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
