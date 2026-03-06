import os
import sys
from pathlib import Path

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import tools.stage2_targeted_resume as targeted_resume
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


def test_main_skips_completed_and_failed_inputs(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    log_file = tmp_path / "runner.log"
    fail_file = tmp_path / "failed.txt"
    pending_file = tmp_path / "pending.txt"

    input_dir.mkdir()
    output_dir.mkdir()

    for name in ["a.parquet", "b.parquet", "c.parquet"]:
        (input_dir / name).write_text("l1", encoding="utf-8")

    (output_dir / "a.parquet").write_text("l2", encoding="utf-8")
    (output_dir / "a.parquet.done").touch()
    fail_file.write_text("b.parquet\n", encoding="utf-8")

    seen: dict[str, list[str]] = {}

    def fake_run_file_batch(*, python_bin, repo_root, l1_files, out_dir, timeout_sec):
        seen["batch"] = [p.name for p in l1_files]
        for path in l1_files:
            (out_dir / path.name).write_text("ok", encoding="utf-8")
            (out_dir / f"{path.name}.done").touch()
        stdout = "__BATCH_START__ c.parquet\n__BATCH_OK__ c.parquet\n"
        return 0, stdout, "", False

    monkeypatch.setattr(targeted_resume, "_run_file_batch", fake_run_file_batch)
    monkeypatch.setattr(targeted_resume, "_enforce_linux_heavy_slice", lambda: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "stage2_targeted_resume.py",
            "--input-dir",
            str(input_dir),
            "--output-dir",
            str(output_dir),
            "--log-file",
            str(log_file),
            "--fail-file",
            str(fail_file),
            "--pending-file",
            str(pending_file),
        ],
    )

    rc = targeted_resume.main()

    assert rc == 0
    assert seen["batch"] == ["c.parquet"]
    assert pending_file.read_text(encoding="utf-8") == "c.parquet\n"
    assert fail_file.read_text(encoding="utf-8") == "b.parquet\n"


def test_main_clears_stale_done_and_requeues_file(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    log_file = tmp_path / "runner.log"
    fail_file = tmp_path / "failed.txt"
    pending_file = tmp_path / "pending.txt"

    input_dir.mkdir()
    output_dir.mkdir()

    (input_dir / "a.parquet").write_text("l1", encoding="utf-8")
    (output_dir / "a.parquet.done").touch()

    seen: dict[str, list[str]] = {}

    def fake_run_file_batch(*, python_bin, repo_root, l1_files, out_dir, timeout_sec):
        seen["batch"] = [p.name for p in l1_files]
        for path in l1_files:
            (out_dir / path.name).write_text("ok", encoding="utf-8")
            (out_dir / f"{path.name}.done").touch()
        stdout = "__BATCH_START__ a.parquet\n__BATCH_OK__ a.parquet\n"
        return 0, stdout, "", False

    monkeypatch.setattr(targeted_resume, "_run_file_batch", fake_run_file_batch)
    monkeypatch.setattr(targeted_resume, "_enforce_linux_heavy_slice", lambda: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "stage2_targeted_resume.py",
            "--input-dir",
            str(input_dir),
            "--output-dir",
            str(output_dir),
            "--log-file",
            str(log_file),
            "--fail-file",
            str(fail_file),
            "--pending-file",
            str(pending_file),
        ],
    )

    rc = targeted_resume.main()

    assert rc == 0
    assert seen["batch"] == ["a.parquet"]
    assert pending_file.read_text(encoding="utf-8") == "a.parquet\n"
    assert "STALE_DONE_CLEARED=a.parquet" in log_file.read_text(encoding="utf-8")
    assert (output_dir / "a.parquet").exists()
    assert (output_dir / "a.parquet.done").exists()
