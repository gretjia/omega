import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.run_vertex_xgb_train import _select_training_weights


def test_select_training_weights_uses_physics_abs_singularity() -> None:
    weights = _select_training_weights(
        mode="physics_abs_singularity",
        singularity=np.array([0.25, -0.5, 0.1]),
        excess_returns=np.array([0.01, -0.02, 0.03]),
    )
    assert weights.tolist() == [0.25, 0.5, 0.1]


def test_select_training_weights_uses_abs_excess_return() -> None:
    weights = _select_training_weights(
        mode="abs_excess_return",
        singularity=np.array([0.25, -0.5, 0.1]),
        excess_returns=np.array([0.01, -0.02, 0.03]),
    )
    assert weights.tolist() == [0.01, 0.02, 0.03]


def test_select_training_weights_uses_sqrt_abs_excess_return() -> None:
    weights = _select_training_weights(
        mode="sqrt_abs_excess_return",
        singularity=np.array([0.25, -0.5, 0.1]),
        excess_returns=np.array([0.04, -0.09, 0.0]),
    )
    assert np.allclose(weights, np.array([0.2, 0.3, 0.0], dtype=np.float64))


def test_select_training_weights_uses_pow_0p75_abs_excess_return() -> None:
    weights = _select_training_weights(
        mode="pow_0p75_abs_excess_return",
        singularity=np.array([0.25, -0.5, 0.1]),
        excess_returns=np.array([0.04, -0.09, 0.0]),
    )
    assert np.allclose(weights, np.array([0.08944272, 0.16431677, 0.0], dtype=np.float64))
