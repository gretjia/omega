"""
Deprecated Framer shim.

The legacy `Framer` implementation was archived to:
`archive/legacy_v50/pipeline_engine_framer_v52.py`

This shim intentionally blocks old v50/v52 framing paths so operators do not
mix them with the v62 two-stage pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _archive_path() -> Path:
    return Path(__file__).resolve().parents[2] / "archive" / "legacy_v50" / "pipeline_engine_framer_v52.py"


def _raise_deprecated() -> None:
    raise RuntimeError(
        "pipeline.engine.framer is archived and disabled.\n"
        f"Archived source: {_archive_path()}\n"
        "Use v62 entrypoints: tools/stage1_*_base_etl.py + tools/stage2_physics_compute.py"
    )


def _validate_is_quote_file(file_path: str, cfg: Any) -> bool:
    _raise_deprecated()
    return False


def _process_single_stock(symbol: str, file_paths: list[str], cfg: Any) -> Any:
    _raise_deprecated()
    return None


def _process_stock_chunk(chunk: list[Any], cfg: Any) -> list[Any]:
    _raise_deprecated()
    return []


class Framer:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        _raise_deprecated()

