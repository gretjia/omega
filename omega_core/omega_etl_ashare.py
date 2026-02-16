"""
A-share ETL anchor expressions for v6 architecture.

These helpers are intentionally small and pure-expression based so they can
be reused inside lazy Polars pipelines.
"""

from __future__ import annotations

import polars as pl

from config_v6 import L2PipelineConfigV6


def _ashare_causal_time_fraction(time_col: str, cfg: L2PipelineConfigV6) -> pl.Expr:
    """
    Fold lunch break (11:30-13:00) so elapsed causal time does not advance.
    `time_col` must already be normalized to ms-of-day.
    """
    s = cfg.session
    t = pl.col(time_col)
    morning_len = s.morning_end_ms - s.morning_start_ms
    elapsed = (
        pl.when(t <= s.morning_end_ms)
        .then(t - s.morning_start_ms)
        .when(t >= s.afternoon_start_ms)
        .then((t - s.afternoon_start_ms) + morning_len)
        .otherwise(morning_len)
    ).clip(lower_bound=0)
    return (elapsed / s.total_duration_ms).clip(lower_bound=0.05, upper_bound=1.0)


def _ashare_singularity_mask(cfg: L2PipelineConfigV6) -> pl.Expr:
    """
    Mask limit-up/down singularities where top-of-book depth collapses.
    """
    eps = cfg.micro.limit_singularity_eps
    is_singularity = (pl.col("bid_v1") <= eps) | (pl.col("ask_v1") <= eps)
    return (~is_singularity).alias("is_physics_valid")
