"""
omega_core package bootstrap.

Note:
- `omega_core/trainer.py` is temporarily file-locked on the current workspace volume.
- We expose v5.1 trainer implementation through `omega_core.trainer` via module alias
  to preserve all existing imports.
"""

from __future__ import annotations

import sys as _sys

from . import trainer_v51 as _trainer_v51

_sys.modules[__name__ + ".trainer"] = _trainer_v51
