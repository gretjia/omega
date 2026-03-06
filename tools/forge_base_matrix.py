#!/usr/bin/env python3
"""
Local-only v60 base-matrix forging via orthogonal ticker sharding.

Hard constraints enforced by design:
- ETL/base-matrix forging runs on local nodes only.
- Time-chunk slicing is forbidden (no chunk-days pipeline).
- Float64 precision is preserved end-to-end.
- Parallelism is along isolated symbols (ticker batches).
"""

from __future__ import annotations

import argparse
import gc
import glob
import hashlib
import json
import multiprocessing as mp
import re
import shutil
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import polars as pl
import os

from configs.node_paths import get_node_config

# [V64 统御指令] 强制收缴所有底层库的并发生成权，防止 128G 节点发生线程踩踏死锁
# 统一内存架构下，保持线程数等于物理核心数的一半即可喂饱总线带宽
os.environ["POLARS_MAX_THREADS"] = str(max(1, os.cpu_count() // 2))
os.environ["NUMBA_NUM_THREADS"] = str(max(1, os.cpu_count() // 2))
os.environ["OPENBLAS_NUM_THREADS"] = "1" # 禁止底层线性代数库抢占算力

try:
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
except Exception:
    pa = None
    pc = None
    pq = None

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from config import load_l2_pipeline_config
from config_v6 import FEATURE_COLS
from omega_core.trainer import OmegaTrainerV3


def _mem_available_gb() -> float | None:
    """
    Linux-only soft signal used to avoid spawning an unsafe number of workers.
    Falls back to None when not available.
    """
    meminfo = Path("/proc/meminfo")
    try:
        raw = meminfo.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    m = re.search(r"^MemAvailable:\s+(\d+)\s+kB$", raw, flags=re.MULTILINE)
    if not m:
        return None
    try:
        kb = float(m.group(1))
    except Exception:
        return None
    return kb / (1024.0 * 1024.0)


def _scan_parquet_safe(paths: list[str]) -> pl.LazyFrame:
    """
    Polars may panic on mixed parquet statistics metadata in multi-file scans.
    Disable statistics pushdown to keep scans deterministic across hosts.
    """
    uniq = [str(x) for x in dict.fromkeys(paths)]
    if not uniq:
        raise ValueError("No parquet paths provided")

    def _scan_one(path: str) -> pl.LazyFrame:
        return pl.scan_parquet(
            path,
            use_statistics=False,
            hive_partitioning=False,
            glob=False,
        )

    if len(uniq) == 1:
        return _scan_one(uniq[0])

    # Cross-file schema drift (especially on Windows) can trigger parser panics.
    # Build a relaxed concat from single-file scans to keep schema unification safe.
    return pl.concat([_scan_one(p) for p in uniq], how="diagonal_relaxed")


def _extract_symbols_one_file(path: str) -> set[str]:
    """
    Return unique symbols from one parquet file using row-group iteration when
    pyarrow is available to keep peak memory lower than full-column reads.
    """
    out: set[str] = set()
    if pq is not None:
        pf = pq.ParquetFile(str(path))
        for rg_idx in range(int(pf.metadata.num_row_groups)):
            table = pf.read_row_group(rg_idx, columns=["symbol"])
            if "symbol" not in table.column_names:
                continue
            symbol_col = table.column("symbol")
            if pc is not None and pa is not None:
                try:
                    symbol_col = pc.cast(symbol_col, pa.string(), safe=False)
                except Exception:
                    pass
                try:
                    values = pc.unique(symbol_col).to_pylist()
                except Exception:
                    values = symbol_col.to_pylist()
            else:
                values = symbol_col.to_pylist()
            for sym in values:
                if sym is not None:
                    out.add(str(sym))
        return out

    sym_df = pl.scan_parquet(str(path)).select("symbol").collect()
    if "symbol" not in sym_df.columns:
        return out
    for sym in sym_df.get_column("symbol").to_list():
        if sym is not None:
            out.add(str(sym))
    return out


def _read_lines(path: Path) -> list[str]:
    out: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            out.append(line)
    return out


def _input_files_fingerprint(files: list[str]) -> str:
    h = hashlib.sha256()
    for item in sorted(set(str(x) for x in files)):
        p = Path(item)
        try:
            st = p.stat()
            token = f"{p.resolve()}|{int(st.st_size)}|{int(st.st_mtime_ns)}"
        except Exception:
            token = f"{item}|missing"
        h.update(token.encode("utf-8", errors="replace"))
        h.update(b"\n")
    return h.hexdigest()


def _validate_local_input_files(files: list[str], source: str) -> list[str]:
    normalized: list[str] = []
    for raw in files:
        item = str(raw).strip()
        if not item:
            continue
        lower = item.lower()
        if "://" in item or lower.startswith("gs://") or lower.startswith("s3://") or lower.startswith("http://") or lower.startswith("https://"):
            raise SystemExit(
                f"Forbidden by v60 objection: {source} must contain local file paths only (got: {item})."
            )
        p = Path(item).expanduser().resolve()
        if not p.is_file():
            raise SystemExit(f"Input file does not exist or is not a file: {p}")
        normalized.append(str(p))
    return sorted(set(normalized))


def _list_files(pattern: str, years: list[str], run_hash: str) -> list[str]:
    out: list[str] = []
    if pattern.startswith("gs://"):
        raise SystemExit(
            "Forbidden by v60 objection: base_matrix ETL inputs must be local files, not gs:// URIs."
        )

    for item in glob.glob(pattern):
        uri = str(Path(item).resolve())
        name = uri.rsplit("/", 1)[-1]
        if years and not any(y in uri for y in years):
            continue
        if run_hash and (f"_{run_hash}.parquet" not in name):
            continue
        out.append(uri)
    return sorted(set(out))


def _build_relaxed_cfg(signal_epi_threshold: float, srl_mult: float, topo_energy_min: float | None):
    cfg = load_l2_pipeline_config()
    sig = cfg.signal
    trn = cfg.train
    mdl = cfg.model

    sig = replace(
        sig,
        signal_epi_threshold=float(signal_epi_threshold),
        srl_resid_sigma_mult=float(srl_mult),
        topo_energy_min=float(sig.topo_energy_min if topo_energy_min is None else topo_energy_min),
    )
    trn = replace(
        trn,
        use_structural_filter=False,
        drop_neutral_labels=False,
        winsor_features=tuple(),
    )
    mdl = replace(mdl, model_type="sgd_logistic")
    return replace(cfg, signal=sig, train=trn, model=mdl)


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = str(uri).replace("gs://", "", 1)
    if "/" not in clean:
        raise ValueError(f"Invalid GCS URI: {uri}")
    bucket, blob = clean.split("/", 1)
    if not bucket or not blob:
        raise ValueError(f"Invalid GCS URI: {uri}")
    return bucket, blob


def _upload_file(local_path: Path, uri: str) -> None:
    try:
        subprocess.check_call(["gcloud", "storage", "cp", str(local_path), uri])
        return
    except FileNotFoundError:
        pass
    except subprocess.CalledProcessError:
        pass

    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(uri)
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(local_path))


def _process_symbol_batch(task: dict) -> dict:
    batch_id = int(task["batch_id"])
    batch_symbols = [str(x) for x in task["batch_symbols"]]
    input_files = [str(x) for x in task["input_files"]]
    shard_dir = Path(task["shard_dir"])
    keep_cols = [str(x) for x in task["keep_cols"]]
    singularity_threshold = float(task["singularity_threshold"])
    batch_symbol_set = {str(x) for x in batch_symbols}
    batch_symbols_sorted = sorted(batch_symbol_set)

    cfg = _build_relaxed_cfg(
        signal_epi_threshold=float(task["signal_epi_threshold"]),
        srl_mult=float(task["srl_resid_sigma_mult"]),
        topo_energy_min=task.get("topo_energy_min"),
    )
    trainer = OmegaTrainerV3(cfg)

    tables: list[pl.DataFrame] = []
    skipped_inputs = 0
    required_input_cols = sorted(
        set(keep_cols)
        | {
            "symbol",
            "date",
            "time_end",
            "bucket_id",
            "open",
            "close",
            "sigma",
            "depth",
            "net_ofi",
            "trade_vol",
            "cancel_vol",
            "has_singularity",
            "trace",
            "ofi_list",
            "ofi_trace",
            "vol_list",
            "vol_trace",
            "time_trace",
        }
    )
    for one in input_files:
        try:
            if pq is None:
                lf = _scan_parquet_safe([str(one)])
                schema_names = set(lf.collect_schema().names())
                select_cols = [c for c in required_input_cols if c in schema_names]
                if "symbol" not in select_cols:
                    continue
                one_df = (
                    lf.select(select_cols)
                    .with_columns(pl.col("symbol").cast(pl.Utf8, strict=False))
                    .filter(pl.col("symbol").is_in(batch_symbols))
                    .collect()
                )
            else:
                try:
                    schema = pq.read_schema(str(one))
                    schema_names = set(schema.names)
                except Exception:
                    skipped_inputs += 1
                    continue

                select_cols = [c for c in required_input_cols if c in schema_names]
                if "symbol" not in select_cols:
                    continue

                filter_expr = [("symbol", "in", batch_symbols_sorted)]
                try:
                    table = pq.read_table(
                        str(one),
                        columns=select_cols,
                        filters=filter_expr,
                    )
                except Exception:
                    # Fallback path for files with incompatible statistics/filter metadata.
                    table = pq.read_table(str(one), columns=select_cols)

                if table.num_rows <= 0:
                    continue

                one_df = pl.from_arrow(table, rechunk=False)
                one_df = one_df.with_columns(pl.col("symbol").cast(pl.Utf8, strict=False)).filter(
                    pl.col("symbol").is_in(batch_symbols)
                )

            if one_df.height <= 0:
                continue

            cast_exprs: list[pl.Expr] = []
            schema_map = one_df.schema
            for col in ("open", "close", "sigma", "depth", "net_ofi", "trade_vol", "cancel_vol"):
                if col in one_df.columns:
                    if schema_map.get(col) == pl.Utf8:
                        cast_exprs.append(
                            pl.col(col)
                            .str.replace_all(",", "")
                            .cast(pl.Float64, strict=False)
                            .alias(col)
                        )
                    else:
                        cast_exprs.append(pl.col(col).cast(pl.Float64, strict=False))
            if "has_singularity" in one_df.columns:
                cast_exprs.append(pl.col("has_singularity").cast(pl.Boolean, strict=False))
            if cast_exprs:
                one_df = one_df.with_columns(cast_exprs)

            sort_cols = [c for c in ("symbol", "date", "time_end", "bucket_id") if c in one_df.columns]
            if sort_cols and one_df.height > 1:
                sort_exprs: list[pl.Expr] = []
                sort_keys: list[str] = []
                drop_cols: list[str] = []
                if "symbol" in one_df.columns:
                    sort_exprs.append(pl.col("symbol").cast(pl.Utf8, strict=False).alias("__sort_symbol"))
                    sort_keys.append("__sort_symbol")
                    drop_cols.append("__sort_symbol")
                if "date" in one_df.columns:
                    sort_exprs.append(pl.col("date").cast(pl.Utf8, strict=False).alias("__sort_date"))
                    sort_keys.append("__sort_date")
                    drop_cols.append("__sort_date")
                if "time_end" in one_df.columns:
                    sort_exprs.append(pl.col("time_end").cast(pl.Utf8, strict=False).alias("__sort_time_end"))
                    sort_keys.append("__sort_time_end")
                    drop_cols.append("__sort_time_end")
                if "bucket_id" in one_df.columns:
                    sort_exprs.append(pl.col("bucket_id").cast(pl.Int64, strict=False).alias("__sort_bucket_num"))
                    sort_exprs.append(pl.col("bucket_id").cast(pl.Utf8, strict=False).alias("__sort_bucket_txt"))
                    sort_keys.extend(["__sort_bucket_num", "__sort_bucket_txt"])
                    drop_cols.extend(["__sort_bucket_num", "__sort_bucket_txt"])
                if sort_exprs and sort_keys:
                    one_df = one_df.with_columns(sort_exprs).sort(sort_keys, nulls_last=True).drop(drop_cols)

            tables.append(one_df)
            if len(tables) % 8 == 0:
                gc.collect()
        except Exception:
            skipped_inputs += 1
            continue

    if skipped_inputs > 0 and not tables:
        tables.clear()
        gc.collect()
        return {
            "batch_id": batch_id,
            "symbols": len(batch_symbols),
            "raw_rows": 0,
            "base_rows": 0,
            "output_path": "",
            "skipped_inputs": int(skipped_inputs),
            "error": "all_input_read_failed",
        }

    if tables:
        raw_df = pl.concat(tables, how="diagonal_relaxed")
    else:
        raw_df = pl.DataFrame()
    tables.clear()
    gc.collect()

    global_sort_cols = [c for c in ("symbol", "date", "time_end", "bucket_id") if c in raw_df.columns]
    if raw_df.height > 1 and global_sort_cols:
        raw_df = raw_df.sort(global_sort_cols, nulls_last=True)

    raw_rows = int(raw_df.height)
    if raw_rows <= 0:
        del raw_df
        gc.collect()
        return {
            "batch_id": batch_id,
            "symbols": len(batch_symbols),
            "raw_rows": 0,
            "base_rows": 0,
            "output_path": "",
            "skipped_inputs": int(skipped_inputs),
        }

    base_df = trainer._prepare_frames(raw_df, cfg)
    if base_df.height <= 0:
        del base_df
        del raw_df
        gc.collect()
        return {
            "batch_id": batch_id,
            "symbols": len(batch_symbols),
            "raw_rows": raw_rows,
            "base_rows": 0,
            "output_path": "",
            "skipped_inputs": int(skipped_inputs),
        }

    # Strict v60 objection enforcement: physics gates must exist.
    missing_critical = [c for c in ["is_physics_valid", "epiplexity"] if c not in base_df.columns]
    if missing_critical:
        raise RuntimeError(f"Batch {batch_id}: Physics engine failed to produce critical columns: {missing_critical}")

    # Enforce Axiom 2 strictly: Float64-only policy for all float columns.
    forbidden_float_cols = [
        col
        for col, dtype in base_df.schema.items()
        if str(dtype).startswith("Float") and dtype != pl.Float64
    ]
    if forbidden_float_cols:
        raise RuntimeError(
            f"Batch {batch_id}: forbidden non-Float64 columns detected: {sorted(forbidden_float_cols)}"
        )

    # [V64.1 极端斯坦绝对闭合守则] 捍卫物理奇点，切除缝合怪！
    # 1. 结构性空值吸敛为0，防止暴力 dropna 造成的级联误杀
    base_df = base_df.with_columns(pl.col("singularity_vector").fill_nan(0.0).fill_null(0.0))

    # [HOTFIX V64.1] Dynamically reconstruct the true `is_signal` based on V64.1 math closure.
    # The L2 parquets on disk have the old V64.0 `is_signal` which compared topo_energy with sigma_eff.
    # We fix it here in-memory before forging the matrix to avoid rerunning Stage 2.
    sig_cfg = cfg.signal
    signal_epi_threshold = float(getattr(sig_cfg, "signal_epi_threshold", 0.5))
    topo_energy_min = float(getattr(sig_cfg, "topo_energy_min", 2.0))
    spoofing_ratio_max = float(getattr(sig_cfg, "spoofing_ratio_max", 2.5))
    srl_resid_sigma_mult = float(getattr(sig_cfg, "srl_resid_sigma_mult", 2.0))
    topo_area_min_abs = float(getattr(sig_cfg, "topo_area_min_abs", 1e-9))
    
    base_df = base_df.with_columns([
        (
            (pl.col("is_energy_active") == True)
            & (pl.col("epiplexity") > signal_epi_threshold) 
            & (pl.col("srl_resid").abs() > srl_resid_sigma_mult * pl.col("sigma_eff"))
            & (pl.col("topo_area").abs() > topo_area_min_abs)
            & (pl.col("topo_energy") > topo_energy_min) # 纯几何无量纲门控比较 (HOTFIX)
            & (pl.col("spoof_ratio") < spoofing_ratio_max)
        ).alias("is_signal")
    ])

    # 2. 自适应底噪阈值：只过滤毫无波动的“绝对死水期”，对顶部的巨大极值绝对放行
    filters: list[pl.Expr] = [
        (pl.col("is_physics_valid") == True),
        (pl.col("singularity_vector").abs() > singularity_threshold),
    ]
    
    # 3. 靶向切除：我们只丢弃没有“未来收益率 (target)”对齐的尾盘数据
    # 严禁使用 Z-Score 截断 singularity_vector！999.0 的极值必须原封不动送入云端！
    if "t1_fwd_return" in base_df.columns:
        base_df = base_df.filter(pl.all_horizontal(filters)).drop_nulls(subset=["t1_fwd_return"])
    else:
        base_df = base_df.filter(pl.all_horizontal(filters))

    if base_df.height <= 0:
        del base_df
        del raw_df
        gc.collect()
        return {
            "batch_id": batch_id,
            "symbols": len(batch_symbols),
            "raw_rows": raw_rows,
            "base_rows": 0,
            "output_path": "",
            "skipped_inputs": int(skipped_inputs),
        }

    selected = [c for c in keep_cols if c in base_df.columns]
    if selected:
        base_df = base_df.select(selected)

    out_path = shard_dir / f"base_matrix_batch_{batch_id:05d}.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    base_df.write_parquet(tmp_path, compression="snappy")
    tmp_path.replace(out_path)
    result = {
        "batch_id": batch_id,
        "symbols": len(batch_symbols),
        "raw_rows": raw_rows,
        "base_rows": int(base_df.height),
        "output_path": str(out_path),
        "skipped_inputs": int(skipped_inputs),
    }
    meta_path = out_path.with_suffix(out_path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    del base_df
    del raw_df
    gc.collect()
    return result


def _merge_batch_parquets(batch_files: list[Path], out_parquet: Path) -> tuple[int, int]:
    if not batch_files:
        return 0, 0
    
    print(f"[SYSTEM ARCHITECT] 开启物理张量流式熔铸 (Zero-Copy Streaming)...", flush=True)
    
    # [V64 纯流式零拷贝纪元] 废弃 pyarrow/multiprocessing，构建延迟计算的 DAG
    lazy_df = pl.scan_parquet([str(x) for x in sorted(batch_files)])
    
    lazy_df.sink_parquet(
        str(out_parquet),
        compression="zstd",
        row_group_size=1048576,
        maintain_order=False
    )
    
    merged_rows = _count_parquet_rows(out_parquet)
    return int(merged_rows), int(len(batch_files))


def _count_parquet_rows(path: Path) -> int:
    if not path.exists() or path.stat().st_size <= 0:
        return 0
    if pq is not None:
        try:
            return int(pq.ParquetFile(str(path)).metadata.num_rows)
        except Exception:
            return 0
    try:
        return int(pl.scan_parquet(str(path)).select(pl.len()).collect().item())
    except Exception:
        return 0


def _is_compatible_reused_shard(path: Path) -> bool:
    required = {"is_physics_valid", "epiplexity"}
    if not path.exists() or path.stat().st_size <= 0:
        return False

    if pq is not None and pa is not None:
        try:
            schema = pq.read_schema(str(path))
            names = list(schema.names)
            if not required.issubset(set(names)):
                return False
            for field in schema:
                t = field.type
                if pa.types.is_floating(t) and not pa.types.is_float64(t):
                    return False
            return True
        except Exception:
            return False

    try:
        schema = pl.scan_parquet(str(path)).collect_schema()
        if not required.issubset(set(schema.names())):
            return False
        for _, dtype in schema.items():
            if str(dtype).startswith("Float") and dtype != pl.Float64:
                return False
        return True
    except Exception:
        return False


class LocalManifoldForger:
    def __init__(
        self,
        *,
        input_files: list[str],
        shard_dir: Path,
        signal_epi_threshold: float,
        srl_resid_sigma_mult: float,
        topo_energy_min: float | None,
        singularity_threshold: float,
        keep_cols: list[str],
    ):
        self.input_files = sorted(set(str(x) for x in input_files))
        self.shard_dir = shard_dir
        self.signal_epi_threshold = float(signal_epi_threshold)
        self.srl_resid_sigma_mult = float(srl_resid_sigma_mult)
        self.topo_energy_min = topo_energy_min
        self.singularity_threshold = float(singularity_threshold)
        self.keep_cols = list(dict.fromkeys(keep_cols))

    def _all_symbols(self, sample_symbols: int, seed: int) -> list[str]:
        symbol_set: set[str] = set()
        skipped_inputs = 0
        for one in self.input_files:
            try:
                symbols = _extract_symbols_one_file(str(one))
            except Exception:
                skipped_inputs += 1
                continue
            for sym in symbols:
                if sym is None:
                    continue
                symbol_set.add(str(sym))

        if not symbol_set:
            return []
        if skipped_inputs > 0:
            print(f"[WARN] _all_symbols skipped unreadable inputs: {skipped_inputs}", flush=True)

        all_symbols = sorted(symbol_set)
        if sample_symbols > 0:
            rng = np.random.default_rng(int(seed))
            if len(all_symbols) <= int(sample_symbols):
                return all_symbols
            chosen = rng.choice(np.array(all_symbols, dtype=object), size=int(sample_symbols), replace=False).tolist()
            return sorted(str(x) for x in chosen)

        return all_symbols

    def run_multicore_forge(
        self,
        *,
        symbols_per_batch: int = 50,
        max_workers: int = 2,
        reserve_mem_gb: float = 40.0,
        worker_mem_gb: float = 10.0,
        dynamic_worker_cap: bool = True,
        sample_symbols: int = 0,
        seed: int = 42,
        resume: bool = True,
    ) -> dict:
        symbols = self._all_symbols(sample_symbols=int(sample_symbols), seed=int(seed))
        if not symbols:
            raise SystemExit("No symbols discovered from input files.")

        batch_size = max(1, int(symbols_per_batch))
        batches = [symbols[i : i + batch_size] for i in range(0, len(symbols), batch_size)]

        self.shard_dir.mkdir(parents=True, exist_ok=True)

        tasks: list[dict] = []
        reused_results: list[dict] = []
        for idx, batch_symbols in enumerate(batches):
            shard_path = self.shard_dir / f"base_matrix_batch_{idx:05d}.parquet"
            if bool(resume) and shard_path.is_file() and shard_path.stat().st_size > 0:
                meta_path = shard_path.with_suffix(shard_path.suffix + ".meta.json")
                meta = None
                try:
                    if meta_path.exists():
                        meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except Exception:
                    meta = None

                meta_ok = False
                if isinstance(meta, dict):
                    meta_skipped = int(meta.get("skipped_inputs", 1))
                    meta_symbols = int(meta.get("symbols", -1))
                    meta_ok = (meta_skipped == 0) and (meta_symbols == len(batch_symbols))

                shard_compatible = _is_compatible_reused_shard(shard_path)
                # Backward compatible resume: older shard dirs may lack per-batch meta.
                if shard_compatible and (meta_ok or meta is None):
                    reused_rows = _count_parquet_rows(shard_path)
                else:
                    reused_rows = 0
                if reused_rows > 0:
                    reused_results.append(
                        {
                            "batch_id": idx,
                            "symbols": len(batch_symbols),
                            "raw_rows": 0,
                            "base_rows": int(reused_rows),
                            "output_path": str(shard_path),
                            "skipped_inputs": 0,
                            "resumed": True,
                        }
                    )
                    continue
            tasks.append(
                {
                    "batch_id": idx,
                    "batch_symbols": batch_symbols,
                    "input_files": self.input_files,
                    "shard_dir": str(self.shard_dir),
                    "keep_cols": self.keep_cols,
                    "signal_epi_threshold": self.signal_epi_threshold,
                    "srl_resid_sigma_mult": self.srl_resid_sigma_mult,
                    "topo_energy_min": self.topo_energy_min,
                    "singularity_threshold": self.singularity_threshold,
                }
            )

        t0 = time.time()
        worker_count = 0
        requested_worker_count = 0
        worker_budget = 0
        parallel_fallback_used = False
        pool_error = ""
        mem_available_gb = _mem_available_gb() if bool(dynamic_worker_cap) else None
        print(
            "[INFO] forge scheduling: "
            f"total_batches={len(batches)}, "
            f"pre_resumed={len(reused_results)}, "
            f"pending={len(tasks)}, "
            f"max_workers={int(max_workers)}",
            flush=True,
        )
        if not tasks:
            results: list[dict] = []
        else:
            requested_worker_count = max(1, min(int(max_workers), len(tasks)))
            worker_count = requested_worker_count
            if bool(dynamic_worker_cap) and float(worker_mem_gb) > 0:
                if mem_available_gb is not None:
                    budget = int((float(mem_available_gb) - float(reserve_mem_gb)) // float(worker_mem_gb))
                    worker_budget = max(1, budget)
                    worker_count = max(1, min(worker_count, worker_budget))
                    if worker_count < requested_worker_count:
                        print(
                            "[WARN] dynamic worker cap applied: "
                            f"requested={requested_worker_count}, "
                            f"effective={worker_count}, "
                            f"mem_available_gb={mem_available_gb:.2f}, "
                            f"reserve_mem_gb={float(reserve_mem_gb):.2f}, "
                            f"worker_mem_gb={float(worker_mem_gb):.2f}",
                            flush=True,
                        )
            print(
                "[INFO] worker plan: "
                f"requested={requested_worker_count}, "
                f"effective={worker_count}, "
                f"worker_budget={worker_budget}, "
                f"mem_available_gb={mem_available_gb}",
                flush=True,
            )
            if worker_count == 1:
                results = [_process_symbol_batch(t) for t in tasks]
            else:
                ctx = mp.get_context("spawn")
                results = []
                try:
                    with ctx.Pool(processes=worker_count) as pool:
                        for item in pool.imap_unordered(_process_symbol_batch, tasks):
                            results.append(item)
                except Exception as exc:
                    parallel_fallback_used = True
                    pool_error = f"{type(exc).__name__}: {exc}"
                    print(
                        "[WARN] multiprocessing pool failed; "
                        f"falling back to serial for remaining tasks ({pool_error})",
                        flush=True,
                    )
                    finished = {int(x.get("batch_id", -1)) for x in results}
                    for t in tasks:
                        bid = int(t.get("batch_id", -1))
                        if bid in finished:
                            continue
                        results.append(_process_symbol_batch(t))
                    worker_count = 1

        ordered = sorted(reused_results + results, key=lambda x: int(x.get("batch_id", -1)))
        elapsed = round(time.time() - t0, 2)
        return {
            "symbols": symbols,
            "batches": ordered,
            "worker_count": worker_count,
            "requested_worker_count": int(requested_worker_count),
            "worker_budget": int(worker_budget),
            "mem_available_gb": None if mem_available_gb is None else round(float(mem_available_gb), 2),
            "parallel_fallback_used": bool(parallel_fallback_used),
            "pool_error": str(pool_error),
            "resumed_batches": int(len(reused_results)),
            "processed_batches": int(len(results)),
            "total_batches": int(len(batches)),
            "seconds": elapsed,
        }


def main() -> int:
    node_cfg = get_node_config()
    default_stage2_output = str(getattr(node_cfg, "stage2_output", "") or "").rstrip("/\\")
    default_input_pattern = (
        f"{default_stage2_output}/*.parquet"
        if default_stage2_output
        else "artifacts/runtime/latest/frames/host=*/*.parquet"
    )

    ap = argparse.ArgumentParser(description="v60 local base-matrix forger (ticker sharding)")
    ap.add_argument("--input-pattern", default=default_input_pattern)
    ap.add_argument("--input-file-list", default="")
    ap.add_argument("--years", default="2023,2024")
    ap.add_argument("--hash", default="")
    ap.add_argument("--max-files", type=int, default=0)
    ap.add_argument("--sample-symbols", type=int, default=0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--symbols-per-batch", type=int, default=50)
    ap.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Dynamic caps remain active. Use values above 2 only after confirming RAM budget on the local node.",
    )
    ap.add_argument("--reserve-mem-gb", type=float, default=40.0)
    ap.add_argument("--worker-mem-gb", type=float, default=10.0)
    ap.add_argument("--no-dynamic-worker-cap", action="store_true")
    ap.add_argument("--max-rows-per-file", type=int, default=0)
    ap.add_argument(
        "--signal-epi-threshold",
        "--peace-threshold",
        dest="signal_epi_threshold",
        type=float,
        default=0.5,
        help="Canonical V64.1 MDL signal gate. Legacy alias: --peace-threshold",
    )
    ap.add_argument(
        "--singularity-threshold",
        "--peace-threshold-baseline",
        dest="singularity_threshold",
        type=float,
        default=0.10,
        help="Canonical singularity_vector amplitude gate. Legacy alias: --peace-threshold-baseline",
    )
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=2.0)
    ap.add_argument(
        "--topo-energy-min",
        "--topo-energy-sigma-mult",
        dest="topo_energy_min",
        type=float,
        default=None,
        help="Canonical dimensionless topology gate. Legacy alias: --topo-energy-sigma-mult",
    )
    ap.add_argument("--output-parquet", required=True)
    ap.add_argument("--output-meta", default="")
    ap.add_argument("--output-uri", default="")
    ap.add_argument("--output-meta-uri", default="")
    ap.add_argument("--shard-dir", default="")
    ap.add_argument("--merge-existing-shards-only", action="store_true")
    ap.add_argument("--expected-shard-count", type=int, default=0)
    ap.add_argument("--no-resume", action="store_true")
    # Backward-compatibility flags kept only to block forbidden paths explicitly.
    ap.add_argument("--chunk-days", type=int, default=0)
    ap.add_argument("--float32-output", action="store_true")
    args = ap.parse_args()

    if int(args.chunk_days) > 0:
        raise SystemExit("Forbidden by v60 objection: --chunk-days is removed. Use ticker sharding only.")
    if bool(args.float32_output):
        raise SystemExit("Forbidden by v60 objection: --float32-output is removed. Float64 is mandatory.")
    if int(args.max_rows_per_file) > 0:
        raise SystemExit("Ticker-sharding mode does not support --max-rows-per-file. Use --sample-symbols/--max-files.")

    out_parquet = Path(args.output_parquet).resolve()
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    resume_enabled = not bool(args.no_resume)

    shard_dir = (
        Path(args.shard_dir).resolve()
        if str(args.shard_dir).strip()
        else (out_parquet.parent / f"{out_parquet.stem}_shards")
    )
    if shard_dir.exists() and not resume_enabled:
        shutil.rmtree(shard_dir)
    shard_dir.mkdir(parents=True, exist_ok=True)

    if bool(args.merge_existing_shards_only):
        shard_files = sorted(shard_dir.glob("base_matrix_batch_*.parquet"))
        if not shard_files:
            raise SystemExit("No shard parquet files found for --merge-existing-shards-only.")
        if int(args.expected_shard_count) > 0 and len(shard_files) != int(args.expected_shard_count):
            raise SystemExit(
                f"Expected {int(args.expected_shard_count)} shard files, got {len(shard_files)}."
            )
        bad = [x for x in shard_files if not _is_compatible_reused_shard(x)]
        if bad:
            raise SystemExit(
                f"Incompatible shard files detected (sample: {bad[0].name}). Refuse merge-only mode."
            )
        if out_parquet.exists():
            out_parquet.unlink()
        merged_rows, merged_files = _merge_batch_parquets(shard_files, out_parquet)
        if merged_rows <= 0:
            raise SystemExit("Merged output is empty in --merge-existing-shards-only mode.")

        out_meta = Path(args.output_meta).resolve() if args.output_meta else out_parquet.with_suffix(
            out_parquet.suffix + ".meta.json"
        )
        meta = {
            "mode": "merge_existing_shards_only",
            "output_parquet": str(out_parquet),
            "output_meta": str(out_meta),
            "shard_dir": str(shard_dir),
            "merged_rows": int(merged_rows),
            "merged_files": int(merged_files),
            "hash": str(args.hash),
        }
        out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.output_uri:
            _upload_file(out_parquet, args.output_uri)
        if args.output_meta_uri:
            _upload_file(out_meta, args.output_meta_uri)
        print(
            json.dumps(
                {
                    "status": "ok",
                    "mode": "merge_existing_shards_only",
                    "output_parquet": str(out_parquet),
                    "output_meta": str(out_meta),
                    "merged_rows": int(merged_rows),
                    "merged_files": int(merged_files),
                },
                ensure_ascii=False,
            )
        )
        return 0

    years = [x.strip() for x in str(args.years).split(",") if x.strip()]
    if args.input_file_list:
        listed = _read_lines(Path(args.input_file_list))
        listed = _validate_local_input_files(listed, source="--input-file-list")
        files = [x for x in listed if (not years or any(y in x for y in years))]
        if args.hash:
            files = [x for x in files if f"_{args.hash}.parquet" in x.rsplit("/", 1)[-1]]
        files = sorted(set(files))
    else:
        files = _list_files(str(args.input_pattern), years=years, run_hash=str(args.hash).strip())

    if int(args.max_files) > 0:
        files = files[: int(args.max_files)]
    if not files:
        raise SystemExit("No input frame files matched.")

    keep_cols = list(
        dict.fromkeys(
            list(FEATURE_COLS)
            + [
                "symbol",
                "date",
                "bucket_id",
                "time_end",
                "epiplexity",
                "singularity_vector",
                "srl_resid",
                "srl_resid_050",
                "sigma_eff",
                "is_energy_active",
                "spoof_ratio",
                "topo_area",
                "topo_energy",
                "is_signal",
                "is_physics_valid",
                "t1_fwd_return",
                "direction_label",
                "adaptive_y",
            ]
        )
    )

    resume_context = {
        "schema_version": 1,
        "hash": str(args.hash),
        "years": years,
        "input_files": files,
        "input_files_fingerprint": _input_files_fingerprint(files),
        "symbols_per_batch": int(args.symbols_per_batch),
        "sample_symbols": int(args.sample_symbols),
        "seed": int(args.seed),
        "signal_epi_threshold": float(args.signal_epi_threshold),
        "singularity_threshold": float(args.singularity_threshold),
        "srl_resid_sigma_mult": float(args.srl_resid_sigma_mult),
        "topo_energy_min": None
        if args.topo_energy_min is None
        else float(args.topo_energy_min),
        "keep_cols": keep_cols,
    }
    def _normalize_resume_context(ctx: dict | None) -> dict | None:
        if not isinstance(ctx, dict):
            return ctx
        normalized = dict(ctx)
        if "signal_epi_threshold" not in normalized and "peace_threshold" in normalized:
            normalized["signal_epi_threshold"] = float(normalized["peace_threshold"])
        if "singularity_threshold" not in normalized and "peace_threshold_baseline" in normalized:
            normalized["singularity_threshold"] = float(normalized["peace_threshold_baseline"])
        if "topo_energy_min" not in normalized and "topo_energy_sigma_mult" in normalized:
            topo_energy_min = normalized["topo_energy_sigma_mult"]
            normalized["topo_energy_min"] = None if topo_energy_min is None else float(topo_energy_min)
        normalized.pop("peace_threshold", None)
        normalized.pop("peace_threshold_baseline", None)
        normalized.pop("topo_energy_sigma_mult", None)
        return normalized
    resume_context_path = shard_dir / "_resume_context.json"
    if resume_enabled and resume_context_path.exists():
        try:
            prev = json.loads(resume_context_path.read_text(encoding="utf-8"))
        except Exception:
            prev = None
        if _normalize_resume_context(prev) != _normalize_resume_context(resume_context):
            raise SystemExit(
                "Resume context mismatch in shard dir. Re-run with --no-resume to rebuild from scratch."
            )
    resume_context_path.write_text(
        json.dumps(resume_context, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    forger = LocalManifoldForger(
        input_files=files,
        shard_dir=shard_dir,
        signal_epi_threshold=float(args.signal_epi_threshold),
        srl_resid_sigma_mult=float(args.srl_resid_sigma_mult),
        topo_energy_min=args.topo_energy_min,
        singularity_threshold=float(args.singularity_threshold),
        keep_cols=keep_cols,
    )

    t0 = time.time()
    forge_result = forger.run_multicore_forge(
        symbols_per_batch=int(args.symbols_per_batch),
        max_workers=int(args.max_workers),
        reserve_mem_gb=float(args.reserve_mem_gb),
        worker_mem_gb=float(args.worker_mem_gb),
        dynamic_worker_cap=not bool(args.no_dynamic_worker_cap),
        sample_symbols=int(args.sample_symbols),
        seed=int(args.seed),
        resume=resume_enabled,
    )
    batch_results = forge_result["batches"]
    failed_batches = [x for x in batch_results if str(x.get("error", "")).strip()]
    if failed_batches:
        bad_ids = ",".join(str(int(x.get("batch_id", -1))) for x in failed_batches[:20])
        raise SystemExit(
            f"One or more batches had unreadable inputs (ids={bad_ids}). "
            "Refusing to merge partial shards."
        )
    skipped_inputs_total = int(sum(int(x.get("skipped_inputs", 0)) for x in batch_results))
    if skipped_inputs_total > 0:
        print(
            f"[WARN] skipped unreadable inputs during forge: {skipped_inputs_total}",
            flush=True,
        )
    shard_files = [Path(x["output_path"]) for x in batch_results if str(x.get("output_path", ""))]
    if not shard_files:
        raise SystemExit("No shard parquet files were produced.")

    if out_parquet.exists():
        out_parquet.unlink()
    merged_rows, merged_files = _merge_batch_parquets(shard_files, out_parquet)
    if merged_rows <= 0:
        raise SystemExit("Base matrix is empty after ticker sharding forge.")

    out_meta = Path(args.output_meta).resolve() if args.output_meta else out_parquet.with_suffix(
        out_parquet.suffix + ".meta.json"
    )
    total_raw_rows = int(sum(int(x.get("raw_rows", 0)) for x in batch_results))
    total_base_rows = int(sum(int(x.get("base_rows", 0)) for x in batch_results))
    meta = {
        "mode": "local_ticker_sharding",
        "input_file_count": len(files),
        "input_files": files,
        "raw_rows": total_raw_rows,
        "base_rows": total_base_rows,
        "merged_rows": int(merged_rows),
        "merged_files": int(merged_files),
        "skipped_inputs_total": int(skipped_inputs_total),
        "output_parquet": str(out_parquet),
        "shard_dir": str(shard_dir),
        "symbols_total": len(forge_result["symbols"]),
        "symbols_per_batch": int(args.symbols_per_batch),
        "batch_count": len(batch_results),
        "worker_count": int(forge_result["worker_count"]),
        "requested_worker_count": int(forge_result.get("requested_worker_count", forge_result["worker_count"])),
        "worker_budget": int(forge_result.get("worker_budget", 0)),
        "mem_available_gb": forge_result.get("mem_available_gb"),
        "reserve_mem_gb": float(args.reserve_mem_gb),
        "worker_mem_gb": float(args.worker_mem_gb),
        "dynamic_worker_cap": bool(not args.no_dynamic_worker_cap),
        "parallel_fallback_used": bool(forge_result.get("parallel_fallback_used", False)),
        "pool_error": str(forge_result.get("pool_error", "")),
        "resume_enabled": bool(resume_enabled),
        "resumed_batches": int(forge_result.get("resumed_batches", 0)),
        "processed_batches": int(forge_result.get("processed_batches", 0)),
        "total_batches": int(forge_result.get("total_batches", len(batch_results))),
        "years": years,
        "hash": str(args.hash),
        "sample_symbols": int(args.sample_symbols),
        "physics_gates": {
            "signal_epi_threshold": float(args.signal_epi_threshold),
            "singularity_threshold": float(args.singularity_threshold),
            "srl_resid_sigma_mult": float(args.srl_resid_sigma_mult),
            "topo_energy_min": float(
                load_l2_pipeline_config().signal.topo_energy_min
                if args.topo_energy_min is None
                else args.topo_energy_min
            ),
            "stage3_param_contract": "canonical_v64_1",
        },
        "dtype_invariants": {
            "strict_float64_required": True,
            "required_float_dtype": "Float64",
            "forbidden_float_dtypes": ["Float16", "Float32"],
            "forbidden_float_dtypes_detected": False,
            "checked_column_count": int(len(keep_cols)),
        },
        "seconds": round(time.time() - t0, 2),
        "batch_stats": batch_results,
    }
    out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.output_uri:
        _upload_file(out_parquet, args.output_uri)
    if args.output_meta_uri:
        _upload_file(out_meta, args.output_meta_uri)

    print(
        json.dumps(
            {
                "status": "ok",
                "mode": "local_ticker_sharding",
                "output_parquet": str(out_parquet),
                "output_meta": str(out_meta),
                "output_uri": str(args.output_uri),
                "output_meta_uri": str(args.output_meta_uri),
                "base_rows": int(merged_rows),
                "input_file_count": len(files),
                "symbols_total": len(forge_result["symbols"]),
                "batch_count": len(batch_results),
                "worker_count": int(forge_result["worker_count"]),
                "seconds": round(time.time() - t0, 2),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
