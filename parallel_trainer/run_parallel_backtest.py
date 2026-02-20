#!/usr/bin/env python3
"""Version-agnostic entrypoint for parallel backtesting."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    target = Path(__file__).with_name("run_parallel_backtest_v31.py")
    runpy.run_path(str(target), run_name="__main__")
