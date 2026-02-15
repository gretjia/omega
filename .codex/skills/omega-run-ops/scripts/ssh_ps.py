#!/usr/bin/env python3
"""
ssh_ps.py

Run PowerShell over SSH without quoting pain by using -EncodedCommand (UTF-16LE base64).

Examples:
  python3 ssh_ps.py windows1-w1 --command 'Get-Date'
  python3 ssh_ps.py windows1-w1 --file path/to/script.ps1

Notes:
  - Avoid using `$pid` as a variable name in PowerShell; it aliases read-only `$PID`.
  - Consider setting `$ProgressPreference = "SilentlyContinue"` in the script to avoid progress noise.
"""

from __future__ import annotations

import argparse
import base64
import subprocess
import sys
from pathlib import Path


def _read_script(file_path: str) -> str:
    if file_path == "-":
        return sys.stdin.read()
    return Path(file_path).read_text(encoding="utf-8")


def _encode_ps(script: str) -> str:
    # PowerShell expects UTF-16LE for -EncodedCommand.
    data = script.encode("utf-16le")
    return base64.b64encode(data).decode("ascii")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("host", help="SSH host (e.g. windows1-w1)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--command", help="Inline PowerShell (use single quotes in Bash/zsh)")
    g.add_argument("--file", help="Path to .ps1 (use '-' for stdin)")
    p.add_argument("--pwsh", action="store_true", help="Use pwsh instead of powershell.exe")
    p.add_argument("--allow-profile", action="store_true", help="Do not pass -NoProfile")
    p.add_argument("--interactive", action="store_true", help="Do not pass -NonInteractive")
    p.add_argument("--dry-run", action="store_true", help="Print the ssh command without executing")
    args = p.parse_args()

    script = args.command if args.command is not None else _read_script(args.file)
    b64 = _encode_ps(script)

    shell = "pwsh" if args.pwsh else "powershell"
    ps_flags: list[str] = []
    if not args.allow_profile:
        ps_flags.append("-NoProfile")
    if not args.interactive:
        ps_flags.append("-NonInteractive")

    cmd = ["ssh", args.host, shell, *ps_flags, "-EncodedCommand", b64]

    if args.dry_run:
        print(" ".join(cmd))
        return 0

    completed = subprocess.run(cmd, text=True)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
