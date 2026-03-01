#!/usr/bin/env python3
"""
Compatibility entrypoint for v60 base-matrix forging.

Canonical implementation now lives in:
- tools/v60_forge_base_matrix_local.py

This preserves existing command paths while enforcing local ticker sharding.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from tools.v60_forge_base_matrix_local import main


if __name__ == "__main__":
    raise SystemExit(main())
