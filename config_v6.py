"""
v6-specific configuration anchors for A-share microstructure.

These dataclasses mirror the architecture constraints in audit/v6.md and
provide a conversion bridge to the runtime `config.L2PipelineConfig`.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

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
class L2PipelineConfigV6:
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
