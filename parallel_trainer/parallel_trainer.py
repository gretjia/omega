from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import math
import os
import pickle
from concurrent.futures import Future, ProcessPoolExecutor

import numpy as np
from sklearn.linear_model import SGDClassifier, SGDRegressor
from sklearn.preprocessing import StandardScaler

from config import DataSourceConfig, KernelConfig, TrainerConfig
from data_adapter import iter_csv_files
from trainer import ReservoirSampler, file_fraction_split

from artifact_loader import dataclass_from_dict
from parallel_config import (
    CHECKPOINT_TMP_SUFFIX,
    CHECKPOINT_VERSION,
    MODEL_TYPE_SGD_LOGISTIC,
    MODEL_TYPE_SGD_REGRESSION,
    ParallelTrainerRunConfig,
    calibration_enabled,
    calibration_max_windows_total,
    calibration_quantiles,
    calibration_reservoir_size,
    feature_standardize_features,
    model_batch_size,
    model_sgd_params,
    model_type,
    supported_split_method,
    split_method,
    trainer_calibration_cfg,
    trainer_feature_cfg,
    trainer_model_cfg,
    trainer_split_cfg,
)
from parallel_dataflow import (
    FileCalibration,
    FileSamples,
    build_file_calibration,
    build_file_samples,
    set_thread_env,
)


@dataclass(frozen=True)
class TrainedArtifacts:
    kernel_config: KernelConfig
    trainer_config: TrainerConfig
    feature_names: List[str]
    scaler: Optional[StandardScaler]
    model: object
    calibration: Dict[str, float]


def _task_build_calibration(task: Tuple[str, KernelConfig, TrainerConfig]) -> FileCalibration:
    fp, kernel_cfg, trainer_cfg = task
    return build_file_calibration(fp, kernel_cfg, trainer_cfg)


def _task_build_samples(task: Tuple[str, KernelConfig, TrainerConfig, DataSourceConfig, str]) -> FileSamples:
    fp, kernel_cfg, trainer_cfg, src, sample_weight_mode = task
    return build_file_samples(fp, kernel_cfg, trainer_cfg, src, sample_weight_mode)


def _ordered_prefetch_map(
    executor: ProcessPoolExecutor,
    fn,
    tasks: Sequence,
    prefetch: int,
) -> Iterator:
    prefetch = max(1, int(prefetch))
    idx = 0
    pending: List[Future] = []

    def submit_one(i: int) -> None:
        pending.append(executor.submit(fn, tasks[i]))

    n = len(tasks)
    while idx < n and len(pending) < prefetch:
        submit_one(idx)
        idx += 1

    out_i = 0
    while pending:
        fut = pending.pop(0)
        yield fut.result()
        out_i += 1

        if idx < n:
            submit_one(idx)
            idx += 1


@dataclass(frozen=True)
class _CheckpointProgress:
    stage_index: int
    epoch_index: int
    source_index: int
    file_index: int


def _atomic_write_pickle(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + CHECKPOINT_TMP_SUFFIX)
    with open(tmp, "wb") as f:
        pickle.dump(payload, f)
    tmp.replace(path)


def _load_checkpoint(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


class ParallelOmegaTrainer:
    def __init__(self, kernel_cfg: KernelConfig, trainer_cfg: TrainerConfig, run_cfg: ParallelTrainerRunConfig):
        self.kernel_cfg = kernel_cfg
        self.trainer_cfg = trainer_cfg
        self.run_cfg = run_cfg
        self.parallelism = run_cfg.parallelism
        self.algorithm = run_cfg.algorithm

    def _iter_stage_files(self, src: DataSourceConfig) -> Tuple[List[str], List[str], List[str]]:
        files = list(iter_csv_files(src))
        split_cfg = trainer_split_cfg(self.trainer_cfg)
        if split_method(split_cfg) != supported_split_method():
            raise NotImplementedError(f"Split method not implemented in v1: {split_method(split_cfg)}")
        return file_fraction_split(files, split_cfg)

    def calibrate_thresholds(self, sources: Sequence[DataSourceConfig]) -> Tuple[KernelConfig, Dict[str, float]]:
        cal_cfg = trainer_calibration_cfg(self.trainer_cfg)
        if not calibration_enabled(cal_cfg):
            return self.kernel_cfg, {}

        res_size = calibration_reservoir_size(cal_cfg)
        q_s_low, q_s_high, q_h_low, q_h_high = calibration_quantiles(cal_cfg)
        max_total = calibration_max_windows_total(cal_cfg)

        s_res = ReservoirSampler(res_size, seed=res_size + 1)
        h_res = ReservoirSampler(res_size, seed=res_size + 2)

        tasks: List[Tuple[str, KernelConfig, TrainerConfig]] = []
        split_cfg = trainer_split_cfg(self.trainer_cfg)
        for src in sources:
            files = list(iter_csv_files(src))
            train_files, _, _ = file_fraction_split(files, split_cfg)
            for fp in train_files:
                tasks.append((fp, self.kernel_cfg, self.trainer_cfg))

        total_windows = 0

        if self.parallelism.enabled:
            set_thread_env(self.parallelism.worker_blas_threads)
            workers = max(1, int(self.parallelism.workers))
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for out in _ordered_prefetch_map(ex, _task_build_calibration, tasks, self.parallelism.prefetch_files):
                    remaining = None if max_total is None else int(max_total) - int(total_windows)
                    if remaining is not None and remaining <= 0:
                        break

                    s_vals = out.s_bps
                    h_vals = out.h_bps
                    if remaining is not None:
                        s_vals = s_vals[:remaining]
                        h_vals = h_vals[:remaining]

                    for s in s_vals.tolist():
                        s_res.add(float(s))
                    for h in h_vals.tolist():
                        h_res.add(float(h))

                    total_windows += int(s_vals.size)
                    if max_total is not None and total_windows >= int(max_total):
                        break
        else:
            for out in map(_task_build_calibration, tasks):
                remaining = None if max_total is None else int(max_total) - int(total_windows)
                if remaining is not None and remaining <= 0:
                    break

                s_vals = out.s_bps
                h_vals = out.h_bps
                if remaining is not None:
                    s_vals = s_vals[:remaining]
                    h_vals = h_vals[:remaining]

                for s in s_vals.tolist():
                    s_res.add(float(s))
                for h in h_vals.tolist():
                    h_res.add(float(h))

                total_windows += int(s_vals.size)
                if max_total is not None and total_windows >= int(max_total):
                    break

        s_low = s_res.quantile(q_s_low)
        s_high = s_res.quantile(q_s_high)
        h_low = h_res.quantile(q_h_low)
        h_high = h_res.quantile(q_h_high)

        if not (math.isfinite(s_low) and math.isfinite(s_high) and s_high > s_low):
            s_low, s_high = self.kernel_cfg.decision.epiplexity_low, self.kernel_cfg.decision.epiplexity_high
        if not (math.isfinite(h_low) and math.isfinite(h_high) and h_high > h_low):
            h_low, h_high = self.kernel_cfg.decision.entropy_low, self.kernel_cfg.decision.entropy_high

        new_decision = replace(
            self.kernel_cfg.decision,
            epiplexity_low=float(s_low),
            epiplexity_high=float(s_high),
            entropy_low=float(h_low),
            entropy_high=float(h_high),
        )
        new_kernel_cfg = replace(self.kernel_cfg, decision=new_decision)

        calibration = {
            "epiplexity_low": float(s_low),
            "epiplexity_high": float(s_high),
            "entropy_low": float(h_low),
            "entropy_high": float(h_high),
            "n_windows_used": float(total_windows),
        }
        return new_kernel_cfg, calibration

    def _build_model_and_scaler(self, feature_dim: int) -> Tuple[object, Optional[StandardScaler]]:
        model_cfg = trainer_model_cfg(self.trainer_cfg)
        feature_cfg = trainer_feature_cfg(self.trainer_cfg)
        scaler = StandardScaler(with_mean=True, with_std=True) if feature_standardize_features(feature_cfg) else None

        mtype = model_type(model_cfg)
        params = model_sgd_params(model_cfg)

        if mtype == MODEL_TYPE_SGD_LOGISTIC:
            model = SGDClassifier(**params)
            return model, scaler
        if mtype == MODEL_TYPE_SGD_REGRESSION:
            model = SGDRegressor(
                penalty=params["penalty"],
                alpha=params["alpha"],
                l1_ratio=params["l1_ratio"],
                max_iter=params["max_iter"],
                tol=params["tol"],
                learning_rate=params["learning_rate"],
                eta0=params["eta0"],
                power_t=params["power_t"],
                average=params["average"],
            )
            return model, scaler
        raise ValueError(f"Unknown model_type: {mtype}")

    def _probe_feature_space(self, kernel_cfg: KernelConfig) -> Tuple[int, List[str]]:
        split_cfg = trainer_split_cfg(self.trainer_cfg)
        for stage in self.trainer_cfg.stages:
            for src in stage.sources:
                files = list(iter_csv_files(src))
                train_files, _, _ = file_fraction_split(files, split_cfg)
                for fp in train_files[: max(1, min(5, len(train_files)))]:
                    out = build_file_samples(fp, kernel_cfg, self.trainer_cfg, src, self.algorithm.sample_weight_mode)
                    if out.n_labeled <= 0 or out.X.size == 0:
                        continue
                    return int(out.X.shape[1]), list(out.feature_names)
        return 0, []

    def _partial_fit(
        self,
        model: object,
        scaler: Optional[StandardScaler],
        X: np.ndarray,
        y: np.ndarray,
        w: np.ndarray,
        classes: np.ndarray,
    ) -> None:
        if X.size == 0:
            return
        if scaler is not None:
            scaler.partial_fit(X)
            X = scaler.transform(X)

        if isinstance(model, SGDClassifier):
            if not hasattr(model, "classes_"):
                model.partial_fit(X, y, classes=classes, sample_weight=w)
            else:
                model.partial_fit(X, y, sample_weight=w)
        elif isinstance(model, SGDRegressor):
            model.partial_fit(X, y.astype(float), sample_weight=w)
        else:
            raise TypeError(f"Unsupported model type: {type(model)}")

    def fit(self) -> TrainedArtifacts:
        ckpt_cfg = self.run_cfg.checkpoint
        ckpt_path = Path(str(ckpt_cfg.checkpoint_path))

        kernel_cfg: KernelConfig
        cal_dict: Dict[str, float]
        model: object
        scaler: Optional[StandardScaler]
        probe_names: List[str]

        start_prog = _CheckpointProgress(0, 0, 0, 0)
        X_buf: List[np.ndarray] = []
        y_buf: List[int] = []
        w_buf: List[float] = []
        probe_dim: int = 0
        resumed = False

        if ckpt_cfg.enabled and ckpt_cfg.resume:
            payload = _load_checkpoint(ckpt_path)
            if payload is not None:
                try:
                    if int(payload.get("version", -1)) != int(CHECKPOINT_VERSION):
                        raise ValueError("Checkpoint version mismatch")
                    kernel_cfg = dataclass_from_dict(KernelConfig, payload["kernel_config"])
                    self.trainer_cfg = dataclass_from_dict(TrainerConfig, payload["trainer_config"])
                    cal_dict = dict(payload.get("calibration", {}))
                    probe_names = list(payload.get("feature_names", []))
                    probe_dim = int(payload.get("feature_dim", 0)) or int(len(probe_names))
                    model = payload.get("model")
                    scaler = payload.get("scaler")
                    if model is None or probe_dim <= 0:
                        raise ValueError("Checkpoint missing model or feature_dim")
                    buf = payload.get("buffer", {})
                    Xb = np.asarray(buf.get("X_buf", np.zeros((0, 0))), dtype=float)
                    yb = np.asarray(buf.get("y_buf", np.asarray([], dtype=int)), dtype=int).tolist()
                    wb = np.asarray(buf.get("w_buf", np.asarray([], dtype=float)), dtype=float).tolist()
                    X_buf = [Xb[i] for i in range(int(Xb.shape[0]))] if Xb.ndim == 2 and Xb.size > 0 else []
                    y_buf = [int(v) for v in yb]
                    w_buf = [float(v) for v in wb]
                    p = payload.get("progress", {})
                    start_prog = _CheckpointProgress(
                        stage_index=int(p.get("stage_index", 0)),
                        epoch_index=int(p.get("epoch_index", 0)),
                        source_index=int(p.get("source_index", 0)),
                        file_index=int(p.get("file_index", 0)),
                    )
                    resumed = True
                except Exception:
                    payload = None

        if not resumed:
            all_sources: List[DataSourceConfig] = []
            for st in self.trainer_cfg.stages:
                all_sources.extend(list(st.sources))
            if len(self.trainer_cfg.stages) == 0:
                raise ValueError("TrainerConfig.stages is empty. Please define at least one TrainingStageConfig.")

            kernel_cfg, cal_dict = self.calibrate_thresholds(all_sources)

            probe_dim, probe_names = self._probe_feature_space(kernel_cfg)
            if probe_dim <= 0:
                raise RuntimeError("Feature dimension probe failed: no valid samples were found.")

            model, scaler = self._build_model_and_scaler(probe_dim)

            if ckpt_cfg.enabled:
                _atomic_write_pickle(
                    ckpt_path,
                    {
                        "version": CHECKPOINT_VERSION,
                        "kernel_config": asdict(kernel_cfg),
                        "trainer_config": asdict(self.trainer_cfg),
                        "feature_names": list(probe_names),
                        "feature_dim": int(probe_dim),
                        "calibration": dict(cal_dict),
                        "model": model,
                        "scaler": scaler,
                        "buffer": {"X_buf": np.zeros((0, probe_dim), dtype=float), "y_buf": [], "w_buf": []},
                        "progress": {
                            "stage_index": 0,
                            "epoch_index": 0,
                            "source_index": 0,
                            "file_index": 0,
                        },
                    },
                )

        model_cfg = trainer_model_cfg(self.trainer_cfg)
        batch_size = model_batch_size(model_cfg)
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        classes = np.asarray(list(self.algorithm.class_labels), dtype=int)

        def flush() -> None:
            nonlocal X_buf, y_buf, w_buf
            if len(X_buf) == 0:
                return
            Xb = np.vstack([x.reshape(1, -1) for x in X_buf])
            yb = np.asarray(y_buf, dtype=int)
            wb = np.asarray(w_buf, dtype=float)
            self._partial_fit(model, scaler, Xb, yb, wb, classes)
            X_buf, y_buf, w_buf = [], [], []

        def maybe_checkpoint(stage_i: int, epoch_i: int, src_i: int, file_i_next: int, feature_dim: int) -> None:
            if not ckpt_cfg.enabled:
                return
            Xb = np.vstack([x.reshape(1, -1) for x in X_buf]) if len(X_buf) > 0 else np.zeros((0, feature_dim), dtype=float)
            _atomic_write_pickle(
                ckpt_path,
                {
                    "version": CHECKPOINT_VERSION,
                    "kernel_config": asdict(kernel_cfg),
                    "trainer_config": asdict(self.trainer_cfg),
                    "feature_names": list(probe_names),
                    "feature_dim": int(feature_dim),
                    "calibration": dict(cal_dict),
                    "model": model,
                    "scaler": scaler,
                    "buffer": {
                        "X_buf": Xb,
                        "y_buf": list(y_buf),
                        "w_buf": list(w_buf),
                    },
                    "progress": {
                        "stage_index": int(stage_i),
                        "epoch_index": int(epoch_i),
                        "source_index": int(src_i),
                        "file_index": int(file_i_next),
                    },
                },
            )

        for stage_i, stage in enumerate(self.trainer_cfg.stages):
            if stage_i < start_prog.stage_index:
                continue
            for epoch_i in range(int(stage.epochs)):
                if stage_i == start_prog.stage_index and epoch_i < start_prog.epoch_index:
                    continue
                for src_i, src in enumerate(stage.sources):
                    if stage_i == start_prog.stage_index and epoch_i == start_prog.epoch_index and src_i < start_prog.source_index:
                        continue

                    train_files, _, _ = self._iter_stage_files(src)
                    start_file = start_prog.file_index if (stage_i == start_prog.stage_index and epoch_i == start_prog.epoch_index and src_i == start_prog.source_index) else 0
                    train_files = train_files[start_file:]

                    tasks = [(fp, kernel_cfg, self.trainer_cfg, src, self.algorithm.sample_weight_mode) for fp in train_files]

                    file_counter = start_file

                    if self.parallelism.enabled:
                        set_thread_env(self.parallelism.worker_blas_threads)
                        workers = max(1, int(self.parallelism.workers))
                        with ProcessPoolExecutor(max_workers=workers) as ex:
                            for out in _ordered_prefetch_map(ex, _task_build_samples, tasks, self.parallelism.prefetch_files):
                                if out.X.size > 0:
                                    for i in range(int(out.X.shape[0])):
                                        X_buf.append(out.X[i])
                                        y_buf.append(int(out.y[i]))
                                        w_buf.append(float(out.w[i]))
                                        if len(X_buf) >= batch_size:
                                            flush()

                                file_counter += 1
                                if ckpt_cfg.enabled and (file_counter % int(ckpt_cfg.save_every_files) == 0):
                                    maybe_checkpoint(stage_i, epoch_i, src_i, file_counter, probe_dim)
                    else:
                        for out in map(_task_build_samples, tasks):
                            if out.X.size > 0:
                                for i in range(int(out.X.shape[0])):
                                    X_buf.append(out.X[i])
                                    y_buf.append(int(out.y[i]))
                                    w_buf.append(float(out.w[i]))
                                    if len(X_buf) >= batch_size:
                                        flush()

                            file_counter += 1
                            if ckpt_cfg.enabled and (file_counter % int(ckpt_cfg.save_every_files) == 0):
                                maybe_checkpoint(stage_i, epoch_i, src_i, file_counter, probe_dim)

                    if ckpt_cfg.enabled and ckpt_cfg.save_on_source_end:
                        maybe_checkpoint(stage_i, epoch_i, src_i + 1, 0, probe_dim)

            if ckpt_cfg.enabled and ckpt_cfg.save_on_stage_end:
                maybe_checkpoint(stage_i + 1, 0, 0, 0, probe_dim)

        flush()

        artifacts = TrainedArtifacts(
            kernel_config=kernel_cfg,
            trainer_config=self.trainer_cfg,
            feature_names=probe_names,
            scaler=scaler,
            model=model,
            calibration=cal_dict,
        )
        return artifacts

    def save_artifacts(self, artifacts: TrainedArtifacts, output_dir: str, artifact_name: str) -> str:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / artifact_name

        payload = {
            "kernel_config": asdict(artifacts.kernel_config),
            "trainer_config": asdict(artifacts.trainer_config),
            "feature_names": artifacts.feature_names,
            "calibration": artifacts.calibration,
            "scaler": artifacts.scaler,
            "model": artifacts.model,
        }
        with open(path, "wb") as f:
            pickle.dump(payload, f)
        return str(path)
