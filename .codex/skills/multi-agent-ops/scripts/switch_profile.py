#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]

PROFILES_CANON = ROOT / "audit" / "runtime" / "multi_agent" / "agent_profiles.yaml"
PROFILES_LEGACY = ROOT / "audit" / "runtime" / "v60" / "agent_profiles.yaml"
LATEST = ROOT / "handover" / "ai-direct" / "LATEST.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_cfg() -> dict:
    if PROFILES_CANON.exists():
        return yaml.safe_load(PROFILES_CANON.read_text(encoding="utf-8")) or {}
    if PROFILES_LEGACY.exists():
        cfg = yaml.safe_load(PROFILES_LEGACY.read_text(encoding="utf-8")) or {}
        PROFILES_CANON.parent.mkdir(parents=True, exist_ok=True)
        PROFILES_CANON.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=False), encoding="utf-8")
        return cfg
    raise SystemExit(f"Missing profiles file: {PROFILES_CANON}")


def _write_cfg(cfg: dict) -> None:
    PROFILES_CANON.parent.mkdir(parents=True, exist_ok=True)
    txt = yaml.safe_dump(cfg, sort_keys=False, allow_unicode=False)
    PROFILES_CANON.write_text(txt, encoding="utf-8")

    # legacy mirror for backward compatibility
    PROFILES_LEGACY.parent.mkdir(parents=True, exist_ok=True)
    PROFILES_LEGACY.write_text(txt, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Switch active multi-agent profiles")
    ap.add_argument("--oracle", default="", help="Oracle profile name")
    ap.add_argument("--mechanic", default="", help="Mechanic profile name")
    ap.add_argument("--auditor-primary", default="", help="Primary auditor profile name")
    ap.add_argument("--auditor-secondary", default="", help="Secondary auditor profile name")
    ap.add_argument("--debug-scribe", default="", help="Debug scribe profile name")
    ap.add_argument("--auditor", default="", help="Legacy single-auditor profile (only if role 'auditor' exists)")
    ap.add_argument("--no-log", action="store_true", help="Skip writing handover LATEST.md log")
    args = ap.parse_args()

    cfg = _load_cfg()
    if not isinstance(cfg, dict):
        raise SystemExit("Invalid profiles yaml root")

    roles = cfg.get("roles", {})
    active = cfg.setdefault("active", {})

    updates = {
        "oracle": args.oracle.strip(),
        "mechanic": args.mechanic.strip(),
        "auditor_primary": args.auditor_primary.strip(),
        "auditor_secondary": args.auditor_secondary.strip(),
        "debug_scribe": args.debug_scribe.strip(),
    }

    legacy = args.auditor.strip()
    if legacy:
        if "auditor" in roles:
            updates["auditor"] = legacy
        else:
            raise SystemExit("--auditor is legacy-only. Use --auditor-primary/--auditor-secondary.")

    applied: list[str] = []
    for role, profile in updates.items():
        if not profile:
            continue
        role_cfg = roles.get(role)
        if not isinstance(role_cfg, dict):
            raise SystemExit(f"Role not found: {role}")
        profiles = role_cfg.get("profiles", {})
        if profile not in profiles:
            valid = ", ".join(sorted(profiles.keys()))
            raise SystemExit(f"Unknown profile '{profile}' for role '{role}'. Valid: {valid}")
        old = active.get(role, "")
        if old == profile:
            continue
        active[role] = profile
        applied.append(f"{role}:{old}->{profile}")

    if not applied:
        print("No changes requested.")
        return 0

    _write_cfg(cfg)
    print("Applied:")
    for item in applied:
        print(f"- {item}")

    if not args.no_log:
        LATEST.parent.mkdir(parents=True, exist_ok=True)
        with LATEST.open("a", encoding="utf-8") as f:
            f.write("\n")
            f.write(f"- [{now_utc()}] model_switch: {'; '.join(applied)}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
