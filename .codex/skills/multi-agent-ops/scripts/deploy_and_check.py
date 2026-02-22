#!/usr/bin/env python3
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[4]

CONSTITUTION_V2 = ROOT / "audit" / "constitution_v2.md"
LEGACY_CONSTITUTION = ROOT / "OMEGA_CONSTITUTION.md"
DOC_CANON = ROOT / "audit" / "multi_agents.md"
DOC_LEGACY = ROOT / "audit" / "v60_multi_agents.md"

RUNTIME_CANON = ROOT / "audit" / "runtime" / "multi_agent"
RUNTIME_LEGACY = ROOT / "audit" / "runtime" / "v60"
PROFILES_CANON = RUNTIME_CANON / "agent_profiles.yaml"
PROFILES_LEGACY = RUNTIME_LEGACY / "agent_profiles.yaml"
PROMPTS_CANON = RUNTIME_CANON / "recursive_audit_prompts.md"
PROMPTS_LEGACY = RUNTIME_LEGACY / "recursive_audit_prompts.md"

AGENTS = ROOT / "AGENTS.md"
PRINCIPLES = ROOT / ".agent" / "principles.yaml"
LIVE = ROOT / "handover" / "ai-direct" / "live"
DEBUG_LESSONS = ROOT / "handover" / "DEBUG_LESSONS.md"
HANDOVER_ENTRIES = ROOT / "handover" / "ai-direct" / "entries"
HANDOVER_INDEX_DIR = ROOT / "handover" / "index"
MEMORY_INDEX_JSONL = HANDOVER_INDEX_DIR / "memory_index.jsonl"
MEMORY_INDEX_SQLITE = HANDOVER_INDEX_DIR / "memory_index.sqlite3"
MEMORY_INDEX_SHA1 = HANDOVER_INDEX_DIR / "memory_index.sha1"
LIVE_RECALL = LIVE / "00_Lesson_Recall.md"

REQUIRED_HANDOFF = [
    LIVE / "01_Raw_Context.md",
    LIVE / "02_Oracle_Insight.md",
    LIVE / "03_Mechanic_Patch.md",
    LIVE / "04A_Gemini_Recursive_Audit.md",
    LIVE / "04B_Codex_Recursive_Audit.md",
    LIVE / "05_Final_Audit_Decision.md",
]

LIVE_CONTEXT_FILES = [
    LIVE / "05_Final_Audit_Decision.md",
    LIVE / "04A_Gemini_Recursive_Audit.md",
    LIVE / "04B_Codex_Recursive_Audit.md",
    LIVE / "03_Mechanic_Patch.md",
    LIVE / "02_Oracle_Insight.md",
    LIVE / "01_Raw_Context.md",
]

META_LINE_RE = re.compile(r"^- ([a-zA-Z0-9_]+):\s*(.*)$")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*\S)\s*$")
DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?(?:\s*[+\-]\d{4})?)")
PATH_RE = re.compile(r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.[A-Za-z0-9_.-]+")
TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_+-]{2,}")
PLACEHOLDER_VALUES = {"", "TODO", "N/A", "NA", "NONE", "NULL", "TBD"}
TOKEN_STOPWORDS = {
    "about",
    "after",
    "again",
    "agent",
    "agents",
    "audit",
    "base",
    "before",
    "build",
    "check",
    "cloud",
    "completed",
    "context",
    "current",
    "debug",
    "decision",
    "details",
    "entry",
    "error",
    "failed",
    "failure",
    "final",
    "from",
    "handover",
    "history",
    "insight",
    "issue",
    "latest",
    "lesson",
    "lessons",
    "live",
    "mechanic",
    "next",
    "none",
    "oracle",
    "output",
    "patch",
    "phase",
    "recent",
    "risk",
    "root",
    "running",
    "session",
    "status",
    "task",
    "this",
    "timestamp",
    "todo",
    "watchdog",
}

DEFAULT_PROFILES = """version: 2

active:
  oracle: codex_xhigh
  mechanic: gemini_flash
  auditor_primary: gemini_pro
  auditor_secondary: codex_xhigh
  debug_scribe: codex_medium

roles:
  oracle:
    provider: codex_cli
    mode: read_only
    profiles:
      codex_xhigh:
        model: gpt-5.3-codex
        codex_config:
          model_reasoning_effort: xhigh
      codex_medium:
        model: gpt-5.3-codex
        codex_config:
          model_reasoning_effort: medium

  mechanic:
    provider: gemini_cli
    mode: write_enabled
    profiles:
      gemini_flash:
        model: gemini-3-flash
        extra_args: ["--approval-mode", "auto_edit", "--output-format", "text"]
      gemini_pro:
        model: gemini-3-pro
        extra_args: ["--approval-mode", "auto_edit", "--output-format", "text"]

  auditor_primary:
    provider: gemini_cli
    mode: read_only
    profiles:
      gemini_pro:
        model: gemini-3-pro
        extra_args: ["--approval-mode", "plan", "--output-format", "text"]
      gemini_flash:
        model: gemini-3-flash
        extra_args: ["--approval-mode", "plan", "--output-format", "text"]

  auditor_secondary:
    provider: codex_cli
    mode: read_only
    profiles:
      codex_xhigh:
        model: gpt-5.3-codex
        codex_config:
          model_reasoning_effort: xhigh
      codex_medium:
        model: gpt-5.3-codex
        codex_config:
          model_reasoning_effort: medium

  debug_scribe:
    provider: codex_cli
    mode: write_enabled
    profiles:
      codex_medium:
        model: gpt-5.3-codex
        codex_config:
          model_reasoning_effort: medium
      codex_xhigh:
        model: gpt-5.3-codex
        codex_config:
          model_reasoning_effort: xhigh

extensions:
  enabled: []
  catalog: {}
"""

DEFAULT_PROMPTS = """# Recursive Audit Prompt Pack (Stable Path)

Use this pack for both auditors.
Hard rule: each auditor runs independently and must not read the other auditor output before finalizing.
Pre-task rule: read `audit/constitution_v2.md` before analysis.

## Shared Inputs
- `/Users/zephryj/work/Omega_vNext/audit/constitution_v2.md`
- `/Users/zephryj/work/Omega_vNext/OMEGA_CONSTITUTION.md` (legacy reference)
- `/Users/zephryj/work/Omega_vNext/README.md`
- `/Users/zephryj/work/Omega_vNext/audit/multi_agents.md`
- `/Users/zephryj/work/Omega_vNext/.agent/principles.yaml`
- `/Users/zephryj/work/Omega_vNext/handover/ai-direct/live/01_Raw_Context.md`
- `/Users/zephryj/work/Omega_vNext/handover/ai-direct/live/03_Mechanic_Patch.md`
"""

DEFAULT_GUIDING_BASELINE = """# OMEGA Multi-Agents Guiding Principles (v60 Baseline)

This document is the principle baseline for multi-agent architecture decisions.
It remains valid across `v6.x+` and is intentionally kept as a stable guidance reference.

## P1. Human Final Authority
- Human is the only final merge authority.
- Agents may propose, implement, and audit; they do not auto-merge.
"""


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def handoff_template(title: str) -> str:
    return (
        f"# {title}\n\n"
        f"- task_id: TODO\n"
        f"- git_hash: TODO\n"
        f"- timestamp_utc: {now_utc()}\n\n"
        "## Content\n"
        "TODO\n"
    )


def debug_lessons_template() -> str:
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


def _relpath(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _clean_value(value: str) -> str:
    return " ".join(value.strip().split())


def _is_placeholder(value: str) -> bool:
    return _clean_value(value).upper() in PLACEHOLDER_VALUES


def _is_meaningful(value: str) -> bool:
    cleaned = _clean_value(value)
    return bool(cleaned) and not _is_placeholder(cleaned) and len(cleaned) >= 8


def _parse_metadata(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        m = META_LINE_RE.match(raw.strip())
        if not m:
            continue
        out[m.group(1).strip()] = _clean_value(m.group(2))
    return out


def _content_section(text: str) -> str:
    marker = "## Content"
    idx = text.find(marker)
    if idx < 0:
        return text
    return text[idx + len(marker) :]


def _write_if_changed(path: Path, content: str) -> bool:
    if path.exists():
        old = path.read_text(encoding="utf-8", errors="replace")
        if old == content:
            return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _mtime_utc(path: Path) -> str:
    ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_paths(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in PATH_RE.findall(text):
        cleaned = raw.strip("`'\".,:;()[]{}")
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        out.append(cleaned)
    return out


def _extract_components(text: str, limit: int = 16) -> list[str]:
    parts: list[str] = []
    for path in _extract_paths(text):
        bits = [b for b in path.split("/") if b]
        if len(bits) >= 2:
            parts.append(bits[0].lower())
        stem = bits[-1].rsplit(".", 1)[0].lower()
        if stem:
            parts.append(stem)

    for token in TOKEN_RE.findall(text.lower()):
        if "_" in token or "-" in token:
            parts.append(token)
        if token in {
            "vertex",
            "quota",
            "autopilot",
            "watchdog",
            "pipeline",
            "orchestrator",
            "backtest",
            "train",
            "upload",
            "shard",
        }:
            parts.append(token)

    out: list[str] = []
    seen: set[str] = set()
    for item in parts:
        key = _clean_value(item).lower()
        if len(key) < 3 or key in seen:
            continue
        seen.add(key)
        out.append(key)
        if len(out) >= limit:
            break
    return out


def _tokenize_keywords(text: str, limit: int = 24) -> list[str]:
    freq: dict[str, int] = {}
    for raw in TOKEN_RE.findall(text.lower()):
        token = raw.strip("_-+")
        if len(token) < 4 or token in TOKEN_STOPWORDS:
            continue
        freq[token] = freq.get(token, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    return [token for token, _ in ranked[:limit]]


def _first_heading(text: str, fallback: str) -> str:
    for raw in text.splitlines():
        m = HEADING_RE.match(raw.strip())
        if m:
            return _clean_value(m.group(1))
    return fallback


def _extract_first_date(text: str) -> str:
    m = DATE_RE.search(text)
    return _clean_value(m.group(1)) if m else ""


def _extract_field(text: str, patterns: tuple[str, ...]) -> str:
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            return _clean_value(m.group(1))
    return ""


def _safe_preview(text: str, max_chars: int = 480) -> str:
    line = _clean_value(text)
    return line[:max_chars].rstrip() if len(line) > max_chars else line


def _record_id(parts: list[str]) -> str:
    raw = "|".join(parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _parse_debug_lesson_records() -> list[dict]:
    if not DEBUG_LESSONS.exists():
        return []

    source_path = _relpath(DEBUG_LESSONS)
    source_mtime = _mtime_utc(DEBUG_LESSONS)
    lines = DEBUG_LESSONS.read_text(encoding="utf-8", errors="replace").splitlines()

    records: list[dict] = []
    header = ""
    block: list[str] = []

    def flush(h: str, body: list[str]) -> None:
        if "|" not in h:
            return
        left, right = h.split("|", 1)
        timestamp = _clean_value(left)
        title = _clean_value(right)
        if not timestamp or not title:
            return
        meta = _parse_metadata("\n".join(body))
        task_id = _clean_value(meta.get("task_id", ""))
        if not task_id or _is_placeholder(task_id):
            return
        git_hash = _clean_value(meta.get("git_hash", ""))
        if _is_placeholder(git_hash):
            git_hash = ""
        symptom = _clean_value(meta.get("symptom", ""))
        root_cause = _clean_value(meta.get("root_cause", ""))
        fix = _clean_value(meta.get("fix", ""))
        guardrail = _clean_value(meta.get("guardrail", ""))
        refs = _clean_value(meta.get("refs", ""))
        text = " ".join(part for part in (symptom, root_cause, fix, guardrail) if part)
        components = _extract_components(" ".join((title, refs, text)))
        keywords = _tokenize_keywords(" ".join((title, text, refs)))
        rec_id = _record_id(["debug_lesson", source_path, timestamp, task_id, title, git_hash])
        records.append(
            {
                "id": rec_id,
                "kind": "debug_lesson",
                "source_path": source_path,
                "source_mtime_utc": source_mtime,
                "timestamp_utc": timestamp,
                "task_id": task_id,
                "git_hash": git_hash,
                "title": title,
                "symptom": symptom,
                "root_cause": root_cause,
                "fix": fix,
                "guardrail": guardrail,
                "refs": refs,
                "components": components,
                "keywords": keywords,
                "text": _safe_preview(text, max_chars=1000),
                "score_boost": 1.0,
            }
        )

    for raw in lines:
        if raw.startswith("## "):
            flush(header, block)
            header = raw[3:].strip()
            block = []
            continue
        if header:
            block.append(raw)
    flush(header, block)
    return records


def _parse_handover_entry_records() -> list[dict]:
    if not HANDOVER_ENTRIES.exists():
        return []

    records: list[dict] = []
    for path in sorted(HANDOVER_ENTRIES.glob("*.md")):
        txt = path.read_text(encoding="utf-8", errors="replace")
        title = _first_heading(txt, fallback=path.stem)
        task_id = _extract_field(
            txt,
            (
                r"\btask[_\s-]*id\b[^A-Za-z0-9]+([A-Za-z0-9._-]{3,})",
                r"\btask\b[^A-Za-z0-9]+([A-Za-z0-9._-]{3,})",
            ),
        )
        git_hash = _extract_field(
            txt,
            (
                r"\bgit[_\s-]*hash\b[^A-Za-z0-9]+`?([A-Za-z0-9]{6,40})`?",
                r"\brun[_\s-]*hash\b[^A-Za-z0-9]+`?([A-Za-z0-9]{6,40})`?",
                r"\bcommit\b[^A-Za-z0-9]+`?([A-Za-z0-9]{6,40})`?",
            ),
        )
        timestamp = _extract_first_date(txt)
        components = _extract_components(txt)
        keywords = _tokenize_keywords(f"{title}\n{txt}")
        rec_id = _record_id(
            [
                "handover_entry",
                _relpath(path),
                _mtime_utc(path),
                title,
            ]
        )
        records.append(
            {
                "id": rec_id,
                "kind": "handover_entry",
                "source_path": _relpath(path),
                "source_mtime_utc": _mtime_utc(path),
                "timestamp_utc": timestamp,
                "task_id": task_id,
                "git_hash": git_hash,
                "title": title,
                "symptom": "",
                "root_cause": "",
                "fix": "",
                "guardrail": "",
                "refs": ", ".join(f"`{p}`" for p in _extract_paths(txt)),
                "components": components,
                "keywords": keywords,
                "text": _safe_preview(txt, max_chars=1000),
                "score_boost": 0.25,
            }
        )
    return records


def _memory_records() -> list[dict]:
    records = _parse_debug_lesson_records() + _parse_handover_entry_records()
    records.sort(key=lambda item: str(item.get("id", "")))
    return records


def _jsonl_dump(records: list[dict]) -> str:
    lines = [json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records]
    return ("\n".join(lines) + "\n") if lines else ""


def _write_memory_sqlite(records: list[dict]) -> None:
    HANDOVER_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    tmp = MEMORY_INDEX_SQLITE.with_suffix(".sqlite3.tmp")
    if tmp.exists():
        tmp.unlink()

    conn = sqlite3.connect(tmp)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE memory_records (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                source_path TEXT NOT NULL,
                source_mtime_utc TEXT,
                timestamp_utc TEXT,
                task_id TEXT,
                git_hash TEXT,
                title TEXT,
                symptom TEXT,
                root_cause TEXT,
                fix TEXT,
                guardrail TEXT,
                refs TEXT,
                components_json TEXT,
                keywords_json TEXT,
                text TEXT,
                score_boost REAL NOT NULL
            )
            """
        )
        cur.execute("CREATE INDEX idx_memory_kind ON memory_records(kind)")
        cur.execute("CREATE INDEX idx_memory_task ON memory_records(task_id)")
        cur.execute("CREATE INDEX idx_memory_source ON memory_records(source_path)")
        rows = [
            (
                str(r.get("id", "")),
                str(r.get("kind", "")),
                str(r.get("source_path", "")),
                str(r.get("source_mtime_utc", "")),
                str(r.get("timestamp_utc", "")),
                str(r.get("task_id", "")),
                str(r.get("git_hash", "")),
                str(r.get("title", "")),
                str(r.get("symptom", "")),
                str(r.get("root_cause", "")),
                str(r.get("fix", "")),
                str(r.get("guardrail", "")),
                str(r.get("refs", "")),
                json.dumps(r.get("components", []), ensure_ascii=False),
                json.dumps(r.get("keywords", []), ensure_ascii=False),
                str(r.get("text", "")),
                float(r.get("score_boost", 0.0)),
            )
            for r in records
        ]
        cur.executemany(
            """
            INSERT INTO memory_records (
                id, kind, source_path, source_mtime_utc, timestamp_utc, task_id, git_hash, title,
                symptom, root_cause, fix, guardrail, refs, components_json, keywords_json, text, score_boost
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    finally:
        conn.close()

    tmp.replace(MEMORY_INDEX_SQLITE)


def sync_memory_index() -> tuple[list[str], list[dict]]:
    records = _memory_records()
    blob = _jsonl_dump(records)
    digest = hashlib.sha1(blob.encode("utf-8")).hexdigest()

    current_digest = ""
    if MEMORY_INDEX_SHA1.exists():
        current_digest = _clean_value(MEMORY_INDEX_SHA1.read_text(encoding="utf-8", errors="replace"))

    needs_rebuild = (
        digest != current_digest
        or not MEMORY_INDEX_JSONL.exists()
        or not MEMORY_INDEX_SQLITE.exists()
        or not MEMORY_INDEX_SHA1.exists()
    )

    changed: list[str] = []
    if _write_if_changed(MEMORY_INDEX_JSONL, blob):
        changed.append(str(MEMORY_INDEX_JSONL.relative_to(ROOT)))

    if needs_rebuild:
        _write_memory_sqlite(records)
        changed.append(str(MEMORY_INDEX_SQLITE.relative_to(ROOT)))

    if _write_if_changed(MEMORY_INDEX_SHA1, f"{digest}\n"):
        changed.append(str(MEMORY_INDEX_SHA1.relative_to(ROOT)))

    return sorted(set(changed)), records


def _live_query_context(context: dict) -> dict:
    task_id = _clean_value(str(context.get("task_id", "")))
    content = _clean_value(str(context.get("content", "")))
    keywords = _tokenize_keywords(" ".join((task_id, content)), limit=18)
    components = _extract_components(" ".join((task_id, content)))
    has_query = bool(task_id and not _is_placeholder(task_id)) or bool(keywords) or bool(components)
    return {
        "task_id": task_id,
        "keywords": keywords,
        "components": components,
        "content": content,
        "has_query": has_query,
    }


def _scored_recall(record: dict, query: dict) -> tuple[float, list[str], list[str], list[str]]:
    if not query.get("has_query"):
        return 0.0, [], [], []

    score = float(record.get("score_boost", 0.0))
    reasons: list[str] = []

    record_task = _clean_value(str(record.get("task_id", ""))).lower()
    query_task = _clean_value(str(query.get("task_id", ""))).lower()
    if query_task and record_task and not _is_placeholder(record_task):
        if record_task == query_task:
            score += 8.0
            reasons.append("task_id exact")
        elif query_task in record_task or record_task in query_task:
            score += 4.0
            reasons.append("task_id partial")

    record_keywords = {str(k).lower() for k in record.get("keywords", []) if str(k).strip()}
    query_keywords = {str(k).lower() for k in query.get("keywords", []) if str(k).strip()}
    keyword_overlap = sorted(record_keywords & query_keywords)
    if keyword_overlap:
        score += min(len(keyword_overlap), 5) * 1.2
        reasons.append(f"keyword x{len(keyword_overlap)}")

    record_components = {str(k).lower() for k in record.get("components", []) if str(k).strip()}
    query_components = {str(k).lower() for k in query.get("components", []) if str(k).strip()}
    component_overlap = sorted(record_components & query_components)
    if component_overlap:
        score += len(component_overlap) * 2.0
        reasons.append(f"component x{len(component_overlap)}")

    title = _clean_value(str(record.get("title", ""))).lower()
    if query_task and query_task in title:
        score += 1.0
        reasons.append("title task hint")

    return score, reasons, keyword_overlap[:5], component_overlap[:5]


def _render_lesson_recall(
    query: dict,
    ranked: list[dict],
    top_k: int,
    total_records: int,
) -> str:
    lines = [
        "# Pre-Task Lesson Recall",
        "",
        "- generated_by: `python3 .codex/skills/multi-agent-ops/scripts/deploy_and_check.py`",
        "- source_of_truth: `handover/ai-direct/entries/*.md` and `handover/DEBUG_LESSONS.md`",
        "- index_layer: `handover/index/memory_index.jsonl` and `handover/index/memory_index.sqlite3` (derived read-only)",
        f"- indexed_records: {total_records}",
        f"- recall_top_k: {top_k}",
        f"- query_task_id: {query.get('task_id', '') or 'N/A'}",
        f"- query_keywords: {', '.join(query.get('keywords', [])) or 'N/A'}",
        f"- query_components: {', '.join(query.get('components', [])) or 'N/A'}",
        "",
    ]

    if not query.get("has_query"):
        lines.extend(
            [
                "## Result",
                "- No actionable live query found in `live/01..05`; recall skipped.",
            ]
        )
        return "\n".join(lines) + "\n"

    if not ranked:
        lines.extend(
            [
                "## Result",
                "- No relevant historical lessons found for this query.",
            ]
        )
        return "\n".join(lines) + "\n"

    lines.append("## Top Matches")
    for idx, item in enumerate(ranked, start=1):
        rec = item["record"]
        reasons = ", ".join(item["reasons"]) or "similar context"
        kw = ", ".join(item["keyword_overlap"]) or "N/A"
        cp = ", ".join(item["component_overlap"]) or "N/A"
        ts = rec.get("timestamp_utc", "") or rec.get("source_mtime_utc", "")
        lines.extend(
            [
                f"{idx}. `{rec.get('kind', 'memory')}` | score={item['score']:.2f} | {rec.get('title', 'untitled')}",
                f"   - task_id: {rec.get('task_id', '') or 'N/A'}",
                f"   - timestamp: {ts or 'N/A'}",
                f"   - source: `{rec.get('source_path', 'N/A')}`",
                f"   - why: {reasons}",
                f"   - keyword_overlap: {kw}",
                f"   - component_overlap: {cp}",
            ]
        )
        if rec.get("symptom"):
            lines.append(f"   - symptom: {rec.get('symptom')}")
        if rec.get("root_cause"):
            lines.append(f"   - root_cause: {rec.get('root_cause')}")
        if rec.get("fix"):
            lines.append(f"   - fix: {rec.get('fix')}")
        if rec.get("guardrail"):
            lines.append(f"   - guardrail: {rec.get('guardrail')}")
    return "\n".join(lines) + "\n"


def generate_lesson_recall(records: list[dict], top_k: int = 5) -> tuple[bool, int]:
    context = _load_live_context()
    query = _live_query_context(context)
    k = max(1, int(top_k))

    ranked: list[dict] = []
    for rec in records:
        score, reasons, keyword_overlap, component_overlap = _scored_recall(rec, query)
        if score <= 0:
            continue
        ranked.append(
            {
                "score": score,
                "reasons": reasons,
                "keyword_overlap": keyword_overlap,
                "component_overlap": component_overlap,
                "record": rec,
            }
        )

    ranked.sort(
        key=lambda item: (
            -float(item["score"]),
            str(item["record"].get("timestamp_utc", "")),
            str(item["record"].get("id", "")),
        )
    )
    top = ranked[:k]
    body = _render_lesson_recall(query=query, ranked=top, top_k=k, total_records=len(records))
    changed = _write_if_changed(LIVE_RECALL, body)
    return changed, len(top)


def _load_live_context() -> dict:
    meta = {"task_id": "", "git_hash": "", "timestamp_utc": ""}
    sources: list[str] = []
    content_chunks: list[str] = []

    for path in LIVE_CONTEXT_FILES:
        if not path.exists():
            continue
        txt = path.read_text(encoding="utf-8", errors="replace")
        this_meta = _parse_metadata(txt)
        for key in ("task_id", "git_hash", "timestamp_utc"):
            if key not in meta:
                continue
            if _is_placeholder(meta[key]) and not _is_placeholder(this_meta.get(key, "")):
                meta[key] = this_meta[key]
        body = _content_section(txt)
        if _is_meaningful(body):
            sources.append(_relpath(path))
            content_chunks.append(body.strip())

    has_task = not _is_placeholder(meta.get("task_id", ""))
    has_content = bool(content_chunks)
    return {
        "task_id": _clean_value(meta.get("task_id", "")),
        "git_hash": _clean_value(meta.get("git_hash", "")),
        "timestamp_utc": _clean_value(meta.get("timestamp_utc", "")),
        "sources": sources,
        "content": "\n".join(content_chunks),
        "has_task": has_task,
        "has_content": has_content,
    }


def _extract_signal(text: str, keywords: tuple[str, ...]) -> str:
    for raw in text.splitlines():
        line = _clean_value(raw.lstrip("-*0123456789. "))
        if not _is_meaningful(line):
            continue
        low = line.lower()
        if any(k in low for k in keywords):
            return line
    return ""


def _active_debug_profile() -> str:
    try:
        cfg = yaml.safe_load(PROFILES_CANON.read_text(encoding="utf-8")) or {}
    except Exception:
        return "codex_medium"
    if not isinstance(cfg, dict):
        return "codex_medium"
    active = cfg.get("active", {})
    if not isinstance(active, dict):
        return "codex_medium"
    profile = _clean_value(str(active.get("debug_scribe", "codex_medium")))
    return profile or "codex_medium"


def _auto_debug_key(context: dict) -> str:
    task_id = _clean_value(str(context.get("task_id", "")))
    git_hash = _clean_value(str(context.get("git_hash", "")))
    if _is_placeholder(git_hash):
        git_hash = "nogit"
    return f"{task_id}|{git_hash}"


def _auto_debug_fields(context: dict) -> dict[str, str]:
    text = str(context.get("content", ""))
    verdict_reject = "reject" in text.lower() or "failed" in text.lower() or "error" in text.lower()
    title = f"{_clean_value(str(context['task_id'])).replace(' ', '_')}_{'reject' if verdict_reject else 'debug'}"

    symptom = _extract_signal(
        text,
        ("symptom", "error", "failed", "failure", "bug", "incident", "timeout", "stale", "reject"),
    )
    root_cause = _extract_signal(text, ("root cause", "because", "reason", "caused by", "cause"))
    fix = _extract_signal(text, ("fix", "resolved", "patched", "changed", "updated", "added"))
    guardrail = _extract_signal(text, ("guardrail", "prevent", "gate", "check", "test", "monitor", "assert"))

    if not symptom:
        symptom = "Implementation or audit surfaced a defect in current task context."
    if not root_cause:
        root_cause = "Root cause captured across mechanic and recursive auditor artifacts."
    if not fix:
        fix = "Patch applied and validated under current multi-agent flow."
    if not guardrail:
        guardrail = "Keep dual-recursive-audit gate and deploy_and_check validation in merge path."

    refs = ", ".join(f"`{p}`" for p in context.get("sources", [])) or "N/A"
    git_hash = _clean_value(str(context.get("git_hash", "")))
    if _is_placeholder(git_hash):
        git_hash = "N/A"

    return {
        "title": title,
        "git_hash": git_hash,
        "symptom": symptom,
        "root_cause": root_cause,
        "fix": fix,
        "guardrail": guardrail,
        "refs": refs,
    }


def auto_append_debug_lesson() -> tuple[bool, str]:
    if not DEBUG_LESSONS.exists():
        DEBUG_LESSONS.parent.mkdir(parents=True, exist_ok=True)
        DEBUG_LESSONS.write_text(debug_lessons_template(), encoding="utf-8")

    context = _load_live_context()
    if not context.get("has_task") or not context.get("has_content"):
        return False, ""

    auto_key = _auto_debug_key(context)
    ledger = DEBUG_LESSONS.read_text(encoding="utf-8", errors="replace")
    if f"- auto_key: {auto_key}" in ledger:
        return False, auto_key

    fields = _auto_debug_fields(context)
    block = (
        f"\n## {now_utc()} | {fields['title']}\n"
        f"- task_id: {context['task_id']}\n"
        f"- git_hash: {fields['git_hash']}\n"
        "- role: debug_scribe\n"
        f"- model_profile: {_active_debug_profile()}\n"
        f"- auto_key: {auto_key}\n"
        f"- symptom: {fields['symptom']}\n"
        f"- root_cause: {fields['root_cause']}\n"
        f"- fix: {fields['fix']}\n"
        f"- guardrail: {fields['guardrail']}\n"
        f"- refs: {fields['refs']}\n"
    )
    with DEBUG_LESSONS.open("a", encoding="utf-8") as f:
        f.write(block)
    return True, auto_key


def _default_profiles_cfg() -> dict:
    cfg = yaml.safe_load(DEFAULT_PROFILES) or {}
    return cfg if isinstance(cfg, dict) else {}


def _merge_profiles_with_defaults(cfg: dict) -> tuple[dict, bool]:
    defaults = _default_profiles_cfg()
    merged = deepcopy(cfg) if isinstance(cfg, dict) else {}
    changed = not isinstance(cfg, dict)

    if "version" not in merged and "version" in defaults:
        merged["version"] = defaults["version"]
        changed = True

    for top_key in ("active", "roles", "extensions"):
        if top_key not in merged and top_key in defaults:
            merged[top_key] = deepcopy(defaults[top_key])
            changed = True

    active = merged.get("active")
    if not isinstance(active, dict):
        active = {}
        merged["active"] = active
        changed = True
    for role, profile in defaults.get("active", {}).items():
        if role not in active:
            active[role] = profile
            changed = True

    roles = merged.get("roles")
    if not isinstance(roles, dict):
        roles = {}
        merged["roles"] = roles
        changed = True

    for role, role_cfg in defaults.get("roles", {}).items():
        if role not in roles or not isinstance(roles.get(role), dict):
            roles[role] = deepcopy(role_cfg)
            changed = True
            continue

        current_role = roles[role]
        for field in ("provider", "mode"):
            if field not in current_role and field in role_cfg:
                current_role[field] = role_cfg[field]
                changed = True

        current_profiles = current_role.get("profiles")
        if not isinstance(current_profiles, dict):
            current_profiles = {}
            current_role["profiles"] = current_profiles
            changed = True

        for profile_name, profile_cfg in role_cfg.get("profiles", {}).items():
            if profile_name not in current_profiles:
                current_profiles[profile_name] = deepcopy(profile_cfg)
                changed = True

    return merged, changed


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    return True


def _ensure_legacy_aliases() -> list[str]:
    changed: list[str] = []

    # Keep v60 baseline doc available as guiding-principle source.
    if not DOC_LEGACY.exists():
        DOC_LEGACY.write_text(DEFAULT_GUIDING_BASELINE, encoding="utf-8")
        changed.append(str(DOC_LEGACY.relative_to(ROOT)))

    # Keep legacy runtime files as mirrors for old commands.
    if PROFILES_CANON.exists():
        PROFILES_LEGACY.parent.mkdir(parents=True, exist_ok=True)
        PROFILES_LEGACY.write_text(PROFILES_CANON.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        changed.append(str(PROFILES_LEGACY.relative_to(ROOT)))

    if PROMPTS_CANON.exists():
        PROMPTS_LEGACY.parent.mkdir(parents=True, exist_ok=True)
        PROMPTS_LEGACY.write_text(PROMPTS_CANON.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        changed.append(str(PROMPTS_LEGACY.relative_to(ROOT)))

    return changed


def repair() -> list[str]:
    changed: list[str] = []

    RUNTIME_CANON.mkdir(parents=True, exist_ok=True)

    if not DOC_CANON.exists():
        if _copy_if_exists(DOC_LEGACY, DOC_CANON):
            changed.append(str(DOC_CANON.relative_to(ROOT)))

    if not PROFILES_CANON.exists():
        if _copy_if_exists(PROFILES_LEGACY, PROFILES_CANON):
            changed.append(str(PROFILES_CANON.relative_to(ROOT)))
        else:
            PROFILES_CANON.write_text(DEFAULT_PROFILES, encoding="utf-8")
            changed.append(str(PROFILES_CANON.relative_to(ROOT)))
    try:
        cfg = yaml.safe_load(PROFILES_CANON.read_text(encoding="utf-8")) or {}
    except Exception:
        cfg = {}
    merged_cfg, profile_changed = _merge_profiles_with_defaults(cfg)
    if profile_changed:
        PROFILES_CANON.write_text(
            yaml.safe_dump(merged_cfg, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )
        changed.append(str(PROFILES_CANON.relative_to(ROOT)))

    if not PROMPTS_CANON.exists():
        if _copy_if_exists(PROMPTS_LEGACY, PROMPTS_CANON):
            changed.append(str(PROMPTS_CANON.relative_to(ROOT)))
        else:
            PROMPTS_CANON.write_text(DEFAULT_PROMPTS, encoding="utf-8")
            changed.append(str(PROMPTS_CANON.relative_to(ROOT)))

    LIVE.mkdir(parents=True, exist_ok=True)
    titles = {
        "01_Raw_Context.md": "01 Raw Context",
        "02_Oracle_Insight.md": "02 Oracle Insight",
        "03_Mechanic_Patch.md": "03 Mechanic Patch",
        "04A_Gemini_Recursive_Audit.md": "04A Gemini Recursive Audit",
        "04B_Codex_Recursive_Audit.md": "04B Codex Recursive Audit",
        "05_Final_Audit_Decision.md": "05 Final Audit Decision",
    }
    for p in REQUIRED_HANDOFF:
        if not p.exists():
            p.write_text(handoff_template(titles[p.name]), encoding="utf-8")
            changed.append(str(p.relative_to(ROOT)))

    if not DEBUG_LESSONS.exists():
        DEBUG_LESSONS.parent.mkdir(parents=True, exist_ok=True)
        DEBUG_LESSONS.write_text(debug_lessons_template(), encoding="utf-8")
        changed.append(str(DEBUG_LESSONS.relative_to(ROOT)))

    changed.extend(_ensure_legacy_aliases())
    return sorted(set(changed))


def check(skip_memory_checks: bool = False) -> list[str]:
    issues: list[str] = []

    if not CONSTITUTION_V2.exists():
        issues.append("Missing highest-priority constitution: audit/constitution_v2.md")
    if not LEGACY_CONSTITUTION.exists():
        issues.append("Missing legacy constitution reference: OMEGA_CONSTITUTION.md")

    if not DOC_CANON.exists():
        issues.append("Missing canonical spec: audit/multi_agents.md")
    else:
        txt = DOC_CANON.read_text(encoding="utf-8", errors="replace")
        if "Role Model (Current Mainstack)" not in txt:
            issues.append("audit/multi_agents.md missing role model section")
        if "Recursive Auditor A" not in txt or "Recursive Auditor B" not in txt:
            issues.append("audit/multi_agents.md missing dual recursive auditor definition")
        if "audit/runtime/multi_agent/agent_profiles.yaml" not in txt:
            issues.append("audit/multi_agents.md missing canonical profile path")
        if "audit/v60_multi_agents.md" not in txt:
            issues.append("audit/multi_agents.md missing v60 guiding-principle reference")
        if "audit/constitution_v2.md" not in txt:
            issues.append("audit/multi_agents.md missing constitution_v2 anchor")

    if not DOC_LEGACY.exists():
        issues.append("Missing guiding-principle baseline: audit/v60_multi_agents.md")
    else:
        txt = DOC_LEGACY.read_text(encoding="utf-8", errors="replace")
        if "Guiding Principles" not in txt and "P1." not in txt:
            issues.append("audit/v60_multi_agents.md missing principle baseline markers")

    if not AGENTS.exists():
        issues.append("Missing AGENTS.md at repository root")
    else:
        txt = AGENTS.read_text(encoding="utf-8", errors="replace")
        if "multi-agent-ops" not in txt:
            issues.append("AGENTS.md missing multi-agent-ops routing")
        if ".agent/skills/*" not in txt or "policy templates" not in txt:
            issues.append("AGENTS.md missing template-vs-executable clarification")
        if "Recursive Auditor A" not in txt or "Recursive Auditor B" not in txt:
            issues.append("AGENTS.md missing dual recursive auditor policy")
        if "Debug Scribe" not in txt and "debug_scribe" not in txt:
            issues.append("AGENTS.md missing debug_scribe policy")
        if "audit/constitution_v2.md" not in txt:
            issues.append("AGENTS.md missing constitution_v2 top-priority reference")
        if "immutable" not in txt:
            issues.append("AGENTS.md missing constitution_v2 immutability rule")
        if "must read" not in txt and "Before any planning/implementation/audit task" not in txt:
            issues.append("AGENTS.md missing pre-task constitution_v2 read rule")

    if not PRINCIPLES.exists():
        issues.append("Missing .agent/principles.yaml")
    else:
        txt = PRINCIPLES.read_text(encoding="utf-8", errors="replace")
        if "omega_v3_core" in txt:
            issues.append("principles.yaml still references omega_v3_core")
        if "omega_core/kernel.py" not in txt:
            issues.append("principles.yaml missing omega_core kernel path")
        if "audit/constitution_v2.md" not in txt:
            issues.append("principles.yaml missing constitution_v2 reference")
        try:
            p_cfg = yaml.safe_load(txt) or {}
        except Exception as exc:
            issues.append(f"principles.yaml parse error: {exc}")
            p_cfg = {}
        if isinstance(p_cfg, dict):
            g = p_cfg.get("global", {})
            constitution_path = ""
            if isinstance(g, dict):
                constitution_path = str(g.get("constitution_path", "")).strip()
            if constitution_path != "audit/constitution_v2.md":
                issues.append(
                    "principles.yaml global.constitution_path must be audit/constitution_v2.md"
                )

    if not PROFILES_CANON.exists():
        issues.append("Missing canonical profiles: audit/runtime/multi_agent/agent_profiles.yaml")
    else:
        try:
            cfg = yaml.safe_load(PROFILES_CANON.read_text(encoding="utf-8")) or {}
        except Exception as exc:  # pragma: no cover
            issues.append(f"agent_profiles.yaml parse error: {exc}")
            cfg = {}

        roles = cfg.get("roles", {}) if isinstance(cfg, dict) else {}
        active = cfg.get("active", {}) if isinstance(cfg, dict) else {}
        for role in ("oracle", "mechanic", "auditor_primary", "auditor_secondary", "debug_scribe"):
            if role not in roles:
                issues.append(f"agent_profiles.yaml missing role: {role}")
                continue
            profiles = roles[role].get("profiles", {}) if isinstance(roles[role], dict) else {}
            active_name = active.get(role)
            if not active_name:
                issues.append(f"agent_profiles.yaml missing active.{role}")
            elif active_name not in profiles:
                issues.append(f"agent_profiles.yaml active.{role} points to unknown profile: {active_name}")

    if not PROMPTS_CANON.exists():
        issues.append("Missing canonical prompts: audit/runtime/multi_agent/recursive_audit_prompts.md")
    else:
        txt = PROMPTS_CANON.read_text(encoding="utf-8", errors="replace")
        if "audit/constitution_v2.md" not in txt:
            issues.append("recursive_audit_prompts.md missing constitution_v2 input anchor")

    if not DEBUG_LESSONS.exists():
        issues.append("Missing handover debug lessons ledger: handover/DEBUG_LESSONS.md")
    else:
        txt = DEBUG_LESSONS.read_text(encoding="utf-8", errors="replace")
        if "Debug Lessons Ledger" not in txt:
            issues.append("handover/DEBUG_LESSONS.md missing ledger title")
        if "Entry Template" not in txt:
            issues.append("handover/DEBUG_LESSONS.md missing entry template section")
        ctx = _load_live_context()
        if ctx.get("has_task") and ctx.get("has_content"):
            auto_key = _auto_debug_key(ctx)
            if f"- auto_key: {auto_key}" not in txt:
                issues.append(f"handover/DEBUG_LESSONS.md missing auto entry for current context: {auto_key}")

    for p in REQUIRED_HANDOFF:
        if not p.exists():
            issues.append(f"Missing handoff file: {p.relative_to(ROOT)}")
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for key in ("task_id", "git_hash", "timestamp_utc"):
            if key not in txt:
                issues.append(f"{p.relative_to(ROOT)} missing key: {key}")

    if not skip_memory_checks:
        if not MEMORY_INDEX_JSONL.exists():
            issues.append("Missing handover memory index: handover/index/memory_index.jsonl")
        if not MEMORY_INDEX_SQLITE.exists():
            issues.append("Missing handover memory index DB: handover/index/memory_index.sqlite3")
        if not LIVE_RECALL.exists():
            issues.append("Missing pre-task recall artifact: handover/ai-direct/live/00_Lesson_Recall.md")

    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Deploy and validate stable multi-agent setup")
    ap.add_argument("--repair", action="store_true", help="Create missing bootstrap files and sync legacy aliases")
    ap.add_argument(
        "--no-auto-debug-scribe",
        action="store_true",
        help="Disable automatic debug lesson append from live context",
    )
    ap.add_argument(
        "--no-memory-recall",
        action="store_true",
        help="Disable derived handover index sync and pre-task Top-K lesson recall",
    )
    ap.add_argument(
        "--memory-top-k",
        type=int,
        default=5,
        help="Top-K historical lessons for pre-task recall (default: 5)",
    )
    ap.add_argument("--json", action="store_true", help="Output machine-readable result")
    args = ap.parse_args()

    changed: list[str] = []
    if args.repair:
        changed = repair()

    if not args.no_auto_debug_scribe:
        auto_changed, auto_key = auto_append_debug_lesson()
        if auto_changed:
            changed.append(f"handover/DEBUG_LESSONS.md (auto:{auto_key})")

    memory_records = 0
    recall_hits = 0
    if not args.no_memory_recall:
        memory_changed, records = sync_memory_index()
        changed.extend(memory_changed)
        memory_records = len(records)
        recall_changed, recall_hits = generate_lesson_recall(records, top_k=max(1, args.memory_top_k))
        if recall_changed:
            changed.append(str(LIVE_RECALL.relative_to(ROOT)))

    changed = sorted(set(changed))
    issues = check(skip_memory_checks=args.no_memory_recall)
    ok = not issues

    if args.json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "changed": changed,
                    "issues": issues,
                    "memory": {
                        "enabled": not args.no_memory_recall,
                        "indexed_records": memory_records,
                        "recall_hits": recall_hits,
                        "top_k": max(1, args.memory_top_k),
                        "recall_file": _relpath(LIVE_RECALL),
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        if changed:
            print("Repaired files:")
            for item in changed:
                print(f"- {item}")
        if not args.no_memory_recall:
            print(f"Memory index records: {memory_records}")
            print(f"Pre-task recall hits: {recall_hits} (top_k={max(1, args.memory_top_k)})")
        print("STATUS: PASS" if ok else "STATUS: FAIL")
        if issues:
            print("Issues:")
            for item in issues:
                print(f"- {item}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
