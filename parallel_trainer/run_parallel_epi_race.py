"""
run_parallel_epi_race.py

Epiplexity v34 algorithm derby trainer.

Goals:
- Run a non-full parallel experiment to compare Epiplexity variants.
- Keep memory stable on 32GB machines.
- Support resumable checkpoints.
- Optionally stage remote/shared parquet files into local temp storage in chunks,
  then clean up chunk files immediately after processing.
"""

from __future__ import annotations

import argparse
import gc
import json
import multiprocessing as mp
import os
import pickle
import shutil
import time
from pathlib import Path
from typing import List, Optional, Sequence, Set, Tuple

import numpy as np
import polars as pl
import psutil
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import L2PipelineConfig, load_l2_pipeline_config
from omega_v3_core.trainer import OmegaTrainerV3
from tools.multi_dir_loader import discover_l2_dirs


def _memory_guard(max_percent: float, sleep_sec: float = 3.0) -> None:
    while psutil.virtual_memory().percent > max_percent:
        print(
            f"[MemoryGuard] usage={psutil.virtual_memory().percent:.1f}% "
            f"> {max_percent:.1f}%, sleeping {sleep_sec:.1f}s..."
        )
        time.sleep(sleep_sec)


def _worker_init() -> None:
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)


def _process_one_file(
    args: Tuple[str, str, L2PipelineConfig, float]
) -> Tuple[str, np.ndarray, np.ndarray, Optional[np.ndarray], int]:
    """
    Returns:
    - logical filename (for processed-files tracking)
    - X matrix
    - y vector
    - optional sample weights
    - row count
    """
    logical_name, read_path, cfg, sample_frac = args

    try:
        trainer = OmegaTrainerV3(cfg)
        with open(read_path, "rb") as fh:
            df = pl.read_parquet(fh)
        if sample_frac < 1.0 and df.height > 0:
            df = df.sample(fraction=sample_frac, seed=42)
        if df.height == 0:
            return logical_name, np.array([]), np.array([]), None, 0

        df = trainer._prepare_frames(df, cfg)
        if df.height == 0:
            return logical_name, np.array([]), np.array([]), None, 0

        missing = [c for c in trainer.feature_cols if c not in df.columns]
        if missing:
            print(f"[Worker Warn] {logical_name} missing columns {missing}, skipped.")
            return logical_name, np.array([]), np.array([]), None, 0

        X = df.select(trainer.feature_cols).to_numpy()
        y = df.select(trainer.label_col).to_numpy().ravel()

        weights = None
        if cfg.train.sample_weight_topo and "topo_area" in df.columns:
            topo = df.select("topo_area").to_numpy().ravel()
            weights = np.log1p(np.abs(topo))

        return logical_name, X, y, weights, df.height
    except Exception as exc:
        print(f"[Worker Error] {logical_name}: {exc}")
        return logical_name, np.array([]), np.array([]), None, 0


class ParallelEpiRaceTrainer:
    def __init__(
        self,
        workers: int,
        batch_rows: int,
        checkpoint_rows: int,
        sample_frac: float,
        max_files: Optional[int],
        out_dir: Path,
        checkpoint_prefix: str,
        stage_local: bool,
        stage_dir: Path,
        stage_chunk_files: int,
        cleanup_stage: bool,
        memory_threshold: float,
        data_dirs: Optional[Sequence[Path]],
        file_list_path: Optional[Path],
    ):
        self.workers = workers
        self.batch_rows = batch_rows
        self.checkpoint_rows = checkpoint_rows
        self.sample_frac = sample_frac
        self.max_files = max_files
        self.out_dir = out_dir
        self.checkpoint_prefix = checkpoint_prefix
        self.stage_local = stage_local
        self.stage_dir = stage_dir
        self.stage_chunk_files = stage_chunk_files
        self.cleanup_stage = cleanup_stage
        self.memory_threshold = memory_threshold
        self.data_dirs = list(data_dirs) if data_dirs else None
        self.file_list_path = file_list_path

        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.stage_dir.mkdir(parents=True, exist_ok=True)
        if self.stage_local and self.cleanup_stage:
            for stale in self.stage_dir.glob("chunk_*"):
                shutil.rmtree(stale, ignore_errors=True)

        base_cfg = load_l2_pipeline_config()
        self.cfg: L2PipelineConfig = base_cfg

        self.template = OmegaTrainerV3(self.cfg)
        self.feature_cols = list(self.template.feature_cols)
        self.label_col = self.template.label_col

        self.model = SGDClassifier(loss="log_loss", penalty="l2", alpha=1e-4, average=True)
        self.scaler = StandardScaler()
        self.processed_files: Set[str] = set()
        self.total_rows = 0
        self.last_checkpoint_rows = 0

    def _latest_checkpoint(self) -> Optional[Path]:
        ckpts = sorted(
            self.out_dir.glob(f"{self.checkpoint_prefix}*.pkl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return ckpts[0] if ckpts else None

    def load_checkpoint(self) -> None:
        ckpt = self._latest_checkpoint()
        if ckpt is None:
            print("[Init] No checkpoint found for epi race. Starting fresh.")
            return
        print(f"[Init] Resume from {ckpt.name}")
        with open(ckpt, "rb") as f:
            payload = pickle.load(f)
        loaded_feature_cols = list(payload.get("feature_cols", []))
        if loaded_feature_cols and loaded_feature_cols != list(self.feature_cols):
            print("[Init] Feature space mismatch vs checkpoint. Starting fresh state.")
            self.model = SGDClassifier(loss="log_loss", penalty="l2", alpha=1e-4, average=True)
            self.scaler = StandardScaler()
            self.processed_files = set()
            self.total_rows = 0
            self.last_checkpoint_rows = 0
            return
        self.model = payload["model"]
        self.scaler = payload["scaler"]
        self.feature_cols = payload.get("feature_cols", self.feature_cols)
        self.processed_files = set(payload.get("processed_files", set()))
        self.total_rows = int(payload.get("total_rows", 0))
        self.last_checkpoint_rows = self.total_rows
        print(
            f"[Init] Restored rows={self.total_rows:,}, "
            f"processed_files={len(self.processed_files)}"
        )

    def _save_checkpoint(self) -> Path:
        name = f"{self.checkpoint_prefix}{self.total_rows}.pkl"
        path = self.out_dir / name
        payload = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_cols": self.feature_cols,
            "cfg": self.cfg,
            "processed_files": self.processed_files,
            "total_rows": self.total_rows,
        }
        tmp = path.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            pickle.dump(payload, f)
        tmp.replace(path)
        self.last_checkpoint_rows = self.total_rows
        print(f"[Checkpoint] {path.name}")
        return path

    def _discover_tasks(self) -> List[Path]:
        if self.file_list_path is not None:
            paths: List[Path] = []
            with open(self.file_list_path, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s:
                        continue
                    p = Path(s)
                    if p.name in self.processed_files:
                        continue
                    paths.append(p)
            if self.max_files is not None:
                paths = paths[: max(int(self.max_files), 0)]
            print(
                f"[Plan] file-list mode: source={self.file_list_path}, "
                f"run_now={len(paths)}",
                flush=True,
            )
            return paths

        if self.data_dirs:
            dirs = [Path(d) for d in self.data_dirs]
        else:
            dirs = discover_l2_dirs()
        print(f"[Plan] data_dirs={len(dirs)}", flush=True)
        if self.max_files is not None:
            limit = max(int(self.max_files), 0)
            selected: List[Path] = []
            scanned = 0
            started = time.time()
            for d in dirs:
                print(f"[Plan] scanning dir={d}", flush=True)
                try:
                    with os.scandir(d) as it:
                        for ent in it:
                            if not ent.is_file(follow_symlinks=False):
                                continue
                            if not ent.name.endswith(".parquet"):
                                continue
                            scanned += 1
                            if scanned % 100 == 0:
                                print(
                                    f"[Plan] scanned={scanned}, selected={len(selected)}, "
                                    f"elapsed={time.time() - started:.1f}s",
                                    flush=True,
                                )
                            if ent.name in self.processed_files:
                                continue
                            selected.append(Path(ent.path))
                            if len(selected) >= limit:
                                break
                except Exception as exc:
                    print(f"[Plan Warn] failed scanning {d}: {exc}", flush=True)
                if len(selected) >= limit:
                    break
            print(
                f"[Plan] scanned~{scanned}, processed={len(self.processed_files)}, "
                f"run_now={len(selected)} (max_files={limit})",
                flush=True,
            )
            return selected

        files: List[Path] = []
        for d in dirs:
            print(f"[Plan] scanning full dir={d}", flush=True)
            try:
                with os.scandir(d) as it:
                    for ent in it:
                        if ent.is_file(follow_symlinks=False) and ent.name.endswith(".parquet"):
                            files.append(Path(ent.path))
            except Exception as exc:
                print(f"[Plan Warn] failed scanning {d}: {exc}", flush=True)
        remaining = [p for p in files if p.name not in self.processed_files]
        print(
            f"[Plan] total={len(files)}, processed={len(self.processed_files)}, "
            f"run_now={len(remaining)}",
            flush=True,
        )
        return remaining

    def _stage_chunk(self, chunk: Sequence[Path], chunk_id: int) -> List[Tuple[str, str]]:
        if not self.stage_local:
            return [(p.name, str(p)) for p in chunk]

        _memory_guard(self.memory_threshold)
        chunk_dir = self.stage_dir / f"chunk_{chunk_id:06d}"
        chunk_dir.mkdir(parents=True, exist_ok=True)
        staged: List[Tuple[str, str]] = []
        t0 = time.time()
        for src in chunk:
            dst = chunk_dir / src.name
            shutil.copy2(src, dst)
            staged.append((src.name, str(dst)))
        elapsed = time.time() - t0
        print(
            f"[Stage] chunk={chunk_id}, files={len(staged)}, "
            f"elapsed={elapsed:.1f}s, dir={chunk_dir}"
        )
        return staged

    def _cleanup_chunk(self, staged: Sequence[Tuple[str, str]]) -> None:
        if not self.stage_local or not self.cleanup_stage:
            return
        if not staged:
            return
        chunk_dir = Path(staged[0][1]).parent
        try:
            shutil.rmtree(chunk_dir, ignore_errors=True)
        except Exception as exc:
            print(f"[Cleanup Warn] {chunk_dir}: {exc}")

    def _fit_buffer(
        self,
        X_buf: List[np.ndarray],
        y_buf: List[np.ndarray],
        w_buf: List[np.ndarray],
        rows_in_buf: int,
        classes: np.ndarray,
    ) -> None:
        if rows_in_buf <= 0:
            return
        X_batch = np.vstack(X_buf)
        y_batch = np.concatenate(y_buf)
        w_batch = np.concatenate(w_buf) if w_buf else None

        self.scaler.partial_fit(X_batch)
        X_scaled = self.scaler.transform(X_batch)
        self.model.partial_fit(X_scaled, y_batch, classes=classes, sample_weight=w_batch)
        self.total_rows += rows_in_buf

        del X_batch, y_batch, w_batch, X_scaled
        gc.collect()

    def train(self) -> Path:
        tasks = self._discover_tasks()
        if not tasks:
            return self._save_checkpoint()

        classes = np.array([-1, 1]) if self.cfg.train.drop_neutral_labels else np.array([-1, 0, 1])
        X_buf: List[np.ndarray] = []
        y_buf: List[np.ndarray] = []
        w_buf: List[np.ndarray] = []
        rows_in_buf = 0
        start = time.time()

        chunks = [
            tasks[i : i + self.stage_chunk_files]
            for i in range(0, len(tasks), self.stage_chunk_files)
        ]

        with mp.Pool(processes=self.workers, initializer=_worker_init) as pool:
            for chunk_id, chunk in enumerate(chunks):
                _memory_guard(self.memory_threshold)
                staged = self._stage_chunk(chunk, chunk_id)
                job_args = [
                    (logical_name, read_path, self.cfg, self.sample_frac)
                    for logical_name, read_path in staged
                ]

                for logical_name, X_part, y_part, w_part, n_rows in pool.imap_unordered(
                    _process_one_file, job_args, chunksize=1
                ):
                    self.processed_files.add(logical_name)
                    if n_rows > 0:
                        X_buf.append(X_part)
                        y_buf.append(y_part)
                        if w_part is not None:
                            w_buf.append(w_part)
                        rows_in_buf += n_rows

                    if rows_in_buf >= self.batch_rows:
                        self._fit_buffer(X_buf, y_buf, w_buf, rows_in_buf, classes)
                        X_buf, y_buf, w_buf = [], [], []
                        rows_in_buf = 0
                        elapsed = max(time.time() - start, 1.0)
                        print(
                            f"[Train] rows={self.total_rows:,}, files={len(self.processed_files)}, "
                            f"speed={self.total_rows / elapsed:.1f} rows/s"
                        )
                        if self.total_rows - self.last_checkpoint_rows >= self.checkpoint_rows:
                            self._save_checkpoint()
                        _memory_guard(self.memory_threshold)

                self._cleanup_chunk(staged)

        if rows_in_buf > 0:
            self._fit_buffer(X_buf, y_buf, w_buf, rows_in_buf, classes)
        final_ckpt = self._save_checkpoint()
        return final_ckpt

    def export_weight_report(self, checkpoint_path: Path, report_path: Path) -> None:
        if not hasattr(self.model, "coef_"):
            report = {
                "checkpoint": str(checkpoint_path),
                "total_rows": self.total_rows,
                "feature_cols": self.feature_cols,
                "status": "no_fitted_batches",
                "message": "No valid training batches were produced under current filtering/label settings.",
            }
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"[Report] {report_path} (no fitted batches)")
            return

        coef = self.model.coef_
        if coef.ndim == 1:
            coef = coef.reshape(1, -1)
        # For multiclass, use L2 norm across classes as a stable importance proxy.
        if coef.shape[0] > 1:
            w = np.linalg.norm(coef, axis=0)
        else:
            w = coef[0]

        rows = []
        for idx, feat in enumerate(self.feature_cols):
            val = float(w[idx])
            rows.append(
                {
                    "feature": feat,
                    "weight": val,
                    "abs_weight": abs(val),
                }
            )
        rows.sort(key=lambda r: r["abs_weight"], reverse=True)

        epi_rows = [r for r in rows if r["feature"].startswith("epiplexity")]
        winner = epi_rows[0]["feature"] if epi_rows else "N/A"

        report = {
            "checkpoint": str(checkpoint_path),
            "total_rows": self.total_rows,
            "feature_cols": self.feature_cols,
            "epiplexity_winner_by_abs_weight": winner,
            "epiplexity_weights": epi_rows,
            "top10_abs_weights": rows[:10],
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"[Report] {report_path}")


def parse_args() -> argparse.Namespace:
    cpu = os.cpu_count() or 8
    default_workers = max(2, min(8, cpu - 2))
    p = argparse.ArgumentParser(description="v34 Epiplexity algorithm derby trainer")
    p.add_argument("--workers", type=int, default=default_workers)
    p.add_argument("--batch-rows", type=int, default=120000)
    p.add_argument("--checkpoint-rows", type=int, default=400000)
    p.add_argument("--sample-frac", type=float, default=0.15)
    p.add_argument("--max-files", type=int, default=600)
    p.add_argument("--out-dir", type=str, default="./artifacts/epi_race")
    p.add_argument("--checkpoint-prefix", type=str, default="epi_race_ckpt_rows_")
    p.add_argument("--stage-local", action="store_true")
    p.add_argument("--stage-dir", type=str, default="/tmp/omega_epi_stage")
    p.add_argument("--stage-chunk-files", type=int, default=24)
    p.add_argument("--no-cleanup-stage", action="store_true")
    p.add_argument("--memory-threshold", type=float, default=82.0)
    p.add_argument("--no-resume", action="store_true")
    p.add_argument("--report-path", type=str, default="./audit/v34_epi_race_report.json")
    p.add_argument(
        "--data-dir",
        action="append",
        default=None,
        help="Optional parquet directory to train on. Can be repeated.",
    )
    p.add_argument(
        "--file-list",
        type=str,
        default=None,
        help="Optional newline-separated absolute parquet file list. Overrides directory scanning.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    trainer = ParallelEpiRaceTrainer(
        workers=max(1, int(args.workers)),
        batch_rows=max(1000, int(args.batch_rows)),
        checkpoint_rows=max(1000, int(args.checkpoint_rows)),
        sample_frac=min(max(float(args.sample_frac), 0.0001), 1.0),
        max_files=None if args.max_files is None else max(1, int(args.max_files)),
        out_dir=Path(args.out_dir),
        checkpoint_prefix=str(args.checkpoint_prefix),
        stage_local=bool(args.stage_local),
        stage_dir=Path(args.stage_dir),
        stage_chunk_files=max(1, int(args.stage_chunk_files)),
        cleanup_stage=not bool(args.no_cleanup_stage),
        memory_threshold=float(args.memory_threshold),
        data_dirs=[Path(p) for p in args.data_dir] if args.data_dir else None,
        file_list_path=Path(args.file_list) if args.file_list else None,
    )

    if not args.no_resume:
        trainer.load_checkpoint()
    ckpt = trainer.train()
    trainer.export_weight_report(ckpt, Path(args.report_path))


if __name__ == "__main__":
    mp.freeze_support()
    main()
