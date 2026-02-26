"""
Unit tests for omega_core/omega_log.py
"""
import io
import json
import time
import pytest

# Add project root to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from omega_core.omega_log import OmegaLogger, ProgressTracker, get_logger, LEVELS


class TestOmegaLogger:
    """Test structured logging output."""

    def test_info_human_format(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="human", level=LEVELS["DEBUG"], stream=buf)
        log.info("hello world")
        line = buf.getvalue().strip()
        assert "[INFO" in line
        assert "[test]" in line
        assert "hello world" in line

    def test_info_json_format(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="json", level=LEVELS["DEBUG"], stream=buf)
        log.info("starting", file="foo.parquet", rows=100)
        record = json.loads(buf.getvalue().strip())
        assert record["level"] == "INFO"
        assert record["ctx"] == "test"
        assert record["msg"] == "starting"
        assert record["data"]["file"] == "foo.parquet"
        assert record["data"]["rows"] == 100

    def test_level_filtering(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="human", level=LEVELS["WARN"], stream=buf)
        log.debug("should not appear")
        log.info("should not appear")
        log.warn("should appear")
        lines = [l for l in buf.getvalue().strip().split("\n") if l.strip()]
        assert len(lines) == 1
        assert "should appear" in lines[0]

    def test_guardrail_level(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="human", level=LEVELS["DEBUG"], stream=buf)
        log.guardrail("thread budget capped")
        line = buf.getvalue().strip()
        assert "GUARDRAIL" in line

    def test_kv_pairs_in_human_format(self):
        buf = io.StringIO()
        log = OmegaLogger("stage2", fmt="human", level=LEVELS["DEBUG"], stream=buf)
        log.info("batch complete", batch=3, rows=5000)
        line = buf.getvalue().strip()
        assert "batch=3" in line
        assert "rows=5000" in line

    def test_child_logger(self):
        buf = io.StringIO()
        log = OmegaLogger("stage2", fmt="human", level=LEVELS["DEBUG"], stream=buf)
        child = log.child("20230410.parquet")
        child.info("processing")
        line = buf.getvalue().strip()
        assert "stage2.20230410.parquet" in line

    def test_fatal_level(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="json", level=LEVELS["DEBUG"], stream=buf)
        log.fatal("out of memory")
        record = json.loads(buf.getvalue().strip())
        assert record["level"] == "FATAL"
        assert record["msg"] == "out of memory"

    def test_json_no_data_when_no_kv(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="json", level=LEVELS["DEBUG"], stream=buf)
        log.info("simple message")
        record = json.loads(buf.getvalue().strip())
        assert "data" not in record

    def test_all_levels_emitted_at_debug(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="human", level=LEVELS["DEBUG"], stream=buf)
        log.debug("d")
        log.info("i")
        log.warn("w")
        log.guardrail("g")
        log.error("e")
        log.fatal("f")
        lines = [l for l in buf.getvalue().strip().split("\n") if l.strip()]
        assert len(lines) == 6


class TestProgressTracker:
    """Test progress tracking with ETA."""

    def test_basic_tracking(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="human", level=LEVELS["DEBUG"], stream=buf)
        tracker = ProgressTracker(total=10, label="test", logger=log, report_every=5)
        for _ in range(10):
            tracker.update(1)
        summary = tracker.done()
        assert summary["completed"] == 10
        assert summary["failed"] == 0
        assert summary["total"] == 10

    def test_mixed_status(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="human", level=LEVELS["DEBUG"], stream=buf)
        tracker = ProgressTracker(total=10, label="test", logger=log, report_every=100)
        tracker.update(5, status="ok")
        tracker.update(2, status="failed")
        tracker.update(3, status="skipped")
        summary = tracker.done()
        assert summary["completed"] == 5
        assert summary["failed"] == 2
        assert summary["skipped"] == 3

    def test_report_every(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="json", level=LEVELS["DEBUG"], stream=buf)
        tracker = ProgressTracker(total=10, label="Files", logger=log, report_every=3)
        for _ in range(10):
            tracker.update(1)
        tracker.done()
        lines = [l for l in buf.getvalue().strip().split("\n") if l.strip()]
        # Should have progress reports at 3, 6, 9 + final done = 4 lines
        assert len(lines) >= 4

    def test_eta_included(self):
        buf = io.StringIO()
        log = OmegaLogger("test", fmt="human", level=LEVELS["DEBUG"], stream=buf)
        tracker = ProgressTracker(total=100, label="Files", logger=log, report_every=1)
        tracker.update(1)
        line = buf.getvalue().strip()
        assert "eta=" in line


class TestGetLogger:
    """Test factory function."""

    def test_default_logger(self):
        log = get_logger("myctx")
        assert log.context == "myctx"
        assert log.fmt == "human"
        assert log.level == LEVELS["INFO"]

    def test_override_level(self):
        log = get_logger("myctx", level="DEBUG")
        assert log.level == LEVELS["DEBUG"]

    def test_override_fmt(self):
        log = get_logger("myctx", fmt="json")
        assert log.fmt == "json"
