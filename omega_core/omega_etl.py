"""
omega_etl.py

Level-2 (v5) vectorized ETL pipeline using Polars.
Fixes Paradox 3: Causal Volume Projection.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import polars as pl

from config import L2PipelineConfig


def _rename_map(cfg: L2PipelineConfig) -> Dict[str, str]:
    m = cfg.mapping
    rename: Dict[str, str] = {
        m.col_symbol: "symbol",
        m.col_exchange: "exchange",
        m.col_date: "date",
        m.col_time: "time",
        m.col_price: "price",
        m.col_volume: "vol",
        m.col_turnover: "turnover",
        m.col_bs_flag: "bs_flag",
    }
    for i in range(1, int(m.book_levels) + 1):
        rename[f"{m.bid_price_prefix}{i}"] = f"bid_p{i}"
        rename[f"{m.bid_volume_prefix}{i}"] = f"bid_v{i}"
        rename[f"{m.ask_price_prefix}{i}"] = f"ask_p{i}"
        rename[f"{m.ask_volume_prefix}{i}"] = f"ask_v{i}"
    return rename


def _sum_expr(exprs: List[pl.Expr]) -> pl.Expr:
    return pl.fold(pl.lit(0.0), lambda acc, x: acc + x, exprs)


def _numeric_cols(cfg: L2PipelineConfig) -> List[str]:
    m = cfg.mapping
    cols = ["price", "vol", "turnover"]
    for i in range(1, int(m.book_levels) + 1):
        cols.extend([f"bid_p{i}", f"bid_v{i}", f"ask_p{i}", f"ask_v{i}"])
    return cols


def scan_l2_quotes(path: str | List[str], cfg: L2PipelineConfig) -> pl.LazyFrame | None:
    if isinstance(path, list):
        if not path:
            return None
        # Check if it's the split CSVs format (has 行情.csv and 逐笔成交.csv)
        path_strs = [str(p) for p in path]
        quote_file = next((p for p in path_strs if "行情.csv" in p), None)
        trade_file = next((p for p in path_strs if "逐笔成交.csv" in p), None)
        
        if quote_file and trade_file:
            print(f"[DEBUG] Processing split files: {quote_file} & {trade_file}")
            return _scan_split_l2_quotes(quote_file, trade_file, cfg)
        else:
            # Fallback for other list formats (e.g. chunked CSVs)
            lfs = []
            for p in path:
                lf = scan_l2_quotes(p, cfg)
                if lf is not None:
                    lfs.append(lf)
            if not lfs:
                return None
            # diagonal_relaxed: allow CSVs with different column sets (e.g. early 2023
            # archives missing L2 depth columns). Missing cols filled with null.
            return pl.concat(lfs, how="diagonal_relaxed")

    is_parquet = path.lower().endswith(".parquet")
    
    if is_parquet or cfg.io.input_format == "parquet":
        lf = pl.scan_parquet(path)
    elif cfg.io.input_format == "csv":
        enc = cfg.io.csv_encoding.lower()
        if enc not in ["utf8", "utf-8"]:
            try:
                lf = pl.read_csv(path, encoding=cfg.io.csv_encoding, infer_schema_length=0).lazy()
            except Exception as e:
                if is_parquet:
                     return pl.scan_parquet(path)
                raise e
        else:
            lf = pl.scan_csv(path, encoding=cfg.io.csv_encoding)
    else:
        if is_parquet:
            lf = pl.scan_parquet(path)
        else:
            raise ValueError(f"Unknown input_format: {cfg.io.input_format}")
            
    rename = _rename_map(cfg)
    schema = lf.collect_schema()
    valid_rename = {k: v for k, v in rename.items() if k in schema.names()}
    
    valid_mapped_cols = set(valid_rename.values())
    if not valid_mapped_cols:
        if "microprice" in schema.names():
            return lf
        return None

    # CRITICAL: L2 pipeline requires BOTH depth and trade columns.
    # Early 2023 archives feature split data (行情.csv, 逐笔成交.csv). We skip these 
    # unifiedly instead of creating diagonal garbage frames.
    required = {"bid_p1", "ask_p1", "price", "vol"}
    if not required.issubset(valid_mapped_cols) and "microprice" not in valid_mapped_cols:
        return None
            
    lf = lf.select([pl.col(c) for c in valid_rename.keys()]).rename(valid_rename)

    num_cols = _numeric_cols(cfg)
    existing_cols = lf.collect_schema().names()
    cols_to_cast = [c for c in num_cols if c in existing_cols]
    
    lf = lf.with_columns(
        [pl.col("time").cast(pl.Int64, strict=False)]
        + [pl.col(c).cast(pl.Float64, strict=False) for c in cols_to_cast]
    )
    return lf


def _scan_split_l2_quotes(quote_file: str, trade_file: str, cfg: L2PipelineConfig) -> pl.LazyFrame | None:
    """
    Dedicated parser for early 2023 split format (行情.csv + 逐笔成交.csv).
    Fuses microsecond trades backward onto 3-second L2 snapshot quotes.
    """
    enc = cfg.io.csv_encoding.lower() if cfg.io.csv_encoding else "utf8"
    
    # 1. Load Quotes (行情.csv)
    if enc not in ["utf8", "utf-8"]:
        q_lf = pl.read_csv(quote_file, encoding=cfg.io.csv_encoding, infer_schema_length=0).lazy()
    else:
        q_lf = pl.scan_csv(quote_file, encoding=enc, infer_schema_length=0)
    q_rename = _rename_map(cfg)
    q_schema = q_lf.collect_schema().names()
    q_valid_rename = {k: v for k, v in q_rename.items() if k in q_schema}
    
    q_lf = q_lf.select([pl.col(c) for c in q_valid_rename.keys()]).rename(q_valid_rename)
    
    if "time" not in q_lf.collect_schema().names():
        print(f"[DEBUG] Quitting: no time col in quote. Columns: {q_lf.collect_schema().names()}")
        return None
        
    q_lf = q_lf.with_columns(pl.col("time").cast(pl.Int64, strict=False))
    q_lf = q_lf.sort("time")

    # Drop intersecting columns from quotes explicitly via select to avoid Polars optimizer join bugs
    intersecting = {"price", "vol", "turnover", "bs_flag", "symbol", "exchange", "date"}
    q_keep_cols = [c for c in q_lf.collect_schema().names() if c not in intersecting]
    if "time" not in q_keep_cols:
        q_keep_cols.append("time")
    q_lf = q_lf.select(q_keep_cols)

    # 2. Load Trades (逐笔成交.csv)
    if enc not in ["utf8", "utf-8"]:
        t_lf = pl.read_csv(trade_file, encoding=cfg.io.csv_encoding, infer_schema_length=0).lazy()
    else:
        t_lf = pl.scan_csv(trade_file, encoding=enc, infer_schema_length=0)
    t_rename = _rename_map(cfg)
    # Add alias mappings for split trades format
    t_rename["成交价格"] = "price"
    t_rename["成交数量"] = "vol"
    t_rename["成交金额"] = "turnover"  # Sometimes named 成交金额 instead of 成交额
    t_rename["成交额"] = "turnover"
    
    t_schema = t_lf.collect_schema().names()
    t_valid_rename = {k: v for k, v in t_rename.items() if k in t_schema}
    
    t_lf = t_lf.select([pl.col(c) for c in t_valid_rename.keys()]).rename(t_valid_rename)
    
    if "time" not in t_lf.collect_schema().names():
        print(f"[DEBUG] Quitting: no time col in trade. Columns: {t_lf.collect_schema().names()}")
        return None
        
    t_lf = t_lf.with_columns(pl.col("time").cast(pl.Int64, strict=False))
    t_lf = t_lf.sort("time")

    # 3. Asof Join Trades into Quotes (Trades -> Quotes)
    lf = t_lf.join_asof(q_lf, on="time", strategy="backward")

    # 4. Standard validation
    valid_mapped_cols = set(lf.collect_schema().names())
    required = {"bid_p1", "ask_p1", "price", "vol"}
    if not required.issubset(valid_mapped_cols) and "microprice" not in valid_mapped_cols:
        print(f"[DEBUG] Quitting: missing required col. Required: {required}, found: {valid_mapped_cols}")
        return None

    print(f"[DEBUG] _scan_split_l2_quotes SUCCESS for {quote_file}")

    # 5. Type Casting
    num_cols = _numeric_cols(cfg)
    existing_cols = lf.collect_schema().names()
    cols_to_cast = [c for c in num_cols if c in existing_cols]
    
    lf = lf.with_columns(
        [pl.col(c).cast(pl.Float64, strict=False) for c in cols_to_cast]
    )
    return lf


def _apply_session_filter(lf: pl.LazyFrame, cfg: L2PipelineConfig) -> pl.LazyFrame:
    s = cfg.session
    if not s.enable_session_filter or s.allow_auction:
        return lf
    cond_hhmmssmmm = (
        (pl.col("time") >= int(s.session_1_start)) & (pl.col("time") <= int(s.session_1_end))
    ) | (
        (pl.col("time") >= int(s.session_2_start)) & (pl.col("time") <= int(s.session_2_end))
    )
    ashare = cfg.ashare_session
    t_ms = _time_of_day_ms_expr("time")
    cond_ms = (
        (t_ms >= int(ashare.morning_start_ms)) & (t_ms <= int(ashare.morning_end_ms))
    ) | (
        (t_ms >= int(ashare.afternoon_start_ms)) & (t_ms <= int(ashare.afternoon_end_ms))
    )
    return lf.filter(cond_hhmmssmmm | cond_ms)


def _hhmmssmmm_to_ms_expr(time_expr: pl.Expr) -> pl.Expr:
    t = time_expr.cast(pl.Int64, strict=False)
    hh = t // 10_000_000
    mm = (t // 100_000) % 100
    ss = (t // 1_000) % 100
    ms = t % 1_000
    return ((((hh * 60) + mm) * 60 + ss) * 1_000 + ms).cast(pl.Int64, strict=False)


def _time_of_day_ms_expr(time_col: str = "time") -> pl.Expr:
    """
    Normalize mixed time formats to milliseconds since midnight.
    Supported inputs:
    - HHMMSSmmm (e.g. 93000000)
    - ms-of-day (0~86400000)
    - epoch ms/us
    """
    t = pl.col(time_col).cast(pl.Int64, strict=False)
    hhmmssmmm_ms = _hhmmssmmm_to_ms_expr(t)
    return (
        pl.when(t.is_null())
        .then(None)
        .when(t >= 1_000_000_000_000_000)
        .then((t // 1_000) % 86_400_000)  # epoch microseconds
        .when(t >= 100_000_000_000)
        .then(t % 86_400_000)  # epoch milliseconds
        .when((t >= 10_000_000) & (t <= 235_959_999))
        .then(hhmmssmmm_ms)  # HHMMSSmmm
        .otherwise(t)  # already ms-of-day
        .cast(pl.Int64, strict=False)
    )


def _ashare_elapsed_expr(t_ms: pl.Expr, cfg: L2PipelineConfig) -> pl.Expr:
    ashare = cfg.ashare_session
    morning_len = int(ashare.morning_end_ms - ashare.morning_start_ms)
    return (
        pl.when(t_ms <= int(ashare.morning_end_ms))
        .then(t_ms - int(ashare.morning_start_ms))
        .when(t_ms >= int(ashare.afternoon_start_ms))
        .then((t_ms - int(ashare.afternoon_start_ms)) + morning_len)
        .otherwise(morning_len)
    ).clip(lower_bound=0)


def _apply_quality_filter(lf: pl.LazyFrame, cfg: L2PipelineConfig) -> pl.LazyFrame:
    q = cfg.quality
    conds = []
    if q.drop_zero_price:
        conds.append(pl.col("price") > float(q.min_price))
    if q.drop_zero_volume:
        conds.append(pl.col("vol") > float(q.min_volume))
    if q.require_valid_top_book:
        schema_names = set(lf.collect_schema().names())
        required = {"bid_p1", "ask_p1", "bid_v1", "ask_v1"}
        missing = sorted(required - schema_names)
        if missing:
            pass # Skip strict check for flexibility
        else:
            conds.append(
                (pl.col("bid_p1") > float(q.min_book_price))
                & (pl.col("ask_p1") > float(q.min_book_price))
            )
    if not conds:
        return lf
    cond = conds[0]
    for c in conds[1:]:
        cond = cond & c
    return lf.filter(cond)


def _volume_tick_expr(cfg: L2PipelineConfig) -> pl.Expr:
    vc = cfg.volume_clock
    if vc.volume_mode == "cumulative":
        diff = pl.col("vol") - pl.col("vol").shift(1)
        return (
            pl.when(diff > float(vc.volume_floor))
            .then(diff)
            .otherwise(float(vc.volume_floor))
            .alias("vol_tick")
        )
    if vc.volume_mode == "delta":
        return pl.col("vol").alias("vol_tick")
    raise ValueError(f"Unknown volume_mode: {vc.volume_mode}")


def _microprice_expr(cfg: L2PipelineConfig) -> pl.Expr:
    depth = int(cfg.microprice.depth_level)
    depth = max(1, depth)
    bid_terms, ask_terms, denom_terms = [], [], []
    for i in range(1, depth + 1):
        bid_terms.append(pl.col(f"bid_p{i}") * pl.col(f"ask_v{i}"))
        ask_terms.append(pl.col(f"ask_p{i}") * pl.col(f"bid_v{i}"))
        denom_terms.append(pl.col(f"bid_v{i}") + pl.col(f"ask_v{i}"))
    num = _sum_expr(bid_terms + ask_terms)
    denom = _sum_expr(denom_terms).clip(lower_bound=float(cfg.microprice.depth_floor))
    return (num / denom).alias("microprice")


def _depth_expr(cfg: L2PipelineConfig) -> pl.Expr:
    depth = int(max(cfg.microprice.depth_level, cfg.ofi.depth_levels))
    depth = max(1, depth)
    bid_v = [pl.col(f"bid_v{i}") for i in range(1, depth + 1)]
    ask_v = [pl.col(f"ask_v{i}") for i in range(1, depth + 1)]
    denom = float(2 * depth)
    return (_sum_expr(bid_v + ask_v) / denom).alias("depth")


def _ofi_expr(cfg: L2PipelineConfig) -> pl.Expr:
    ofi_cfg = cfg.ofi
    if ofi_cfg.ofi_mode == "price_change":
        return (
            pl.when(pl.col("price") > pl.col("price").shift(1)).then(pl.col("vol_tick"))
            .when(pl.col("price") < pl.col("price").shift(1)).then(-pl.col("vol_tick"))
            .otherwise(float(ofi_cfg.ofi_zero_value)).alias("v_ofi")
        )
    if ofi_cfg.ofi_mode == "queue_delta":
        depth = int(max(1, ofi_cfg.depth_levels))
        decay = float(ofi_cfg.ofi_weight_decay)
        parts = []
        for i in range(1, depth + 1):
            weight = decay ** (i - 1)
            bid_contrib = (
                pl.when(pl.col(f"bid_p{i}") > pl.col(f"bid_p{i}").shift(1)).then(pl.col(f"bid_v{i}"))
                .when(pl.col(f"bid_p{i}") < pl.col(f"bid_p{i}").shift(1)).then(-pl.col(f"bid_v{i}").shift(1))
                .otherwise(pl.col(f"bid_v{i}") - pl.col(f"bid_v{i}").shift(1))
            )
            ask_contrib = (
                pl.when(pl.col(f"ask_p{i}") < pl.col(f"ask_p{i}").shift(1)).then(pl.col(f"ask_v{i}"))
                .when(pl.col(f"ask_p{i}") > pl.col(f"ask_p{i}").shift(1)).then(-pl.col(f"ask_v{i}").shift(1))
                .otherwise(pl.col(f"ask_v{i}") - pl.col(f"ask_v{i}").shift(1))
            )
            parts.append((bid_contrib - ask_contrib) * weight)
        return _sum_expr(parts).alias("v_ofi")
    raise ValueError(f"Unknown ofi_mode: {ofi_cfg.ofi_mode}")


def _lob_flux_expr(group_col: str | None = None) -> pl.Expr:
    """LOB flux = |Δbid_v1| + |Δask_v1|. Must isolate by symbol to prevent
    cross-symbol diff bleeding (stock B open - stock A close = phantom flux)."""
    b_diff = pl.col("bid_v1").diff().over(group_col) if group_col else pl.col("bid_v1").diff()
    a_diff = pl.col("ask_v1").diff().over(group_col) if group_col else pl.col("ask_v1").diff()
    return (b_diff.abs() + a_diff.abs()).alias("lob_flux")


def build_l2_frames(path: str | List[str], cfg: L2PipelineConfig, target_frames: float | None = None) -> pl.DataFrame:
    # --- ANTI-FRAGILE MEMORY & ISOLATION FIX ---
    # Process files individually to cap Polars memory at ~100MB per dataset,
    # rather than bursting to 50GB+ when resolving a 5000-stock LazyFrame DAG.
    # This also guarantees cross-symbol isolation for chronological shift() ops.
    if isinstance(path, list):
        if not path:
            return pl.DataFrame()
            
        # If this list is ALREADY a targeted split-CSV group for a single symbol,
        # we bypass the chunking loop and fall through to the ETL engine below.
        is_split_group = len(path) <= 4 and any("行情.csv" in str(p) for p in path) and any("逐笔成交.csv" in str(p) for p in path)
        if not is_split_group:
            from collections import defaultdict
            from pathlib import Path
            
            # Group flat list of thousands of CSVs into per-symbol lists
            grouped = defaultdict(list)
            for p in path:
                grouped[str(Path(p).parent)].append(str(p))
                
            collected = []
            for symbol_dir, group_files in grouped.items():
                try:
                    # Depending on whether it's 2024 unified CSVs (len=1) or 2023 split (len>1),
                    # recursively call build_l2_frames. The targeted group will either bypass 
                    # the list-check entirely or hit the is_split_group=True check.
                    if len(group_files) == 1:
                        df = build_l2_frames(group_files[0], cfg, target_frames)
                    else:
                        df = build_l2_frames(group_files, cfg, target_frames)
                        
                    if df.height > 0:
                        collected.append(df)
                except Exception as e:
                    print(f"Error processing {symbol_dir}: {e}")
                    continue
            if not collected:
                return pl.DataFrame()
            return pl.concat(collected, how="vertical_relaxed")

    # Standard single-file (or single split-group) processing
    lf = scan_l2_quotes(path, cfg)
    if lf is None:
        return pl.DataFrame()
    
    # Check for symbol column to enable multi-symbol isolation
    schema_names = lf.collect_schema().names()
    group_col = "symbol" if "symbol" in schema_names else None

    # Sort strictly by symbol then time (Causal Ordering)
    sort_cols = ["date", "time"]
    if group_col:
        sort_cols = [group_col, "date", "time"]
    lf = lf.sort(sort_cols)
    
    lf = _apply_session_filter(lf, cfg)
    lf = _apply_quality_filter(lf, cfg)

    lf = lf.with_columns(
        [_volume_tick_expr(cfg), _microprice_expr(cfg), _depth_expr(cfg)]
    )
    if cfg.quality.drop_nonpositive_frame_price:
        lf = lf.filter(pl.col("microprice") > float(cfg.quality.min_frame_price))
    lf = lf.with_columns(_ofi_expr(cfg))
    lf = lf.with_columns(_lob_flux_expr(group_col))
    lf = lf.with_columns(_time_of_day_ms_expr("time").alias("__time_ms"))

    # Phase 1: 3-second snapshot aggregation handling (Anti-Aliasing Low-Pass Filter)
    # Must group by symbol if present to avoid cross-contamination
    if group_col:
        lf = lf.with_columns([
            pl.col("v_ofi").rolling_mean(window_size=3, min_periods=1).over(group_col).alias("v_ofi"),
            pl.col("depth").rolling_mean(window_size=3, min_periods=1).over(group_col).alias("depth")
        ])
    else:
        lf = lf.with_columns([
            pl.col("v_ofi").rolling_mean(window_size=3, min_periods=1).alias("v_ofi"),
            pl.col("depth").rolling_mean(window_size=3, min_periods=1).alias("depth")
        ])

    vc = cfg.volume_clock

    if getattr(vc, "dynamic_bucket_size", False) or target_frames is not None:
        frames_target = float(target_frames) if target_frames is not None else float(vc.daily_volume_proxy_div)

        elapsed = _ashare_elapsed_expr(pl.col("__time_ms"), cfg)
        time_fraction = (elapsed / float(cfg.ashare_session.total_duration_ms)).clip(
            lower_bound=0.05, upper_bound=1.0
        )

        # Cumulative volume must be per-symbol
        if group_col:
            cum_vol_expr = pl.col("vol_tick").cum_sum().over(group_col)
        else:
            cum_vol_expr = pl.col("vol_tick").cum_sum()
            
        est_daily_vol = cum_vol_expr / time_fraction
        target_bucket_size = est_daily_vol / frames_target
        bucket_size_expr = (
            pl.when(target_bucket_size > float(vc.min_bucket_size))
            .then(target_bucket_size)
            .otherwise(float(vc.min_bucket_size))
        )

        lf = lf.with_columns(
            [
                cum_vol_expr.alias("cum_vol"),
                bucket_size_expr.alias("dynamic_bucket_sz"),
            ]
        )
        
        # Bucket ID Calculation
        if group_col:
            lf = lf.with_columns(
                (pl.col("vol_tick") / pl.col("dynamic_bucket_sz"))
                .cum_sum().over(group_col)
                .cast(pl.Int64)
                .alias("bucket_id")
            )
        else:
            lf = lf.with_columns(
                (pl.col("vol_tick") / pl.col("dynamic_bucket_sz"))
                .cum_sum()
                .cast(pl.Int64)
                .alias("bucket_id")
            )
    else:
        if group_col:
            lf = lf.with_columns(pl.col("vol_tick").cum_sum().over(group_col).alias("cum_vol"))
        else:
            lf = lf.with_columns(pl.col("vol_tick").cum_sum().alias("cum_vol"))
            
        lf = lf.with_columns(
            (pl.col("cum_vol") // float(vc.bucket_size)).cast(pl.Int64).alias("bucket_id")
        )

    schema_names = set(lf.collect_schema().names())
    if {"bid_v1", "ask_v1"}.issubset(schema_names):
        singularity_eps = float(cfg.micro.limit_singularity_eps)
        singularity_expr = (
            (pl.col("bid_v1") <= singularity_eps) | (pl.col("ask_v1") <= singularity_eps)
        ).alias("is_singularity")
    else:
        singularity_expr = pl.lit(False).alias("is_singularity")
    lf = lf.with_columns(singularity_expr)

    # Group By (Must include Symbol if present)
    group_keys = ["bucket_id"]
    if group_col:
        group_keys = [group_col, "bucket_id"]

    frames = lf.group_by(group_keys).agg(
        [
            pl.col("microprice").first().alias("open"),
            pl.col("microprice").last().alias("close"),
            pl.col("microprice").std().alias("sigma"),
            pl.col("v_ofi").sum().alias("net_ofi"),
            pl.col("depth").mean().alias("depth"),
            pl.col("microprice").alias("trace"),
            pl.col("v_ofi").alias("ofi_list"),
            pl.col("v_ofi").cum_sum().alias("ofi_trace"),
            pl.col("vol_tick").alias("vol_list"),
            pl.col("vol_tick").cum_sum().alias("vol_trace"),
            (pl.col("__time_ms") - pl.col("__time_ms").first()).alias("time_trace"),
            pl.col("__time_ms").first().alias("time_start"),
            pl.col("__time_ms").last().alias("time_end"),
            pl.col("date").first().alias("_date_temp"),
            pl.col("symbol").first().alias("_symbol_temp"),
            pl.len().alias("n_ticks"),
            pl.col("vol_tick").sum().alias("trade_vol"),
            pl.col("lob_flux").sum().alias("cancel_vol"),
            pl.col("is_singularity").max().alias("has_singularity"),
        ],
        maintain_order=True,
    )
    
    # Rename temp columns to standard names if they were not group keys
    rename_rules = {}
    if "date" not in frames.collect_schema().names():
        rename_rules["_date_temp"] = "date"
    if "symbol" not in frames.collect_schema().names():
        rename_rules["_symbol_temp"] = "symbol"
        
    frames = frames.rename(rename_rules)
    frames = frames.drop(["_date_temp", "_symbol_temp"], strict=False)

    frames = frames.filter(pl.col("n_ticks") >= int(vc.min_ticks_per_bucket))
    if cfg.quality.drop_nonpositive_frame_price:
        min_frame_px = float(cfg.quality.min_frame_price)
        frames = frames.filter(
            (pl.col("open") > min_frame_px) & (pl.col("close") > min_frame_px)
        )
    frames = frames.with_columns(
        [
            (pl.col("time_end") - pl.col("time_start")).alias("bar_duration_ms"),
            (~pl.col("has_singularity")).alias("is_physics_valid"),
        ]
    )
    return frames.collect()
