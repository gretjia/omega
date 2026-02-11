from __future__ import annotations

from dataclasses import dataclass
import os
from typing import List, Optional, Sequence, Tuple

import numpy as np

from config import DataSourceConfig, KernelConfig, TrainerConfig
from data_adapter import read_tick_csv
from trainer import iter_samples_from_bars, label_from_future_return, tickdata_to_bars
from parallel_config import (
    compute_sample_weight,
    source_max_windows_per_file,
    trainer_csv_cfg,
    trainer_feature_cfg,
    trainer_window_cfg,
    window_label_threshold,
)


def set_thread_env(threads: int) -> None:
    t = str(max(1, int(threads)))
    os.environ.setdefault("OMP_NUM_THREADS", t)
    os.environ.setdefault("OPENBLAS_NUM_THREADS", t)
    os.environ.setdefault("MKL_NUM_THREADS", t)
    os.environ.setdefault("NUMEXPR_NUM_THREADS", t)


@dataclass(frozen=True)
class FileCalibration:
    file_path: str
    s_bps: np.ndarray
    h_bps: np.ndarray


@dataclass(frozen=True)
class FileSamples:
    file_path: str
    X: np.ndarray
    y: np.ndarray
    w: np.ndarray
    feature_names: List[str]
    n_labeled: int


def build_file_calibration(
    file_path: str,
    kernel_cfg: KernelConfig,
    trainer_cfg: TrainerConfig,
) -> FileCalibration:
    csv_cfg = trainer_csv_cfg(trainer_cfg)
    tick = read_tick_csv(file_path, csv_cfg)
    bars = tickdata_to_bars(tick, kernel_cfg)

    window_cfg = trainer_window_cfg(trainer_cfg)
    feature_cfg = trainer_feature_cfg(trainer_cfg)

    s_vals: List[float] = []
    h_vals: List[float] = []
    for pack, _ in iter_samples_from_bars(
        bars,
        kernel_cfg,
        window_cfg,
        feature_cfg=feature_cfg,
    ):
        s_vals.append(float(pack.info.epiplexity_bps))
        h_vals.append(float(pack.info.entropy_bps))

    return FileCalibration(
        file_path=str(file_path),
        s_bps=np.asarray(s_vals, dtype=float),
        h_bps=np.asarray(h_vals, dtype=float),
    )


def build_file_samples(
    file_path: str,
    kernel_cfg: KernelConfig,
    trainer_cfg: TrainerConfig,
    stage_source: DataSourceConfig,
    sample_weight_mode: str,
) -> FileSamples:
    csv_cfg = trainer_csv_cfg(trainer_cfg)
    tick = read_tick_csv(file_path, csv_cfg)
    bars = tickdata_to_bars(tick, kernel_cfg)

    window_cfg = trainer_window_cfg(trainer_cfg)
    feature_cfg = trainer_feature_cfg(trainer_cfg)

    thr = window_label_threshold(window_cfg)
    max_wpf = source_max_windows_per_file(stage_source)

    X_list: List[np.ndarray] = []
    y_list: List[int] = []
    w_list: List[float] = []
    feature_names: Optional[List[str]] = None

    n_labeled = 0
    for pack, fut_ret in iter_samples_from_bars(
        bars,
        kernel_cfg,
        window_cfg,
        feature_cfg=feature_cfg,
    ):
        y = label_from_future_return(float(fut_ret), thr)
        if y is None:
            continue

        if feature_names is None:
            feature_names = list(pack.names)

        X_list.append(np.asarray(pack.values, dtype=float))
        y_list.append(int(y))
        w_list.append(compute_sample_weight(float(fut_ret), sample_weight_mode))
        n_labeled += 1

        if max_wpf is not None and n_labeled >= int(max_wpf):
            break

    if feature_names is None:
        feature_names = []

    if len(X_list) == 0:
        X = np.zeros((0, 0), dtype=float)
    else:
        X = np.vstack([x.reshape(1, -1) for x in X_list])

    return FileSamples(
        file_path=str(file_path),
        X=X,
        y=np.asarray(y_list, dtype=int),
        w=np.asarray(w_list, dtype=float),
        feature_names=feature_names,
        n_labeled=int(n_labeled),
    )


def iter_ordered_map(
    files: Sequence[str],
    fn,
    fn_args: Tuple,
):
    for fp in files:
        yield fn(fp, *fn_args)
