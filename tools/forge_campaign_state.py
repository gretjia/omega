#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Iterable

import numpy as np
import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import L2PipelineConfig

try:
    from numba import njit
except Exception:  # pragma: no cover - runtime fallback for nodes without numba
    njit = None


# Keep local Phase-1 forge from oversubscribing controller UMA / worker CPUs.
os.environ.setdefault("POLARS_MAX_THREADS", str(max(1, (os.cpu_count() or 2) // 2)))

DATE_HASH_PARQUET_RE = re.compile(r"^(?P<date>\d{8})_[0-9a-f]{7}\.parquet$")
DEFAULT_HORIZONS = (5, 10, 20)
DEFAULT_EPS = 1e-12
DEFAULT_PULSE_MIN_GAP = 30
DEFAULT_PULSE_FLOOR = 1e-12
DEFAULT_WINDOW_LEN = int(L2PipelineConfig().epiplexity.min_trace_len)


def _log(msg: str) -> None:
    print(f"[V653] {msg}", flush=True)


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


def _assert_unique_symbol_date(df: pl.DataFrame, frame_name: str) -> None:
    if df.height <= 0:
        return
    dupes = (
        df.group_by(["symbol", "pure_date"])
        .len()
        .filter(pl.col("len") > 1)
    )
    if dupes.height > 0:
        raise ValueError(f"{frame_name} contains duplicate symbol/pure_date rows: {dupes.height}")


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


def _collect_legacy_daily_events_from_l2(l2_files: list[str]) -> pl.DataFrame:
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


def _choose_intraday_order_col(schema_names: set[str]) -> str:
    for cand in ("time_end", "bucket_id", "time"):
        if cand in schema_names:
            return cand
    raise ValueError("no stable intraday ordering key found; need one of: time_end, bucket_id, time")


def _bits_topology_expr(schema_names: set[str]) -> pl.Expr:
    if "bits_topology" in schema_names:
        return pl.col("bits_topology").cast(pl.Float64, strict=False).fill_null(0.0).fill_nan(0.0)
    if {"topo_area", "topo_energy"}.issubset(schema_names):
        compactness = (4.0 * math.pi * pl.col("topo_area").cast(pl.Float64, strict=False).abs()) / (
            pl.col("topo_energy").cast(pl.Float64, strict=False) ** 2 + 1e-12
        )
        return (compactness * math.log(float(DEFAULT_WINDOW_LEN))).clip(lower_bound=0.0).fill_null(0.0).fill_nan(0.0)
    raise ValueError("missing bits_topology and no topo_area/topo_energy fallback is available")


def _build_intraday_sort_expr(order_col: str) -> pl.Expr:
    if order_col in {"time_end", "time"}:
        return pl.col(order_col).cast(pl.Utf8, strict=False).alias("__order_txt")
    return pl.col(order_col).cast(pl.Int64, strict=False).cast(pl.Utf8, strict=False).alias("__order_txt")


def _assign_intraday_ordinals(df: pl.DataFrame) -> pl.DataFrame:
    if df.height <= 0:
        return df.with_columns(pl.lit(0).cast(pl.Int32).alias("__ord"))
    symbols = df["symbol"].to_list()
    dates = df["pure_date"].to_list()
    ords = np.empty(df.height, dtype=np.int32)
    last_key: tuple[str, str] | None = None
    counter = 0
    for idx, key in enumerate(zip(symbols, dates)):
        if key != last_key:
            counter = 0
            last_key = key
        ords[idx] = counter
        counter += 1
    return df.with_columns(pl.Series("__ord", ords, dtype=pl.Int32))


def _factorize_day_ids(symbols: list[str], pure_dates: list[str]) -> np.ndarray:
    out = np.empty(len(symbols), dtype=np.int32)
    last_key: tuple[str, str] | None = None
    day_id = -1
    for idx, key in enumerate(zip(symbols, pure_dates)):
        if key != last_key:
            day_id += 1
            last_key = key
        out[idx] = day_id
    return out


def _collect_intraday_candidates_from_l2(
    l2_files: list[str],
    pulse_floor: float,
    require_is_signal: bool,
    require_is_physics_valid: bool,
    eps: float,
) -> pl.DataFrame:
    candidate_frames: list[pl.DataFrame] = []
    for one in l2_files:
        lf = pl.scan_parquet(one)
        schema_names = set(lf.collect_schema().names())
        required = {"symbol", "date", "singularity_vector", "epiplexity"}
        missing = required.difference(schema_names)
        if missing:
            raise ValueError(f"{Path(one).name} missing required pulse columns: {sorted(missing)}")
        order_col = _choose_intraday_order_col(schema_names)
        if require_is_signal and "is_signal" not in schema_names:
            raise ValueError(f"{Path(one).name} missing required is_signal column")
        if require_is_physics_valid and "is_physics_valid" not in schema_names:
            raise ValueError(f"{Path(one).name} missing required is_physics_valid column")

        bits_expr = _bits_topology_expr(schema_names).alias("__bits_topology")
        epi_expr = pl.col("epiplexity").cast(pl.Float64, strict=False).fill_null(0.0).fill_nan(0.0).clip(lower_bound=0.0).alias("__epiplexity")
        sing_expr = pl.col("singularity_vector").cast(pl.Float64, strict=False).fill_null(0.0).fill_nan(0.0).alias("__singularity")

        select_cols = ["symbol", "date", "singularity_vector", "epiplexity", order_col]
        if "bits_topology" in schema_names:
            select_cols.append("bits_topology")
        elif {"topo_area", "topo_energy"}.issubset(schema_names):
            select_cols.extend(["topo_area", "topo_energy"])
        if "srl_phase" in schema_names:
            select_cols.append("srl_phase")
        if "is_signal" in schema_names:
            select_cols.append("is_signal")
        if "is_physics_valid" in schema_names:
            select_cols.append("is_physics_valid")

        one_df = (
            lf.select(list(dict.fromkeys(select_cols)))
            .with_columns(
                [
                    pl.col("symbol").cast(pl.Utf8, strict=False),
                    pl.col("date").cast(pl.Utf8, strict=False).str.slice(0, 8).alias("pure_date"),
                    _build_intraday_sort_expr(order_col),
                    epi_expr,
                    bits_expr,
                    sing_expr,
                ]
            )
            .with_columns(
                [
                    pl.col("__epiplexity").alias("E"),
                    pl.col("__bits_topology").alias("T"),
                    (
                        pl.col("srl_phase").cast(pl.Float64, strict=False).fill_null(0.0).fill_nan(0.0)
                        if "srl_phase" in schema_names
                        else pl.col("__singularity") / (pl.col("__epiplexity") + pl.col("__bits_topology") + float(eps))
                    ).alias("Phi"),
                    pl.when(pl.col("__singularity") >= 0.0).then(pl.lit(1)).otherwise(pl.lit(-1)).alias("__sv_sign"),
                ]
            )
        )
        if require_is_signal:
            one_df = one_df.filter(pl.col("is_signal") == True)
        if require_is_physics_valid:
            one_df = one_df.filter(pl.col("is_physics_valid") == True)
        one_df = (
            one_df.filter(pl.col("__singularity").abs() > float(pulse_floor))
            .select(
                [
                    "symbol",
                    "pure_date",
                    "__order_txt",
                    "__singularity",
                    "__sv_sign",
                    "E",
                    "T",
                    "Phi",
                ]
            )
            .sort(["symbol", "pure_date", "__order_txt"])
            .collect()
        )
        if one_df.height > 0:
            candidate_frames.append(_assign_intraday_ordinals(one_df))

    if not candidate_frames:
        return pl.DataFrame(
            schema={
                "symbol": pl.Utf8,
                "pure_date": pl.Utf8,
                "__order_txt": pl.Utf8,
                "__singularity": pl.Float64,
                "__sv_sign": pl.Int8,
                "E": pl.Float64,
                "T": pl.Float64,
                "Phi": pl.Float64,
                "__ord": pl.Int32,
            }
        )
    return pl.concat(candidate_frames, how="vertical_relaxed").sort(["symbol", "pure_date", "__order_txt"])


def _compress_same_sign_peaks_impl(
    day_ids: np.ndarray,
    ordinals: np.ndarray,
    signs: np.ndarray,
    magnitudes: np.ndarray,
    min_gap: int,
) -> np.ndarray:
    n = len(day_ids)
    keep = np.zeros(n, dtype=np.bool_)
    if n <= 0:
        return keep
    group_start = 0
    while group_start < n:
        curr_day = day_ids[group_start]
        curr_sign = signs[group_start]
        group_end = group_start + 1
        while group_end < n and day_ids[group_end] == curr_day and signs[group_end] == curr_sign:
            group_end += 1

        keep_idx = group_start
        keep_ord = ordinals[group_start]
        keep_mag = magnitudes[group_start]
        for idx in range(group_start + 1, group_end):
            if (ordinals[idx] - keep_ord) < min_gap:
                if magnitudes[idx] > keep_mag:
                    keep_idx = idx
                    keep_ord = ordinals[idx]
                    keep_mag = magnitudes[idx]
            else:
                keep[keep_idx] = True
                keep_idx = idx
                keep_ord = ordinals[idx]
                keep_mag = magnitudes[idx]
        keep[keep_idx] = True
        group_start = group_end
    return keep


if njit is not None:
    compress_same_sign_peaks = njit(cache=True)(_compress_same_sign_peaks_impl)
else:  # pragma: no cover - runtime fallback for nodes without numba
    compress_same_sign_peaks = _compress_same_sign_peaks_impl


def _pulse_compress_and_aggregate_daily(candidates: pl.DataFrame, pulse_min_gap: int) -> pl.DataFrame:
    if candidates.height <= 0:
        return pl.DataFrame(
            schema={
                "symbol": pl.Utf8,
                "pure_date": pl.Utf8,
                "F_epi": pl.Float64,
                "A_epi": pl.Float64,
                "F_topo": pl.Float64,
                "A_topo": pl.Float64,
                "F_phase": pl.Float64,
                "A_phase": pl.Float64,
                "pulse_count": pl.Int64,
                "pulse_concentration": pl.Float64,
            }
        )

    work = candidates.sort(["symbol", "pure_date", "__sv_sign", "__ord"])
    day_ids = _factorize_day_ids(work["symbol"].to_list(), work["pure_date"].to_list())
    ordinals = work["__ord"].to_numpy()
    signs = work["__sv_sign"].to_numpy()
    magnitudes = work["__singularity"].abs().to_numpy()
    keep_mask = compress_same_sign_peaks(
        day_ids=day_ids,
        ordinals=ordinals,
        signs=signs,
        magnitudes=magnitudes,
        min_gap=int(pulse_min_gap),
    )
    kept = work.filter(pl.Series("__keep", keep_mask, dtype=pl.Boolean))
    sign_phi = pl.when(pl.col("Phi") > 0.0).then(pl.lit(1.0)).when(pl.col("Phi") < 0.0).then(pl.lit(-1.0)).otherwise(pl.lit(0.0))
    return (
        kept.group_by(["symbol", "pure_date"])
        .agg(
            [
                (pl.col("E") * sign_phi).sum().alias("F_epi"),
                pl.col("E").sum().alias("A_epi"),
                (pl.col("T") * sign_phi).sum().alias("F_topo"),
                pl.col("T").sum().alias("A_topo"),
                pl.col("Phi").sum().alias("F_phase"),
                pl.col("Phi").abs().sum().alias("A_phase"),
                pl.len().alias("pulse_count"),
                (
                    pl.col("__singularity").abs().max() / (pl.col("__singularity").abs().sum() + float(DEFAULT_EPS))
                ).alias("pulse_concentration"),
            ]
        )
        .sort(["symbol", "pure_date"])
    )


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

    required_defaults: dict[str, float | int] = {
        "F_force": 0.0,
        "A_action": 0.0,
        "N_events": 0,
        "day_epi_integral": 0.0,
        "day_topo_integral": 0.0,
        "F_epi": 0.0,
        "A_epi": 0.0,
        "F_topo": 0.0,
        "A_topo": 0.0,
        "F_phase": 0.0,
        "A_phase": 0.0,
        "pulse_count": 0,
        "pulse_concentration": 0.0,
    }
    for col, default in required_defaults.items():
        if col not in daily_events.columns:
            daily_events = daily_events.with_columns(pl.lit(default).alias(col))

    df = (
        daily_spine.join(daily_events, on=["symbol", "pure_date"], how="left")
        .with_columns(
            [
                pl.col("F_force").fill_null(0.0).fill_nan(0.0),
                pl.col("A_action").fill_null(0.0).fill_nan(0.0),
                pl.col("N_events").fill_null(0).cast(pl.Int64, strict=False),
                pl.col("day_epi_integral").fill_null(0.0).fill_nan(0.0),
                pl.col("day_topo_integral").fill_null(0.0).fill_nan(0.0),
                pl.col("F_epi").fill_null(0.0).fill_nan(0.0),
                pl.col("A_epi").fill_null(0.0).fill_nan(0.0),
                pl.col("F_topo").fill_null(0.0).fill_nan(0.0),
                pl.col("A_topo").fill_null(0.0).fill_nan(0.0),
                pl.col("F_phase").fill_null(0.0).fill_nan(0.0),
                pl.col("A_phase").fill_null(0.0).fill_nan(0.0),
                pl.col("pulse_count").fill_null(0).cast(pl.Int64, strict=False),
                pl.col("pulse_concentration").fill_null(0.0).fill_nan(0.0),
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
                pl.col("F_epi")
                .ewm_mean(alpha=alpha, adjust=False, ignore_nulls=False)
                .over("symbol")
                .alias(f"S_epi_{tau}d"),
                pl.col("A_epi")
                .ewm_mean(alpha=alpha, adjust=False, ignore_nulls=False)
                .over("symbol")
                .alias(f"V_epi_{tau}d"),
                pl.col("F_topo")
                .ewm_mean(alpha=alpha, adjust=False, ignore_nulls=False)
                .over("symbol")
                .alias(f"S_topo_{tau}d"),
                pl.col("A_topo")
                .ewm_mean(alpha=alpha, adjust=False, ignore_nulls=False)
                .over("symbol")
                .alias(f"V_topo_{tau}d"),
                pl.col("F_phase")
                .ewm_mean(alpha=alpha, adjust=False, ignore_nulls=False)
                .over("symbol")
                .alias(f"S_phase_{tau}d"),
                pl.col("A_phase")
                .ewm_mean(alpha=alpha, adjust=False, ignore_nulls=False)
                .over("symbol")
                .alias(f"V_phase_{tau}d"),
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
        omega_exprs.extend(
            [
                (pl.col(f"S_epi_{tau}d").abs() / (pl.col(f"V_epi_{tau}d") + float(eps))).alias(f"OmegaE_{tau}d"),
                (pl.col(f"S_topo_{tau}d").abs() / (pl.col(f"V_topo_{tau}d") + float(eps))).alias(f"OmegaT_{tau}d"),
                (pl.col(f"S_phase_{tau}d").abs() / (pl.col(f"V_phase_{tau}d") + float(eps))).alias(f"OmegaPhase_{tau}d"),
                pl.min_horizontal(
                    pl.col(f"S_epi_{tau}d").abs() / (pl.col(f"V_epi_{tau}d") + float(eps)),
                    pl.col(f"S_topo_{tau}d").abs() / (pl.col(f"V_topo_{tau}d") + float(eps)),
                    pl.col(f"S_phase_{tau}d").abs() / (pl.col(f"V_phase_{tau}d") + float(eps)),
                ).alias(f"OmegaStar_{tau}d"),
            ]
        )
        psi_exprs.append((pl.col(f"S_{tau}d") * pl.col(f"Omega_{tau}d")).alias(f"Psi_{tau}d"))
        psi_exprs.extend(
            [
                (pl.col(f"S_epi_{tau}d") * pl.col(f"OmegaE_{tau}d")).alias(f"PsiE_{tau}d"),
                (pl.col(f"S_topo_{tau}d") * pl.col(f"OmegaT_{tau}d")).alias(f"PsiT_{tau}d"),
                (
                    pl.when(pl.col(f"S_phase_{tau}d") > 0.0)
                    .then(pl.lit(1.0))
                    .when(pl.col(f"S_phase_{tau}d") < 0.0)
                    .then(pl.lit(-1.0))
                    .otherwise(pl.lit(0.0))
                    * (pl.col(f"S_epi_{tau}d") * pl.col(f"S_topo_{tau}d")).abs().sqrt()
                    * pl.col(f"OmegaStar_{tau}d")
                ).alias(f"PsiStar_{tau}d"),
            ]
        )

    df = df.with_columns(omega_exprs + raw_label_exprs)
    df = df.with_columns(psi_exprs)

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
    pulse_mode: str,
    pulse_min_gap: int,
    pulse_floor: float,
    require_is_signal: bool,
    require_is_physics_valid: bool,
) -> dict:
    started = time.monotonic()
    l1_files = _expand_patterns(l1_patterns, years=years)
    l2_files = _expand_patterns(l2_patterns, years=years)
    if not l1_files:
        raise FileNotFoundError("no L1 daily-spine source files matched the supplied patterns")
    if not l2_files:
        raise FileNotFoundError("no L2 pulse-source files matched the supplied patterns")
    if str(pulse_mode).strip() != "sign_nms":
        raise ValueError(f"unsupported pulse mode: {pulse_mode}")

    _log(
        f"matched L1 files={len(l1_files)} L2 files={len(l2_files)} horizons={list(horizons)} pulse_mode={pulse_mode} pulse_min_gap={pulse_min_gap}"
    )
    _log("phase 1/4 collecting daily spine from L1")
    daily_spine = _collect_daily_spine_from_l1(l1_files)
    _assert_unique_symbol_date(daily_spine, frame_name="daily_spine")
    _log(f"phase 1/4 done rows={daily_spine.height} symbols={daily_spine.select(pl.col('symbol').n_unique()).item() if daily_spine.height > 0 else 0}")

    _log("phase 2/4 collecting and compressing L2 intraday pulses")
    legacy_daily = _collect_legacy_daily_events_from_l2(l2_files)
    candidates = _collect_intraday_candidates_from_l2(
        l2_files=l2_files,
        pulse_floor=float(pulse_floor),
        require_is_signal=bool(require_is_signal),
        require_is_physics_valid=bool(require_is_physics_valid),
        eps=float(eps),
    )
    compressed_daily = _pulse_compress_and_aggregate_daily(candidates=candidates, pulse_min_gap=int(pulse_min_gap))
    daily_events = legacy_daily.join(compressed_daily, on=["symbol", "pure_date"], how="left").sort(["symbol", "pure_date"])
    _assert_unique_symbol_date(daily_events, frame_name="daily_events")
    total_events = int(daily_events["N_events"].sum()) if daily_events.height > 0 and "N_events" in daily_events.columns else 0
    if total_events <= 0:
        raise ValueError("daily_events contains zero usable pulse mass; refusing to forge a structurally dead campaign matrix")
    kept_pulses = int(compressed_daily["pulse_count"].sum()) if compressed_daily.height > 0 and "pulse_count" in compressed_daily.columns else 0
    raw_candidates = int(candidates.height)
    _log(
        f"phase 2/4 done rows={daily_events.height} total_events={total_events} raw_candidates={raw_candidates} kept_pulses={kept_pulses}"
    )

    _log("phase 3/4 building campaign-state frame")
    campaign_df = build_campaign_state_frame(daily_spine=daily_spine, daily_events=daily_events, horizons=horizons, eps=eps)
    _log(f"phase 3/4 done rows={campaign_df.height} cols={len(campaign_df.columns)}")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    _log(f"phase 4/4 writing parquet tmp={tmp_path.name}")
    campaign_df.write_parquet(tmp_path, compression="zstd")
    tmp_path.replace(out_path)

    meta = _build_meta(out_path=out_path, l1_files=l1_files, l2_files=l2_files, df=campaign_df, horizons=horizons)
    meta_path = out_path.with_suffix(out_path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    _log(f"complete seconds={time.monotonic() - started:.1f} output={out_path}")
    return meta


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Forge V653 campaign-state matrix from L1 daily spine plus Stage2 pulse source.")
    ap.add_argument("--l1-input-pattern", action="append", required=True, help="Glob pattern(s) for raw L1 daily-spine source parquet files.")
    ap.add_argument("--l2-input-pattern", action="append", required=True, help="Glob pattern(s) for Stage2 pulse-source parquet files.")
    ap.add_argument("--output-path", required=True, help="Output campaign-state parquet path.")
    ap.add_argument("--years", default="", help="Comma-separated years to keep, for example 2023,2024.")
    ap.add_argument("--horizons", default="5,10,20", help="Comma-separated day horizons. Default: 5,10,20.")
    ap.add_argument("--eps", type=float, default=DEFAULT_EPS, help="Small epsilon used in Omega calculation.")
    ap.add_argument("--pulse-mode", default="sign_nms", help="Pulse compression mode. Default: sign_nms.")
    ap.add_argument("--pulse-min-gap", type=int, default=DEFAULT_PULSE_MIN_GAP, help="Same-sign pulse suppression gap in intraday bars.")
    ap.add_argument("--pulse-floor", type=float, default=DEFAULT_PULSE_FLOOR, help="Absolute singularity floor used before pulse compression.")
    ap.add_argument("--require-is-signal", type=int, default=1, help="Require is_signal == 1 before pulse compression. Default: 1.")
    ap.add_argument("--require-is-physics-valid", type=int, default=1, help="Require is_physics_valid == 1 before pulse compression. Default: 1.")
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
        pulse_mode=str(args.pulse_mode),
        pulse_min_gap=int(args.pulse_min_gap),
        pulse_floor=float(args.pulse_floor),
        require_is_signal=bool(int(args.require_is_signal)),
        require_is_physics_valid=bool(int(args.require_is_physics_valid)),
    )
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
