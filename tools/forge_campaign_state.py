#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import polars as pl

try:
    from numba import njit
except Exception:  # pragma: no cover - runtime fallback for nodes without numba
    njit = None


# Keep local Phase-1 forge from oversubscribing controller UMA / worker CPUs.
os.environ.setdefault("POLARS_MAX_THREADS", str(max(1, (os.cpu_count() or 2) // 2)))

DATE_HASH_PARQUET_RE = re.compile(r"^(?P<date>\d{8})_[0-9a-f]{7}\.parquet$")
DEFAULT_HORIZONS = (5, 10, 20)
DEFAULT_EPS = 1e-12


def _parse_years(raw: str | None) -> set[str] | None:
    if raw is None or not str(raw).strip():
        return None
    years = {x.strip() for x in str(raw).split(",") if x.strip()}
    return years or None


def _date_from_path(path: str) -> str | None:
    m = DATE_HASH_PARQUET_RE.match(Path(path).name)
    if not m:
        return None
    return str(m.group("date"))


def _expand_patterns(patterns: Iterable[str], years: set[str] | None = None) -> list[str]:
    files: list[str] = []
    for pattern in patterns:
        for path in sorted(glob.glob(str(pattern))):
            if not path.endswith(".parquet"):
                continue
            if years is not None:
                ymd = _date_from_path(path)
                if ymd is None or ymd[:4] not in years:
                    continue
            files.append(path)
    # De-duplicate while preserving stable order.
    return list(dict.fromkeys(files))


def _half_life_alpha(tau: int) -> float:
    if tau <= 0:
        raise ValueError(f"half-life must be positive, got {tau}")
    return float(1.0 - math.exp(-math.log(2.0) / float(tau)))


def _collect_daily_spine_from_l1(l1_files: list[str]) -> pl.DataFrame:
    daily_frames: list[pl.DataFrame] = []
    for one in l1_files:
        lf = pl.scan_parquet(one).select(["symbol", "date", "time", "price"])
        day_df = (
            lf.with_columns(
                [
                    pl.col("symbol").cast(pl.Utf8, strict=False),
                    pl.col("date").cast(pl.Utf8, strict=False).str.slice(0, 8).alias("pure_date"),
                    pl.col("time").cast(pl.Int64, strict=False).alias("__time_num"),
                    pl.col("price").cast(pl.Float64, strict=False),
                ]
            )
            .group_by(["symbol", "pure_date"])
            .agg(
                [
                    pl.col("price").sort_by(pl.col("__time_num")).first().alias("open"),
                    pl.col("price").max().alias("high"),
                    pl.col("price").min().alias("low"),
                    pl.col("price").sort_by(pl.col("__time_num")).last().alias("close"),
                    pl.len().alias("n_ticks_day"),
                ]
            )
            .collect()
        )
        if day_df.height > 0:
            daily_frames.append(day_df)
    if not daily_frames:
        return pl.DataFrame(
            schema={
                "symbol": pl.Utf8,
                "pure_date": pl.Utf8,
                "open": pl.Float64,
                "high": pl.Float64,
                "low": pl.Float64,
                "close": pl.Float64,
                "n_ticks_day": pl.UInt32,
            }
        )
    return pl.concat(daily_frames, how="vertical_relaxed").sort(["symbol", "pure_date"])


def _collect_daily_events_from_l2(l2_files: list[str]) -> pl.DataFrame:
    daily_frames: list[pl.DataFrame] = []
    optional_cols = ["epiplexity", "bits_topology"]
    for one in l2_files:
        lf = pl.scan_parquet(one)
        schema_names = set(lf.collect_schema().names())
        required = {"symbol", "date", "singularity_vector"}
        if not required.issubset(schema_names):
            continue
        select_cols = ["symbol", "date", "singularity_vector"] + [c for c in optional_cols if c in schema_names]
        day_df = (
            lf.select(select_cols)
            .with_columns(
                [
                    pl.col("symbol").cast(pl.Utf8, strict=False),
                    pl.col("date").cast(pl.Utf8, strict=False).str.slice(0, 8).alias("pure_date"),
                    pl.col("singularity_vector").cast(pl.Float64, strict=False).fill_null(0.0).fill_nan(0.0),
                ]
            )
            .group_by(["symbol", "pure_date"])
            .agg(
                [
                    pl.col("singularity_vector").sum().alias("F_force"),
                    pl.col("singularity_vector").abs().sum().alias("A_action"),
                    pl.len().alias("N_events"),
                ]
                + (
                    [pl.col("epiplexity").cast(pl.Float64, strict=False).sum().alias("day_epi_integral")]
                    if "epiplexity" in select_cols
                    else []
                )
                + (
                    [pl.col("bits_topology").cast(pl.Float64, strict=False).sum().alias("day_topo_integral")]
                    if "bits_topology" in select_cols
                    else []
                )
            )
            .collect()
        )
        if day_df.height > 0:
            daily_frames.append(day_df)
    if not daily_frames:
        return pl.DataFrame(
            schema={
                "symbol": pl.Utf8,
                "pure_date": pl.Utf8,
                "F_force": pl.Float64,
                "A_action": pl.Float64,
                "N_events": pl.UInt32,
                "day_epi_integral": pl.Float64,
                "day_topo_integral": pl.Float64,
            }
        )
    return pl.concat(daily_frames, how="vertical_relaxed").sort(["symbol", "pure_date"])


def _compute_triple_barrier_labels_impl(
    sym_ids: np.ndarray,
    opens: np.ndarray,
    highs: np.ndarray,
    lows: np.ndarray,
    vol20d: np.ndarray,
    horizon: int,
    up_mult: float,
    down_mult: float,
) -> np.ndarray:
    n = len(sym_ids)
    out = np.zeros(n, dtype=np.int8)
    for i in range(n):
        if i + horizon >= n or i + 1 >= n:
            continue
        sid = sym_ids[i]
        if sym_ids[i + 1] != sid or sym_ids[i + horizon] != sid:
            continue

        entry = opens[i + 1]
        sigma = vol20d[i]
        if not np.isfinite(entry) or entry <= 1e-12 or not np.isfinite(sigma):
            continue

        upper = entry * (1.0 + up_mult * sigma)
        lower = entry * (1.0 - down_mult * sigma)
        label = np.int8(0)

        # The written formula is d+1 .. d+H inclusive, with conservative stop precedence.
        for curr_idx in range(i + 1, i + horizon + 1):
            if sym_ids[curr_idx] != sid:
                label = np.int8(0)
                break
            lo = lows[curr_idx]
            hi = highs[curr_idx]
            if np.isfinite(lo) and lo <= lower:
                label = np.int8(-1)
                break
            if np.isfinite(hi) and hi >= upper:
                label = np.int8(1)
                break
        out[i] = label
    return out


if njit is not None:
    compute_triple_barrier_labels = njit(cache=True)(_compute_triple_barrier_labels_impl)
else:  # pragma: no cover - exercised on worker nodes without numba
    compute_triple_barrier_labels = _compute_triple_barrier_labels_impl


def build_campaign_state_frame(
    daily_spine: pl.DataFrame,
    daily_events: pl.DataFrame,
    horizons: Iterable[int] = DEFAULT_HORIZONS,
    eps: float = DEFAULT_EPS,
) -> pl.DataFrame:
    horizons = tuple(int(x) for x in horizons)
    if daily_spine.height <= 0:
        raise ValueError("daily_spine is empty")

    df = (
        daily_spine.join(daily_events, on=["symbol", "pure_date"], how="left")
        .with_columns(
            [
                pl.col("F_force").fill_null(0.0).fill_nan(0.0),
                pl.col("A_action").fill_null(0.0).fill_nan(0.0),
                pl.col("N_events").fill_null(0).cast(pl.Int64, strict=False),
                pl.col("day_epi_integral").fill_null(0.0).fill_nan(0.0),
                pl.col("day_topo_integral").fill_null(0.0).fill_nan(0.0),
            ]
        )
        .sort(["symbol", "pure_date"])
    )

    df = df.with_columns(
        (
            pl.col("close") / pl.col("close").shift(1).over("symbol") - 1.0
        ).alias("raw_d1_ret")
    )
    df = df.with_columns(
        pl.col("raw_d1_ret")
        .rolling_std(window_size=20)
        .over("symbol")
        .fill_nan(0.02)
        .fill_null(0.02)
        .alias("vol20d")
    )

    state_exprs: list[pl.Expr] = []
    omega_exprs: list[pl.Expr] = []
    psi_exprs: list[pl.Expr] = []
    raw_label_exprs: list[pl.Expr] = []

    next_open_expr = pl.col("open").shift(-1).over("symbol").alias("entry_open_t1")
    df = df.with_columns(next_open_expr)

    for tau in horizons:
        alpha = _half_life_alpha(tau)
        state_exprs.extend(
            [
                pl.col("F_force")
                .ewm_mean(alpha=alpha, adjust=False, ignore_nulls=False)
                .over("symbol")
                .alias(f"S_{tau}d"),
                pl.col("A_action")
                .ewm_mean(alpha=alpha, adjust=False, ignore_nulls=False)
                .over("symbol")
                .alias(f"V_{tau}d"),
            ]
        )
        raw_label_exprs.append(
            (
                pl.col("close").shift(-tau).over("symbol") / pl.col("entry_open_t1") - 1.0
            ).alias(f"raw_ret_t1_to_{tau}d")
        )

    df = df.with_columns(state_exprs)
    for tau in horizons:
        omega_exprs.append(
            (pl.col(f"S_{tau}d").abs() / (pl.col(f"V_{tau}d") + float(eps))).alias(f"Omega_{tau}d")
        )
        psi_exprs.append((pl.col(f"S_{tau}d") * pl.col(f"Omega_{tau}d")).alias(f"Psi_{tau}d"))

    df = df.with_columns(omega_exprs + psi_exprs + raw_label_exprs)

    excess_exprs: list[pl.Expr] = []
    for horizon in horizons:
        excess_exprs.append(
            (
                pl.col(f"raw_ret_t1_to_{horizon}d")
                - pl.col(f"raw_ret_t1_to_{horizon}d").mean().over("pure_date")
            ).alias(f"excess_ret_t1_to_{horizon}d")
        )
    df = df.with_columns(excess_exprs)

    sym_ids = (
        df.select(pl.col("symbol").cast(pl.Categorical).to_physical().cast(pl.Int32))
        .to_series()
        .to_numpy()
    )
    opens = df["open"].to_numpy()
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    vol20d = df["vol20d"].to_numpy()

    barrier_series: list[pl.Series] = []
    for horizon in horizons:
        labels = compute_triple_barrier_labels(
            sym_ids=sym_ids,
            opens=opens,
            highs=highs,
            lows=lows,
            vol20d=vol20d,
            horizon=int(horizon),
            up_mult=2.0,
            down_mult=1.0,
        )
        barrier_series.append(pl.Series(f"barrier_{horizon}d", labels, dtype=pl.Int8))
    df = df.with_columns(barrier_series)

    max_horizon = max(horizons)
    df = df.drop_nulls(subset=[f"excess_ret_t1_to_{max_horizon}d"])
    return df


def _build_meta(
    out_path: Path,
    l1_files: list[str],
    l2_files: list[str],
    df: pl.DataFrame,
    horizons: Iterable[int],
) -> dict:
    horizons = tuple(int(x) for x in horizons)
    meta: dict[str, object] = {
        "output_path": str(out_path),
        "rows": int(df.height),
        "columns": list(df.columns),
        "horizons": list(horizons),
        "l1_files": len(l1_files),
        "l2_files": len(l2_files),
        "min_date": df["pure_date"].min() if df.height > 0 else None,
        "max_date": df["pure_date"].max() if df.height > 0 else None,
        "symbols": int(df.select(pl.col("symbol").n_unique()).item()) if df.height > 0 else 0,
    }
    for horizon in horizons:
        col = f"excess_ret_t1_to_{horizon}d"
        if col in df.columns:
            zero_frac = (
                df.select((pl.col(col).fill_null(0.0).fill_nan(0.0) == 0.0).mean()).item()
                if df.height > 0
                else 0.0
            )
            meta[f"{col}_zero_fraction"] = float(zero_frac or 0.0)
    return meta


def forge_campaign_state(
    l1_patterns: list[str],
    l2_patterns: list[str],
    output_path: str,
    years: set[str] | None,
    horizons: Iterable[int],
    eps: float,
) -> dict:
    l1_files = _expand_patterns(l1_patterns, years=years)
    l2_files = _expand_patterns(l2_patterns, years=years)
    if not l1_files:
        raise FileNotFoundError("no L1 daily-spine source files matched the supplied patterns")
    if not l2_files:
        raise FileNotFoundError("no L2 pulse-source files matched the supplied patterns")

    daily_spine = _collect_daily_spine_from_l1(l1_files)
    daily_events = _collect_daily_events_from_l2(l2_files)
    campaign_df = build_campaign_state_frame(daily_spine=daily_spine, daily_events=daily_events, horizons=horizons, eps=eps)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    campaign_df.write_parquet(tmp_path, compression="zstd")
    tmp_path.replace(out_path)

    meta = _build_meta(out_path=out_path, l1_files=l1_files, l2_files=l2_files, df=campaign_df, horizons=horizons)
    meta_path = out_path.with_suffix(out_path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Forge V653 campaign-state matrix from L1 daily spine plus Stage2 pulse source.")
    ap.add_argument("--l1-input-pattern", action="append", required=True, help="Glob pattern(s) for raw L1 daily-spine source parquet files.")
    ap.add_argument("--l2-input-pattern", action="append", required=True, help="Glob pattern(s) for Stage2 pulse-source parquet files.")
    ap.add_argument("--output-path", required=True, help="Output campaign-state parquet path.")
    ap.add_argument("--years", default="", help="Comma-separated years to keep, for example 2023,2024.")
    ap.add_argument("--horizons", default="5,10,20", help="Comma-separated day horizons. Default: 5,10,20.")
    ap.add_argument("--eps", type=float, default=DEFAULT_EPS, help="Small epsilon used in Omega calculation.")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    years = _parse_years(args.years)
    horizons = tuple(int(x) for x in str(args.horizons).split(",") if str(x).strip())
    meta = forge_campaign_state(
        l1_patterns=args.l1_input_pattern,
        l2_patterns=args.l2_input_pattern,
        output_path=args.output_path,
        years=years,
        horizons=horizons,
        eps=float(args.eps),
    )
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
