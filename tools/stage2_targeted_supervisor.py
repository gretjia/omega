#!/usr/bin/env python3
"""
v62 Stage2 crash-tolerant supervisor.

Purpose:
- Repeatedly run `stage2_targeted_resume.py` in small batches.
- If a run exits with no observable progress, force-append the last started file
  into the fail ledger so the next run can continue.

This only changes orchestration/failure isolation. It does not change feature
math, schema, or per-file compute logic.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


START_RE = re.compile(r"^\[\d+/\d+\] START (.+\.parquet)$")
OK_RE = re.compile(r"^\[\d+/\d+\] OK (.+\.parquet)$")
FAIL_RE = re.compile(r"^\[\d+/\d+\] FAIL rc=.* (.+\.parquet)$")
TIMEOUT_RE = re.compile(r"^\[\d+/\d+\] TIMEOUT (.+\.parquet) after")


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _resolve_path(value: str, repo_root: Path) -> Path:
    p = Path(value)
    return p if p.is_absolute() else (repo_root / p)


def _append_line(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _count_files(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.glob(pattern))


def _read_fail_set(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    }


def _append_unique_fail(path: Path, file_name: str, known: set[str]) -> bool:
    if file_name in known:
        return False
    _append_line(path, file_name)
    known.add(file_name)
    return True


def _parse_log_window(log_file: Path, old_size: int) -> tuple[str | None, set[str]]:
    if not log_file.exists():
        return None, set()
    data = log_file.read_bytes()
    if old_size < 0 or old_size > len(data):
        old_size = 0
    text = data[old_size:].decode("utf-8", errors="replace")
    last_started: str | None = None
    terminal: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        m = START_RE.match(line)
        if m:
            last_started = m.group(1)
            continue
        m = OK_RE.match(line)
        if m:
            terminal.add(m.group(1))
            continue
        m = FAIL_RE.match(line)
        if m:
            terminal.add(m.group(1))
            continue
        m = TIMEOUT_RE.match(line)
        if m:
            terminal.add(m.group(1))
            continue
    return last_started, terminal


def _build_runner_cmd(
    *,
    python_bin: str,
    runner_script: Path,
    input_dir: Path,
    output_dir: Path,
    timeout_sec: int,
    max_files: int,
    log_file: Path,
    fail_file: Path,
    pending_file: Path,
    allow_user_slice: bool,
) -> list[str]:
    cmd = [
        python_bin,
        "-u",
        str(runner_script),
        "--input-dir",
        str(input_dir),
        "--output-dir",
        str(output_dir),
        "--timeout-sec",
        str(timeout_sec),
        "--max-files",
        str(max_files),
        "--log-file",
        str(log_file),
        "--fail-file",
        str(fail_file),
        "--pending-file",
        str(pending_file),
        "--python-bin",
        python_bin,
    ]
    if allow_user_slice:
        cmd.append("--allow-user-slice")
    return cmd


def main() -> int:
    ap = argparse.ArgumentParser(description="Crash-tolerant supervisor for stage2_targeted_resume")
    ap.add_argument("--input-dir", required=True, help="Directory containing Base_L1 parquet files")
    ap.add_argument("--output-dir", required=True, help="Directory containing Feature_L2 outputs")
    ap.add_argument("--timeout-sec", type=int, default=60, help="Per-file timeout passed to targeted runner")
    ap.add_argument("--max-files", type=int, default=1, help="Files per targeted runner invocation")
    ap.add_argument("--sleep-sec", type=float, default=1.0, help="Sleep between iterations")
    ap.add_argument("--max-iterations", type=int, default=0, help="0 means run until remaining=0")
    ap.add_argument("--python-bin", default=sys.executable, help="Python interpreter for child runner")
    ap.add_argument(
        "--runner-script",
        default="tools/stage2_targeted_resume.py",
        help="Path to targeted runner script (absolute or repo-relative)",
    )
    ap.add_argument(
        "--log-file",
        default="audit/stage2_targeted_resume.log",
        help="Runner log path (absolute or repo-relative)",
    )
    ap.add_argument(
        "--fail-file",
        default="audit/stage2_targeted_failed.txt",
        help="Fail ledger path (absolute or repo-relative)",
    )
    ap.add_argument(
        "--pending-file",
        default="audit/stage2_pending_list.txt",
        help="Pending list path (absolute or repo-relative)",
    )
    ap.add_argument(
        "--state-log",
        default="audit/stage2_targeted_supervisor.log",
        help="Supervisor own state log (absolute or repo-relative)",
    )
    ap.add_argument(
        "--allow-user-slice",
        action="store_true",
        help="Pass --allow-user-slice to targeted runner (Linux only).",
    )
    args = ap.parse_args()

    if args.max_files <= 0:
        raise SystemExit("--max-files must be >= 1 for supervisor mode.")

    repo_root = Path(__file__).resolve().parents[1]
    input_dir = _resolve_path(args.input_dir, repo_root)
    output_dir = _resolve_path(args.output_dir, repo_root)
    runner_script = _resolve_path(args.runner_script, repo_root)
    log_file = _resolve_path(args.log_file, repo_root)
    fail_file = _resolve_path(args.fail_file, repo_root)
    pending_file = _resolve_path(args.pending_file, repo_root)
    state_log = _resolve_path(args.state_log, repo_root)

    _append_line(
        state_log,
        f"=== SUPERVISOR_START {_now()} timeout={args.timeout_sec} max_files={args.max_files} ===",
    )

    iteration = 0
    while True:
        if args.max_iterations > 0 and iteration >= args.max_iterations:
            _append_line(state_log, f"[{_now()}] STOP max_iterations={args.max_iterations}")
            break

        iteration += 1
        total = _count_files(input_dir, "*.parquet")
        done = _count_files(output_dir, "*.parquet.done")
        fail_set = _read_fail_set(fail_file)
        remaining = max(total - done - len(fail_set), 0)
        _append_line(
            state_log,
            f"[{_now()}] ITER={iteration} BEFORE total={total} done={done} failed={len(fail_set)} remaining={remaining}",
        )
        if remaining <= 0:
            _append_line(state_log, f"[{_now()}] COMPLETE remaining=0")
            break

        old_log_size = log_file.stat().st_size if log_file.exists() else 0
        cmd = _build_runner_cmd(
            python_bin=args.python_bin,
            runner_script=runner_script,
            input_dir=input_dir,
            output_dir=output_dir,
            timeout_sec=args.timeout_sec,
            max_files=args.max_files,
            log_file=log_file,
            fail_file=fail_file,
            pending_file=pending_file,
            allow_user_slice=args.allow_user_slice,
        )
        cp = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        _append_line(state_log, f"[{_now()}] ITER={iteration} RUN_RC={cp.returncode}")

        if cp.stdout:
            for line in cp.stdout.rstrip().splitlines()[-20:]:
                _append_line(state_log, f"[child-stdout] {line}")
        if cp.stderr:
            for line in cp.stderr.rstrip().splitlines()[-20:]:
                _append_line(state_log, f"[child-stderr] {line}")

        done_after = _count_files(output_dir, "*.parquet.done")
        fail_set_after = _read_fail_set(fail_file)

        progressed = (done_after > done) or (len(fail_set_after) > len(fail_set))
        if not progressed:
            last_started, terminal = _parse_log_window(log_file, old_log_size)
            if (
                last_started
                and last_started not in fail_set_after
                and last_started not in terminal
                and not (output_dir / f"{last_started}.done").exists()
            ):
                appended = _append_unique_fail(fail_file, last_started, fail_set_after)
                if appended:
                    _append_line(
                        state_log,
                        f"[{_now()}] ITER={iteration} FORCE_FAIL_APPEND {last_started} (no progress, rc={cp.returncode})",
                    )

        total2 = _count_files(input_dir, "*.parquet")
        done2 = _count_files(output_dir, "*.parquet.done")
        fail2 = len(_read_fail_set(fail_file))
        rem2 = max(total2 - done2 - fail2, 0)
        _append_line(
            state_log,
            f"[{_now()}] ITER={iteration} AFTER total={total2} done={done2} failed={fail2} remaining={rem2}",
        )

        if rem2 <= 0:
            _append_line(state_log, f"[{_now()}] COMPLETE remaining=0")
            break

        if args.sleep_sec > 0:
            time.sleep(args.sleep_sec)

    _append_line(state_log, f"=== SUPERVISOR_END {_now()} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
