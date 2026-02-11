#!/usr/bin/env python3
"""
check_readme_sync.py

Validate README index consistency:
1. Root README covers all `.agent/skills/*/SKILL.md`
2. Root README links required sub READMEs
3. Sub READMEs link back to root README

Usage:
  python3 tools/check_readme_sync.py
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import List, Sequence


ROOT = Path(__file__).resolve().parent.parent
ROOT_README = ROOT / "README.md"
SUB_READMES = [
    ROOT / "omega_v3_core" / "README.md",
    ROOT / "parallel_trainer" / "README.md",
    ROOT / "rq" / "README.md",
]
SKILLS_ROOT = ROOT / ".agent" / "skills"
SKILL_PATTERN = re.compile(r"\.agent/skills/[A-Za-z0-9_\-]+/SKILL\.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _skill_files() -> List[str]:
    skills: List[str] = []
    for skill in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
        skills.append(_rel(skill))
    return skills


def _skill_links_in_root(root_text: str) -> Sequence[str]:
    return sorted(set(SKILL_PATTERN.findall(root_text)))


def main() -> int:
    issues: List[str] = []

    if not ROOT_README.exists():
        print("README sync check failed:")
        print(f"- Missing root README: {_rel(ROOT_README)}")
        return 1

    root_text = _read(ROOT_README)
    actual_skills = _skill_files()
    indexed_skills = set(_skill_links_in_root(root_text))

    for skill in actual_skills:
        if skill not in indexed_skills:
            issues.append(f"Root README missing skill link: `{skill}`")

    for skill in sorted(indexed_skills):
        skill_path = ROOT / skill
        if not skill_path.exists():
            issues.append(f"Root README has stale skill link: `{skill}`")

    for sub_readme in SUB_READMES:
        rel = _rel(sub_readme)
        if rel not in root_text:
            issues.append(f"Root README missing sub README link: `{rel}`")

    for sub_readme in SUB_READMES:
        rel = _rel(sub_readme)
        if not sub_readme.exists():
            issues.append(f"Missing sub README file: `{rel}`")
            continue
        sub_text = _read(sub_readme)
        if "../README.md" not in sub_text:
            issues.append(f"Sub README missing backlink `../README.md`: `{rel}`")

    if issues:
        print("README sync check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("README sync check passed.")
    print(f"- Skills indexed in root README: {len(actual_skills)}")
    print(f"- Sub README links checked: {len(SUB_READMES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
