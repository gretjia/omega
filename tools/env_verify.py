#!/usr/bin/env python3
"""
OMEGA Environment Verification Tool
====================================
Validates that all required dependencies are installed with correct versions.
Run this BEFORE any Stage1/Stage2/Stage3 work to catch missing dependencies early.

Usage:
    python3 tools/env_verify.py                  # interactive check
    python3 tools/env_verify.py --strict         # exit(1) on any mismatch
    python3 tools/env_verify.py --json           # machine-readable output
    python3 tools/env_verify.py --fix            # print pip install command for fixes

Exit codes:
    0 = all checks passed
    1 = at least one check failed (--strict mode)
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import platform
import sys
from pathlib import Path

# ── Required packages: (import_name, pip_name, min_version, pinned_version) ──
REQUIRED_PACKAGES = [
    ("polars",    "polars",       "1.0.0",    "1.36.1"),
    ("numpy",     "numpy",        "1.26.0",   "1.26.4"),
    ("pyarrow",   "pyarrow",      "14.0.0",   "21.0.0"),
    ("numba",     "numba",        "0.58.0",   "0.60.0"),
    ("llvmlite",  "llvmlite",     "0.41.0",   "0.43.0"),
    ("sklearn",   "scikit-learn", "1.4.0",    "1.6.1"),
    ("xgboost",   "xgboost",     "2.0.0",    "2.1.4"),
    ("pandas",    "pandas",       "2.0.0",    "2.3.3"),
    ("psutil",    "psutil",       "5.9.0",    "7.2.1"),
    ("yaml",      "PyYAML",       "6.0.0",    "6.0.3"),
]


def _parse_version(v: str) -> tuple:
    """Parse version string into comparable tuple."""
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(p)
    return tuple(parts)


def check_package(import_name: str, pip_name: str, min_ver: str, pinned_ver: str) -> dict:
    """Check a single package. Returns status dict."""
    result = {
        "package": pip_name,
        "import_name": import_name,
        "pinned": pinned_ver,
        "min": min_ver,
    }
    try:
        mod = importlib.import_module(import_name)
        installed = getattr(mod, "__version__", "unknown")
        result["installed"] = installed

        if installed == "unknown":
            result["status"] = "WARN"
            result["message"] = "version attribute missing"
        elif _parse_version(installed) < _parse_version(min_ver):
            result["status"] = "FAIL"
            result["message"] = f"below minimum {min_ver}"
        elif installed != pinned_ver:
            result["status"] = "WARN"
            result["message"] = f"differs from pinned {pinned_ver}"
        else:
            result["status"] = "PASS"
            result["message"] = "exact match"
    except ImportError:
        result["installed"] = None
        result["status"] = "FAIL"
        result["message"] = "NOT INSTALLED"

    return result


def check_python_version() -> dict:
    """Verify Python version is 3.10+."""
    ver = platform.python_version()
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 10):
        return {"status": "FAIL", "installed": ver, "message": "Python >= 3.10 required"}
    return {"status": "PASS", "installed": ver, "message": "OK"}


def check_git_state(repo_root: Path) -> dict:
    """Check git HEAD commit hash."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root, capture_output=True, text=True, timeout=5,
        )
        commit = result.stdout.strip() if result.returncode == 0 else "unknown"
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root, capture_output=True, text=True, timeout=5,
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        dirty_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root, capture_output=True, text=True, timeout=5,
        )
        dirty = bool(dirty_result.stdout.strip())
        return {
            "status": "PASS",
            "commit": commit,
            "branch": branch,
            "dirty": dirty,
            "message": f"{branch}@{commit}" + (" [dirty]" if dirty else ""),
        }
    except Exception as e:
        return {"status": "WARN", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="OMEGA Environment Verification")
    parser.add_argument("--strict", action="store_true", help="exit(1) on any failure")
    parser.add_argument("--json", action="store_true", dest="json_out", help="JSON output")
    parser.add_argument("--fix", action="store_true", help="print pip install command for fixes")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    # ── Gather results ──
    results = []
    py_result = check_python_version()
    git_result = check_git_state(repo_root)

    for import_name, pip_name, min_ver, pinned_ver in REQUIRED_PACKAGES:
        results.append(check_package(import_name, pip_name, min_ver, pinned_ver))

    # ── Count ──
    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]
    passes = [r for r in results if r["status"] == "PASS"]

    # ── JSON output ──
    if args.json_out:
        report = {
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.machine()}",
            "python": py_result,
            "git": git_result,
            "packages": results,
            "summary": {
                "pass": len(passes),
                "warn": len(warns),
                "fail": len(fails),
                "ok": len(fails) == 0,
            },
        }
        print(json.dumps(report, indent=2))
        if args.strict and fails:
            sys.exit(1)
        return

    # ── Human-readable output ──
    print("=" * 60)
    print("  OMEGA Environment Verification")
    print(f"  Host: {platform.node()} ({platform.system()} {platform.machine()})")
    print(f"  Python: {py_result['installed']}  [{py_result['status']}]")
    print(f"  Git: {git_result.get('message', 'N/A')}")
    print("=" * 60)

    for r in results:
        icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}[r["status"]]
        installed_str = r.get("installed") or "MISSING"
        print(f"  {icon} {r['package']:<16} installed={installed_str:<10} pinned={r['pinned']:<10} {r['message']}")

    print("-" * 60)
    summary = f"  PASS={len(passes)}  WARN={len(warns)}  FAIL={len(fails)}"
    if fails:
        print(f"  ❌ ENVIRONMENT CHECK FAILED  {summary}")
    elif warns:
        print(f"  ⚠️  ENVIRONMENT CHECK PASSED (with warnings)  {summary}")
    else:
        print(f"  ✅ ENVIRONMENT CHECK PASSED  {summary}")
    print("=" * 60)

    # ── Fix suggestion ──
    if args.fix and fails:
        missing = [r["package"] + "==" + r["pinned"] for r in fails]
        print(f"\n  Fix command:\n  pip install {' '.join(missing)}\n")
    elif fails:
        print("\n  Run with --fix to see the install command.\n")

    if args.strict and fails:
        sys.exit(1)


if __name__ == "__main__":
    main()
