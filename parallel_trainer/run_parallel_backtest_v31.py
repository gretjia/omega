"""
run_parallel_backtest_v31.py

High-performance Parallel Backtest Driver for OMEGA v5.0 (Holographic Damper).
(Filename retained for pipeline compatibility; Logic aligned with v5.0)

Executes the "Shadow Mode" Audit on Out-of-Sample data using the trained policy.

Architecture:
- Loads the trained `checkpoint_rows_*.pkl`.
- Uses Multiprocessing to apply recursive physics (Bottleneck) and Model Prediction in parallel.
- Aggregates PnL and Physics Metrics (SNR, Orthogonality).

Usage:
    python parallel_trainer/run_parallel_backtest_v31.py
"""

import sys
import os
import time
import pickle
import json
import numpy as np
import polars as pl
import argparse
from pathlib import Path
from typing import Iterator, List, Tuple, Dict, Optional, Sequence
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import psutil
import shutil

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config import L2PipelineConfig, load_l2_pipeline_config
from omega_core.trainer import OmegaTrainerV3, evaluate_frames, evaluate_dod


def _sanitize_for_json(value):
    if isinstance(value, dict):
        return {k: _sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_for_json(v) for v in value]
    if isinstance(value, float):
        if not np.isfinite(value):
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
    if last_exc is not None:
        # Windows share mode may block os.replace(). Fallback to direct overwrite.
        try:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(safe_payload, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            return
        except Exception:
            raise last_exc
    raise RuntimeError(f"atomic json write failed: {path}")


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
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

# Global cache for worker process
_WORKER_POLICY_CACHE = None

def get_worker_policy(policy_path: str):
    global _WORKER_POLICY_CACHE
    if _WORKER_POLICY_CACHE is None:
        with open(policy_path, "rb") as f:
            _WORKER_POLICY_CACHE = pickle.load(f)
    return _WORKER_POLICY_CACHE

def process_backtest_file(args) -> Dict:
    """
    Worker function:
    1. Loads Parquet Frame.
    2. Re-applies Physics.
    3. Generates Model Predictions.
    """
    logical_name, read_path, policy_path, ret_clip_abs_override = args
    
    try:
        # Load Policy (Cached per process)
        policy_data = get_worker_policy(policy_path)
        policy_cfg = policy_data["cfg"]
        model = policy_data["model"]
        scaler = policy_data["scaler"]
        feature_cols = policy_data["feature_cols"]
        
        # 1. Load Data
        df = pl.read_parquet(str(read_path))
        if df.height == 0:
            return {"file": str(logical_name), "empty": True, "rows": 0, "trades": 0, "pnl": 0.0}

        # 2. Apply Physics & Labeling
        # If any downstream feature or ret_k label is missing, recompute the full
        # physics/label pipeline to make file format self-consistent.
        has_ret_k = "ret_k" in df.columns
        missing_features = [c for c in feature_cols if c not in df.columns]

        if missing_features or not has_ret_k:
            try:
                trainer_tool = OmegaTrainerV3(policy_cfg)
                df = trainer_tool._prepare_frames(df, policy_cfg)
            except Exception as exc:
                return {
                    "error": f"Physics/label prep failed: {exc}",
                    "file": str(logical_name),
                }
        
        if df.height == 0:
            return {"file": str(logical_name), "empty": True, "rows": 0, "trades": 0, "pnl": 0.0}

        # 3. Model Prediction
        try:
            X = df.select(feature_cols).to_numpy()
            X_scaled = scaler.transform(X)
            probs = model.predict_proba(X_scaled)[:, 1]
        except Exception as e:
            return {"error": f"Prediction failed: {e}", "file": str(logical_name)}
        
        # 4. Metrics & PnL Simulation
        # Eval Metrics
        metrics = evaluate_frames(df, policy_cfg)
        
        # Simulation: Use decision_margin from config
        # Default is 0.05, which yields 0.55/0.45
        margin = float(getattr(policy_cfg.train, "decision_margin", 0.05))
        upper_thr = 0.5 + margin
        lower_thr = 0.5 - margin
        cfg_clip = getattr(getattr(policy_cfg, "validation", object()), "backtest_ret_clip_abs", None)
        if ret_clip_abs_override is not None:
            ret_clip_abs = float(ret_clip_abs_override)
        elif cfg_clip is not None:
            ret_clip_abs = float(cfg_clip)
        else:
            ret_clip_abs = None

        pnl = 0.0
        trades = 0
        if "ret_k" in df.columns:
            # Longs
            long_mask = probs > upper_thr
            short_mask = probs < lower_thr
            
            ret_k = df["ret_k"].to_numpy()
            
            # Optional robustness clipping comes from config or CLI override.
            if ret_clip_abs is not None and ret_clip_abs > 0.0:
                ret_eval = np.clip(ret_k, -ret_clip_abs, ret_clip_abs)
            else:
                ret_eval = ret_k

            pnl += np.sum(ret_eval[long_mask])
            pnl -= np.sum(ret_eval[short_mask])
            trades += (np.sum(long_mask) + np.sum(short_mask))
        else:
             return {"error": "ret_k still missing after prepare_frames", "file": str(logical_name)}

        return {
            "file": str(logical_name),
            "metrics": metrics,
            "pnl": float(pnl),
            "trades": int(trades),
            "rows": df.height
        }

    except Exception:
        import traceback
        return {"error": traceback.format_exc(), "file": str(logical_name)}

# --- Main Driver ---

class ParallelBacktester:
    def __init__(
        self,
        policy_path: str,
        data_roots: List[Path],
        workers: int = 12,
        file_list_path: Optional[Path] = None,
        max_files: Optional[int] = None,
        state_file: Optional[Path] = None,
        status_json: Optional[Path] = None,
        save_every_files: int = 20,
        state_save_every_files: int = 200,
        planning_progress_every_lines: int = 250000,
        memory_threshold: float = 88.0,
        no_resume: bool = False,
        max_file_errors: int = 0,
        fail_on_audit_failed: bool = True,
        ret_clip_abs_override: Optional[float] = None,
        stage_local: bool = False,
        stage_dir: Optional[Path] = None,
        stage_chunk_files: int = 24,
        stage_copy_workers: int = 1,
        cleanup_stage: bool = True,
    ):
        self.policy_path = policy_path
        self.data_roots = data_roots
        self.workers = workers
        self.file_list_path = file_list_path
        self.max_files = max_files
        self.state_file = state_file
        self.status_json = status_json
        self.save_every_files = max(1, int(save_every_files))
        self.state_save_every_files = max(1, int(state_save_every_files))
        self.planning_progress_every_lines = max(10000, int(planning_progress_every_lines))
        self.memory_threshold = float(memory_threshold)
        self.no_resume = no_resume
        self.max_file_errors = max(0, int(max_file_errors))
        self.fail_on_audit_failed = bool(fail_on_audit_failed)
        self.ret_clip_abs_override = ret_clip_abs_override
        self.stage_local = bool(stage_local)
        self.stage_dir = stage_dir if stage_dir is not None else Path("D:/Omega_backtest_stage")
        self.stage_chunk_files = max(1, int(stage_chunk_files))
        self.stage_copy_workers = max(1, int(stage_copy_workers))
        self.cleanup_stage = bool(cleanup_stage)
        self._status_write_errors: int = 0
        self._state_write_errors: int = 0
        self._stage_copy_sec_total: float = 0.0
        self._stage_copy_files_total: int = 0
        self._stage_copy_failures: int = 0
        self.started_at = time.time()
        self.processed_files = set()
        self.total_pnl = 0.0
        self.total_trades = 0
        self.total_rows = 0
        self.metric_sums = {
            "Topo_SNR": 0.0,
            "Orthogonality": 0.0,
            "Vector_Alignment": 0.0,
            "n_valid": 0,
        }
        self.files_processed_in_run = 0
        self.error_count = 0
        self.total_tasks = 0
        
        print(f"[Init] Loading Policy: {policy_path}")
        with open(policy_path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.feature_cols = data["feature_cols"]
            self.cfg = data["cfg"] # Type: L2PipelineConfig
        cfg_clip = getattr(getattr(self.cfg, "validation", object()), "backtest_ret_clip_abs", None)
        if self.ret_clip_abs_override is not None:
            self.ret_clip_abs = float(self.ret_clip_abs_override)
        elif cfg_clip is not None:
            self.ret_clip_abs = float(cfg_clip)
        else:
            self.ret_clip_abs = None
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
            "stage": "backtest",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "running",
            "workers": self.workers,
            "planning_progress_every_lines": self.planning_progress_every_lines,
            "policy": self.policy_path,
            "memory_threshold": self.memory_threshold,
            "stage_local": self.stage_local,
            "stage_dir": str(self.stage_dir) if self.stage_local else "",
            "stage_chunk_files": self.stage_chunk_files,
            "stage_copy_workers": self.stage_copy_workers,
            "cleanup_stage": self.cleanup_stage,
            "save_every_files": self.save_every_files,
            "state_save_every_files": self.state_save_every_files,
            "total_tasks": self.total_tasks,
            "files_processed_in_run": self.files_processed_in_run,
            "processed_files_total": len(self.processed_files),
            "error_count": self.error_count,
            "total_rows": self.total_rows,
            "total_trades": self.total_trades,
            "total_pnl": self.total_pnl,
            "elapsed_sec": max(0.0, time.time() - self.started_at),
            "state_file": str(self.state_file) if self.state_file else "",
            "ret_clip_abs": self.ret_clip_abs,
            "max_file_errors": self.max_file_errors,
            "fail_on_audit_failed": self.fail_on_audit_failed,
            "status_write_errors": self._status_write_errors,
            "state_write_errors": self._state_write_errors,
            "stage_copy_sec_total": self._stage_copy_sec_total,
            "stage_copy_files_total": self._stage_copy_files_total,
            "stage_copy_failures": self._stage_copy_failures,
            "stage_copy_avg_ms_per_file": (
                (1000.0 * self._stage_copy_sec_total / self._stage_copy_files_total)
                if self._stage_copy_files_total > 0 else 0.0
            ),
        }
        payload.update(kwargs)
        try:
            _write_json_atomic(self.status_json, payload)
        except Exception as exc:
            self._status_write_errors += 1
            if self._status_write_errors <= 3 or self._status_write_errors % 20 == 0:
                print(f"[Status Warn] status_json write failed: {exc}", flush=True)

    def _load_state(self) -> None:
        if self.no_resume or self.state_file is None or (not self.state_file.exists()):
            return
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            self.processed_files = set(state.get("processed_files", []))
            self.total_pnl = float(state.get("total_pnl", 0.0))
            self.total_trades = int(state.get("total_trades", 0))
            self.total_rows = int(state.get("total_rows", 0))
            self.metric_sums = state.get("metric_sums", self.metric_sums)
            self.error_count = int(state.get("error_count", 0))
            print(
                f"[Resume] Loaded backtest state: files={len(self.processed_files)}, "
                f"rows={self.total_rows:,}, trades={self.total_trades:,}, pnl={self.total_pnl:.6f}",
                flush=True
            )
        except Exception as exc:
            print(f"[Resume Warn] Failed to load state file: {exc}", flush=True)

    def _save_state(self, completed: bool = False) -> None:
        if self.state_file is None:
            return
        payload = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed": bool(completed),
            "policy": self.policy_path,
            # Avoid O(n log n) sort for very large state files.
            "processed_files": list(self.processed_files),
            "total_pnl": self.total_pnl,
            "total_trades": self.total_trades,
            "total_rows": self.total_rows,
            "metric_sums": self.metric_sums,
            "error_count": self.error_count,
            "total_tasks": self.total_tasks,
            "files_processed_in_run": self.files_processed_in_run,
        }
        try:
            _write_json_atomic(self.state_file, payload)
        except Exception as exc:
            self._state_write_errors += 1
            if self._state_write_errors <= 3 or self._state_write_errors % 20 == 0:
                print(f"[State Warn] state write failed: {exc}", flush=True)

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

    def _iter_file_list_chunks(self) -> Iterator[Tuple[List[Path], int, int]]:
        if self.file_list_path is None:
            return
        scanned = 0
        selected = 0
        chunk: List[Path] = []
        max_files = max(0, int(self.max_files)) if self.max_files is not None else None
        started_at = time.time()
        with open(self.file_list_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip().lstrip("\ufeff")
                if not s:
                    continue
                scanned += 1
                if scanned % self.planning_progress_every_lines == 0:
                    elapsed = max(time.time() - started_at, 1.0)
                    print(
                        f"[Plan] scanning manifest... scanned={scanned:,} selected={selected:,} "
                        f"speed={scanned/elapsed:.0f} lines/s",
                        flush=True,
                    )
                    self._emit_status(
                        status="running",
                        phase="planning_scan",
                        files_scanned=scanned,
                        files_selected=selected,
                    )
                p = Path(s)
                if p.name in self.processed_files:
                    continue
                chunk.append(p)
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
            
    def run(self):
        self.started_at = time.time()
        self._load_state()
        # 1. Discovery
        stream_mode = self.file_list_path is not None
        scanned_total = 0
        if stream_mode:
            print(f"[Plan] loading file list (stream mode): {self.file_list_path}", flush=True)
            self._emit_status(
                status="running",
                phase="planning_scan",
                files_scanned=0,
                files_selected=0,
            )
            chunk_iter = self._iter_file_list_chunks()
        else:
            all_files = []
            for d in self.data_roots:
                if d.exists():
                    all_files.extend(list(d.rglob("*.parquet")))
            all_files = sorted(all_files)
            
            # Enforce Test Split
            split = self.cfg.split
            allowed_years = [str(y) for y in getattr(split, "test_years", [])]
            allowed_months = [str(m) for m in getattr(split, "test_year_months", [])]
            
            if allowed_years or allowed_months:
                def is_test_file(path: Path) -> bool:
                    name = path.name
                    if any(name.startswith(y) for y in allowed_years): return True
                    if any(name.startswith(m) for m in allowed_months): return True
                    return False
                all_files = [f for f in all_files if is_test_file(f)]
                print(f"[Plan] Enforcing Test Split: Years {allowed_years}, Months {allowed_months}. Files: {len(all_files)}", flush=True)

            if self.max_files is not None:
                all_files = all_files[: max(0, int(self.max_files))]
            tasks_files = [p for p in all_files if p.name not in self.processed_files]
            self.total_tasks = len(tasks_files)
            scanned_total = len(all_files)
            print(
                f"[Plan] Found {len(all_files)} files for backtest. "
                f"Already done={len(self.processed_files)}. Run now={self.total_tasks}.",
                flush=True
            )
            self._emit_status(
                status="running",
                phase="discovery_complete",
                files_remaining=self.total_tasks,
            )
            if self.total_tasks == 0:
                print("[Done] No files to process.", flush=True)
                self._save_state(completed=True)
                self._emit_status(status="completed", phase="done_no_tasks", files_remaining=0)
                return
            chunk_iter = (
                (tasks_files[i : i + self.stage_chunk_files], scanned_total, self.total_tasks)
                for i in range(0, len(tasks_files), self.stage_chunk_files)
            )

        # 2. Parallel execution
        print(f"[Start] Launching {self.workers} workers...", flush=True)
        start_time = time.time()
        last_log_rows = 0
        files_processed = 0
        chunk_count = 0
        with mp.Pool(processes=self.workers, initializer=worker_init) as pool:
            for chunk_id, (chunk, running_scanned, running_selected) in enumerate(chunk_iter):
                chunk_count += 1
                scanned_total = max(scanned_total, int(running_scanned))
                self.total_tasks = max(self.total_tasks, int(running_selected))
                if stream_mode and chunk_count == 1:
                    print(
                        f"[Plan] file-list stream selected first chunk. "
                        f"scanned={scanned_total:,}, selected={self.total_tasks:,}",
                        flush=True,
                    )
                    self._emit_status(
                        status="running",
                        phase="discovery_complete",
                        files_scanned=scanned_total,
                        files_selected=self.total_tasks,
                        files_remaining=self.total_tasks,
                    )
                _memory_guard(self.memory_threshold)
                staged, chunk_dir = self._stage_chunk(chunk, chunk_id)
                tasks = [
                    (logical_name, read_path, self.policy_path, self.ret_clip_abs)
                    for logical_name, read_path in staged
                ]
                for res in pool.map(process_backtest_file, tasks):
                    files_processed += 1
                    self.files_processed_in_run += 1
                    _memory_guard(self.memory_threshold)
                    if "error" in res:
                        print(f"  [Warn] {res.get('file', '?')}: {res['error']}", flush=True)
                        self.error_count += 1
                        self._emit_status(
                            status="running",
                            phase="in_progress",
                            files_remaining=max(self.total_tasks - self.files_processed_in_run, 0),
                        )
                        if self.files_processed_in_run % self.state_save_every_files == 0:
                            self._save_state(completed=False)
                        continue
                    
                    if not res:
                        continue
                    file_key = str(res.get("file", ""))
                    if file_key:
                        self.processed_files.add(file_key)
                    if res.get("empty"):
                        continue
                    
                    # Aggregate PnL
                    self.total_pnl += res["pnl"]
                    self.total_trades += res["trades"]
                    self.total_rows += res["rows"]
                    
                    # Aggregate Metrics
                    m = res["metrics"]
                    if np.isfinite(m.get("Topo_SNR", np.nan)):
                        self.metric_sums["Topo_SNR"] += m["Topo_SNR"]
                        self.metric_sums["Orthogonality"] += m["Orthogonality"]
                        self.metric_sums["Vector_Alignment"] += m["Vector_Alignment"]
                        self.metric_sums["n_valid"] += 1
                    
                    if self.total_rows - last_log_rows >= 500000:
                        elapsed = time.time() - start_time
                        fps = files_processed / elapsed if elapsed > 0 else 0
                        print(
                            f"  Progress: {self.total_rows:,} rows | Files: {files_processed:,}/{self.total_tasks:,} | "
                            f"PnL: {self.total_pnl:.4f} | Trades: {self.total_trades:,} | Speed: {fps:.1f} f/s",
                            flush=True,
                        )
                        last_log_rows = self.total_rows

                    if self.files_processed_in_run % self.state_save_every_files == 0:
                        self._save_state(completed=False)
                    if self.files_processed_in_run % self.save_every_files == 0:
                        self._emit_status(
                            status="running",
                            phase="in_progress",
                            files_remaining=max(self.total_tasks - self.files_processed_in_run, 0),
                        )
                self._cleanup_chunk(chunk_dir)

        if stream_mode:
            if chunk_count == 0:
                print("[Done] No files to process.")
                self._save_state(completed=True)
                self._emit_status(
                    status="completed",
                    phase="done_no_tasks",
                    files_scanned=scanned_total,
                    files_selected=0,
                    files_remaining=0,
                )
                return
            print(
                f"[Plan] file-list mode complete: scanned={scanned_total:,}, "
                f"selected={self.total_tasks:,}"
            )

        if self.error_count > self.max_file_errors:
            msg = (
                f"backtest file errors exceeded max_file_errors={self.max_file_errors}: "
                f"errors={self.error_count}"
            )
            self._save_state(completed=False)
            self._emit_status(
                status="failed",
                phase="failed",
                files_remaining=max(self.total_tasks - self.files_processed_in_run, 0),
                error=msg,
            )
            raise RuntimeError(msg)

        # 3. Final Report
        n = max(1, self.metric_sums["n_valid"])
        avg_snr = self.metric_sums["Topo_SNR"] / n
        avg_orth = self.metric_sums["Orthogonality"] / n
        avg_align = self.metric_sums["Vector_Alignment"] / n
        
        print("\n" + "="*50, flush=True)
        print("OMEGA v3.1 PARALLEL BACKTEST REPORT", flush=True)
        print("="*50, flush=True)
        if self.file_list_path is not None:
            print("Data Source Mode: manifest(file-list)", flush=True)
            print(f"Manifest Path: {self.file_list_path}", flush=True)
            print(f"Manifest Selected Files: {self.total_tasks}", flush=True)
            print(f"Configured Data Roots: {[str(d) for d in self.data_roots]}", flush=True)
        else:
            print(f"Data Sources: {[str(d) for d in self.data_roots]}", flush=True)
        print(f"Total Rows  : {self.total_rows:,}", flush=True)
        print(f"Total Trades: {self.total_trades:,}", flush=True)
        print(f"Total PnL   : {self.total_pnl:.6f} (Unit: Return k)", flush=True)
        print(f"Ret Clip Abs: {self.ret_clip_abs}", flush=True)
        print("-" * 50, flush=True)
        print("PHYSICS AUDIT METRICS (DoD)", flush=True)
        print(f"Topo SNR         : {avg_snr:.4f}  (Target > {self.cfg.validation.topo_snr_min})", flush=True)
        print(f"Orthogonality    : {avg_orth:.4f}  (Target < {self.cfg.validation.orthogonality_max_abs})", flush=True)
        print(f"Vector Alignment : {avg_align:.4f} (Target > {self.cfg.validation.vector_alignment_min})", flush=True)
        
        # Validation Logic
        passed = True
        if avg_snr <= float(self.cfg.validation.topo_snr_min): passed = False
        if abs(avg_orth) >= float(self.cfg.validation.orthogonality_max_abs): passed = False
        if avg_align <= float(self.cfg.validation.vector_alignment_min): passed = False
        
        status = "PASSED" if passed else "FAILED"
        print("-" * 50, flush=True)
        print(f"FINAL AUDIT STATUS: {status}", flush=True)
        print("="*50, flush=True)
        if (status == "FAILED") and self.fail_on_audit_failed:
            msg = "final audit status is FAILED and fail_on_audit_failed=true"
            self._save_state(completed=False)
            self._emit_status(
                status="failed",
                phase="failed",
                files_remaining=0,
                final_audit_status=status,
                avg_snr=avg_snr,
                avg_orth=avg_orth,
                avg_align=avg_align,
                error=msg,
            )
            raise RuntimeError(msg)

        self._save_state(completed=True)
        self._emit_status(
            status="completed",
            phase="complete",
            files_remaining=0,
            final_audit_status=status,
            avg_snr=avg_snr,
            avg_orth=avg_orth,
            avg_align=avg_align,
        )

def parse_args() -> argparse.Namespace:
    cpu = os.cpu_count() or 8
    default_workers = max(2, min(18, cpu - 2))
    p = argparse.ArgumentParser(description="Parallel backtest for OMEGA v31/v40 features")
    p.add_argument("--policy", type=str, default="")
    p.add_argument("--workers", type=int, default=default_workers)
    p.add_argument("--data-dir", action="append", default=None, help="Repeatable parquet directory")
    p.add_argument("--file-list", type=str, default=None)
    p.add_argument("--max-files", type=int, default=None)
    p.add_argument("--state-file", type=str, default=None)
    p.add_argument("--status-json", type=str, default=None)
    p.add_argument("--save-every-files", type=int, default=20)
    p.add_argument("--state-save-every-files", type=int, default=200)
    p.add_argument("--planning-progress-every-lines", type=int, default=250000)
    p.add_argument("--memory-threshold", type=float, default=88.0)
    p.add_argument("--max-file-errors", type=int, default=0)
    stage_group = p.add_mutually_exclusive_group()
    stage_group.add_argument("--stage-local", dest="stage_local", action="store_true")
    stage_group.add_argument("--no-stage-local", dest="stage_local", action="store_false")
    p.add_argument("--stage-dir", type=str, default="D:/Omega_backtest_stage")
    p.add_argument("--stage-chunk-files", type=int, default=24)
    p.add_argument("--stage-copy-workers", type=int, default=1)
    p.add_argument("--no-cleanup-stage", action="store_true")
    p.add_argument("--no-resume", action="store_true")
    p.add_argument("--ret-clip-abs", type=float, default=None, help="Optional backtest return clip abs override")
    audit_group = p.add_mutually_exclusive_group()
    audit_group.add_argument("--fail-on-audit-failed", dest="fail_on_audit_failed", action="store_true")
    audit_group.add_argument("--allow-audit-failed", dest="fail_on_audit_failed", action="store_false")
    p.set_defaults(stage_local=True, fail_on_audit_failed=True)
    return p.parse_args()


if __name__ == "__main__":
    mp.freeze_support()
    args = parse_args()

    policy = args.policy.strip() if args.policy else ""
    if policy:
        if not Path(policy).exists():
            print(f"Policy not found: {policy}")
            sys.exit(1)
    else:
        avail = sorted(
            list(Path("artifacts").glob("checkpoint_rows_*.pkl")),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if avail:
            policy = str(avail[0])
        else:
            print("No policy found in artifacts/")
            sys.exit(1)

    if args.data_dir:
        data_roots = [Path(d) for d in args.data_dir]
    else:
        data_roots = []
        root = Path("data")
        for d in root.glob("level2_frames_*"):
            if d.is_dir():
                data_roots.append(d)

    print(f"Running Parallel Backtest on: {[d.name for d in data_roots]}")
    bt = ParallelBacktester(
        policy,
        data_roots,
        workers=max(1, int(args.workers)),
        file_list_path=Path(args.file_list) if args.file_list else None,
        max_files=args.max_files,
        state_file=Path(args.state_file) if args.state_file else None,
        status_json=Path(args.status_json) if args.status_json else None,
        save_every_files=max(1, int(args.save_every_files)),
        state_save_every_files=max(1, int(args.state_save_every_files)),
        planning_progress_every_lines=max(10000, int(args.planning_progress_every_lines)),
        memory_threshold=float(args.memory_threshold),
        no_resume=bool(args.no_resume),
        max_file_errors=max(0, int(args.max_file_errors)),
        fail_on_audit_failed=bool(args.fail_on_audit_failed),
        ret_clip_abs_override=args.ret_clip_abs,
        stage_local=bool(args.stage_local),
        stage_dir=Path(args.stage_dir),
        stage_chunk_files=max(1, int(args.stage_chunk_files)),
        stage_copy_workers=max(1, int(args.stage_copy_workers)),
        cleanup_stage=not bool(args.no_cleanup_stage),
    )
    try:
        bt.run()
    except Exception as exc:
        try:
            bt._emit_status(status="failed", phase="exception", error=str(exc))
        except Exception:
            pass
        raise
