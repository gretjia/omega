#!/usr/bin/env python3
"""
OMEGA v6 edge-cloud orchestrator.

Responsibilities:
1. Dispatch framing jobs from Mac controller to Windows/Linux workers via SSH.
2. Sync framed parquet artifacts from workers to GCS.
3. Trigger Vertex AI XGBoost training on the synced signal data.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


_WIN_ABS_RE = re.compile(r"^[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class WorkerSpec:
    name: str
    host: str
    platform: str  # linux|windows
    repo_root: str
    python_exec: str
    config_path: str
    archive_list: str
    task_name: str | None = None


def _run(cmd: list[str], dry_run: bool = False) -> None:
    print("+", " ".join(shlex.quote(c) for c in cmd), flush=True)
    if dry_run:
        return
    subprocess.run(cmd, check=True)


def _ssh(host: str, remote_cmd: str, dry_run: bool = False) -> None:
    _run(["ssh", host, remote_cmd], dry_run=dry_run)


def _parse_workers(path: str) -> list[WorkerSpec]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    out: list[WorkerSpec] = []
    for item in raw:
        out.append(
            WorkerSpec(
                name=str(item["name"]),
                host=str(item["host"]),
                platform=str(item["platform"]).lower(),
                repo_root=str(item["repo_root"]),
                python_exec=str(item.get("python_exec", "python3")),
                config_path=str(item["config_path"]),
                archive_list=str(item["archive_list"]),
                task_name=item.get("task_name"),
            )
        )
    return out


def _is_windows_abs(path: str) -> bool:
    return bool(_WIN_ABS_RE.match(path)) or path.startswith("\\\\")


def _resolve_remote_path(worker: WorkerSpec, p: str) -> str:
    if worker.platform == "windows":
        if _is_windows_abs(p):
            return p.replace("/", "\\")
        return (Path(worker.repo_root) / p).as_posix().replace("/", "\\")
    if p.startswith("/"):
        return p
    return str(Path(worker.repo_root) / p)


def _launch_linux_frame(worker: WorkerSpec, dry_run: bool) -> None:
    config_path = _resolve_remote_path(worker, worker.config_path)
    archive_list = _resolve_remote_path(worker, worker.archive_list)
    pid_file = f"artifacts/runtime/v52/frame_{worker.name}.pid"
    cmd = (
        f"cd {shlex.quote(worker.repo_root)} && "
        f"mkdir -p artifacts/runtime/v52 && "
        f"nohup {shlex.quote(worker.python_exec)} -u pipeline_runner.py --stage frame "
        f"--config {shlex.quote(config_path)} --archive-list {shlex.quote(archive_list)} "
        f"> audit/_pipeline_frame.nohup.log 2>&1 & echo $! > {shlex.quote(pid_file)}"
    )
    _ssh(worker.host, cmd, dry_run=dry_run)


def _encode_ps(script: str) -> str:
    return base64.b64encode(script.encode("utf-16le")).decode("ascii")


def _launch_windows_frame(worker: WorkerSpec, dry_run: bool) -> None:
    task_name = worker.task_name or f"Omega_v6_frame_{worker.name}"
    root = _resolve_remote_path(worker, worker.repo_root)
    config_path = _resolve_remote_path(worker, worker.config_path)
    archive_list = _resolve_remote_path(worker, worker.archive_list)
    runner = f"{root}\\pipeline_runner.py"

    ps = f"""
$task = "{task_name}"
$root = "{root}"
$py = "{worker.python_exec}"
$args = "-u `"{runner}`" --stage frame --config `"{config_path}`" --archive-list `"{archive_list}`""

$action = New-ScheduledTaskAction -Execute $py -Argument $args -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 7)

Register-ScheduledTask -TaskName $task -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $task
Get-ScheduledTask -TaskName $task | Select TaskName,State
"""
    encoded = _encode_ps(ps)
    remote_cmd = f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded}"
    _ssh(worker.host, remote_cmd, dry_run=dry_run)


def cmd_dispatch_frame(args: argparse.Namespace) -> None:
    workers = _parse_workers(args.workers_file)
    for worker in workers:
        print(f"[Dispatch] {worker.name} ({worker.platform})", flush=True)
        if worker.platform == "linux":
            _launch_linux_frame(worker, dry_run=args.dry_run)
        elif worker.platform == "windows":
            _launch_windows_frame(worker, dry_run=args.dry_run)
        else:
            raise ValueError(f"Unsupported worker platform: {worker.platform}")


def cmd_sync_gcs(args: argparse.Namespace) -> None:
    cmd = [sys.executable, "tools/mac_gateway_sync.py", "--bucket", args.bucket]
    if args.host:
        cmd.extend(["--host", args.host])
    if args.year:
        cmd.extend(["--year", args.year])
    if args.hash:
        cmd.extend(["--hash", args.hash])
    _run(cmd, dry_run=args.dry_run)


def cmd_trigger_vertex(args: argparse.Namespace) -> None:
    script_args = list(args.script_arg)
    if not script_args and Path(args.script).name == "run_vertex_xgb_train.py":
        run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        script_args = ["--output-uri", f"gs://omega_v52_central/staging/models/v6/{run_id}"]

    cmd = [
        sys.executable,
        "tools/submit_vertex_sweep.py",
        "--script",
        args.script,
        "--machine-type",
        args.machine_type,
    ]
    for item in script_args:
        cmd.append(f"--script-arg={item}")
    _run(cmd, dry_run=args.dry_run)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="OMEGA v6 Orchestrator")
    sub = ap.add_subparsers(dest="command", required=True)

    p_dispatch = sub.add_parser("dispatch-frame", help="Dispatch framing jobs to workers")
    p_dispatch.add_argument("--workers-file", required=True, help="JSON file containing worker specs")
    p_dispatch.add_argument("--dry-run", action="store_true")
    p_dispatch.set_defaults(func=cmd_dispatch_frame)

    p_sync = sub.add_parser("sync-gcs", help="Sync framed parquet from workers to GCS")
    p_sync.add_argument("--bucket", default="gs://omega_v52_central")
    p_sync.add_argument("--host", default=None, help="Optional: linux1 or windows1")
    p_sync.add_argument("--year", default=None, help="Optional: year filter (e.g. 2025)")
    p_sync.add_argument("--hash", default="", help="Frame git short hash (optional)")
    p_sync.add_argument("--dry-run", action="store_true")
    p_sync.set_defaults(func=cmd_sync_gcs)

    p_vertex = sub.add_parser("trigger-vertex", help="Trigger Vertex XGBoost training job")
    p_vertex.add_argument("--script", default="tools/run_vertex_xgb_train.py")
    p_vertex.add_argument("--machine-type", default="c2-standard-60")
    p_vertex.add_argument("--script-arg", action="append", default=[], help="Forwarded script argument")
    p_vertex.add_argument("--dry-run", action="store_true")
    p_vertex.set_defaults(func=cmd_trigger_vertex)

    return ap


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
