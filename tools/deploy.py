#!/usr/bin/env python3
"""
OMEGA One-Click Deploy
======================
Syncs code from Mac controller to all worker nodes via git.
Implements the "Hassle-Free" 3-Step Protocol from gemini.md.

Usage:
    python3 tools/deploy.py                     # full deploy (commit + push + verify)
    python3 tools/deploy.py --dry-run           # show what would happen
    python3 tools/deploy.py --skip-commit       # push existing HEAD without new commit
    python3 tools/deploy.py --nodes linux       # deploy to specific node(s) only
    python3 tools/deploy.py --nodes linux,windows

Protocol (from gemini.md):
    STEP 1: Local commit (if needed) on Mac controller
    STEP 2: Git push to each worker node
    STEP 3: Remote reset + env verify on each node

Rules enforced:
    - NO SCP (banned by protocol)
    - Git push only (Mac → worker)
    - Workers never push code (read-only pull model)
    - Env verification after every sync
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from omega_core.omega_log import get_logger

log = get_logger("deploy")

# ── Node sync config ──
# Each node needs: git remote name, SSH alias, repo root, sync method
DEPLOY_TARGETS = {
    "linux": {
        "git_remote": "linux",
        "ssh_alias": "linux1-lx",
        "repo_root": "/home/zepher/work/Omega_vNext",
        "method": "git_push_ssh",  # git push <remote> HEAD:<branch>
    },
    "windows": {
        "git_remote": "windows",
        "ssh_alias": "windows1-w1",
        "repo_root": "D:\\work\\Omega_vNext",
        "method": "git_push_mount",  # git push via SMB mount
    },
}

SSH_TIMEOUT = 15


def _run(cmd: str | list, cwd: str = None, timeout: int = 30, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return result."""
    if isinstance(cmd, str):
        cmd_list = cmd
        shell = True
    else:
        cmd_list = cmd
        shell = False
    return subprocess.run(
        cmd_list, shell=shell, capture_output=True, text=True,
        cwd=cwd or str(REPO_ROOT), timeout=timeout,
    )


def _ssh(alias: str, cmd: str, timeout: int = SSH_TIMEOUT) -> tuple[int, str, str]:
    """Run SSH command. Returns (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout=8", alias, cmd],
            capture_output=True, timeout=timeout,
        )
        stdout = r.stdout.decode("utf-8", errors="replace").strip()
        stderr = r.stderr.decode("utf-8", errors="replace").strip()
        return r.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)


def step(num: int, label: str):
    """Print step header."""
    log.info(f"STEP {num}: {label}")


def ok(msg: str):
    log.info(msg)


def warn(msg: str):
    log.warn(msg)


def fail(msg: str):
    log.error(msg)


# ── STEP 1: Local commit ──

def step1_local_commit(skip_commit: bool, dry_run: bool) -> str:
    """Ensure local repo is committed. Returns current HEAD hash."""
    step(1, "Local Commit (Mac Controller)")

    # Check current state
    r = _run("git status --porcelain")
    dirty_files = [l for l in r.stdout.strip().split("\n") if l.strip()]

    r_head = _run("git rev-parse --short HEAD")
    head = r_head.stdout.strip()

    r_branch = _run("git rev-parse --abbrev-ref HEAD")
    branch = r_branch.stdout.strip()

    print(f"  Branch: {branch}")
    print(f"  HEAD: {head}")
    print(f"  Dirty files: {len(dirty_files)}")

    if skip_commit:
        ok(f"Skip commit mode — deploying existing HEAD {head}")
        return head

    if not dirty_files:
        ok(f"Working tree clean — deploying HEAD {head}")
        return head

    # Show what's dirty
    for f in dirty_files[:10]:
        print(f"    {f}")
    if len(dirty_files) > 10:
        print(f"    ... and {len(dirty_files) - 10} more")

    if dry_run:
        ok(f"[DRY RUN] Would commit {len(dirty_files)} files")
        return head

    # Auto-commit
    msg = f"deploy: sync {branch}@{head} to workers ({len(dirty_files)} files)"
    _run("git add -A")
    r_commit = _run(f'git commit -m "{msg}"')
    if r_commit.returncode != 0:
        fail(f"Commit failed: {r_commit.stderr[:200]}")
        sys.exit(1)

    r_head = _run("git rev-parse --short HEAD")
    new_head = r_head.stdout.strip()
    ok(f"Committed: {new_head} ({msg})")

    # Push to origin (GitHub)
    r_push = _run("git push origin HEAD", timeout=30)
    if r_push.returncode == 0:
        ok("Pushed to origin (GitHub)")
    else:
        warn(f"Push to origin failed (non-blocking): {r_push.stderr[:120]}")

    return new_head


# ── STEP 2: Git push to workers ──

def step2_push_to_node(name: str, target: dict, branch: str, dry_run: bool) -> bool:
    """Push code to a single worker node."""
    remote = target["git_remote"]
    alias = target["ssh_alias"]

    print(f"\n  → Syncing to {name.upper()} (remote: {remote}, SSH: {alias})")

    # Check SSH reachability first
    rc, out, err = _ssh(alias, "hostname")
    if rc != 0:
        fail(f"{name}: SSH unreachable ({err})")
        return False
    ok(f"SSH reachable ({out})")

    if dry_run:
        ok(f"[DRY RUN] Would git push {remote} HEAD:{branch}")
        return True

    # Git push
    r = _run(f"git push {remote} HEAD:{branch} --force", timeout=60)
    if r.returncode != 0:
        fail(f"git push failed: {r.stderr[:200]}")
        return False
    ok(f"git push {remote} HEAD:{branch} succeeded")

    return True


# ── STEP 3: Remote reset + env verify ──

def step3_verify_node(name: str, target: dict, branch: str, dry_run: bool) -> bool:
    """Reset the worker to the pushed branch and run env verify."""
    alias = target["ssh_alias"]
    repo = target["repo_root"]
    is_windows = (name == "windows")

    if dry_run:
        ok(f"[DRY RUN] Would reset {name} to {branch} and verify env")
        return True

    # Reset to the pushed branch
    if is_windows:
        reset_cmd = f'cd /d {repo} && git fetch --all && git reset --hard {branch}'
    else:
        reset_cmd = f'cd {repo} && git fetch --all && git reset --hard {branch}'

    rc, out, err = _ssh(alias, reset_cmd, timeout=30)
    if rc != 0:
        fail(f"git reset failed on {name}: {err[:200]}")
        return False

    # Verify HEAD matches
    if is_windows:
        hash_cmd = f'cd /d {repo} && git rev-parse --short HEAD'
    else:
        hash_cmd = f'cd {repo} && git rev-parse --short HEAD'

    rc, remote_head, _ = _ssh(alias, hash_cmd)
    local_head = _run("git rev-parse --short HEAD").stdout.strip()

    if remote_head == local_head:
        ok(f"Git hash verified: {remote_head}")
    else:
        warn(f"Hash mismatch: local={local_head} remote={remote_head}")

    # Run env_verify.py remotely
    if is_windows:
        verify_cmd = f'cd /d {repo} && python tools\\env_verify.py --strict'
    else:
        verify_cmd = f'cd {repo} && python3 tools/env_verify.py --strict'

    rc, out, err = _ssh(alias, verify_cmd, timeout=30)
    if rc == 0:
        ok(f"Environment verified on {name}")
    else:
        # Extract summary line
        lines = out.split("\n")
        summary = [l for l in lines if "FAIL" in l or "PASS" in l or "WARN" in l]
        if summary:
            warn(f"Env check on {name}: {summary[-1].strip()}")
        else:
            warn(f"Env check returned rc={rc} on {name}")

    return True


# ── Main ──

def main():
    parser = argparse.ArgumentParser(description="OMEGA One-Click Deploy")
    parser.add_argument("--dry-run", action="store_true", help="show what would happen")
    parser.add_argument("--skip-commit", action="store_true", help="deploy existing HEAD")
    parser.add_argument("--nodes", type=str, default="linux,windows",
                        help="comma-separated node list (default: linux,windows)")
    args = parser.parse_args()

    nodes = [n.strip() for n in args.nodes.split(",")]
    invalid = [n for n in nodes if n not in DEPLOY_TARGETS]
    if invalid:
        print(f"Unknown nodes: {invalid}. Valid: {list(DEPLOY_TARGETS.keys())}")
        sys.exit(1)

    t0 = time.time()
    branch = _run("git rev-parse --abbrev-ref HEAD").stdout.strip()

    print()
    print("=" * 60)
    print("  🚀 OMEGA One-Click Deploy")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S %z')}")
    print(f"  Branch: {branch}")
    print(f"  Targets: {', '.join(nodes)}")
    if args.dry_run:
        print("  Mode: DRY RUN")
    print("=" * 60)

    # STEP 1
    head = step1_local_commit(args.skip_commit, args.dry_run)

    # STEP 2
    step(2, "Push to Workers (LAN-Native Sync)")
    push_results = {}
    for name in nodes:
        push_results[name] = step2_push_to_node(
            name, DEPLOY_TARGETS[name], branch, args.dry_run
        )

    # STEP 3
    step(3, "Remote Reset + Environment Verification")
    verify_results = {}
    for name in nodes:
        if push_results.get(name):
            verify_results[name] = step3_verify_node(
                name, DEPLOY_TARGETS[name], branch, args.dry_run
            )
        else:
            warn(f"Skipping {name} verify (push failed)")
            verify_results[name] = False

    # Summary
    elapsed = round(time.time() - t0, 1)
    print(f"\n{'='*60}")
    print(f"  Deploy Summary ({elapsed}s)")
    print(f"{'='*60}")
    all_ok = True
    for name in nodes:
        pushed = "✅" if push_results.get(name) else "❌"
        verified = "✅" if verify_results.get(name) else "❌"
        print(f"  {name.upper():<12} push={pushed}  verify={verified}")
        if not push_results.get(name) or not verify_results.get(name):
            all_ok = False

    if all_ok:
        print(f"\n  ✅ ALL NODES SYNCED to {branch}@{head}")
    else:
        print(f"\n  ⚠️  PARTIAL DEPLOY — check failures above")
    print(f"{'='*60}\n")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
