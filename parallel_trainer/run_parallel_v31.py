"""
run_parallel_v31.py

High-performance Parallel Trainer for OMEGA v5.0 (Holographic Damper).
(Filename retained for pipeline compatibility; Logic aligned with v5.0)

Strictly adheres to v5.0 math/logic while parallelizing the 'apply_recursive_physics' bottleneck.

Architecture:
- Producer (Workers): Load Parquet -> Apply Recursive Physics (CPU intensive) -> Label Engineering -> Return Vectors
- Consumer (Main): Aggregates vectors -> SGD Partial Fit (Single Threaded)

Compatibility:
- Reads/Writes the EXACT SAME checkpoint format as `omega_core/trainer.py`.
- Can resume directly from `artifacts/checkpoint_rows_*.pkl`.
"""

import sys
import os
import time
import pickle
import shutil
import math
import argparse
import json
from pathlib import Path
from typing import Iterator, List, Tuple, Set, Optional, Dict, Sequence
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import polars as pl
import psutil
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config import load_l2_pipeline_config, L2PipelineConfig
from omega_core.trainer import OmegaTrainerV3
from tools.multi_dir_loader import discover_l2_dirs


def _sanitize_for_json(value):
    if isinstance(value, dict):
        return {k: _sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_for_json(v) for v in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return value
    return value


def _write_json_atomic(
    path: Path,
    payload: Dict,
    retries: int = 8,
    base_sleep_sec: float = 0.05,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_payload = _sanitize_for_json(payload)
    last_exc: Optional[Exception] = None
    max_retries = max(1, int(retries))
    for attempt in range(max_retries):
        tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}.{attempt}")
        try:
            with open(tmp, "w", encoding="utf-8", newline="\n") as f:
                json.dump(safe_payload, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
            return
        except PermissionError as exc:
            last_exc = exc
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            if attempt + 1 >= max_retries:
                break
            sleep_sec = float(base_sleep_sec) * (2 ** attempt)
            time.sleep(min(sleep_sec, 2.0))
        except Exception:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            raise

    # Windows share mode may block os.replace(). Fallback to direct overwrite.
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(safe_payload, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        return
    except Exception:
        if last_exc is not None:
            raise last_exc
        raise


def _memory_guard(threshold: float, sleep_sec: float = 3.0) -> None:
    while psutil.virtual_memory().percent > threshold:
        print(
            f"[MemoryGuard] usage={psutil.virtual_memory().percent:.1f}% "
            f"> {threshold:.1f}%, sleeping {sleep_sec:.1f}s...",
            flush=True
        )
        time.sleep(sleep_sec)
# --- Worker Logic ---

def worker_init():
    """Initializer for worker processes to handle signal interrupts gracefully."""
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def process_file_v31(args) -> Tuple[str, np.ndarray, np.ndarray, Optional[np.ndarray], int, str]:
    """
    Worker function:
    1. Loads a single Parquet file.
    2. Applies v3.1 Recursive Physics & Label Engineering (via OmegaTrainerV3 logic).
    3. Returns feature vectors (X), labels (y), and weights (w).
    
    Returns: (filename, X, y, w, n_rows, result_tag)
    """
    logical_name, read_path, cfg_dict = args
    
    try:
        # Reconstruct config in worker (pickling config objects can be flaky)
        # Note: We rely on the fact that L2PipelineConfig is a dataclass or picklable.
        # Ideally we pass the dict and reconstruct, or just pass the object if safe.
        # Here we assume the cfg object passed is safe.
        cfg: L2PipelineConfig = cfg_dict 
        
        # Instantiate a temporary trainer to access the _prepare_frames logic.
        # We invoke the static/class methods or helper methods.
        # Accessing private methods `_prepare_frames` is necessary to guarantee EXACT logic match.
        trainer = OmegaTrainerV3(cfg)
        
        # Load Frame
        # We don't need cache logic in worker; the OS file cache handles repeated reads best.
        read_file = Path(read_path)
        lf = pl.scan_parquet(str(read_file))
        df = lf.collect()
        
        if df.height == 0:
            return (logical_name, np.array([]), np.array([]), None, 0, "empty_input")

        # Apply Physics & Labels (The Heavy Lifting)
        # This calls `apply_recursive_physics` internally.
        df_processed = trainer._prepare_frames(df, cfg)
        
        if df_processed.height == 0:
            return (logical_name, np.array([]), np.array([]), None, 0, "empty_after_prepare")
        
        # Select Features
        missing = [c for c in trainer.feature_cols if c not in df_processed.columns]
        if missing:
            # Missing prepared feature columns indicates schema/compatibility break.
            return (logical_name, np.array([]), np.array([]), None, 0, "missing_features")

        X = df_processed.select(trainer.feature_cols).to_numpy()
        y = df_processed.select(trainer.label_col).to_numpy().ravel()
        
        # Weights (Structure Emphasis)
        w = None
        if cfg.train.sample_weight_topo and "topo_area" in df_processed.columns:
            topo = df_processed.select("topo_area").to_numpy().ravel()
            w = np.log1p(np.abs(topo))
            
        return (logical_name, X, y, w, df_processed.height, "ok")
        
    except Exception as e:
        # Return error as valid tuple but empty data
        # We print here because main process might not see worker stderr easily
        print(f"[Worker Error] {logical_name}: {e}", flush=True)
        return (logical_name, np.array([]), np.array([]), None, 0, f"worker_exception:{e}")

# --- Main Driver ---

class ParallelTrainerV31:
    def __init__(
        self,
        workers: int = 8,
        batch_size: int = 200000,
        file_list_path: Optional[Path] = None,
        max_files: Optional[int] = None,
        checkpoint_rows: int = 500000,
        memory_threshold: float = 88.0,
        progress_every_files: int = 20,
        planning_progress_every_lines: int = 250000,
        max_worker_errors: int = 0,
        status_json: Optional[Path] = None,
        stage_local: bool = False,
        stage_dir: Optional[Path] = None,
        stage_chunk_files: int = 24,
        stage_copy_workers: int = 1,
        cleanup_stage: bool = True,
    ):
        self.workers = workers
        self.batch_size = batch_size # Rows per SGD update
        self.checkpoint_interval = checkpoint_rows # Rows per checkpoint
        self.cfg = load_l2_pipeline_config()
        self.out_dir = Path("artifacts")
        self.out_dir.mkdir(exist_ok=True)
        self.file_list_path = file_list_path
        self.max_files = max_files
        self.memory_threshold = memory_threshold
        self.progress_every_files = max(1, int(progress_every_files))
        self.planning_progress_every_lines = max(10000, int(planning_progress_every_lines))
        self.max_worker_errors = max(0, int(max_worker_errors))
        self.status_json = status_json
        self.stage_local = bool(stage_local)
        self.stage_dir = stage_dir if stage_dir is not None else Path("D:/Omega_train_stage")
        self.stage_chunk_files = max(1, int(stage_chunk_files))
        self.stage_copy_workers = max(1, int(stage_copy_workers))
        self.cleanup_stage = bool(cleanup_stage)
        self._status_write_errors: int = 0
        self._stage_copy_sec_total: float = 0.0
        self._stage_copy_files_total: int = 0
        self._stage_copy_failures: int = 0
        
        # State
        self.model = SGDClassifier(loss="log_loss", penalty="l2", alpha=1e-4, average=True)
        self.scaler = StandardScaler()
        self.processed_files: Set[str] = set()
        self.total_rows = 0
        self.last_checkpoint_rows = 0
        self._latest_checkpoint: str = ""
        self._run_started_at: float = time.time()
        self._manifest_scanned_total: int = 0
        self._manifest_selected_total: int = 0
        
        # Features follow OmegaTrainerV3 config-driven selection.
        self.feature_cols = list(OmegaTrainerV3(self.cfg).feature_cols)
        if self.stage_local:
            self.stage_dir.mkdir(parents=True, exist_ok=True)
            if self.cleanup_stage:
                for stale in self.stage_dir.glob("chunk_*"):
                    if stale.is_dir():
                        shutil.rmtree(stale, ignore_errors=True)

    def _emit_status(self, **kwargs) -> None:
        if self.status_json is None:
            return
        payload = {
            "stage": "train",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "workers": self.workers,
            "batch_rows": self.batch_size,
            "checkpoint_rows": self.checkpoint_interval,
            "memory_threshold": self.memory_threshold,
            "stage_local": self.stage_local,
            "stage_dir": str(self.stage_dir) if self.stage_local else "",
            "stage_chunk_files": self.stage_chunk_files,
            "stage_copy_workers": self.stage_copy_workers,
            "cleanup_stage": self.cleanup_stage,
            "total_rows": self.total_rows,
            "processed_files_total": len(self.processed_files),
            "latest_checkpoint": self._latest_checkpoint,
            "elapsed_sec": max(0.0, time.time() - self._run_started_at),
            "status_write_errors": self._status_write_errors,
            "stage_copy_sec_total": self._stage_copy_sec_total,
            "stage_copy_files_total": self._stage_copy_files_total,
            "stage_copy_failures": self._stage_copy_failures,
            "stage_copy_avg_ms_per_file": (
                (1000.0 * self._stage_copy_sec_total / self._stage_copy_files_total)
                if self._stage_copy_files_total > 0 else 0.0
            ),
            "status": "running",
        }
        payload.update(kwargs)
        try:
            _write_json_atomic(self.status_json, payload)
        except Exception as exc:
            self._status_write_errors += 1
            if self._status_write_errors <= 3 or self._status_write_errors % 20 == 0:
                print(f"[Status Warn] status_json write failed: {exc}", flush=True)
        
    def load_latest_checkpoint(self):
        """Loads the standard sequential checkpoint to resume seamlessly."""
        ckpt_files = sorted(list(self.out_dir.glob("checkpoint_rows_*.pkl")), key=lambda p: p.stat().st_mtime, reverse=True)
        if not ckpt_files:
            print("[Init] No checkpoint found. Starting fresh.", flush=True)
            self._emit_status(status="ready", note="no_checkpoint_found")
            return

        latest = ckpt_files[0]
        print(f"[Init] Resuming from checkpoint: {latest.name}", flush=True)
        
        try:
            with open(latest, "rb") as f:
                payload = pickle.load(f)
            loaded_feature_cols = list(payload.get("feature_cols", []))
            if loaded_feature_cols and loaded_feature_cols != list(self.feature_cols):
                print("[Init] Feature space mismatch vs checkpoint. Resetting trainer state.", flush=True)
                self.model = SGDClassifier(loss="log_loss", penalty="l2", alpha=1e-4, average=True)
                self.scaler = StandardScaler()
                self.processed_files = set()
                self.total_rows = 0
                self.last_checkpoint_rows = 0
                self._latest_checkpoint = ""
                self._emit_status(status="ready", note="checkpoint_feature_mismatch_reset")
                return

            self.model = payload["model"]
            self.scaler = payload["scaler"]

            if "processed_files" in payload:
                self.processed_files = payload["processed_files"]
                self.total_rows = payload.get("total_rows", 0)
                self.last_checkpoint_rows = self.total_rows
                self._latest_checkpoint = str(latest)
                print(f"[Init] State restored. Processed {len(self.processed_files)} files, {self.total_rows:,} rows.", flush=True)
            else:
                print("[Init] Checkpoint loaded but lacks 'processed_files'. Features preserved, but file tracking reset.", flush=True)
            self._emit_status(status="ready", note="checkpoint_loaded")
                
        except Exception as e:
            print(f"[Init Error] Failed to load checkpoint: {e}", flush=True)
            self._emit_status(status="ready", note=f"checkpoint_load_failed: {e}")
            
    def save_checkpoint(self):
        """Saves in the EXACT format of OmegaTrainerV3 for compatibility."""
        name = f"checkpoint_rows_{self.total_rows}.pkl"
        path = self.out_dir / name
        
        payload = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_cols": self.feature_cols,
            "cfg": self.cfg,
            "processed_files": self.processed_files,
            "total_rows": self.total_rows
        }
        
        # Atomic write
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "wb") as f:
            pickle.dump(payload, f)
        tmp_path.replace(path)
        print(f"[Checkpoint] Saved {name} (Rows: {self.total_rows:,})", flush=True)
        self.last_checkpoint_rows = self.total_rows
        self._latest_checkpoint = str(path)
        self._emit_status(status="running", note="checkpoint_saved")

    def _copy_to_stage(self, src: Path, chunk_dir: Path) -> Tuple[str, str, Optional[str]]:
        dst = chunk_dir / src.name
        try:
            # copyfile avoids metadata-copy overhead on temporary stage files.
            shutil.copyfile(src, dst)
            return src.name, str(dst), None
        except Exception as exc:
            return src.name, str(src), str(exc)

    def _stage_chunk(self, chunk: Sequence[Path], chunk_id: int) -> Tuple[List[Tuple[str, str]], Optional[Path]]:
        if not self.stage_local:
            return [(p.name, str(p)) for p in chunk], None
        _memory_guard(self.memory_threshold)
        chunk_dir = self.stage_dir / f"chunk_{chunk_id:06d}"
        chunk_dir.mkdir(parents=True, exist_ok=True)
        staged: List[Tuple[str, str]] = []
        t0 = time.time()
        if self.stage_copy_workers <= 1 or len(chunk) <= 1:
            for src in chunk:
                logical_name, read_path, err = self._copy_to_stage(src, chunk_dir)
                if err is not None:
                    self._stage_copy_failures += 1
                    print(
                        f"[Stage Warn] copy failed for {src}: {err}. Fallback to source path.",
                        flush=True,
                    )
                staged.append((logical_name, read_path))
        else:
            max_workers = min(self.stage_copy_workers, len(chunk))
            with ThreadPoolExecutor(max_workers=max_workers) as tp:
                futures = [tp.submit(self._copy_to_stage, src, chunk_dir) for src in chunk]
                for fut in futures:
                    logical_name, read_path, err = fut.result()
                    if err is not None:
                        self._stage_copy_failures += 1
                        print(
                            f"[Stage Warn] copy failed for {logical_name}: {err}. Fallback to source path.",
                            flush=True,
                        )
                    staged.append((logical_name, read_path))
        elapsed = time.time() - t0
        self._stage_copy_sec_total += elapsed
        self._stage_copy_files_total += len(staged)
        print(
            f"[Stage] chunk={chunk_id}, files={len(staged)}, elapsed={elapsed:.1f}s, "
            f"copy_workers={self.stage_copy_workers}, dir={chunk_dir}",
            flush=True,
        )
        return staged, chunk_dir

    def _cleanup_chunk(self, chunk_dir: Optional[Path]) -> None:
        if not self.stage_local or not self.cleanup_stage or chunk_dir is None:
            return
        try:
            shutil.rmtree(chunk_dir, ignore_errors=True)
        except Exception as exc:
            print(f"[Cleanup Warn] {chunk_dir}: {exc}", flush=True)

    def _iter_manifest_task_chunks(self) -> Iterator[Tuple[List[Path], int, int]]:
        if self.file_list_path is None:
            return
        scanned = 0
        selected = 0
        chunk: List[Path] = []
        max_files = max(0, int(self.max_files)) if self.max_files is not None else None
        planning_started_at = time.time()
        with open(self.file_list_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip().lstrip("\ufeff")
                if not s:
                    continue
                scanned += 1
                if scanned % self.planning_progress_every_lines == 0:
                    elapsed = max(time.time() - planning_started_at, 1.0)
                    print(
                        f"[Plan] scanning manifest... scanned={scanned:,} "
                        f"selected={selected:,} speed={scanned/elapsed:.0f} lines/s",
                        flush=True,
                    )
                    self._emit_status(
                        status="running",
                        phase="planning_scan",
                        files_scanned=scanned,
                        files_selected=selected,
                    )
                if os.path.basename(s) in self.processed_files:
                    continue
                chunk.append(Path(s))
                selected += 1
                if max_files is not None and selected >= max_files:
                    yield chunk, scanned, selected
                    chunk = []
                    break
                if len(chunk) >= self.stage_chunk_files:
                    yield chunk, scanned, selected
                    chunk = []
        if chunk:
            yield chunk, scanned, selected
        self._manifest_scanned_total = scanned
        self._manifest_selected_total = selected

    def train(self):
        self._run_started_at = time.time()

        classes = np.array([-1, 0, 1])
        if self.cfg.train.drop_neutral_labels:
            classes = np.array([-1, 1])

        # Buffers for SGD batching
        X_buf: List[np.ndarray] = []
        y_buf: List[np.ndarray] = []
        w_buf: List[np.ndarray] = []
        rows_in_buf = 0

        files_done_in_run = 0
        files_with_rows = 0
        files_empty_or_skipped = 0
        files_schema_errors = 0
        files_worker_errors = 0
        files_total = 0
        files_selected = 0
        chunk_count = 0

        # 1) Discovery / chunk iterator selection
        if self.file_list_path is not None:
            print(f"[Plan] loading file list (stream mode): {self.file_list_path}", flush=True)
            self._emit_status(
                status="running",
                phase="planning_scan",
                files_scanned=0,
                files_selected=0,
            )
            task_chunk_iter = self._iter_manifest_task_chunks()
        else:
            dirs = discover_l2_dirs()
            all_files: List[Path] = []
            for d in dirs:
                all_files.extend(sorted(list(d.rglob("*.parquet"))))
            files_total = len(all_files)
            
            # Enforce Train Split
            if self.cfg.split.train_years:
                allowed = [str(y) for y in self.cfg.split.train_years]
                all_files = [f for f in all_files if any(f.name.startswith(y) for y in allowed)]
                print(f"[Plan] Enforcing Train Split: Years {allowed}. Files remaining: {len(all_files)}", flush=True)
            
            tasks = [f for f in all_files if f.name not in self.processed_files]
            if self.max_files is not None:
                tasks = tasks[: max(0, int(self.max_files))]
            files_selected = len(tasks)
            print(
                f"[Plan] Total files: {files_total:,}. Processed: {len(self.processed_files):,}. "
                f"Remaining: {files_selected:,}.",
                flush=True
            )
            self._emit_status(
                status="running",
                phase="discovery_complete",
                files_total=files_total,
                files_selected=files_selected,
                files_remaining=files_selected,
                files_done_in_run=0,
                files_with_rows=0,
            )
            if not tasks:
                print("[Done] No new files to process.", flush=True)
                self._emit_status(
                    status="completed",
                    phase="done_no_tasks",
                    files_total=files_total,
                    files_selected=0,
                    files_remaining=0,
                )
                return
            task_chunk_iter = (
                (tasks[i : i + self.stage_chunk_files], files_total, files_selected)
                for i in range(0, len(tasks), self.stage_chunk_files)
            )

        # 2) Parallel execution
        print(f"[Start] Launching {self.workers} workers...", flush=True)
        with mp.Pool(processes=self.workers, initializer=worker_init) as pool:
            start_time = time.time()
            for chunk_id, (chunk, running_total, running_selected) in enumerate(task_chunk_iter):
                chunk_count += 1
                files_total = max(files_total, int(running_total))
                files_selected = max(files_selected, int(running_selected))
                if self.file_list_path is not None and chunk_count == 1:
                    print(
                        f"[Plan] file-list stream selected first chunk. "
                        f"scanned={files_total:,}, selected={files_selected:,}",
                        flush=True,
                    )
                    self._emit_status(
                        status="running",
                        phase="discovery_complete",
                        files_total=files_total,
                        files_selected=files_selected,
                        files_remaining=files_selected,
                        files_done_in_run=0,
                        files_with_rows=0,
                    )
                _memory_guard(self.memory_threshold)
                staged, chunk_dir = self._stage_chunk(chunk, chunk_id)
                task_args = ((name, read_path, self.cfg) for name, read_path in staged)
                for fname, X_part, y_part, w_part, n_rows, result_tag in pool.imap_unordered(
                    process_file_v31, task_args, chunksize=1
                ):
                    files_done_in_run += 1
                    if n_rows > 0:
                        X_buf.append(X_part)
                        y_buf.append(y_part)
                        if w_part is not None:
                            w_buf.append(w_part)
                        rows_in_buf += n_rows
                        files_with_rows += 1
                    else:
                        if result_tag in ("empty_input", "empty_after_prepare"):
                            files_empty_or_skipped += 1
                        elif result_tag == "missing_features":
                            files_schema_errors += 1
                            print(f"[Schema Error] {fname}: missing features after prepare.", flush=True)
                        else:
                            files_worker_errors += 1
                            print(f"[Worker Error] {fname}: {result_tag}", flush=True)

                    # Keep resume semantics: processed files are tracked even when empty/skipped.
                    self.processed_files.add(fname)

                    if files_done_in_run % self.progress_every_files == 0:
                        elapsed = max(time.time() - start_time, 1.0)
                        done_den = max(files_selected, files_done_in_run)
                        print(
                            f"  Files: {files_done_in_run:,}/{done_den:,} | "
                            f"Rows(total): {self.total_rows:,} | Rows(buf): {rows_in_buf:,} | "
                            f"Speed: {self.total_rows / elapsed:.1f} rows/s",
                            flush=True,
                        )
                        self._emit_status(
                            status="running",
                            phase="in_progress",
                            files_total=files_total,
                            files_selected=files_selected,
                            files_remaining=max(files_selected - files_done_in_run, 0),
                            files_done_in_run=files_done_in_run,
                            files_with_rows=files_with_rows,
                            files_empty_or_skipped=files_empty_or_skipped,
                            files_schema_errors=files_schema_errors,
                            files_worker_errors=files_worker_errors,
                            rows_buffered=rows_in_buf,
                        )

                    # Batch fit gate
                    if rows_in_buf >= self.batch_size:
                        _memory_guard(self.memory_threshold)
                        X_batch = np.vstack(X_buf)
                        y_batch = np.concatenate(y_buf)
                        w_batch = np.concatenate(w_buf) if w_buf else None
                        self.scaler.partial_fit(X_batch)
                        X_scaled = self.scaler.transform(X_batch)
                        self.model.partial_fit(
                            X_scaled, y_batch, classes=classes, sample_weight=w_batch
                        )
                        self.total_rows += rows_in_buf
                        X_buf, y_buf, w_buf = [], [], []
                        rows_in_buf = 0
                        elapsed = time.time() - start_time
                        speed = self.total_rows / max(1.0, elapsed)
                        print(
                            f"  Rows: {self.total_rows:,} | Speed: {speed:.1f} rows/s | "
                            f"Files: {len(self.processed_files)}",
                            flush=True
                        )
                        self._emit_status(
                            status="running",
                            phase="batch_fit",
                            files_total=files_total,
                            files_selected=files_selected,
                            files_remaining=max(files_selected - files_done_in_run, 0),
                            files_done_in_run=files_done_in_run,
                            files_with_rows=files_with_rows,
                            files_empty_or_skipped=files_empty_or_skipped,
                            files_schema_errors=files_schema_errors,
                            files_worker_errors=files_worker_errors,
                            rows_buffered=rows_in_buf,
                        )
                        if self.total_rows - self.last_checkpoint_rows >= self.checkpoint_interval:
                            self.save_checkpoint()
                self._cleanup_chunk(chunk_dir)

        if self.file_list_path is not None:
            files_total = max(files_total, self._manifest_scanned_total)
            files_selected = max(files_selected, self._manifest_selected_total)
            print(
                f"[Plan] file-list mode complete: scanned={self._manifest_scanned_total:,}, "
                f"selected={self._manifest_selected_total:,}",
                flush=True
            )
            if chunk_count == 0:
                print("[Done] No new files to process.", flush=True)
                self._emit_status(
                    status="completed",
                    phase="done_no_tasks",
                    files_total=files_total,
                    files_selected=0,
                    files_remaining=0,
                    files_done_in_run=0,
                    files_with_rows=0,
                    files_empty_or_skipped=0,
                    files_schema_errors=0,
                    files_worker_errors=0,
                    rows_buffered=0,
                )
                return

        # Final flush
        if rows_in_buf > 0:
            _memory_guard(self.memory_threshold)
            X_batch = np.vstack(X_buf)
            y_batch = np.concatenate(y_buf)
            w_batch = np.concatenate(w_buf) if w_buf else None
            self.scaler.partial_fit(X_batch)
            X_scaled = self.scaler.transform(X_batch)
            self.model.partial_fit(X_scaled, y_batch, classes=classes, sample_weight=w_batch)
            self.total_rows += rows_in_buf
            self.save_checkpoint()

        # v5.1 C6: always flush a final checkpoint if tail updates are newer than last checkpoint.
        if self.total_rows > self.last_checkpoint_rows:
            self.save_checkpoint()

        hard_errors = files_schema_errors + files_worker_errors
        if hard_errors > self.max_worker_errors:
            msg = (
                f"worker/schema errors exceeded max_worker_errors={self.max_worker_errors}: "
                f"schema={files_schema_errors}, worker={files_worker_errors}"
            )
            self._emit_status(
                status="failed",
                phase="failed",
                files_total=files_total,
                files_selected=files_selected,
                files_remaining=max(files_selected - files_done_in_run, 0),
                files_done_in_run=files_done_in_run,
                files_with_rows=files_with_rows,
                files_empty_or_skipped=files_empty_or_skipped,
                files_schema_errors=files_schema_errors,
                files_worker_errors=files_worker_errors,
                rows_buffered=0,
                error=msg,
            )
            raise RuntimeError(msg)

        print("=== Training Complete ===", flush=True)
        self._emit_status(
            status="completed",
            phase="complete",
            files_total=files_total,
            files_selected=files_selected,
            files_remaining=max(files_selected - files_done_in_run, 0),
            files_done_in_run=files_done_in_run,
            files_with_rows=files_with_rows,
            files_empty_or_skipped=files_empty_or_skipped,
            files_schema_errors=files_schema_errors,
            files_worker_errors=files_worker_errors,
            rows_buffered=0,
        )

def parse_args() -> argparse.Namespace:
    cpu = os.cpu_count() or 8
    default_workers = max(2, min(20, cpu - 2))
    p = argparse.ArgumentParser(description="Parallel Trainer for OMEGA v31/v40 feature stack")
    p.add_argument("--workers", type=int, default=default_workers)
    p.add_argument("--batch-rows", type=int, default=200000)
    p.add_argument("--checkpoint-rows", type=int, default=500000)
    p.add_argument("--file-list", type=str, default=None)
    p.add_argument("--max-files", type=int, default=None)
    p.add_argument("--memory-threshold", type=float, default=88.0)
    p.add_argument("--progress-every-files", type=int, default=20)
    p.add_argument("--planning-progress-every-lines", type=int, default=250000)
    p.add_argument("--max-worker-errors", type=int, default=0)
    p.add_argument("--status-json", type=str, default=None)
    stage_group = p.add_mutually_exclusive_group()
    stage_group.add_argument("--stage-local", dest="stage_local", action="store_true")
    stage_group.add_argument("--no-stage-local", dest="stage_local", action="store_false")
    p.add_argument("--stage-dir", type=str, default="D:/Omega_train_stage")
    p.add_argument("--stage-chunk-files", type=int, default=24)
    p.add_argument("--stage-copy-workers", type=int, default=1)
    p.add_argument("--no-cleanup-stage", action="store_true")
    p.add_argument("--no-resume", action="store_true")
    p.set_defaults(stage_local=True)
    return p.parse_args()


if __name__ == "__main__":
    mp.freeze_support()
    args = parse_args()
    trainer = ParallelTrainerV31(
        workers=max(1, int(args.workers)),
        batch_size=max(1000, int(args.batch_rows)),
        file_list_path=Path(args.file_list) if args.file_list else None,
        max_files=args.max_files,
        checkpoint_rows=max(1000, int(args.checkpoint_rows)),
        memory_threshold=float(args.memory_threshold),
        progress_every_files=max(1, int(args.progress_every_files)),
        planning_progress_every_lines=max(10000, int(args.planning_progress_every_lines)),
        max_worker_errors=max(0, int(args.max_worker_errors)),
        status_json=Path(args.status_json) if args.status_json else None,
        stage_local=bool(args.stage_local),
        stage_dir=Path(args.stage_dir),
        stage_chunk_files=max(1, int(args.stage_chunk_files)),
        stage_copy_workers=max(1, int(args.stage_copy_workers)),
        cleanup_stage=not bool(args.no_cleanup_stage),
    )

    if not args.no_resume:
        trainer.load_latest_checkpoint()
    trainer.train()

