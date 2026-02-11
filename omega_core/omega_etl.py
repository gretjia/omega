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


def scan_l2_quotes(path: str | List[str], cfg: L2PipelineConfig) -> pl.LazyFrame:
    if isinstance(path, list):
        lfs = [scan_l2_quotes(p, cfg) for p in path]
        return pl.concat(lfs)

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
    
    if not valid_rename:
        if "microprice" in schema.names():
            return lf
            
    lf = lf.select([pl.col(c) for c in valid_rename.keys()]).rename(valid_rename)

    num_cols = _numeric_cols(cfg)
    existing_cols = lf.collect_schema().names()
    cols_to_cast = [c for c in num_cols if c in existing_cols]
    
    lf = lf.with_columns(
        [pl.col("time").cast(pl.Int64, strict=False)]
        + [pl.col(c).cast(pl.Float64, strict=False) for c in cols_to_cast]
    )
    return lf


def _apply_session_filter(lf: pl.LazyFrame, cfg: L2PipelineConfig) -> pl.LazyFrame:
    s = cfg.session
    if not s.enable_session_filter or s.allow_auction:
        return lf
    cond = (
        (pl.col("time") >= int(s.session_1_start)) & (pl.col("time") <= int(s.session_1_end))
    ) | (
        (pl.col("time") >= int(s.session_2_start)) & (pl.col("time") <= int(s.session_2_end))
    )
    return lf.filter(cond)


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


def _lob_flux_expr() -> pl.Expr:
    return (pl.col("bid_v1").diff().abs() + pl.col("ask_v1").diff().abs()).alias("lob_flux")


def build_l2_frames(path: str, cfg: L2PipelineConfig, target_frames: float | None = None) -> pl.DataFrame:
    lf = scan_l2_quotes(path, cfg)
    lf = lf.sort("time")
    lf = _apply_session_filter(lf, cfg)
    lf = _apply_quality_filter(lf, cfg)

    lf = lf.with_columns(
        [_volume_tick_expr(cfg), _microprice_expr(cfg), _depth_expr(cfg)]
    )
    if cfg.quality.drop_nonpositive_frame_price:
        lf = lf.filter(pl.col("microprice") > float(cfg.quality.min_frame_price))
    lf = lf.with_columns(_ofi_expr(cfg))
    lf = lf.with_columns(_lob_flux_expr())

    vc = cfg.volume_clock

    # --- v5.0 Fix: Causal Volume Projection ---
    # Replace global .sum().over(1) (Paradox 3) with Causal Extrapolation.
    # Est_Daily_Vol = Current_Cum_Vol / Fraction_Of_Day_Passed
    
    if getattr(vc, "dynamic_bucket_size", False) or target_frames is not None:
        frames_target = float(target_frames) if target_frames is not None else float(vc.daily_volume_proxy_div)
        
        # 1. Calculate Time Fraction
        session_start = int(cfg.session.session_1_start)
        session_end = int(cfg.session.session_2_end)
        total_duration = max(1.0, float(session_end - session_start))
        
        # Avoid div/0 at opening: clamp elapsed time to min 1 min (60000 ms)
        # Ensure elapsed is safe
        elapsed = (pl.col("time") - session_start).clip(lower_bound=60000)
        time_fraction = (elapsed / total_duration).clip(lower_bound=0.01, upper_bound=1.0)
        
        # 2. Causal Extrapolation
        # If we are 10% into the day and have 1M vol, we project 10M total.
        cum_vol_expr = pl.col("vol_tick").cum_sum()
        est_daily_vol = cum_vol_expr / time_fraction
        
        # 3. Dynamic Bucket Size
        target_bucket_size = est_daily_vol / frames_target
        
        bucket_size_expr = (
            pl.when(target_bucket_size > float(vc.min_bucket_size))
            .then(target_bucket_size)
            .otherwise(float(vc.min_bucket_size))
        )
        
        lf = lf.with_columns(
            [
                cum_vol_expr.alias("cum_vol"),
                bucket_size_expr.alias("dynamic_bucket_sz")
            ]
        )
        
        # Integral Bucket Sizing
        # We integrate 1/BucketSize to find BucketID. This naturally adapts to volatility.
        lf = lf.with_columns(
            (pl.col("vol_tick") / pl.col("dynamic_bucket_sz")).cum_sum().cast(pl.Int64).alias("bucket_id")
        )
        
    else:
        # Static bucket mode
        lf = lf.with_columns(
            [pl.col("vol_tick").cum_sum().alias("cum_vol")]
        )
        lf = lf.with_columns(
            [(pl.col("cum_vol") // float(vc.bucket_size)).cast(pl.Int64).alias("bucket_id")]
        )

    frames = lf.group_by("bucket_id").agg(
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
            (pl.col("time") - pl.col("time").first()).alias("time_trace"),
            pl.col("time").first().alias("time_start"),
            pl.col("time").last().alias("time_end"),
            pl.col("date").first().alias("date"),
            pl.count().alias("n_ticks"),
            pl.col("vol_tick").sum().alias("trade_vol"),
            pl.col("lob_flux").sum().alias("cancel_vol"),
        ],
        maintain_order=True,
    )

    frames = frames.filter(pl.col("n_ticks") >= int(vc.min_ticks_per_bucket))
    if cfg.quality.drop_nonpositive_frame_price:
        min_frame_px = float(cfg.quality.min_frame_price)
        frames = frames.filter(
            (pl.col("open") > min_frame_px) & (pl.col("close") > min_frame_px)
        )
    frames = frames.with_columns(
        (pl.col("time_end") - pl.col("time_start")).alias("bar_duration_ms")
    )
    return frames.collect()