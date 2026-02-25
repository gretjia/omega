#!/usr/bin/env python3
"""
v62 Stage2 targeted resume runner.

Purpose:
- Isolate each Stage2 file in its own Python subprocess.
- Enforce per-file timeout so one pathological file cannot block the whole host.
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


PROCESS_CHUNK_CODE = (
    "import sys; "
    "from tools.stage2_physics_compute import process_chunk; "
    "print(process_chunk({'l1_file': sys.argv[1], 'out_dir': sys.argv[2]}), flush=True)"
)


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


def _run_one_file(
    *,
    python_bin: str,
    repo_root: Path,
    l1_file: Path,
    out_dir: Path,
    timeout_sec: int,
) -> tuple[int, str, str, bool]:
    cmd = [
        python_bin,
        "-u",
        "-c",
        PROCESS_CHUNK_CODE,
        str(l1_file),
        str(out_dir),
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
    ap.add_argument("--timeout-sec", type=int, default=900, help="Per-file timeout seconds")
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
        "--pending-file",
        default="audit/stage2_pending_list.txt",
        help="Pending file list (absolute or repo-relative)",
    )
    ap.add_argument(
        "--python-bin",
        default=sys.executable,
        help="Python interpreter used for per-file subprocess runs",
    )
    ap.add_argument("--max-files", type=int, default=0, help="Optional cap for pending files (0 means all)")
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

    _append_line(log_file, f"=== TARGETED_RESUME_START {_now()} ===")
    _append_line(log_file, f"PYTHON_EXE={args.python_bin}")
    _append_line(log_file, f"TIMEOUT_SEC={args.timeout_sec}")

    inputs = sorted(p for p in input_dir.glob("*.parquet") if p.is_file())
    pending: list[Path] = []
    for src in inputs:
        done = output_dir / f"{src.name}.done"
        if not done.exists():
            pending.append(src)

    if args.max_files > 0:
        pending = pending[: args.max_files]

    pending_file.write_text(
        "\n".join(p.name for p in pending) + ("\n" if pending else ""),
        encoding="utf-8",
    )
    fail_file.write_text("", encoding="utf-8")

    _append_line(log_file, f"INPUT_TOTAL={len(inputs)}")
    _append_line(log_file, f"PENDING_TOTAL={len(pending)}")

    failed_names: list[str] = []
    total = len(pending)

    for idx, src in enumerate(pending, 1):
        done_path = output_dir / f"{src.name}.done"
        tmp_path = output_dir / f"{src.name}.tmp"
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass

        _append_line(log_file, f"[{idx}/{total}] START {src.name}")
        rc, stdout, stderr, timed_out = _run_one_file(
            python_bin=args.python_bin,
            repo_root=repo_root,
            l1_file=src,
            out_dir=output_dir,
            timeout_sec=args.timeout_sec,
        )

        if timed_out:
            _append_line(log_file, f"[{idx}/{total}] TIMEOUT {src.name} after {args.timeout_sec}s")
        _log_multiline(log_file, stdout)
        _log_multiline(log_file, stderr)

        ok = done_path.exists() and rc == 0
        if ok:
            _append_line(log_file, f"[{idx}/{total}] OK {src.name}")
        else:
            _append_line(log_file, f"[{idx}/{total}] FAIL rc={rc} {src.name}")
            failed_names.append(src.name)
            _append_line(fail_file, src.name)

    done_now = len(list(output_dir.glob("*.parquet.done")))
    _append_line(log_file, f"DONE_NOW={done_now}")
    _append_line(log_file, f"FAILED_TOTAL={len(failed_names)}")
    _append_line(log_file, f"=== TARGETED_RESUME_END {_now()} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

