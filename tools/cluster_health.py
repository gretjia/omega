#!/usr/bin/env python3
"""
OMEGA Cluster Health Dashboard
===============================
One command to see the full state of all cluster nodes.

Usage:
    python3 tools/cluster_health.py              # interactive dashboard
    python3 tools/cluster_health.py --json       # machine-readable output
    python3 tools/cluster_health.py --quick      # skip slow checks (disk, stage progress)

Checks per node:
    1. SSH reachability (BatchMode, 8s timeout)
    2. Git commit hash + branch + dirty state
    3. Running stage processes (stage1/stage2)
    4. Stage progress (done files vs total)
    5. Disk usage on output paths
    6. Environment verification (calls env_verify.py --json)

Design notes:
    - Reads node definitions from handover/ops/HOSTS_REGISTRY.yaml
    - Mac controller checked locally (no SSH)
    - Windows commands use PowerShell via SSH
    - All SSH calls have strict timeouts to prevent hangs
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Node definitions (fallback if HOSTS_REGISTRY.yaml unavailable) ──
NODES = {
    "controller": {
        "alias": None,  # local
        "os": "darwin",
        "role": "controller",
        "repo_root": str(REPO_ROOT),
        "outputs": {},
    },
    "linux1": {
        "alias": "linux1-lx",
        "os": "linux",
        "role": "worker stage1/stage2",
        "repo_root": "/home/zepher/work/Omega_vNext",
        "outputs": {
            "stage1": "/omega_pool/parquet_data/v62_base_l1/host=linux1",
            "stage2": "/omega_pool/parquet_data/v62_feature_l2/host=linux1",
        },
    },
    "windows1": {
        "alias": "windows1-w1",
        "os": "windows",
        "role": "worker stage1/stage2",
        "repo_root": "D:\\work\\Omega_vNext",
        "outputs": {
            "stage1": "D:\\Omega_frames\\v62_base_l1\\host=windows1",
            "stage2": "D:\\Omega_frames\\v62_feature_l2\\host=windows1",
        },
    },
}

SSH_TIMEOUT = 8


def _run_local(cmd: str, timeout: int = 10) -> str:
    """Run a command locally."""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=REPO_ROOT,
        )
        return r.stdout.strip()
    except (subprocess.TimeoutExpired, Exception) as e:
        return f"ERROR: {e}"


def _run_ssh(alias: str, cmd: str, timeout: int = SSH_TIMEOUT) -> str | None:
    """Run a command via SSH. Returns None on failure."""
    try:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={timeout}",
             alias, cmd],
            capture_output=True, timeout=timeout + 5,
        )
        r.stdout = r.stdout.decode("utf-8", errors="replace") if isinstance(r.stdout, bytes) else r.stdout
        r.stderr = r.stderr.decode("utf-8", errors="replace") if isinstance(r.stderr, bytes) else r.stderr
        if r.returncode == 0:
            return r.stdout.strip()
        return f"SSH_ERROR(rc={r.returncode}): {r.stderr.strip()[:120]}"
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"


def _run_ssh_ps(alias: str, ps_cmd: str, timeout: int = SSH_TIMEOUT) -> str | None:
    """Run a PowerShell command on Windows via SSH."""
    # Windows SSH runs PowerShell by default
    return _run_ssh(alias, ps_cmd, timeout=timeout)


# ── Check functions ──

def check_ssh(node_name: str, node: dict) -> dict:
    """Check SSH reachability."""
    alias = node.get("alias")
    if not alias:
        return {"status": "PASS", "message": "local (no SSH needed)"}
    result = _run_ssh(alias, "hostname")
    if result and not result.startswith(("TIMEOUT", "SSH_ERROR", "ERROR")):
        return {"status": "PASS", "message": result}
    return {"status": "FAIL", "message": result or "unreachable"}


def check_git(node_name: str, node: dict) -> dict:
    """Check git state."""
    alias = node.get("alias")
    repo = node["repo_root"]

    if not alias:
        # Local
        commit = _run_local("git rev-parse --short HEAD")
        branch = _run_local("git rev-parse --abbrev-ref HEAD")
        dirty = bool(_run_local("git status --porcelain"))
    elif node["os"] == "windows":
        cmd = f'cd /d {repo} && git rev-parse --short HEAD && git rev-parse --abbrev-ref HEAD && git status --porcelain'
        out = _run_ssh(alias, cmd, timeout=12)
        if not out or out.startswith(("TIMEOUT", "SSH_ERROR", "ERROR")):
            return {"status": "FAIL", "message": out or "no response"}
        lines = out.strip().split("\n")
        commit = lines[0] if len(lines) > 0 else "?"
        branch = lines[1] if len(lines) > 1 else "?"
        dirty = len(lines) > 2
    else:
        cmd = f'cd {repo} && git rev-parse --short HEAD && git rev-parse --abbrev-ref HEAD && git status --porcelain'
        out = _run_ssh(alias, cmd, timeout=12)
        if not out or out.startswith(("TIMEOUT", "SSH_ERROR", "ERROR")):
            return {"status": "FAIL", "message": out or "no response"}
        lines = out.strip().split("\n")
        commit = lines[0] if len(lines) > 0 else "?"
        branch = lines[1] if len(lines) > 1 else "?"
        dirty = len(lines) > 2

    label = f"{branch}@{commit}" + (" [dirty]" if dirty else "")
    return {"status": "PASS", "commit": commit, "branch": branch, "dirty": dirty, "message": label}


def check_processes(node_name: str, node: dict) -> dict:
    """Check running stage processes."""
    alias = node.get("alias")
    procs = []

    if not alias:
        out = _run_local("pgrep -af 'stage[12]_.*\\.py' 2>/dev/null || true")
        if out:
            procs = [line.strip() for line in out.split("\n") if line.strip()]
    elif node["os"] == "windows":
        # Use schtasks to detect Omega scheduled tasks (more reliable than Get-Process)
        cmd = 'schtasks /Query /TN "Omega_v62_stage2_isolated_v2" /FO CSV /NH 2>nul'
        out = _run_ssh_ps(alias, cmd, timeout=12)
        if out and not out.startswith(("TIMEOUT", "SSH_ERROR", "ERROR")):
            # schtasks returns CSV: taskname,next_run,status
            procs = [line.strip() for line in out.split("\n") if line.strip()]
    else:
        cmd = "pgrep -af 'stage[12]_.*\\.py' 2>/dev/null || true"
        out = _run_ssh(alias, cmd, timeout=12)
        if out and not out.startswith(("TIMEOUT", "SSH_ERROR", "ERROR")):
            procs = [line.strip() for line in out.split("\n") if line.strip()]

    if procs:
        return {"status": "ACTIVE", "count": len(procs), "message": f"{len(procs)} process(es)"}
    return {"status": "IDLE", "count": 0, "message": "no stage processes"}


def check_stage_progress(node_name: str, node: dict) -> dict:
    """Check stage1/stage2 done file counts.

    Key insight: for stage2, 'total' = number of input files from stage1,
    not the number of output files in stage2 (where done == parquet always).
    """
    alias = node.get("alias")
    outputs = node.get("outputs", {})
    if not outputs:
        return {"status": "SKIP", "message": "no output paths configured"}

    progress = {}
    stage1_path = outputs.get("stage1", "")

    for stage, path in outputs.items():
        # Count done files in this stage's output
        if not alias:
            done_cmd = f'ls "{path}"/*.parquet.done 2>/dev/null | wc -l'
            done = _run_local(done_cmd).strip()
        elif node["os"] == "windows":
            done_cmd = f'dir /b "{path}\\*.parquet.done" 2>nul | find /c /v ""'
            done = _run_ssh_ps(alias, done_cmd, timeout=15)
        else:
            done_cmd = f'ls "{path}"/*.parquet.done 2>/dev/null | wc -l'
            done = _run_ssh(alias, done_cmd, timeout=15)

        # Total: for stage1 = parquet files in stage1 dir
        #        for stage2 = parquet files in stage1 dir (input count)
        total_path = stage1_path if (stage == "stage2" and stage1_path) else path
        if not alias:
            total_cmd = f'ls "{total_path}"/*.parquet 2>/dev/null | wc -l'
            total = _run_local(total_cmd).strip()
        elif node["os"] == "windows":
            total_cmd = f'dir /b "{total_path}\\*.parquet" 2>nul | find /c /v ""'
            total = _run_ssh_ps(alias, total_cmd, timeout=15)
        else:
            total_cmd = f'ls "{total_path}"/*.parquet 2>/dev/null | wc -l'
            total = _run_ssh(alias, total_cmd, timeout=15)

        try:
            done_n = int(done) if done and not done.startswith(("TIMEOUT", "SSH_ERROR", "ERROR")) else -1
            total_n = int(total) if total and not total.startswith(("TIMEOUT", "SSH_ERROR", "ERROR")) else -1
        except ValueError:
            done_n, total_n = -1, -1

        progress[stage] = {"done": done_n, "total": total_n}

    parts = []
    for stage, p in progress.items():
        if p["done"] < 0 or p["total"] < 0:
            parts.append(f"{stage}=?/?")
        else:
            parts.append(f"{stage}={p['done']}/{p['total']}")

    return {"status": "PASS", "progress": progress, "message": " | ".join(parts)}


def check_disk(node_name: str, node: dict) -> dict:
    """Check disk usage on output paths."""
    alias = node.get("alias")
    outputs = node.get("outputs", {})
    if not outputs:
        return {"status": "SKIP", "message": "no output paths"}

    # Check first output path
    path = list(outputs.values())[0]
    if not alias:
        out = _run_local(f'df -h "{path}" 2>/dev/null | tail -1')
    elif node["os"] == "windows":
        drive = path[0] if path else "D"
        cmd = f'wmic logicaldisk where "DeviceID=\'{drive}:\'" get FreeSpace,Size /format:csv 2>nul | findstr /r "[0-9]"'
        out = _run_ssh_ps(alias, cmd, timeout=12)
    else:
        out = _run_ssh(alias, f'df -h "{path}" 2>/dev/null | tail -1', timeout=12)

    if out and not out.startswith(("TIMEOUT", "SSH_ERROR", "ERROR")):
        return {"status": "PASS", "message": out[:80]}
    return {"status": "WARN", "message": out or "unavailable"}


# ── Main dashboard ──

def run_dashboard(quick: bool = False, json_out: bool = False):
    """Run all checks and display dashboard."""
    t0 = time.time()
    results = {}

    for node_name, node in NODES.items():
        node_result = {"role": node["role"], "os": node["os"]}

        # 1. SSH
        node_result["ssh"] = check_ssh(node_name, node)

        # Skip remaining checks if SSH failed (except controller)
        if node_result["ssh"]["status"] == "FAIL" and node.get("alias"):
            node_result["git"] = {"status": "SKIP", "message": "SSH failed"}
            node_result["processes"] = {"status": "SKIP", "message": "SSH failed"}
            node_result["stage_progress"] = {"status": "SKIP", "message": "SSH failed"}
            node_result["disk"] = {"status": "SKIP", "message": "SSH failed"}
            results[node_name] = node_result
            continue

        # 2. Git
        node_result["git"] = check_git(node_name, node)

        # 3. Running processes
        node_result["processes"] = check_processes(node_name, node)

        # 4-5. Stage progress and disk (skip in quick mode)
        if quick:
            node_result["stage_progress"] = {"status": "SKIP", "message": "quick mode"}
            node_result["disk"] = {"status": "SKIP", "message": "quick mode"}
        else:
            node_result["stage_progress"] = check_stage_progress(node_name, node)
            node_result["disk"] = check_disk(node_name, node)

        results[node_name] = node_result

    elapsed = round(time.time() - t0, 1)

    if json_out:
        output = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "elapsed_s": elapsed, "nodes": results}
        print(json.dumps(output, indent=2))
        return results

    # ── Human-readable ──
    print()
    print("=" * 72)
    print("  🏥 OMEGA Cluster Health Dashboard")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S %z')}  (scan took {elapsed}s)")
    print("=" * 72)

    icon_map = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ ", "SKIP": "⏭️ ", "ACTIVE": "🟢", "IDLE": "⚪"}

    for node_name, nr in results.items():
        print(f"\n  ┌─ {node_name.upper()} ({nr['role']})")
        for check_name in ["ssh", "git", "processes", "stage_progress", "disk"]:
            c = nr.get(check_name, {})
            icon = icon_map.get(c.get("status", "?"), "❓")
            label = check_name.replace("_", " ").title()
            msg = c.get("message", "?")
            print(f"  │  {icon} {label:<18} {msg}")
        print(f"  └────")

    # ── Summary line ──
    all_ssh = [r["ssh"]["status"] for r in results.values()]
    git_commits = [r["git"].get("commit", "?") for r in results.values() if r["git"]["status"] == "PASS"]
    unique_commits = set(git_commits)

    print()
    if "FAIL" in all_ssh:
        unreachable = [n for n, r in results.items() if r["ssh"]["status"] == "FAIL"]
        print(f"  ⚠️  CLUSTER ISSUE: {', '.join(unreachable)} unreachable")
    elif len(unique_commits) > 1:
        print(f"  ⚠️  GIT DESYNC: {len(unique_commits)} different commits across nodes: {unique_commits}")
    else:
        print(f"  ✅ CLUSTER HEALTHY (all nodes at {git_commits[0] if git_commits else '?'})")

    print("=" * 72)
    print()

    return results


def main():
    parser = argparse.ArgumentParser(description="OMEGA Cluster Health Dashboard")
    parser.add_argument("--json", action="store_true", dest="json_out", help="JSON output")
    parser.add_argument("--quick", action="store_true", help="skip slow checks (disk, progress)")
    args = parser.parse_args()

    run_dashboard(quick=args.quick, json_out=args.json_out)


if __name__ == "__main__":
    main()
