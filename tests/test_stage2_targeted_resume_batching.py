import os
import sys
from pathlib import Path

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.stage2_targeted_resume import _chunk_paths, _parse_batch_markers, _run_file_batch


def test_parse_batch_markers_collects_started_ok_fail():
    stdout = "\n".join(
        [
            "__BATCH_START__ a.parquet",
            "__BATCH_OK__ a.parquet",
            "__BATCH_START__ b.parquet",
            "__BATCH_FAIL__ b.parquet",
        ]
    )
    stderr = "__BATCH_START__ c.parquet\n"

    started, ok, failed = _parse_batch_markers(stdout, stderr)

    assert started == {"a.parquet", "b.parquet", "c.parquet"}
    assert ok == {"a.parquet"}
    assert failed == {"b.parquet"}


def test_chunk_paths_enforces_min_chunk_size_one():
    items = [Path("f1"), Path("f2"), Path("f3")]
    chunks = list(_chunk_paths(items, 0))
    assert chunks == [[Path("f1")], [Path("f2")], [Path("f3")]]


def test_run_file_batch_empty_returns_noop(tmp_path):
    rc, stdout, stderr, timed_out = _run_file_batch(
        python_bin=sys.executable,
        repo_root=tmp_path,
        l1_files=[],
        out_dir=tmp_path,
        timeout_sec=1,
    )
    assert rc == 0
    assert stdout == ""
    assert stderr == ""
    assert timed_out is False

