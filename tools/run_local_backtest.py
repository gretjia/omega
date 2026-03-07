#!/usr/bin/env python3
"""
v64 Local Edge Backtest Engine

Engineering fast path:
1. Read each parquet file once.
2. Precompute the compact symbol/date -> T+1 close map once.
3. Reuse precomputed Stage2 physics and avoid N(symbol_batches) repeated re-scans.
4. Keep the old symbol-batch engine available behind an explicit legacy switch.
"""

from __future__ import annotations

import argparse
import gc
import json
import multiprocessing as mp
import os
import pickle
import sys
import time
from pathlib import Path
from typing import Dict, List

_CPU_COUNT = max(1, int(os.cpu_count() or 1))
os.environ.setdefault("POLARS_MAX_THREADS", str(max(1, _CPU_COUNT // 2)))
for _env_name in (
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OMP_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_env_name, "1")

import numpy as np
import polars as pl

try:
    import xgboost as xgb
except ImportError:
    xgb = None

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from config import load_l2_pipeline_config
from omega_core.trainer import OmegaTrainerV3, evaluate_frames

HEAVY_TRACE_COLS = ("ofi_list", "ofi_trace", "vol_list", "vol_trace", "time_trace", "trace")
TIME_KEY_CANDIDATES = ("time_end", "bucket_id", "time_start", "time", "__time_dt")


def _parse_years(raw: str) -> tuple[str, ...]:
    return tuple(sorted({x.strip() for x in str(raw).split(",") if x.strip()}))


def _scan_local_frames(input_pattern: str) -> List[str]:
    import glob

    files = sorted(glob.glob(input_pattern, recursive=True))
    if not files:
        raise FileNotFoundError(f"No files found matching: {input_pattern}")
    return files


def _apply_year_filter(lf: pl.LazyFrame, schema_names: List[str], years: tuple[str, ...]) -> pl.LazyFrame:
    if not years:
        return lf
    if "date" not in schema_names:
        raise RuntimeError("Backtest year isolation requires a `date` column in frame data.")
    return lf.filter(
        pl.col("date")
        .cast(pl.Utf8, strict=False)
        .str.slice(0, 4)
        .is_in(list(years))
    )


def _detect_time_key(schema_names: List[str]) -> str | None:
    for cand in TIME_KEY_CANDIDATES:
        if cand in schema_names:
            return cand
    return None


def _audit_backtest_frame_contract(file_paths: List[str], years: tuple[str, ...]) -> dict:
    lf = pl.scan_parquet(file_paths)
    schema_names = lf.collect_schema().names()
    required = {
        "symbol",
        "date",
        "epiplexity",
        "topo_energy",
        "singularity_vector",
    }
    missing = sorted(required - set(schema_names))
    if missing:
        raise RuntimeError(f"backtest_input_contract_missing_columns:{','.join(missing)}")

    lf = _apply_year_filter(lf, schema_names, years)
    diag = (
        lf.select([
            pl.len().alias("rows"),
            (pl.col("epiplexity").fill_null(0.0).fill_nan(0.0) > 0.0).sum().alias("epi_pos_rows"),
            (pl.col("topo_energy").fill_null(0.0).fill_nan(0.0) > 0.0).sum().alias("topo_energy_pos_rows"),
            (pl.col("singularity_vector").fill_null(0.0).fill_nan(0.0).abs() > 0.0).sum().alias("sv_nonzero_rows"),
        ])
        .collect()
        .row(0, named=True)
    )
    diag = {k: int(v or 0) for k, v in diag.items()}
    if diag["rows"] <= 0:
        raise RuntimeError("backtest_input_contract_empty")
    if diag["epi_pos_rows"] <= 0 or diag["topo_energy_pos_rows"] <= 0 or diag["sv_nonzero_rows"] <= 0:
        raise RuntimeError(
            "backtest_input_contract_degenerate_signal_chain:"
            + json.dumps(diag, ensure_ascii=False, sort_keys=True)
        )
    print(
        "[GATE] Backtest input contract passed "
        f"{json.dumps(diag, ensure_ascii=False, sort_keys=True)}",
        flush=True,
    )
    return diag


def _build_daily_close_map(file_paths: List[str], years: tuple[str, ...]) -> pl.DataFrame | None:
    """
    Build the compact symbol/date -> next-day close map once, then reuse it for
    every file. This preserves T+1 label semantics without requiring every
    backtest batch to rescan the full universe.
    """
    try:
        lf = pl.scan_parquet(file_paths)
        schema_names = lf.collect_schema().names()
    except Exception as exc:
        print(f"[WARN] Could not build global T+1 close map: {exc}", flush=True)
        return None

    required = {"symbol", "date", "close"}
    if not required.issubset(set(schema_names)):
        print("[WARN] Skipping global T+1 close map (missing symbol/date/close).", flush=True)
        return None

    lf = _apply_year_filter(lf, schema_names, years)
    time_key = _detect_time_key(schema_names)

    if time_key is None:
        daily = lf.group_by(["symbol", "date"]).agg(
            pl.col("close").last().alias("_day_close")
        )
    else:
        daily = lf.group_by(["symbol", "date"]).agg(
            pl.col("close").sort_by(time_key).last().alias("_day_close")
        )

    daily = (
        daily.sort(["symbol", "date"])
        .with_columns(pl.col("_day_close").shift(-1).over("symbol").alias("t1_close"))
        .select(["symbol", "date", "t1_close"])
        .collect()
    )
    print(f"[*] Built compact T+1 close map with {daily.height} symbol/day rows.", flush=True)
    return daily


def _load_backtest_file(
    file_path: str,
    years: tuple[str, ...],
    daily_close_lf: pl.LazyFrame | None,
    require_global_t1_join: bool = False,
) -> pl.DataFrame:
    lf = pl.scan_parquet(file_path)
    schema_names = lf.collect_schema().names()

    lf = _apply_year_filter(lf, schema_names, years)

    drop_cols = [c for c in HEAVY_TRACE_COLS if c in schema_names]
    if drop_cols:
        lf = lf.drop(drop_cols)

    if daily_close_lf is not None:
        if not {"symbol", "date"}.issubset(set(schema_names)):
            if require_global_t1_join:
                raise RuntimeError("missing_symbol_date_for_t1_join")
        else:
            lf = lf.join(daily_close_lf, on=["symbol", "date"], how="left")

    return lf.collect()


def _extract_all_symbols(file_paths: List[str]) -> List[str]:
    """
    Legacy symbol-batch discovery path, kept only behind an explicit opt-in.
    """
    print(f"[*] Scanning {len(file_paths)} files for symbols...", flush=True)
    all_symbols = set()

    try:
        lf = pl.scan_parquet(file_paths)
        if "symbol" not in lf.collect_schema().names():
            print("[!] Warning: 'symbol' column not found in schema. Assuming single-asset or error.")
            return []

        symbols = lf.select("symbol").unique().collect().get_column("symbol").to_list()
        all_symbols.update(s for s in symbols if s)

    except Exception as e:
        print(f"[!] Symbol scan failed: {e}. Falling back to file iteration.")
        for f in file_paths:
            try:
                df = pl.read_parquet(f, columns=["symbol"])
                all_symbols.update(df["symbol"].unique().to_list())
            except Exception:
                continue

    sorted_syms = sorted(list(all_symbols))
    print(f"[*] Found {len(sorted_syms)} unique symbols.", flush=True)
    return sorted_syms


def _process_backtest_batch(task: dict) -> dict:
    """
    Legacy worker: rescans all files for a symbol batch. Retained only for
    compatibility fallback.
    """
    batch_id = task["batch_id"]
    symbols = task["symbols"]
    input_files = task["input_files"]
    model_path = task["model_path"]
    cfg_dump = task["cfg_dump"]
    years = tuple(task.get("years", ()))

    cfg = pickle.loads(cfg_dump)
    trainer = OmegaTrainerV3(cfg)

    with open(model_path, "rb") as f:
        payload = pickle.load(f)
        model = payload.get("model")
        scaler = payload.get("scaler")
        feature_cols = payload.get("feature_cols")

    try:
        tables = []
        for f_path in input_files:
            try:
                lf_one = pl.scan_parquet(f_path).filter(pl.col("symbol").is_in(symbols))
                schema_names = lf_one.collect_schema().names()
                lf_one = _apply_year_filter(lf_one, schema_names, years)

                drop_cols = [c for c in HEAVY_TRACE_COLS if c in schema_names]
                if drop_cols:
                    lf_one = lf_one.drop(drop_cols)

                if _detect_time_key(schema_names) is None:
                    lf_one = lf_one.with_row_index(name="time_idx")

                df_one = lf_one.collect()
                if df_one.height > 0:
                    tables.append(df_one)
            except Exception:
                continue

        if not tables:
            return {"batch_id": batch_id, "rows": 0, "metrics": {}}

        df = pl.concat(tables, how="diagonal_relaxed")
        df = trainer._prepare_frames(df, cfg)

        if df.height == 0:
            return {"batch_id": batch_id, "rows": 0, "metrics": {}}

        batch_metrics = evaluate_frames(df, cfg, model=model, scaler=scaler, feature_cols=feature_cols)
        n = batch_metrics["n_frames"]
        res = {
            "batch_id": batch_id,
            "rows": n,
            "weighted_metrics": {k: v * n for k, v in batch_metrics.items() if k != "DoD_pass"},
            "raw_metrics": batch_metrics,
        }

        del df
        gc.collect()
        return res

    except Exception as e:
        print(f"[!] Batch {batch_id} failed: {e}")
        import traceback

        traceback.print_exc()
        return {"batch_id": batch_id, "rows": 0, "error": str(e)}


def _run_file_stream_backtest(
    *,
    input_files: List[str],
    model_path: str,
    cfg,
    years: tuple[str, ...],
    start_time: float,
) -> Dict[str, float]:
    """
    Canonical engineering fast path: single-pass file streaming.
    """
    with open(model_path, "rb") as f:
        payload = pickle.load(f)
    model = payload.get("model")
    scaler = payload.get("scaler")
    feature_cols = payload.get("feature_cols")

    trainer = OmegaTrainerV3(cfg)
    daily_close_map = _build_daily_close_map(input_files, years)
    need_t1 = int(max(0, getattr(cfg.micro, "t_plus_1_horizon_days", 0))) > 0
    if need_t1 and len(input_files) > 1 and (daily_close_map is None or daily_close_map.height == 0):
        raise RuntimeError("global_t1_close_map_unavailable")
    daily_close_lf = daily_close_map.lazy() if daily_close_map is not None and daily_close_map.height > 0 else None
    require_global_t1_join = need_t1 and len(input_files) > 1 and daily_close_lf is not None

    global_stats = {
        "n_frames": 0.0,
        "Topo_SNR": 0.0,
        "Orthogonality": 0.0,
        "Phys_Alignment": 0.0,
        "Model_Alignment": 0.0,
        "Vector_Alignment": 0.0,
    }

    gc_every = max(0, int(os.environ.get("OMEGA_BACKTEST_GC_EVERY_FILES", "25")))
    processed_files = 0

    print(
        "[*] Using file-stream backtest engine "
        f"(files={len(input_files)}, polars_threads={os.environ.get('POLARS_MAX_THREADS')}).",
        flush=True,
    )

    for idx, file_path in enumerate(input_files, start=1):
        try:
            df = _load_backtest_file(
                file_path,
                years,
                daily_close_lf,
                require_global_t1_join=require_global_t1_join,
            )
            if df.height > 0:
                df = trainer._prepare_frames(df, cfg)

            if df.height > 0:
                metrics = evaluate_frames(df, cfg, model=model, scaler=scaler, feature_cols=feature_cols)
                n = metrics["n_frames"]
                if n > 0:
                    global_stats["n_frames"] += n
                    for key, value in metrics.items():
                        if key in global_stats and key != "n_frames" and np.isfinite(value):
                            global_stats[key] += value * n

            processed_files += 1
            if processed_files <= 3 or processed_files == len(input_files) or processed_files % 10 == 0:
                print(
                    "    Progress: "
                    f"{processed_files}/{len(input_files)} files "
                    f"(rows={int(global_stats['n_frames'])}, "
                    f"elapsed={round(time.time() - start_time, 2)}s, "
                    f"last={Path(file_path).name})",
                    flush=True,
                )

            del df
            if gc_every > 0 and (idx % gc_every == 0):
                gc.collect()

        except Exception as exc:
            if str(exc) in {"missing_symbol_date_for_t1_join"}:
                raise
            print(f"[WARN] File-stream backtest skipped {Path(file_path).name}: {exc}", flush=True)

    total_n = global_stats["n_frames"]
    if total_n > 0:
        for key in global_stats:
            if key != "n_frames":
                global_stats[key] /= total_n

    global_stats["seconds"] = round(time.time() - start_time, 2)
    global_stats["status"] = "completed"
    global_stats["engine"] = "file_stream"
    return global_stats


def _run_legacy_symbol_batch_backtest(
    *,
    input_files: List[str],
    model_path: str,
    cfg,
    years: tuple[str, ...],
    requested_workers: int,
    symbols_per_batch: int,
    start_time: float,
) -> Dict[str, float]:
    """
    Compatibility-only legacy engine.
    """
    cfg_dump = pickle.dumps(cfg)
    all_symbols = _extract_all_symbols(input_files)

    if not all_symbols:
        return {
            "n_frames": 0.0,
            "Topo_SNR": 0.0,
            "Orthogonality": 0.0,
            "Phys_Alignment": 0.0,
            "Model_Alignment": 0.0,
            "Vector_Alignment": 0.0,
            "seconds": round(time.time() - start_time, 2),
            "status": "empty",
            "engine": "legacy_symbol_batch",
        }

    batches = [
        all_symbols[i : i + symbols_per_batch]
        for i in range(0, len(all_symbols), symbols_per_batch)
    ]
    print(f"[*] Created {len(batches)} legacy batches for {len(all_symbols)} symbols.", flush=True)

    tasks = []
    for idx, syms in enumerate(batches):
        tasks.append({
            "batch_id": idx,
            "symbols": syms,
            "input_files": input_files,
            "model_path": model_path,
            "cfg_dump": cfg_dump,
            "years": years,
        })

    mp_opt_in = os.environ.get("OMEGA_ENABLE_LOCAL_BACKTEST_MP", "").strip().lower() in {
        "1", "true", "yes", "on",
    }
    use_multiprocessing = mp_opt_in and requested_workers > 1 and len(tasks) > 1

    if use_multiprocessing:
        print(f"[*] Starting legacy backtest on {requested_workers} workers...", flush=True)
    else:
        if requested_workers > 1 and len(tasks) > 1:
            print(
                "[*] Legacy multiprocessing path disabled by default; "
                f"falling back to sequential execution (requested_workers={requested_workers}).",
                flush=True,
            )
        else:
            print("[*] Starting legacy backtest on sequential execution path...", flush=True)

    global_stats = {
        "n_frames": 0.0,
        "Topo_SNR": 0.0,
        "Orthogonality": 0.0,
        "Phys_Alignment": 0.0,
        "Model_Alignment": 0.0,
        "Vector_Alignment": 0.0,
    }

    processed_batches = 0

    def _accumulate_result(res: dict) -> None:
        nonlocal processed_batches
        if "error" in res:
            print(f"    [!] Batch {res['batch_id']} error: {res['error']}")
            return

        n = res["rows"]
        if n > 0:
            global_stats["n_frames"] += n
            for k, v in res["weighted_metrics"].items():
                if k in global_stats and k != "n_frames" and np.isfinite(v):
                    global_stats[k] += v

        processed_batches += 1
        if processed_batches <= 3 or processed_batches == len(batches) or processed_batches % 10 == 0:
            print(
                "    Progress: "
                f"{processed_batches}/{len(batches)} batches "
                f"(rows={int(global_stats['n_frames'])}, "
                f"elapsed={round(time.time() - start_time, 2)}s)",
                flush=True,
            )

    if not use_multiprocessing:
        print("[*] Using sequential legacy backtest execution path.", flush=True)
        for task in tasks:
            _accumulate_result(_process_backtest_batch(task))
    else:
        print(
            "[WARN] Legacy multiprocessing is explicitly enabled; "
            "this path remains compatibility-only.",
            flush=True,
        )
        try:
            with mp.Pool(requested_workers, maxtasksperchild=1) as pool:
                for res in pool.imap_unordered(_process_backtest_batch, tasks):
                    _accumulate_result(res)
        except Exception as exc:
            print(
                "[WARN] Legacy multiprocessing failed; "
                f"falling back to sequential execution ({type(exc).__name__}: {exc})",
                flush=True,
            )
            for task in tasks:
                _accumulate_result(_process_backtest_batch(task))

    total_n = global_stats["n_frames"]
    if total_n > 0:
        for key in global_stats:
            if key != "n_frames":
                global_stats[key] /= total_n

    global_stats["seconds"] = round(time.time() - start_time, 2)
    global_stats["status"] = "completed"
    global_stats["engine"] = "legacy_symbol_batch"
    return global_stats


def main() -> int:
    ap = argparse.ArgumentParser(description="v64 Local Edge Backtest")
    ap.add_argument("--model-path", required=True, help="Path to downloaded .pkl model")
    ap.add_argument("--frames-dir", required=True, help="Local directory containing parquet frames")
    ap.add_argument("--years", default="", help="Comma-separated holdout years for backtest isolation")
    ap.add_argument("--output", default="backtest_metrics.json", help="Path to save result")
    ap.add_argument("--workers", type=int, default=8, help="Legacy compatibility worker count")
    ap.add_argument("--symbols-per-batch", type=int, default=50, help="Legacy symbol-batch size")
    args = ap.parse_args()

    start_time = time.time()

    if not os.path.exists(args.model_path):
        raise FileNotFoundError(f"Model not found at {args.model_path}")

    os.environ["OMEGA_REUSE_PRECOMPUTED_PHYSICS"] = "1"
    cfg = load_l2_pipeline_config()
    backtest_years = _parse_years(args.years)

    input_files = _scan_local_frames(os.path.join(args.frames_dir, "**/*.parquet"))
    _audit_backtest_frame_contract(input_files, backtest_years)

    use_legacy_symbol_engine = os.environ.get("OMEGA_BACKTEST_LEGACY_SYMBOL_BATCH", "").strip().lower() in {
        "1", "true", "yes", "on",
    }

    if use_legacy_symbol_engine:
        print("[WARN] OMEGA_BACKTEST_LEGACY_SYMBOL_BATCH=1 -> using compatibility symbol-batch engine.", flush=True)
        global_stats = _run_legacy_symbol_batch_backtest(
            input_files=input_files,
            model_path=args.model_path,
            cfg=cfg,
            years=backtest_years,
            requested_workers=max(1, int(args.workers)),
            symbols_per_batch=max(1, int(args.symbols_per_batch)),
            start_time=start_time,
        )
    else:
        try:
            global_stats = _run_file_stream_backtest(
                input_files=input_files,
                model_path=args.model_path,
                cfg=cfg,
                years=backtest_years,
                start_time=start_time,
            )
        except RuntimeError as exc:
            if str(exc) not in {"global_t1_close_map_unavailable", "missing_symbol_date_for_t1_join"}:
                raise
            print(
                "[WARN] File-stream backtest cannot guarantee a single global T+1 label path; "
                "falling back to compatibility symbol-batch engine to preserve label semantics.",
                flush=True,
            )
            global_stats = _run_legacy_symbol_batch_backtest(
                input_files=input_files,
                model_path=args.model_path,
                cfg=cfg,
                years=backtest_years,
                requested_workers=max(1, int(args.workers)),
                symbols_per_batch=max(1, int(args.symbols_per_batch)),
                start_time=start_time,
            )

    print("=== V64 Edge Backtest Results ===")
    print(json.dumps(global_stats, indent=2))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(global_stats, f, indent=2)

    print(f"[*] Results saved to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
