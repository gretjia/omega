#!/usr/bin/env python3
"""
A/B Benchmark: Old vs New Stage2 implementations.
Measures wall-clock time for:
  1. ETL temporal rolling (old join vs new rolling_mean_by)
  2. Kernel MDL arena (old concat_list vs new when/then)
  3. Full pipeline (build_l2 + apply_recursive_physics)
"""
import os, sys, time
import numpy as np
import polars as pl

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from config import load_l2_pipeline_config, L2PipelineConfig
import math

CFG = load_l2_pipeline_config()

# ============================================================
# Synthetic L1 data — 3 symbols × 5000 ticks = 15,000 rows
# ============================================================
def make_l1(n_per_sym=5000, n_symbols=3):
    np.random.seed(42)
    symbols = [f"SYM{i:04d}" for i in range(n_symbols)]
    base_time = 34_200_000
    rows = []
    for sym in symbols:
        px = 10.0 + np.random.randn() * 2
        for i in range(n_per_sym):
            t = base_time + i * 500  # 500ms apart
            px += np.random.randn() * 0.02
            vol = max(1, int(np.random.exponential(500)))
            rows.append({
                "symbol": sym, "date": "20250101", "time": int(t),
                "__time_ms": int(t), "price": px, "vol": float(vol),
                "turnover": px * vol, "vol_tick": float(vol),
                "bid_p1": px - 0.01, "ask_p1": px + 0.01,
                "bid_v1": float(max(1, int(np.random.exponential(200)))),
                "ask_v1": float(max(1, int(np.random.exponential(200)))),
                "bs_flag": 1,
            })
    df = pl.DataFrame(rows).cast({
        "price": pl.Float64, "vol": pl.Float64, "turnover": pl.Float64,
        "vol_tick": pl.Float64, "bid_p1": pl.Float64, "ask_p1": pl.Float64,
        "bid_v1": pl.Float64, "ask_v1": pl.Float64, "__time_ms": pl.Int64,
    })
    return df

# ============================================================
# OLD ETL rolling implementation (agg + join)
# ============================================================
def old_rolling(lf, group_col):
    from omega_core.omega_etl import _microprice_expr, _depth_expr, _ofi_expr, _lob_flux_expr, _volume_tick_expr
    lf = lf.with_columns([_microprice_expr(CFG), _depth_expr(CFG)])
    lf = lf.with_columns(_ofi_expr(CFG))
    lf = lf.with_columns(_lob_flux_expr(group_col))
    lf = lf.with_columns(pl.from_epoch(pl.col("__time_ms"), time_unit="ms").alias("__time_dt"))

    if group_col:
        lf = lf.sort([group_col, "__time_dt"])
        rolled = lf.rolling(index_column="__time_dt", period="3s", closed="left", group_by=group_col).agg([
            pl.col("v_ofi").mean().alias("v_ofi_mean"),
            pl.col("depth").mean().alias("depth_mean")
        ])
        lf = lf.join(rolled, on=[group_col, "__time_dt"], how="left")
    else:
        lf = lf.sort(["__time_dt"])
        rolled = lf.rolling(index_column="__time_dt", period="3s", closed="left").agg([
            pl.col("v_ofi").mean().alias("v_ofi_mean"),
            pl.col("depth").mean().alias("depth_mean")
        ])
        lf = lf.join(rolled, on="__time_dt", how="left")
    lf = lf.with_columns([
        pl.col("v_ofi_mean").alias("v_ofi"),
        pl.col("depth_mean").alias("depth")
    ]).drop(["v_ofi_mean", "depth_mean"])
    return lf.collect()

# ============================================================
# NEW ETL rolling implementation (inline rolling_mean_by)
# ============================================================
def new_rolling(lf, group_col):
    from omega_core.omega_etl import _microprice_expr, _depth_expr, _ofi_expr, _lob_flux_expr
    lf = lf.with_columns([_microprice_expr(CFG), _depth_expr(CFG)])
    lf = lf.with_columns(_ofi_expr(CFG))
    lf = lf.with_columns(_lob_flux_expr(group_col))
    lf = lf.with_columns(pl.from_epoch(pl.col("__time_ms"), time_unit="ms").alias("__time_dt"))

    if group_col:
        lf = lf.sort([group_col, "__time_dt"])
        lf = lf.with_columns([
            pl.col("v_ofi").rolling_mean_by("__time_dt", window_size="3s", closed="left").over(group_col).alias("v_ofi"),
            pl.col("depth").rolling_mean_by("__time_dt", window_size="3s", closed="left").over(group_col).alias("depth"),
        ])
    else:
        lf = lf.sort(["__time_dt"])
        lf = lf.with_columns([
            pl.col("v_ofi").rolling_mean_by("__time_dt", window_size="3s", closed="left").alias("v_ofi"),
            pl.col("depth").rolling_mean_by("__time_dt", window_size="3s", closed="left").alias("depth"),
        ])
    return lf.collect()

# ============================================================
# OLD kernel argmax (concat_list)
# ============================================================
def old_argmax(df):
    window_len = 10
    group_expr = pl.col("symbol")
    bits_linear = pl.col("epiplexity").forward_fill()
    var_srl_resid = pl.col("srl_resid").rolling_var(window_size=window_len).over(group_expr).forward_fill()
    var_price_change = pl.col("price_change").rolling_var(window_size=window_len).over(group_expr).forward_fill()
    r2_srl = (1.0 - (var_srl_resid / (var_price_change + 1e-12))).clip(0.0, 0.9999)
    bits_srl = (-(window_len / 2.0) * (1.0 - r2_srl).log() - 0.5 * math.log(window_len)).clip(0.0, 999.0)
    compactness = (4.0 * math.pi * pl.col("topo_area").abs()) / (pl.col("topo_energy")**2 + 1e-12)
    bits_topo = (compactness * math.log(window_len)).forward_fill().clip(0.0, 999.0)
    df = df.with_columns([bits_linear.alias("bits_linear"), bits_srl.alias("bits_srl"), bits_topo.alias("bits_topology")])
    dominant_probe = pl.concat_list(["bits_linear", "bits_srl", "bits_topology"]).list.arg_max() + 1
    return df.with_columns(dominant_probe.alias("dominant_probe"))

# ============================================================
# NEW kernel argmax (when/then)
# ============================================================
def new_argmax(df):
    window_len = 10
    group_expr = pl.col("symbol")
    bits_linear = pl.col("epiplexity").forward_fill()
    var_srl_resid = pl.col("srl_resid").rolling_var(window_size=window_len).over(group_expr).forward_fill()
    var_price_change = pl.col("price_change").rolling_var(window_size=window_len).over(group_expr).forward_fill()
    r2_srl = (1.0 - (var_srl_resid / (var_price_change + 1e-12))).clip(0.0, 0.9999)
    bits_srl = (-(window_len / 2.0) * (1.0 - r2_srl).log() - 0.5 * math.log(window_len)).clip(0.0, 999.0)
    compactness = (4.0 * math.pi * pl.col("topo_area").abs()) / (pl.col("topo_energy")**2 + 1e-12)
    bits_topo = (compactness * math.log(window_len)).forward_fill().clip(0.0, 999.0)
    df = df.with_columns([bits_linear.alias("bits_linear"), bits_srl.alias("bits_srl"), bits_topo.alias("bits_topology")])
    dominant_probe = (
        pl.when((pl.col("bits_srl") > pl.col("bits_linear")) & (pl.col("bits_srl") >= pl.col("bits_topology"))).then(pl.lit(2))
        .when((pl.col("bits_topology") > pl.col("bits_linear")) & (pl.col("bits_topology") > pl.col("bits_srl"))).then(pl.lit(3))
        .otherwise(pl.lit(1))
    )
    return df.with_columns(dominant_probe.alias("dominant_probe"))

# ============================================================
# Full pipeline benchmark
# ============================================================
def bench_full_pipeline(l1_df, use_new=True):
    from omega_core.omega_etl import build_l2_features_from_l1
    from omega_core.kernel import apply_recursive_physics
    l2 = build_l2_features_from_l1(l1_df.lazy(), CFG)
    result = apply_recursive_physics(l2, CFG)
    return result

# ============================================================
def timeit(fn, *args, warmup=1, repeats=5, **kwargs):
    for _ in range(warmup):
        fn(*args, **kwargs)
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        times.append(time.perf_counter() - t0)
    return np.median(times), np.min(times), np.max(times)

if __name__ == "__main__":
    print("=" * 60)
    print("Stage 2 A/B Benchmark (synthetic 15,000 rows)")
    print("=" * 60)

    l1 = make_l1(n_per_sym=5000, n_symbols=3)
    print(f"L1 shape: {l1.shape}")

    # --- ETL Rolling ---
    print("\n--- ETL Temporal Rolling ---")
    t_old = timeit(old_rolling, l1.lazy(), "symbol")
    t_new = timeit(new_rolling, l1.lazy(), "symbol")
    speedup_rolling = t_old[0] / t_new[0]
    print(f"  OLD (agg+join):      median={t_old[0]*1000:.1f}ms  range=[{t_old[1]*1000:.1f}, {t_old[2]*1000:.1f}]ms")
    print(f"  NEW (rolling_mean_by): median={t_new[0]*1000:.1f}ms  range=[{t_new[1]*1000:.1f}, {t_new[2]*1000:.1f}]ms")
    print(f"  Speedup: {speedup_rolling:.2f}x")

    # --- Kernel Argmax ---
    print("\n--- Kernel MDL Argmax ---")
    # Need physics output for argmax benchmark
    from omega_core.omega_etl import build_l2_features_from_l1
    from omega_core.kernel import apply_recursive_physics
    l2 = build_l2_features_from_l1(l1.lazy(), CFG)
    phys = apply_recursive_physics(l2, CFG)
    # Remove existing bits/dominant columns for clean benchmark
    drop_cols = [c for c in phys.columns if c.startswith("bits_") or c == "dominant_probe"]
    phys_clean = phys.drop(drop_cols)

    t_old_a = timeit(old_argmax, phys_clean)
    t_new_a = timeit(new_argmax, phys_clean)
    speedup_argmax = t_old_a[0] / t_new_a[0]
    print(f"  OLD (concat_list): median={t_old_a[0]*1000:.1f}ms  range=[{t_old_a[1]*1000:.1f}, {t_old_a[2]*1000:.1f}]ms")
    print(f"  NEW (when/then):   median={t_new_a[0]*1000:.1f}ms  range=[{t_new_a[1]*1000:.1f}, {t_new_a[2]*1000:.1f}]ms")
    print(f"  Speedup: {speedup_argmax:.2f}x")

    # --- Full Pipeline ---
    print("\n--- Full Pipeline (ETL + Physics + MDL Arena) ---")
    t_full = timeit(bench_full_pipeline, l1, repeats=3)
    print(f"  NEW full pipeline: median={t_full[0]*1000:.1f}ms  range=[{t_full[1]*1000:.1f}, {t_full[2]*1000:.1f}]ms")

    print("\n" + "=" * 60)
    print(f"SUMMARY: Rolling={speedup_rolling:.2f}x  Argmax={speedup_argmax:.2f}x")
    print("=" * 60)
