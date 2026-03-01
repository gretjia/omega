#!/usr/bin/env python3
"""
Stage3 full-chain supervisor (unattended):
1) Resume/finish base matrix on linux1-lx.
2) Upload base matrix to GCS.
3) Submit and wait Vertex training job.
4) Download model to linux1-lx and run local backtest.
5) On anomaly/failure, call LLM debug (gemini -> codex exec fallback),
   then clean stale PID/tmp/cache artifacts before conservative restart.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Any, Dict


def _now_utc() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _log_line(log_file: pathlib.Path, message: str) -> None:
    line = f"[{_now_utc()}] {message}"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def _run(
    cmd: list[str],
    *,
    cwd: str | None = None,
    env: Dict[str, str] | None = None,
    check: bool = True,
    log_file: pathlib.Path | None = None,
) -> subprocess.CompletedProcess:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        cmd_text = " ".join(cmd)
        if len(cmd_text) > 800:
            cmd_text = cmd_text[:800] + " ...<truncated>"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"\n$ {cmd_text}\n")
            if proc.stdout:
                out = proc.stdout
                if len(out) > 12000:
                    out = out[:12000] + "\n...[stdout truncated]...\n"
                f.write(out)
            if proc.stderr:
                err = proc.stderr
                if len(err) > 12000:
                    err = err[:12000] + "\n...[stderr truncated]...\n"
                f.write(err)
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"Command failed rc={proc.returncode}: {' '.join(cmd)}\n"
            f"stdout={proc.stdout[-4000:]}\n"
            f"stderr={proc.stderr[-4000:]}"
        )
    return proc


def _ssh(host: str, remote_cmd: str, *, check: bool = True, log_file: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    return _run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", host, remote_cmd],
        check=check,
        log_file=log_file,
    )


def _ssh_capture(host: str, remote_cmd: str, *, log_file: pathlib.Path | None = None) -> str:
    proc = _ssh(host, remote_cmd, check=True, log_file=log_file)
    return (proc.stdout or "").strip()


def _write_json(path: pathlib.Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _ensure_python_cloud_deps(repo_root: pathlib.Path, log_file: pathlib.Path) -> None:
    probe = _run(
        [sys.executable, "-c", "import google.cloud.storage, google.cloud.aiplatform; print('ok')"],
        cwd=str(repo_root),
        check=False,
        log_file=log_file,
    )
    if probe.returncode == 0:
        return
    _run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--user",
            "google-cloud-storage",
            "google-cloud-aiplatform",
        ],
        cwd=str(repo_root),
        check=True,
        log_file=log_file,
    )


def _llm_debug(stage: str, prompt: str, debug_log: pathlib.Path) -> None:
    gemini_cmd = ["timeout", "240s", "gemini", "-y", "-p", prompt]
    g = _run(gemini_cmd, check=False, log_file=debug_log)
    c = None
    if g.returncode != 0:
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        codex_cmd = [
            "timeout",
            "300s",
            "codex",
            "exec",
            "--full-auto",
            "--skip-git-repo-check",
            "-C",
            str(repo_root),
            prompt,
        ]
        c = _run(codex_cmd, check=False, log_file=debug_log)
    with debug_log.open("a", encoding="utf-8") as f:
        if c is None:
            f.write(f"\n[debug-stage={stage}] tool=gemini rc={g.returncode} at {_now_utc()}\n")
        else:
            f.write(
                f"\n[debug-stage={stage}] gemini_rc={g.returncode} "
                f"codex_exec_rc={c.returncode} at {_now_utc()}\n"
            )


def _remote_proc_snapshot(
    args: argparse.Namespace,
    *,
    pid_file: str,
    cmd_pattern: str,
    local_log: pathlib.Path,
) -> Dict[str, Any]:
    payload = {
        "pid_file": str(pid_file),
        "cmd_pattern": str(cmd_pattern),
    }
    py = (
        "python3 - <<'PY'\n"
        "import json, os, subprocess\n"
        f"cfg = json.loads({json.dumps(json.dumps(payload, ensure_ascii=False))})\n"
        "pid_file = str(cfg.get('pid_file', '')).strip()\n"
        "pattern = str(cfg.get('cmd_pattern', '')).strip()\n"
        "out = {\n"
        "  'pid_file': pid_file,\n"
        "  'pid': '',\n"
        "  'pid_status': 'missing',\n"
        "  'pid_stat': '',\n"
        "  'match_pids': [],\n"
        "  'match_count': 0,\n"
        "  'zombie_pids': [],\n"
        "  'orphan_pids': [],\n"
        "  'has_anomaly': False,\n"
        "}\n"
        "if pid_file and os.path.isfile(pid_file):\n"
        "    try:\n"
        "        out['pid'] = open(pid_file, 'r', encoding='utf-8', errors='replace').read().strip()\n"
        "    except Exception:\n"
        "        out['pid'] = ''\n"
        "pid = out['pid']\n"
        "if pid:\n"
        "    if pid.isdigit():\n"
        "        p = subprocess.run(['ps', '-p', pid, '-o', 'stat='], text=True, capture_output=True)\n"
        "        if p.returncode == 0 and (p.stdout or '').strip():\n"
        "            stat = (p.stdout or '').strip()\n"
        "            out['pid_stat'] = stat\n"
        "            out['pid_status'] = 'zombie' if 'Z' in stat else 'alive'\n"
        "        else:\n"
        "            out['pid_status'] = 'stale'\n"
        "    else:\n"
        "        out['pid_status'] = 'stale'\n"
        "if pattern:\n"
        "    p = subprocess.run(['pgrep', '-f', pattern], text=True, capture_output=True)\n"
        "    if p.returncode in (0, 1):\n"
        "        raw = [x.strip() for x in (p.stdout or '').splitlines() if x.strip().isdigit()]\n"
        "        out['match_pids'] = sorted(set(raw), key=lambda x: int(x))\n"
        "for one in out['match_pids']:\n"
        "    st = subprocess.run(['ps', '-p', one, '-o', 'stat='], text=True, capture_output=True)\n"
        "    if st.returncode == 0 and 'Z' in ((st.stdout or '').strip()):\n"
        "        out['zombie_pids'].append(one)\n"
        "if out['pid']:\n"
        "    out['orphan_pids'] = [x for x in out['match_pids'] if x != out['pid']]\n"
        "else:\n"
        "    out['orphan_pids'] = list(out['match_pids'])\n"
        "out['match_count'] = len(out['match_pids'])\n"
        "out['has_anomaly'] = bool(\n"
        "    out['pid_status'] in ('stale', 'zombie')\n"
        "    or len(out['zombie_pids']) > 0\n"
        "    or len(out['orphan_pids']) > 0\n"
        "    or len(out['match_pids']) > 1\n"
        ")\n"
        "print(json.dumps(out, ensure_ascii=False))\n"
        "PY"
    )
    raw = _ssh_capture(args.remote_host, f"cd {args.remote_repo} && {py}", log_file=local_log)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return {
        "pid_file": pid_file,
        "pid": "",
        "pid_status": "unknown",
        "match_pids": [],
        "match_count": 0,
        "zombie_pids": [],
        "orphan_pids": [],
        "has_anomaly": True,
        "raw": raw,
    }


def _remote_housekeeping(
    args: argparse.Namespace,
    *,
    pid_file: str,
    cmd_pattern: str,
    tmp_dirs: list[str],
    symbol_cache_path: str,
    kill_processes: bool,
    local_log: pathlib.Path,
) -> Dict[str, Any]:
    payload = {
        "pid_file": str(pid_file),
        "cmd_pattern": str(cmd_pattern),
        "tmp_dirs": [str(x) for x in tmp_dirs],
        "symbol_cache_path": str(symbol_cache_path),
        "kill_processes": bool(kill_processes),
        "tmp_cleanup_age_min": int(args.tmp_cleanup_age_min),
        "cache_max_age_hours": int(args.cache_max_age_hours),
        "cache_max_mb": int(args.cache_max_mb),
    }
    py = (
        "python3 - <<'PY'\n"
        "import json, os, signal, subprocess, time\n"
        f"cfg = json.loads({json.dumps(json.dumps(payload, ensure_ascii=False))})\n"
        "pid_file = str(cfg.get('pid_file', '')).strip()\n"
        "pattern = str(cfg.get('cmd_pattern', '')).strip()\n"
        "tmp_dirs = [str(x) for x in (cfg.get('tmp_dirs', []) or []) if str(x).strip()]\n"
        "symbol_cache_path = str(cfg.get('symbol_cache_path', '')).strip()\n"
        "kill_processes = bool(cfg.get('kill_processes', False))\n"
        "tmp_cleanup_age_min = max(1, int(cfg.get('tmp_cleanup_age_min', 45)))\n"
        "cache_max_age_hours = max(1, int(cfg.get('cache_max_age_hours', 168)))\n"
        "cache_max_mb = max(1, int(cfg.get('cache_max_mb', 64)))\n"
        "now = time.time()\n"
        "out = {\n"
        "  'pid_file_removed': False,\n"
        "  'killed_pids': [],\n"
        "  'deleted_tmp_files': [],\n"
        "  'deleted_pid_files': [],\n"
        "  'deleted_cache_files': [],\n"
        "}\n"
        "match_pids = []\n"
        "if pattern:\n"
        "    p = subprocess.run(['pgrep', '-f', pattern], text=True, capture_output=True)\n"
        "    if p.returncode in (0, 1):\n"
        "        match_pids = sorted({x.strip() for x in (p.stdout or '').splitlines() if x.strip().isdigit()}, key=int)\n"
        "if kill_processes and match_pids:\n"
        "    for one in match_pids:\n"
        "        try:\n"
        "            os.kill(int(one), signal.SIGTERM)\n"
        "            out['killed_pids'].append(one)\n"
        "        except Exception:\n"
        "            pass\n"
        "    time.sleep(2.0)\n"
        "    for one in list(match_pids):\n"
        "        p = subprocess.run(['ps', '-p', one, '-o', 'pid='], text=True, capture_output=True)\n"
        "        if p.returncode == 0 and (p.stdout or '').strip():\n"
        "            try:\n"
        "                os.kill(int(one), signal.SIGKILL)\n"
        "            except Exception:\n"
        "                pass\n"
        "if pid_file and os.path.isfile(pid_file):\n"
        "    stale = False\n"
        "    try:\n"
        "        pid = open(pid_file, 'r', encoding='utf-8', errors='replace').read().strip()\n"
        "    except Exception:\n"
        "        pid = ''\n"
        "    if (not pid) or (not pid.isdigit()):\n"
        "        stale = True\n"
        "    else:\n"
        "        p = subprocess.run(['ps', '-p', pid, '-o', 'stat='], text=True, capture_output=True)\n"
        "        stat = (p.stdout or '').strip() if p.returncode == 0 else ''\n"
        "        stale = (not stat) or ('Z' in stat)\n"
        "    if stale:\n"
        "        try:\n"
        "            os.remove(pid_file)\n"
        "            out['pid_file_removed'] = True\n"
        "        except Exception:\n"
        "            pass\n"
        "for d in tmp_dirs:\n"
        "    if not os.path.isdir(d):\n"
        "        continue\n"
        "    for name in os.listdir(d):\n"
        "        lower = name.lower()\n"
        "        if not (lower.endswith('.tmp') or lower.endswith('.part') or lower.endswith('.lock')):\n"
        "            continue\n"
        "        path = os.path.join(d, name)\n"
        "        try:\n"
        "            st = os.stat(path)\n"
        "        except Exception:\n"
        "            continue\n"
        "        age_min = (now - st.st_mtime) / 60.0\n"
        "        if age_min >= float(tmp_cleanup_age_min):\n"
        "            try:\n"
        "                os.remove(path)\n"
        "                out['deleted_tmp_files'].append(path)\n"
        "            except Exception:\n"
        "                pass\n"
        "audit_dir = 'audit/stage3_full'\n"
        "if os.path.isdir(audit_dir):\n"
        "    for name in os.listdir(audit_dir):\n"
        "        if not name.endswith('.pid'):\n"
        "            continue\n"
        "        p = os.path.join(audit_dir, name)\n"
        "        try:\n"
        "            if os.path.getsize(p) <= 0:\n"
        "                os.remove(p)\n"
        "                out['deleted_pid_files'].append(p)\n"
        "        except Exception:\n"
        "            pass\n"
        "if symbol_cache_path and os.path.isfile(symbol_cache_path):\n"
        "    try:\n"
        "        st = os.stat(symbol_cache_path)\n"
        "        too_old = ((now - st.st_mtime) >= (float(cache_max_age_hours) * 3600.0))\n"
        "        too_big = (st.st_size >= int(cache_max_mb) * 1024 * 1024)\n"
        "        if too_old or too_big:\n"
        "            os.remove(symbol_cache_path)\n"
        "            out['deleted_cache_files'].append(symbol_cache_path)\n"
        "    except Exception:\n"
        "        pass\n"
        "out['deleted_tmp_count'] = len(out['deleted_tmp_files'])\n"
        "out['deleted_pid_count'] = len(out['deleted_pid_files'])\n"
        "out['deleted_cache_count'] = len(out['deleted_cache_files'])\n"
        "out['killed_pid_count'] = len(out['killed_pids'])\n"
        "print(json.dumps(out, ensure_ascii=False))\n"
        "PY"
    )
    raw = _ssh_capture(args.remote_host, f"cd {args.remote_repo} && {py}", log_file=local_log)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return {
        "pid_file_removed": False,
        "killed_pids": [],
        "deleted_tmp_files": [],
        "deleted_pid_files": [],
        "deleted_cache_files": [],
        "raw": raw,
    }


def _maybe_debug_anomaly(
    *,
    stage: str,
    details: Dict[str, Any],
    tail: str,
    local_log: pathlib.Path,
    cooldown_sec: int,
    last_debug_ts: float,
) -> float:
    now = time.time()
    if (now - float(last_debug_ts)) < float(max(1, cooldown_sec)):
        _log_line(local_log, f"{stage}: anomaly debug skipped by cooldown")
        return float(last_debug_ts)
    prompt = (
        "你是故障排查助手。下面是 supervisor 检测到的运行异常快照(JSON)和日志尾部。"
        "请先给根因假设(按概率排序)，再给最小修复动作和一条可直接执行的重试命令。\n\n"
        f"[snapshot]\n{json.dumps(details, ensure_ascii=False, indent=2)}\n\n"
        f"[log_tail]\n{tail}\n"
    )
    _llm_debug(stage, prompt, local_log)
    _log_line(local_log, f"{stage}: llm debug triggered")
    return float(now)


def _remote_start_forge(args: argparse.Namespace, remote_log: str, remote_pid: str, local_log: pathlib.Path) -> None:
    cmd = (
        f"cd {args.remote_repo} || exit 1; "
        "mkdir -p audit/stage3_full || exit 1; "
        f"nohup python3 tools/forge_base_matrix.py "
        f"--input-pattern '{args.input_pattern}' "
        f"--years '{args.years}' "
        f"--symbols-per-batch {args.symbols_per_batch} "
        f"--max-workers {args.forge_workers} "
        f"--reserve-mem-gb {args.reserve_mem_gb} "
        f"--worker-mem-gb {args.worker_mem_gb} "
        f"--output-parquet '{args.remote_output_parquet}' "
        f"--output-meta '{args.remote_output_meta}' "
        f"--shard-dir '{args.remote_shard_dir}' "
        f"> '{remote_log}' 2>&1 < /dev/null & "
        f"echo $! > '{remote_pid}'"
    )
    _ssh(args.remote_host, cmd, check=True, log_file=local_log)
    _log_line(local_log, f"forge launched on {args.remote_host} pid_file={remote_pid}")


def _remote_forge_done(args: argparse.Namespace, local_log: pathlib.Path) -> bool:
    out = _ssh_capture(
        args.remote_host,
        (
            f"cd {args.remote_repo} && "
            f"if [ -s '{args.remote_output_parquet}' ] && [ -s '{args.remote_output_meta}' ]; then echo yes; else echo no; fi"
        ),
        log_file=local_log,
    )
    return out == "yes"


def _remote_shard_count(args: argparse.Namespace, local_log: pathlib.Path) -> int:
    out = _ssh_capture(
        args.remote_host,
        (
            f"cd {args.remote_repo} && "
            f"ls -1 '{args.remote_shard_dir}'/base_matrix_batch_*.parquet 2>/dev/null | wc -l"
        ),
        log_file=local_log,
    )
    try:
        return int(out.strip())
    except Exception:
        return -1


def _tail_remote_log(args: argparse.Namespace, remote_log: str, lines: int, local_log: pathlib.Path) -> str:
    return _ssh_capture(
        args.remote_host,
        f"cd {args.remote_repo} && tail -n {lines} '{remote_log}' 2>/dev/null || true",
        log_file=local_log,
    )


def _wait_base_matrix(args: argparse.Namespace, state: Dict[str, Any], state_path: pathlib.Path, local_log: pathlib.Path) -> None:
    remote_log = "audit/stage3_full/linux1_forge_fast.log"
    remote_pid = "audit/stage3_full/linux1_forge_fast.pid"
    proc_pattern = r"^python3 tools/forge_base_matrix\.py( |$)"
    restarts = 0
    max_restarts = int(args.max_forge_restarts)
    last_debug_ts = 0.0

    _log_line(local_log, "base_matrix phase started")

    snapshot = _remote_proc_snapshot(args, pid_file=remote_pid, cmd_pattern=proc_pattern, local_log=local_log)
    if str(snapshot.get("pid_status", "")) != "alive":
        tail = _tail_remote_log(args, remote_log, 220, local_log)
        last_debug_ts = _maybe_debug_anomaly(
            stage="base_matrix_bootstrap",
            details={"snapshot": snapshot, "event": "bootstrap_not_alive"},
            tail=tail,
            local_log=local_log,
            cooldown_sec=int(args.debug_cooldown_sec),
            last_debug_ts=last_debug_ts,
        )
        _remote_housekeeping(
            args,
            pid_file=remote_pid,
            cmd_pattern=proc_pattern,
            tmp_dirs=[args.remote_shard_dir, "audit/stage3_full"],
            symbol_cache_path=f"{args.remote_shard_dir.rstrip('/')}/_symbols_cache.json",
            kill_processes=True,
            local_log=local_log,
        )
        _remote_start_forge(args, remote_log, remote_pid, local_log)
        restarts += 1

    while True:
        done = _remote_forge_done(args, local_log)
        snapshot = _remote_proc_snapshot(args, pid_file=remote_pid, cmd_pattern=proc_pattern, local_log=local_log)
        alive = str(snapshot.get("pid_status", "")) == "alive"
        anomaly = bool(snapshot.get("has_anomaly", False))
        shard_cnt = _remote_shard_count(args, local_log)
        housekeeping = _remote_housekeeping(
            args,
            pid_file=remote_pid,
            cmd_pattern=proc_pattern,
            tmp_dirs=[args.remote_shard_dir, "audit/stage3_full"],
            symbol_cache_path=f"{args.remote_shard_dir.rstrip('/')}/_symbols_cache.json",
            kill_processes=False,
            local_log=local_log,
        )

        state["base_matrix"] = {
            "done": done,
            "alive": alive,
            "pid_status": snapshot.get("pid_status"),
            "shard_count": shard_cnt,
            "restarts": restarts,
            "process_snapshot": snapshot,
            "housekeeping": housekeeping,
            "updated_at": _now_utc(),
        }
        _write_json(state_path, state)

        if done:
            _log_line(local_log, f"base_matrix phase completed shard_count={shard_cnt}")
            return

        if (not alive) or anomaly:
            tail = _tail_remote_log(args, remote_log, 240, local_log)
            last_debug_ts = _maybe_debug_anomaly(
                stage="base_matrix_anomaly",
                details={
                    "snapshot": snapshot,
                    "housekeeping": housekeeping,
                    "done": done,
                    "shard_count": shard_cnt,
                    "restarts": restarts,
                },
                tail=tail,
                local_log=local_log,
                cooldown_sec=int(args.debug_cooldown_sec),
                last_debug_ts=last_debug_ts,
            )
            cleanup = _remote_housekeeping(
                args,
                pid_file=remote_pid,
                cmd_pattern=proc_pattern,
                tmp_dirs=[args.remote_shard_dir, "audit/stage3_full"],
                symbol_cache_path=f"{args.remote_shard_dir.rstrip('/')}/_symbols_cache.json",
                kill_processes=True,
                local_log=local_log,
            )
            state["base_matrix"]["repair_cleanup"] = cleanup
            _write_json(state_path, state)

            if restarts >= max_restarts:
                raise RuntimeError("base matrix exited and restart budget exhausted")

            _remote_start_forge(args, remote_log, remote_pid, local_log)
            restarts += 1
            _log_line(local_log, f"forge restarted count={restarts}")

        time.sleep(int(args.poll_sec))


def _upload_base_matrix(args: argparse.Namespace, state: Dict[str, Any], state_path: pathlib.Path, local_log: pathlib.Path) -> None:
    _log_line(local_log, "gcs upload phase started")
    cmd = (
        f"cd {args.remote_repo} && "
        f"gsutil -m cp '{args.remote_output_parquet}' '{args.base_matrix_uri}' && "
        f"gsutil -m cp '{args.remote_output_meta}' '{args.base_matrix_meta_uri}'"
    )
    _ssh(args.remote_host, cmd, check=True, log_file=local_log)
    state["gcs_upload"] = {"done": True, "updated_at": _now_utc()}
    _write_json(state_path, state)
    _log_line(local_log, "gcs upload phase completed")


def _submit_training(args: argparse.Namespace, repo_root: pathlib.Path, state: Dict[str, Any], state_path: pathlib.Path, local_log: pathlib.Path) -> None:
    _log_line(local_log, "training phase started")
    _ensure_python_cloud_deps(repo_root, local_log)
    cmd = [
        sys.executable,
        "tools/submit_vertex_sweep.py",
        "--script",
        "tools/run_vertex_xgb_train.py",
        "--machine-type",
        args.vertex_machine_type,
        "--sync",
        "--sync-timeout-sec",
        str(args.train_timeout_sec),
        "--force-gcloud-fallback",
        "--code-bundle-uri",
        args.code_bundle_uri,
        "--script-arg",
        f"--base-matrix-uri={args.base_matrix_uri}",
        "--script-arg",
        f"--output-uri={args.model_output_prefix}",
        "--script-arg",
        f"--peace-threshold={args.peace_threshold}",
        "--script-arg",
        f"--srl-resid-sigma-mult={args.srl_resid_sigma_mult}",
        "--script-arg",
        f"--topo-energy-sigma-mult={args.topo_energy_sigma_mult}",
        "--script-arg",
        f"--xgb-max-depth={args.xgb_max_depth}",
        "--script-arg",
        f"--xgb-learning-rate={args.xgb_learning_rate}",
        "--script-arg",
        f"--xgb-subsample={args.xgb_subsample}",
        "--script-arg",
        f"--xgb-colsample-bytree={args.xgb_colsample_bytree}",
    ]
    proc = _run(cmd, cwd=str(repo_root), check=False, log_file=local_log)
    if proc.returncode != 0:
        _llm_debug(
            "training",
            (
                "你是GCP训练任务调试助手。以下是 submit_vertex_sweep 执行失败日志尾部，"
                "请给出最小修复建议和重试命令。\n\n"
                + ((proc.stdout or "") + "\n" + (proc.stderr or ""))[-8000:]
            ),
            local_log,
        )
        raise RuntimeError(f"training submission failed rc={proc.returncode}")

    model_uri = f"{args.model_output_prefix.rstrip('/')}/omega_xgb_final.pkl"
    metrics_uri = f"{args.model_output_prefix.rstrip('/')}/train_metrics.json"
    _run(["gsutil", "ls", model_uri], check=True, log_file=local_log)
    _run(["gsutil", "ls", metrics_uri], check=True, log_file=local_log)

    state["training"] = {
        "done": True,
        "model_uri": model_uri,
        "metrics_uri": metrics_uri,
        "updated_at": _now_utc(),
    }
    _write_json(state_path, state)
    _log_line(local_log, f"training phase completed model_uri={model_uri}")


def _remote_start_backtest(args: argparse.Namespace, local_log: pathlib.Path, model_remote_path: str, bt_log: str, bt_pid: str, bt_out: str, workers: int) -> None:
    cmd = (
        f"cd {args.remote_repo} || exit 1; "
        f"mkdir -p audit/stage3_full || exit 1; "
        f"gsutil cp '{args.model_uri}' '{model_remote_path}' || exit 1; "
        f"nohup python3 tools/run_local_backtest.py "
        f"--model-path '{model_remote_path}' "
        f"--frames-dir '{args.backtest_frames_dir}' "
        f"--output '{bt_out}' "
        f"--workers {workers} "
        f"--symbols-per-batch {args.backtest_symbols_per_batch} "
        f"> '{bt_log}' 2>&1 < /dev/null & "
        f"echo $! > '{bt_pid}'"
    )
    _ssh(args.remote_host, cmd, check=True, log_file=local_log)
    _log_line(local_log, f"backtest launched on {args.remote_host} workers={workers}")


def _wait_backtest(args: argparse.Namespace, state: Dict[str, Any], state_path: pathlib.Path, local_log: pathlib.Path) -> None:
    bt_log = f"audit/stage3_full/linux1_backtest_{args.run_id}.log"
    bt_pid = f"audit/stage3_full/linux1_backtest_{args.run_id}.pid"
    bt_out = f"audit/stage3_full/backtest_metrics_{args.run_id}.json"
    model_remote_path = f"audit/stage3_full/model_{args.run_id}.pkl"
    proc_pattern = r"^python3 tools/run_local_backtest\.py( |$)"

    restarts = 0
    workers = int(args.backtest_workers)
    last_debug_ts = 0.0

    _log_line(local_log, "backtest phase started")
    _remote_housekeeping(
        args,
        pid_file=bt_pid,
        cmd_pattern=proc_pattern,
        tmp_dirs=["audit/stage3_full"],
        symbol_cache_path="",
        kill_processes=True,
        local_log=local_log,
    )
    _remote_start_backtest(args, local_log, model_remote_path, bt_log, bt_pid, bt_out, workers)
    restarts += 1

    while True:
        snapshot = _remote_proc_snapshot(args, pid_file=bt_pid, cmd_pattern=proc_pattern, local_log=local_log)
        alive = str(snapshot.get("pid_status", "")) == "alive"
        anomaly = bool(snapshot.get("has_anomaly", False))
        housekeeping = _remote_housekeeping(
            args,
            pid_file=bt_pid,
            cmd_pattern=proc_pattern,
            tmp_dirs=["audit/stage3_full"],
            symbol_cache_path="",
            kill_processes=False,
            local_log=local_log,
        )
        done = _ssh_capture(
            args.remote_host,
            f"cd {args.remote_repo} && if [ -s '{bt_out}' ]; then echo yes; else echo no; fi",
            log_file=local_log,
        ) == "yes"

        state["backtest"] = {
            "done": done,
            "alive": alive,
            "pid_status": snapshot.get("pid_status"),
            "restarts": restarts,
            "workers": workers,
            "output": bt_out,
            "process_snapshot": snapshot,
            "housekeeping": housekeeping,
            "updated_at": _now_utc(),
        }
        _write_json(state_path, state)

        if done:
            result = _ssh_capture(args.remote_host, f"cd {args.remote_repo} && cat '{bt_out}'", log_file=local_log)
            try:
                parsed = json.loads(result)
            except Exception:
                parsed = {"raw": result}
            state["backtest_result"] = parsed
            _write_json(state_path, state)
            _ssh(
                args.remote_host,
                f"cd {args.remote_repo} && gsutil cp '{bt_out}' '{args.backtest_output_uri}'",
                check=True,
                log_file=local_log,
            )
            _log_line(local_log, f"backtest phase completed output_uri={args.backtest_output_uri}")
            return

        if (not alive) or anomaly:
            tail = _tail_remote_log(args, bt_log, 260, local_log)
            last_debug_ts = _maybe_debug_anomaly(
                stage="backtest_anomaly",
                details={
                    "snapshot": snapshot,
                    "housekeeping": housekeeping,
                    "done": done,
                    "workers": workers,
                    "restarts": restarts,
                },
                tail=tail,
                local_log=local_log,
                cooldown_sec=int(args.debug_cooldown_sec),
                last_debug_ts=last_debug_ts,
            )
            cleanup = _remote_housekeeping(
                args,
                pid_file=bt_pid,
                cmd_pattern=proc_pattern,
                tmp_dirs=["audit/stage3_full"],
                symbol_cache_path="",
                kill_processes=True,
                local_log=local_log,
            )
            state["backtest"]["repair_cleanup"] = cleanup
            _write_json(state_path, state)

            if restarts >= int(args.max_backtest_restarts):
                raise RuntimeError("backtest exited and restart budget exhausted")

            workers = max(1, workers - 1)
            _remote_start_backtest(args, local_log, model_remote_path, bt_log, bt_pid, bt_out, workers)
            restarts += 1
            _log_line(local_log, f"backtest restarted count={restarts} workers={workers}")

        time.sleep(int(args.poll_sec))


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Stage3 full chain supervisor")
    ap.add_argument("--run-id", default=dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S"))
    ap.add_argument("--remote-host", default="linux1-lx")
    ap.add_argument("--remote-repo", default="/home/zepher/work/Omega_vNext")
    ap.add_argument("--input-pattern", default="/omega_pool/parquet_data/latest_feature_l2/host=linux1/*.parquet")
    ap.add_argument("--years", default="2023,2024,2025,2026")
    ap.add_argument("--symbols-per-batch", type=int, default=200)
    ap.add_argument("--forge-workers", type=int, default=2)
    ap.add_argument("--reserve-mem-gb", type=float, default=40.0)
    ap.add_argument("--worker-mem-gb", type=float, default=10.0)
    ap.add_argument("--poll-sec", type=int, default=60)
    ap.add_argument("--max-forge-restarts", type=int, default=6)
    ap.add_argument("--max-backtest-restarts", type=int, default=3)
    ap.add_argument("--debug-cooldown-sec", type=int, default=900)
    ap.add_argument("--tmp-cleanup-age-min", type=int, default=45)
    ap.add_argument("--cache-max-age-hours", type=int, default=168)
    ap.add_argument("--cache-max-mb", type=int, default=64)

    ap.add_argument("--remote-output-parquet", default="audit/stage3_full/linux1_base_matrix_full_fast.parquet")
    ap.add_argument("--remote-output-meta", default="audit/stage3_full/linux1_base_matrix_full_fast.meta.json")
    ap.add_argument("--remote-shard-dir", default="audit/stage3_full/linux1_base_matrix_full_fast_shards")

    ap.add_argument("--vertex-machine-type", default="n1-standard-32")
    ap.add_argument("--train-timeout-sec", type=int, default=21600)

    ap.add_argument("--peace-threshold", type=float, default=0.5253567667772991)
    ap.add_argument("--srl-resid-sigma-mult", type=float, default=1.9773888188507172)
    ap.add_argument("--topo-energy-sigma-mult", type=float, default=5.427559578121958)
    ap.add_argument("--xgb-max-depth", type=int, default=5)
    ap.add_argument("--xgb-learning-rate", type=float, default=0.006525909043483982)
    ap.add_argument("--xgb-subsample", type=float, default=0.9382970275902356)
    ap.add_argument("--xgb-colsample-bytree", type=float, default=0.7855991276821759)

    ap.add_argument("--backtest-workers", type=int, default=2)
    ap.add_argument("--backtest-symbols-per-batch", type=int, default=50)
    ap.add_argument("--backtest-frames-dir", default="/omega_pool/parquet_data/latest_feature_l2/host=linux1")

    args = ap.parse_args()

    args.base_matrix_uri = (
        f"gs://omega_central/omega/staging/base_matrix/latest/{args.run_id}/base_matrix.parquet"
    )
    args.base_matrix_meta_uri = (
        f"gs://omega_central/omega/staging/base_matrix/latest/{args.run_id}/base_matrix.meta.json"
    )
    args.code_bundle_uri = (
        f"gs://omega_central/omega/staging/code/omega_core_{args.run_id}.zip"
    )
    args.model_output_prefix = (
        f"gs://omega_central/omega/staging/models/latest/{args.run_id}"
    )
    args.model_uri = f"{args.model_output_prefix}/omega_xgb_final.pkl"
    args.backtest_output_uri = (
        f"gs://omega_central/omega/staging/backtest/latest/{args.run_id}/backtest_metrics_local.json"
    )
    return args


def main() -> int:
    args = parse_args()
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    run_dir = repo_root / "audit" / "stage3_full_supervisor" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    local_log = run_dir / "supervisor.log"
    state_path = run_dir / "state.json"

    state: Dict[str, Any] = {
        "run_id": args.run_id,
        "started_at": _now_utc(),
        "status": "running",
        "base_matrix_uri": args.base_matrix_uri,
        "base_matrix_meta_uri": args.base_matrix_meta_uri,
        "model_output_prefix": args.model_output_prefix,
        "backtest_output_uri": args.backtest_output_uri,
    }
    _write_json(state_path, state)
    _log_line(local_log, f"supervisor started run_id={args.run_id}")

    try:
        _wait_base_matrix(args, state, state_path, local_log)
        _upload_base_matrix(args, state, state_path, local_log)
        _submit_training(args, repo_root, state, state_path, local_log)
        _wait_backtest(args, state, state_path, local_log)

        state["status"] = "completed"
        state["finished_at"] = _now_utc()
        _write_json(state_path, state)
        _log_line(local_log, "supervisor completed")
        print(json.dumps({"status": "completed", "run_id": args.run_id}, ensure_ascii=False))
        return 0
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = str(exc)
        state["finished_at"] = _now_utc()
        _write_json(state_path, state)
        _log_line(local_log, f"[ERROR] {exc}")
        print(json.dumps({"status": "failed", "run_id": args.run_id, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
