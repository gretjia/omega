#!/usr/bin/env python3
"""
Deprecated by v60 vertex objection.

Base-matrix ETL must run on local AMD nodes with ticker sharding:
- tools/v60_build_base_matrix.py (compat entrypoint)
- tools/v60_forge_base_matrix_local.py (canonical implementation)
"""

from __future__ import annotations

def main() -> int:
    msg = (
        "FATAL: tools/run_vertex_base_matrix.py is disabled. "
        "v60 base_matrix ETL is local-only and cannot run on Vertex AI. "
        "Use: python3 tools/v60_build_base_matrix.py ..."
    )
    print(msg, flush=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
