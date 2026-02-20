#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LEDGER = ROOT / "handover" / "DEBUG_LESSONS.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ledger_template() -> str:
    return (
        "# Debug Lessons Ledger\n\n"
        "This file is the shared anti-regression memory for all agents.\n"
        "Write only reproducible, technical lessons.\n\n"
        "## Entry Template\n\n"
        "## 0000-00-00T00:00:00Z | short_title\n"
        "- task_id: TODO\n"
        "- git_hash: TODO\n"
        "- role: debug_scribe\n"
        "- model_profile: codex_medium\n"
        "- auto_key: optional_for_auto_entries\n"
        "- symptom: TODO\n"
        "- root_cause: TODO\n"
        "- fix: TODO\n"
        "- guardrail: TODO\n"
        "- refs: TODO\n"
    )


def _clean(value: str) -> str:
    return " ".join(value.strip().split())


def _refs(value: str) -> str:
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        return "N/A"
    return ", ".join(f"`{item}`" for item in items)


def ensure_ledger() -> None:
    if LEDGER.exists():
        return
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(ledger_template(), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Append a debug lesson entry for cross-agent learning")
    ap.add_argument("--title", required=True, help="Short lesson title")
    ap.add_argument("--task-id", default="N/A", help="Task or issue identifier")
    ap.add_argument("--git-hash", default="N/A", help="Git hash for this lesson context")
    ap.add_argument("--model-profile", default="codex_medium", help="Role profile used by debug scribe")
    ap.add_argument("--auto-key", default="", help="Optional deterministic dedupe key")
    ap.add_argument("--symptom", required=True, help="Observed failure symptom")
    ap.add_argument("--root-cause", required=True, help="Root cause summary")
    ap.add_argument("--fix", required=True, help="Applied fix summary")
    ap.add_argument("--guardrail", required=True, help="Regression-prevention guardrail")
    ap.add_argument("--refs", default="", help="Comma-separated file paths or commands")
    args = ap.parse_args()

    ensure_ledger()
    ts = now_utc()
    auto_key = _clean(args.auto_key)
    auto_key_line = f"- auto_key: {auto_key}\n" if auto_key else ""
    block = (
        f"\n## {ts} | {_clean(args.title)}\n"
        f"- task_id: {_clean(args.task_id)}\n"
        f"- git_hash: {_clean(args.git_hash)}\n"
        "- role: debug_scribe\n"
        f"- model_profile: {_clean(args.model_profile)}\n"
        f"{auto_key_line}"
        f"- symptom: {_clean(args.symptom)}\n"
        f"- root_cause: {_clean(args.root_cause)}\n"
        f"- fix: {_clean(args.fix)}\n"
        f"- guardrail: {_clean(args.guardrail)}\n"
        f"- refs: {_refs(args.refs)}\n"
    )

    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(block)

    print(f"Appended debug lesson: {ts}")
    print(f"Ledger: {LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
