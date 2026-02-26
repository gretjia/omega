"""
OMEGA Unified Logging & Progress Tracker
==========================================
Drop-in replacement for raw print() across the OMEGA pipeline.

Features:
    - Structured log lines: timestamp + level + context + message
    - JSON-line mode for machine consumption (watchdog, cluster_health)
    - Human-readable mode for terminal (default)
    - Progress tracker with ETA and throughput
    - Zero external dependencies (stdlib only)

Usage:
    from omega_core.omega_log import get_logger, ProgressTracker

    log = get_logger("stage2")
    log.info("Starting physics compute", file="20230410.parquet", rows=50000)
    log.warn("Polars panic detected, falling back to scan path")
    log.guardrail("POLARS_MAX_THREADS capped 8 -> 2", workers=4)

    tracker = ProgressTracker(total=552, label="Stage2")
    tracker.update(1)   # prints progress bar + ETA
    tracker.done()       # prints final summary

Environment:
    OMEGA_LOG_FORMAT=json     → JSON-line output (default: human)
    OMEGA_LOG_LEVEL=DEBUG     → minimum level (default: INFO)
    OMEGA_LOG_FILE=/path      → also write to file (default: stderr only)
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Optional, TextIO


# ── Log levels ──

LEVELS = {"DEBUG": 10, "INFO": 20, "WARN": 30, "GUARDRAIL": 35, "ERROR": 40, "FATAL": 50}
_LEVEL_NAMES = {v: k for k, v in LEVELS.items()}


def _parse_level(raw: str) -> int:
    """Parse level from string, defaulting to INFO."""
    return LEVELS.get(raw.upper().strip(), LEVELS["INFO"])


# ── Logger ──

class OmegaLogger:
    """Structured logger for OMEGA pipelines.

    Each log line includes: timestamp, level, context, message, and optional kv pairs.
    Outputs to stderr (never stdout) to avoid polluting data streams.
    """

    def __init__(
        self,
        context: str,
        *,
        fmt: str = "human",
        level: int = LEVELS["INFO"],
        stream: TextIO | None = None,
        file_path: str | None = None,
    ):
        self.context = context
        self.fmt = fmt
        self.level = level
        self.stream = stream or sys.stderr
        self._file: TextIO | None = None
        if file_path:
            os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
            self._file = open(file_path, "a", encoding="utf-8")

    def _emit(self, level: int, msg: str, **kv: Any) -> None:
        if level < self.level:
            return

        ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        level_name = _LEVEL_NAMES.get(level, "INFO")

        if self.fmt == "json":
            record = {
                "ts": ts,
                "level": level_name,
                "ctx": self.context,
                "msg": msg,
            }
            if kv:
                record["data"] = kv
            line = json.dumps(record, default=str, ensure_ascii=False)
        else:
            # Human-readable: [timestamp] [LEVEL] [context] message  key=value ...
            kv_str = ""
            if kv:
                kv_str = "  " + " ".join(f"{k}={v}" for k, v in kv.items())
            line = f"[{ts}] [{level_name:<9}] [{self.context}] {msg}{kv_str}"

        print(line, file=self.stream, flush=True)
        if self._file:
            print(line, file=self._file, flush=True)

    def debug(self, msg: str, **kv: Any) -> None:
        self._emit(LEVELS["DEBUG"], msg, **kv)

    def info(self, msg: str, **kv: Any) -> None:
        self._emit(LEVELS["INFO"], msg, **kv)

    def warn(self, msg: str, **kv: Any) -> None:
        self._emit(LEVELS["WARN"], msg, **kv)

    def guardrail(self, msg: str, **kv: Any) -> None:
        self._emit(LEVELS["GUARDRAIL"], msg, **kv)

    def error(self, msg: str, **kv: Any) -> None:
        self._emit(LEVELS["ERROR"], msg, **kv)

    def fatal(self, msg: str, **kv: Any) -> None:
        self._emit(LEVELS["FATAL"], msg, **kv)

    def child(self, sub_context: str) -> "OmegaLogger":
        """Create a child logger with a sub-context prefix."""
        return OmegaLogger(
            context=f"{self.context}.{sub_context}",
            fmt=self.fmt,
            level=self.level,
            stream=self.stream,
            file_path=None,  # share parent file handle
        )

    def close(self) -> None:
        if self._file:
            self._file.close()
            self._file = None


def get_logger(context: str = "omega", **overrides: Any) -> OmegaLogger:
    """Factory that reads config from env vars.

    Args:
        context: Logger context name (e.g., "stage2", "deploy", "health")
        **overrides: Override fmt, level, file_path directly

    Returns:
        Configured OmegaLogger instance
    """
    fmt = overrides.get("fmt", os.environ.get("OMEGA_LOG_FORMAT", "human"))
    level_str = overrides.get("level", os.environ.get("OMEGA_LOG_LEVEL", "INFO"))
    file_path = overrides.get("file_path", os.environ.get("OMEGA_LOG_FILE"))

    level = _parse_level(str(level_str)) if isinstance(level_str, str) else level_str

    return OmegaLogger(context=context, fmt=fmt, level=level, file_path=file_path)


# ── Progress tracker ──

class ProgressTracker:
    """Track progress of batch operations with ETA.

    Usage:
        tracker = ProgressTracker(total=552, label="Stage2 files")
        for file in files:
            process(file)
            tracker.update(1)
        tracker.done()
    """

    def __init__(
        self,
        total: int,
        label: str = "Progress",
        *,
        logger: OmegaLogger | None = None,
        report_every: int = 1,
    ):
        self.total = total
        self.label = label
        self.logger = logger or get_logger("progress")
        self.report_every = max(1, report_every)
        self.completed = 0
        self.failed = 0
        self.skipped = 0
        self.t0 = time.time()
        self._last_report = 0

    def update(self, n: int = 1, *, status: str = "ok") -> None:
        """Record completion of n items."""
        if status == "ok" or status == "completed":
            self.completed += n
        elif status == "skipped":
            self.skipped += n
        elif status == "failed":
            self.failed += n
        else:
            self.completed += n

        done = self.completed + self.failed + self.skipped
        if done - self._last_report >= self.report_every:
            self._report(done)
            self._last_report = done

    def _report(self, done: int) -> None:
        elapsed = time.time() - self.t0
        pct = (done / self.total * 100) if self.total > 0 else 0
        rate = done / elapsed if elapsed > 0 else 0
        remaining = (self.total - done) / rate if rate > 0 else 0

        # Format ETA
        if remaining > 3600:
            eta_str = f"{remaining / 3600:.1f}h"
        elif remaining > 60:
            eta_str = f"{remaining / 60:.1f}m"
        else:
            eta_str = f"{remaining:.0f}s"

        self.logger.info(
            f"{self.label}: {done}/{self.total} ({pct:.1f}%)",
            elapsed=f"{elapsed:.1f}s",
            eta=eta_str,
            ok=self.completed,
            fail=self.failed,
            skip=self.skipped,
        )

    def done(self) -> dict:
        """Finalize and return summary."""
        elapsed = time.time() - self.t0
        total_done = self.completed + self.failed + self.skipped
        summary = {
            "label": self.label,
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
            "elapsed_s": round(elapsed, 1),
        }
        self.logger.info(
            f"{self.label} DONE: {self.completed} ok, {self.failed} failed, {self.skipped} skipped in {elapsed:.1f}s",
        )
        return summary
