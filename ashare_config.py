"""
A-share configuration anchors for microstructure-specific runtime wiring.

These dataclasses provide a stable, non-versioned bridge to the runtime
`config.L2PipelineConfig`.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Sequence

from config import (
    AShareMicrostructureConfig as RuntimeAShareMicrostructureConfig,
    AShareSessionConfig as RuntimeAShareSessionConfig,
    L2PipelineConfig,
)


@dataclass(frozen=True)
class AShareSessionConfig:
    morning_start_ms: int = 34_200_000   # 09:30:00
    morning_end_ms: int = 41_400_000     # 11:30:00
    afternoon_start_ms: int = 46_800_000 # 13:00:00
    afternoon_end_ms: int = 54_000_000   # 15:00:00

    @property
    def total_duration_ms(self) -> float:
        return float(
            (self.morning_end_ms - self.morning_start_ms)
            + (self.afternoon_end_ms - self.afternoon_start_ms)
        )


@dataclass(frozen=True)
class AShareMicrostructureConfig:
    limit_singularity_eps: float = 1e-5
    t_plus_1_horizon_days: int = 1


@dataclass(frozen=True)
class ASharePipelineConfig:
    session: AShareSessionConfig = field(default_factory=AShareSessionConfig)
    micro: AShareMicrostructureConfig = field(default_factory=AShareMicrostructureConfig)
    base: L2PipelineConfig = field(default_factory=L2PipelineConfig)

    def to_runtime_config(self) -> L2PipelineConfig:
        runtime_session = RuntimeAShareSessionConfig(
            morning_start_ms=self.session.morning_start_ms,
            morning_end_ms=self.session.morning_end_ms,
            afternoon_start_ms=self.session.afternoon_start_ms,
            afternoon_end_ms=self.session.afternoon_end_ms,
        )
        runtime_micro = RuntimeAShareMicrostructureConfig(
            limit_singularity_eps=self.micro.limit_singularity_eps,
            t_plus_1_horizon_days=self.micro.t_plus_1_horizon_days,
        )
        return replace(self.base, ashare_session=runtime_session, micro=runtime_micro)


def canonical_feature_cols(cfg: L2PipelineConfig | None = None) -> list[str]:
    """
    Canonical A-share feature list for tree models and swarm optimizers.
    Keep this centralized so scripts do not hard-code column names.
    """
    runtime_cfg = cfg or L2PipelineConfig()
    topo_race_cols: Sequence[str] = tuple(getattr(runtime_cfg.train, "topology_race_features", ()))
    cols = [
        "sigma_eff",
        "net_ofi",
        "depth_eff",
        "epiplexity",
        "srl_resid",
        "topo_area",
        "topo_energy",
        *topo_race_cols,
        "price_change",
        "bar_duration_ms",
        "adaptive_y",
        "epi_x_srl_resid",
        "epi_x_topo_area",
        "epi_x_net_ofi",
    ]
    return list(dict.fromkeys(cols))


# Architectural anchor used by training / backtest / matrix scripts.
FEATURE_COLS = tuple(canonical_feature_cols())
