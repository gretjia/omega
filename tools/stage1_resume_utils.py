"""Stage1 resume helpers.

These helpers preserve output semantics while making resume behavior robust
across git hash changes and interrupted writes.
"""

from __future__ import annotations

from pathlib import Path


def find_existing_done_for_date(output_root: Path, date_str: str) -> Path | None:
    """Return an existing .done marker for the date, regardless of hash.

    Only markers with a corresponding parquet file are considered valid.
    """
    pattern = f"{date_str}_*.parquet.done"
    for done_path in sorted(output_root.glob(pattern)):
        parquet_path = done_path.with_suffix("")
        if parquet_path.exists():
            return done_path
    return None


def clear_stale_done_marker(out_path: Path, done_path: Path) -> bool:
    """Remove stale .done markers that no longer have parquet payloads."""
    if done_path.exists() and not out_path.exists():
        done_path.unlink(missing_ok=True)
        return True
    return False


def ensure_done_for_existing_parquet(out_path: Path, done_path: Path) -> bool:
    """Repair missing .done marker for an already materialized parquet file."""
    if out_path.exists() and not done_path.exists():
        done_path.touch()
        return True
    return False
