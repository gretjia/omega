#!/usr/bin/env python3
"""
Read v40 runtime status snapshots/log tails for frame/train/backtest.
Designed for Mac-side monitoring of Windows execution via shared folder.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def tail_lines(path: Path, n: int) -> List[str]:
    if not path.exists() or n <= 0:
        return []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return [ln.rstrip("\n") for ln in lines[-n:]]
    except Exception:
        return []


def parse_ts(ts: str) -> float:
    if not ts:
        return 0.0
    try:
        return time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S"))
    except Exception:
        return 0.0


def stale_minutes(ts: str) -> float:
    t = parse_ts(ts)
    if t <= 0:
        return -1.0
    return max(0.0, (time.time() - t) / 60.0)


def summarize_stage(name: str, status: Dict[str, Any], log_tail: List[str], stale_limit: float) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "stage": name,
        "status": status.get("status", "missing"),
        "timestamp": status.get("timestamp", ""),
        "stale_min": round(stale_minutes(str(status.get("timestamp", ""))), 2),
        "summary": {},
        "warnings": [],
        "log_tail": log_tail,
    }

    if name == "frame":
        out["summary"] = {
            "archives_completed_in_run": status.get("archives_completed_in_run", 0),
            "archives_remaining_in_run": status.get("archives_remaining_in_run", 0),
            "parquet_files_written_in_run": status.get("parquet_files_written_in_run", 0),
        }
    elif name == "train":
        out["summary"] = {
            "files_done_in_run": status.get("files_done_in_run", 0),
            "files_remaining": status.get("files_remaining", 0),
            "total_rows": status.get("total_rows", 0),
            "latest_checkpoint": status.get("latest_checkpoint", ""),
        }
    elif name == "backtest":
        out["summary"] = {
            "files_processed_in_run": status.get("files_processed_in_run", 0),
            "files_remaining": status.get("files_remaining", 0),
            "total_rows": status.get("total_rows", 0),
            "total_trades": status.get("total_trades", 0),
            "total_pnl": status.get("total_pnl", 0.0),
            "error_count": status.get("error_count", 0),
        }

    sm = out["stale_min"]
    if sm >= stale_limit:
        out["warnings"].append(f"status stale for {sm:.1f} min")

    if name == "train":
        if out["summary"].get("files_done_in_run", 0) > 0 and not out["summary"].get("latest_checkpoint"):
            out["warnings"].append("no checkpoint path reported yet")
    if name == "backtest":
        if out["summary"].get("error_count", 0) > 0:
            out["warnings"].append("worker errors detected")
        if out["summary"].get("files_processed_in_run", 0) > 0 and out["summary"].get("total_rows", 0) == 0:
            out["warnings"].append("processed files but total_rows=0")

    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Show v40 runtime status for frame/train/backtest")
    p.add_argument(
        "--runtime-root",
        default="/Volumes/desktop-41jidl2/Omega_vNext/audit/v40_runtime/windows",
        help="Runtime root containing frame/train/backtest status",
    )
    p.add_argument("--tail", type=int, default=3, help="Tail N lines for each stage log")
    p.add_argument("--stale-min", type=float, default=10.0, help="Warn if status is older than this")
    p.add_argument("--json", action="store_true", help="Emit JSON only")
    args = p.parse_args()

    root = Path(args.runtime_root)
    stages = {
        "frame": (root / "frame" / "frame_status.json", root / "frame" / "frame.log"),
        "train": (root / "train" / "train_status.json", root / "train" / "train.log"),
        "backtest": (root / "backtest" / "backtest_status.json", root / "backtest" / "backtest.log"),
    }

    result = {
        "runtime_root": str(root),
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stages": [],
    }

    for name, (status_path, log_path) in stages.items():
        status = load_json(status_path)
        log_tail = tail_lines(log_path, args.tail)
        result["stages"].append(summarize_stage(name, status, log_tail, float(args.stale_min)))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"Runtime root: {result['runtime_root']}")
    print(f"Generated at: {result['generated_at']}")
    print("=" * 72)
    for st in result["stages"]:
        print(f"[{st['stage']}] status={st['status']} ts={st['timestamp']} stale={st['stale_min']} min")
        for k, v in st["summary"].items():
            print(f"  - {k}: {v}")
        if st["warnings"]:
            for w in st["warnings"]:
                print(f"  ! warning: {w}")
        if st["log_tail"]:
            print("  tail:")
            for ln in st["log_tail"]:
                print(f"    {ln}")
        print("-" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
