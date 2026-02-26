from __future__ import annotations

import os
import sys

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.stage2_physics_compute import (
    _maybe_skip_pathological_symbol_failure,
    _profile_symbol_time_density,
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
