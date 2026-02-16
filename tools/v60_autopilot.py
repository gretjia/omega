#!/usr/bin/env python3
"""
v60 full-stack autopilot:
frame monitor -> GCS sync -> Vertex training -> Vertex backtest.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SSH_PS = REPO_ROOT / ".codex" / "skills" / "omega-run-ops" / "scripts" / "ssh_ps.py"


def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO_ROOT, check=check, capture_output=True, text=True)


def run_stream(cmd: list[str], log_fn) -> str:
    log_fn("+ " + " ".join(cmd))
    proc = subprocess.Popen(
        cmd,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    out = []
    assert proc.stdout is not None
    for line in proc.stdout:
        out.append(line)
        log_fn(line.rstrip("\n"))
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
    return "".join(out)


def detect_git_hash() -> str:
    try:
        res = run(["git", "rev-parse", "--short", "HEAD"])
        return res.stdout.strip()
    except Exception:
        return ""


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for line in f if line.strip() and not line.strip().startswith("#"))


def parse_prefixed_int(text: str, key: str) -> int:
    m = re.search(rf"{re.escape(key)}=(\d+)", text)
    return int(m.group(1)) if m else -1


def parse_prefixed_str(text: str, key: str) -> str:
    m = re.search(rf"{re.escape(key)}=([^\r\n]+)", text)
    return m.group(1).strip() if m else ""


def linux_done_count(git_hash: str) -> int:
    cmd = [
        "ssh",
        "linux1-lx",
        (
            "find /omega_pool/parquet_data/v52/frames/host=linux1 -maxdepth 1 -type f "
            f"-name '*_{git_hash}.parquet.done' 2>/dev/null | wc -l"
        ),
    ]
    res = run(cmd)
    try:
        return int(res.stdout.strip().splitlines()[-1])
    except Exception:
        return -1


def windows_done_and_state(git_hash: str, task_name: str) -> tuple[int, str]:
    ps = (
        "$ProgressPreference='SilentlyContinue'; "
        "$done=(Get-ChildItem -Path 'D:\\Omega_frames\\v52\\frames\\host=windows1' "
        f"-Filter '*_{git_hash}.parquet.done' -ErrorAction SilentlyContinue).Count; "
        f"$state=(Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue).State; "
        "Write-Output ('done_windows=' + $done); "
        "Write-Output ('task_state=' + $state)"
    )
    res = run([sys.executable, str(SSH_PS), "windows1-w1", "--command", ps], check=False)
    text = (res.stdout or "") + "\n" + (res.stderr or "")
    return parse_prefixed_int(text, "done_windows"), parse_prefixed_str(text, "task_state")


def collect_diag(task_name: str) -> dict:
    linux_log = run(
        [
            "ssh",
            "linux1-lx",
            "cd /home/zepher/work/Omega_vNext && tail -n 20 audit/_pipeline_frame.frame03.nohup.log 2>/dev/null || true",
        ],
        check=False,
    ).stdout
    win_ps = (
        "$ProgressPreference='SilentlyContinue'; "
        f"$state=(Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue).State; "
        "Write-Output ('task_state=' + $state); "
        "Get-Content 'D:\\work\\Omega_vNext\\audit\\_pipeline_frame.log' -Tail 20 -ErrorAction SilentlyContinue"
    )
    win_out = run([sys.executable, str(SSH_PS), "windows1-w1", "--command", win_ps], check=False).stdout
    return {"linux_tail": linux_log.strip(), "windows_tail": (win_out or "").strip()}


def gcs_count(bucket: str, host: str, git_hash: str) -> int:
    pattern = f"{bucket}/omega/v52/frames/host={host}/*_{git_hash}.parquet"
    res = run(["bash", "-lc", f"gcloud storage ls '{pattern}' 2>/dev/null | wc -l"], check=False)
    try:
        return int((res.stdout or "0").strip().splitlines()[-1])
    except Exception:
        return -1


def main() -> int:
    ap = argparse.ArgumentParser(description="OMEGA v60 full-stack autopilot")
    ap.add_argument("--hash", default="", help="Frame git short hash (default: local HEAD)")
    ap.add_argument("--bucket", default="gs://omega_v52")
    ap.add_argument("--windows-expected", type=int, default=0)
    ap.add_argument("--linux-expected", type=int, default=0)
    ap.add_argument("--poll-sec", type=int, default=180)
    ap.add_argument("--stall-sec", type=int, default=1800)
    ap.add_argument("--windows-task-name", default="Omega_v52_frame03")
    ap.add_argument("--train-years", default="2023,2024")
    ap.add_argument("--test-years", default="2025,2026")
    ap.add_argument("--train-machine-type", default="c2-standard-60")
    ap.add_argument("--backtest-machine-type", default="n1-standard-8")
    args = ap.parse_args()

    git_hash = args.hash.strip() or detect_git_hash()
    if not git_hash:
        raise SystemExit("Cannot determine git hash. Pass --hash explicitly.")

    win_expected = int(args.windows_expected) or count_lines(REPO_ROOT / "audit/runtime/v52/shard_windows1.txt")
    lin_expected = int(args.linux_expected) or count_lines(REPO_ROOT / "audit/runtime/v52/shard_linux.txt")
    status_path = REPO_ROOT / f"audit/runtime/v52/autopilot_{git_hash}.status.json"
    log_path = REPO_ROOT / f"audit/runtime/v52/autopilot_{git_hash}.log"
    status_path.parent.mkdir(parents=True, exist_ok=True)

    def log(msg: str) -> None:
        line = f"[{now_ts()}] {msg}"
        print(line, flush=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    state = {
        "started_at": now_ts(),
        "git_hash": git_hash,
        "bucket": args.bucket,
        "windows_expected": win_expected,
        "linux_expected": lin_expected,
        "stage": "monitor_frame",
        "frame": {},
        "upload": {},
        "train": {},
        "backtest": {},
    }

    def flush_state() -> None:
        tmp = status_path.with_suffix(status_path.suffix + ".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(status_path)

    flush_state()
    log(
        f"Autopilot started hash={git_hash} expected windows={win_expected} linux={lin_expected} "
        f"poll={args.poll_sec}s stall={args.stall_sec}s"
    )

    # Stage 1: monitor framing
    last_total = -1
    last_progress_ts = time.time()
    while True:
        lin = linux_done_count(git_hash)
        win, win_state = windows_done_and_state(git_hash, args.windows_task_name)
        total = max(0, lin) + max(0, win)

        state["frame"] = {
            "linux_done": lin,
            "windows_done": win,
            "windows_task_state": win_state,
            "updated_at": now_ts(),
        }
        flush_state()
        log(f"Frame progress linux={lin}/{lin_expected} windows={win}/{win_expected} task={win_state or 'unknown'}")

        if lin >= lin_expected and win >= win_expected:
            log("Frame stage complete.")
            break

        if total > last_total:
            last_total = total
            last_progress_ts = time.time()
        elif time.time() - last_progress_ts >= float(args.stall_sec):
            diag = collect_diag(args.windows_task_name)
            state["frame"]["stall_diag"] = diag
            flush_state()
            log("Progress stalled; diagnostics captured in status json.")
            last_progress_ts = time.time()

        time.sleep(max(10, int(args.poll_sec)))

    # Stage 2: upload
    state["stage"] = "sync_gcs"
    flush_state()
    for host in ("linux1", "windows1"):
        log(f"Sync start host={host}")
        run_stream(
            [
                sys.executable,
                "tools/mac_gateway_sync.py",
                "--bucket",
                args.bucket,
                "--host",
                host,
                "--hash",
                git_hash,
            ],
            log,
        )
        state["upload"][host] = {"synced_at": now_ts()}
        flush_state()

    lin_gcs = gcs_count(args.bucket, "linux1", git_hash)
    win_gcs = gcs_count(args.bucket, "windows1", git_hash)
    state["upload"]["gcs_counts"] = {"linux1": lin_gcs, "windows1": win_gcs, "checked_at": now_ts()}
    flush_state()
    log(f"GCS counts linux1={lin_gcs} windows1={win_gcs}")

    # Stage 3: Vertex training
    state["stage"] = "vertex_train"
    run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    train_output_uri = f"{args.bucket}/staging/models/v6/{run_id}_{git_hash}"
    data_pattern = f"{args.bucket}/omega/v52/frames/host=*/*_{git_hash}.parquet"
    state["train"]["output_uri"] = train_output_uri
    state["train"]["data_pattern"] = data_pattern
    flush_state()
    log("Submitting Vertex train job (sync mode)...")
    run_stream(
        [
            sys.executable,
            "tools/submit_vertex_sweep.py",
            "--script",
            "tools/run_vertex_xgb_train.py",
            "--machine-type",
            args.train_machine_type,
            "--sync",
            f"--script-arg=--data-pattern={data_pattern}",
            f"--script-arg=--train-years={args.train_years}",
            f"--script-arg=--output-uri={train_output_uri}",
        ],
        log,
    )
    state["train"]["completed_at"] = now_ts()
    state["train"]["model_uri"] = f"{train_output_uri}/omega_v6_xgb_final.pkl"
    flush_state()

    # Stage 4: Vertex backtest
    state["stage"] = "vertex_backtest"
    backtest_output_uri = f"{args.bucket}/staging/backtest/v6/{run_id}_{git_hash}/backtest_metrics.json"
    state["backtest"]["output_uri"] = backtest_output_uri
    flush_state()
    log("Submitting Vertex backtest job (sync mode)...")
    run_stream(
        [
            sys.executable,
            "tools/submit_vertex_sweep.py",
            "--script",
            "tools/run_cloud_backtest.py",
            "--machine-type",
            args.backtest_machine_type,
            "--sync",
            f"--script-arg=--data-pattern={data_pattern}",
            f"--script-arg=--test-years={args.test_years}",
            f"--script-arg=--model-uri={state['train']['model_uri']}",
            f"--script-arg=--output-uri={backtest_output_uri}",
        ],
        log,
    )
    state["backtest"]["completed_at"] = now_ts()

    state["stage"] = "completed"
    state["completed_at"] = now_ts()
    flush_state()
    log("Autopilot completed end-to-end.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
