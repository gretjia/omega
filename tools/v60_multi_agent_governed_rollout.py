#!/usr/bin/env python3
"""
Governed rollout for v60 multi-agent operations.

Required sequence:
1) Constitution preflight.
2) Smoke gate.
3) Dual independent recursive audits.
4) Execute only when both auditors return PASS.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "handover" / "ai-direct" / "live"
CONSTITUTION = ROOT / "audit" / "constitution_v2.md"
RECURSIVE_PROMPTS = ROOT / "audit" / "runtime" / "multi_agent" / "recursive_audit_prompts.md"
RAW_CONTEXT = LIVE / "01_Raw_Context.md"
MECHANIC_PATCH = LIVE / "03_Mechanic_Patch.md"
AUDIT_A = LIVE / "04A_Gemini_Recursive_Audit.md"
AUDIT_B = LIVE / "04B_Codex_Recursive_Audit.md"
AUDIT_DECISION = LIVE / "05_Final_Audit_Decision.md"
LEGACY_CONSTITUTION = ROOT / "OMEGA_CONSTITUTION.md"
PROJECT_README = ROOT / "README.md"
MULTI_AGENTS_DOC = ROOT / "audit" / "multi_agents.md"
PRINCIPLES = ROOT / ".agent" / "principles.yaml"
ROLLOUT_SCRIPT = ROOT / "tools" / "v60_multi_agent_governed_rollout.py"
TICK_SCRIPT = ROOT / "tools" / "v60_multi_agent_tick.py"
CRON_SCRIPT = ROOT / "tools" / "v60_install_multi_agents_cron.sh"
RESEARCH_BASIS = ROOT / "audit" / "runtime" / "v60" / "v60_multi_agent_research_basis_20260219.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def current_git_hash() -> str:
    r = run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, timeout=20)
    g = (r.stdout or "").strip()
    return g if g else "unknown"


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    stdin_text: str | None = None,
    timeout: int = 3600,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=str(cwd or ROOT),
            input=stdin_text,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "")
        err = (exc.stderr or "")
        return subprocess.CompletedProcess(cmd, 124, out, f"{err}\nTimeoutExpired: {timeout}s")


def ensure_required_files() -> None:
    missing = [
        p
        for p in (
            CONSTITUTION,
            LEGACY_CONSTITUTION,
            PROJECT_README,
            MULTI_AGENTS_DOC,
            PRINCIPLES,
            RECURSIVE_PROMPTS,
            RAW_CONTEXT,
            MECHANIC_PATCH,
            ROLLOUT_SCRIPT,
            TICK_SCRIPT,
            CRON_SCRIPT,
            RESEARCH_BASIS,
        )
        if not p.exists()
    ]
    if missing:
        raise SystemExit("Missing required files:\n" + "\n".join(str(p) for p in missing))


def build_audit_bundle() -> str:
    parts: list[str] = []
    files: list[tuple[Path, int]] = [
        (CONSTITUTION, 220),
        (LEGACY_CONSTITUTION, 220),
        (PROJECT_README, 220),
        (MULTI_AGENTS_DOC, 260),
        (PRINCIPLES, 260),
        (RECURSIVE_PROMPTS, 260),
        (RAW_CONTEXT, 260),
        (MECHANIC_PATCH, 260),
        (ROLLOUT_SCRIPT, 9999),
        (TICK_SCRIPT, 9999),
        (CRON_SCRIPT, 9999),
        (RESEARCH_BASIS, 260),
    ]
    for p, max_lines in files:
        parts.append(f"\n\n===== BEGIN {p} =====\n")
        text = p.read_text(encoding="utf-8", errors="replace")
        if max_lines > 0:
            lines = text.splitlines()
            if len(lines) > max_lines:
                text = "\n".join(lines[:max_lines]) + f"\n... [truncated after {max_lines} lines]\n"
        parts.append(text)
        parts.append(f"\n===== END {p} =====\n")
    return "".join(parts)


def extract_verdict(text: str) -> str:
    m = re.search(r"VERDICT:\s*(PASS|REJECT)\b", text, flags=re.IGNORECASE)
    return (m.group(1).upper() if m else "UNKNOWN")


def run_smoke(
    hashv: str,
    event_log: Path,
    state_path: Path,
    debug_dir: Path,
    *,
    linux_git_sync: str,
    linux_git_ref: str,
) -> list[tuple[str, int, str]]:
    checks: list[tuple[str, int, str]] = []
    cmd1 = [
        "python3",
        ".codex/skills/multi-agent-ops/scripts/deploy_and_check.py",
        "--repair",
    ]
    r1 = run(cmd1, timeout=1200)
    checks.append(("deploy_and_check --repair", r1.returncode, (r1.stdout + "\n" + r1.stderr).strip()))

    cmd2 = ["python3", "-m", "py_compile", "tools/v60_multi_agent_tick.py", "tools/v60_multi_agent_governed_rollout.py"]
    r2 = run(cmd2, timeout=120)
    checks.append(("py_compile", r2.returncode, (r2.stdout + "\n" + r2.stderr).strip()))

    roles = ["windows-monitor", "linux-bootstrap", "linux-monitor", "autopilot-gate"]
    for role in roles:
        cmd = [
            "python3",
            "tools/v60_multi_agent_tick.py",
            "--hash",
            hashv,
            "--role",
            role,
            "--state-path",
            str(state_path),
            "--event-log",
            str(event_log),
            "--debug-dir",
            str(debug_dir),
            "--linux-git-sync",
            linux_git_sync,
            "--linux-git-ref",
            linux_git_ref,
            "--dry-run",
            "--strict-exit",
        ]
        r = run(cmd, timeout=420)
        checks.append((f"tick dry-run {role}", r.returncode, (r.stdout + "\n" + r.stderr).strip()))
    return checks


def run_dual_audit() -> tuple[int, str, int, str]:
    bundle = build_audit_bundle()
    gemini_prompt = (
        "You are Recursive Auditor A. "
        "Use only the provided stdin bundle. "
        "Independent audit only: do not read other auditor outputs. "
        "Perform recursive audit depth >=2 and output sections with VERDICT: PASS|REJECT."
    )
    codex_prompt = (
        "You are Recursive Auditor B. "
        "Use only the provided stdin bundle. "
        "Independent audit only: do not read other auditor outputs. "
        "Perform recursive audit depth >=2. "
        "Output sections: VERDICT, Critical Findings, Constitution Alignment, Operational Risk, Required Fixes, Re-check Commands."
    )

    # Run both auditors first, then publish 04A/04B together to reduce cross-read leakage.
    with tempfile.TemporaryDirectory(prefix="v60_dual_audit_") as tdir:
        tmp_b = Path(tdir) / "codex_b.md"
        cb = run(
            [
                "codex",
                "exec",
                "-C",
                str(ROOT),
                "-m",
                "gpt-5.3-codex",
                "-c",
                'model_reasoning_effort="xhigh"',
                "-s",
                "read-only",
                "-o",
                str(tmp_b),
                "-",
            ],
            stdin_text=bundle + "\n\n" + codex_prompt + "\n",
            timeout=1500,
        )
        b_text = tmp_b.read_text(encoding="utf-8", errors="replace") if tmp_b.exists() else (cb.stdout + "\n" + cb.stderr)

    ga = run(
        ["gemini", "--approval-mode", "plan", "--output-format", "text", "-p", gemini_prompt],
        stdin_text=bundle,
        timeout=900,
    )
    a_text = (ga.stdout + "\n" + ga.stderr).strip()

    git_hash = current_git_hash()
    meta = (
        "- task_id: TASK-20260219-V60-MULTI-AGENT-GOVERNED-ROLLOUT\n"
        f"- git_hash: {git_hash}\n"
        f"- timestamp_utc: {now_utc()}\n\n"
    )
    AUDIT_A.write_text("# 04A Gemini Recursive Audit\n\n" + meta + (a_text or "").strip() + "\n", encoding="utf-8")
    AUDIT_B.write_text("# 04B Codex Recursive Audit\n\n" + meta + (b_text or "").strip() + "\n", encoding="utf-8")
    return ga.returncode, a_text, cb.returncode, b_text


def write_decision(*, smoke_ok: bool, verdict_a: str, verdict_b: str, executed: bool, hashv: str) -> None:
    git_hash = current_git_hash()
    status = "PASS" if smoke_ok and verdict_a == "PASS" and verdict_b == "PASS" else "REJECT"
    text = (
        "# 05 Final Audit Decision\n\n"
        f"- task_id: TASK-20260219-V60-MULTI-AGENT-GOVERNED-ROLLOUT\n"
        f"- git_hash: {git_hash}\n"
        f"- timestamp_utc: {now_utc()}\n\n"
        "## Decision\n"
        f"- verdict: {status}\n"
        f"- smoke_gate: {'PASS' if smoke_ok else 'REJECT'}\n"
        f"- recursive_auditor_A: {verdict_a}\n"
        f"- recursive_auditor_B: {verdict_b}\n"
        f"- execute_after_audit: {'YES' if executed else 'NO'}\n"
        f"- run_hash: {hashv}\n"
    )
    AUDIT_DECISION.write_text(text, encoding="utf-8")


def execute_live(
    hashv: str,
    event_log: Path,
    state_path: Path,
    debug_dir: Path,
    *,
    linux_git_sync: str,
    linux_git_ref: str,
) -> list[tuple[str, int, str]]:
    steps: list[tuple[str, int, str]] = []
    inst = run(["bash", "tools/v60_install_multi_agents_cron.sh", hashv], timeout=120)
    steps.append(("install_cron", inst.returncode, (inst.stdout + "\n" + inst.stderr).strip()))
    for role in ("windows-monitor", "linux-bootstrap", "linux-monitor", "autopilot-gate"):
        cmd = [
            "python3",
            "tools/v60_multi_agent_tick.py",
            "--hash",
            hashv,
            "--role",
            role,
            "--state-path",
            str(state_path),
            "--event-log",
            str(event_log),
            "--debug-dir",
            str(debug_dir),
            "--linux-git-sync",
            linux_git_sync,
            "--linux-git-ref",
            linux_git_ref,
        ]
        if role in ("windows-monitor", "linux-monitor"):
            cmd.append("--trigger-debug-agent")
        r = run(cmd, timeout=420)
        steps.append((f"tick live {role}", r.returncode, (r.stdout + "\n" + r.stderr).strip()))
    return steps


def main() -> int:
    ap = argparse.ArgumentParser(description="Governed v60 multi-agent rollout")
    ap.add_argument("--hash", default="aa8abb7")
    ap.add_argument("--execute", action="store_true", help="execute live rollout after smoke + dual PASS")
    ap.add_argument("--state-path", default="")
    ap.add_argument("--event-log", default="")
    ap.add_argument("--debug-dir", default="")
    ap.add_argument("--linux-git-sync", choices=["none", "pull", "pin"], default="none")
    ap.add_argument("--linux-git-ref", default="")
    args = ap.parse_args()

    ensure_required_files()

    state_path = Path(args.state_path) if args.state_path else ROOT / "audit" / "runtime" / "v60" / f"multi_agents_{args.hash}.state.json"
    event_log = Path(args.event_log) if args.event_log else ROOT / "audit" / "runtime" / "v60" / f"multi_agents_{args.hash}.events.log"
    debug_dir = Path(args.debug_dir) if args.debug_dir else ROOT / "audit" / "runtime" / "v60" / "incidents"

    smoke_checks = run_smoke(
        args.hash,
        event_log,
        state_path,
        debug_dir,
        linux_git_sync=args.linux_git_sync,
        linux_git_ref=args.linux_git_ref,
    )
    smoke_ok = all(rc == 0 for _, rc, _ in smoke_checks)

    ga_rc, ga_text, cb_rc, cb_text = run_dual_audit()
    verdict_a = extract_verdict(ga_text)
    verdict_b = extract_verdict(cb_text)
    dual_pass = (ga_rc == 0 and cb_rc == 0 and verdict_a == "PASS" and verdict_b == "PASS")

    executed = False
    live_steps: list[tuple[str, int, str]] = []
    if args.execute and smoke_ok and dual_pass:
        live_steps = execute_live(
            args.hash,
            event_log,
            state_path,
            debug_dir,
            linux_git_sync=args.linux_git_sync,
            linux_git_ref=args.linux_git_ref,
        )
        executed = all(rc == 0 for _, rc, _ in live_steps)

    write_decision(
        smoke_ok=smoke_ok,
        verdict_a=verdict_a,
        verdict_b=verdict_b,
        executed=executed,
        hashv=args.hash,
    )

    print("=== Governed Rollout Summary ===")
    print(f"smoke_ok={smoke_ok}")
    for name, rc, _ in smoke_checks:
        print(f"[smoke] {name}: rc={rc}")
    print(f"[audit] gemini_rc={ga_rc} verdict={verdict_a}")
    print(f"[audit] codex_rc={cb_rc} verdict={verdict_b}")
    if args.execute:
        print(f"execute_requested=yes executed={executed}")
        for name, rc, _ in live_steps:
            print(f"[execute] {name}: rc={rc}")
    else:
        print("execute_requested=no")

    if not smoke_ok:
        return 2
    if not dual_pass:
        return 3
    if args.execute and not executed:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
