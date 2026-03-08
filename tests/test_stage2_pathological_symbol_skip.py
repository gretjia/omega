from __future__ import annotations

import os
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.stage2_physics_compute import (
    _iter_complete_symbol_frames_from_parquet,
    _maybe_skip_pathological_symbol_failure,
    _profile_symbol_time_density,
    process_chunk,
)


def _write_probe_parquet(path, symbol, n_rows, times):
    time_vals = [times[i % len(times)] for i in range(n_rows)]
    table = pa.table(
        {
            "symbol": [symbol] * n_rows,
            "time": time_vals,
            "__time_ms": [1_700_000_000_000 + i for i in range(n_rows)],
        }
    )
    pq.write_table(table, path)


def test_pathological_symbol_is_skip_eligible(tmp_path, monkeypatch):
    p = tmp_path / "pathological.parquet"
    _write_probe_parquet(p, "123257.SZ", n_rows=60000, times=[145700000, 150000000])

    prof = _profile_symbol_time_density(str(p), "123257.SZ", unique_cap=2)
    assert prof["rows"] == 60000
    assert prof["unique_times"] == 2
    assert prof["has_time"] is True

    monkeypatch.setenv("OMEGA_STAGE2_SKIP_PATHOLOGICAL_SYMBOL_ON_FAIL", "1")
    monkeypatch.setenv("OMEGA_STAGE2_PATHO_SYMBOL_MIN_ROWS", "50000")
    monkeypatch.setenv("OMEGA_STAGE2_PATHO_SYMBOL_MAX_UNIQUE_TIMES", "2")

    assert _maybe_skip_pathological_symbol_failure(
        l1_file=str(p),
        file_name="unit-test",
        symbol="123257.SZ",
        rc=3221225477,
    )


def test_non_pathological_symbol_is_not_auto_skipped(tmp_path, monkeypatch):
    p = tmp_path / "normal.parquet"
    # Same row count but with more distinct time points -> should not be auto-skipped.
    _write_probe_parquet(
        p,
        "600000.SH",
        n_rows=60000,
        times=[93000000, 100000000, 110000000, 130000000],
    )

    prof = _profile_symbol_time_density(str(p), "600000.SH", unique_cap=2)
    assert prof["rows"] > 0
    assert prof["unique_times"] > 2

    monkeypatch.setenv("OMEGA_STAGE2_SKIP_PATHOLOGICAL_SYMBOL_ON_FAIL", "1")
    monkeypatch.setenv("OMEGA_STAGE2_PATHO_SYMBOL_MIN_ROWS", "50000")
    monkeypatch.setenv("OMEGA_STAGE2_PATHO_SYMBOL_MAX_UNIQUE_TIMES", "2")

    assert not _maybe_skip_pathological_symbol_failure(
        l1_file=str(p),
        file_name="unit-test",
        symbol="600000.SH",
        rc=3221225477,
    )


def test_iter_complete_symbol_frames_filters_non_tail_pathological_symbol(tmp_path):
    p = tmp_path / "mixed_symbols.parquet"
    pathological_rows = 12000
    normal_rows = 3

    table = pa.table(
        {
            "symbol": ["123257.SZ"] * pathological_rows + ["600000.SH"] * normal_rows,
            "time": [145700000, 150000000] * (pathological_rows // 2)
            + [93000000, 93030000, 93060000],
            "__time_ms": list(range(pathological_rows + normal_rows)),
        }
    )
    pq.write_table(table, p)

    frames = list(_iter_complete_symbol_frames_from_parquet(str(p)))

    assert len(frames) == 2
    assert frames[0].num_rows == 0
    assert frames[1].num_rows == normal_rows
    assert frames[1].column("symbol")[0].as_py() == "600000.SH"


def test_process_chunk_skips_empty_symbol_frame_and_completes(tmp_path, monkeypatch):
    l1_file = tmp_path / "20241128_b07c2229.parquet"
    out_dir = tmp_path / "l2"
    out_dir.mkdir()

    source = pa.table(
        {
            "symbol": ["600000.SH"],
            "date": ["20241128"],
            "time": [93000000],
            "__time_ms": [1],
        }
    )
    pq.write_table(source, l1_file)

    empty_symbol_tbl = pa.table({"symbol": pa.array([], type=pa.string())})
    normal_symbol_tbl = pa.table({"symbol": ["600000.SH"]})
    seen = {}

    class _DummyWriter:
        def close(self):
            return None

    def fake_iter_complete_symbol_frames(_l1_file):
        return iter([empty_symbol_tbl, normal_symbol_tbl])

    def fake_run_feature_physics_batch(batch_frames, writer, tmp_parquet):
        seen["frame_count"] = len(batch_frames)
        seen["symbols"] = [frame.column("symbol")[0].as_py() for frame in batch_frames]
        Path(tmp_parquet).write_text("ok", encoding="utf-8")
        return (_DummyWriter() if writer is None else writer), 7

    monkeypatch.setattr(
        "tools.stage2_physics_compute._iter_complete_symbol_frames_from_parquet",
        fake_iter_complete_symbol_frames,
    )
    monkeypatch.setattr(
        "tools.stage2_physics_compute._run_feature_physics_batch",
        fake_run_feature_physics_batch,
    )

    result = process_chunk({"l1_file": str(l1_file), "out_dir": str(out_dir)})

    assert result["ok"] is True
    assert result["status"] == "completed"
    assert seen["frame_count"] == 1
    assert seen["symbols"] == ["600000.SH"]
    assert (out_dir / l1_file.name).exists()
    assert (out_dir / f"{l1_file.name}.done").exists()
