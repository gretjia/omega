"""Stage1 incremental parquet writing utilities.

This module keeps Stage1 output semantics unchanged while avoiding full-day
materialization in a single DataFrame.
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Callable, Iterable, Sequence
import gc

import polars as pl
import pyarrow.parquet as pq


def group_csvs_by_symbol_parent(csv_paths: Sequence[str]) -> list[list[str]]:
    """Group CSV paths by their parent directory (symbol folder), preserving
    first-seen order for compatibility with prior output ordering."""
    grouped: "OrderedDict[str, list[str]]" = OrderedDict()
    for raw in csv_paths:
        p = str(raw)
        key = str(Path(p).parent)
        grouped.setdefault(key, []).append(p)
    return list(grouped.values())


def _iter_chunks(items: Sequence[list[str]], chunk_size: int) -> Iterable[Sequence[list[str]]]:
    step = max(1, int(chunk_size))
    for i in range(0, len(items), step):
        yield items[i : i + step]


def write_l1_incremental_parquet(
    csv_paths: Sequence[str],
    cfg,
    tmp_parquet_path: str | Path,
    symbol_batch_size: int = 64,
    build_fn: Callable[[str | list[str], object], pl.DataFrame] | None = None,
) -> int:
    """Write Stage1 Base_L1 parquet incrementally and return total written rows.

    `build_fn` defaults to `omega_core.omega_etl.build_l1_base_ticks`.
    """
    if build_fn is None:
        from omega_core.omega_etl import build_l1_base_ticks as build_fn  # local import to keep module lightweight

    symbol_groups = group_csvs_by_symbol_parent([str(p) for p in csv_paths])
    if not symbol_groups:
        return 0

    out_path = Path(tmp_parquet_path)
    writer: pq.ParquetWriter | None = None
    total_rows = 0

    try:
        for group_batch in _iter_chunks(symbol_groups, symbol_batch_size):
            batch_frames: list[pl.DataFrame] = []

            for group_files in group_batch:
                if len(group_files) == 1:
                    df = build_fn(group_files[0], cfg)
                else:
                    df = build_fn(group_files, cfg)
                if df is not None and df.height > 0:
                    batch_frames.append(df)

            if not batch_frames:
                gc.collect()
                continue

            if len(batch_frames) == 1:
                batch_df = batch_frames[0]
            else:
                batch_df = pl.concat(batch_frames, how="vertical_relaxed")

            arrow_table = batch_df.to_arrow()
            if writer is None:
                writer = pq.ParquetWriter(out_path, arrow_table.schema, compression="snappy")
            writer.write_table(arrow_table)
            total_rows += batch_df.height

            del arrow_table
            del batch_df
            del batch_frames
            gc.collect()
    finally:
        if writer is not None:
            writer.close()

    return total_rows

