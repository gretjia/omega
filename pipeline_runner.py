#!/usr/bin/env python3
"""
Deprecated entrypoint.

`pipeline_runner.py` (v50 line) has been archived and is intentionally blocked
to prevent mixed old/new execution paths.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    archived = repo_root / "archive" / "legacy_v50" / "pipeline_runner_v50.py"
    msg = (
        "[DEPRECATED] pipeline_runner.py has been archived and is disabled.\n"
        f"Archived source: {archived}\n"
        "Use the v62 two-stage entrypoints instead:\n"
        "  1) tools/stage1_linux_base_etl.py or tools/stage1_windows_base_etl.py\n"
        "  2) tools/stage2_physics_compute.py\n"
    )
    print(msg, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
