from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Optional, Sequence, Tuple


def _getattr_first(obj: Any, names: Sequence[str], default: Any = None, required: bool = False) -> Any:
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    if required:
        raise AttributeError(f"Missing attributes {list(names)} on {type(obj)}")
    return default


def default_workers() -> int:
    n = os.cpu_count() or 4
    return max(1, min(int(n), 8))

SPLIT_METHOD_FILE_FRACTION = "file_fraction"
MODEL_TYPE_SGD_LOGISTIC = "sgd_logistic"
MODEL_TYPE_SGD_REGRESSION = "sgd_regression"

CHECKPOINT_VERSION = 1
CHECKPOINT_TMP_SUFFIX = ".tmp"


@dataclass(frozen=True)
class ParallelismConfig:
    enabled: bool = True
    workers: int = default_workers()
    prefetch_files: int = 2
    worker_blas_threads: int = 1


@dataclass(frozen=True)
class ParallelAlgorithmConfig:
    class_labels: Tuple[int, int] = (0, 1)
    sample_weight_mode: str = "abs_return"


@dataclass(frozen=True)
class ParallelPathsConfig:
    output_dir: str = "./parallel_trainer/artifacts"
    artifact_name: str = "omega_policy_parallel.pkl"
    audit_dir: str = "./parallel_trainer/audit"

@dataclass(frozen=True)
class ParallelCheckpointConfig:
    enabled: bool = True
    resume: bool = True
    checkpoint_path: str = "./parallel_trainer/audit/omega_parallel_checkpoint.pkl"
    save_every_files: int = 10
    save_on_source_end: bool = True
    save_on_stage_end: bool = True


@dataclass(frozen=True)
class ParallelTrainerRunConfig:
    parallelism: ParallelismConfig = ParallelismConfig()
    algorithm: ParallelAlgorithmConfig = ParallelAlgorithmConfig()
    paths: ParallelPathsConfig = ParallelPathsConfig()
    checkpoint: ParallelCheckpointConfig = ParallelCheckpointConfig()


def load_root_kernel_config() -> Any:
    try:
        from config import KernelConfig
    except Exception as e:
        raise RuntimeError(f"Failed to import KernelConfig from root config.py: {e}") from e
    return KernelConfig()


def load_root_trainer_config() -> Any:
    try:
        from trainer import example_trainer_config
        return example_trainer_config()
    except Exception:
        pass

    try:
        from config import TrainerConfig
        return TrainerConfig()
    except Exception as e:
        raise RuntimeError(
            "Failed to build TrainerConfig. Provide trainer.example_trainer_config() "
            "or ensure config.TrainerConfig() has defaults."
        ) from e


def trainer_csv_cfg(trainer_cfg: Any) -> Any:
    return _getattr_first(trainer_cfg, ["csv", "csv_parse", "csv_parse_config"], required=True)


def trainer_feature_cfg(trainer_cfg: Any) -> Any:
    return _getattr_first(trainer_cfg, ["feature", "features", "feature_config"], required=True)


def trainer_window_cfg(trainer_cfg: Any) -> Any:
    return _getattr_first(trainer_cfg, ["window", "window_cfg", "window_config"], required=True)


def window_label_threshold(window_cfg: Any) -> float:
    return float(_getattr_first(window_cfg, ["label_return_threshold", "label_thr", "label_threshold"], required=True))


def source_max_windows_per_file(source_cfg: Any) -> Optional[int]:
    return _getattr_first(source_cfg, ["max_windows_per_file", "max_wpf"], default=None, required=False)


def compute_sample_weight(future_return: float, mode: str) -> float:
    m = str(mode).lower()
    if m == "abs_return":
        return float(abs(float(future_return)))
    if m == "one":
        return 1.0
    return float(abs(float(future_return)))


def trainer_split_cfg(trainer_cfg: Any) -> Any:
    return _getattr_first(trainer_cfg, ["split", "split_cfg", "split_config"], required=True)


def trainer_calibration_cfg(trainer_cfg: Any) -> Any:
    return _getattr_first(trainer_cfg, ["calibration", "calibration_cfg", "calibration_config"], required=True)


def trainer_model_cfg(trainer_cfg: Any) -> Any:
    return _getattr_first(trainer_cfg, ["model", "model_cfg", "model_config"], required=True)


def feature_standardize_features(feature_cfg: Any) -> bool:
    return bool(_getattr_first(feature_cfg, ["standardize_features", "standardize"], default=False))


def model_type(model_cfg: Any) -> str:
    return str(_getattr_first(model_cfg, ["model_type", "type"], required=True))


def model_batch_size(model_cfg: Any) -> int:
    return int(_getattr_first(model_cfg, ["batch_size", "batch"], required=True))


def model_sgd_params(model_cfg: Any) -> dict:
    return {
        "loss": _getattr_first(model_cfg, ["loss"], default="log_loss"),
        "penalty": _getattr_first(model_cfg, ["penalty"], default="l2"),
        "alpha": float(_getattr_first(model_cfg, ["alpha"], default=1e-4)),
        "l1_ratio": _getattr_first(model_cfg, ["l1_ratio"], default=0.15),
        "max_iter": int(_getattr_first(model_cfg, ["max_iter"], default=1)),
        "tol": _getattr_first(model_cfg, ["tol"], default=None),
        "learning_rate": _getattr_first(model_cfg, ["learning_rate"], default="optimal"),
        "eta0": float(_getattr_first(model_cfg, ["eta0"], default=0.01)),
        "power_t": float(_getattr_first(model_cfg, ["power_t"], default=0.5)),
        "average": _getattr_first(model_cfg, ["average"], default=True),
    }


def split_method(split_cfg: Any) -> str:
    return str(_getattr_first(split_cfg, ["method", "split_method"], required=True))


def supported_split_method() -> str:
    return SPLIT_METHOD_FILE_FRACTION


def split_seed(split_cfg: Any) -> int:
    return int(_getattr_first(split_cfg, ["split_seed", "seed"], default=0))


def calibration_enabled(cal_cfg: Any) -> bool:
    return bool(_getattr_first(cal_cfg, ["enabled"], default=False))


def calibration_reservoir_size(cal_cfg: Any) -> int:
    return int(_getattr_first(cal_cfg, ["reservoir_size", "reservoir"], required=True))


def calibration_max_windows_total(cal_cfg: Any) -> Optional[int]:
    v = _getattr_first(cal_cfg, ["max_windows_total", "max_windows"], default=None)
    return None if v is None else int(v)


def calibration_quantiles(cal_cfg: Any) -> Tuple[float, float, float, float]:
    q_s_low = float(_getattr_first(cal_cfg, ["q_s_low"], default=0.2))
    q_s_high = float(_getattr_first(cal_cfg, ["q_s_high"], default=0.8))
    q_h_low = float(_getattr_first(cal_cfg, ["q_h_low"], default=0.2))
    q_h_high = float(_getattr_first(cal_cfg, ["q_h_high"], default=0.8))
    return q_s_low, q_s_high, q_h_low, q_h_high
