"""
config.py

OMEGA Quant System - centralized configuration.

Design goal:
- omega_v3_core/kernel.py and omega_v3_core/omega_math_core.py must contain
  *only* mathematical logic and formulas.
- All tunable parameters (thresholds, lookbacks, constants, scaling factors) live here.

You can:
- Edit the dataclass defaults directly; or
- Build configs at runtime from your own config loader (YAML/JSON/env).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Iterable, List, Optional, Sequence, Tuple
import json
import os


# =========================
# Core-kernel configs
# =========================

@dataclass(frozen=True)
class VolumeClockConfig:
    """
    "Physical time" -> "Volume time" (等量K线 / volume bars) configuration.
    """
    volume_per_bar: float = 50_000.0   # shares (or contract units); tune for A-share liquidity regimes
    min_ticks_per_bar: int = 5         # guardrail against ultra-sparse intervals
    max_bars: int = 2_048              # cap for memory / compute safety


@dataclass(frozen=True)
class EmbeddingConfig:
    """
    Takens' delay embedding configuration.
    """
    delay: int = 3                     # tau
    dimension: int = 8                 # d
    # If multivariate features are used, final embedding dimension becomes dimension * n_features.


@dataclass(frozen=True)
class TDAConfig:
    """
    Persistent-topology proxy configuration (graph/VR-1-skeleton + triangle filling approximation).
    """
    # Filtration (epsilon) grid used to summarize topology across scales
    eps_min: float = 0.25
    eps_max: float = 3.00
    n_eps: int = 16

    # Adaptive epsilon for "decision-time" topology (recursive feedback)
    epsilon_base: float = 1.00
    epsilon_min: float = 0.25
    epsilon_max: float = 3.00

    # When epiplexity rises, reduce epsilon (higher resolution).
    # epsilon = clamp(epsilon_base * exp(-epsilon_shrink_k * s_norm), [epsilon_min, epsilon_max])
    epsilon_shrink_k: float = 0.75

    # Point-cloud pre-normalization
    standardize_point_cloud: bool = True
    # Numerical floor for standardization (std deviation)
    standardize_eps: float = 1e-12

    # Optional triangle-based loop filling correction (0.0 means disabled)
    triangle_penalty: float = 0.0

    # Null-hypothesis test (Topo_SNR) settings
    topo_snr_metric: str = "beta1_auc"   # {"beta1_auc", "beta1_max"}
    topo_snr_n_shuffle: int = 100
    topo_snr_seed: Optional[int] = 1337
    topo_snr_std_floor: float = 1e-12
    topo_snr_min_shuffles: int = 10


@dataclass(frozen=True)
class CompressionConfig:
    """
    Compression proxy configuration used for time-bounded information decomposition.

    Notes:
    - We use compression length as a computable proxy for description length.
    - Quantization controls the implicit "coding precision".
    """
    codec: str = "gzip"                # currently only gzip is used (zlib wrapper)
    level_data: int = 6
    level_model: int = 6

    # Quantization step sizes for converting float arrays -> integers -> bytes
    residual_quant_step: float = 1e-4
    raw_quant_step: float = 1e-4
    coef_quant_step: float = 1e-6


@dataclass(frozen=True)
class MDLConfig:
    """
    Time-bounded MDL proxy configuration.

    We approximate:
      MDL_T(x) = min_{model in M_T} [ L_T(model) + L_T(x | model) ]
      S_T(x)   = L_T(model*)          (Epiplexity)
      H_T(x)   = L_T(x | model*)      (Time-bounded entropy)

    Model family in this first version: AR(p) with ridge stabilization.
    """
    max_ar_order: int = 12
    candidate_orders: Optional[Sequence[int]] = None  # if None: range(0, max_ar_order+1)
    ridge_alpha: float = 1e-6

    # Choose data cost estimator
    data_cost_method: str = "gzip"     # {"gzip", "gaussian_nll"}

    # Choose model cost estimator
    model_cost_method: str = "bic"     # {"bic", "gzip"}

    # Residual scaling to avoid double-penalizing volatility (which SRL handles)
    residual_scale_method: str = "std" # {"none", "std", "mad"}
    residual_scale_floor: float = 1e-6

    compression: CompressionConfig = field(default_factory=CompressionConfig)


@dataclass(frozen=True)
class SRLConfig:
    """
    Square-Root Law (price impact) configuration.
    """
    # Impact model: I = Y * sigma * (|Q|/V)^exponent
    impact_Y: float = 1.0
    exponent: float = 0.5

    # How to estimate sigma and V in intraday/volume-clock context
    sigma_floor: float = 1e-6
    price_floor: float = 1e-12
    V_floor: float = 1.0

    # Convert returns -> "impact" (absolute log-return by default)
    impact_mode: str = "abs_log_return"  # {"abs_log_return", "raw_return"}

    # Order-flow proxy from tick/bars
    ofi_mode: str = "tick_rule"  # {"tick_rule", "signed_return"}

    # For iceberg detection: require predicted impact to be meaningful
    min_predicted_impact: float = 1e-5


@dataclass(frozen=True)
class DecisionConfig:
    """
    Trading regime classification thresholds and mapping to actions.
    """
    # Regime gating (bits per sample)
    epiplexity_high: float = 0.25
    epiplexity_low: float = 0.05

    entropy_high: float = 0.90
    entropy_low: float = 0.40

    # TDA structural triggers
    beta1_high: float = 1.5
    beta0_low: float = 1.5

    # Iceberg / "physics violation" triggers
    iceberg_ratio_low: float = 0.50   # realized / predicted
    iceberg_ratio_high: float = 1.50

    # Directionality gate
    min_ofi_abs: float = 0.0

    # TDA directionality fallback
    use_signed_area_direction: bool = True

    # Vector alignment gate (direction consistency)
    vector_align_window: int = 8
    vector_align_min: float = 0.8
    vector_align_norm_floor: float = 1e-12
    vector_align_nan_fallback: float = 0.0

    # Signed-area direction threshold
    signed_area_min_abs: float = 1e-9


@dataclass(frozen=True)
class RiskConfig:
    """
    Risk / position sizing recursion.
    """
    base_position: float = 1.0  # position units (strategy-specific)
    max_position: float = 3.0

    # Entropy-based decay: pos = base * exp(-entropy_k * H_norm)
    entropy_k: float = 1.0

    # Optional SRL-based decay: increase risk when "iceberg suppressed" (ratio small) or decrease otherwise
    iceberg_k: float = 0.25


@dataclass(frozen=True)
class BoundaryConfig:
    """
    Market boundary (limit up/down) protection configuration.
    """
    enabled: bool = True
    
    # Detection: window size to check for "stalled" price action
    stall_window_bars: int = 5
    # Threshold for "stalled" returns (fraction of bars with nearly zero return)
    stall_zero_return_frac: float = 0.8
    # Threshold for "near extrema" (current price vs window max/min)
    # If price >= max * (1 - boundary_margin), consider upper boundary.
    boundary_margin: float = 0.002

    # Actions
    disable_srl: bool = True       # If boundary detected, force SRL to NaN (avoid physics violation false positive)
    disable_trading: bool = True   # If boundary detected, force signal=0


@dataclass(frozen=True)
class KernelConfig:
    """
    Full kernel configuration bundle.
    """
    volume_clock: VolumeClockConfig = field(default_factory=VolumeClockConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    tda: TDAConfig = field(default_factory=TDAConfig)
    mdl: MDLConfig = field(default_factory=MDLConfig)
    srl: SRLConfig = field(default_factory=SRLConfig)
    boundary: BoundaryConfig = field(default_factory=BoundaryConfig)
    decision: DecisionConfig = field(default_factory=DecisionConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    # Minimum number of volume bars required to run kernel features
    min_bars: int = 3


# =========================
# Trainer configs (NO hard-coding inside trainer)
# =========================

@dataclass(frozen=True)
class CSVParseConfig:
    """
    CSV parsing and normalization.

    history_ticks_full has two known formats:
      (A) RQ standard: datetime, open/high/low/last, volume, total_turnover, a1-a5, b1-b5
      (B) simplified: time(ms), price, vol, ask1, bid1

    The adapter auto-detects format by column names, but these options define defaults.
    """
    # If simplified time is epoch milliseconds, unit="ms" works. If it's "ms of day", you'd need a date anchor.
    simplified_time_unit: str = "ms"     # passed to pandas.to_datetime(..., unit=...)
    simplified_time_is_epoch: bool = True

    # Volume semantics: auto detects monotonic cumulative, otherwise treat as per-tick delta.
    volume_mode: str = "auto"            # {"auto", "cumulative", "delta"}

    # Sorting / de-duplication
    sort_by_time: bool = True
    drop_duplicated_time: bool = True


@dataclass(frozen=True)
class DataSourceConfig:
    """
    A data source is a folder with CSV files.

    Two typical sources:
      - ./data/history_ticks_full : many slice CSVs (24,015) across 4000+ A-share stocks, high volatility and multi-day continuity.
      - ./data/history_ticks      : 156 selected high-vol stocks, full-year 2025, level-1 ticks.

    The trainer treats both as sources and can define a staged curriculum.
    """
    root_dir: str
    glob_pattern: str = "*.csv"
    recursive: bool = True

    # Sampling controls to keep compute bounded
    max_files: Optional[int] = None
    max_windows_per_file: Optional[int] = 512
    file_sampling_seed: int = 1337

    # If you want to bias training, you can assign a weight; the sampler can use it.
    source_weight: float = 1.0

    # Optional label: "slices" or "continuous" (only affects default sampling heuristics).
    kind: str = "slices"



@dataclass(frozen=True)
class SplitConfig:
    """
    Train/Val/Test splitting configuration.
    
    Default is file-level splitting (fast, robust for heterogeneous slices).
    If you want calendar splits, you can implement it in trainer.py using bar timestamps.
    """
    method: str = "time"  # {"file_fraction", "time"}
    
    # file_fraction split
    train_frac: float = 0.80
    val_frac: float = 0.10
    test_frac: float = 0.10
    split_seed: int = 2026
    
    # time split (strict separation)
    train_years: Sequence[int] = (2023, 2024)
    test_years: Sequence[int] = (2025,)
    # Optional month-level backtest additions (YYYYMM), e.g. (202601,)
    test_year_months: Sequence[int] = (202601,)
    val_years: Sequence[int] = () # If empty, val is random sample from train or specific slice

@dataclass(frozen=True)
class WindowSamplingConfig:
    """
    Windowing in volume-clock bars.
    """
    lookback_bars: int = 128
    stride_bars: int = 8

    # Label horizon (future bars)
    label_horizon_bars: int = 16

    # Skip tiny labels around 0 (avoid micro noise classification)
    label_return_threshold: float = 0.0

    # Whether to drop windows when bars are too few for embedding
    require_min_embedded_points: bool = True


@dataclass(frozen=True)
class CalibrationConfig:
    """
    Calibrate DecisionConfig thresholds from empirical feature distributions.

    We run a "Pass-0" scan on training sources, compute epiplexity_bps and entropy_bps,
    then set:
      epiplexity_low  = quantile(q_s_low)
      epiplexity_high = quantile(q_s_high)
      entropy_low     = quantile(q_h_low)
      entropy_high    = quantile(q_h_high)

    Using a reservoir sampler keeps memory bounded.
    """
    enabled: bool = True
    reservoir_size: int = 50_000
    max_windows_total: Optional[int] = 300_000

    q_s_low: float = 0.20
    q_s_high: float = 0.80
    q_h_low: float = 0.20
    q_h_high: float = 0.80


@dataclass(frozen=True)
class FeatureConfig:
    """
    Feature engineering knobs (still math-derived, but trainer may toggle).
    """
    include_raw_tda_curve_stats: bool = True
    include_srl: bool = True
    include_ofi: bool = True
    include_sigma_V: bool = True

    # Feature normalization
    standardize_features: bool = True
    # Fallback value for non-finite feature values
    nan_fallback: float = 0.0
    # Whether audit diagnostics are included in model features
    include_diagnostics_in_model: bool = False


@dataclass(frozen=True)
class AuditMetricsConfig:
    """
    Math-model audit metrics and Definition-of-Done thresholds.
    """
    # Definition of Done thresholds
    topo_snr_avg_min: float = 3.0
    epi_entropy_corr_max: float = 0.1
    vector_align_avg_min: float = 0.8

    # Correlation estimation controls
    corr_min_samples: int = 30
    corr_eps: float = 1e-12

    # Kurtosis estimation controls (SRL residual)
    kurtosis_min_samples: int = 30
    kurtosis_eps: float = 1e-12
    kurtosis_excess: bool = True
    kurtosis_excess_offset: float = 3.0


@dataclass(frozen=True)
class ModelConfig:
    """
    Model configuration.

    v6 default uses XGBoost for non-linear manifold learning.
    Legacy SGD remains available for compatibility.
    """
    model_type: str = "xgboost"  # {"xgboost", "sgd_logistic", "sgd_regression"}

    # SGD hyperparameters (sklearn-style)
    loss: str = "log_loss"
    penalty: str = "l2"
    alpha: float = 1e-4               # L2 regularization strength
    l1_ratio: float = 0.15            # only for elasticnet
    max_iter: int = 1                 # we control epochs ourselves
    tol: Optional[float] = None
    learning_rate: str = "optimal"
    eta0: float = 0.01
    power_t: float = 0.5
    average: bool = True              # Polyak averaging helps stability

    # Training loop
    epochs: int = 3
    batch_size: int = 512
    shuffle_within_file: bool = False

    # Probability to act (evaluation) margin
    decision_margin: float = 0.05

    # XGBoost (v6 default)
    xgb_objective: str = "binary:logistic"
    xgb_eval_metric: str = "logloss"
    xgb_max_depth: int = 6
    xgb_eta: float = 0.1
    xgb_subsample: float = 0.9
    xgb_colsample_bytree: float = 0.9
    xgb_num_boost_round: int = 60


@dataclass(frozen=True)
class BacktestConfig:
    """
    Lightweight evaluation config on windowed samples.
    """
    cost_weight: float = 1.0
    annualization_factor: float = 252.0  # for sharpe proxy, if you interpret a "day" as one unit

    # When computing PnL per window, you can clip extremes to stabilize stats.
    pnl_clip: Optional[float] = None


@dataclass(frozen=True)
class TrainingStageConfig:
    """
    Curriculum stage: train for some epochs on a set of sources.
    """
    name: str
    sources: Sequence[DataSourceConfig]
    epochs: int


@dataclass(frozen=True)
class TrainerConfig:
    """
    Full trainer configuration.
    """
    csv: CSVParseConfig = field(default_factory=CSVParseConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    window: WindowSamplingConfig = field(default_factory=WindowSamplingConfig)
    calibration: CalibrationConfig = field(default_factory=CalibrationConfig)
    feature: FeatureConfig = field(default_factory=FeatureConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    audit: AuditMetricsConfig = field(default_factory=AuditMetricsConfig)


# =========================
# Level-2 (v3) configs
# =========================

@dataclass(frozen=True)
class L2MappingConfig:
    """
    Column mappings for Level-2 quote CSVs (GB18030 headers).
    """
    col_symbol: str = "万得代码"
    col_exchange: str = "交易所代码"
    col_date: str = "自然日"
    col_time: str = "时间"
    col_price: str = "成交价"
    col_volume: str = "成交量"
    col_turnover: str = "成交额"
    col_bs_flag: str = "BS标志"

    ask_price_prefix: str = "申卖价"
    ask_volume_prefix: str = "申卖量"
    bid_price_prefix: str = "申买价"
    bid_volume_prefix: str = "申买量"
    book_levels: int = 10


@dataclass(frozen=True)
class L2SessionConfig:
    """
    Trading session filters in HHMMSSmmm integer format.
    """
    enable_session_filter: bool = True
    session_1_start: int = 93000000
    session_1_end: int = 113000000
    session_2_start: int = 130000000
    session_2_end: int = 150000000
    allow_auction: bool = False


@dataclass(frozen=True)
class L2IOConfig:
    """
    L2 input/output and encoding.
    """
    input_root: str = "./data/level2"
    output_root: str = "./data/level2_frames"
    input_format: str = "csv"       # {"csv", "parquet"}
    csv_encoding: str = "gb18030"
    seven_zip_exe: str = ""          # optional path override
    audit_report_path: str = "./audit/level2_v3_audit_report.md"


@dataclass(frozen=True)
class L2VolumeClockConfig:
    """
    Volume-clock resampling settings.
    """
    bucket_size: float = 2000.0
    dynamic_bucket_size: bool = True  # NEW: Enable dynamic sizing
    daily_volume_proxy_div: float = 50.0  # target ~50 bars per day
    min_bucket_size: float = 1000.0   # floor for small caps
    min_ticks_per_bucket: int = 10
    volume_mode: str = "cumulative"   # {"cumulative", "delta"}
    volume_floor: float = 0.0


@dataclass(frozen=True)
class L2QualityConfig:
    """
    Data quality filters for L2 quotes.
    """
    drop_zero_price: bool = True
    drop_zero_volume: bool = True
    min_price: float = 0.0
    min_volume: float = 0.0
    # Top-of-book validity guard (prevents microprice=0 artifacts from invalid quotes).
    require_valid_top_book: bool = True
    min_book_price: float = 0.0
    min_top_book_depth: float = 0.0
    # Frame-level fail-closed guard for non-positive derived prices.
    drop_nonpositive_frame_price: bool = True
    min_frame_price: float = 0.0


@dataclass(frozen=True)
class L2MicroPriceConfig:
    """
    Microprice computation settings.
    """
    depth_level: int = 1
    depth_floor: float = 1.0


@dataclass(frozen=True)
class L2OFIConfig:
    """
    Order Flow Imbalance settings.
    """
    ofi_mode: str = "price_change"    # {"price_change", "queue_delta"}
    depth_levels: int = 1
    ofi_weight_decay: float = 1.0     # weight = decay^(level-1)
    ofi_zero_value: float = 0.0


@dataclass(frozen=True)
class L2SRLConfig:
    """
    Inverse Square-Root Law settings.
    """
    y_coeff: float = 0.75
    sigma_floor: float = 1e-12
    depth_floor: float = 1.0
    exponent: float = 0.5

    # v40 race lanes (nonlinear impact exponent sweep)
    race_exponents: Tuple[float, ...] = (0.33, 0.5, 0.66)
    race_lane_names: Tuple[str, ...] = ("033", "050", "066")
    standard_lane_index: int = 1

    # Effective-depth correction for spoofing / cancellation-heavy tapes
    spoof_penalty_gamma: float = 0.5
    spoof_ratio_eps: float = 1e-9
    implied_y_min_penalty: float = 0.5
    implied_y_min_impact: float = 1e-9

    # Adaptive Y recursion bounds
    y_min: float = 0.1
    y_max: float = 5.0
    y_ema_alpha: float = 0.1494  # Optimized (Hero Run)
    # v40 patch_02: anchor prior learned from market-wide implied Y distribution
    anchor_y: float = 0.75
    anchor_weight: float = 0.01
    anchor_clip_min: float = 0.4
    anchor_clip_max: float = 1.5


@dataclass(frozen=True)
class L2EpiplexityConfig:
    """
    Epiplexity (symbolic compression) settings.
    """
    mode: str = "lz76_linear"
    min_trace_len: int = 10
    sax_scale_mult: float = 0.5
    scale_eps: float = 0.01
    compress_level: int = 6
    min_bytes: int = 8
    fallback_value: float = 0.0
    # v40 patch_02: energy gate (learned from market sigma distribution)
    sigma_gate_enabled: bool = True
    sigma_gate: float = 0.01
    sigma_gate_quantile: float = 0.10
    prior_sample_files: int = 50
    prior_min_sigma_points: int = 1000
    prior_min_y_points: int = 1000
    prior_random_seed: int = 42


@dataclass(frozen=True)
class L2TopologyRaceConfig:
    """
    v40 topology race configuration (multi-manifold).
    """
    enabled: bool = True
    green_coeff: float = 0.5

    # Feature names emitted by kernel reduce pass
    micro_feature: str = "topo_micro"
    classic_feature: str = "topo_classic"
    trend_feature: str = "topo_trend"

    # Robust scale floors (Denominator Trap guards)
    price_scale_floor: float = 0.01
    ofi_scale_floor: float = 1.0
    vol_scale_floor: float = 1.0
    time_scale_floor: float = 1.0

    # Fully declarative topology race mapping:
    # (feature_name, x_trace_col, y_trace_col, x_scale_attr, y_scale_attr)
    manifolds: Tuple[Tuple[str, str, str, str, str], ...] = (
        ("topo_micro", "trace", "ofi_trace", "price_scale_floor", "ofi_scale_floor"),
        ("topo_classic", "trace", "vol_trace", "price_scale_floor", "vol_scale_floor"),
        ("topo_trend", "trace", "time_trace", "price_scale_floor", "time_scale_floor"),
    )


@dataclass(frozen=True)
class L2TopoSNRConfig:
    """
    Topological SNR settings (shuffle test).
    """
    n_shuffle: int = 100
    seed: Optional[int] = 1337
    std_floor: float = 1e-12
    min_shuffles: int = 10


@dataclass(frozen=True)
class L2SignalConfig:
    """
    Signal synthesis thresholds.
    """
    epiplexity_min: float = 0.4
    peace_threshold: float = 0.8799  # Optimized (Hero Run)
    srl_resid_sigma_mult: float = 2.0
    topo_area_min_abs: float = 1e-9
    topo_energy_sigma_mult: float = 10.0
    spoofing_ratio_max: float = 2.5
    min_ofi_for_y_update: float = 100.0


@dataclass(frozen=True)
class L2ValidationConfig:
    """
    Definition-of-Done thresholds for L2 audit.
    """
    topo_snr_min: float = 3.0
    orthogonality_max_abs: float = 0.1
    vector_alignment_min: float = 0.6
    forward_return_horizon_buckets: int = 3
    min_samples: int = 30
    max_traces: Optional[int] = None
    corr_eps: float = 1e-12
    # Renormalization scan scoring controls.
    # score = snr * (renorm_ortho_penalty_factor if ortho > threshold else 1.0)
    renorm_ortho_penalty_threshold: float = 0.3
    renorm_ortho_penalty_factor: float = 0.5
    # Optional clipping for backtest return robustness.
    # Keep None by default to avoid hidden evaluation distortion.
    backtest_ret_clip_abs: Optional[float] = None


@dataclass(frozen=True)
class L2TrainConfig:
    """
    Training-specific settings for v3 (labels, sampling, robustness).
    """
    label_horizon_buckets: int = 3
    label_sigma_mult: float = 1.0
    drop_neutral_labels: bool = True
    decision_margin: float = 0.05  # Added for backtest thresholding
    # Labeling only on strictly positive price regime to avoid denominator explosions.
    min_valid_close: float = 0.0

    use_structural_filter: bool = True
    ofi_abs_quantile: float = 0.9
    topo_energy_quantile: float = 0.8

    winsor_q_low: float = 0.001
    winsor_q_high: float = 0.999

    log1p_features: Tuple[str, ...] = (
        "net_ofi",
        "depth_eff",
        "srl_resid",
        "topo_area",
        "topo_energy",
    )
    winsor_features: Tuple[str, ...] = ("topo_area",)

    sample_weight_topo: bool = True
    scale_spectrum: Tuple[int, ...] = (20, 30, 40, 50, 60, 80, 100, 120)
    renorm_sample_frac: float = 0.2

    # v40 race features (SRL + topology). Keep names explicit in config to avoid code hard-coding.
    srl_race_features: Tuple[str, ...] = (
        "srl_resid_033",
        "srl_resid_050",
        "srl_resid_066",
    )
    topology_race_features: Tuple[str, ...] = (
        "topo_micro",
        "topo_classic",
        "topo_trend",
    )


@dataclass(frozen=True)
class AShareSessionConfig:
    """
    A-Share session timings (Milliseconds from 00:00:00).
    Morning: 09:30 - 11:30
    Afternoon: 13:00 - 15:00
    """
    morning_start_ms: int = 34200000   # 09:30:00
    morning_end_ms: int = 41400000     # 11:30:00
    afternoon_start_ms: int = 46800000 # 13:00:00
    afternoon_end_ms: int = 54000000   # 15:00:00
    
    @property
    def total_duration_ms(self) -> float:
        return float((self.morning_end_ms - self.morning_start_ms) + 
                     (self.afternoon_end_ms - self.afternoon_start_ms))

@dataclass(frozen=True)
class AShareMicrostructureConfig:
    """
    A-Share specific microstructure limits.
    """
    # Limit Up/Down Singularity Threshold (Depth -> 0)
    limit_singularity_eps: float = 1e-5
    # T+1 Horizon (Days)
    t_plus_1_horizon_days: int = 1

@dataclass(frozen=True)
class L2PipelineConfig:
    """
    Full L2 pipeline configuration bundle (v3/v6).
    """
    mapping: L2MappingConfig = field(default_factory=L2MappingConfig)
    session: L2SessionConfig = field(default_factory=L2SessionConfig)
    ashare_session: AShareSessionConfig = field(default_factory=AShareSessionConfig) # v6.0
    micro: AShareMicrostructureConfig = field(default_factory=AShareMicrostructureConfig) # v6.0
    io: L2IOConfig = field(default_factory=L2IOConfig)
    volume_clock: L2VolumeClockConfig = field(default_factory=L2VolumeClockConfig)
    quality: L2QualityConfig = field(default_factory=L2QualityConfig)
    microprice: L2MicroPriceConfig = field(default_factory=L2MicroPriceConfig)
    ofi: L2OFIConfig = field(default_factory=L2OFIConfig)
    srl: L2SRLConfig = field(default_factory=L2SRLConfig)
    epiplexity: L2EpiplexityConfig = field(default_factory=L2EpiplexityConfig)
    topology_race: L2TopologyRaceConfig = field(default_factory=L2TopologyRaceConfig)
    topo_snr: L2TopoSNRConfig = field(default_factory=L2TopoSNRConfig)
    signal: L2SignalConfig = field(default_factory=L2SignalConfig)
    validation: L2ValidationConfig = field(default_factory=L2ValidationConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    train: L2TrainConfig = field(default_factory=L2TrainConfig)

    # Training plan
    stages: Sequence[TrainingStageConfig] = field(default_factory=tuple)

    # Output paths
    output_dir: str = "./artifacts"
    artifact_name: str = "omega_policy.pkl"


def load_l2_pipeline_config(prod_conf_path: Optional[str] = None) -> L2PipelineConfig:
    """
    Load L2PipelineConfig with optional overrides from a production config JSON.
    This keeps config.py immutable while allowing audited parameters to be applied at runtime.
    """
    cfg = L2PipelineConfig()
    if not prod_conf_path:
        prod_conf_path = "./model_audit/production_config.json"
    if not os.path.exists(prod_conf_path):
        return cfg

    try:
        with open(prod_conf_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return cfg

    params = data.get("AUTO_LEARNED_PARAMS", {}) if isinstance(data, dict) else {}
    target_frames = params.get("TARGET_FRAMES_DAY")
    initial_y = params.get("INITIAL_Y")
    sigma_gate = params.get("PLANCK_SIGMA_GATE")
    anchor_y = params.get("ANCHOR_Y")
    epi_min_len = params.get("EPI_BLOCK_MIN_LEN")
    epi_symbol_thresh = params.get("EPI_SYMBOL_THRESH")
    renorm_ortho_penalty_threshold = params.get("RENORM_ORTHO_PENALTY_THRESHOLD")
    renorm_ortho_penalty_factor = params.get("RENORM_ORTHO_PENALTY_FACTOR")
    backtest_ret_clip_abs = params.get("BACKTEST_RET_CLIP_ABS")

    if (
        target_frames is None
        and initial_y is None
        and sigma_gate is None
        and anchor_y is None
        and epi_min_len is None
        and epi_symbol_thresh is None
        and renorm_ortho_penalty_threshold is None
        and renorm_ortho_penalty_factor is None
        and backtest_ret_clip_abs is None
    ):
        return cfg

    vc = cfg.volume_clock
    srl = cfg.srl
    epi = cfg.epiplexity
    val = cfg.validation

    if target_frames is not None:
        vc = replace(vc, daily_volume_proxy_div=float(target_frames), dynamic_bucket_size=True)
    if initial_y is not None:
        srl = replace(srl, y_coeff=float(initial_y))
    if anchor_y is not None:
        srl = replace(srl, anchor_y=float(anchor_y))
    if sigma_gate is not None:
        epi = replace(epi, sigma_gate=float(sigma_gate))
    if epi_min_len is not None:
        epi = replace(epi, min_trace_len=int(epi_min_len))
    if epi_symbol_thresh is not None:
        epi = replace(epi, sax_scale_mult=float(epi_symbol_thresh))
    if renorm_ortho_penalty_threshold is not None:
        val = replace(val, renorm_ortho_penalty_threshold=float(renorm_ortho_penalty_threshold))
    if renorm_ortho_penalty_factor is not None:
        val = replace(val, renorm_ortho_penalty_factor=float(renorm_ortho_penalty_factor))
    if backtest_ret_clip_abs is not None:
        val = replace(val, backtest_ret_clip_abs=float(backtest_ret_clip_abs))

    return replace(cfg, volume_clock=vc, srl=srl, epiplexity=epi, validation=val)
