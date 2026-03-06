#!/usr/bin/env python3
"""
v62 Stage2 targeted resume runner.

Purpose:
- Isolate Stage2 execution into bounded subprocess batches.
- Enforce per-subprocess timeout so one pathological chunk cannot block the host.
- Maintain explicit pending/failed ledgers for deterministic resume.

This runner does not change feature logic/output schema. It only changes
execution orchestration and failure isolation.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROCESS_CHUNK_BATCH_CODE = """
import sys
from pathlib import Path
from tools.stage2_physics_compute import process_chunk

out_dir = sys.argv[1]
files = sys.argv[2:]
any_fail = False

for f in files:
    name = Path(f).name
    print(f"__BATCH_START__ {name}", flush=True)
    r = process_chunk({"l1_file": f, "out_dir": out_dir})
    msg = r.get("message") if isinstance(r, dict) else str(r)
    print(msg, flush=True)

    done = Path(out_dir, f"{name}.done").exists()
    ok = done or (bool(r.get("ok")) if isinstance(r, dict) else False)
    print(f"__BATCH_{'OK' if ok else 'FAIL'}__ {name}", flush=True)
    any_fail = any_fail or (not ok)

raise SystemExit(0 if not any_fail else 2)
""".strip()


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _resolve_path(value: str, repo_root: Path) -> Path:
    p = Path(value)
    if p.is_absolute():
        return p
    return repo_root / p


def _append_line(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _enforce_linux_heavy_slice() -> None:
    if sys.platform != "linux":
        return
    if os.environ.get("OMEGA_STAGE2_ALLOW_USER_SLICE") == "1":
        return

    cgroup_path = Path("/proc/self/cgroup")
    if not cgroup_path.exists():
        return

    content = cgroup_path.read_text(encoding="utf-8", errors="replace")
    if "heavy-workload.slice" not in content:
        raise SystemExit(
            "[FATAL] stage2 targeted runner must run in heavy-workload.slice "
            "(set OMEGA_STAGE2_ALLOW_USER_SLICE=1 to override)."
        )


def _chunk_paths(items: list[Path], chunk_size: int):
    size = max(1, int(chunk_size))
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _parse_batch_markers(stdout: str, stderr: str) -> tuple[set[str], set[str], set[str]]:
    started: set[str] = set()
    ok: set[str] = set()
    failed: set[str] = set()
    for raw in f"{stdout}\n{stderr}".splitlines():
        line = raw.strip()
        if line.startswith("__BATCH_START__ "):
            started.add(line[len("__BATCH_START__ ") :].strip())
        elif line.startswith("__BATCH_OK__ "):
            ok.add(line[len("__BATCH_OK__ ") :].strip())
        elif line.startswith("__BATCH_FAIL__ "):
            failed.add(line[len("__BATCH_FAIL__ ") :].strip())
    return started, ok, failed


def _run_file_batch(
    *,
    python_bin: str,
    repo_root: Path,
    l1_files: list[Path],
    out_dir: Path,
    timeout_sec: int,
) -> tuple[int, str, str, bool]:
    if not l1_files:
        return 0, "", "", False

    cmd = [
        python_bin,
        "-u",
        "-c",
        PROCESS_CHUNK_BATCH_CODE,
        str(out_dir),
        *[str(p) for p in l1_files],
    ]
    try:
        cp = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        return cp.returncode, cp.stdout or "", cp.stderr or "", False
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ""
        stderr = e.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return 124, stdout, stderr, True


def _log_multiline(log_file: Path, text: str) -> None:
    if not text:
        return
    for line in text.rstrip().splitlines():
        _append_line(log_file, line)


def main() -> int:
    ap = argparse.ArgumentParser(description="v62 Stage2 targeted timeout-isolated runner")
    ap.add_argument("--input-dir", required=True, help="Directory containing Base_L1 parquet files")
    ap.add_argument("--output-dir", required=True, help="Directory for Feature_L2 parquet outputs")
    ap.add_argument("--timeout-sec", type=int, default=900, help="Per-subprocess timeout seconds")
    ap.add_argument(
        "--log-file",
        default="audit/stage2_targeted_resume.log",
        help="Runner log file (absolute or repo-relative)",
    )
    ap.add_argument(
        "--fail-file",
        default="audit/stage2_targeted_failed.txt",
        help="Failed file list (absolute or repo-relative)",
    )
    ap.add_argument(
        "--reset-fail-file",
        action="store_true",
        help="Reset fail ledger before this run (default keeps/extends previous failures).",
    )
    ap.add_argument(
        "--pending-file",
        default="audit/stage2_pending_list.txt",
        help="Pending file list (absolute or repo-relative)",
    )
    ap.add_argument(
        "--python-bin",
        default=sys.executable,
        help="Python interpreter used for subprocess runs",
    )
    ap.add_argument("--max-files", type=int, default=0, help="Optional cap for pending files (0 means all)")
    ap.add_argument(
        "--files-per-process",
        type=int,
        default=max(1, int(os.environ.get("OMEGA_STAGE2_FILES_PER_PROCESS", "1"))),
        help="How many input files to process in one subprocess (default: 1)",
    )
    ap.add_argument(
        "--allow-user-slice",
        action="store_true",
        help="Allow running outside heavy-workload.slice on Linux",
    )
    args = ap.parse_args()

    if args.allow_user_slice:
        os.environ["OMEGA_STAGE2_ALLOW_USER_SLICE"] = "1"

    repo_root = Path(__file__).resolve().parents[1]
    input_dir = _resolve_path(args.input_dir, repo_root)
    output_dir = _resolve_path(args.output_dir, repo_root)
    log_file = _resolve_path(args.log_file, repo_root)
    fail_file = _resolve_path(args.fail_file, repo_root)
    pending_file = _resolve_path(args.pending_file, repo_root)

    _enforce_linux_heavy_slice()

    output_dir.mkdir(parents=True, exist_ok=True)
    fail_file.parent.mkdir(parents=True, exist_ok=True)
    pending_file.parent.mkdir(parents=True, exist_ok=True)

    existing_failed: set[str] = set()
    if fail_file.exists() and not args.reset_fail_file:
        existing_failed = {
            line.strip()
            for line in fail_file.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()
        }
    if args.reset_fail_file:
        fail_file.write_text("", encoding="utf-8")

    _append_line(log_file, f"=== TARGETED_RESUME_START {_now()} ===")
    _append_line(log_file, f"PYTHON_EXE={args.python_bin}")
    _append_line(log_file, f"TIMEOUT_SEC={args.timeout_sec}")
    _append_line(log_file, f"FILES_PER_PROCESS={max(1, args.files_per_process)}")
    _append_line(log_file, f"FAILED_CARRY_IN={len(existing_failed)}")

    inputs = sorted(p for p in input_dir.glob("*.parquet") if p.is_file())
    pending: list[Path] = []
    for src in inputs:
        done = output_dir / f"{src.name}.done"
        out_path = output_dir / src.name
        if done.exists() and not out_path.exists():
            done.unlink()
            _append_line(log_file, f"STALE_DONE_CLEARED={src.name}")
        if not done.exists() and src.name not in existing_failed:
            pending.append(src)

    if args.max_files > 0:
        pending = pending[: args.max_files]

    pending_file.write_text(
        "\n".join(p.name for p in pending) + ("\n" if pending else ""),
        encoding="utf-8",
    )
    _append_line(log_file, f"INPUT_TOTAL={len(inputs)}")
    _append_line(log_file, f"PENDING_TOTAL={len(pending)}")

    failed_names: set[str] = set(existing_failed)
    run_failures = 0
    files_per_process = max(1, args.files_per_process)
    batches = list(_chunk_paths(pending, files_per_process))
    _append_line(log_file, f"BATCH_TOTAL={len(batches)}")

    for batch_idx, batch in enumerate(batches, 1):
        batch_total = len(batches)
        batch_names = [p.name for p in batch]
        if batch_names:
            _append_line(
                log_file,
                f"[batch {batch_idx}/{batch_total}] START n={len(batch)} "
                f"first={batch_names[0]} last={batch_names[-1]}",
            )
        else:
            _append_line(log_file, f"[batch {batch_idx}/{batch_total}] START n=0")

        for src in batch:
            tmp_path = output_dir / f"{src.name}.tmp"
            try:
                tmp_path.unlink()
            except FileNotFoundError:
                pass

        rc, stdout, stderr, timed_out = _run_file_batch(
            python_bin=args.python_bin,
            repo_root=repo_root,
            l1_files=batch,
            out_dir=output_dir,
            timeout_sec=args.timeout_sec,
        )

        if timed_out:
            _append_line(
                log_file,
                f"[batch {batch_idx}/{batch_total}] TIMEOUT after {args.timeout_sec}s",
            )
        _log_multiline(log_file, stdout)
        _log_multiline(log_file, stderr)

        started, marker_ok, marker_fail = _parse_batch_markers(stdout, stderr)
        _append_line(
            log_file,
            f"[batch {batch_idx}/{batch_total}] END rc={rc} started={len(started)} "
            f"ok_markers={len(marker_ok)} fail_markers={len(marker_fail)}",
        )

        for src in batch:
            done_path = output_dir / f"{src.name}.done"
            if done_path.exists():
                _append_line(log_file, f"[batch {batch_idx}/{batch_total}] OK {src.name}")
                continue

            if timed_out and src.name not in started:
                # Do not poison fail ledger for files not started before timeout.
                _append_line(
                    log_file,
                    f"[batch {batch_idx}/{batch_total}] DEFER not-started {src.name}",
                )
                continue

            _append_line(log_file, f"[batch {batch_idx}/{batch_total}] FAIL rc={rc} {src.name}")
            run_failures += 1
            if src.name not in failed_names:
                failed_names.add(src.name)
                _append_line(fail_file, src.name)

    done_now = len(list(output_dir.glob("*.parquet.done")))
    _append_line(log_file, f"DONE_NOW={done_now}")
    _append_line(log_file, f"FAILED_TOTAL={len(failed_names)}")
    _append_line(log_file, f"RUN_FAILED={run_failures}")
    _append_line(log_file, f"=== TARGETED_RESUME_END {_now()} ===")
    return 0 if run_failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
