#!/usr/bin/env python3
"""
v60 multi-agent tick runner (controller side).

Design goals:
- Replace fragile single watchdog with independent, idempotent role ticks.
- Each role can be scheduled by cron/system scheduler.
- Shared state + event log for transparent coordination.

Roles:
- windows-monitor
- linux-bootstrap
- linux-monitor
- autopilot-gate
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SSH_PS = REPO_ROOT / ".codex" / "skills" / "omega-run-ops" / "scripts" / "ssh_ps.py"
DEFAULT_STATE = REPO_ROOT / "audit" / "runtime" / "v60" / "multi_agents_state.json"
DEFAULT_EVENTS = REPO_ROOT / "audit" / "runtime" / "v60" / "multi_agents_events.log"
DEFAULT_DEBUG_DIR = REPO_ROOT / "audit" / "runtime" / "v60" / "incidents"
CONSTITUTION_PATH = REPO_ROOT / "audit" / "constitution_v2.md"


@dataclass
class CmdResult:
    rc: int
    out: str
    err: str


def resolve_bin(name: str, fallbacks: list[str] | None = None) -> str | None:
    p = shutil.which(name)
    if p:
        return p
    for raw in fallbacks or []:
        path = Path(raw).expanduser()
        if path.exists() and os.access(str(path), os.X_OK):
            return str(path)
    return None


GCLOUD_BIN = resolve_bin(
    "gcloud",
    ["/opt/homebrew/bin/gcloud", "/usr/local/bin/gcloud", "/usr/bin/gcloud"],
)
GEMINI_BIN = resolve_bin(
    "gemini",
    ["~/.local/bin/gemini", "/opt/homebrew/bin/gemini", "/usr/local/bin/gemini"],
)


def ts_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], timeout: int = 120, cwd: Path | None = None) -> CmdResult:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return CmdResult(proc.returncode, proc.stdout or "", proc.stderr or "")
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout if isinstance(exc.stdout, str) else ""
        err = exc.stderr if isinstance(exc.stderr, str) else ""
        return CmdResult(124, out, err or f"timeout after {timeout}s")
    except FileNotFoundError as exc:
        return CmdResult(127, "", str(exc))


def ssh_linux(host: str, remote_cmd: str, timeout: int = 180) -> CmdResult:
    cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "StrictHostKeyChecking=no",
        host,
        remote_cmd,
    ]
    return run(cmd, timeout=timeout)


def ssh_windows_ps(host: str, ps_script: str, timeout: int = 180) -> CmdResult:
    cmd = [sys.executable, str(SSH_PS), host, "--command", ps_script]
    return run(cmd, timeout=timeout)


@contextmanager
def locked_json(path: Path):
    ensure_parent(path)
    lock_path = path.with_suffix(path.suffix + ".lock")
    ensure_parent(lock_path)
    with lock_path.open("a+", encoding="utf-8") as lock_fp:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                data = {}
        else:
            data = {}
        if not isinstance(data, dict):
            data = {}
        yield data
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_UN)


def append_event(path: Path, role: str, event: str, payload: dict | None = None) -> None:
    ensure_parent(path)
    line = {
        "ts_utc": ts_utc(),
        "role": role,
        "event": event,
        "payload": payload or {},
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def parse_kv_lines(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("KV "):
            continue
        body = line[3:]
        if "=" not in body:
            continue
        k, v = body.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def to_int(v: str, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


def to_float(v: str, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def is_truthy(v: str) -> bool:
    return str(v).strip().lower() in {"1", "true", "yes", "y"}


def sanitize_for_ps_single_quote(text: str) -> str:
    return text.replace("'", "''")


def windows_resume_cmd(args: argparse.Namespace) -> str:
    root = args.windows_repo_root
    out_root = f"{root}\\artifacts\\runtime\\v60\\windows_full_{args.hash}"
    dynamic_cap_flag = "--no-dynamic-worker-cap " if bool(args.no_dynamic_worker_cap) else ""
    return (
        f'cd /d "{root}" && '
        "python tools\\v60_build_base_matrix.py "
        f"--input-pattern={args.windows_frame_dir}\\*_{args.hash}.parquet "
        "--years=2023,2024 "
        f"--hash={args.hash} "
        "--peace-threshold=0.10 "
        "--peace-threshold-baseline=0.10 "
        "--srl-resid-sigma-mult=0.5 "
        f"--symbols-per-batch={int(args.symbols_per_batch)} "
        f"--max-workers={int(args.max_workers)} "
        f"--reserve-mem-gb={float(args.reserve_mem_gb):.2f} "
        f"--worker-mem-gb={float(args.worker_mem_gb):.2f} "
        f"{dynamic_cap_flag}"
        f"--output-parquet={out_root}\\base_matrix.parquet "
        f"--output-meta={out_root}\\base_matrix.parquet.meta.json "
        f"--shard-dir={out_root}\\base_matrix_shards "
        f'1>>"{root}\\audit\\runtime\\v60\\windows_base_matrix_run.log" 2>&1'
    )


def linux_resume_cmd(args: argparse.Namespace) -> str:
    root = args.linux_repo_root
    out_root = f"{root}/artifacts/runtime/v60/linux_full_{args.hash}"
    dynamic_cap_flag = "--no-dynamic-worker-cap " if bool(args.no_dynamic_worker_cap) else ""
    return (
        f"cd {shlex.quote(root)} && "
        "mkdir -p "
        f"{shlex.quote(out_root)} "
        f"{shlex.quote(out_root + '/base_matrix_shards')} "
        "audit/runtime/v60 artifacts/runtime/v60 && "
        "PYTHONUNBUFFERED=1 python3 -u tools/v60_build_base_matrix.py "
        f"--input-pattern={shlex.quote(args.linux_frame_dir + f'/*_{args.hash}.parquet')} "
        "--years=2023,2024 "
        f"--hash={shlex.quote(args.hash)} "
        "--peace-threshold=0.10 "
        "--peace-threshold-baseline=0.10 "
        "--srl-resid-sigma-mult=0.5 "
        f"--symbols-per-batch={int(args.symbols_per_batch)} "
        f"--max-workers={int(args.max_workers)} "
        f"--reserve-mem-gb={float(args.reserve_mem_gb):.2f} "
        f"--worker-mem-gb={float(args.worker_mem_gb):.2f} "
        f"{dynamic_cap_flag}"
        f"--output-parquet={shlex.quote(out_root + '/base_matrix.parquet')} "
        f"--output-meta={shlex.quote(out_root + '/base_matrix.parquet.meta.json')} "
        f"--shard-dir={shlex.quote(out_root + '/base_matrix_shards')} "
        ">> audit/runtime/v60/linux_base_matrix_run.log 2>&1"
    )


def maybe_launch_debug_agent(
    *,
    enabled: bool,
    state: dict,
    role: str,
    reason: str,
    context: str,
    debug_dir: Path,
    event_log: Path,
) -> None:
    if not enabled:
        return
    debug_dir.mkdir(parents=True, exist_ok=True)
    active = state.setdefault("debug_agent", {})
    active_pid = int(active.get("pid", 0) or 0)
    if active_pid > 0:
        try:
            os.kill(active_pid, 0)
            return
        except OSError:
            pass

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = debug_dir / f"{ts}_{role}_{reason}.gemini.txt"
    if not GEMINI_BIN:
        append_event(event_log, role, "debug_agent_skipped", {"reason": "gemini_not_found"})
        return
    prompt = (
        "You are a read-only incident debugger for Omega_vNext.\n"
        f"Role: {role}\nReason: {reason}\n"
        "Task: propose minimal-safe recovery actions with concrete commands.\n"
        "Do not propose chunk-days, float32/float16 downcast, or cloud ETL for base matrix.\n\n"
        "Context:\n"
        f"{context}\n"
    )
    cmd = [GEMINI_BIN, "-y", "--output-format", "text", "-p", prompt]
    try:
        with out_path.open("w", encoding="utf-8") as fp:
            proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), stdout=fp, stderr=subprocess.STDOUT, text=True)
    except OSError as exc:
        append_event(event_log, role, "debug_agent_failed", {"error": str(exc)})
        return
    active["pid"] = int(proc.pid)
    active["started_at_utc"] = ts_utc()
    active["role"] = role
    active["reason"] = reason
    active["report"] = str(out_path)
    append_event(
        event_log,
        role,
        "debug_agent_launched",
        {"pid": proc.pid, "reason": reason, "report": str(out_path)},
    )


def role_windows_monitor(args: argparse.Namespace, state: dict) -> dict:
    role = "windows-monitor"
    out_root = f"{args.windows_repo_root}\\artifacts\\runtime\\v60\\windows_full_{args.hash}"
    ps = f"""
$ProgressPreference='SilentlyContinue'
$ErrorActionPreference='SilentlyContinue'
$taskState=(Get-ScheduledTask -TaskName '{sanitize_for_ps_single_quote(args.windows_task_name)}' -ErrorAction SilentlyContinue).State
$guardState=(Get-ScheduledTask -TaskName '{sanitize_for_ps_single_quote(args.windows_guard_task_name)}' -ErrorAction SilentlyContinue).State
$base='{sanitize_for_ps_single_quote(out_root)}\\base_matrix.parquet'
$meta='{sanitize_for_ps_single_quote(out_root)}\\base_matrix.parquet.meta.json'
$shardDir='{sanitize_for_ps_single_quote(out_root)}\\base_matrix_shards'
$parq=(Get-ChildItem -Path $shardDir -Filter 'base_matrix_batch_*.parquet' -File -ErrorAction SilentlyContinue).Count
$metaCnt=(Get-ChildItem -Path $shardDir -Filter 'base_matrix_batch_*.parquet.meta.json' -File -ErrorAction SilentlyContinue).Count
$py=@(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {{ $_.Name -ieq 'python.exe' -and $_.CommandLine -match 'v60_build_base_matrix.py' }}).Count
$os=Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
$free=[math]::Round($os.FreePhysicalMemory/1MB,2)
$total=[math]::Round($os.TotalVisibleMemorySize/1MB,2)
Write-Output "KV task_state=$taskState"
Write-Output "KV guard_state=$guardState"
Write-Output "KV base_exists=$([int](Test-Path $base))"
Write-Output "KV meta_exists=$([int](Test-Path $meta))"
Write-Output "KV shard_parquet=$parq"
Write-Output "KV shard_meta=$metaCnt"
Write-Output "KV py_count=$py"
Write-Output "KV mem_free_gb=$free"
Write-Output "KV mem_total_gb=$total"
"""
    res = ssh_windows_ps(args.windows_host, ps, timeout=180)
    kv = parse_kv_lines(res.out + "\n" + res.err)
    agent = state.setdefault("agents", {}).setdefault(role, {})
    prev_shard = to_int(str(agent.get("shard_parquet", "0")), 0)
    prev_change = float(agent.get("last_progress_epoch", 0.0) or 0.0)
    if prev_change <= 0.0:
        prev_change = time.time()

    shard_now = to_int(kv.get("shard_parquet", "0"), 0)
    base_done = is_truthy(kv.get("base_exists", "0")) and is_truthy(kv.get("meta_exists", "0"))
    py_count = to_int(kv.get("py_count", "0"), 0)
    task_state = kv.get("task_state", "")

    if shard_now > prev_shard:
        prev_change = time.time()
    stall_age = int(time.time() - prev_change)

    action = "none"
    if (not base_done) and py_count <= 0 and str(task_state).lower() != "running":
        cmd = windows_resume_cmd(args)
        ps_start = f"""
$ProgressPreference='SilentlyContinue'
$ErrorActionPreference='Stop'
$cmd='{sanitize_for_ps_single_quote(cmd)}'
Start-Process -FilePath 'cmd.exe' -ArgumentList ("/c " + $cmd) -WindowStyle Hidden
Write-Output "KV started=1"
"""
        if not args.dry_run:
            start_res = ssh_windows_ps(args.windows_host, ps_start, timeout=60)
            started = parse_kv_lines(start_res.out + "\n" + start_res.err).get("started", "0")
            action = "start_resume_process" if started == "1" else "start_failed"
        else:
            action = "dryrun_start_resume_process"

    agent.update(
        {
            "last_tick_utc": ts_utc(),
            "status": "ok" if res.rc == 0 else "warn",
            "task_state": task_state,
            "guard_state": kv.get("guard_state", ""),
            "base_done": bool(base_done),
            "shard_parquet": int(shard_now),
            "shard_meta": int(to_int(kv.get("shard_meta", "0"), 0)),
            "py_count": int(py_count),
            "mem_free_gb": to_float(kv.get("mem_free_gb", "0"), 0.0),
            "mem_total_gb": to_float(kv.get("mem_total_gb", "0"), 0.0),
            "last_progress_epoch": prev_change,
            "stall_age_sec": stall_age,
            "last_action": action,
        }
    )

    if stall_age >= int(args.stall_sec) and not base_done:
        maybe_launch_debug_agent(
            enabled=bool(args.trigger_debug_agent),
            state=state,
            role=role,
            reason="stalled",
            context=json.dumps(agent, ensure_ascii=False, indent=2),
            debug_dir=Path(args.debug_dir),
            event_log=Path(args.event_log),
        )
    return {
        "status": agent.get("status"),
        "action": action,
        "base_done": base_done,
        "shard_parquet": shard_now,
        "stall_age_sec": stall_age,
    }


def fetch_linux_existing_set(args: argparse.Namespace) -> set[str]:
    cmd = (
        f"find {shlex.quote(args.linux_frame_dir)} -maxdepth 1 -type f "
        f"-name '*_{args.hash}.parquet' -printf '%f\\n' 2>/dev/null"
    )
    res = ssh_linux(args.linux_host, cmd, timeout=120)
    if res.rc != 0:
        return set()
    return {x.strip() for x in res.out.splitlines() if x.strip()}


def fetch_gcs_linux_objects(args: argparse.Namespace) -> list[str]:
    if not GCLOUD_BIN:
        return []
    pattern = f"{args.gcs_linux_prefix}/*_{args.hash}.parquet"
    res = run([GCLOUD_BIN, "storage", "ls", pattern], timeout=300, cwd=REPO_ROOT)
    if res.rc != 0:
        return []
    out: list[str] = []
    for line in res.out.splitlines():
        s = line.strip()
        if s.startswith("gs://"):
            out.append(s)
    return out


def stream_copy_object_to_linux(args: argparse.Namespace, gcs_uri: str, fname: str) -> bool:
    if not GCLOUD_BIN:
        return False
    dst = f"{args.linux_frame_dir}/{fname}"
    mk = ssh_linux(args.linux_host, f"mkdir -p {shlex.quote(args.linux_frame_dir)}", timeout=30)
    if mk.rc != 0:
        return False
    ssh_cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=12",
        "-o",
        "StrictHostKeyChecking=no",
        args.linux_host,
        f"cat > {shlex.quote(dst + '.tmp')} && mv {shlex.quote(dst + '.tmp')} {shlex.quote(dst)}",
    ]
    try:
        cat = subprocess.Popen(
            [GCLOUD_BIN, "storage", "cat", gcs_uri],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError:
        return False
    sink = subprocess.Popen(ssh_cmd, stdin=cat.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert cat.stdout is not None
    cat.stdout.close()
    sink_out, sink_err = sink.communicate(timeout=1800)
    cat_rc = cat.wait(timeout=1800)
    if cat_rc != 0 or sink.returncode != 0:
        return False
    _ = sink_out, sink_err
    return True


def role_linux_bootstrap(args: argparse.Namespace, state: dict) -> dict:
    role = "linux-bootstrap"
    agent = state.setdefault("agents", {}).setdefault(role, {})

    git_sync = str(args.linux_git_sync).strip().lower()
    pull_ok = True
    git_sync_mode = "none"
    if git_sync == "pull":
        pull = ssh_linux(
            args.linux_host,
            f"cd {shlex.quote(args.linux_repo_root)} && git pull --rebase --autostash --stat",
            timeout=180,
        )
        pull_ok = pull.rc == 0
        git_sync_mode = "pull"
    elif git_sync == "pin":
        ref = str(args.linux_git_ref or "").strip()
        if ref:
            pin = ssh_linux(
                args.linux_host,
                (
                    f"cd {shlex.quote(args.linux_repo_root)} && "
                    "git fetch --all --tags --prune && "
                    f"git checkout --detach {shlex.quote(ref)}"
                ),
                timeout=240,
            )
            pull_ok = pin.rc == 0
            git_sync_mode = f"pin:{ref}"
        else:
            pull_ok = False
            git_sync_mode = "pin:missing_ref"

    existing = fetch_linux_existing_set(args)
    gcs_objs = fetch_gcs_linux_objects(args)
    missing_objs: list[tuple[str, str]] = []
    for uri in gcs_objs:
        fname = uri.rsplit("/", 1)[-1]
        if fname not in existing:
            missing_objs.append((uri, fname))

    copied = 0
    copy_fail = 0
    for uri, fname in missing_objs[: max(0, int(args.sync_per_tick))]:
        if args.dry_run:
            copied += 1
            continue
        ok = stream_copy_object_to_linux(args, uri, fname)
        if ok:
            copied += 1
        else:
            copy_fail += 1

    after_existing = fetch_linux_existing_set(args)
    frame_count = len(after_existing)
    start_action = "none"

    out_root = f"{args.linux_repo_root}/artifacts/runtime/v60/linux_full_{args.hash}"
    probe_cmd = f"""python3 - <<'PY'
import os
from pathlib import Path

base = Path({json.dumps(out_root + '/base_matrix.parquet')})
meta = Path({json.dumps(out_root + '/base_matrix.parquet.meta.json')})
run_hash = {json.dumps(args.hash)}
ignore = {str(os.getpid()), str(os.getppid())}
proc_count = 0
for pid in os.listdir('/proc'):
    if not pid.isdigit():
        continue
    if pid in ignore:
        continue
    p = Path('/proc') / pid / 'cmdline'
    try:
        raw = p.read_bytes()
    except Exception:
        continue
    cmd = raw.replace(b'\\x00', b' ').decode('utf-8', errors='ignore')
    if (
        'tools/v60_build_base_matrix.py' in cmd
        and f'--hash={{run_hash}}' in cmd
        and '--input-pattern=' in cmd
    ):
        proc_count += 1

print(f"KV proc_count={{proc_count}}")
print(f"KV base_exists={{1 if base.exists() else 0}}")
print(f"KV meta_exists={{1 if meta.exists() else 0}}")
PY"""
    probe = ssh_linux(args.linux_host, probe_cmd, timeout=60)
    kv = parse_kv_lines(probe.out + "\n" + probe.err)
    proc_count = to_int(kv.get("proc_count", "0"), 0)
    base_done = is_truthy(kv.get("base_exists", "0")) and is_truthy(kv.get("meta_exists", "0"))

    if (not base_done) and proc_count <= 0 and frame_count > 0:
        launch = linux_resume_cmd(args)
        run_cmd = (
            f"cd {shlex.quote(args.linux_repo_root)} && "
            "mkdir -p artifacts/runtime/v60 && "
            f"nohup bash -lc {shlex.quote(launch)} >/dev/null 2>&1 & "
            "echo $! > artifacts/runtime/v60/linux_base_matrix.pid"
        )
        if not args.dry_run:
            launch_res = ssh_linux(args.linux_host, run_cmd, timeout=90)
            start_action = "start_resume_process" if launch_res.rc == 0 else "start_failed"
        else:
            start_action = "dryrun_start_resume_process"

    agent.update(
        {
            "last_tick_utc": ts_utc(),
            "status": "ok" if pull_ok else "warn",
            "git_pull_ok": bool(pull_ok),
            "git_sync_mode": git_sync_mode,
            "frame_count": frame_count,
            "gcs_count": len(gcs_objs),
            "missing_count": max(0, len(gcs_objs) - frame_count),
            "copied_this_tick": copied,
            "copy_fail_this_tick": copy_fail,
            "base_done": bool(base_done),
            "proc_count": proc_count,
            "last_action": start_action,
        }
    )
    return {
        "status": agent.get("status"),
        "frame_count": frame_count,
        "gcs_count": len(gcs_objs),
        "copied_this_tick": copied,
        "action": start_action,
        "base_done": bool(base_done),
    }


def role_linux_monitor(args: argparse.Namespace, state: dict) -> dict:
    role = "linux-monitor"
    agent = state.setdefault("agents", {}).setdefault(role, {})
    out_root = f"{args.linux_repo_root}/artifacts/runtime/v60/linux_full_{args.hash}"
    cmd = f"""python3 - <<'PY'
import os
from pathlib import Path

repo = Path({json.dumps(args.linux_repo_root)})
frames = Path({json.dumps(args.linux_frame_dir)})
shard = Path({json.dumps(out_root + '/base_matrix_shards')})
base = Path({json.dumps(out_root + '/base_matrix.parquet')})
meta = Path({json.dumps(out_root + '/base_matrix.parquet.meta.json')})
run_hash = {json.dumps(args.hash)}

ignore = {str(os.getpid()), str(os.getppid())}
proc_count = 0
for pid in os.listdir('/proc'):
    if not pid.isdigit():
        continue
    if pid in ignore:
        continue
    p = Path('/proc') / pid / 'cmdline'
    try:
        raw = p.read_bytes()
    except Exception:
        continue
    cmdline = raw.replace(b'\\x00', b' ').decode('utf-8', errors='ignore')
    if (
        'tools/v60_build_base_matrix.py' in cmdline
        and f'--hash={{run_hash}}' in cmdline
        and '--input-pattern=' in cmdline
    ):
        proc_count += 1

frame_count = 0
if frames.exists():
    frame_count = len(list(frames.glob(f"*_{{run_hash}}.parquet")))

shard_parquet = 0
shard_meta = 0
if shard.exists():
    shard_parquet = len(list(shard.glob("base_matrix_batch_*.parquet")))
    shard_meta = len(list(shard.glob("base_matrix_batch_*.parquet.meta.json")))

log_tail = ""
log_path = repo / "audit/runtime/v60/linux_base_matrix_run.log"
if log_path.exists():
    try:
        with log_path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        if lines:
            log_tail = lines[-1].strip()
    except Exception:
        log_tail = ""

print(f"KV proc_count={{proc_count}}")
print(f"KV shard_parquet={{shard_parquet}}")
print(f"KV shard_meta={{shard_meta}}")
print(f"KV frame_count={{frame_count}}")
print(f"KV base_exists={{1 if base.exists() else 0}}")
print(f"KV meta_exists={{1 if meta.exists() else 0}}")
print(f"KV log_tail={{log_tail}}")
PY"""
    res = ssh_linux(args.linux_host, cmd, timeout=120)
    kv = parse_kv_lines(res.out + "\n" + res.err)

    shard_now = to_int(kv.get("shard_parquet", "0"), 0)
    prev_shard = to_int(str(agent.get("shard_parquet", "0")), 0)
    prev_change = float(agent.get("last_progress_epoch", 0.0) or 0.0)
    if prev_change <= 0.0:
        prev_change = time.time()
    if shard_now > prev_shard:
        prev_change = time.time()
    stall_age = int(time.time() - prev_change)

    base_done = is_truthy(kv.get("base_exists", "0")) and is_truthy(kv.get("meta_exists", "0"))
    proc_count = to_int(kv.get("proc_count", "0"), 0)
    frame_count = to_int(kv.get("frame_count", "0"), 0)
    action = "none"
    if (not base_done) and proc_count <= 0 and frame_count > 0:
        launch = linux_resume_cmd(args)
        run_cmd = (
            f"cd {shlex.quote(args.linux_repo_root)} && "
            "mkdir -p artifacts/runtime/v60 && "
            f"nohup bash -lc {shlex.quote(launch)} >/dev/null 2>&1 & "
            "echo $! > artifacts/runtime/v60/linux_base_matrix.pid"
        )
        if not args.dry_run:
            launch_res = ssh_linux(args.linux_host, run_cmd, timeout=90)
            action = "restart_resume_process" if launch_res.rc == 0 else "restart_failed"
        else:
            action = "dryrun_restart_resume_process"

    agent.update(
        {
            "last_tick_utc": ts_utc(),
            "status": "ok" if res.rc == 0 else "warn",
            "proc_count": proc_count,
            "shard_parquet": shard_now,
            "shard_meta": to_int(kv.get("shard_meta", "0"), 0),
            "frame_count": frame_count,
            "base_done": bool(base_done),
            "stall_age_sec": stall_age,
            "last_progress_epoch": prev_change,
            "last_action": action,
            "log_tail": kv.get("log_tail", ""),
        }
    )
    if stall_age >= int(args.stall_sec) and not base_done and frame_count > 0:
        maybe_launch_debug_agent(
            enabled=bool(args.trigger_debug_agent),
            state=state,
            role=role,
            reason="stalled",
            context=json.dumps(agent, ensure_ascii=False, indent=2),
            debug_dir=Path(args.debug_dir),
            event_log=Path(args.event_log),
        )
    return {
        "status": agent.get("status"),
        "action": action,
        "base_done": base_done,
        "shard_parquet": shard_now,
        "stall_age_sec": stall_age,
    }


def role_autopilot_gate(args: argparse.Namespace, state: dict) -> dict:
    role = "autopilot-gate"
    agent = state.setdefault("agents", {}).setdefault(role, {})
    win = state.get("agents", {}).get("windows-monitor", {})
    lin = state.get("agents", {}).get("linux-monitor", {})

    windows_done = bool(win.get("base_done"))
    linux_done = bool(lin.get("base_done"))

    # Keep the gate strictly aligned with v60 objection core constraints.
    guard_issues: list[str] = []
    if int(args.chunk_days_guard) != 0:
        guard_issues.append("chunk_days_guard must be 0")
    if bool(args.float32_guard):
        guard_issues.append("float32_guard must be disabled")
    if not CONSTITUTION_PATH.exists():
        guard_issues.append(f"constitution missing: {CONSTITUTION_PATH}")

    ready = windows_done and linux_done and not guard_issues
    launched = bool(state.get("autopilot", {}).get("launched", False))
    action = "none"

    if ready and not launched:
        # Stage handoff: mark ready for post-base-matrix chain.
        state.setdefault("autopilot", {})["ready_at_utc"] = ts_utc()
        state["autopilot"]["launched"] = False
        state["autopilot"]["status"] = "ready_post_base"
        action = "ready_post_base"

    agent.update(
        {
            "last_tick_utc": ts_utc(),
            "status": "ok" if not guard_issues else "warn",
            "windows_done": windows_done,
            "linux_done": linux_done,
            "guard_issues": guard_issues,
            "ready": ready,
            "launched": launched,
            "last_action": action,
        }
    )
    return {
        "status": agent.get("status"),
        "windows_done": windows_done,
        "linux_done": linux_done,
        "ready": ready,
        "action": action,
    }


ROLE_FUNCS = {
    "windows-monitor": role_windows_monitor,
    "linux-bootstrap": role_linux_bootstrap,
    "linux-monitor": role_linux_monitor,
    "autopilot-gate": role_autopilot_gate,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="v60 multi-agent role tick")
    ap.add_argument("--hash", required=True)
    ap.add_argument("--role", choices=sorted(ROLE_FUNCS.keys()), required=True)
    ap.add_argument("--state-path", default=str(DEFAULT_STATE))
    ap.add_argument("--event-log", default=str(DEFAULT_EVENTS))
    ap.add_argument("--debug-dir", default=str(DEFAULT_DEBUG_DIR))
    ap.add_argument("--windows-host", default="jiazi@192.168.3.112")
    ap.add_argument("--linux-host", default="zepher@192.168.3.113")
    ap.add_argument("--windows-task-name", default="Omega_v60_BaseMatrix_Local")
    ap.add_argument("--windows-guard-task-name", default="Omega_Windows_MemoryGuard")
    ap.add_argument("--windows-repo-root", default=r"D:\work\Omega_vNext")
    ap.add_argument("--windows-frame-dir", default=r"D:\Omega_frames\v52\frames\host=windows1")
    ap.add_argument("--linux-repo-root", default="/home/zepher/work/Omega_vNext")
    ap.add_argument(
        "--linux-frame-dir",
        default="/omega_pool/parquet_data/v52/frames/host=linux1",
    )
    ap.add_argument("--gcs-linux-prefix", default="gs://omega_v52_central/omega/v52/frames/host=linux1")
    ap.add_argument("--linux-git-sync", choices=["none", "pull", "pin"], default="none")
    ap.add_argument("--linux-git-ref", default="")
    ap.add_argument("--sync-per-tick", type=int, default=1)
    ap.add_argument("--symbols-per-batch", type=int, default=50)
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--reserve-mem-gb", type=float, default=40.0)
    ap.add_argument("--worker-mem-gb", type=float, default=10.0)
    ap.add_argument("--no-dynamic-worker-cap", action="store_true")
    ap.add_argument("--stall-sec", type=int, default=3600)
    ap.add_argument("--chunk-days-guard", type=int, default=0)
    ap.add_argument("--float32-guard", action="store_true")
    ap.add_argument("--trigger-debug-agent", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict-exit", action="store_true")
    args = ap.parse_args()

    state_path = Path(args.state_path)
    event_log = Path(args.event_log)

    if not CONSTITUTION_PATH.exists():
        append_event(event_log, args.role, "constitution_missing", {"path": str(CONSTITUTION_PATH)})

    with locked_json(state_path) as state:
        state.setdefault("hash", args.hash)
        state.setdefault("updated_at_utc", ts_utc())
        state.setdefault("agents", {})

        func = ROLE_FUNCS[args.role]
        payload = func(args, state)
        state["updated_at_utc"] = ts_utc()
        append_event(event_log, args.role, "tick_ok", payload)

    if args.strict_exit and str(payload.get("status", "")).lower() != "ok":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
