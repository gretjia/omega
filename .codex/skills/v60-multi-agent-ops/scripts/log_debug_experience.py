#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[2] / "multi-agent-ops" / "scripts" / "log_debug_experience.py"

if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, str(TARGET), *sys.argv[1:]]))
