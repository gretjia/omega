#!/usr/bin/env python3
"""
AI incident watchdog for long-running Omega pipelines.

Purpose:
- Continuously watch runtime status/logs.
- Detect stuck/failed conditions.
- Capture an incident snapshot.
- Optionally trigger non-interactive AI debug (`gemini -y`).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import shlex
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple


def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_epoch() -> float:
    return time.time()


def read_json(path: Path, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if not path.exists():
        return {} if default is None else dict(default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else dict(default)


def write_json_atomic(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def gcs_count(bucket: str, host: str, git_hash: str) -> int:
    pattern = f"{bucket}/omega/v52/frames/host={host}/*_{git_hash}.parquet"
    res = run(["bash", "-lc", f"gcloud storage ls '{pattern}' 2>/dev/null | wc -l"])
    if res.returncode != 0:
        return -1
    try:
        return int((res.stdout or "0").strip().splitlines()[-1])
    except Exception:
        return -1


def is_pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def pgrep_exists(pattern: str) -> bool:
    res = run(["pgrep", "-f", pattern])
    return res.returncode == 0


def tail(path: Path, n: int = 120) -> str:
    if not path.exists():
        return f"(missing) {path}"
    res = run(["tail", "-n", str(n), str(path)])
    if res.returncode != 0:
        return f"(tail failed) {path}"
    return res.stdout or ""


def scan_new_text(path: Path, pos: int) -> Tuple[str, int]:
    if not path.exists():
        return "", pos
    try:
        size = path.stat().st_size
        if pos > size:
            pos = 0
        with path.open("r", encoding="utf-8", errors="replace") as f:
            f.seek(max(0, pos))
            data = f.read()
            new_pos = f.tell()
        return data, new_pos
    except Exception:
        return "", pos


def file_size(path: Path) -> int:
    try:
        return int(path.stat().st_size)
    except Exception:
        return 0


def build_default_autopilot_launch(
    run_hash: str,
    autopilot_runner_log: Path,
    upload_mode: str,
    poll_sec: int,
    stall_sec: int,
) -> str:
    return (
        "PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py "
        f"--hash {shlex.quote(run_hash)} "
        f"--upload-mode {shlex.quote(upload_mode)} "
        f"--poll-sec {int(poll_sec)} "
        f"--stall-sec {int(stall_sec)} "
        f">> {shlex.quote(str(autopilot_runner_log))} 2>&1"
    )


def ensure_uplink_loop_script(
    script_path: Path,
    repo_root: Path,
    run_hash: str,
    bucket: str,
    sleep_sec: int,
) -> None:
    if script_path.exists():
        return
    script_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -u",
            f"cd {shlex.quote(str(repo_root))} || exit 1",
            "while true; do",
            "  ts=\"$(date '+%Y-%m-%d %H:%M:%S')\"",
            "  echo \"[$ts] uplink cycle begin\"",
            (
                "  PYTHONUNBUFFERED=1 python3 -u tools/mac_gateway_sync.py "
                f"--bucket {shlex.quote(bucket)} --host linux1 --hash {shlex.quote(run_hash)}"
            ),
            "  rc1=$?",
            "  ts=\"$(date '+%Y-%m-%d %H:%M:%S')\"",
            "  echo \"[$ts] linux1 sync rc=$rc1\"",
            (
                "  PYTHONUNBUFFERED=1 python3 -u tools/mac_gateway_sync.py "
                f"--bucket {shlex.quote(bucket)} --host windows1 --hash {shlex.quote(run_hash)}"
            ),
            "  rc2=$?",
            "  ts=\"$(date '+%Y-%m-%d %H:%M:%S')\"",
            "  echo \"[$ts] windows1 sync rc=$rc2\"",
            f"  echo \"[$ts] uplink cycle sleep {int(sleep_sec)}s\"",
            f"  sleep {int(sleep_sec)}",
            "done",
            "",
        ]
    )
    script_path.write_text(content, encoding="utf-8")
    script_path.chmod(0o755)


def build_default_uplink_launch(script_path: Path, uplink_log: Path) -> str:
    return f"bash {shlex.quote(str(script_path))} >> {shlex.quote(str(uplink_log))} 2>&1"


def start_detached_screen(session_name: str, command: str, repo_root: Path) -> Tuple[bool, str]:
    wrapped = f"cd {shlex.quote(str(repo_root))} && {command}"
    res = run(["screen", "-dmS", session_name, "bash", "-lc", wrapped])
    ok = res.returncode == 0
    text = ((res.stdout or "") + (res.stderr or "")).strip()
    return ok, text


def append_handover_event(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {now_ts()} | {title}\n")
        for line in lines:
            f.write(f"- {line}\n")


def make_incident_snapshot(
    incident_id: str,
    reason: str,
    status_payload: Dict[str, Any],
    autopilot_status: Path,
    autopilot_runner_log: Path,
    autopilot_log: Path,
    uplink_log: Path,
    out_dir: Path,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot = out_dir / f"{incident_id}.md"
    screen_ls = run(["screen", "-ls"])
    pgrep_all = run(
        ["pgrep", "-fl", "tools/v60_autopilot.py|uplink_loop|mac_gateway_sync.py|gemini -y|codex exec"]
    )

    lines: list[str] = []
    lines.append(f"# Incident {incident_id}")
    lines.append(f"- ts: {now_ts()}")
    lines.append(f"- reason: {reason}")
    lines.append(f"- autopilot_status: {autopilot_status}")
    lines.append(f"- autopilot_runner_log: {autopilot_runner_log}")
    lines.append(f"- autopilot_log: {autopilot_log}")
    lines.append(f"- uplink_log: {uplink_log}")
    lines.append("")
    lines.append("## Status JSON")
    lines.append("```json")
    lines.append(json.dumps(status_payload, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## screen -ls")
    lines.append("```text")
    lines.append((screen_ls.stdout or "") + (screen_ls.stderr or ""))
    lines.append("```")
    lines.append("")
    lines.append("## pgrep")
    lines.append("```text")
    lines.append((pgrep_all.stdout or "") + (pgrep_all.stderr or ""))
    lines.append("```")
    lines.append("")
    lines.append("## Tail: autopilot runner log")
    lines.append("```text")
    lines.append(tail(autopilot_runner_log, n=120))
    lines.append("```")
    lines.append("")
    lines.append("## Tail: autopilot log")
    lines.append("```text")
    lines.append(tail(autopilot_log, n=120))
    lines.append("```")
    lines.append("")
    lines.append("## Tail: uplink log")
    lines.append("```text")
    lines.append(tail(uplink_log, n=120))
    lines.append("```")
    snapshot.write_text("\n".join(lines), encoding="utf-8")
    return snapshot


def launch_ai_debug(
    repo_root: Path,
    incident_id: str,
    reason: str,
    run_hash: str,
    snapshot_path: Path,
    incident_dir: Path,
    model: str,
    context_files: list[Path],
) -> Tuple[int, Path, Path]:
    report_path = incident_dir / f"{incident_id}.ai_debug_report.txt"
    log_path = incident_dir / f"{incident_id}.ai_debug_exec.log"

    context_lines = "\n".join(f"- {p}" for p in context_files) if context_files else "- (none)"
    prompt = (
        f"# Incident\n"
        f"- run_hash: {run_hash}\n"
        f"- incident_id: {incident_id}\n"
        f"- reason: {reason}\n"
        f"- snapshot: {snapshot_path}\n\n"
        f"# Goal\n"
        f"Recover Omega v60 pipeline progress with minimal safe intervention.\n\n"
        f"# Constraints\n"
        f"- Do NOT change v6 mathematical logic/principles.\n"
        f"- No destructive git commands.\n"
        f"- Prefer smallest fix that restores forward progress.\n\n"
        f"# Context Files\n"
        f"{context_lines}\n\n"
        f"# Required Workflow\n"
        f"1) Read snapshot and context files.\n"
        f"2) Identify root cause with concrete evidence.\n"
        f"3) Apply fixes/restarts if needed.\n"
        f"4) Verify recovery with logs/status.\n\n"
        f"# Deliverable\n"
        f"Write final incident response summary to {report_path} with:\n"
        f"- root cause\n"
        f"- exact actions/commands\n"
        f"- current status and whether pipeline resumed\n"
        f"- next checks and remaining risks\n"
    )

    cmd = ["gemini", "-y", "--cd", str(repo_root)]
    if model:
        # gemini might not support --model in the same way, or defaults to a smart one.
        # usually gemini -y uses the default configured model.
        pass 
    cmd.append(prompt)

    log_f = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        cmd,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc.pid, report_path, log_path


def main() -> int:
    ap = argparse.ArgumentParser(description="AI incident watchdog for Omega long runs")
    ap.add_argument("--hash", required=True, help="run git short hash")
    ap.add_argument("--bucket", default="gs://omega_v52_central")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--poll-sec", type=int, default=120)
    ap.add_argument("--status-stale-sec", type=int, default=900)
    ap.add_argument("--upload-stall-sec", type=int, default=1200)
    ap.add_argument("--cooldown-sec", type=int, default=1800)
    ap.add_argument("--max-triggers", type=int, default=12)
    ap.add_argument(
        "--trigger-debug-agent",
        action="store_true",
        help="auto launch AI debug agent on incident (default agent: gemini -y)",
    )
    ap.add_argument(
        "--trigger-codex",
        action="store_true",
        help="[legacy] alias for --trigger-debug-agent",
    )
    ap.add_argument("--debug-model", default="", help="reserved debug model selector (currently unused by gemini -y)")
    ap.add_argument("--codex-model", default="", help="[legacy] deprecated alias for --debug-model")
    ap.add_argument("--context-file", action="append", default=[], help="extra context file path (repeatable)")
    ap.add_argument("--state-json", default="")
    ap.add_argument("--incident-dir", default="")
    ap.add_argument("--autopilot-status-json", default="")
    ap.add_argument("--autopilot-runner-log", default="")
    ap.add_argument("--autopilot-log", default="")
    ap.add_argument("--uplink-log", default="")
    ap.add_argument("--auto-resume", action="store_true", help="auto restart autopilot/uplink when process is missing")
    ap.add_argument("--autopilot-session", default="")
    ap.add_argument("--autopilot-launch", default="")
    ap.add_argument("--autopilot-upload-mode", choices=("sync_once", "wait_existing"), default="wait_existing")
    ap.add_argument("--autopilot-poll-sec", type=int, default=180)
    ap.add_argument("--autopilot-stall-sec", type=int, default=1800)
    ap.add_argument("--autopilot-grace-sec", type=int, default=120)
    ap.add_argument("--autopilot-restart-cooldown-sec", type=int, default=300)
    ap.add_argument("--autopilot-restart-max", type=int, default=20)
    ap.add_argument("--uplink-session", default="")
    ap.add_argument("--uplink-launch", default="")
    ap.add_argument("--uplink-loop-script", default="")
    ap.add_argument("--uplink-sleep-sec", type=int, default=300)
    ap.add_argument("--uplink-grace-sec", type=int, default=180)
    ap.add_argument("--uplink-restart-cooldown-sec", type=int, default=600)
    ap.add_argument("--uplink-restart-max", type=int, default=20)
    ap.add_argument("--handover-live-json", default="")
    ap.add_argument("--handover-events-md", default="")
    args = ap.parse_args()
    trigger_debug_agent = bool(args.trigger_debug_agent or args.trigger_codex)
    debug_model = args.debug_model.strip() or args.codex_model.strip()

    repo_root = Path(args.repo_root).resolve()
    run_hash = args.hash.strip()
    runtime_dir = repo_root / "audit" / "runtime" / "v52"
    state_path = Path(args.state_json) if args.state_json else (runtime_dir / f"ai_watchdog_{run_hash}.state.json")
    incident_dir = Path(args.incident_dir) if args.incident_dir else (runtime_dir / "incidents")
    autopilot_status = Path(args.autopilot_status_json) if args.autopilot_status_json else (
        runtime_dir / f"autopilot_{run_hash}.status.json"
    )
    autopilot_runner_log = Path(args.autopilot_runner_log) if args.autopilot_runner_log else (
        runtime_dir / f"autopilot_{run_hash}.runner.log"
    )
    autopilot_log = Path(args.autopilot_log) if args.autopilot_log else (runtime_dir / f"autopilot_{run_hash}.log")
    uplink_log = Path(args.uplink_log) if args.uplink_log else (runtime_dir / f"uplink_{run_hash}.log")
    uplink_loop_script = Path(args.uplink_loop_script) if args.uplink_loop_script else (
        runtime_dir / f"uplink_loop_{run_hash}.sh"
    )
    autopilot_session = args.autopilot_session.strip() or f"v60_autopilot_{run_hash}"
    uplink_session = args.uplink_session.strip() or f"v60_uplink_{run_hash}"
    handover_live_json = Path(args.handover_live_json) if args.handover_live_json else (
        repo_root / "handover" / "ai-direct" / "live" / f"v60_run_{run_hash}.json"
    )
    handover_events_md = Path(args.handover_events_md) if args.handover_events_md else (
        repo_root / "handover" / "ai-direct" / "live" / f"v60_events_{run_hash}.md"
    )
    autopilot_launch = args.autopilot_launch.strip() or build_default_autopilot_launch(
        run_hash=run_hash,
        autopilot_runner_log=autopilot_runner_log,
        upload_mode=args.autopilot_upload_mode,
        poll_sec=int(args.autopilot_poll_sec),
        stall_sec=int(args.autopilot_stall_sec),
    )
    if args.uplink_launch.strip():
        uplink_launch = args.uplink_launch.strip()
    else:
        ensure_uplink_loop_script(
            script_path=uplink_loop_script,
            repo_root=repo_root,
            run_hash=run_hash,
            bucket=args.bucket,
            sleep_sec=int(args.uplink_sleep_sec),
        )
        uplink_launch = build_default_uplink_launch(uplink_loop_script, uplink_log)

    state = read_json(
        state_path,
        default={
            "started_at": now_ts(),
            "hash": run_hash,
            "runner_pos": -1,
            "last_gcs_total": -1,
            "last_gcs_change_ts": now_epoch(),
            "last_trigger_ts": 0.0,
            "active_debug_pid": 0,
            "active_debug": {},
            "active_codex_pid": 0,
            "active_codex": {},
            "trigger_count": 0,
            "seen_fingerprints": [],
            "autopilot_down_since_ts": 0.0,
            "last_autopilot_restart_ts": 0.0,
            "autopilot_restart_count": 0,
            "uplink_down_since_ts": 0.0,
            "last_uplink_restart_ts": 0.0,
            "uplink_restart_count": 0,
            "last_probe": {},
        },
    )
    if int(state.get("runner_pos", -1)) < 0:
        state["runner_pos"] = file_size(autopilot_runner_log)

    # Backward compatibility with old state keys.
    if "active_debug_pid" not in state:
        state["active_debug_pid"] = int(state.get("active_codex_pid", 0) or 0)
    if "active_debug" not in state:
        old = state.get("active_codex", {})
        state["active_debug"] = dict(old) if isinstance(old, dict) else {}
    state["active_codex_pid"] = int(state.get("active_debug_pid", 0) or 0)
    state["active_codex"] = dict(state.get("active_debug", {}))

    def get_active_debug_pid() -> int:
        return int(state.get("active_debug_pid", 0) or state.get("active_codex_pid", 0) or 0)

    def log(msg: str) -> None:
        line = f"[{now_ts()}] {msg}"
        print(line, flush=True)

    def record_event(title: str, lines: list[str]) -> None:
        append_handover_event(handover_events_md, title, lines)

    context_files: list[Path] = []
    default_contexts = [
        repo_root / "AGENTS.md",
        repo_root / "audit" / "v6.md",
        repo_root / "handover" / "ai-direct" / "LATEST.md",
        repo_root / "handover" / "ai-direct" / "entries" / "20260216_vertex_god_view_lessons.md",
        handover_live_json,
        handover_events_md,
        runtime_dir / f"autopilot_{run_hash}.status.json",
        runtime_dir / f"autopilot_{run_hash}.runner.log",
        runtime_dir / f"uplink_{run_hash}.log",
    ]
    for p in default_contexts:
        if p.exists():
            context_files.append(p)
    for raw in args.context_file:
        p = Path(raw).resolve()
        if p.exists() and p not in context_files:
            context_files.append(p)

    def write_handover_live(
        status_payload: Dict[str, Any],
        stage: str,
        is_completed: bool,
        autopilot_running: bool,
        uplink_running: bool,
        lin_gcs: int,
        win_gcs: int,
        gcs_stall_age: float,
        status_age: float,
    ) -> None:
        payload = {
            "updated_at": now_ts(),
            "hash": run_hash,
            "stage": stage,
            "completed": bool(is_completed),
            "autopilot_running": bool(autopilot_running),
            "uplink_running": bool(uplink_running),
            "gcs": {
                "linux1_parquet": lin_gcs,
                "windows1_parquet": win_gcs,
                "total_parquet": max(0, lin_gcs) + max(0, win_gcs),
                "stall_age_sec": int(gcs_stall_age),
            },
            "status_age_sec": int(status_age),
            "restarts": {
                "autopilot": int(state.get("autopilot_restart_count", 0)),
                "uplink": int(state.get("uplink_restart_count", 0)),
            },
            "triggers": {
                "count": int(state.get("trigger_count", 0)),
                "last_trigger_ts": float(state.get("last_trigger_ts", 0.0)),
                "active_debug_pid": get_active_debug_pid(),
                "active_codex_pid": get_active_debug_pid(),  # legacy compatibility
            },
            "paths": {
                "state_json": str(state_path),
                "autopilot_status_json": str(autopilot_status),
                "autopilot_runner_log": str(autopilot_runner_log),
                "autopilot_log": str(autopilot_log),
                "uplink_log": str(uplink_log),
                "incidents_dir": str(incident_dir),
                "handover_events_md": str(handover_events_md),
            },
            "status_snapshot": status_payload,
        }
        write_json_atomic(handover_live_json, payload)

    def maybe_trigger(reason: str, fingerprint: str, status_payload: Dict[str, Any]) -> None:
        seen = [str(x) for x in state.get("seen_fingerprints", []) if str(x).strip()]
        if fingerprint in seen:
            return
        if state.get("trigger_count", 0) >= int(args.max_triggers):
            log(f"incident skipped (max_triggers reached): {reason}")
            return
        if now_epoch() - float(state.get("last_trigger_ts", 0.0)) < float(args.cooldown_sec):
            log(f"incident suppressed by cooldown: {reason}")
            return
        if is_pid_alive(get_active_debug_pid()):
            log(f"incident deferred (ai debug already running): {reason}")
            return

        incident_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        incident_id = f"{incident_id}_{re.sub(r'[^a-zA-Z0-9_]+', '_', reason)[:40]}"
        snapshot = make_incident_snapshot(
            incident_id=incident_id,
            reason=reason,
            status_payload=status_payload,
            autopilot_status=autopilot_status,
            autopilot_runner_log=autopilot_runner_log,
            autopilot_log=autopilot_log,
            uplink_log=uplink_log,
            out_dir=incident_dir,
        )
        log(f"incident captured: {snapshot}")
        record_event(
            "incident_captured",
            [
                f"reason: {reason}",
                f"fingerprint: {fingerprint}",
                f"snapshot: {snapshot}",
            ],
        )

        if trigger_debug_agent:
            try:
                pid, report_path, exec_log = launch_ai_debug(
                    repo_root=repo_root,
                    incident_id=incident_id,
                    reason=reason,
                    run_hash=run_hash,
                    snapshot_path=snapshot,
                    incident_dir=incident_dir,
                    model=debug_model,
                    context_files=context_files,
                )
                state["active_debug_pid"] = pid
                state["active_debug"] = {
                    "pid": pid,
                    "incident_id": incident_id,
                    "reason": reason,
                    "report_path": str(report_path),
                    "log_path": str(exec_log),
                    "started_at": now_ts(),
                }
                state["active_codex_pid"] = pid  # legacy compatibility
                state["active_codex"] = dict(state["active_debug"])
                log(f"ai debug launched pid={pid} report={report_path} log={exec_log}")
                record_event(
                    "ai_debug_launched",
                    [
                        f"pid: {pid}",
                        f"reason: {reason}",
                        f"incident_id: {incident_id}",
                        f"report_path: {report_path}",
                        f"log_path: {exec_log}",
                    ],
                )
            except Exception as exc:
                log(f"ai debug launch failed: {exc}")
                record_event("ai_debug_launch_failed", [f"reason: {reason}", f"error: {exc}"])

        state["trigger_count"] = int(state.get("trigger_count", 0)) + 1
        state["last_trigger_ts"] = now_epoch()
        state["seen_fingerprints"] = (seen + [fingerprint])[-200:]

    log(
        f"ai watchdog started hash={run_hash} poll={args.poll_sec}s "
        f"trigger_debug_agent={trigger_debug_agent} auto_resume={bool(args.auto_resume)}"
    )
    record_event(
        "watchdog_started",
        [
            f"hash: {run_hash}",
            f"auto_resume: {bool(args.auto_resume)}",
            f"autopilot_session: {autopilot_session}",
            f"uplink_session: {uplink_session}",
            f"autopilot_launch: {autopilot_launch}",
            f"uplink_launch: {uplink_launch}",
            f"live_state: {handover_live_json}",
            f"events_log: {handover_events_md}",
        ],
    )

    while True:
        status_payload = read_json(autopilot_status, default={})
        stage = str(status_payload.get("stage", "")).strip()
        is_completed = stage == "completed"
        status_mtime = autopilot_status.stat().st_mtime if autopilot_status.exists() else 0.0
        status_age = now_epoch() - status_mtime if status_mtime > 0 else 10**9
        runner_mtime = autopilot_runner_log.stat().st_mtime if autopilot_runner_log.exists() else 0.0
        runner_age = now_epoch() - runner_mtime if runner_mtime > 0 else 10**9

        runner_new, new_pos = scan_new_text(autopilot_runner_log, int(state.get("runner_pos", 0)))
        state["runner_pos"] = new_pos

        autopilot_running = pgrep_exists(f"tools/v60_autopilot.py --hash {run_hash}")
        uplink_running = pgrep_exists(f"uplink_loop_{run_hash}.sh") or pgrep_exists("tools/mac_gateway_sync.py")

        lin_gcs = gcs_count(args.bucket, "linux1", run_hash)
        win_gcs = gcs_count(args.bucket, "windows1", run_hash)
        gcs_total = max(0, lin_gcs) + max(0, win_gcs)

        last_gcs_total = int(state.get("last_gcs_total", -1))
        if gcs_total > last_gcs_total:
            state["last_gcs_total"] = gcs_total
            state["last_gcs_change_ts"] = now_epoch()
        gcs_stall_age = now_epoch() - float(state.get("last_gcs_change_ts", now_epoch()))

        active_pid = get_active_debug_pid()
        if active_pid and not is_pid_alive(active_pid):
            debug_info = dict(state.get("active_debug", {}))
            state["active_debug_pid"] = 0
            state["active_debug"] = {}
            state["active_codex_pid"] = 0  # legacy compatibility
            state["active_codex"] = {}
            record_event(
                "ai_debug_finished",
                [
                    f"pid: {active_pid}",
                    f"incident_id: {debug_info.get('incident_id', '')}",
                    f"reason: {debug_info.get('reason', '')}",
                    f"report_path: {debug_info.get('report_path', '')}",
                ],
            )
        debug_running = is_pid_alive(get_active_debug_pid())

        needs_uplink = (not is_completed) and stage in {"", "monitor_frame", "sync_gcs", "wait_gcs_upload"}
        if not is_completed and not autopilot_running:
            if float(state.get("autopilot_down_since_ts", 0.0)) <= 0.0:
                state["autopilot_down_since_ts"] = now_epoch()
            down_age = now_epoch() - float(state.get("autopilot_down_since_ts", now_epoch()))
            can_retry = (
                args.auto_resume
                and not debug_running
                and down_age >= float(args.autopilot_grace_sec)
                and now_epoch() - float(state.get("last_autopilot_restart_ts", 0.0))
                >= float(args.autopilot_restart_cooldown_sec)
                and int(state.get("autopilot_restart_count", 0)) < int(args.autopilot_restart_max)
            )
            if can_retry:
                ok, out = start_detached_screen(autopilot_session, autopilot_launch, repo_root)
                if ok:
                    state["autopilot_restart_count"] = int(state.get("autopilot_restart_count", 0)) + 1
                    state["last_autopilot_restart_ts"] = now_epoch()
                    state["autopilot_down_since_ts"] = 0.0
                    log(
                        f"autopilot auto-resume launched session={autopilot_session} "
                        f"restart_count={state['autopilot_restart_count']}"
                    )
                    record_event(
                        "autopilot_auto_resumed",
                        [
                            f"session: {autopilot_session}",
                            f"restart_count: {state['autopilot_restart_count']}",
                            f"launch: {autopilot_launch}",
                        ],
                    )
                else:
                    log(f"autopilot auto-resume failed session={autopilot_session} out={out}")
                    record_event(
                        "autopilot_auto_resume_failed",
                        [
                            f"session: {autopilot_session}",
                            f"launch: {autopilot_launch}",
                            f"stdout_stderr: {out}",
                        ],
                    )
            if not debug_running:
                maybe_trigger(
                    reason="autopilot_not_running",
                    fingerprint=f"autopilot_not_running:{stage or 'unknown'}",
                    status_payload=status_payload,
                )
        else:
            state["autopilot_down_since_ts"] = 0.0

        if needs_uplink and not uplink_running:
            if float(state.get("uplink_down_since_ts", 0.0)) <= 0.0:
                state["uplink_down_since_ts"] = now_epoch()
            down_age = now_epoch() - float(state.get("uplink_down_since_ts", now_epoch()))
            can_retry = (
                args.auto_resume
                and not debug_running
                and down_age >= float(args.uplink_grace_sec)
                and now_epoch() - float(state.get("last_uplink_restart_ts", 0.0))
                >= float(args.uplink_restart_cooldown_sec)
                and int(state.get("uplink_restart_count", 0)) < int(args.uplink_restart_max)
            )
            if can_retry:
                ok, out = start_detached_screen(uplink_session, uplink_launch, repo_root)
                if ok:
                    state["uplink_restart_count"] = int(state.get("uplink_restart_count", 0)) + 1
                    state["last_uplink_restart_ts"] = now_epoch()
                    state["uplink_down_since_ts"] = 0.0
                    log(
                        f"uplink auto-resume launched session={uplink_session} "
                        f"restart_count={state['uplink_restart_count']}"
                    )
                    record_event(
                        "uplink_auto_resumed",
                        [
                            f"session: {uplink_session}",
                            f"restart_count: {state['uplink_restart_count']}",
                            f"launch: {uplink_launch}",
                        ],
                    )
                else:
                    log(f"uplink auto-resume failed session={uplink_session} out={out}")
                    record_event(
                        "uplink_auto_resume_failed",
                        [
                            f"session: {uplink_session}",
                            f"launch: {uplink_launch}",
                            f"stdout_stderr: {out}",
                        ],
                    )
            if not debug_running:
                maybe_trigger(
                    reason="uplink_not_running",
                    fingerprint=f"uplink_not_running:{stage or 'unknown'}",
                    status_payload=status_payload,
                )
        else:
            state["uplink_down_since_ts"] = 0.0

        state["last_probe"] = {
            "ts": now_ts(),
            "stage": stage,
            "status_age_sec": int(status_age),
            "runner_age_sec": int(runner_age),
            "autopilot_running": autopilot_running,
            "uplink_running": uplink_running,
            "gcs_linux_parquet": lin_gcs,
            "gcs_windows_parquet": win_gcs,
            "gcs_total": gcs_total,
            "gcs_stall_age_sec": int(gcs_stall_age),
            "autopilot_restart_count": int(state.get("autopilot_restart_count", 0)),
            "uplink_restart_count": int(state.get("uplink_restart_count", 0)),
            "active_debug_pid": get_active_debug_pid(),
            "active_codex_pid": get_active_debug_pid(),  # legacy compatibility
        }

        if (
            (not is_completed)
            and stage
            and status_age > float(args.status_stale_sec)
            and runner_age > float(args.status_stale_sec)
        ):
            maybe_trigger(
                reason="autopilot_status_stale",
                fingerprint=f"autopilot_status_stale:{stage}:{int(status_age // 300)}",
                status_payload=status_payload,
            )

        if runner_new:
            err = re.search(r"(Traceback|RuntimeError|CalledProcessError|JOB_STATE_FAILED|Exception:)", runner_new)
            if err:
                snippet = runner_new[max(0, err.start() - 80) : min(len(runner_new), err.start() + 160)]
                fp = f"runner_error:{err.group(1)}:{hash(snippet)}"
                maybe_trigger(
                    reason=f"runner_error_{err.group(1)}",
                    fingerprint=fp,
                    status_payload=status_payload,
                )

        upload_sensitive_stages = {"", "monitor_frame", "sync_gcs", "wait_gcs_upload"}
        if (
            (not is_completed)
            and (stage in upload_sensitive_stages)
            and uplink_running
            and gcs_stall_age > float(args.upload_stall_sec)
        ):
            maybe_trigger(
                reason="upload_progress_stalled",
                fingerprint=f"upload_progress_stalled:{int(gcs_stall_age // 300)}",
                status_payload=status_payload,
            )

        # Maintain backward-compatible keys for existing dashboards/readers.
        state["active_codex_pid"] = int(state.get("active_debug_pid", 0))
        state["active_codex"] = dict(state.get("active_debug", {}))

        write_json_atomic(state_path, state)
        write_handover_live(
            status_payload=status_payload,
            stage=stage,
            is_completed=is_completed,
            autopilot_running=autopilot_running,
            uplink_running=uplink_running,
            lin_gcs=lin_gcs,
            win_gcs=win_gcs,
            gcs_stall_age=gcs_stall_age,
            status_age=status_age,
        )
        time.sleep(max(20, int(args.poll_sec)))


if __name__ == "__main__":
    raise SystemExit(main())
