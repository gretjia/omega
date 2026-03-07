#!/usr/bin/env python3
"""
v62 Stage 2 Physics Compute Agent
Reads Base_L1.parquet -> Computes MDL/SRL/Topology -> Writes Feature_L2.parquet

Anti-Fragile Fixes (Codex Validated):
  1. Explicit Symbol-Batch Loading: Prevents OOM by lazy-scanning and executing
     physics per symbol/date chunk instead of blindly loading the entire universe.
"""

import os
import sys
import glob
import argparse
import gc
import json
import re
import time
import shutil
import tempfile
import subprocess
import platform


def _setdefault_numeric_thread_caps():
    """
    Constrain nested native thread pools before importing heavy runtimes.
    Stage2 already parallelizes at the process/file level; letting Polars/BLAS/
    OpenMP all fan out independently only creates thread thrash.
    """
    cpu_count = max(1, int(os.cpu_count() or 1))
    default_polars = "2" if sys.platform == "win32" else str(max(1, cpu_count // 2))
    os.environ.setdefault("OMEGA_STAGE2_POLARS_THREADS", default_polars)
    os.environ.setdefault("NUMBA_NUM_THREADS", default_polars)
    for name in (
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OMP_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ.setdefault(name, "1")


_setdefault_numeric_thread_caps()


def _apply_windows_machine_probe_bypass():
    """
    Windows/Python 3.14 guardrail:
    platform.machine() may block on WMI in some hosts, which can deadlock
    `import polars`. Use environment-backed architecture as a stable fallback.
    """
    if sys.platform != "win32":
        return

    enabled = os.environ.get("OMEGA_WINDOWS_WMI_MACHINE_BYPASS", "1").strip().lower()
    if enabled not in {"1", "true", "yes"}:
        return

    raw_arch = (
        os.environ.get("PROCESSOR_ARCHITEW6432")
        or os.environ.get("PROCESSOR_ARCHITECTURE")
        or "AMD64"
    ).strip()
    lowered = raw_arch.lower()
    if lowered in {"amd64", "x86_64", "x64"}:
        machine = "x86_64"
    elif lowered in {"arm64", "aarch64"}:
        machine = "arm64"
    else:
        machine = raw_arch or "x86_64"

    platform.machine = lambda: machine


_apply_windows_machine_probe_bypass()
import polars as pl
from pathlib import Path
from multiprocessing import get_context

# Prevent Polars Rayon thread explosion; allow operator override for stability tuning.
_DEFAULT_POLARS_THREADS = "2" if sys.platform == "win32" else "8"
os.environ["POLARS_MAX_THREADS"] = os.environ.get(
    "OMEGA_STAGE2_POLARS_THREADS",
    _DEFAULT_POLARS_THREADS,
)
# Windows guardrail: numba import can stall/hard-hang in cp314 runtime on some hosts.
# Keep Stage2 productive by defaulting to non-JIT math path on Windows.
if sys.platform == "win32":
    os.environ.setdefault("OMEGA_DISABLE_NUMBA", "1")
    # Windows native-extension crash guardrail:
    # run heavy symbol batches in isolated subprocesses by default.
    os.environ.setdefault("OMEGA_STAGE2_ISOLATE_SYMBOL_BATCH", "1")

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l2_features_from_l1

GLOBAL_CFG = load_l2_pipeline_config()

from omega_core.kernel import apply_recursive_physics


DATE_HASH_PARQUET_RE = re.compile(r"^(?P<date>\d{8})_[0-9a-f]{7}\.parquet$")
ALLOW_USER_SLICE_ENV = "OMEGA_STAGE2_ALLOW_USER_SLICE"
TARGET_OOM_SCORE_ADJ = 300
WINDOWS_RISKY_PYTHON_MAJOR_MINOR = (3, 14)
PATHO_SYMBOL_MIN_ROWS_DEFAULT = 50000
PATHO_SYMBOL_MAX_UNIQUE_TIMES_DEFAULT = 2
_STAGE2_REQUIRED_FEATURE_COLS = {
    "symbol",
    "date",
    "open",
    "close",
    "sigma",
    "depth",
    "net_ofi",
    "trade_vol",
    "cancel_vol",
}
_STAGE2_REQUIRED_RAW_COLS = {"symbol", "date"}
_STAGE2_RAW_TIME_KEYS = ("__time_dt", "time", "time_start", "time_end")
_STAGE2_ORDER_KEYS = ("time_end", "bucket_id")


def _read_self_cgroup_path():
    """Return cgroup v2 path for current process, best-effort."""
    cgroup_file = Path("/proc/self/cgroup")
    if not cgroup_file.exists():
        return ""
    try:
        for line in cgroup_file.read_text(encoding="utf-8").splitlines():
            # cgroup v2 format: 0::/some/path
            parts = line.split(":", 2)
            if len(parts) == 3 and parts[2]:
                return parts[2]
    except Exception:
        return ""
    return ""


def _ensure_heavy_workload_slice():
    """
    Hard guardrail:
    Refuse to run stage2 outside heavy-workload.slice unless explicitly bypassed.
    """
    if sys.platform != "linux":
        return

    if os.environ.get(ALLOW_USER_SLICE_ENV, "").strip().lower() in {"1", "true", "yes"}:
        print(
            f"[WARN] {ALLOW_USER_SLICE_ENV}=1 set, bypassing heavy-workload.slice guardrail.",
            flush=True,
        )
        return

    cgroup_path = _read_self_cgroup_path()
    in_heavy_slice = (
        "/heavy-workload.slice/" in cgroup_path or cgroup_path.endswith("/heavy-workload.slice")
    )
    if in_heavy_slice:
        return

    print(
        "[FATAL] stage2 is not running in heavy-workload.slice.\n"
        f"Detected cgroup path: {cgroup_path or '<unknown>'}\n"
        "Refusing to continue to avoid user.slice OOM storms.\n"
        "Launch with: bash tools/launch_linux_stage2_heavy_slice.sh\n"
        f"(Emergency override only: export {ALLOW_USER_SLICE_ENV}=1)",
        file=sys.stderr,
        flush=True,
    )
    raise SystemExit(101)


def _raise_oom_score_adj(target=TARGET_OOM_SCORE_ADJ):
    """
    Make stage2 easier to kill under pressure, so desktop/session services survive.
    """
    if sys.platform != "linux":
        return

    oom_adj_file = Path("/proc/self/oom_score_adj")
    if not oom_adj_file.exists():
        return

    try:
        current = int(oom_adj_file.read_text(encoding="utf-8").strip())
    except Exception:
        return

    if current >= target:
        return

    try:
        oom_adj_file.write_text(str(target), encoding="utf-8")
        print(f"[GUARDRAIL] oom_score_adj raised from {current} to {target}.", flush=True)
    except Exception as exc:
        print(
            f"[WARN] Could not raise oom_score_adj from {current} to {target}: {exc}",
            flush=True,
        )


def _pool_initializer():
    _ensure_heavy_workload_slice()
    _raise_oom_score_adj()


def _is_truthy_env(name):
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def _coerce_positive_int(value, fallback):
    try:
        parsed = int(str(value).strip())
        if parsed > 0:
            return parsed
    except Exception:
        pass
    return int(fallback)


def _is_truthy_env_default(name, default):
    raw = os.environ.get(name)
    if raw is None:
        raw = default
    return str(raw).strip().lower() in {"1", "true", "yes"}


def _first_present_name(names, candidates):
    name_set = set(names)
    for cand in candidates:
        if cand in name_set:
            return cand
    return None


def _strict_batch_window_gate_enabled():
    return _is_truthy_env_default("OMEGA_STAGE2_STRICT_BATCH_WINDOW_GATE", "0")


def _audit_stage2_feature_contract(feat_df, *, window_len, require_window_reachable=True):
    missing = sorted(_STAGE2_REQUIRED_FEATURE_COLS - set(feat_df.columns))
    if missing:
        raise RuntimeError(f"missing_feature_columns:{','.join(missing)}")

    order_key = _first_present_name(feat_df.columns, _STAGE2_ORDER_KEYS)
    if order_key is None:
        raise RuntimeError("missing_order_key:time_end|bucket_id")

    group_sizes = feat_df.group_by(["symbol", "date"]).len()
    max_group_rows = int(group_sizes.select(pl.col("len").max()).item() or 0)
    eligible_groups = int(group_sizes.filter(pl.col("len") >= int(window_len)).height)
    if eligible_groups <= 0 and require_window_reachable:
        raise RuntimeError(
            f"no_groups_reach_window:window={int(window_len)},max_group_rows={max_group_rows}"
        )

    run_df = (
        feat_df.select([
            pl.col("symbol").cast(pl.Utf8, strict=False).fill_null("").alias("__sym"),
            pl.col("date").cast(pl.Utf8, strict=False).fill_null("").alias("__date"),
        ])
        .with_columns(
            (
                (pl.col("__sym") != pl.col("__sym").shift(1))
                | (pl.col("__date") != pl.col("__date").shift(1))
            ).fill_null(True).cast(pl.Int64).cum_sum().alias("__run_id")
        )
    )
    disordered_groups = int(
        run_df.group_by(["__sym", "__date"])
        .agg(pl.col("__run_id").n_unique().alias("__n_runs"))
        .filter(pl.col("__n_runs") > 1)
        .height
    )
    max_run_rows = int(
        run_df.group_by("__run_id").len().select(pl.col("len").max()).item() or 0
    )

    report = {
        "rows": int(feat_df.height),
        "window_len": int(window_len),
        "order_key": order_key,
        "eligible_groups": eligible_groups,
        "max_group_rows": max_group_rows,
        "disordered_groups": disordered_groups,
        "max_consecutive_group_rows": max_run_rows,
        "repairable_by_kernel_reorder": bool(disordered_groups > 0),
    }

    if disordered_groups > 0 and not _is_truthy_env_default("OMEGA_STAGE2_FIX_KERNEL_ORDERING", "1"):
        raise RuntimeError(
            "repairable_ordering_violation:"
            + json.dumps(report, ensure_ascii=False, sort_keys=True)
        )

    return report


def _profile_symbol_time_density(l1_file, symbol, *, unique_cap):
    """
    Probe a symbol's row count and distinct `time` cardinality with a low-memory parquet scan.
    Used only on isolated native-crash symbols to decide whether we can safely skip.
    """
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    target = str(symbol)
    total_rows = 0
    unique_times = set()
    has_time = False

    parquet = pq.ParquetFile(l1_file)
    for rg_idx in range(parquet.num_row_groups):
        rg = parquet.read_row_group(rg_idx, columns=["symbol", "time"])
        if "symbol" not in rg.column_names:
            continue
        has_time = "time" in rg.column_names

        try:
            sym_col = pc.cast(rg.column("symbol"), pa.string(), safe=False)
            mask = pc.equal(sym_col, pa.scalar(target, type=pa.string()))
            matched = rg.filter(mask)
        except Exception:
            # Conservative fallback for Arrow kernel edge cases.
            syms = rg.column("symbol").to_pylist()
            idx = [i for i, v in enumerate(syms) if str(v) == target]
            if not idx:
                continue
            matched = rg.take(pa.array(idx, type=pa.int32()))

        n = int(matched.num_rows)
        if n <= 0:
            continue

        total_rows += n
        if has_time:
            for t in matched.column("time").to_pylist():
                unique_times.add(t)
                if len(unique_times) > unique_cap:
                    # Early exit: once unique time count exceeds cap, it is not skip-eligible.
                    return {
                        "rows": total_rows,
                        "unique_times": len(unique_times),
                        "has_time": has_time,
                        "early_stop": True,
                    }

    return {
        "rows": total_rows,
        "unique_times": len(unique_times),
        "has_time": has_time,
        "early_stop": False,
    }


def _maybe_skip_pathological_symbol_failure(*, l1_file, file_name, symbol, rc):
    """
    For Windows native crash symbols, optionally skip only clearly pathological symbols
    (huge rows with extremely low distinct-time support). This keeps the file progressing
    while preserving fail-fast for normal symbols/errors.
    """
    default_enabled = "1" if sys.platform == "win32" else "0"
    if _is_truthy_env("OMEGA_STAGE2_SKIP_ANY_CRASH_SYMBOL"):
        print(
            f"[{file_name}] [WARN] Skip crash symbol by override rc={rc}: symbol={symbol}.",
            flush=True,
        )
        return True

    if not _is_truthy_env_default(
        "OMEGA_STAGE2_SKIP_PATHOLOGICAL_SYMBOL_ON_FAIL", default_enabled
    ):
        return False

    min_rows = _coerce_positive_int(
        os.environ.get("OMEGA_STAGE2_PATHO_SYMBOL_MIN_ROWS"),
        PATHO_SYMBOL_MIN_ROWS_DEFAULT,
    )
    max_unique_times = _coerce_positive_int(
        os.environ.get("OMEGA_STAGE2_PATHO_SYMBOL_MAX_UNIQUE_TIMES"),
        PATHO_SYMBOL_MAX_UNIQUE_TIMES_DEFAULT,
    )

    prof = _profile_symbol_time_density(
        l1_file,
        symbol,
        unique_cap=max_unique_times,
    )
    rows = int(prof.get("rows", 0))
    unique_times = int(prof.get("unique_times", 0))
    has_time = bool(prof.get("has_time", False))

    if has_time and rows >= min_rows and unique_times <= max_unique_times:
        print(
            f"[{file_name}] [WARN] Skip pathological symbol after native crash rc={rc}: "
            f"symbol={symbol} rows={rows} unique_time={unique_times} "
            f"(threshold rows>={min_rows}, unique_time<={max_unique_times}).",
            flush=True,
        )
        return True

    return False


def _apply_worker_thread_budget(workers):
    """
    Keep Stage2 worker/process parallelism from oversubscribing the host.
    This is an execution-only guardrail and does not change feature math.
    """
    if workers <= 1:
        return

    if _is_truthy_env("OMEGA_STAGE2_DISABLE_THREAD_BUDGET"):
        print(
            "[WARN] OMEGA_STAGE2_DISABLE_THREAD_BUDGET=1 set; skipping thread budget cap.",
            flush=True,
        )
        return

    cpu_count = max(1, int(os.cpu_count() or 1))
    current_polars = _coerce_positive_int(
        os.environ.get("POLARS_MAX_THREADS"),
        _coerce_positive_int(_DEFAULT_POLARS_THREADS, 1),
    )
    thread_budget = max(1, cpu_count // max(1, int(workers)))
    tuned_polars = min(current_polars, thread_budget)
    os.environ["POLARS_MAX_THREADS"] = str(tuned_polars)

    current_numba = _coerce_positive_int(
        os.environ.get("NUMBA_NUM_THREADS"),
        thread_budget,
    )
    tuned_numba = min(current_numba, thread_budget)
    os.environ["NUMBA_NUM_THREADS"] = str(tuned_numba)
    for name in (
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OMP_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ[name] = "1"

    try:
        import numba

        if hasattr(numba, "set_num_threads"):
            numba.set_num_threads(tuned_numba)
    except Exception:
        pass

    print(
        "[GUARDRAIL] thread budget applied "
        f"POLARS_MAX_THREADS={current_polars}->{tuned_polars}, "
        f"NUMBA_NUM_THREADS={current_numba}->{tuned_numba}, "
        "native_threads=1, "
        f"workers={workers}, cpu_count={cpu_count}",
        flush=True,
    )


def _windows_runtime_risk_notes():
    """
    Best-effort runtime risk probe for Windows native extension stability.
    """
    if sys.platform != "win32":
        return []

    notes = []
    if sys.version_info[:2] >= WINDOWS_RISKY_PYTHON_MAJOR_MINOR:
        notes.append(
            f"python {sys.version_info.major}.{sys.version_info.minor} detected "
            "(known crash risk in some native-extension workloads)"
        )

    try:
        polars_path = str(Path(pl.__file__).resolve())
    except Exception:
        polars_path = str(getattr(pl, "__file__", ""))
    if "AppData\\Roaming\\Python" in polars_path:
        notes.append(f"polars imported from user-site path: {polars_path}")

    return notes


def _dedupe_l1_files_by_date(l1_files):
    """
    Keep one Base_L1 parquet per trading date.

    If mixed-hash artifacts exist for the same date, keep the newest file by
    mtime and drop older duplicates to avoid double-processing in Stage2.
    """
    per_date = {}
    passthrough = []
    duplicates = []

    for raw in l1_files:
        p = Path(raw)
        m = DATE_HASH_PARQUET_RE.match(p.name)
        if m is None:
            passthrough.append(str(p))
            continue

        date_key = m.group("date")
        current = per_date.get(date_key)
        if current is None:
            per_date[date_key] = p
            continue

        if p.stat().st_mtime > current.stat().st_mtime:
            duplicates.append(str(current))
            per_date[date_key] = p
        else:
            duplicates.append(str(p))

    selected = [str(v) for _, v in sorted(per_date.items(), key=lambda kv: kv[0])]
    selected.extend(sorted(passthrough))
    return selected, sorted(duplicates)


def _iter_complete_symbol_frames_from_parquet(l1_file):
    """
    Iterate complete symbol blocks in file order with a single parquet pass.
    Assumes Stage1 output is sorted by symbol/date/time.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    parquet = pq.ParquetFile(l1_file)
    current_symbol = None
    current_parts = []

    for rg_idx in range(parquet.num_row_groups):
        rg_table = parquet.read_row_group(rg_idx)
        if rg_table.num_rows == 0:
            continue

        # Windows hardening:
        # Avoid Polars partition_by("symbol") panic seen on certain mixed symbol chunks.
        # Split contiguous symbol segments on Arrow side, then convert slices to Polars.
        if "symbol" not in rg_table.column_names:
            if rg_table.num_rows > 0:
                yield rg_table
            continue

        symbol_values = rg_table.column("symbol").to_pylist()
        if not symbol_values:
            continue

        seg_start = 0
        current_seg_symbol = symbol_values[0]

        for i in range(1, len(symbol_values)):
            if symbol_values[i] == current_seg_symbol:
                continue

            part = rg_table.slice(seg_start, i - seg_start)
            symbol = current_seg_symbol

            if current_symbol is None:
                current_symbol = symbol
                current_parts = [part]
            elif symbol == current_symbol:
                current_parts.append(part)
            else:
                yield pa.concat_tables(current_parts, promote_options="default")
                current_symbol = symbol
                current_parts = [part]

            seg_start = i
            current_seg_symbol = symbol_values[i]

        # Tail segment
        part = rg_table.slice(seg_start, len(symbol_values) - seg_start)
        symbol = current_seg_symbol
        if current_symbol is None:
            current_symbol = symbol
            current_parts = [part]
        elif symbol == current_symbol:
            current_parts.append(part)
        else:
            yield _filter_pathological(pa.concat_tables(current_parts, promote_options="default"))
            current_symbol = symbol
            current_parts = [part]

    if current_parts:
        yield _filter_pathological(pa.concat_tables(current_parts, promote_options="default"))

def _filter_pathological(tbl):
    import pyarrow.compute as pc
    if tbl.num_rows > 10000 and "time" in tbl.column_names:
        u_times = len(pc.unique(tbl.column("time")))
        if u_times <= 5:
            print(f"[GUARDRAIL] Proactively dropping pathological symbol (rows={tbl.num_rows}, unique_times={u_times}).", flush=True)
            return tbl.slice(0, 0)
    return tbl


def _list_symbols_from_parquet(l1_file):
    """
    Build symbol list via pyarrow row-group streaming without Polars scan.
    Preserves first-seen order in file.
    """
    symbols = []
    seen = set()
    for symbol_tbl in _iter_complete_symbol_frames_from_parquet(l1_file):
        if symbol_tbl.num_rows <= 0 or "symbol" not in symbol_tbl.column_names:
            continue
        try:
            sym = str(symbol_tbl.column("symbol")[0].as_py())
        except Exception:
            sym = str(symbol_tbl.column("symbol")[0])
        if sym not in seen:
            seen.add(sym)
            symbols.append(sym)
    return symbols


def _run_feature_physics_batch(batch_frames, writer, tmp_parquet):
    """
    Run Stage2 feature + physics on a symbol batch and append to parquet writer.
    Returns updated writer and rows written for this batch.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    rows_written = 0
    batch_df = None
    input_df = None
    arrow_table = None

    try:
        if not batch_frames:
            return writer, 0

        if isinstance(batch_frames[0], pl.DataFrame):
            input_df = pl.concat(batch_frames, how="vertical_relaxed")
        else:
            input_table = pa.concat_tables(batch_frames, promote_options="default")
            try:
                input_df = pl.from_arrow(input_table)
            except BaseException as arrow_exc:
                # Windows/Polars hardening:
                # Some parquet/arrow payloads trigger pyo3 panic in from_arrow().
                # Round-trip through parquet to normalize buffers before ingest.
                tmp_norm = Path(tempfile.mkstemp(prefix="omega_stage2_norm_", suffix=".parquet")[1])
                try:
                    pq.write_table(input_table, str(tmp_norm), compression="snappy")
                    input_df = pl.read_parquet(str(tmp_norm))
                    print(
                        f"[WARN] pl.from_arrow() failed, recovered via parquet round-trip: {arrow_exc}",
                        flush=True,
                    )
                finally:
                    try:
                        tmp_norm.unlink()
                    except Exception:
                        pass
        batch_df = build_l2_features_from_l1(input_df, GLOBAL_CFG)

        if batch_df is not None and batch_df.height > 0:
            stage2_gate = _audit_stage2_feature_contract(
                batch_df,
                window_len=int(GLOBAL_CFG.epiplexity.min_trace_len),
                require_window_reachable=_strict_batch_window_gate_enabled(),
            )
            if int(stage2_gate.get("eligible_groups", 0)) <= 0:
                print(
                    "[GATE] Stage2 batch has no window-reachable groups; "
                    f"strict_batch_gate={_strict_batch_window_gate_enabled()} "
                    f"report={json.dumps(stage2_gate, ensure_ascii=False, sort_keys=True)}",
                    flush=True,
                )
            if int(stage2_gate.get("disordered_groups", 0)) > 0:
                print(
                    "[GATE] Stage2 detected repairable ordering violation; "
                    f"kernel reorder enabled={_is_truthy_env_default('OMEGA_STAGE2_FIX_KERNEL_ORDERING', '1')} "
                    f"report={json.dumps(stage2_gate, ensure_ascii=False, sort_keys=True)}",
                    flush=True,
                )
            batch_df = apply_recursive_physics(batch_df, GLOBAL_CFG)

        if batch_df is not None and batch_df.height > 0:
            rows_written = batch_df.height
            arrow_table = batch_df.to_arrow()
            if writer is None:
                writer = pq.ParquetWriter(tmp_parquet, arrow_table.schema, compression="snappy")
            writer.write_table(arrow_table)
    finally:
        del arrow_table
        del batch_df
        del input_df
        gc.collect()

    return writer, rows_written


def _process_file_via_symbol_scan_fallback(
    *,
    l1_file,
    batch_size,
    writer,
    tmp_parquet,
    total_rows,
    file_name,
    diag_every_batches,
    t0,
    symbol_subset=None,
):
    """
    Robust fallback path for files that trigger Polars panic in Arrow conversion path.
    Uses lazy scan + symbol filter batches (slower but resilient).
    """
    lf = None
    symbol_expr = pl.col("symbol").cast(pl.Utf8, strict=False)
    isolate_batches = (
        sys.platform == "win32" and _is_truthy_env("OMEGA_STAGE2_ISOLATE_SYMBOL_BATCH")
    )
    if isolate_batches:
        all_symbols = _list_symbols_from_parquet(l1_file)
    else:
        lf = pl.scan_parquet(l1_file)
        all_symbols = (
            lf.select(symbol_expr.alias("symbol").unique().sort())
            .collect()
            .get_column("symbol")
            .to_list()
        )
    if symbol_subset:
        subset = {str(x) for x in symbol_subset if str(x)}
        all_symbols = [s for s in all_symbols if str(s) in subset]
    print(
        f"[{file_name}] Fallback path enabled: scan/filter by symbol batches ({len(all_symbols)} symbols).",
        flush=True,
    )

    batch_idx = 0
    for start in range(0, len(all_symbols), batch_size):
        sym_batch = all_symbols[start : start + batch_size]
        batch_idx += 1
        rows_written = 0

        if isolate_batches:
            writer, rows_written, rc, iso_out, iso_err = _run_windows_isolated_symbol_batch(
                l1_file=l1_file,
                symbols=sym_batch,
                writer=writer,
                tmp_parquet=tmp_parquet,
            )
            if iso_out:
                print(iso_out.rstrip(), flush=True)
            if iso_err:
                print(iso_err.rstrip(), flush=True)

            if rc != 0:
                # rc=4 means this symbol subset yielded no output rows.
                # Treat as non-fatal so one sparse/invalid symbol does not poison
                # the whole file resume run.
                if rc == 4 and len(sym_batch) <= 1:
                    one = sym_batch[0] if sym_batch else "<none>"
                    print(
                        f"[{file_name}] [WARN] Isolated symbol returned empty output, skip symbol={one}.",
                        flush=True,
                    )
                    continue
                if len(sym_batch) <= 1:
                    one = sym_batch[0] if sym_batch else "<none>"
                    if one != "<none>" and _maybe_skip_pathological_symbol_failure(
                        l1_file=l1_file,
                        file_name=file_name,
                        symbol=one,
                        rc=rc,
                    ):
                        continue
                    raise RuntimeError(
                        f"isolated symbol batch failed rc={rc} symbol={one}"
                    )
                # Split fallback: isolate each symbol to bypass batch-level native crashes.
                print(
                    f"[{file_name}] [WARN] Isolated batch failed (rc={rc}) on {len(sym_batch)} symbols, retrying single-symbol mode.",
                    flush=True,
                )
                for one_sym in sym_batch:
                    writer, one_rows, rc1, out1, err1 = _run_windows_isolated_symbol_batch(
                        l1_file=l1_file,
                        symbols=[one_sym],
                        writer=writer,
                        tmp_parquet=tmp_parquet,
                    )
                    if out1:
                        print(out1.rstrip(), flush=True)
                    if err1:
                        print(err1.rstrip(), flush=True)
                    if rc1 == 4:
                        print(
                            f"[{file_name}] [WARN] Single-symbol returned empty output, skip symbol={one_sym}.",
                            flush=True,
                        )
                        continue
                    if rc1 != 0:
                        if _maybe_skip_pathological_symbol_failure(
                            l1_file=l1_file,
                            file_name=file_name,
                            symbol=one_sym,
                            rc=rc1,
                        ):
                            continue
                        raise RuntimeError(
                            f"single-symbol isolated failure rc={rc1} symbol={one_sym}"
                        )
                    rows_written += one_rows
        else:
            if lf is None:
                lf = pl.scan_parquet(l1_file)
            batch_df = lf.filter(symbol_expr.is_in(sym_batch)).collect()
            writer, rows_written = _run_feature_physics_batch([batch_df], writer, tmp_parquet)
            del batch_df
            gc.collect()

        total_rows += rows_written
        if diag_every_batches > 0 and (batch_idx % diag_every_batches == 0):
            elapsed = time.time() - t0
            print(
                f"[{file_name}] Fallback progress batch={batch_idx} symbols_done={min(start + batch_size, len(all_symbols))}/{len(all_symbols)} rows_written={total_rows} elapsed={elapsed:.1f}s",
                flush=True,
            )

    return writer, total_rows


def _run_single_symbol_batch_file(l1_file, symbols_file, output_parquet):
    """
    Child-process entrypoint:
    process one symbol subset into one parquet chunk.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    symbols = [
        line.strip()
        for line in Path(symbols_file).read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    ]
    if not symbols:
        return 4

    symbol_set = {str(s) for s in symbols if str(s)}
    symbol_tables = []
    seen_symbols = set()
    try:
        # Fast path: iterate parquet once and only materialize requested symbols.
        for symbol_tbl in _iter_complete_symbol_frames_from_parquet(l1_file):
            if symbol_tbl.num_rows <= 0 or "symbol" not in symbol_tbl.column_names:
                continue
            try:
                symbol_name = str(symbol_tbl.column("symbol")[0].as_py())
            except Exception:
                symbol_name = str(symbol_tbl.column("symbol")[0])
            if symbol_name in symbol_set:
                if symbol_name in seen_symbols:
                    raise RuntimeError(f"duplicate_symbol_partition_detected:{symbol_name}")
                seen_symbols.add(symbol_name)
                symbol_tables.append(symbol_tbl)
                symbol_set.discard(symbol_name)
                if not symbol_set:
                    break
        if symbol_tables:
            if len(symbol_tables) == 1:
                input_table = symbol_tables[0]
            else:
                input_table = pa.concat_tables(symbol_tables, promote_options="default")
            try:
                batch_df = pl.from_arrow(input_table)
            except BaseException:
                tmp_norm = Path(tempfile.mkstemp(prefix="omega_stage2_iso_norm_", suffix=".parquet")[1])
                try:
                    pq.write_table(input_table, str(tmp_norm), compression="snappy")
                    batch_df = pl.read_parquet(str(tmp_norm))
                finally:
                    try:
                        tmp_norm.unlink()
                    except Exception:
                        pass
        else:
            batch_df = pl.DataFrame()
    except RuntimeError as exc:
        if "duplicate_symbol_partition_detected:" in str(exc):
            raise
        # Compatibility fallback for unexpected parquet-layout edge cases.
        lf = pl.scan_parquet(l1_file)
        symbol_expr = pl.col("symbol").cast(pl.Utf8, strict=False)
        batch_df = lf.filter(symbol_expr.is_in(symbols)).collect()
    except Exception:
        # Compatibility fallback for unexpected parquet-layout edge cases.
        lf = pl.scan_parquet(l1_file)
        symbol_expr = pl.col("symbol").cast(pl.Utf8, strict=False)
        batch_df = lf.filter(symbol_expr.is_in(symbols)).collect()

    if batch_df.height <= 0:
        return 4

    feat_df = build_l2_features_from_l1(batch_df, GLOBAL_CFG)
    if feat_df is None or feat_df.height <= 0:
        return 4
    try:
        stage2_gate = _audit_stage2_feature_contract(
            feat_df,
            window_len=int(GLOBAL_CFG.epiplexity.min_trace_len),
            require_window_reachable=_strict_batch_window_gate_enabled(),
        )
    except Exception as exc:
        print(f"[GATE] Stage2 feature contract failed: {exc}", flush=True)
        return 4
    if int(stage2_gate.get("eligible_groups", 0)) <= 0:
        print(
            "[GATE] Stage2 isolated batch has no window-reachable groups; "
            f"strict_batch_gate={_strict_batch_window_gate_enabled()} "
            f"report={json.dumps(stage2_gate, ensure_ascii=False, sort_keys=True)}",
            flush=True,
        )
    if int(stage2_gate.get("disordered_groups", 0)) > 0:
        print(
            "[GATE] Stage2 detected repairable ordering violation; "
            f"kernel reorder enabled={_is_truthy_env_default('OMEGA_STAGE2_FIX_KERNEL_ORDERING', '1')} "
            f"report={json.dumps(stage2_gate, ensure_ascii=False, sort_keys=True)}",
            flush=True,
        )
    feat_df = apply_recursive_physics(feat_df, GLOBAL_CFG)
    if feat_df is None or feat_df.height <= 0:
        return 4

    # Keep output schema stable with legacy Stage2 artifacts.
    cast_exprs = []
    if "n_ticks" in feat_df.columns:
        cast_exprs.append(pl.col("n_ticks").cast(pl.UInt32, strict=False).alias("n_ticks"))
    if "dominant_probe" in feat_df.columns:
        cast_exprs.append(
            pl.col("dominant_probe").cast(pl.UInt32, strict=False).alias("dominant_probe")
        )
    if cast_exprs:
        feat_df = feat_df.with_columns(cast_exprs)

    Path(output_parquet).parent.mkdir(parents=True, exist_ok=True)
    feat_df.write_parquet(output_parquet, compression="snappy")
    return 0


def _run_windows_isolated_symbol_batch(*, l1_file, symbols, writer, tmp_parquet):
    """
    Run one symbol subset in a fresh Python subprocess to isolate native crashes.
    Returns: writer, rows_written, rc, stdout, stderr
    """
    import pyarrow.parquet as pq

    tmp_dir = Path(tempfile.mkdtemp(prefix="omega_stage2_iso_"))
    symbols_file = tmp_dir / "symbols.txt"
    chunk_out = tmp_dir / "chunk.parquet"
    symbols_file.write_text("\n".join(str(s) for s in symbols) + "\n", encoding="utf-8")

    code = (
        "import sys; "
        "from tools.stage2_physics_compute import _run_single_symbol_batch_file; "
        "raise SystemExit(_run_single_symbol_batch_file(sys.argv[1], sys.argv[2], sys.argv[3]))"
    )
    env = dict(os.environ)
    env["OMEGA_STAGE2_ISOLATE_SYMBOL_BATCH"] = "0"
    repo_root = str(Path(__file__).resolve().parents[1])
    env["PYTHONPATH"] = (
        repo_root if not env.get("PYTHONPATH") else repo_root + os.pathsep + env.get("PYTHONPATH")
    )

    cp = subprocess.run(
        [
            sys.executable,
            "-u",
            "-c",
            code,
            str(l1_file),
            str(symbols_file),
            str(chunk_out),
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=repo_root,
    )

    rows_written = 0
    try:
        if cp.returncode == 0 and chunk_out.exists():
            table = pq.read_table(str(chunk_out))
            rows_written = int(table.num_rows)
            if rows_written > 0:
                if writer is None:
                    writer = pq.ParquetWriter(tmp_parquet, table.schema, compression="snappy")
                writer.write_table(table)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return writer, rows_written, cp.returncode, cp.stdout or "", cp.stderr or ""


def process_chunk(kwargs):
    l1_file = kwargs['l1_file']
    out_dir = kwargs['out_dir']
    
    file_path = Path(l1_file)
    out_path = Path(out_dir) / file_path.name.replace("Base_L1", "Feature_L2")
    done_path = Path(out_dir) / (file_path.name.replace("Base_L1", "Feature_L2") + ".done")
    
    if done_path.exists():
        return {
            "ok": True,
            "status": "skipped",
            "file": file_path.name,
            "message": f"[{file_path.name}] Skipped (Done)",
        }
        
    print(f"[{file_path.name}] Starting Stage 2 Physics Computation...", flush=True)

    try:
        t0 = time.time()
        # Single parquet pass path: avoid N-times re-scan from repeated lf.filter(...).collect().
        file_size_mb = Path(l1_file).stat().st_size / (1024 * 1024)
        parquet_meta = None
        try:
            import pyarrow.parquet as pq

            parquet_meta = pq.ParquetFile(l1_file).metadata
        except Exception:
            parquet_meta = None

        if parquet_meta is not None:
            print(
                f"[{file_path.name}] Input size={file_size_mb:.2f}MB rows={parquet_meta.num_rows} row_groups={parquet_meta.num_row_groups}",
                flush=True,
            )
        else:
            print(
                f"[{file_path.name}] Input size={file_size_mb:.2f}MB rows=<unknown> row_groups=<unknown>",
                flush=True,
            )

        # Avoid Polars schema panic on certain corrupted/mixed parquet metadata.
        # Probe columns via pyarrow first; fall back to Polars only if needed.
        schema_names = []
        try:
            import pyarrow.parquet as pq

            schema_names = list(pq.ParquetFile(l1_file).schema.names or [])
        except Exception:
            try:
                schema_names = pl.scan_parquet(l1_file).collect_schema().names()
            except Exception as schema_exc:
                return {
                    "ok": False,
                    "status": "schema_probe_failed",
                    "file": file_path.name,
                    "message": f"[{file_path.name}] CRITICAL Error: schema probe failed: {schema_exc}",
                }

        has_symbol = "symbol" in schema_names
        missing_raw = sorted(_STAGE2_REQUIRED_RAW_COLS - set(schema_names))
        if missing_raw:
            return {
                "ok": False,
                "status": "input_contract_failed",
                "file": file_path.name,
                "message": f"[{file_path.name}] Stage2 input contract failed: missing raw columns {missing_raw}",
            }
        if _first_present_name(schema_names, _STAGE2_RAW_TIME_KEYS) is None:
            return {
                "ok": False,
                "status": "input_contract_failed",
                "file": file_path.name,
                "message": f"[{file_path.name}] Stage2 input contract failed: missing raw time key {list(_STAGE2_RAW_TIME_KEYS)}",
            }

        default_batch_size = "20" if sys.platform == "win32" else "50"
        batch_size = max(1, int(os.environ.get("OMEGA_STAGE2_SYMBOL_BATCH_SIZE", default_batch_size)))
        diag_every_batches = max(0, int(os.environ.get("OMEGA_STAGE2_DIAG_EVERY_BATCHES", "0")))
        print(
            f"[{file_path.name}] Stage2 batch_size={batch_size}, polars_threads={os.environ.get('POLARS_MAX_THREADS')}",
            flush=True,
        )
        tmp_parquet = out_path.with_suffix(".parquet.tmp")
        # Ensure any leftover tmp files from previous OOMs/crashes are cleared before we start
        if tmp_parquet.exists():
            try:
                tmp_parquet.unlink()
            except OSError:
                pass
                
        writer = None
        total_rows = 0

        if has_symbol:
            force_scan_env = os.environ.get("OMEGA_STAGE2_FORCE_SCAN_FALLBACK", "").strip().lower()
            if force_scan_env in {"0", "false", "no"}:
                force_scan_fallback = False
            elif force_scan_env in {"1", "true", "yes"}:
                force_scan_fallback = True
            else:
                force_scan_fallback = sys.platform == "win32"

            if force_scan_fallback:
                print(
                    f"[{file_path.name}] Using scan/filter fallback path (platform/override).",
                    flush=True,
                )
                writer, total_rows = _process_file_via_symbol_scan_fallback(
                    l1_file=l1_file,
                    batch_size=batch_size,
                    writer=writer,
                    tmp_parquet=tmp_parquet,
                    total_rows=total_rows,
                    file_name=file_path.name,
                    diag_every_batches=diag_every_batches,
                    t0=t0,
                )
            else:
                symbol_frames = []
                symbols_seen = 0
                batch_idx = 0
                seen_symbols = set()
                try:
                    for symbol_df in _iter_complete_symbol_frames_from_parquet(l1_file):
                        try:
                            symbol_name = str(symbol_df.column("symbol")[0].as_py())
                        except Exception:
                            symbol_name = str(symbol_df.column("symbol")[0])
                        if symbol_name in seen_symbols:
                            raise RuntimeError(
                                f"duplicate_symbol_partition_detected:{symbol_name}"
                            )
                        seen_symbols.add(symbol_name)
                        symbol_frames.append(symbol_df)
                        symbols_seen += 1
                        if len(symbol_frames) >= batch_size:
                            batch_idx += 1
                            writer, rows_written = _run_feature_physics_batch(
                                symbol_frames, writer, tmp_parquet
                            )
                            total_rows += rows_written
                            if diag_every_batches > 0 and (batch_idx % diag_every_batches == 0):
                                elapsed = time.time() - t0
                                print(
                                    f"[{file_path.name}] Progress batch={batch_idx} symbols_seen={symbols_seen} rows_written={total_rows} elapsed={elapsed:.1f}s",
                                    flush=True,
                                )
                            symbol_frames = []
                            gc.collect()

                    if symbol_frames:
                        batch_idx += 1
                        writer, rows_written = _run_feature_physics_batch(
                            symbol_frames, writer, tmp_parquet
                        )
                        total_rows += rows_written
                        if diag_every_batches > 0:
                            elapsed = time.time() - t0
                            print(
                                f"[{file_path.name}] Progress batch={batch_idx} symbols_seen={symbols_seen} rows_written={total_rows} elapsed={elapsed:.1f}s",
                                flush=True,
                            )
                        symbol_frames = []
                        gc.collect()
                except BaseException as stream_exc:
                    err_txt = str(stream_exc)
                    is_polars_panic = (
                        "ParseIntError" in err_txt
                        or "PanicException" in stream_exc.__class__.__name__
                        or "pyo3_runtime" in stream_exc.__class__.__module__
                    )
                    if not is_polars_panic:
                        raise

                    print(
                        f"[{file_path.name}] [WARN] Arrow symbol path panic detected: {stream_exc}. Falling back to scan/filter path.",
                        flush=True,
                    )
                    try:
                        if writer is not None:
                            writer.close()
                    except Exception:
                        pass
                    writer = None
                    total_rows = 0
                    try:
                        tmp_parquet.unlink()
                    except FileNotFoundError:
                        pass

                    writer, total_rows = _process_file_via_symbol_scan_fallback(
                        l1_file=l1_file,
                        batch_size=batch_size,
                        writer=writer,
                        tmp_parquet=tmp_parquet,
                        total_rows=total_rows,
                        file_name=file_path.name,
                        diag_every_batches=diag_every_batches,
                        t0=t0,
                    )
        else:
            # Rare fallback: no symbol column, process file once.
            full_df = pl.read_parquet(l1_file)
            writer, rows_written = _run_feature_physics_batch([full_df], writer, tmp_parquet)
            total_rows += rows_written
            del full_df
            gc.collect()
        
        if writer is not None:
            writer.close()
            # Atomic write completion
            tmp_parquet.rename(out_path)
            done_path.touch()
            elapsed = time.time() - t0
            return_msg = f"[{file_path.name}] Completed: {total_rows} rows in {elapsed:.1f}s"
            return {
                "ok": True,
                "status": "completed",
                "file": file_path.name,
                "message": return_msg,
            }
        else:
            return_msg = f"[{file_path.name}] Error: Empty physics frames generated"
            return {
                "ok": False,
                "status": "empty_output",
                "file": file_path.name,
                "message": return_msg,
            }
            
    except Exception as e:
        # Cleanup incomplete temporary files to avoid stale caches on failure
        try:
            if 'tmp_parquet' in locals() and tmp_parquet.exists():
                tmp_parquet.unlink()
        except OSError:
            pass
            
        return {
            "ok": False,
            "status": "exception",
            "file": file_path.name,
            "message": f"[{file_path.name}] CRITICAL Error: {e}",
        }
    finally:
        # OOM Guard: Force garbage collection on both success and exception paths
        gc.collect()

def main():
    ap = argparse.ArgumentParser(description="v62 Stage 2 Physics Compute Agent")
    ap.add_argument("--input-dir", required=True, help="Directory containing Base_L1.parquet files")
    ap.add_argument("--output-dir", required=True, help="Directory to output Feature_L2.parquet files")
    ap.add_argument("--workers", type=int, default=2, help="Number of parallel workers")
    args = ap.parse_args()

    _ensure_heavy_workload_slice()
    _raise_oom_score_adj()
    _apply_worker_thread_budget(args.workers)

    runtime_notes = _windows_runtime_risk_notes()
    if runtime_notes:
        joined = "; ".join(runtime_notes)
        print(f"[WARN] Windows runtime risk detected: {joined}", flush=True)
        if _is_truthy_env("OMEGA_STAGE2_STRICT_RUNTIME"):
            print(
                "[FATAL] OMEGA_STAGE2_STRICT_RUNTIME=1 and runtime risk detected. "
                "Refusing to run Stage2 in this environment.",
                file=sys.stderr,
                flush=True,
            )
            raise SystemExit(103)

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    l1_files = list(input_path.rglob("*.parquet"))
    # Filter out tmp/done files
    l1_files = [str(p) for p in l1_files if not str(p).endswith(".tmp") and not str(p).endswith(".done")]
    l1_files, dropped_dupes = _dedupe_l1_files_by_date(l1_files)

    print(f"Found {len(l1_files)} Base_L1 chunks to process.")
    if dropped_dupes:
        print(
            f"[WARN] Dropped {len(dropped_dupes)} duplicate date chunks (mixed hash).",
            flush=True,
        )

    tasks = []
    for f in l1_files:
        tasks.append({'l1_file': f, 'out_dir': str(output_path)})

    if not tasks:
        print("Nothing to do. Exiting.")
        return

    failures = 0
    successes = 0

    if args.workers <= 1:
        # Stability path: avoid multiprocessing SemLock/spawn regressions in single-worker mode.
        print("[GUARDRAIL] workers<=1 detected, using single-process execution.", flush=True)
        for task in tasks:
            res = process_chunk(task)
            if res:
                if isinstance(res, dict):
                    print(res.get("message", str(res)), flush=True)
                    if res.get("ok"):
                        successes += 1
                    else:
                        failures += 1
                else:
                    msg = str(res)
                    print(msg, flush=True)
                    if "Completed" in msg or "Skipped (Done)" in msg:
                        successes += 1
                    else:
                        failures += 1
    else:
        # Use spawn for safety across different OS
        ctx = get_context("spawn")
        with ctx.Pool(args.workers, maxtasksperchild=10, initializer=_pool_initializer) as p:
            for res in p.imap_unordered(process_chunk, tasks):
                if res:
                    if isinstance(res, dict):
                        print(res.get("message", str(res)), flush=True)
                        if res.get("ok"):
                            successes += 1
                        else:
                            failures += 1
                    else:
                        msg = str(res)
                        print(msg, flush=True)
                        if "Completed" in msg or "Skipped (Done)" in msg:
                            successes += 1
                        else:
                            failures += 1

    print(
        f"=== STAGE 2 PHYSICS COMPUTE COMPLETE (success={successes}, failed={failures}) ===",
        flush=True,
    )
    if failures > 0:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
